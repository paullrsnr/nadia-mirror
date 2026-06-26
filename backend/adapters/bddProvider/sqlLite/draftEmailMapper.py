import json
from datetime import datetime

from backend.core.models.email import DraftEmail, EmailAddress
from backend.adapters.bddProvider.sqlLite.models.draftEmailModel import DraftEmailModel


def to_domain(model: DraftEmailModel) -> DraftEmail:
    return DraftEmail(
        id=model.id,
        provider=model.provider,
        to_addresses=_parse_addresses(model.to_addresses),
        cc_addresses=_parse_addresses(model.cc_addresses),
        bcc_addresses=_parse_addresses(model.bcc_addresses),
        subject=model.subject or "",
        body_text=model.body_text or "",
        body_html=model.body_html,
        updated_at=datetime.fromisoformat(model.updated_at) if model.updated_at else datetime.now(),
        in_reply_to_email_id=model.in_reply_to_email_id,
    )


def to_model(draft: DraftEmail) -> DraftEmailModel:
    return DraftEmailModel(
        id=draft.id,
        provider=draft.provider,
        to_addresses=json.dumps([{"name": a.name, "email": a.email} for a in draft.to_addresses]),
        cc_addresses=json.dumps([{"name": a.name, "email": a.email} for a in draft.cc_addresses]),
        bcc_addresses=json.dumps([{"name": a.name, "email": a.email} for a in draft.bcc_addresses]),
        subject=draft.subject,
        body_text=draft.body_text,
        body_html=draft.body_html,
        in_reply_to_email_id=draft.in_reply_to_email_id,
        updated_at=draft.updated_at.isoformat(),
    )


def _parse_addresses(data: str | None) -> list[EmailAddress]:
    if not data or data == "null":
        return []
    return [EmailAddress(email=a["email"], name=a.get("name")) for a in json.loads(data)]
