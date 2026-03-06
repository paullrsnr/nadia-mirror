import base64
from typing import Optional, Tuple

from backend.adapters.mailProvider.GMAIL.models import GmailBodyData, GmailPartForBody
from backend.utils.textCleaner import html_to_text


def parse_gmail_part_from_dict(part_dict: dict) -> GmailPartForBody:
    body_dict = part_dict.get("body") or {}
    return GmailPartForBody(
        mime_type=part_dict.get("mimeType", ""),
        body=GmailBodyData(data=body_dict.get("data")),
        parts=[
            parse_gmail_part_from_dict(sub)
            for sub in part_dict.get("parts") or []
        ],
    )


def parse_gmail_payload_to_parts(payload: dict) -> list[GmailPartForBody]:
    if "parts" in payload:
        return [parse_gmail_part_from_dict(p) for p in payload["parts"]]
    return [parse_gmail_part_from_dict(payload)]


def decode_gmail_base64(data: Optional[str]) -> str:
    if not data:
        return ""
    try:
        return base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")
    except (ValueError, UnicodeDecodeError):
        return ""


def text_and_html_from_part(part: GmailPartForBody) -> Tuple[str, Optional[str]]:
    part_text = ""
    part_html: Optional[str] = None

    if part.mime_type == "text/plain" and part.body.data:
        part_text = decode_gmail_base64(part.body.data)
    elif part.mime_type == "text/html" and part.body.data:
        part_html = decode_gmail_base64(part.body.data)
        part_text = html_to_text(part_html) if part_html else ""

    if part.parts:
        sub_text, sub_html = extract_text_and_html_from_parts(part.parts)
        if not part_text:
            part_text = sub_text
        if part_html is None:
            part_html = sub_html

    return part_text, part_html


def extract_text_and_html_from_parts(
    parts: list[GmailPartForBody],
) -> Tuple[str, Optional[str]]:
    body_text = ""
    body_html: Optional[str] = None

    for part in parts:
        part_text, part_html = text_and_html_from_part(part)
        if not body_text and part_text:
            body_text = part_text
        if body_html is None and part_html is not None:
            body_html = part_html

    return body_text, body_html


def extract_gmail_body(payload: dict) -> Tuple[str, Optional[str]]:
    parts = parse_gmail_payload_to_parts(payload)
    body_text, body_html = extract_text_and_html_from_parts(parts)

    if body_html and not body_text:
        body_text = html_to_text(body_html)

    if not body_text:
        body_text = "[Corps de l'email non disponible]"

    return body_text, body_html
