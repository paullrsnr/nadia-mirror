import re
import base64
from email.utils import parseaddr
from typing import Tuple, Optional
from backend.api.schemas import EmailAddress
from backend.utils.textCleaner import html_to_text


def parse_email_address(address_string: str) -> EmailAddress:
    """Parse une chaîne d'adresse email (ex: "John Doe <john@example.com>")"""
    if not address_string or not address_string.strip():
        return EmailAddress(email="")
    
    name, email = parseaddr(address_string)
    return EmailAddress(name=name if name else None, email=email)


def extract_email_body(payload: dict) -> Tuple[str, Optional[str]]:
    """Extrait le corps texte et HTML d'un email depuis le payload Gmail"""
    body_text = ""
    body_html = None
    
    def extract_from_part(part: dict):
        nonlocal body_text, body_html
        
        mime_type = part.get("mimeType", "")
        body_data = part.get("body", {})
        
        if mime_type == "text/plain":
            data = body_data.get("data")
            if data:
                body_text = base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")
        elif mime_type == "text/html":
            data = body_data.get("data")
            if data:
                body_html = base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")
                # Si on n'a pas de texte, convertir HTML en texte
                if not body_text:
                    body_text = html_to_text(body_html)
        
        # Récursion pour les parties multipart
        if "parts" in part:
            for subpart in part["parts"]:
                extract_from_part(subpart)
    
    extract_from_part(payload)
    
    # Si on n'a que du HTML, convertir en texte
    if body_html and not body_text:
        body_text = html_to_text(body_html)
    
    # Si on n'a rien, retourner un message par défaut
    if not body_text:
        body_text = "[Corps de l'email non disponible]"
    
    return body_text, body_html
