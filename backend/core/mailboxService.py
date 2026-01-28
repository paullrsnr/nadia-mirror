# pylint: disable=invalid-name,too-few-public-methods
"""Service de gestion de la boîte mail."""
import logging
from datetime import datetime, timedelta
from typing import Optional

from backend.adapters.gmailAdapter import GmailAdapter
from backend.adapters.sqliteStorage import SqliteStorage

logger = logging.getLogger(__name__)


class MailboxService:
    """Service pour gérer la synchronisation et le stockage des emails."""

    def __init__(self):
        self.storage = SqliteStorage()

    def sync_emails(
        self,
        max_results: int = 100,
        query: Optional[str] = None,
        force: bool = False,
    ) -> dict:
        """Synchronise les emails depuis Gmail vers le stockage local."""
        try:
            adapter = GmailAdapter()

            # Si force=False, ne synchroniser que les nouveaux emails
            if not force:
                last_sync = self.storage.get_last_sync_time()
                if last_sync:
                    # Synchroniser seulement les emails des 7 derniers jours
                    query = f"after:{(datetime.now() - timedelta(days=7)).strftime('%Y/%m/%d')}"

            emails, _ = adapter.get_emails(max_results=max_results, query=query)

            # Sauvegarder les emails dans le stockage local
            saved_count = 0
            for email in emails:
                if self.storage.save_email(email):
                    saved_count += 1

            # Mettre à jour le timestamp de dernière synchronisation
            self.storage.update_last_sync_time()

            return {
                "status": "success",
                "synced": len(emails),
                "saved": saved_count,
                "timestamp": datetime.now().isoformat(),
            }
        except ValueError as e:
            return {"status": "error", "message": str(e)}
        except RuntimeError as e:
            return {
                "status": "error",
                "message": f"Erreur de synchronisation: {str(e)}",
            }
