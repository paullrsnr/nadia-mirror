"""Composition root FastAPI : instancie les services avec leurs implémentations concrètes."""
from backend.adapters.emailAdapterFactory import create_email_adapter
from backend.adapters.AuthProvider.credentialGatewayAdapter import CredentialGatewayAdapter
from backend.adapters.AuthProvider.GMAIL.gmailOAuthAdapter import GmailOAuthPort
from backend.adapters.AuthProvider.Outlook.outlookOAuthAdapter import OutlookOAuthPort
from backend.core.mailboxService import MailboxService
from backend.core.services.authService import AuthService
from backend.core.services.emailsService import EmailsService
from backend.adapters.BDDProvider.sqlLite import SqliteStorage
from backend.config.settings import storage_settings


def _credential_gateway() -> CredentialGatewayAdapter:
    return CredentialGatewayAdapter()


def _oauth_ports() -> dict:
    return {
        "gmail": GmailOAuthPort(),
        "outlook": OutlookOAuthPort(),
    }


def get_auth_service() -> AuthService:
    return AuthService(
        oauth_ports=_oauth_ports(),
        credential_gateway=_credential_gateway(),
    )


def get_mailbox_service() -> MailboxService:
    return MailboxService(
        storage=SqliteStorage(),
        adapter_factory=create_email_adapter,
        credential_gateway=_credential_gateway(),
        sync_min_interval_minutes=storage_settings.SYNC_MIN_INTERVAL_MINUTES,
    )


def get_emails_service() -> EmailsService:
    return EmailsService(
        adapter_factory=create_email_adapter,
        credential_gateway=_credential_gateway(),
    )
