"""Parsing et mapping des messages Outlook (Microsoft Graph JSON -> Email métier).

Ce module encapsule la fonction de mapping vers le modèle métier `Email`
et les headers HTTP pour les appels Graph. Les modèles Pydantic (GraphMessage, etc.)
sont dans backend.core.models.Graph.
"""
from datetime import datetime
from typing import Optional

from backend.core.models.Email import Email, EmailAddress
from backend.adapters.MailProvider.Outlook.models import GraphMessage, GraphRecipient


BODY_FALLBACK = "[Corps non disponible]"


def graph_request_headers(access_token: str) -> dict[str, str]:
    """Headers HTTP pour les requêtes Microsoft Graph."""
    return {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }


def _graph_address_to_email_address(recipient: Optional[GraphRecipient]) -> EmailAddress:
    """Construit EmailAddress depuis un GraphRecipient."""
    if not recipient:
        return EmailAddress(email="")
    addr = recipient.email_address
    return EmailAddress(email=addr.address or "", name=addr.name)


def _parse_graph_datetime(received: Optional[str]) -> datetime:
    """Parse receivedDateTime Graph (ISO avec Z) en datetime."""
    if not received:
        return datetime.now()
    try:
        return datetime.fromisoformat(str(received).replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return datetime.now()


def _body_text_and_html(msg: GraphMessage) -> tuple[str, Optional[str]]:
    """Extrait body_text et body_html depuis le body du message Graph."""
    body = msg.body
    preview = msg.body_preview or ""
    if not body:
        return (preview or BODY_FALLBACK, None)
    content = body.content or ""
    content_type = (body.content_type or "text").lower()
    if content_type == "text":
        return (content or preview or BODY_FALLBACK, None)
    if content_type == "html":
        return (preview or BODY_FALLBACK, content or None)
    return (preview or BODY_FALLBACK, None)


def parse_outlook_message(message: dict) -> Email:
    """Transforme un message Microsoft Graph brut (JSON) en objet Email métier."""
    graph_message = GraphMessage.model_validate(message)

    body_text, body_html = _body_text_and_html(graph_message)
    msg_id = graph_message.id or ""
    thread_id = graph_message.conversation_id or msg_id

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
        snippet=graph_message.body_preview,
    )
