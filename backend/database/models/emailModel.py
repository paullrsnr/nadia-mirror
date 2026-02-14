# pylint: disable=invalid-name
"""Modèle SQLAlchemy pour les emails."""
from datetime import datetime
from typing import Optional

from sqlalchemy import String, Text, JSON, Index
from sqlalchemy.orm import Mapped, mapped_column

from backend.database.models.base import Base


class EmailModel(Base):
    """Modèle de la table emails en base de données.
    
    Stocke les emails synchronisés depuis Gmail et Outlook.
    """
    __tablename__ = "emails"

    # Colonnes
    id: Mapped[str] = mapped_column(String, primary_key=True)
    thread_id: Mapped[Optional[str]] = mapped_column(String, nullable=True, index=True)
    subject: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    from_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    from_email: Mapped[str] = mapped_column(String, nullable=False, index=True)
    to_addresses: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON string
    cc_addresses: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON string
    bcc_addresses: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON string
    date: Mapped[str] = mapped_column(String, nullable=False, index=True)  # ISO format
    body_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    body_html: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    attachments: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON string
    labels: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON string
    snippet: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    provider: Mapped[str] = mapped_column(String, nullable=False)

    def __repr__(self) -> str:
        return f"EmailModel(id={self.id!r}, subject={self.subject!r}, provider={self.provider!r})"
