from abc import ABC, abstractmethod

from backend.core.models.email import AttachmentContent, EmailAttachment


class AttachmentStorage(ABC):

    @abstractmethod
    def save_attachment(self, draft_id: str, filename: str, content: bytes) -> EmailAttachment:
        """Enregistre une pièce jointe pour un brouillon et retourne ses métadonnées."""

    @abstractmethod
    def list_attachments(self, draft_id: str) -> list[EmailAttachment]:
        """Liste les pièces jointes stockées pour un brouillon."""

    @abstractmethod
    def read_attachment(self, draft_id: str, attachment_id: str) -> AttachmentContent:
        """Lit le contenu binaire d'une pièce jointe d'un brouillon."""

    @abstractmethod
    def delete_attachment(self, draft_id: str, attachment_id: str) -> None:
        """Supprime une pièce jointe d'un brouillon. Idempotent si déjà absente."""

    @abstractmethod
    def delete_draft_attachments(self, draft_id: str) -> None:
        """Supprime toutes les pièces jointes d'un brouillon. Idempotent."""
