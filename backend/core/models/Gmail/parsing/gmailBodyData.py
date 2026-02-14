# pylint: disable=invalid-name
"""Modèle pour les données body d'une part Gmail lors du parsing."""
from dataclasses import dataclass
from typing import Optional


@dataclass
class GmailBodyData:
    """Données body d'une part Gmail pour l'extraction du corps.
    
    Contient le champ optionnel 'data' en base64 qui représente
    le contenu textuel ou HTML du message.
    """

    data: Optional[str] = None
