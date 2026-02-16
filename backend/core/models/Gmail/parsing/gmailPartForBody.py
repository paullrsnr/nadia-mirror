# pylint: disable=invalid-name
"""Modèle pour les parts Gmail lors du parsing du corps."""
from dataclasses import dataclass, field

from backend.core.models.Gmail.parsing.gmailBodyData import GmailBodyData


@dataclass
class GmailPartForBody:
    """Part Gmail pour l'extraction du corps du message.

    Structure récursive qui permet de parcourir les parts d'un
    message Gmail pour extraire le contenu text/plain et text/html.

    Attributes:
        mime_type: Type MIME de la part (ex: 'text/plain', 'text/html', 'multipart/alternative')
        body: Données du corps avec le champ 'data' en base64
        parts: Sous-parts pour les messages multipart (structure récursive)
    """

    mime_type: str = ""
    body: GmailBodyData = field(default_factory=GmailBodyData)
    parts: list["GmailPartForBody"] = field(default_factory=list)
