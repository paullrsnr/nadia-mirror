"""Tests unitaires pour la synchro des emails envoyés de MailboxService."""
import unittest
from unittest.mock import MagicMock
from datetime import datetime

from backend.core.mailboxService import MailboxService
from backend.core.models.email import Email, EmailAddress, EmailPage, Provider
from backend.core.services.enrichmentService import EnrichmentService
from backend.ports.credentialGateway import CredentialGateway
from backend.ports.emailProviderGateway import EmailProviderGateway
from backend.ports.emailStorage import EmailStorage


def _make_email(email_id: str) -> Email:
    return Email(
        id=email_id,
        thread_id=f"thread_{email_id}",
        subject="Test",
        from_address=EmailAddress(email="moi@example.com"),
        to_addresses=[EmailAddress(email="dest@example.com")],
        date=datetime.now(),
        body_text="Contenu test",
        provider=Provider.GMAIL,
    )


class TestMailboxServiceSyncSentEmails(unittest.TestCase):
    """Tests pour sync_sent_emails."""

    def setUp(self):
        self.storage = MagicMock(spec=EmailStorage)
        self.gateway = MagicMock(spec=EmailProviderGateway)
        self.service = MailboxService(
            storage=self.storage,
            email_provider_gateway=self.gateway,
            credential_gateway=MagicMock(spec=CredentialGateway),
            enrichment_service=MagicMock(spec=EnrichmentService),
        )

    def test_sync_sent_emails_stores_emails_in_sent_folder(self):
        """Les emails récupérés sont enregistrés dans le dossier sent."""
        self.gateway.fetch_emails.return_value = EmailPage(
            emails=[_make_email("1"), _make_email("2")], next_page_token=None
        )

        self.service.sync_sent_emails("gmail")

        stored, = self.storage.upsert_emails_batch.call_args.args
        self.assertEqual([e.folder for e in stored], ["sent", "sent"])
        self.assertEqual(self.storage.upsert_emails_batch.call_args.kwargs["provider"], "gmail")

    def test_sync_sent_emails_queries_sent_only(self):
        """La requête cible uniquement les emails envoyés, avec les bons paramètres."""
        self.gateway.fetch_emails.return_value = EmailPage(emails=[], next_page_token=None)
        after = datetime(2026, 1, 1)

        self.service.sync_sent_emails("gmail", after=after, max_results=5)

        kwargs = self.gateway.fetch_emails.call_args.kwargs
        self.assertEqual(kwargs["provider"], "gmail")
        self.assertEqual(kwargs["max_results"], 5)
        self.assertTrue(kwargs["query"].sent_only)
        self.assertFalse(kwargs["query"].unread_only)
        self.assertEqual(kwargs["query"].after_date, after)

    def test_sync_sent_emails_lowercases_provider_for_storage(self):
        """Le provider est enregistré en minuscules."""
        self.gateway.fetch_emails.return_value = EmailPage(
            emails=[_make_email("1")], next_page_token=None
        )

        self.service.sync_sent_emails("GMAIL")

        self.assertEqual(self.storage.upsert_emails_batch.call_args.kwargs["provider"], "gmail")

    def test_sync_sent_emails_swallows_errors(self):
        """Une erreur du provider est journalisée sans être propagée."""
        self.gateway.fetch_emails.side_effect = RuntimeError("API indisponible")

        with self.assertLogs("backend.core.mailboxService", level="WARNING"):
            self.service.sync_sent_emails("gmail")

        self.storage.upsert_emails_batch.assert_not_called()


if __name__ == "__main__":
    unittest.main()
