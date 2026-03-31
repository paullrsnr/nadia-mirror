from backend.core.models.llm import ClassifyEmailRequest
from backend.core.services.llm.service import LlmService
from backend.ports.emailStorage import EmailStorage


class ClassificationService:

    def __init__(self, llm_service: LlmService, storage: EmailStorage) -> None:
        self._llm = llm_service
        self._storage = storage

    def classify_one(self, email_id: str) -> dict | None:
        email = self._storage.find_email_by_id(email_id)
        if email is None:
            return None

        category = self._llm.classify_email(ClassifyEmailRequest(
            subject=email.subject or "",
            snippet=email.snippet or (email.body_text[:400] if email.body_text else ""),
            from_address=email.from_address.email,
        ))
        self._storage.update_email_category(email_id, category)
        return {"email_id": email_id, "category": category}

    def classify_all_uncategorized(self, limit: int = 20) -> dict:
        emails = self._storage.find_uncategorized_emails(limit=limit)
        results = []
        for email in emails:
            try:
                category = self._llm.classify_email(ClassifyEmailRequest(
                    subject=email.subject or "",
                    snippet=email.snippet or (email.body_text[:400] if email.body_text else ""),
                    from_address=email.from_address.email,
                ))
                self._storage.update_email_category(email.id, category)
                results.append({"email_id": email.id, "category": category})
            except ValueError:
                # LLM non chargé — on arrête
                break
        return {"classified": len(results), "results": results}
