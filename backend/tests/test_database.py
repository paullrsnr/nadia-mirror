# pylint: disable=invalid-name
"""Tests unitaires pour la couche base de données SQLAlchemy."""
import shutil
import time
import unittest
import tempfile
from pathlib import Path
from datetime import datetime, timezone
from unittest.mock import patch

from backend.database.models import Base
from backend.database.session import get_engine
from backend.database import (
    EmailModel,
    SyncMetadataModel,
    EmailRepository,
    SqliteStorage,
    init_engine,
    dispose_engine,
    create_session,
)
from backend.core.models.email import Email, EmailAddress


class TestEmailModel(unittest.TestCase):
    """Tests pour le modèle EmailModel."""

    def test_email_model_table_name(self):
        """Vérifie le nom de la table."""
        self.assertEqual(EmailModel.__tablename__, "emails")

    def test_email_model_required_fields(self):
        """Vérifie que les champs requis sont définis."""
        required_fields = ["id", "thread_id", "subject", "from_name", "from_email",
                          "to_addresses", "date", "body_text", "provider"]
        for field in required_fields:
            self.assertTrue(hasattr(EmailModel, field))


class TestSyncMetadataModel(unittest.TestCase):
    """Tests pour le modèle SyncMetadataModel."""

    def test_sync_metadata_model_table_name(self):
        """Vérifie le nom de la table."""
        self.assertEqual(SyncMetadataModel.__tablename__, "sync_metadata")

    def test_sync_metadata_model_fields(self):
        """Vérifie que les champs sont définis."""
        required_fields = ["id", "last_sync_time", "sync_count"]
        for field in required_fields:
            self.assertTrue(hasattr(SyncMetadataModel, field))


class TestEmailRepository(unittest.TestCase):
    """Tests pour le repository EmailRepository."""

    def setUp(self):
        """Initialise une base de données temporaire pour chaque test."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test_emails.db"

        with patch("backend.config.settings.storage_settings.DATA_DIR", Path(self.temp_dir)):
            init_engine(self.db_path)
            Base.metadata.create_all(get_engine())

        self.session = create_session()
        self.repo = EmailRepository(self.session)

    def tearDown(self):
        """Nettoie la base de données temporaire."""
        self.session.close()
        dispose_engine()

        # Supprimer le fichier temporaire
        if self.db_path.exists():
            self.db_path.unlink()

    def test_save_email(self):
        """Teste la sauvegarde d'un email."""
        email = Email(
            id="test123",
            thread_id="thread123",
            subject="Test Subject",
            from_address=EmailAddress(name="Test", email="test@example.com"),
            to_addresses=[EmailAddress(name="Dest", email="dest@example.com")],
            cc_addresses=[],
            bcc_addresses=[],
            date=datetime.now(timezone.utc),
            body_text="Test body",
            body_html=None,
            attachments=[],
            labels=["INBOX"],
            snippet="Test snippet"
        )

        result = self.repo.save_email(email, "gmail")
        self.assertTrue(result)

    def test_get_emails(self):
        """Teste la récupération des emails."""
        # Sauvegarder un email d'abord
        email = Email(
            id="test456",
            thread_id="thread456",
            subject="Test Get",
            from_address=EmailAddress(name="Test", email="test@example.com"),
            to_addresses=[EmailAddress(name="Dest", email="dest@example.com")],
            cc_addresses=[],
            bcc_addresses=[],
            date=datetime.now(timezone.utc),
            body_text="Test body",
            body_html=None,
            attachments=[],
            labels=["INBOX"],
            snippet="Test snippet"
        )
        self.repo.save_email(email, "gmail")

        # Récupérer les emails
        emails, total = self.repo.get_emails(max_results=10, offset=0, provider_filter="gmail")
        self.assertIsInstance(emails, list)
        self.assertGreater(len(emails), 0)
        self.assertEqual(emails[0].id, "test456")
        self.assertGreaterEqual(total, 1)

    def test_update_last_sync_time(self):
        """Teste la mise à jour du dernier temps de sync."""
        # update_last_sync_time ne prend pas de paramètres
        self.repo.update_last_sync_time()
        # Pas de valeur de retour, on vérifie juste qu'il n'y a pas d'erreur

    def test_get_last_sync_time(self):
        """Teste la récupération du dernier temps de sync."""
        self.repo.update_last_sync_time()

        last_sync = self.repo.get_last_sync_time()
        self.assertIsNotNone(last_sync)


class TestSqliteStorage(unittest.TestCase):
    """Tests pour SqliteStorage."""

    def setUp(self):
        """Initialise une base de données temporaire pour chaque test."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)

        # Utiliser SqliteStorage avec un data_dir personnalisé
        self.storage = SqliteStorage(data_dir=self.temp_path)

    def tearDown(self):
        """Nettoie la base de données temporaire."""
        dispose_engine()
        time.sleep(0.1)
        try:
            shutil.rmtree(self.temp_path, ignore_errors=True)
        except Exception:  # pylint: disable=broad-exception-caught
            pass

    def test_save_email(self):
        """Teste la sauvegarde d'un email."""
        email = Email(
            id="test1",
            thread_id="thread1",
            subject="Test 1",
            from_address=EmailAddress(name="Test", email="test@example.com"),
            to_addresses=[EmailAddress(name="Dest", email="dest@example.com")],
            cc_addresses=[],
            bcc_addresses=[],
            date=datetime.now(timezone.utc),
            body_text="Test body 1",
            body_html=None,
            attachments=[],
            labels=["INBOX"],
            snippet="Test snippet 1"
        )

        result = self.storage.save_email(email, "gmail")
        self.assertTrue(result)

    def test_get_emails(self):
        """Teste la récupération des emails."""
        # Sauvegarder un email d'abord
        email = Email(
            id="test3",
            thread_id="thread3",
            subject="Test 3",
            from_address=EmailAddress(name="Test", email="test@example.com"),
            to_addresses=[EmailAddress(name="Dest", email="dest@example.com")],
            cc_addresses=[],
            bcc_addresses=[],
            date=datetime.now(timezone.utc),
            body_text="Test body 3",
            body_html=None,
            attachments=[],
            labels=["INBOX"],
            snippet="Test snippet 3"
        )
        self.storage.save_email(email, "gmail")

        # Récupérer les emails
        emails, total = self.storage.get_emails(max_results=10, offset=0, provider_filter="gmail")
        self.assertIsInstance(emails, list)
        self.assertGreater(len(emails), 0)
        self.assertGreaterEqual(total, 1)


if __name__ == "__main__":
    unittest.main()
