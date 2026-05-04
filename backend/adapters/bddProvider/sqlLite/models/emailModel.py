# pylint: disable=too-few-public-methods
from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.adapters.bddProvider.sqlLite.models.base import Base

if TYPE_CHECKING:
    from backend.adapters.bddProvider.sqlLite.models.categoryModel import CategoryModel


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
    category_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("categories.id"), nullable=True)
    category_rel: Mapped[Optional[CategoryModel]] = relationship("CategoryModel", lazy="select")
    draft_reply: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_archived: Mapped[bool] = mapped_column(default=False, nullable=False)
    pending_archive: Mapped[bool] = mapped_column(default=False, nullable=False)

    def __repr__(self) -> str:
        return f"EmailModel(id={self.id!r}, subject={self.subject!r}, provider={self.provider!r})"
