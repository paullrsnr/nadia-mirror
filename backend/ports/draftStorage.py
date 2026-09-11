from abc import ABC, abstractmethod
from typing import Optional

from backend.core.models.email import DraftEmail


class DraftStorage(ABC):

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
