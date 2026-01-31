# pylint: disable=invalid-name
"""Tests unitaires pour les services."""
import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime

from backend.core.mailboxService import MailboxService
from backend.core.models.email import Email, EmailAddress


class TestMailboxService(unittest.TestCase):
    """Tests pour MailboxService."""

    @patch("backend.core.mailboxService.SqliteStorage")
    def test_sync_emails_success(self, mock_storage):
        """Test synchronisation réussie."""
        mock_storage_instance = MagicMock()
        mock_storage.return_value = mock_storage_instance
        mock_storage_instance.get_last_sync_time.return_value = None
        mock_storage_instance.save_email.return_value = True

        mock_provider = MagicMock()
        test_email = Email(
            id="123",
            thread_id="thread_123",
            subject="Test",
            from_address=EmailAddress(email="test@example.com"),
            to_addresses=[EmailAddress(email="dest@example.com")],
            date=datetime.now(),
            body_text="Contenu test",
        )
        mock_provider.get_emails.return_value = ([test_email], None)

        service = MailboxService(mock_provider)
        result = service.sync_emails(max_results=10)

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["synced"], 1)
        self.assertEqual(result["saved"], 1)
        mock_storage_instance.update_last_sync_time.assert_called_once()

    @patch("backend.core.mailboxService.SqliteStorage")
    def test_sync_emails_with_error(self, mock_storage):
        """Test synchronisation avec erreur."""
        mock_storage.return_value = MagicMock()
        mock_provider = MagicMock()
        mock_provider.get_emails.side_effect = ValueError("Non authentifié")

        service = MailboxService(mock_provider)
        result = service.sync_emails()

        self.assertEqual(result["status"], "error")
        self.assertIn("Non authentifié", result["message"])

    @patch("backend.core.mailboxService.storage_settings")
    @patch("backend.core.mailboxService.SqliteStorage")
    def test_sync_emails_skipped_when_recent(self, mock_storage, mock_settings):
        """Test que la sync est ignorée si dernière sync trop récente."""
        mock_settings.SYNC_MIN_INTERVAL_MINUTES = 5
        mock_storage_instance = MagicMock()
        mock_storage.return_value = mock_storage_instance
        mock_storage_instance.get_last_sync_time.return_value = datetime.now()

        mock_provider = MagicMock()

        service = MailboxService(mock_provider)
        result = service.sync_emails()

        self.assertEqual(result["status"], "skipped")
        mock_provider.get_emails.assert_not_called()


if __name__ == "__main__":
    unittest.main()
