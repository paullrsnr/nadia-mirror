from backend.adapters.mailProvider.emailProviderGatewayAdapter import EmailProviderGatewayAdapter
from backend.adapters.authProvider.credentialGatewayAdapter import CredentialGatewayAdapter
from backend.adapters.authProvider.oauthGatewayAdapter import OAuthGatewayAdapter
from backend.core.mailboxService import MailboxService
from backend.core.services.authService import AuthService
from backend.core.services.emailsService import EmailsService
from backend.core.services.classificationService import ClassificationService
from backend.core.services.replyService import ReplyService
from backend.core.services.autoArchiveService import AutoArchiveService
from backend.adapters.bddProvider.sqlLite import SqliteStorageAdapter
from backend.config.settings import storage_settings
from backend.adapters.llm.llmGatewayAdapter import LlmGatewayAdapter
from backend.core.services.llm.service import LlmService


_credential_gateway = CredentialGatewayAdapter()
_oauth_gateway = OAuthGatewayAdapter()
_email_provider_gateway = EmailProviderGatewayAdapter()
_storage_adapter = SqliteStorageAdapter()

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
    data_dir=storage_settings.DATA_DIR,
)

_mailbox_service = MailboxService(
    storage=_storage_adapter,
    email_provider_gateway=_email_provider_gateway,
    credential_gateway=_credential_gateway,
    sync_min_interval_minutes=storage_settings.SYNC_MIN_INTERVAL_MINUTES,
    llm_service=_llm_service,
    reply_service=_reply_service,
    auto_archive_service=_auto_archive_service,
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
