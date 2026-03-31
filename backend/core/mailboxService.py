import logging
from datetime import datetime, timedelta
from typing import Optional

from backend.core.providers import (
    Provider,
    LIST_PROVIDERS,
    CONNECTABLE_PROVIDERS,
    DEFAULT_PROVIDER,
    MSG_UNAUTHENTICATED,
)
from backend.core.exceptions import AuthError
from backend.ports.emailProviderGateway import EmailProviderGateway
from backend.ports.emailStorage import EmailStorage
from backend.ports.credentialGateway import CredentialGateway
from backend.core.models.email import EmailListQuery, EmailListResult
from backend.core.models.email import SyncResult, SyncAllResult, ProviderSyncResult
from backend.utils.textCleaner import normalize_string

logger = logging.getLogger(__name__)


class MailboxService:
    def __init__(
        self,
        storage: EmailStorage,
        email_provider_gateway: EmailProviderGateway,
        credential_gateway: CredentialGateway,
        sync_min_interval_minutes: int = 5,
        llm_service: Optional[object] = None,
    ) -> None:
        self._storage = storage
        self._email_provider_gateway = email_provider_gateway
        self._credentials = credential_gateway
        self._sync_min_interval = sync_min_interval_minutes
        self._llm = llm_service


    def get_stored_emails(
        self,
        provider: str | None,
        max_results: int = 50,
        page: int = 1,
    ) -> EmailListResult:
        normalized = normalize_string(provider)
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
        normalized = normalize_string(provider)
        if normalized not in LIST_PROVIDERS:
            normalized = DEFAULT_PROVIDER

        if normalized == Provider.ALL.value:
            try:
                return self._sync_all_providers(max_results)
            except AuthError as e:
                return SyncResult(status="error", message=str(e))
        try:
            return self._sync_single_provider(normalized, max_results)
        except AuthError as e:
            return SyncResult(status="error", message=str(e))

    def _sync_all_providers(self, max_results: int) -> SyncAllResult:
        results: list[ProviderSyncResult] = []
        for provider_key in CONNECTABLE_PROVIDERS:
            credentials = self._credentials.load(provider_key)
            if not credentials:
                continue
            try:
                sync_result = self._do_sync(provider_key, max_results, skip_cooldown=True)
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

        return self._do_sync(provider, max_results, skip_cooldown=False)

    def _do_sync(
        self, provider_tag: str, max_results: int, skip_cooldown: bool
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
            page_result = self._email_provider_gateway.fetch_emails(
                provider=provider_tag,
                max_results=max_results,
                query=query_unread,
            )

            if not page_result.emails:
                query_all = EmailListQuery(unread_only=False, after_date=after)
                page_result = self._email_provider_gateway.fetch_emails(
                    provider=provider_tag,
                    max_results=max_results,
                    query=query_all,
                )

            saved_count = 0
            tag = provider_tag.lower()
            for email in page_result.emails:
                is_new = self._storage.save_email(email, provider=tag)
                if is_new:
                    saved_count += 1
                    self._auto_classify(email)

            # Sync des emails envoyés pour avoir les discussions complètes
            try:
                sent_result = self._email_provider_gateway.fetch_emails(
                    provider=provider_tag,
                    max_results=50,
                    query=EmailListQuery(unread_only=False, after_date=after, sent_only=True),
                )
                for email in sent_result.emails:
                    self._storage.save_email(email, provider=tag)
            except Exception as exc:  # pylint: disable=broad-except
                logger.warning("Sync emails envoyés échoué pour %s : %s", provider_tag, exc)

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

    def _auto_classify(self, email) -> None:
        if self._llm is None:
            return
        try:
            from backend.core.models.llm import ClassifyEmailRequest
            category = self._llm.classify_email(ClassifyEmailRequest(
                subject=email.subject or "",
                snippet=email.snippet or (email.body_text[:400] if email.body_text else ""),
                from_address=email.from_address.email,
            ))
            self._storage.update_email_category(email.id, category)
        except Exception as exc:  # pylint: disable=broad-except
            logger.warning("Classification automatique échouée pour %s : %s", email.id, exc)
