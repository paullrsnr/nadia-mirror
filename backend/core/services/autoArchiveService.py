import json
import logging
from pathlib import Path

from backend.core.models.email import Email
from backend.core.services.llm.service import LlmService
from backend.ports.emailStorage import EmailStorage

logger = logging.getLogger(__name__)

_RULES_FILENAME = "auto_archive_rules.json"


class AutoArchiveService:

    def __init__(self, llm_service: LlmService, storage: EmailStorage, data_dir: Path) -> None:
        self._llm = llm_service
        self._storage = storage
        self._rules_file = data_dir / _RULES_FILENAME

    def get_rules(self) -> dict:
        if not self._rules_file.exists():
            return {"rules": "", "enabled": False}
        return json.loads(self._rules_file.read_text(encoding="utf-8"))

    def save_rules(self, rules: str) -> dict:
        data = {"rules": rules, "enabled": bool(rules.strip())}
        self._rules_file.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        return data

    def evaluate_and_apply(self, email: Email) -> None:
        config = self.get_rules()
        if not config.get("enabled") or not config.get("rules"):
            return
        try:
            snippet = email.snippet or (email.body_text[:400] if email.body_text else "")
            decision = self._llm.evaluate_archive_decision(
                rules=config["rules"],
                subject=email.subject or "",
                snippet=snippet,
                from_address=email.from_address.email,
            )
            if decision == "oui":
                self._storage.archive_email_locally(email.id)
            elif decision == "incertain":
                self._storage.set_pending_archive(email.id, pending=True)
        except Exception as exc:  # pylint: disable=broad-except
            logger.warning("Auto-archivage échoué pour %s : %s", email.id, exc)

    def confirm_archive(self, email_id: str) -> bool:
        self._storage.set_pending_archive(email_id, pending=False)
        return self._storage.archive_email_locally(email_id)

    def reject_archive(self, email_id: str) -> bool:
        return self._storage.set_pending_archive(email_id, pending=False)

    def get_pending(self) -> list[Email]:
        return self._storage.find_pending_archive_emails()
