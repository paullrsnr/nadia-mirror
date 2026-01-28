# pylint: disable=invalid-name
"""Tests unitaires pour les services."""
import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime

from backend.core.mailboxService import MailboxService
from backend.api.schemas import Email, EmailAddress


class TestMailboxService(unittest.TestCase):
    """Tests pour MailboxService."""

    @patch("backend.core.mailboxService.SqliteStorage")
    @patch("backend.core.mailboxService.GmailAdapter")
    def test_sync_emails_success(self, mock_gmail, mock_storage):
        """Test synchronisation réussie."""
        # Setup mocks
        mock_storage_instance = MagicMock()
        mock_storage.return_value = mock_storage_instance
        mock_storage_instance.get_last_sync_time.return_value = None
        mock_storage_instance.save_email.return_value = True

        mock_gmail_instance = MagicMock()
        mock_gmail.return_value = mock_gmail_instance

        test_email = Email(
            id="123",
            thread_id="thread_123",
            subject="Test",
            from_address=EmailAddress(email="test@example.com"),
            to_addresses=[EmailAddress(email="dest@example.com")],
            date=datetime.now(),
            body_text="Contenu test",
        )
        mock_gmail_instance.get_emails.return_value = ([test_email], None)

        # Execute
        service = MailboxService()
        result = service.sync_emails(max_results=10)

        # Assert
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["synced"], 1)
        self.assertEqual(result["saved"], 1)
        mock_storage_instance.update_last_sync_time.assert_called_once()

    @patch("backend.core.mailboxService.SqliteStorage")
    @patch("backend.core.mailboxService.GmailAdapter")
    def test_sync_emails_with_error(self, mock_gmail, mock_storage):
        """Test synchronisation avec erreur."""
        mock_storage.return_value = MagicMock()
        mock_gmail.side_effect = ValueError("Non authentifié")

        service = MailboxService()
        result = service.sync_emails()

        self.assertEqual(result["status"], "error")
        self.assertIn("Non authentifié", result["message"])

    @patch("backend.core.mailboxService.SqliteStorage")
    @patch("backend.core.mailboxService.GmailAdapter")
    def test_sync_emails_force_mode(self, mock_gmail, mock_storage):
        """Test synchronisation en mode force."""
        mock_storage_instance = MagicMock()
        mock_storage.return_value = mock_storage_instance
        mock_storage_instance.get_last_sync_time.return_value = datetime.now()
        mock_storage_instance.save_email.return_value = True

        mock_gmail_instance = MagicMock()
        mock_gmail.return_value = mock_gmail_instance
        mock_gmail_instance.get_emails.return_value = ([], None)

        service = MailboxService()
        service.sync_emails(force=True)

        # En mode force, get_last_sync_time ne devrait pas influencer la query
        mock_gmail_instance.get_emails.assert_called_once()


if __name__ == "__main__":
    unittest.main()
