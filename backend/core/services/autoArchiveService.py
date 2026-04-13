import json
import logging

from backend.core.archiveDecision import ArchiveDecision
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
        except ValueError as exc:
            logger.warning("Auto-archivage échoué pour %s : %s", email.id, exc)
            return

        if decision == ArchiveDecision.YES:
            self._storage.archive_email_locally(email.id)
        elif decision == ArchiveDecision.UNCERTAIN:
            self._storage.update_pending_archive(email.id, pending=True)

    def confirm_archive(self, email_id: str) -> None:
        self._storage.update_pending_archive(email_id, pending=False)
        self._storage.archive_email_locally(email_id)

    def reject_archive(self, email_id: str) -> None:
        self._storage.update_pending_archive(email_id, pending=False)

    def get_pending(self) -> list[Email]:
        return self._storage.find_pending_archive_emails()

    def get_rules(self) -> AutoArchiveConfig:
        return self._load_config()

    def save_rules(self, rules: str) -> AutoArchiveConfig:
        config = AutoArchiveConfig(rules=rules, enabled=bool(rules.strip()))
        self._settings.set_setting(
            _SETTING_KEY,
            json.dumps({"rules": config.rules, "enabled": config.enabled}, ensure_ascii=False),
        )
        return config

    def _load_config(self) -> AutoArchiveConfig:
        raw = self._settings.get_setting(_SETTING_KEY)
        if raw is None:
            return AutoArchiveConfig(rules="", enabled=False)
        data = json.loads(raw)
        return AutoArchiveConfig(rules=data["rules"], enabled=data["enabled"])
