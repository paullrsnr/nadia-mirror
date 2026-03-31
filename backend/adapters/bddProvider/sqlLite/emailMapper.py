import json
from datetime import datetime

from backend.core.models.email import Email, EmailAddress, EmailAttachment, Provider
from backend.adapters.bddProvider.sqlLite.models.emailModel import EmailModel


def to_domain(model: EmailModel) -> Email:
    return Email(
        id=model.id,
        thread_id=model.thread_id,
        subject=model.subject or "",
        from_address=EmailAddress(email=model.from_email or "", name=model.from_name),
        to_addresses=_parse_addresses(model.to_addresses),
        cc_addresses=_parse_addresses(model.cc_addresses),
        bcc_addresses=_parse_addresses(model.bcc_addresses),
        date=datetime.fromisoformat(model.date) if model.date else datetime.now(),
        body_text=model.body_text or "",
        body_html=model.body_html,
        attachments=_parse_attachments(model.attachments),
        labels=json.loads(model.labels) if model.labels and model.labels != "null" else [],
        snippet=model.snippet,
        provider=Provider(model.provider) if model.provider else Provider.ALL,
        category=model.category,
    )


def to_model(email: Email, provider: str) -> EmailModel:
    return EmailModel(
        id=email.id,
        thread_id=email.thread_id,
        subject=email.subject,
        from_name=email.from_address.name,
        from_email=email.from_address.email,
        to_addresses=json.dumps([{"name": a.name, "email": a.email} for a in email.to_addresses]),
        cc_addresses=json.dumps([{"name": a.name, "email": a.email} for a in email.cc_addresses]),
        bcc_addresses=json.dumps([{"name": a.name, "email": a.email} for a in email.bcc_addresses]),
        date=email.date.isoformat(),
        body_text=email.body_text,
        body_html=email.body_html,
        attachments=json.dumps([
            {
                "filename": a.filename, "mime_type": a.mime_type,
                "size": a.size, "attachment_id": a.attachment_id,
            }
            for a in email.attachments
        ]),
        labels=json.dumps(email.labels),
        snippet=email.snippet,
        provider=provider.lower(),
        category=email.category,
    )


def _parse_addresses(data: str | None) -> list[EmailAddress]:
    if not data or data == "null":
        return []
    return [EmailAddress(email=a["email"], name=a.get("name")) for a in json.loads(data)]


def _parse_attachments(data: str | None) -> list[EmailAttachment]:
    if not data or data == "null":
        return []
    return [
        EmailAttachment(
            filename=a["filename"],
            mime_type=a["mime_type"],
            size=a["size"],
            attachment_id=a.get("attachment_id"),
        )
        for a in json.loads(data)
    ]
