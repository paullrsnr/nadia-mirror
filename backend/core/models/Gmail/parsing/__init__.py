# pylint: disable=invalid-name
"""Modèles simplifiés pour le parsing du corps des messages Gmail.

Ces modèles sont spécifiquement conçus pour l'extraction du corps
des messages Gmail, avec support du champ 'data' en base64 et
de la structure récursive des parts.
"""
from backend.core.models.Gmail.parsing.gmailBodyData import GmailBodyData
from backend.core.models.Gmail.parsing.gmailPartForBody import GmailPartForBody

__all__ = ["GmailBodyData", "GmailPartForBody"]
