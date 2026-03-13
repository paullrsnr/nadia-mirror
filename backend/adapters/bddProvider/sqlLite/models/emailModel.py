# pylint: disable=too-few-public-methods
from typing import Optional

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.adapters.bddProvider.sqlLite.models.base import Base


class EmailModel(Base):
    __tablename__ = "emails"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    thread_id: Mapped[Optional[str]] = mapped_column(String, nullable=True, index=True)
    subject: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    from_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    from_email: Mapped[str] = mapped_column(String, nullable=False, index=True)
    to_addresses: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    cc_addresses: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    bcc_addresses: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    date: Mapped[str] = mapped_column(String, nullable=False, index=True)
    body_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    body_html: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    attachments: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    labels: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    snippet: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    provider: Mapped[str] = mapped_column(String, nullable=False)

    def __repr__(self) -> str:
        return f"EmailModel(id={self.id!r}, subject={self.subject!r}, provider={self.provider!r})"
