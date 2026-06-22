import logging
import threading
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
from backend.core.models.email import Email, EmailListQuery, EmailListResult
from backend.core.models.email import SyncResult, SyncAllResult, ProviderSyncResult
from backend.core.models.email.sync.syncLaunchResult import SyncLaunchResult
from backend.core.models.email.sync.syncStatusResult import SyncStatusResult
from backend.core.models.email.emailThread import EmailThread
from backend.core.exceptions import NotFoundError
from backend.core.services.enrichmentService import EnrichmentService
from backend.utils.textCleaner import normalize_string

logger = logging.getLogger(__name__)

_LLM_ENRICH_CAP = 20
_FIRST_SYNC_LOOKBACK_DAYS = 30


class MailboxService:
    def __init__(
        self,
        storage: EmailStorage,
        email_provider_gateway: EmailProviderGateway,
        credential_gateway: CredentialGateway,
        enrichment_service: EnrichmentService,
        sync_min_interval_minutes: int = 5,
    ) -> None:
        self._storage = storage
        self._email_provider_gateway = email_provider_gateway
        self._credentials = credential_gateway
        self._sync_min_interval = sync_min_interval_minutes
        self._enrichment = enrichment_service
        self._sync_lock = threading.Lock()
        self._sync_running = False
        self._last_sync_result: Optional[SyncResult | SyncAllResult] = None

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

    def get_thread(self, thread_id: str) -> EmailThread:
        emails = self._storage.find_emails_by_thread_id(thread_id)
        if not emails:
            raise NotFoundError(f"Discussion introuvable : {thread_id}")
        seen: set[str] = set()
        participants = [
            e.from_address for e in emails
            if e.from_address.email not in seen and not seen.add(e.from_address.email)  # type: ignore[func-returns-value]
        ]
        return EmailThread(
            thread_id=thread_id,
            subject=emails[0].subject,
            emails=emails,
            participants=participants,
            last_message_date=max(e.date for e in emails),
        )

    def sync_emails(
        self,
        provider: str | None,
        max_results: int = 100,
        full_sync: bool = False,
    ) -> SyncLaunchResult:
        with self._sync_lock:
            if self._sync_running:
                return SyncLaunchResult(status="already_running")
            self._sync_running = True

        threading.Thread(
            target=self._run_sync_background,
            args=(provider, max_results, full_sync),
            daemon=True,
        ).start()

        return SyncLaunchResult(status="started")

    def get_sync_status(self) -> SyncStatusResult:
        if self._sync_running:
            return SyncStatusResult(status="running")
        return SyncStatusResult(status="idle", last_result=self._last_sync_result)

    def _run_sync_background(self, provider: str | None, max_results: int, full_sync: bool = False) -> None:
        try:
            normalized = normalize_string(provider)
            if normalized not in LIST_PROVIDERS:
                normalized = DEFAULT_PROVIDER

            if normalized == Provider.ALL.value:
                try:
                    result = self._sync_all_providers(max_results, full_sync)
                except AuthError as e:
                    result = SyncResult(status="error", message=str(e))
            else:
                try:
                    result = self._sync_single_provider(normalized, max_results, full_sync)
                except AuthError as e:
                    result = SyncResult(status="error", message=str(e))

            self._last_sync_result = result
        except Exception as exc:  # pylint: disable=broad-except
            logger.exception("Erreur sync background : %s", exc)
            self._last_sync_result = SyncResult(status="error", message=str(exc))
        finally:
            with self._sync_lock:
                self._sync_running = False

    def _sync_all_providers(self, max_results: int, full_sync: bool = False) -> SyncAllResult:
        results = [
            self._sync_provider_safely(provider_key, max_results, full_sync)
            for provider_key in CONNECTABLE_PROVIDERS
            if self._credentials.load(provider_key)
        ]

        if not results:
            raise AuthError(f"{MSG_UNAUTHENTICATED} (aucune boîte)")

        self._storage.update_last_sync_time()
        return SyncAllResult(status="success", results=results)

    def _sync_provider_safely(self, provider_key: str, max_results: int, full_sync: bool = False) -> ProviderSyncResult:
        try:
            r = self._do_sync(provider_key, max_results, skip_cooldown=True, full_sync=full_sync)
            return ProviderSyncResult(
                provider=provider_key,
                status=r.status,
                message=r.message,
                synced=r.synced,
                saved=r.saved,
                timestamp=r.timestamp,
            )
        except Exception as e:  # pylint: disable=broad-except
            return ProviderSyncResult(provider=provider_key, status="error", message=str(e))

    def _sync_single_provider(self, provider: str, max_results: int, full_sync: bool = False) -> SyncResult:
        if not self._credentials.load(provider):
            raise AuthError(MSG_UNAUTHENTICATED)
        return self._do_sync(provider, max_results, skip_cooldown=False, full_sync=full_sync)

    def _do_sync(
        self, provider_tag: str, max_results: int, skip_cooldown: bool, full_sync: bool = False
    ) -> SyncResult:
        try:
            skipped = self._check_cooldown(skip_cooldown or full_sync)
            if skipped:
                return skipped

            after = self._compute_after_date(full_sync)
            tag = provider_tag.lower()

            page_result = self._fetch_inbox_emails(provider_tag, max_results, after)
            new_ids = self._storage.upsert_emails_batch(page_result.emails, provider=tag)
            new_emails = [e for e in page_result.emails if e.id in set(new_ids)]

            if new_emails:
                self._enrich_new_emails(new_emails[:_LLM_ENRICH_CAP])

            self._sync_sent_emails(provider_tag, tag, after)

            if not skip_cooldown:
                self._storage.update_last_sync_time()

            return SyncResult(
                status="success",
                synced=len(page_result.emails),
                saved=len(new_ids),
                timestamp=datetime.now().isoformat(),
            )
        except ValueError as e:
            return SyncResult(status="error", message=str(e))
        except RuntimeError as e:
            return SyncResult(status="error", message=f"Erreur de synchronisation: {str(e)}")

    def _check_cooldown(self, skip_cooldown: bool) -> Optional[SyncResult]:
        if skip_cooldown:
            return None
        last_sync = self._storage.get_last_sync_time()
        if last_sync and (datetime.now() - last_sync) < timedelta(minutes=self._sync_min_interval):
            return SyncResult(status="skipped", message="Déjà à jour", last_sync=last_sync.isoformat())
        return None

    def _fetch_inbox_emails(self, provider_tag: str, max_results: int, after):
        page_result = self._email_provider_gateway.fetch_emails(
            provider=provider_tag,
            max_results=max_results,
            query=EmailListQuery(unread_only=True, after_date=after),
        )
        if not page_result.emails:
            page_result = self._email_provider_gateway.fetch_emails(
                provider=provider_tag,
                max_results=max_results,
                query=EmailListQuery(unread_only=False, after_date=after),
            )
        return page_result

    def _sync_sent_emails(self, provider_tag: str, tag: str, after) -> None:
        try:
            sent = self._email_provider_gateway.fetch_emails(
                provider=provider_tag,
                max_results=50,
                query=EmailListQuery(unread_only=False, after_date=after, sent_only=True),
            )
            self._storage.upsert_emails_batch(sent.emails, provider=tag)
        except Exception as exc:  # pylint: disable=broad-except
            logger.warning("Sync emails envoyés échoué pour %s : %s", provider_tag, exc)

    def _compute_after_date(self, full_sync: bool = False):
        if not full_sync:
            last_sync = self._storage.get_last_sync_time()
            if last_sync:
                return last_sync.date()
        return (datetime.now() - timedelta(days=_FIRST_SYNC_LOOKBACK_DAYS)).date()

    def _enrich_new_emails(self, emails: list[Email]) -> None:
        for email in emails:
            self._enrichment.enrich(email)
