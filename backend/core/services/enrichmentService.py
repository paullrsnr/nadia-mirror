import logging

from backend.core.models.email import Email
from backend.core.services.autoArchiveService import AutoArchiveService
from backend.core.services.classificationService import ClassificationService
from backend.core.services.replyService import ReplyService

logger = logging.getLogger(__name__)


class EnrichmentService:

    def __init__(
        self,
        classification_service: ClassificationService,
        reply_service: ReplyService,
        auto_archive_service: AutoArchiveService,
    ) -> None:
        self._classification = classification_service
        self._reply = reply_service
        self._auto_archive = auto_archive_service

    def enrich(self, email: Email) -> None:
        self._classify(email)
        self._draft_reply_if_necessary(email)
        self._evaluate_archive(email)

    def _classify(self, email: Email) -> None:
        try:
            self._classification.classify_one(email.id)
        except Exception as exc:  # pylint: disable=broad-except
            logger.warning("Classification automatique échouée pour %s : %s", email.id, exc)

    def _draft_reply_if_necessary(self, email: Email) -> None:
        try:
            self._reply.suggest_reply_if_necessary(email.id)
        except Exception as exc:  # pylint: disable=broad-except
            logger.warning("Brouillon automatique échoué pour %s : %s", email.id, exc)

    def _evaluate_archive(self, email: Email) -> None:
        self._auto_archive.evaluate_and_apply(email)
