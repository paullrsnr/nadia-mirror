from backend.adapters.emailProviderGatewayAdapter import EmailProviderGatewayAdapter
from backend.adapters.authProvider.credentialGatewayAdapter import CredentialGatewayAdapter
from backend.adapters.authProvider.oauthGatewayAdapter import OAuthGatewayAdapter
from backend.core.mailboxService import MailboxService
from backend.core.services.authService import AuthService
from backend.core.services.emailsService import EmailsService
from backend.adapters.BDDProvider.sqlLite import SqliteStorageAdapter
from backend.config.settings import storage_settings


def _credential_gateway() -> CredentialGatewayAdapter:
    return CredentialGatewayAdapter()


def _oauth_gateway() -> OAuthGatewayAdapter:
    return OAuthGatewayAdapter()


def get_auth_service() -> AuthService:
    return AuthService(
        oauth_gateway=_oauth_gateway(),
        credential_gateway=_credential_gateway(),
    )


def get_mailbox_service() -> MailboxService:
    return MailboxService(
        storage=SqliteStorageAdapter(),
        email_provider_gateway=EmailProviderGatewayAdapter(),
        credential_gateway=_credential_gateway(),
        sync_min_interval_minutes=storage_settings.SYNC_MIN_INTERVAL_MINUTES,
    )


def get_emails_service() -> EmailsService:
    return EmailsService(
        email_provider_gateway=EmailProviderGatewayAdapter(),
        credential_gateway=_credential_gateway(),
    )
