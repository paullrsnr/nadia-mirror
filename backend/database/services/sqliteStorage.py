# pylint: disable=invalid-name,import-outside-toplevel
"""Stockage SQLite pour les emails avec SQLAlchemy.

Cette classe est une facade qui utilise SQLAlchemy et Alembic pour
gérer la base de données. Elle délègue toutes les opérations CRUD
au EmailRepository.
"""
import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional

from backend.config.providers import EmailProvider
from backend.core.models.email import Email
from backend.database.services.emailRepository import EmailRepository
from backend.database.session import init_engine, create_session

logger = logging.getLogger(__name__)


class SqliteStorage:
    """Stockage local SQLite pour les emails avec SQLAlchemy.

    Le répertoire de données (data_dir) est storage_settings.DATA_DIR (~/.nadia).
    """

    def __init__(self, data_dir: Path | None = None) -> None:
        """Initialise le stockage.

        Args:
            data_dir: Répertoire de stockage (emails.db sera créé dedans).
                     Si None, utilise storage_settings.DATA_DIR.
        """
        from backend.config.settings import storage_settings

        self._data_dir = data_dir or storage_settings.DATA_DIR
        self._data_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = self._data_dir / "emails.db"
        self._migrate_legacy_data_if_needed()
        self._init_database()

    def _migrate_legacy_data_if_needed(self) -> None:
        """Migre les anciennes données (user_spaces/default/) vers DATA_DIR si nécessaire."""
        from backend.config.settings import storage_settings

        if self.db_path.exists():
            return
        # Ancien emplacement multi-user : user_spaces/default/
        legacy_user_space = storage_settings.DATA_DIR / "user_spaces" / "default"
        legacy_db = legacy_user_space / "emails.db"
        if not legacy_db.exists():
            return
        logger.info("Migration user_spaces/default/ → DATA_DIR : %s", legacy_db)
        shutil.copy2(legacy_db, self.db_path)
        for token_file in legacy_user_space.glob("tokens_*.json"):
            dest = self._data_dir / token_file.name
            if not dest.exists():
                shutil.copy2(token_file, dest)

    def _init_database(self) -> None:
        """Initialise l'engine SQLAlchemy et crée les tables si nécessaire.

        Note: Les migrations Alembic doivent être exécutées manuellement
        avec 'alembic upgrade head' dans backend/database/.
        """
        init_engine(self.db_path)

        # Créer les tables si elles n'existent pas (pour les nouvelles installations)
        from backend.database.models import Base
        from backend.database.session import get_engine
        Base.metadata.create_all(bind=get_engine())

    def save_email(self, email: Email, provider: str = EmailProvider.GMAIL.value) -> bool:
        """Sauvegarde un email dans la base de données (avec la boîte d'origine).

        Args:
            email: Email à sauvegarder.
            provider: Provider d'origine (gmail ou outlook).

        Returns:
            True si succès, False sinon.
        """
        session = create_session()
        try:
            repository = EmailRepository(session)
            return repository.save_email(email, provider)
        finally:
            session.close()

    def get_emails(
        self,
        max_results: int = 50,
        offset: int = 0,
        provider_filter: str | None = None,
    ) -> tuple[list[Email], int]:
        """Retourne les emails en base (paginés). provider_filter: gmail, outlook, ou None/all.

        Args:
            max_results: Nombre maximum de résultats.
            offset: Offset pour la pagination.
            provider_filter: Filtre par provider (gmail, outlook) ou None pour tous.

        Returns:
            Tuple (liste d'emails, total).
        """
        session = create_session()
        try:
            repository = EmailRepository(session)
            return repository.get_emails(max_results, offset, provider_filter)
        finally:
            session.close()

    def get_last_sync_time(self) -> Optional[datetime]:
        """Récupère le timestamp de la dernière synchronisation.

        Returns:
            Datetime de la dernière sync ou None.
        """
        session = create_session()
        try:
            repository = EmailRepository(session)
            return repository.get_last_sync_time()
        finally:
            session.close()

    def update_last_sync_time(self) -> None:
        """Met à jour le timestamp de dernière synchronisation."""
        session = create_session()
        try:
            repository = EmailRepository(session)
            repository.update_last_sync_time()
        finally:
            session.close()
