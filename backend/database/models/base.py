# pylint: disable=invalid-name
"""Classe de base pour les modèles SQLAlchemy."""
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base pour tous les modèles SQLAlchemy."""
    pass
