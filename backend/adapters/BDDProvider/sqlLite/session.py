
from pathlib import Path
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool


_engine = None
_SessionLocal: sessionmaker | None = None


def init_engine(db_path: Path | str) -> None:
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
    if _engine is None:
        raise RuntimeError("Database engine not initialized. Call init_engine() first.")
    return _engine


def get_session() -> Generator[Session, None, None]:
    if _SessionLocal is None:
        raise RuntimeError("Database session factory not initialized. Call init_engine() first.")
    session = _SessionLocal()
    try:
        yield session
    finally:
        session.close()


def create_session() -> Session:
    if _SessionLocal is None:
        raise RuntimeError("Database session factory not initialized. Call init_engine() first.")
    return _SessionLocal()


def dispose_engine() -> None:
    global _engine
    if _engine is not None:
        _engine.dispose()
        _engine = None
