from datetime import datetime, timedelta

from backend.core.providers import (
    Provider,
    LIST_PROVIDERS,
    CONNECTABLE_PROVIDERS,
    DEFAULT_PROVIDER,
    MSG_UNAUTHENTICATED,
    MSG_INVALID_PROVIDER,
)
from backend.core.exceptions import AuthError, ProviderError
from backend.ports.emailProviderGateway import EmailProviderGateway
from backend.ports.emailStorage import EmailStorage
from backend.ports.credentialGateway import CredentialGateway
from backend.core.models.email import EmailListQuery, EmailListResult
from backend.core.models.email import SyncResult, SyncAllResult, ProviderSyncResult


class MailboxService:
    def __init__(
        self,
        storage: EmailStorage,
        email_provider_gateway: EmailProviderGateway,
        credential_gateway: CredentialGateway,
        sync_min_interval_minutes: int = 5,
    ) -> None:
        self._storage = storage
        self._email_provider_gateway = email_provider_gateway
        self._credentials = credential_gateway
        self._sync_min_interval = sync_min_interval_minutes


    def get_stored_emails(
        self,
        provider: str | None,
        max_results: int = 50,
        page: int = 1,
    ) -> EmailListResult:
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

    def _create_adapter(self, provider: str):
        return self._email_provider_gateway.create(provider)

    def _do_sync(
        self, adapter, provider_tag: str, max_results: int, skip_cooldown: bool
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

    def _normalize_provider(self, provider: str | None, default: str = DEFAULT_PROVIDER) -> str:
        return (provider or "").strip().lower() or default