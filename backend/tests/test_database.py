"""Tests unitaires pour la couche base de données SQLAlchemy."""
import shutil
import time
import unittest
import tempfile
from pathlib import Path
from datetime import datetime, timezone

from backend.adapters.bddProvider.sqlLite.models import EmailModel, SyncMetadataModel
from backend.adapters.bddProvider.sqlLite.session import dispose_engine, create_session
from backend.tests.dbHelper import create_test_storage
from backend.core.models.email import Email, EmailAddress, Provider


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
        for field in ["id", "last_sync_time"]:
            self.assertTrue(hasattr(SyncMetadataModel, field))


def _make_email(email_id: str) -> Email:
    return Email(
        id=email_id,
        thread_id=f"thread_{email_id}",
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
        snippet="Test snippet",
        provider=Provider.GMAIL,
    )


class TestSqliteStorageAdapter(unittest.TestCase):
    """Tests pour SqliteStorageAdapter (implémentation du port EmailStorage)."""

    def setUp(self):
        """Initialise une base de données temporaire pour chaque test."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
        self.storage = create_test_storage(self.temp_path)

    def tearDown(self):
        """Nettoie la base de données temporaire."""
        dispose_engine()
        time.sleep(0.1)
        shutil.rmtree(self.temp_path, ignore_errors=True)

    def test_upsert_email_returns_true_when_new(self):
        """upsert_email retourne True si l'email est nouveau."""
        result = self.storage.upsert_email(_make_email("new_1"), "gmail")
        self.assertTrue(result)

    def test_upsert_email_returns_false_when_duplicate(self):
        """upsert_email retourne False si l'email existe déjà."""
        email = _make_email("dup_1")
        self.storage.upsert_email(email, "gmail")
        result = self.storage.upsert_email(email, "gmail")
        self.assertFalse(result)

    def test_find_emails_returns_saved(self):
        """find_emails retourne les emails sauvegardés."""
        self.storage.upsert_email(_make_email("find_1"), "gmail")
        emails, total = self.storage.find_emails(max_results=10, offset=0, provider_filter="gmail")
        self.assertIsInstance(emails, list)
        self.assertGreater(len(emails), 0)
        self.assertGreaterEqual(total, 1)
        self.assertEqual(emails[0].id, "find_1")

    def test_find_emails_provider_filter(self):
        """find_emails filtre correctement par provider."""
        self.storage.upsert_email(_make_email("gmail_1"), "gmail")
        self.storage.upsert_email(_make_email("outlook_1"), "outlook")
        emails, _ = self.storage.find_emails(provider_filter="gmail")
        self.assertTrue(all(e.provider == Provider.GMAIL for e in emails))

    def test_update_and_get_last_sync_time(self):
        """update_last_sync_time met à jour la ligne unique, get_last_sync_time la lit."""
        self.assertIsNone(self.storage.get_last_sync_time())
        self.storage.update_last_sync_time()
        t1 = self.storage.get_last_sync_time()
        self.assertIsNotNone(t1)
        time.sleep(0.01)
        self.storage.update_last_sync_time()
        t2 = self.storage.get_last_sync_time()
        self.assertGreaterEqual(t2, t1)

    def test_update_last_sync_time_single_row(self):
        """update_last_sync_time ne crée qu'une seule ligne dans sync_metadata."""
        self.storage.update_last_sync_time()
        self.storage.update_last_sync_time()
        self.storage.update_last_sync_time()
        session = create_session()
        try:
            from sqlalchemy import select, func  # pylint: disable=import-outside-toplevel
            count = session.execute(select(func.count(SyncMetadataModel.id))).scalar()  # pylint: disable=not-callable
            self.assertEqual(count, 1)
        finally:
            session.close()


if __name__ == "__main__":
    unittest.main()
