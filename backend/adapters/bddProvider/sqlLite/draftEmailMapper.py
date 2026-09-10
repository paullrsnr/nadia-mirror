from datetime import datetime

from backend.core.models.email import DraftEmail
from backend.adapters.bddProvider.sqlLite import addressMapper
from backend.adapters.bddProvider.sqlLite.models.draftEmailModel import DraftEmailModel


def to_domain(model: DraftEmailModel) -> DraftEmail:
    return DraftEmail(
        id=model.id,
        provider=model.provider,
        to_addresses=addressMapper.from_json(model.to_addresses),
        cc_addresses=addressMapper.from_json(model.cc_addresses),
        bcc_addresses=addressMapper.from_json(model.bcc_addresses),
        subject=model.subject or "",
        body_text=model.body_text or "",
        body_html=model.body_html,
        updated_at=datetime.fromisoformat(model.updated_at),
        in_reply_to_email_id=model.in_reply_to_email_id,
    )


def to_model(draft: DraftEmail) -> DraftEmailModel:
    return DraftEmailModel(
        id=draft.id,
        provider=draft.provider,
        to_addresses=addressMapper.to_json(draft.to_addresses),
        cc_addresses=addressMapper.to_json(draft.cc_addresses),
        bcc_addresses=addressMapper.to_json(draft.bcc_addresses),
        subject=draft.subject,
        body_text=draft.body_text,
        body_html=draft.body_html,
        in_reply_to_email_id=draft.in_reply_to_email_id,
        updated_at=draft.updated_at.isoformat(),
    )
