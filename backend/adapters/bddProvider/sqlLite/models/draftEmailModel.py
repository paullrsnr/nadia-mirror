# pylint: disable=too-few-public-methods
from typing import Optional

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.adapters.bddProvider.sqlLite.models.base import Base


class DraftEmailModel(Base):
    __tablename__ = "email_drafts"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    provider: Mapped[str] = mapped_column(String, nullable=False)
    to_addresses: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    cc_addresses: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    bcc_addresses: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    subject: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    body_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    body_html: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    in_reply_to_email_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    updated_at: Mapped[str] = mapped_column(String, nullable=False)

    def __repr__(self) -> str:
        return f"DraftEmailModel(id={self.id!r}, subject={self.subject!r})"
