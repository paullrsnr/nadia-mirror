# pylint: disable=import-outside-toplevel
"""Tests unitaires pour les adapters et utilitaires."""
import base64
import unittest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

from backend.utils.textCleaner import html_to_text
from backend.adapters.mailProvider.GMAIL.gmailMessageParser import parse_email_address
from backend.adapters.mailProvider.GMAIL.gmailBodyParser import extract_gmail_body
from backend.core.models.email import Email, EmailAddress, Provider


class TestTextCleaner(unittest.TestCase):
    """Tests pour html_to_text."""

    def test_html_to_text_simple(self):
        """Test conversion HTML simple."""
        html = "<p>Bonjour</p>"
        result = html_to_text(html)

        self.assertEqual(result, "Bonjour")

    def test_html_to_text_with_tags(self):
        """Test conversion avec plusieurs tags."""
        html = "<div><p>Ligne 1</p><p>Ligne 2</p></div>"
        result = html_to_text(html)

        self.assertIn("Ligne 1", result)
        self.assertIn("Ligne 2", result)

    def test_html_to_text_with_script(self):
        """Test suppression des scripts."""
        html = "<p>Texte</p><script>alert('test');</script>"
        result = html_to_text(html)

        self.assertEqual(result, "Texte")
        self.assertNotIn("alert", result)

    def test_html_to_text_with_style(self):
        """Test suppression des styles."""
        html = "<style>.class { color: red; }</style><p>Contenu</p>"
        result = html_to_text(html)

        self.assertEqual(result, "Contenu")
        self.assertNotIn("color", result)

    def test_html_to_text_empty(self):
        """Test avec HTML vide."""
        self.assertEqual(html_to_text(""), "")
        self.assertEqual(html_to_text(None), "")

    def test_html_to_text_entities(self):
        """Test décodage entités HTML."""
        html = "<p>Test &amp; test &quot;value&quot;</p>"
        result = html_to_text(html)

        self.assertIn("&", result)
        self.assertIn('"value"', result)

    def test_html_to_text_br_tags(self):
        """Test conversion des balises br."""
        html = "Ligne 1<br>Ligne 2<br/>Ligne 3"
        result = html_to_text(html)

        self.assertIn("Ligne 1", result)
        self.assertIn("Ligne 2", result)
        self.assertIn("Ligne 3", result)


class TestEmailParser(unittest.TestCase):
    """Tests pour le parser d'emails."""

    def test_parse_email_address_full(self):
        """Test parsing adresse complète."""
        result = parse_email_address("John Doe <john@example.com>")

        self.assertEqual(result.name, "John Doe")
        self.assertEqual(result.email, "john@example.com")

    def test_parse_email_address_simple(self):
        """Test parsing adresse simple."""
        result = parse_email_address("john@example.com")

        self.assertIsNone(result.name)
        self.assertEqual(result.email, "john@example.com")

    def test_parse_email_address_empty(self):
        """Test parsing adresse vide."""
        result = parse_email_address("")

        self.assertEqual(result.email, "")

    def test_parse_email_address_none(self):
        """Test parsing None."""
        result = parse_email_address(None)

        self.assertEqual(result.email, "")

    def test_parse_email_address_whitespace(self):
        """Test parsing avec espaces."""
        result = parse_email_address("   ")

        self.assertEqual(result.email, "")

    def test_extract_email_body_plain_text(self):
        """Test extraction corps texte simple (payload Gmail)."""
        text_content = "Bonjour, ceci est un test."
        encoded = base64.urlsafe_b64encode(text_content.encode()).decode()

        payload = {"mimeType": "text/plain", "body": {"data": encoded}}

        body_text, body_html = extract_gmail_body(payload)

        self.assertEqual(body_text, text_content)
        self.assertIsNone(body_html)

    def test_extract_email_body_empty(self):
        """Test extraction corps vide."""
        payload = {"mimeType": "text/plain", "body": {}}

        body_text, body_html = extract_gmail_body(payload)

        self.assertEqual(body_text, "[Corps de l'email non disponible]")
        self.assertIsNone(body_html)


class TestSqliteStorageAdapter(unittest.TestCase):
    """Tests pour SqliteStorageAdapter."""

    def setUp(self):
        """Crée un répertoire temporaire pour les tests."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)

    def tearDown(self):
        """Supprime le répertoire temporaire."""
        from backend.adapters.bddProvider.sqlLite.session import dispose_engine
        dispose_engine()
        shutil.rmtree(self.temp_dir)

    def test_storage_init_creates_database(self):
        """Test que l'initialisation crée la base de données."""
        from backend.tests.dbHelper import create_test_storage

        storage = create_test_storage(self.temp_path)

        self.assertTrue(storage.db_path.exists())

    def test_save_and_get_sync_time(self):
        """Test sauvegarde et récupération du temps de sync."""
        from backend.tests.dbHelper import create_test_storage

        storage = create_test_storage(self.temp_path)

        # Pas de sync au départ (sync_metadata vide)
        self.assertIsNone(storage.get_last_sync_time())

        # Mise à jour
        storage.update_last_sync_time()

        # Vérification
        sync_time = storage.get_last_sync_time()
        self.assertIsNotNone(sync_time)
        self.assertIsInstance(sync_time, datetime)

    def test_upsert_email(self):
        """Test sauvegarde d'un email."""
        from backend.tests.dbHelper import create_test_storage

        storage = create_test_storage(self.temp_path)

        email = Email(
            id="test_123",
            thread_id="thread_123",
            subject="Test Subject",
            from_address=EmailAddress(name="Sender", email="sender@test.com"),
            to_addresses=[EmailAddress(email="dest@test.com")],
            date=datetime.now(),
            body_text="Corps du message",
            provider=Provider.GMAIL,
        )

        result = storage.upsert_email(email, provider="gmail")

        self.assertTrue(result)


if __name__ == "__main__":
    unittest.main()
