# pylint: disable=invalid-name
"""Tests unitaires pour les services."""
import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime

from backend.config.providers import EmailProvider
from backend.core.mailboxService import MailboxService
from backend.core.models.email import Email, EmailAddress, EmailPage


class TestMailboxService(unittest.TestCase):
    """Tests pour MailboxService."""

    @patch("backend.core.mailboxService.get_connection_credentials")
    @patch("backend.config.adapterRegistry.AdapterRegistry.get_adapter_class")
    @patch("backend.core.mailboxService.SqliteStorage")
    def test_sync_emails_success(
        self, mock_storage: MagicMock, mock_get_adapter: MagicMock, mock_credentials: MagicMock
    ) -> None:
        """Test synchronisation réussie."""
        mock_storage_instance = MagicMock()
        mock_storage.return_value = mock_storage_instance
        mock_storage_instance.get_last_sync_time.return_value = None
        mock_storage_instance.save_email.return_value = True

        mock_credentials.return_value = {"access_token": "fake"}

        # Mock de l'adapter
        mock_adapter = MagicMock()
        mock_adapter_class = MagicMock(return_value=mock_adapter)
        mock_get_adapter.return_value = mock_adapter_class

        test_email = Email(
            id="123",
            thread_id="thread_123",
            subject="Test",
            from_address=EmailAddress(email="test@example.com"),
            to_addresses=[EmailAddress(email="dest@example.com")],
            date=datetime.now(),
            body_text="Contenu test",
        )
        mock_adapter.get_emails.return_value = EmailPage(emails=[test_email], next_page_token=None)

        service = MailboxService()
        result = service.sync_emails(provider=EmailProvider.GMAIL.value, max_results=10)

        self.assertEqual(result.status, "success")
        self.assertEqual(result.synced, 1)
        self.assertEqual(result.saved, 1)
        mock_storage_instance.update_last_sync_time.assert_called_once()

    @patch("backend.core.mailboxService.get_connection_credentials")
    @patch("backend.config.adapterRegistry.AdapterRegistry.get_adapter_class")
    @patch("backend.core.mailboxService.SqliteStorage")
    def test_sync_emails_with_error(
        self, mock_storage: MagicMock, mock_get_adapter: MagicMock, mock_credentials: MagicMock
    ) -> None:
        """Test synchronisation avec erreur."""
        mock_storage_instance = MagicMock()
        mock_storage_instance.get_last_sync_time.return_value = None
        mock_storage.return_value = mock_storage_instance

        mock_credentials.return_value = {"access_token": "fake"}

        # Mock de l'adapter qui lève une exception
        mock_adapter = MagicMock()
        mock_adapter.get_emails.side_effect = ValueError("Non authentifié")
        mock_adapter_class = MagicMock(return_value=mock_adapter)
        mock_get_adapter.return_value = mock_adapter_class

        service = MailboxService()
        result = service.sync_emails(provider=EmailProvider.GMAIL.value)

        self.assertEqual(result.status, "error")
        self.assertIn("Non authentifié", result.message)

    @patch("backend.core.mailboxService.get_connection_credentials")
    @patch("backend.config.settings.storage_settings")
    @patch("backend.core.mailboxService.SqliteStorage")
    def test_sync_emails_skipped_when_recent(
        self, mock_storage: MagicMock, mock_settings: MagicMock, mock_credentials: MagicMock
    ) -> None:
        """Test que la sync est ignorée si dernière sync trop récente."""
        mock_settings.SYNC_MIN_INTERVAL_MINUTES = 5
        mock_storage_instance = MagicMock()
        mock_storage.return_value = mock_storage_instance
        mock_storage_instance.get_last_sync_time.return_value = datetime.now()

        mock_credentials.return_value = {"access_token": "fake"}

        service = MailboxService()
        result = service.sync_emails(provider=EmailProvider.GMAIL.value)

        self.assertEqual(result.status, "skipped")


if __name__ == "__main__":
    unittest.main()
