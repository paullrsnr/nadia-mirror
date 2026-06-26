from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional

from backend.core.models.email import Email, DraftEmail
from backend.core.models.email.category import Category


class EmailStorage(ABC):

    @abstractmethod
    def upsert_email(self, email: Email, provider: str) -> bool:
        """Sauvegarde un email. Retourne True si créé, False si déjà présent."""

    @abstractmethod
    def upsert_emails_batch(self, emails: list[Email], provider: str) -> list[str]:
        """Insère ou met à jour une liste d'emails en une seule transaction.
        Retourne les IDs des emails nouvellement insérés."""

    @abstractmethod
    def find_emails(
        self,
        max_results: int = 50,
        offset: int = 0,
        provider_filter: str | None = None,
        folder: str | None = "inbox",
    ) -> tuple[list[Email], int]:
        """Retourne (emails paginés, total) depuis le stockage local.

        provider_filter=None → toutes les boîtes.
        folder=None → tous les dossiers (inbox + sent).
        """

    @abstractmethod
    def get_last_sync_time(self) -> Optional[datetime]:
        """Timestamp de la dernière synchronisation, ou None."""

    @abstractmethod
    def update_last_sync_time(self) -> None:
        """Met à jour le timestamp de dernière synchronisation."""

    @abstractmethod
    def find_emails_by_thread_id(self, thread_id: str) -> list[Email]:
        """Retourne tous les emails d'un même fil de discussion, triés par date."""

    @abstractmethod
    def find_email_by_id(self, email_id: str) -> Optional[Email]:
        """Retourne un email par son identifiant, ou None s'il n'existe pas."""

    @abstractmethod
    def update_email_category(self, email_id: str, category: str) -> None:
        """Met à jour la catégorie d'un email. Lève NotFoundError si introuvable."""

    @abstractmethod
    def find_uncategorized_emails(self, limit: int = 50) -> list[Email]:
        """Retourne les emails sans catégorie, les plus récents en premier."""

    @abstractmethod
    def get_categories(self) -> list[Category]:
        """Retourne toutes les catégories."""

    @abstractmethod
    def update_email_draft(self, email_id: str, draft: str) -> None:
        """Sauvegarde un brouillon de réponse. Lève NotFoundError si introuvable."""

    @abstractmethod
    def archive_email_locally(self, email_id: str) -> None:
        """Marque l'email comme archivé en local. Lève NotFoundError si introuvable."""

    @abstractmethod
    def update_pending_archive(self, email_id: str, pending: bool) -> None:
        """Marque/démarque un email comme en attente d'archivage. Lève NotFoundError si introuvable."""

    @abstractmethod
    def find_pending_archive_emails(self) -> list[Email]:
        """Retourne les emails en attente de confirmation d'archivage."""

    @abstractmethod
    def set_starred(self, email_id: str, starred: bool) -> None:
        """Marque/démarque un email comme favori. Lève NotFoundError si introuvable."""

    @abstractmethod
    def mark_email_read(self, email_id: str) -> None:
        """Retire le label UNREAD d'un email en local. Lève NotFoundError si introuvable."""

    @abstractmethod
    def save_draft(self, draft: DraftEmail) -> DraftEmail:
        """Crée ou met à jour un brouillon local (upsert par id)."""

    @abstractmethod
    def find_draft_by_id(self, draft_id: str) -> Optional[DraftEmail]:
        """Retourne un brouillon par son identifiant, ou None s'il n'existe pas."""

    @abstractmethod
    def delete_draft(self, draft_id: str) -> None:
        """Supprime un brouillon local. Idempotent si déjà absent."""

    @abstractmethod
    def find_drafts(self, provider: str | None = None) -> list[DraftEmail]:
        """Retourne les brouillons locaux, les plus récemment modifiés en premier."""

