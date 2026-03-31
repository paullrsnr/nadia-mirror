from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional

from backend.core.models.email import Email


class EmailStorage(ABC):

    @abstractmethod
    def save_email(self, email: Email, provider: str) -> bool:
        """Sauvegarde un email. Retourne True si créé, False si déjà présent."""

    @abstractmethod
    def find_emails(
        self,
        max_results: int = 50,
        offset: int = 0,
        provider_filter: str | None = None,
    ) -> tuple[list[Email], int]:
        """Retourne (emails paginés, total) depuis le stockage local.

        provider_filter=None → toutes les boîtes.
        """

    @abstractmethod
    def get_last_sync_time(self) -> Optional[datetime]:
        """Timestamp de la dernière synchronisation, ou None."""

    @abstractmethod
    def update_last_sync_time(self) -> None:
        """Met à jour le timestamp de dernière synchronisation."""

    @abstractmethod
    def find_emails_by_thread(self, thread_id: str) -> list[Email]:
        """Retourne tous les emails d'un même fil de discussion, triés par date."""
