# pylint: disable=invalid-name
"""Utilitaires pour parser les emails."""
import base64
from dataclasses import dataclass, field
from email.utils import parseaddr
from typing import Optional, Tuple

from backend.core.models.email import EmailAddress
from backend.utils.textCleaner import html_to_text


def parse_email_address(address_string: str) -> EmailAddress:
    """Parse une chaîne d'adresse email (ex: 'John Doe <john@example.com>')."""
    if not address_string or not address_string.strip():
        return EmailAddress(email="")

    name, email = parseaddr(address_string)
    return EmailAddress(name=name if name else None, email=email)


@dataclass
class GmailBodyData:
    """Données body d'une part Gmail (champ optionnel 'data' en base64)."""

    data: Optional[str] = None


@dataclass
class GmailPartForBody:
    """Part Gmail pour l'extraction du corps : mimeType, body.data, sous-parts."""

    mime_type: str = ""
    body: GmailBodyData = field(default_factory=GmailBodyData)
    parts: list["GmailPartForBody"] = field(default_factory=list)


def _parse_gmail_part_from_dict(part_dict: dict) -> GmailPartForBody:
    """Mappe un dict (JSON Gmail) vers GmailPartForBody (récursif)."""
    body_dict = part_dict.get("body") or {}
    return GmailPartForBody(
        mime_type=part_dict.get("mimeType", ""),
        body=GmailBodyData(data=body_dict.get("data")),
        parts=[
            _parse_gmail_part_from_dict(sub)
            for sub in part_dict.get("parts") or []
        ],
    )


def _parse_gmail_payload_to_parts(payload: dict) -> list[GmailPartForBody]:
    """Construit la liste de parts Gmail à partir du payload (niveau racine ou part)."""
    if "parts" in payload:
        return [_parse_gmail_part_from_dict(p) for p in payload["parts"]]
    # Payload sans "parts" : traiter comme une seule part (ex. message simple)
    return [_parse_gmail_part_from_dict(payload)]


def _decode_gmail_base64(data: Optional[str]) -> str:
    """Décode le champ data base64url Gmail en chaîne UTF-8."""
    if not data:
        return ""
    try:
        return base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")
    except (ValueError, UnicodeDecodeError):
        return ""


def _text_and_html_from_part(part: GmailPartForBody) -> Tuple[str, Optional[str]]:
    """Retourne (texte, html) pour une part Gmail (récursif sur part.parts)."""
    part_text = ""
    part_html: Optional[str] = None
    if part.mime_type == "text/plain" and part.body.data:
        part_text = _decode_gmail_base64(part.body.data)
    elif part.mime_type == "text/html" and part.body.data:
        part_html = _decode_gmail_base64(part.body.data)
        part_text = html_to_text(part_html) if part_html else ""

    if part.parts:
        sub_text, sub_html = _extract_text_and_html_from_parts(part.parts)
        if not part_text:
            part_text = sub_text
        if part_html is None:
            part_html = sub_html
    return part_text, part_html


def _extract_text_and_html_from_parts(
    parts: list[GmailPartForBody],
) -> Tuple[str, Optional[str]]:
    """Parcourt les parts Gmail (récursif), retourne le premier text/plain et text/html."""
    body_text = ""
    body_html: Optional[str] = None
    for part in parts:
        part_text, part_html = _text_and_html_from_part(part)
        if not body_text and part_text:
            body_text = part_text
        if body_html is None and part_html is not None:
            body_html = part_html
    return body_text, body_html


def extract_gmail_body(payload: dict) -> Tuple[str, Optional[str]]:
    """Extrait le corps texte et HTML depuis le payload JSON Gmail (structure maîtrisée)."""
    parts = _parse_gmail_payload_to_parts(payload)
    body_text, body_html = _extract_text_and_html_from_parts(parts)

    if body_html and not body_text:
        body_text = html_to_text(body_html)
    if not body_text:
        body_text = "[Corps de l'email non disponible]"

    return body_text, body_html


def extract_email_body(payload: dict) -> Tuple[str, Optional[str]]:
    """Extrait le corps texte et HTML depuis un payload Gmail."""
    return extract_gmail_body(payload)
