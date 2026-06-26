from backend.adapters.mailProvider.emailProviderGatewayAdapter import EmailProviderGatewayAdapter
from backend.adapters.authProvider.credentialGatewayAdapter import CredentialGatewayAdapter
from backend.adapters.authProvider.oauthGatewayAdapter import OAuthGatewayAdapter
from backend.core.mailboxService import MailboxService
from backend.core.services.authService import AuthService
from backend.core.services.emailsService import EmailsService
from backend.core.services.classificationService import ClassificationService
from backend.core.services.replyService import ReplyService
from backend.core.services.draftService import DraftService
from backend.core.services.autoArchiveService import AutoArchiveService
from backend.core.services.enrichmentService import EnrichmentService
from backend.adapters.bddProvider.sqlLite import SqliteStorageAdapter
from backend.adapters.fileProvider.draftAttachmentFileStorage import DraftAttachmentFileStorage

from backend.adapters.llm.llmGatewayAdapter import LlmGatewayAdapter
from backend.config.settings import storage_settings
from backend.core.services.llm.service import LlmService


_credential_gateway = CredentialGatewayAdapter()
_oauth_gateway = OAuthGatewayAdapter()
_email_provider_gateway = EmailProviderGatewayAdapter()
_storage_adapter = SqliteStorageAdapter()
_attachment_storage = DraftAttachmentFileStorage()

_llm_service = LlmService(LlmGatewayAdapter())

_classification_service = ClassificationService(
    llm_service=_llm_service,
    storage=_storage_adapter,
)

_reply_service = ReplyService(
    llm_service=_llm_service,
    storage=_storage_adapter,
)

_auto_archive_service = AutoArchiveService(
    llm_service=_llm_service,
    storage=_storage_adapter,
    settings=_storage_adapter,
)

_enrichment_service = EnrichmentService(
    classification_service=_classification_service,
    reply_service=_reply_service,
    auto_archive_service=_auto_archive_service,
)

_mailbox_service = MailboxService(
    storage=_storage_adapter,
    email_provider_gateway=_email_provider_gateway,
    credential_gateway=_credential_gateway,
    sync_min_interval_minutes=storage_settings.SYNC_MIN_INTERVAL_MINUTES,
    enrichment_service=_enrichment_service,
)

_emails_service = EmailsService(
    email_provider_gateway=_email_provider_gateway,
    credential_gateway=_credential_gateway,
    storage=_storage_adapter,
)

_auth_service = AuthService(
    oauth_gateway=_oauth_gateway,
    credential_gateway=_credential_gateway,
)

_draft_service = DraftService(
    email_provider_gateway=_email_provider_gateway,
    credential_gateway=_credential_gateway,
    storage=_storage_adapter,
    attachment_storage=_attachment_storage,
)


def get_auth_service() -> AuthService:
    return _auth_service


def get_mailbox_service() -> MailboxService:
    return _mailbox_service


def get_emails_service() -> EmailsService:
    return _emails_service


def get_llm_service() -> LlmService:
    return _llm_service


def get_storage() -> SqliteStorageAdapter:
    return _storage_adapter


def get_classification_service() -> ClassificationService:
    return _classification_service


def get_reply_service() -> ReplyService:
    return _reply_service


def get_auto_archive_service() -> AutoArchiveService:
    return _auto_archive_service


def get_draft_service() -> DraftService:
    return _draft_service
