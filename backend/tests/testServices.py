"""Tests unitaires pour les services du core."""
import unittest
from unittest.mock import MagicMock
from datetime import datetime

from backend.core.models.email import Provider
from backend.core.mailboxService import MailboxService
from backend.core.models.email import Email, EmailAddress, EmailPage
from backend.ports.emailStorage import EmailStorage
from backend.ports.credentialGateway import CredentialGateway
from backend.ports.emailProviderGateway import EmailProviderGateway


def _build_service(
    storage: MagicMock | None = None,
    email_provider_gateway: MagicMock | None = None,
    credential_gateway: MagicMock | None = None,
) -> MailboxService:
    return MailboxService(
        storage=storage or MagicMock(spec=EmailStorage),
        email_provider_gateway=email_provider_gateway or MagicMock(),
        credential_gateway=credential_gateway or MagicMock(spec=CredentialGateway),
    )


def _make_email(email_id: str = "123") -> Email:
    return Email(
        id=email_id,
        thread_id=f"thread_{email_id}",
        subject="Test",
        from_address=EmailAddress(email="test@example.com"),
        to_addresses=[EmailAddress(email="dest@example.com")],
        date=datetime.now(),
        body_text="Contenu test",
        provider=Provider.GMAIL,
    )


class TestMailboxServiceSync(unittest.TestCase):
    """Tests pour la synchronisation des emails."""

    def test_sync_emails_success(self):
        """La synchronisation réussit et retourne synced=1, saved=1."""
        storage = MagicMock(spec=EmailStorage)
        storage.get_last_sync_time.return_value = None
        storage.upsert_email.return_value = True

        page = EmailPage(emails=[_make_email()], next_page_token=None)
        email_provider_gateway = MagicMock(spec=EmailProviderGateway)
        email_provider_gateway.fetch_emails.return_value = page

        credential_gateway = MagicMock(spec=CredentialGateway)
        credential_gateway.load.return_value = {"access_token": "fake"}

        service = _build_service(storage, email_provider_gateway, credential_gateway)
        result = service.sync_emails(provider=Provider.GMAIL.value, max_results=10)

        self.assertEqual(result.status, "success")
        self.assertEqual(result.synced, 1)
        self.assertEqual(result.saved, 1)
        storage.update_last_sync_time.assert_called_once()
        email_provider_gateway.fetch_emails.assert_called()

    def test_sync_emails_skipped_when_recent(self):
        """La sync est ignorée si la dernière sync est trop récente."""
        storage = MagicMock(spec=EmailStorage)
        storage.get_last_sync_time.return_value = datetime.now()

        credential_gateway = MagicMock(spec=CredentialGateway)
        credential_gateway.load.return_value = {"access_token": "fake"}

        service = _build_service(storage, credential_gateway=credential_gateway)
        result = service.sync_emails(provider=Provider.GMAIL.value)

        self.assertEqual(result.status, "skipped")

    def test_sync_emails_error_from_adapter(self):
        """Si fetch_emails lève ValueError, le résultat est status=error."""
        storage = MagicMock(spec=EmailStorage)
        storage.get_last_sync_time.return_value = None

        email_provider_gateway = MagicMock(spec=EmailProviderGateway)
        email_provider_gateway.fetch_emails.side_effect = ValueError("Non authentifié")

        credential_gateway = MagicMock(spec=CredentialGateway)
        credential_gateway.load.return_value = {"access_token": "fake"}

        service = _build_service(storage, email_provider_gateway, credential_gateway)
        result = service.sync_emails(provider=Provider.GMAIL.value)

        self.assertEqual(result.status, "error")
        self.assertIn("Non authentifié", result.message)


class TestMailboxServiceGetStored(unittest.TestCase):
    """Tests pour la récupération des emails stockés."""

    def test_get_stored_emails_returns_list(self):
        """get_stored_emails retourne une EmailListResult valide."""
        storage = MagicMock(spec=EmailStorage)
        storage.find_emails.return_value = ([_make_email()], 1)

        service = _build_service(storage)
        result = service.get_stored_emails(provider="gmail", max_results=10, page=1)

        self.assertEqual(result.total, 1)
        self.assertEqual(len(result.emails), 1)
        storage.find_emails.assert_called_once_with(max_results=10, offset=0, provider_filter="gmail")

    def test_get_stored_emails_all_provider(self):
        """get_stored_emails avec provider=all ne filtre pas par provider."""
        storage = MagicMock(spec=EmailStorage)
        storage.find_emails.return_value = ([], 0)

        service = _build_service(storage)
        service.get_stored_emails(provider="all", max_results=50, page=1)

        storage.find_emails.assert_called_once_with(max_results=50, offset=0, provider_filter=None)


if __name__ == "__main__":
    unittest.main()
