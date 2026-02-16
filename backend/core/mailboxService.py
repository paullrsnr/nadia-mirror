# pylint: disable=invalid-name,too-few-public-methods
"""Service boîte mail : liste depuis SQLite + synchronisation depuis le provider (Gmail/Outlook)."""
from datetime import datetime, timedelta

from fastapi import HTTPException

from backend.config.settings import storage_settings
from backend.config.providers import (
    EmailProvider,
    LIST_PROVIDERS,
    CONNECTABLE_PROVIDERS,
    DEFAULT_PROVIDER,
    MSG_UNAUTHENTICATED,
    MSG_INVALID_PROVIDER,
)
from backend.config.adapterRegistry import AdapterRegistry
from backend.core.models.email import EmailListQuery, EmailListResult
from backend.core.models.Email import SyncResult, SyncAllResult, ProviderSyncResult
from backend.core.services.connectionOrchestrator import get_connection_credentials
from backend.database import SqliteStorage


class MailboxService:
    """Liste les emails stockés (SQLite) et synchronise depuis un provider (non lus → SQLite).

    - get_stored_emails : lecture locale, filtrée par boîte (gmail / outlook / all).
    - sync_emails : récupère les non lus depuis le(s) provider(s), enregistre dans SQLite.
    """

    def __init__(self) -> None:
        self._storage = SqliteStorage()

    def _normalize_provider(self, provider: str | None, default: str = DEFAULT_PROVIDER) -> str:
        """Normalise le provider (strip, lower, fallback)."""
        return (provider or "").strip().lower() or default

    def get_stored_emails(
        self,
        provider: str | None,
        max_results: int = 50,
        page: int = 1,
    ) -> EmailListResult:
        """Retourne les emails déjà en base (paginés). provider : gmail, outlook ou all."""
        normalized = self._normalize_provider(provider)
        if normalized not in LIST_PROVIDERS:
            normalized = DEFAULT_PROVIDER

        offset = (page - 1) * max_results
        provider_filter = None if normalized == EmailProvider.ALL.value else normalized
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
        provider: str | None,
        max_results: int = 100,
    ) -> SyncResult | SyncAllResult:
        """Synchronise les non lus depuis le(s) provider(s) vers le stockage local.

        Si provider=all, synchronise Gmail puis Outlook (ceux qui sont connectés).
        Sinon, synchronise uniquement le provider demandé (requiert credentials).
        """
        normalized = self._normalize_provider(provider)
        if normalized not in LIST_PROVIDERS:
            normalized = DEFAULT_PROVIDER

        if normalized == EmailProvider.ALL.value:
            return self._sync_all_providers(max_results)

        return self._sync_single_provider(normalized, max_results)

    def _sync_all_providers(self, max_results: int) -> SyncAllResult:
        """Synchronise Gmail et Outlook (ceux qui sont connectés)."""
        results: list[ProviderSyncResult] = []
        for provider_key in CONNECTABLE_PROVIDERS:
            credentials = get_connection_credentials(provider_key)
            if not credentials:
                continue
            try:
                adapter = self._create_adapter(provider_key)
                sync_result = self._do_sync(adapter, provider_key, max_results, skip_cooldown=True)
                results.append(ProviderSyncResult(
                    provider=provider_key,
                    status=sync_result.status,
                    message=sync_result.message,
                    synced=sync_result.synced,
                    saved=sync_result.saved,
                    timestamp=sync_result.timestamp,
                ))
            except Exception as e:
                results.append(ProviderSyncResult(
                    provider=provider_key,
                    status="error",
                    message=str(e),
                ))

        if not results:
            raise HTTPException(
                status_code=401, detail=f"{MSG_UNAUTHENTICATED} (aucune boîte)"
            )

        self._storage.update_last_sync_time()
        return SyncAllResult(status="success", results=results)

    def _sync_single_provider(self, provider: str, max_results: int) -> SyncResult:
        """Synchronise un seul provider (gmail ou outlook)."""
        credentials = get_connection_credentials(provider)
        if not credentials:
            raise HTTPException(status_code=401, detail=MSG_UNAUTHENTICATED)

        adapter = self._create_adapter(provider)
        return self._do_sync(adapter, provider, max_results, skip_cooldown=False)

    def _create_adapter(self, provider: str):
        """Crée l'adapter pour le provider (gmail ou outlook)."""
        adapter_class = AdapterRegistry.get_adapter_class(provider)
        if not adapter_class:
            raise HTTPException(status_code=400, detail=MSG_INVALID_PROVIDER)
        return adapter_class()

    def _do_sync(
        self, adapter, provider_tag: str, max_results: int, skip_cooldown: bool
    ) -> SyncResult:
        """Effectue la synchronisation pour un adapter donné."""
        try:
            if not skip_cooldown:
                last_sync = self._storage.get_last_sync_time()
                min_interval = timedelta(minutes=storage_settings.SYNC_MIN_INTERVAL_MINUTES)
                if last_sync and (datetime.now() - last_sync) < min_interval:
                    return SyncResult(
                        status="skipped",
                        message="Déjà à jour",
                        last_sync=last_sync.isoformat(),
                    )

            after = (datetime.now() - timedelta(days=7)).date()
            # Essayer d'abord les non lus, puis tous les emails récents si aucun non lu
            query_unread = EmailListQuery(unread_only=True, after_date=after)
            page_result = adapter.get_emails(max_results=max_results, query=query_unread)
            
            # Si aucun email non lu trouvé, récupérer tous les emails récents
            if not page_result.emails:
                query_all = EmailListQuery(unread_only=False, after_date=after)
                page_result = adapter.get_emails(max_results=max_results, query=query_all)

            saved_count = 0
            tag = provider_tag.lower()
            for email in page_result.emails:
                if self._storage.save_email(email, provider=tag):
                    saved_count += 1

            if not skip_cooldown:
                self._storage.update_last_sync_time()

            return SyncResult(
                status="success",
                synced=len(page_result.emails),
                saved=saved_count,
                timestamp=datetime.now().isoformat(),
            )
        except ValueError as e:
            return SyncResult(status="error", message=str(e))
        except RuntimeError as e:
            return SyncResult(status="error", message=f"Erreur de synchronisation: {str(e)}")
