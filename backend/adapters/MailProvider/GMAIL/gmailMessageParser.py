"""Parsing et mapping des messages Gmail (JSON brut -> Email métier).

Ce module encapsule la fonction de mapping vers le modèle métier `Email`.
Les modèles Pydantic (GmailMessage, etc.) sont dans backend.core.models.Gmail.
"""
from datetime import datetime
from email.utils import parsedate_to_datetime

from backend.core.models.Email import Email, EmailAttachment
from backend.adapters.MailProvider.GMAIL.models import GmailMessage
from backend.utils.emailParser import parse_email_address
from backend.adapters.MailProvider.GMAIL.gmailBodyParser import extract_gmail_body


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

    # Corps : payload brut (GmailPayload n'a pas body/mimeType pour messages simples)
    raw_payload = message.get("payload", {})
    body_text, body_html = extract_gmail_body(raw_payload)

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
