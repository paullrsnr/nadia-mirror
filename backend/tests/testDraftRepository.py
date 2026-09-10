"""Tests unitaires pour le stockage SQLite des brouillons et du dossier des emails."""
import shutil
import tempfile
import unittest
from pathlib import Path
from datetime import datetime, timedelta

from backend.adapters.bddProvider.sqlLite import draftEmailMapper
from backend.adapters.bddProvider.sqlLite.models.base import Base
from backend.adapters.bddProvider.sqlLite.readRepository import SqliteReadRepository
from backend.adapters.bddProvider.sqlLite.session import dispose_engine, get_engine, init_engine
from backend.adapters.bddProvider.sqlLite.writeRepository import SqliteWriteRepository
from backend.core.models.email import DraftEmail, Email, EmailAddress, Provider


def _make_draft(
    draft_id: str = "d1",
    provider: str = "gmail",
    updated_at: datetime | None = None,
) -> DraftEmail:
    return DraftEmail(
        id=draft_id,
        provider=provider,
        to_addresses=[EmailAddress(email="dest@example.com", name="Dest")],
        cc_addresses=[EmailAddress(email="cc@example.com")],
        subject="Sujet",
        body_text="Contenu",
        body_html="<p>Contenu</p>",
        updated_at=updated_at or datetime(2026, 1, 1, 12, 0),
        in_reply_to_email_id="email_42",
    )


def _make_email(email_id: str, folder: str = "inbox") -> Email:
    return Email(
        id=email_id,
        thread_id=f"thread_{email_id}",
        subject="Test",
        from_address=EmailAddress(email="test@example.com"),
        to_addresses=[EmailAddress(email="dest@example.com")],
        date=datetime.now(),
        body_text="Contenu test",
        provider=Provider.GMAIL,
        folder=folder,
    )


class TestDraftEmailMapper(unittest.TestCase):
    """Tests pour la conversion brouillon <-> modèle SQLAlchemy."""

    def test_round_trip_keeps_all_fields(self):
        """Un brouillon converti en modèle puis en domaine reste identique."""
        draft = _make_draft()

        result = draftEmailMapper.to_domain(draftEmailMapper.to_model(draft))

        self.assertEqual(result, draft)


class TestSqliteDraftRepository(unittest.TestCase):
    """Tests des brouillons et du filtre de dossier sur une base SQLite temporaire."""

    def setUp(self):
        self.tmp_dir = Path(tempfile.mkdtemp())
        init_engine(self.tmp_dir / "test.db")
        Base.metadata.create_all(get_engine())
        self.reads = SqliteReadRepository()
        self.writes = SqliteWriteRepository(self.reads)

    def tearDown(self):
        dispose_engine()
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_save_and_find_draft_by_id(self):
        """Un brouillon enregistré est relu à l'identique."""
        draft = _make_draft()

        self.writes.save_draft(draft)

        self.assertEqual(self.reads.find_draft_by_id("d1"), draft)

    def test_find_draft_by_id_missing_returns_none(self):
        """Un identifiant inconnu renvoie None."""
        self.assertIsNone(self.reads.find_draft_by_id("absent"))

    def test_save_draft_twice_updates_existing(self):
        """Enregistrer deux fois le même id met à jour le brouillon."""
        self.writes.save_draft(_make_draft())
        updated = _make_draft()
        updated.subject = "Nouveau sujet"

        self.writes.save_draft(updated)

        drafts = self.reads.find_drafts()
        self.assertEqual(len(drafts), 1)
        self.assertEqual(drafts[0].subject, "Nouveau sujet")

    def test_find_drafts_most_recent_first(self):
        """Les brouillons sont triés du plus récent au plus ancien."""
        base = datetime(2026, 1, 1, 12, 0)
        self.writes.save_draft(_make_draft("old", updated_at=base))
        self.writes.save_draft(_make_draft("new", updated_at=base + timedelta(hours=1)))

        self.assertEqual([d.id for d in self.reads.find_drafts()], ["new", "old"])

    def test_find_drafts_filters_by_provider(self):
        """Le filtre provider ne renvoie que les brouillons de ce provider."""
        self.writes.save_draft(_make_draft("g", provider="gmail"))
        self.writes.save_draft(_make_draft("o", provider="outlook"))

        self.assertEqual([d.id for d in self.reads.find_drafts("outlook")], ["o"])

    def test_delete_draft(self):
        """delete_draft supprime le brouillon."""
        self.writes.save_draft(_make_draft())

        self.writes.delete_draft("d1")

        self.assertIsNone(self.reads.find_draft_by_id("d1"))

    def test_delete_draft_missing_is_idempotent(self):
        """Supprimer un brouillon absent ne lève pas d'erreur."""
        self.writes.delete_draft("absent")

    def test_find_emails_filters_by_folder(self):
        """find_emails ne renvoie que les emails du dossier demandé."""
        self.writes.upsert_emails_batch(
            [_make_email("in1"), _make_email("sent1", folder="sent")], provider="gmail"
        )

        inbox, inbox_total = self.reads.find_emails()
        sent, sent_total = self.reads.find_emails(folder="sent")

        self.assertEqual(([e.id for e in inbox], inbox_total), (["in1"], 1))
        self.assertEqual(([e.id for e in sent], sent_total), (["sent1"], 1))
        self.assertEqual(sent[0].folder, "sent")


if __name__ == "__main__":
    unittest.main()
