"""Tests unitaires pour les endpoints des brouillons."""
import unittest
from unittest.mock import MagicMock
from datetime import datetime

from fastapi.testclient import TestClient

from backend.api.deps import get_draft_service
from backend.api.main import app
from backend.core.exceptions import InvalidInputError, NotFoundError, ProviderError
from backend.core.models.email import DraftEmail, EmailAddress, EmailAttachment, SendResult
from backend.core.services.draftService import DraftService


def _make_draft(draft_id: str = "d1") -> DraftEmail:
    return DraftEmail(
        id=draft_id,
        provider="gmail",
        to_addresses=[EmailAddress(email="dest@example.com")],
        subject="Sujet",
        body_text="Contenu",
        updated_at=datetime(2026, 1, 1, 12, 0),
    )


class TestDraftsEndpoints(unittest.TestCase):
    """Tests pour les endpoints /drafts (services mockés)."""

    def setUp(self):
        self.client = TestClient(app)
        self.draft_service = MagicMock(spec=DraftService)
        app.dependency_overrides[get_draft_service] = lambda: self.draft_service

    def tearDown(self):
        app.dependency_overrides.pop(get_draft_service, None)

    def test_list_drafts(self):
        """GET /drafts/ retourne la liste des brouillons."""
        self.draft_service.list_drafts.return_value = [_make_draft("d1")]

        response = self.client.get("/drafts/?provider=gmail")

        self.assertEqual(response.status_code, 200)
        self.assertEqual([d["id"] for d in response.json()], ["d1"])
        self.draft_service.list_drafts.assert_called_once_with("gmail")

    def test_save_draft(self):
        """POST /drafts/{id} transmet la requête au service."""
        self.draft_service.save_draft.return_value = _make_draft("d1")

        response = self.client.post(
            "/drafts/d1", json={"provider": "gmail", "to": ["dest@example.com"]}
        )

        self.assertEqual(response.status_code, 200)
        draft_id, request = self.draft_service.save_draft.call_args.args
        self.assertEqual(draft_id, "d1")
        self.assertEqual(request.provider, "gmail")
        self.assertEqual(request.to, ["dest@example.com"])

    def test_save_draft_unknown_provider_returns_400(self):
        """Un ProviderError levé par le service donne une erreur 400."""
        self.draft_service.save_draft.side_effect = ProviderError("Provider inconnu : 'foo'")

        response = self.client.post("/drafts/d1", json={"provider": "foo"})

        self.assertEqual(response.status_code, 400)

    def test_send_draft_success_refreshes_sent_folder(self):
        """Un envoi réussi lance la synchro des emails envoyés."""
        self.draft_service.send_draft.return_value = SendResult(
            status="success", draft_id="d1", provider="gmail"
        )

        response = self.client.post("/drafts/d1/send")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "success")
        self.draft_service.refresh_sent_folder.assert_called_once_with("gmail")

    def test_send_draft_error_does_not_refresh(self):
        """Un envoi en erreur ne lance pas la synchro des emails envoyés."""
        self.draft_service.send_draft.return_value = SendResult(status="error", draft_id="d1")

        response = self.client.post("/drafts/d1/send")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "error")
        self.draft_service.refresh_sent_folder.assert_not_called()

    def test_send_draft_not_found_returns_404(self):
        """Un brouillon introuvable donne une erreur 404."""
        self.draft_service.send_draft.side_effect = NotFoundError("Brouillon introuvable : d1")

        response = self.client.post("/drafts/d1/send")

        self.assertEqual(response.status_code, 404)

    def test_delete_draft(self):
        """DELETE /drafts/{id} supprime le brouillon."""
        response = self.client.delete("/drafts/d1")

        self.assertEqual(response.status_code, 200)
        self.draft_service.delete_draft.assert_called_once_with("d1")

    def test_add_attachment(self):
        """POST /drafts/{id}/attachments transmet le nom et le contenu du fichier."""
        self.draft_service.add_attachment.return_value = EmailAttachment(
            filename="a.txt", mime_type="text/plain", size=3, attachment_id="att1"
        )

        response = self.client.post(
            "/drafts/d1/attachments",
            files={"file": ("a.txt", b"abc", "text/plain")},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["attachment_id"], "att1")
        self.draft_service.add_attachment.assert_called_once_with("d1", "a.txt", b"abc")

    def test_add_attachment_too_big_returns_400(self):
        """Un InvalidInputError levé par le service donne une erreur 400."""
        self.draft_service.add_attachment.side_effect = InvalidInputError(
            "Fichier trop volumineux (max 25 Mo)."
        )

        response = self.client.post(
            "/drafts/d1/attachments",
            files={"file": ("a.bin", b"x", "application/octet-stream")},
        )

        self.assertEqual(response.status_code, 400)

    def test_remove_attachment(self):
        """DELETE /drafts/{id}/attachments/{att} retire la pièce jointe."""
        response = self.client.delete("/drafts/d1/attachments/att1")

        self.assertEqual(response.status_code, 200)
        self.draft_service.remove_attachment.assert_called_once_with("d1", "att1")


if __name__ == "__main__":
    unittest.main()
