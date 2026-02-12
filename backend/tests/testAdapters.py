# pylint: disable=invalid-name
"""Tests unitaires pour les adapters et utilitaires."""
import unittest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from unittest.mock import patch, MagicMock

from backend.utils.textCleaner import html_to_text
from backend.utils.emailParser import parse_email_address, extract_email_body
from backend.core.models.email import Email, EmailAddress


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
        """Test extraction corps texte simple."""
        import base64

        text_content = "Bonjour, ceci est un test."
        encoded = base64.urlsafe_b64encode(text_content.encode()).decode()

        payload = {"mimeType": "text/plain", "body": {"data": encoded}}

        body_text, body_html = extract_email_body(payload)

        self.assertEqual(body_text, text_content)
        self.assertIsNone(body_html)

    def test_extract_email_body_empty(self):
        """Test extraction corps vide."""
        payload = {"mimeType": "text/plain", "body": {}}

        body_text, body_html = extract_email_body(payload)

        self.assertEqual(body_text, "[Corps de l'email non disponible]")
        self.assertIsNone(body_html)


class TestSqliteStorage(unittest.TestCase):
    """Tests pour SqliteStorage."""

    def setUp(self):
        """Crée un répertoire temporaire pour les tests."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)

    def tearDown(self):
        """Supprime le répertoire temporaire."""
        shutil.rmtree(self.temp_dir)

    @patch("backend.config.user_space.get_current_user_space_dir")
    def test_storage_init_creates_database(self, mock_user_space_dir):
        """Test que l'initialisation crée la base de données."""
        mock_user_space_dir.return_value = self.temp_path

        from backend.database.email_storage import SqliteStorage

        storage = SqliteStorage()

        self.assertTrue(storage.db_path.exists())

    @patch("backend.config.settings.storage_settings")
    @patch("backend.config.user_space.get_current_user_space_dir")
    def test_save_and_get_sync_time(self, mock_user_space_dir, mock_storage_settings):
        """Test sauvegarde et récupération du temps de sync."""
        test_dir = Path(tempfile.mkdtemp(dir=self.temp_dir))
        mock_user_space_dir.return_value = test_dir
        # Éviter la migration depuis l'ancien emplacement (DATA_DIR sans emails.db)
        mock_storage_settings.DATA_DIR = test_dir

        from backend.database.email_storage import SqliteStorage

        storage = SqliteStorage()

        # Pas de sync au départ (sync_metadata vide)
        self.assertIsNone(storage.get_last_sync_time())

        # Mise à jour
        storage.update_last_sync_time()

        # Vérification
        sync_time = storage.get_last_sync_time()
        self.assertIsNotNone(sync_time)
        self.assertIsInstance(sync_time, datetime)

    @patch("backend.config.user_space.get_current_user_space_dir")
    def test_save_email(self, mock_user_space_dir):
        """Test sauvegarde d'un email."""
        mock_user_space_dir.return_value = self.temp_path

        from backend.database.email_storage import SqliteStorage

        storage = SqliteStorage()

        email = Email(
            id="test_123",
            thread_id="thread_123",
            subject="Test Subject",
            from_address=EmailAddress(name="Sender", email="sender@test.com"),
            to_addresses=[EmailAddress(email="dest@test.com")],
            date=datetime.now(),
            body_text="Corps du message",
        )

        result = storage.save_email(email)

        self.assertTrue(result)


if __name__ == "__main__":
    unittest.main()
