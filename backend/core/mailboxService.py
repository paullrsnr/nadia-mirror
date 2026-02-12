# pylint: disable=invalid-name,too-few-public-methods
"""Service boîte mail : liste depuis SQLite + synchronisation depuis le provider (Gmail/Outlook)."""
from datetime import datetime, timedelta

from backend.config.settings import storage_settings
from backend.core.models.email import EmailListResult
from backend.ports.emailProvider import EmailProvider
from backend.database.email_storage import SqliteStorage


class MailboxService:
    """Liste les emails stockés (SQLite) et synchronise depuis un provider (non lus → SQLite).

    - get_stored_emails : lecture locale, filtrée par boîte (gmail / outlook / all).
    - sync_emails : récupère les non lus via l'adapter, les enregistre avec un tag provider.
    """

    def __init__(self) -> None:
        self._storage = SqliteStorage()

    def get_stored_emails(
        self,
        provider: str,
        max_results: int = 50,
        page: int = 1,
    ) -> EmailListResult:
        """Retourne les emails déjà en base (paginés). provider : gmail, outlook ou all."""
        offset = (page - 1) * max_results
        provider_filter = None if (provider or "").lower() == "all" else (provider or "gmail")
        emails, total = self._storage.get_emails(
            max_results=max_results,
            offset=offset,
            provider_filter=provider_filter,
        )
        return EmailListResult(
            emails=emails,
            total=total,
            page=page,
            page_size=max_results,
        )

    def sync_emails(
        self,
        adapter: EmailProvider,
        provider_tag: str,
        max_results: int = 100,
        skip_cooldown: bool = False,
    ) -> dict:
        """Sync non lus depuis l'adapter vers le stockage. provider_tag : gmail ou outlook.
        skip_cooldown=True pour enchaîner plusieurs sync (ex. « toutes les boîtes »).
        """
        try:
            if not skip_cooldown:
                last_sync = self._storage.get_last_sync_time()
                min_interval = timedelta(minutes=storage_settings.SYNC_MIN_INTERVAL_MINUTES)
                if last_sync and (datetime.now() - last_sync) < min_interval:
                    return {
                        "status": "skipped",
                        "message": "Déjà à jour",
                        "last_sync": last_sync.isoformat(),
                    }

            after_date = (datetime.now() - timedelta(days=7)).strftime("%Y/%m/%d")
            query = f"is:unread after:{after_date}"
            page_result = adapter.get_emails(max_results=max_results, query=query)

            saved_count = 0
            tag = (provider_tag or "gmail").lower()
            for email in page_result.emails:
                if self._storage.save_email(email, provider=tag):
                    saved_count += 1

            if not skip_cooldown:
                self._storage.update_last_sync_time()

            return {
                "status": "success",
                "synced": len(page_result.emails),
                "saved": saved_count,
                "timestamp": datetime.now().isoformat(),
            }
        except ValueError as e:
            return {"status": "error", "message": str(e)}
        except RuntimeError as e:
            return {"status": "error", "message": f"Erreur de synchronisation: {str(e)}"}

    def update_last_sync_time(self) -> None:
        """Met à jour le timestamp de dernière sync (ex. après sync « toutes les boîtes »)."""
        self._storage.update_last_sync_time()
