# pylint: disable=invalid-name
"""Parsing du corps des messages Gmail.

Extraction du texte et HTML depuis la structure multipart du payload Gmail.
Utilise les modèles `GmailBodyData` et `GmailPartForBody` pour gérer
la structure récursive des parts.
"""
import base64
from typing import Optional, Tuple

from backend.core.models.Gmail.parsing import GmailBodyData, GmailPartForBody
from backend.utils.textCleaner import html_to_text


def parse_gmail_part_from_dict(part_dict: dict) -> GmailPartForBody:
    """Mappe un dict (JSON Gmail) vers GmailPartForBody (récursif).

    Args:
        part_dict: Dictionnaire représentant une part Gmail

    Returns:
        GmailPartForBody: Part structurée avec body et sous-parts
    """
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
    """Construit la liste de parts Gmail à partir du payload.

    Gère le cas des payloads avec "parts" (multipart) et sans "parts" (simple).

    Args:
        payload: Dictionnaire du payload Gmail (niveau racine ou part)

    Returns:
        list[GmailPartForBody]: Liste des parts à analyser
    """
    if "parts" in payload:
        return [parse_gmail_part_from_dict(p) for p in payload["parts"]]
    # Payload sans "parts" : traiter comme une seule part (ex. message simple)
    return [parse_gmail_part_from_dict(payload)]


def decode_gmail_base64(data: Optional[str]) -> str:
    """Décode le champ data base64url Gmail en chaîne UTF-8.

    Gmail utilise un encodage base64 URL-safe pour le contenu des messages.

    Args:
        data: Chaîne base64url encodée

    Returns:
        str: Texte décodé ou chaîne vide si échec
    """
    if not data:
        return ""
    try:
        return base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")
    except (ValueError, UnicodeDecodeError):
        return ""


def text_and_html_from_part(part: GmailPartForBody) -> Tuple[str, Optional[str]]:
    """Retourne (texte, html) pour une part Gmail.

    Parcourt récursivement les sous-parts si nécessaire.
    Convertit le HTML en texte si seul le HTML est disponible.

    Args:
        part: Part Gmail à analyser

    Returns:
        Tuple[str, Optional[str]]: (texte brut, html ou None)
    """
    part_text = ""
    part_html: Optional[str] = None

    if part.mime_type == "text/plain" and part.body.data:
        part_text = decode_gmail_base64(part.body.data)
    elif part.mime_type == "text/html" and part.body.data:
        part_html = decode_gmail_base64(part.body.data)
        part_text = html_to_text(part_html) if part_html else ""

    # Parcourir récursivement les sous-parts
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
    """Parcourt les parts Gmail (récursif), retourne le premier text/plain et text/html.

    Args:
        parts: Liste des parts Gmail à analyser

    Returns:
        Tuple[str, Optional[str]]: (texte brut, html ou None)
    """
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
    """Extrait le corps texte et HTML depuis le payload JSON Gmail.

    Gère la structure multipart complexe de Gmail et retourne
    le contenu text/plain et text/html quand disponibles.

    Args:
        payload: Dictionnaire du payload Gmail

    Returns:
        Tuple[str, Optional[str]]: (texte brut, html ou None)
            Le texte est toujours retourné, même si c'est un fallback.
    """
    parts = parse_gmail_payload_to_parts(payload)
    body_text, body_html = extract_text_and_html_from_parts(parts)

    # Fallback : convertir HTML en texte si pas de texte brut
    if body_html and not body_text:
        body_text = html_to_text(body_html)

    # Fallback final : message par défaut
    if not body_text:
        body_text = "[Corps de l'email non disponible]"

    return body_text, body_html
