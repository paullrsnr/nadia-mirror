# pylint: disable=invalid-name,too-few-public-methods
"""Service de gestion de la boîte mail : récupération paginée + persistance SQLite."""
import logging
from datetime import datetime, timedelta

from backend.config.settings import storage_settings
from backend.core.models.email import EmailListResult
from backend.ports.emailProvider import EmailProvider
from backend.adapters.sqliteStorage import SqliteStorage

logger = logging.getLogger(__name__)


class MailboxService:
    """Récupère les derniers emails (non lus / récents) du provider et les stocke en SQLite.

    - Liste emails : lecture depuis SQLite (ce qui existe déjà).
    - Sync : Gmail (non lus uniquement) → SQLite. Délai entre deux syncs géré par le backend.
    """

    def __init__(self, email_provider: EmailProvider):
        self._provider = email_provider
        self._storage = SqliteStorage()

    def get_stored_emails(
        self, max_results: int = 50, page: int = 1
    ) -> EmailListResult:
        """Retourne les emails déjà présents en SQLite (paginés). Pas d'appel Gmail."""
        offset = (page - 1) * max_results
        emails, total = self._storage.get_emails(max_results=max_results, offset=offset)
        return EmailListResult(
            emails=emails,
            total=total,
            page=page,
            page_size=max_results,
        )

    def sync_emails(self, max_results: int = 100) -> dict:
        """Synchronise les derniers emails (non lus, paginés) vers le stockage local.

        Ne fait rien si la dernière sync a eu lieu il y a moins de SYNC_MIN_INTERVAL_MINUTES.
        Sinon : fetch Gmail (is:unread + récents), sauvegarde en SQLite, met à jour last_sync.
        """
        try:
            last_sync = self._storage.get_last_sync_time()
            min_interval = timedelta(minutes=storage_settings.SYNC_MIN_INTERVAL_MINUTES)
            if last_sync and (datetime.now() - last_sync) < min_interval:
                return {
                    "status": "skipped",
                    "message": "Déjà à jour",
                    "last_sync": last_sync.isoformat(),
                }

            # Derniers non lus (Gmail), limités aux 7 derniers jours pour limiter le flux
            after_date = (datetime.now() - timedelta(days=7)).strftime("%Y/%m/%d")
            query = f"is:unread after:{after_date}"
            emails, _ = self._provider.get_emails(
                max_results=max_results,
                query=query,
            )

            saved_count = 0
            for email in emails:
                if self._storage.save_email(email):
                    saved_count += 1

            self._storage.update_last_sync_time()

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
