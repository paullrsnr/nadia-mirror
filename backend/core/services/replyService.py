from backend.adapters.bddProvider.sqlLite.models.email.suggestReplyResult import SuggestReplyResult
from backend.core.exceptions import NotFoundError
from backend.core.services.llm.service import LlmService
from backend.ports.emailStorage import EmailStorage


class ReplyService:

    def __init__(self, llm_service: LlmService, storage: EmailStorage) -> None:
        self._llm = llm_service
        self._storage = storage

    def suggest_reply(self, email_id: str) -> SuggestReplyResult:
        email = self._storage.find_email_by_id(email_id)
        if email is None:
            raise NotFoundError(f"Email introuvable : {email_id}")

        subject = email.subject or ""
        snippet = email.snippet or (email.body_text[:400] if email.body_text else "")
        from_address = email.from_address.email
        body = email.body_text or ""

        important = self._llm.is_important(subject, snippet, from_address)
        if not important:
            return SuggestReplyResult(important=False, draft=None)

        draft = self._llm.draft_reply(subject, body, from_address)
        self._storage.update_email_draft(email_id, draft)
        return SuggestReplyResult(important=True, draft=draft)
