"""Tests unitaires pour le service des brouillons."""
import unittest
from unittest.mock import MagicMock
from datetime import datetime

from backend.core.exceptions import InvalidInputError, NotFoundError, ProviderError
from backend.core.models.email import (
    AttachmentContent,
    DraftEmail,
    EmailAddress,
    EmailAttachment,
    SaveDraftRequest,
)
from backend.core.mailboxService import MailboxService
from backend.core.services.draftService import (
    DraftService,
    MAX_ATTACHMENT_SIZE_BYTES,
    SENT_REFRESH_MAX_RESULTS,
)
from backend.ports.attachmentStorage import AttachmentStorage
from backend.ports.credentialGateway import CredentialGateway
from backend.ports.emailProviderGateway import EmailProviderGateway
from backend.ports.draftStorage import DraftStorage


def _build_service(
    storage: MagicMock | None = None,
    email_provider_gateway: MagicMock | None = None,
    credential_gateway: MagicMock | None = None,
    attachment_storage: MagicMock | None = None,
    mailbox_service: MagicMock | None = None,
) -> DraftService:
    return DraftService(
        email_provider_gateway=email_provider_gateway or MagicMock(spec=EmailProviderGateway),
        credential_gateway=credential_gateway or MagicMock(spec=CredentialGateway),
        draft_storage=storage or MagicMock(spec=DraftStorage),
        attachment_storage=attachment_storage or MagicMock(spec=AttachmentStorage),
        mailbox_service=mailbox_service or MagicMock(spec=MailboxService),
    )


def _make_draft(draft_id: str = "d1", provider: str = "gmail") -> DraftEmail:
    return DraftEmail(
        id=draft_id,
        provider=provider,
        to_addresses=[EmailAddress(email="dest@example.com")],
        subject="Sujet",
        body_text="Contenu",
        updated_at=datetime.now(),
    )


class TestDraftServiceSave(unittest.TestCase):
    """Tests pour l'enregistrement d'un brouillon."""

    def test_save_draft_builds_domain_draft(self):
        """save_draft construit un DraftEmail complet à partir de la requête."""
        storage = MagicMock(spec=DraftStorage)
        storage.save_draft.side_effect = lambda draft: draft
        service = _build_service(storage=storage)

        request = SaveDraftRequest(
            provider="gmail",
            subject="Sujet",
            body_text="Contenu",
            body_html="<p>Contenu</p>",
            to=["a@example.com"],
            cc=["b@example.com"],
            bcc=["c@example.com"],
            in_reply_to_email_id="email_42",
        )
        draft = service.save_draft("d1", request)

        self.assertEqual(draft.id, "d1")
        self.assertEqual(draft.provider, "gmail")
        self.assertEqual(draft.to_addresses, [EmailAddress(email="a@example.com")])
        self.assertEqual(draft.cc_addresses, [EmailAddress(email="b@example.com")])
        self.assertEqual(draft.bcc_addresses, [EmailAddress(email="c@example.com")])
        self.assertEqual(draft.body_html, "<p>Contenu</p>")
        self.assertEqual(draft.in_reply_to_email_id, "email_42")
        storage.save_draft.assert_called_once()

    def test_save_draft_normalizes_provider(self):
        """Le provider est enregistré sous sa forme normalisée."""
        storage = MagicMock(spec=DraftStorage)
        storage.save_draft.side_effect = lambda draft: draft
        service = _build_service(storage=storage)

        draft = service.save_draft("d1", SaveDraftRequest(provider="  GMAIL "))

        self.assertEqual(draft.provider, "gmail")

    def test_save_draft_empty_html_becomes_none(self):
        """Un body_html vide est enregistré à None."""
        storage = MagicMock(spec=DraftStorage)
        storage.save_draft.side_effect = lambda draft: draft
        service = _build_service(storage=storage)

        draft = service.save_draft("d1", SaveDraftRequest(provider="gmail", body_html=""))

        self.assertIsNone(draft.body_html)

    def test_save_draft_unknown_provider_raises(self):
        """Un provider inconnu lève ProviderError et rien n'est enregistré."""
        storage = MagicMock(spec=DraftStorage)
        service = _build_service(storage=storage)

        with self.assertRaises(ProviderError):
            service.save_draft("d1", SaveDraftRequest(provider="foo"))

        storage.save_draft.assert_not_called()


class TestDraftServiceListAndDelete(unittest.TestCase):
    """Tests pour la liste et la suppression des brouillons."""

    def test_list_drafts_fills_attachments(self):
        """list_drafts ajoute les pièces jointes stockées à chaque brouillon."""
        storage = MagicMock(spec=DraftStorage)
        storage.find_drafts.return_value = [_make_draft("d1")]
        attachment = EmailAttachment(
            filename="a.pdf", mime_type="application/pdf", size=3, attachment_id="att1"
        )
        attachment_storage = MagicMock(spec=AttachmentStorage)
        attachment_storage.list_attachments.return_value = [attachment]
        service = _build_service(storage=storage, attachment_storage=attachment_storage)

        drafts = service.list_drafts("gmail")

        storage.find_drafts.assert_called_once_with("gmail")
        attachment_storage.list_attachments.assert_called_once_with("d1")
        self.assertEqual(drafts[0].attachments, [attachment])

    def test_delete_draft_removes_draft_and_attachments(self):
        """delete_draft supprime le brouillon et ses pièces jointes."""
        storage = MagicMock(spec=DraftStorage)
        attachment_storage = MagicMock(spec=AttachmentStorage)
        service = _build_service(storage=storage, attachment_storage=attachment_storage)

        service.delete_draft("d1")

        storage.delete_draft.assert_called_once_with("d1")
        attachment_storage.delete_draft_attachments.assert_called_once_with("d1")


class TestDraftServiceAttachments(unittest.TestCase):
    """Tests pour l'ajout et le retrait des pièces jointes."""

    def test_add_attachment_saves_file(self):
        """add_attachment délègue au stockage des pièces jointes."""
        attachment_storage = MagicMock(spec=AttachmentStorage)
        service = _build_service(attachment_storage=attachment_storage)

        service.add_attachment("d1", "a.txt", b"abc")

        attachment_storage.save_attachment.assert_called_once_with("d1", "a.txt", b"abc")

    def test_add_attachment_accepts_max_size(self):
        """Un fichier pile à la taille maximale est accepté."""
        attachment_storage = MagicMock(spec=AttachmentStorage)
        service = _build_service(attachment_storage=attachment_storage)

        service.add_attachment("d1", "a.bin", b"x" * MAX_ATTACHMENT_SIZE_BYTES)

        attachment_storage.save_attachment.assert_called_once()

    def test_add_attachment_too_big_raises(self):
        """Un fichier au-delà de la taille maximale lève InvalidInputError."""
        attachment_storage = MagicMock(spec=AttachmentStorage)
        service = _build_service(attachment_storage=attachment_storage)

        with self.assertRaises(InvalidInputError):
            service.add_attachment("d1", "a.bin", b"x" * (MAX_ATTACHMENT_SIZE_BYTES + 1))

        attachment_storage.save_attachment.assert_not_called()

    def test_remove_attachment(self):
        """remove_attachment délègue la suppression au stockage."""
        attachment_storage = MagicMock(spec=AttachmentStorage)
        service = _build_service(attachment_storage=attachment_storage)

        service.remove_attachment("d1", "att1")

        attachment_storage.delete_attachment.assert_called_once_with("d1", "att1")


class TestDraftServiceSend(unittest.TestCase):
    """Tests pour l'envoi d'un brouillon."""

    def setUp(self):
        self.storage = MagicMock(spec=DraftStorage)
        self.storage.find_draft_by_id.return_value = _make_draft("d1", "gmail")
        self.gateway = MagicMock(spec=EmailProviderGateway)
        self.gateway.send_email.return_value = True
        self.credentials = MagicMock(spec=CredentialGateway)
        self.credentials.load.return_value = {"access_token": "fake"}
        self.attachment_storage = MagicMock(spec=AttachmentStorage)
        self.attachment_storage.list_attachments.return_value = []
        self.service = _build_service(
            storage=self.storage,
            email_provider_gateway=self.gateway,
            credential_gateway=self.credentials,
            attachment_storage=self.attachment_storage,
        )

    def test_send_draft_not_found_raises(self):
        """Un brouillon introuvable lève NotFoundError."""
        self.storage.find_draft_by_id.return_value = None

        with self.assertRaises(NotFoundError):
            self.service.send_draft("absent")

        self.gateway.send_email.assert_not_called()

    def test_send_draft_without_credentials_returns_error(self):
        """Sans identifiants, l'envoi n'est pas tenté et le résultat est en erreur."""
        self.credentials.load.return_value = None

        result = self.service.send_draft("d1")

        self.assertEqual(result.status, "error")
        self.assertIsNone(result.provider)
        self.gateway.send_email.assert_not_called()
        self.storage.delete_draft.assert_not_called()

    def test_send_draft_success_deletes_draft(self):
        """Un envoi réussi supprime le brouillon et ses pièces jointes."""
        result = self.service.send_draft("d1")

        self.assertEqual(result.status, "success")
        self.assertEqual(result.draft_id, "d1")
        self.assertEqual(result.provider, "gmail")
        self.credentials.load.assert_called_once_with("gmail")
        self.storage.delete_draft.assert_called_once_with("d1")
        self.attachment_storage.delete_draft_attachments.assert_called_once_with("d1")

    def test_send_draft_passes_attachments_to_gateway(self):
        """Les pièces jointes stockées sont lues et envoyées avec le brouillon."""
        self.attachment_storage.list_attachments.return_value = [
            EmailAttachment(filename="a.txt", mime_type="text/plain", size=3, attachment_id="att1"),
        ]
        content = AttachmentContent(filename="a.txt", mime_type="text/plain", content=b"abc")
        self.attachment_storage.read_attachment.return_value = content

        self.service.send_draft("d1")

        self.attachment_storage.read_attachment.assert_called_once_with("d1", "att1")
        provider, draft, attachments = self.gateway.send_email.call_args.args
        self.assertEqual(provider, "gmail")
        self.assertEqual(draft.id, "d1")
        self.assertEqual(attachments, [content])

    def test_send_draft_failure_keeps_draft(self):
        """Si le provider refuse l'envoi, le brouillon est conservé."""
        self.gateway.send_email.return_value = False

        result = self.service.send_draft("d1")

        self.assertEqual(result.status, "error")
        self.assertIsNone(result.provider)
        self.storage.delete_draft.assert_not_called()
        self.attachment_storage.delete_draft_attachments.assert_not_called()


class TestDraftServiceRefreshSentFolder(unittest.TestCase):
    """Tests pour le rafraîchissement du dossier envoyés après un envoi."""

    def test_refresh_sent_folder_delegates_to_mailbox(self):
        """refresh_sent_folder lance la synchro des derniers emails envoyés."""
        mailbox = MagicMock(spec=MailboxService)
        service = _build_service(mailbox_service=mailbox)

        service.refresh_sent_folder("gmail")

        mailbox.sync_sent_emails.assert_called_once_with(
            "gmail", max_results=SENT_REFRESH_MAX_RESULTS
        )


if __name__ == "__main__":
    unittest.main()
