from datetime import datetime
from typing import Optional

from backend.core.models.email import Email, EmailAddress, EmailAttachment
from backend.core.models.email.provider import Provider
from backend.adapters.mailProvider.Outlook.models import GraphMessage, GraphRecipient


def graph_request_headers(access_token: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }


def parse_outlook_message(message: dict) -> Email:
    graph_message = GraphMessage.model_validate(message)

    body_text, body_html = _body_text_and_html(graph_message)
    msg_id = graph_message.id or ""
    thread_id = graph_message.conversation_id or msg_id

    attachments = [
        EmailAttachment(
            filename=a.name,
            mime_type=a.content_type,
            size=a.size,
            attachment_id=a.id,
        )
        for a in graph_message.attachments
        if a.id
    ]

    return Email(
        id=msg_id,
        thread_id=thread_id,
        subject=graph_message.subject or "",
        from_address=_graph_address_to_email_address(graph_message.from_),
        to_addresses=[
            _graph_address_to_email_address(r) for r in graph_message.to_recipients
        ],
        date=_parse_graph_datetime(graph_message.received_date_time),
        body_text=body_text,
        body_html=body_html,
        attachments=attachments,
        snippet=graph_message.body_preview,
        provider=Provider.OUTLOOK,
    )

def _graph_address_to_email_address(recipient: Optional[GraphRecipient]) -> EmailAddress:
    if not recipient:
        return EmailAddress(email="")
    addr = recipient.email_address
    return EmailAddress(email=addr.address or "", name=addr.name)


def _parse_graph_datetime(received: Optional[str]) -> datetime:
    if not received:
        return datetime.now()
    try:
        return datetime.fromisoformat(str(received).replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return datetime.now()


def _body_text_and_html(msg: GraphMessage) -> tuple[str, Optional[str]]:
    body = msg.body
    preview = msg.body_preview or ""
    if not body:
        return (preview or "[Corps non disponible]", None)
    content = body.content or ""
    content_type = (body.content_type or "text").lower()
    if content_type == "text":
        return (content or preview or "[Corps non disponible]", None)
    if content_type == "html":
        return (preview or "[Corps non disponible]", content or None)
    return (preview or "[Corps non disponible]", None)
    