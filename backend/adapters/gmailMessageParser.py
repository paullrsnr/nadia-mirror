"""Parsing et mapping des messages Gmail (JSON brut -> Email métier).

Ce module encapsule :
- les modèles Pydantic qui décrivent le JSON Gmail que l'on consomme
- la fonction de mapping vers le modèle métier `Email`
"""
from datetime import datetime
from email.utils import parsedate_to_datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict

from backend.core.models.email import Email, EmailAttachment
from backend.utils.emailParser import parse_email_address, extract_email_body


class GmailBody(BaseModel):
    """Représentation typée de la partie 'body' d'une part Gmail."""

    size: int = 0
    attachment_id: Optional[str] = Field(default=None, alias="attachmentId")


class GmailPart(BaseModel):
    """Représentation typée d'une part du payload Gmail."""

    filename: str = ""
    mime_type: str = Field(
        default="application/octet-stream",
        alias="mimeType",
    )
    body: GmailBody


class GmailHeader(BaseModel):
    """Header individuel d'un message Gmail."""

    name: str
    value: str


class GmailPayload(BaseModel):
    """Payload normalisé d'un message Gmail."""

    headers: list[GmailHeader] = Field(default_factory=list)
    parts: list[GmailPart] = Field(default_factory=list)


class GmailMessage(BaseModel):
    """Message Gmail typé, correspondant au JSON renvoyé par l'API Gmail."""

    id: str
    thread_id: str = Field(alias="threadId")
    payload: GmailPayload
    label_ids: list[str] = Field(default_factory=list, alias="labelIds")
    snippet: Optional[str] = None

    model_config = ConfigDict(
        extra="ignore",  # on ignore les champs qu'on ne mappe pas
        populate_by_name=True,  # permet d'utiliser 'thread_id' ou 'threadId'
    )


def parse_gmail_message(message: dict) -> Email:
    """Transforme un message Gmail brut (JSON) en objet Email métier."""
    gmail_message = GmailMessage.model_validate(message)

    # Headers normalisés (nom en minuscule)
    header_dict = {
        h.name.lower(): h.value for h in gmail_message.payload.headers
    }

    # Adresses
    from_addr = parse_email_address(header_dict.get("from", ""))
    to_addrs = [
        parse_email_address(addr)
        for addr in header_dict.get("to", "").split(",")
        if addr.strip()
    ]
    cc_addrs = [
        parse_email_address(addr)
        for addr in header_dict.get("cc", "").split(",")
        if addr.strip()
    ]

    # Date (RFC 2822)
    date_str = header_dict.get("date")
    try:
        date = parsedate_to_datetime(date_str) if date_str else datetime.now()
    except (ValueError, TypeError):
        date = datetime.now()

    # Corps du message : on repasse par un dict de payload "gmail-like"
    body_text, body_html = extract_email_body(
        gmail_message.payload.model_dump(by_alias=True)
    )

    # Pièces jointes
    attachments = [
        EmailAttachment(
            filename=part.filename,
            mime_type=part.mime_type,
            size=part.body.size,
            attachment_id=part.body.attachment_id,
        )
        for part in gmail_message.payload.parts
        if part.filename and part.body.attachment_id
    ]

    return Email(
        id=gmail_message.id,
        thread_id=gmail_message.thread_id,
        subject=header_dict.get("subject", ""),
        from_address=from_addr,
        to_addresses=to_addrs,
        cc_addresses=cc_addrs,
        bcc_addresses=[],
        date=date,
        body_text=body_text,
        body_html=body_html,
        attachments=attachments,
        labels=gmail_message.label_ids,
        snippet=gmail_message.snippet,
    )
