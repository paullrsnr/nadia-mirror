# pylint: disable=invalid-name,too-few-public-methods
"""Service boîte mail : liste depuis le stockage + synchronisation depuis le provider."""
from datetime import datetime, timedelta
from typing import Callable

from backend.core.providers import (
    Provider,
    LIST_PROVIDERS,
    CONNECTABLE_PROVIDERS,
    DEFAULT_PROVIDER,
    MSG_UNAUTHENTICATED,
    MSG_INVALID_PROVIDER,
)
from backend.core.exceptions import AuthError, ProviderError
from backend.ports.emailProvider import EmailProvider as IEmailProvider
from backend.ports.emailStorage import EmailStorage
from backend.ports.credentialGateway import CredentialGateway
from backend.core.models.Email import EmailListQuery, EmailListResult
from backend.core.models.Email import SyncResult, SyncAllResult, ProviderSyncResult


class MailboxService:
    """Liste les emails stockés et synchronise depuis un provider.

    Les dépendances (storage, adapter_factory) sont injectées depuis la couche API.
    Le core ne sait pas quelle base de données ni quel SDK est utilisé.
    """

    def __init__(
        self,
        storage: EmailStorage,
        adapter_factory: Callable[[str], IEmailProvider],
        credential_gateway: CredentialGateway,
        sync_min_interval_minutes: int = 5,
    ) -> None:
        self._storage = storage
        self._adapter_factory = adapter_factory
        self._credentials = credential_gateway
        self._sync_min_interval = sync_min_interval_minutes

    def _normalize_provider(self, provider: str | None, default: str = DEFAULT_PROVIDER) -> str:
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
        provider_filter = None if normalized == Provider.ALL.value else normalized
        emails, total = self._storage.find_emails(
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
        """Synchronise les non lus depuis le(s) provider(s) vers le stockage local."""
        normalized = self._normalize_provider(provider)
        if normalized not in LIST_PROVIDERS:
            normalized = DEFAULT_PROVIDER

        if normalized == Provider.ALL.value:
            return self._sync_all_providers(max_results)

        return self._sync_single_provider(normalized, max_results)

    def _sync_all_providers(self, max_results: int) -> SyncAllResult:
        results: list[ProviderSyncResult] = []
        for provider_key in CONNECTABLE_PROVIDERS:
            credentials = self._credentials.load(provider_key)
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
            raise AuthError(f"{MSG_UNAUTHENTICATED} (aucune boîte)")

        self._storage.update_last_sync_time()
        return SyncAllResult(status="success", results=results)

    def _sync_single_provider(self, provider: str, max_results: int) -> SyncResult:
        credentials = self._credentials.load(provider)
        if not credentials:
            raise AuthError(MSG_UNAUTHENTICATED)

        adapter = self._create_adapter(provider)
        return self._do_sync(adapter, provider, max_results, skip_cooldown=False)

    def _create_adapter(self, provider: str) -> IEmailProvider:
        try:
            return self._adapter_factory(provider)
        except ValueError as e:
            raise ProviderError(MSG_INVALID_PROVIDER) from e

    def _do_sync(
        self, adapter: IEmailProvider, provider_tag: str, max_results: int, skip_cooldown: bool
    ) -> SyncResult:
        try:
            if not skip_cooldown:
                last_sync = self._storage.get_last_sync_time()
                min_interval = timedelta(minutes=self._sync_min_interval)
                if last_sync and (datetime.now() - last_sync) < min_interval:
                    return SyncResult(
                        status="skipped",
                        message="Déjà à jour",
                        last_sync=last_sync.isoformat(),
                    )

            after = (datetime.now() - timedelta(days=7)).date()
            query_unread = EmailListQuery(unread_only=True, after_date=after)
            page_result = adapter.fetch_emails(max_results=max_results, query=query_unread)

            if not page_result.emails:
                query_all = EmailListQuery(unread_only=False, after_date=after)
                page_result = adapter.fetch_emails(max_results=max_results, query=query_all)

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
