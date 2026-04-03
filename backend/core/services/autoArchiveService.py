import json
import logging

from backend.core.archiveDecision import ArchiveDecision
from backend.core.exceptions import NotFoundError
from backend.adapters.bddProvider.sqlLite.models.autoArchiveConfig import AutoArchiveConfig
from backend.core.models.email import Email
from backend.core.services.llm.service import LlmService
from backend.ports.emailStorage import EmailStorage
from backend.ports.settingsStorage import SettingsStorage

logger = logging.getLogger(__name__)

_SETTING_KEY = "auto_archive_rules"


class AutoArchiveService:

    def __init__(self, llm_service: LlmService, storage: EmailStorage, settings: SettingsStorage) -> None:
        self._llm = llm_service
        self._storage = storage
        self._settings = settings

    def evaluate_and_apply(self, email: Email) -> None:
        config = self._load_config()
        if not config.enabled or not config.rules:
            return
        try:
            snippet = email.snippet or (email.body_text[:400] if email.body_text else "")
            decision = self._llm.evaluate_archive_decision(
                rules=config.rules,
                subject=email.subject or "",
                snippet=snippet,
                from_address=email.from_address.email,
            )
            if decision == ArchiveDecision.YES:
                self._storage.archive_email_locally(email.id)
            elif decision == ArchiveDecision.UNCERTAIN:
                self._storage.set_pending_archive(email.id, pending=True)
        except Exception as exc:  # pylint: disable=broad-except
            logger.warning("Auto-archivage échoué pour %s : %s", email.id, exc)

    def confirm_archive(self, email_id: str) -> None:
        if not self._storage.set_pending_archive(email_id, pending=False):
            raise NotFoundError(f"Email introuvable : {email_id}")
        self._storage.archive_email_locally(email_id)

    def reject_archive(self, email_id: str) -> None:
        if not self._storage.set_pending_archive(email_id, pending=False):
            raise NotFoundError(f"Email introuvable : {email_id}")

    def get_pending(self) -> list[Email]:
        return self._storage.find_pending_archive_emails()

    def _load_config(self) -> AutoArchiveConfig:
        raw = self._settings.get_setting(_SETTING_KEY)
        if raw is None:
            return AutoArchiveConfig(rules="", enabled=False)
        data = json.loads(raw)
        return AutoArchiveConfig(rules=data["rules"], enabled=data["enabled"])
