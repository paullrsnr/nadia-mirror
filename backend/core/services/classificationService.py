from backend.adapters.bddProvider.sqlLite.models.email.classifyAllResult import ClassifyAllResult
from backend.adapters.bddProvider.sqlLite.models.email.classifyResult import ClassifyResult
from backend.core.exceptions import NotFoundError
from backend.core.models.llm import ClassifyEmailRequest
from backend.core.services.llm.service import LlmService
from backend.ports.emailStorage import EmailStorage


class ClassificationService:

    def __init__(self, llm_service: LlmService, storage: EmailStorage) -> None:
        self._llm = llm_service
        self._storage = storage

    def classify_one(self, email_id: str) -> ClassifyResult:
        email = self._storage.find_email_by_id(email_id)
        if email is None:
            raise NotFoundError(f"Email introuvable : {email_id}")

        category = self._llm.analyze_email_category(ClassifyEmailRequest(
            subject=email.subject or "",
            snippet=email.snippet or (email.body_text[:400] if email.body_text else ""),
            from_address=email.from_address.email,
        ))
        self._storage.update_email_category(email_id, category)
        return ClassifyResult(email_id=email_id, category=category)

    def classify_all_uncategorized(self, limit: int = 20) -> ClassifyAllResult:
        emails = self._storage.find_uncategorized_emails(limit=limit)
        results: list[ClassifyResult] = []
        for email in emails:
            try:
                category = self._llm.analyze_email_category(ClassifyEmailRequest(
                    subject=email.subject or "",
                    snippet=email.snippet or (email.body_text[:400] if email.body_text else ""),
                    from_address=email.from_address.email,
                ))
                self._storage.update_email_category(email.id, category)
                results.append(ClassifyResult(email_id=email.id, category=category))
            except ValueError:
                # LLM non chargé — on arrête
                break
        return ClassifyAllResult(classified=len(results), results=results)
