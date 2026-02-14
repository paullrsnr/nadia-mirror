# pylint: disable=invalid-name
"""Configuration de la session SQLAlchemy et de l'engine.

Fournit une factory pour créer des sessions de base de données 
et gère la connexion à SQLite de manière centralisée.
"""
from pathlib import Path
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool


# Engine global (initialisé par init_engine)
_engine = None
_SessionLocal: sessionmaker | None = None


def init_engine(db_path: Path | str) -> None:
    """Initialise l'engine SQLAlchemy avec le chemin de la base de données.
    
    Args:
        db_path: Chemin vers le fichier SQLite (emails.db).
    """
    global _engine, _SessionLocal
    
    # SQLite avec check_same_thread=False pour FastAPI
    # StaticPool pour éviter les problèmes de connexion multiples en SQLite
    database_url = f"sqlite:///{db_path}"
    
    _engine = create_engine(
        database_url,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,  # True pour debug SQL
    )
    
    _SessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=_engine,
    )


def get_engine():
    """Retourne l'engine SQLAlchemy global.
    
    Raises:
        RuntimeError: Si l'engine n'a pas été initialisé.
    """
    if _engine is None:
        raise RuntimeError("Database engine not initialized. Call init_engine() first.")
    return _engine


def get_session() -> Generator[Session, None, None]:
    """Génère une session de base de données pour les dépendances FastAPI.
    
    Yields:
        Session: Session SQLAlchemy à utiliser dans un contexte.
    
    Raises:
        RuntimeError: Si l'engine n'a pas été initialisé.
    """
    if _SessionLocal is None:
        raise RuntimeError("Database session factory not initialized. Call init_engine() first.")
    
    session = _SessionLocal()
    try:
        yield session
    finally:
        session.close()


def create_session() -> Session:
    """Crée une nouvelle session de base de données (pour usage direct).
    
    Returns:
        Session: Session SQLAlchemy.
    
    Raises:
        RuntimeError: Si l'engine n'a pas été initialisé.
    """
    if _SessionLocal is None:
        raise RuntimeError("Database session factory not initialized. Call init_engine() first.")
    return _SessionLocal()


def dispose_engine() -> None:
    """Ferme toutes les connexions de l'engine et dispose de l'engine.
    
    Utile pour les tests et le nettoyage.
    """
    global _engine
    if _engine is not None:
        _engine.dispose()
        _engine = None
