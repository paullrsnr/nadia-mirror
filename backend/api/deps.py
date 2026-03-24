from backend.adapters.mailProvider.emailProviderGatewayAdapter import EmailProviderGatewayAdapter
from backend.adapters.authProvider.credentialGatewayAdapter import CredentialGatewayAdapter
from backend.adapters.authProvider.oauthGatewayAdapter import OAuthGatewayAdapter
from backend.core.mailboxService import MailboxService
from backend.core.services.authService import AuthService
from backend.core.services.emailsService import EmailsService
from backend.adapters.bddProvider.sqlLite import SqliteStorageAdapter
from backend.config.settings import storage_settings
from backend.adapters.llm.llama import LlamaCppAdapter
from backend.core.services.llm.service import init_llm_service, LlmService


_credential_gateway = CredentialGatewayAdapter()
_oauth_gateway = OAuthGatewayAdapter()
_email_provider_gateway = EmailProviderGatewayAdapter()
_storage_adapter = SqliteStorageAdapter()

_mailbox_service = MailboxService(
    storage=_storage_adapter,
    email_provider_gateway=_email_provider_gateway,
    credential_gateway=_credential_gateway,
    sync_min_interval_minutes=storage_settings.SYNC_MIN_INTERVAL_MINUTES,
)

_emails_service = EmailsService(
    email_provider_gateway=_email_provider_gateway,
    credential_gateway=_credential_gateway,
)

_auth_service = AuthService(
    oauth_gateway=_oauth_gateway,
    credential_gateway=_credential_gateway,
)

_llm_adapter = LlamaCppAdapter()
_llm_service = init_llm_service(_llm_adapter)


def get_auth_service() -> AuthService:
    return _auth_service


def get_mailbox_service() -> MailboxService:
    return _mailbox_service


def get_emails_service() -> EmailsService:
    return _emails_service


def get_llm_service() -> LlmService:
    return _llm_service