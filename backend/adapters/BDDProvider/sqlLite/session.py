# pylint: disable=invalid-name
"""Configuration de la session SQLAlchemy et de l'engine."""
from pathlib import Path
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool


_engine = None
_SessionLocal: sessionmaker | None = None


def init_engine(db_path: Path | str) -> None:
    """Initialise l'engine SQLAlchemy avec le chemin de la base de données."""
    global _engine, _SessionLocal

    database_url = f"sqlite:///{db_path}"
    _engine = create_engine(
        database_url,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )
    _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)


def get_engine():
    """Retourne l'engine SQLAlchemy global."""
    if _engine is None:
        raise RuntimeError("Database engine not initialized. Call init_engine() first.")
    return _engine


def get_session() -> Generator[Session, None, None]:
    """Génère une session pour les dépendances FastAPI."""
    if _SessionLocal is None:
        raise RuntimeError("Database session factory not initialized. Call init_engine() first.")
    session = _SessionLocal()
    try:
        yield session
    finally:
        session.close()


def create_session() -> Session:
    """Crée une nouvelle session (pour usage direct)."""
    if _SessionLocal is None:
        raise RuntimeError("Database session factory not initialized. Call init_engine() first.")
    return _SessionLocal()


def dispose_engine() -> None:
    """Ferme toutes les connexions et dispose l'engine. Utile pour les tests."""
    global _engine
    if _engine is not None:
        _engine.dispose()
        _engine = None
