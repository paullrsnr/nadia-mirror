# pylint: disable=invalid-name
"""Utilitaires génériques pour parser les emails.

Ce module contient les fonctions de parsing génériques utilisables
par tous les providers (Gmail, Outlook, etc.).

Pour les fonctions spécifiques à Gmail, voir:
    backend.adapters.MailProvider.GMAIL.gmailBodyParser
"""
from email.utils import parseaddr
from typing import Optional, Tuple

from backend.core.models.email import EmailAddress


def parse_email_address(address_string: str) -> EmailAddress:
    """Parse une chaîne d'adresse email (ex: 'John Doe <john@example.com>').

    Utilise le module standard email.utils pour un parsing robuste.

    Args:
        address_string: Chaîne d'adresse au format RFC 2822

    Returns:
        EmailAddress: Objet avec name (optionnel) et email

    Examples:
        >>> parse_email_address("John Doe <john@example.com>")
        EmailAddress(name="John Doe", email="john@example.com")
        >>> parse_email_address("john@example.com")
        EmailAddress(name=None, email="john@example.com")
    """
    if not address_string or not address_string.strip():
        return EmailAddress(email="")

    name, email = parseaddr(address_string)
    return EmailAddress(name=name if name else None, email=email)


def extract_email_body(payload: dict) -> Tuple[str, Optional[str]]:
    """Extrait le corps texte et HTML depuis un payload email.

    Actuellement supporte uniquement Gmail. Pour ajouter d'autres providers,
    détecter le format et router vers le parser approprié.

    Args:
        payload: Dictionnaire du payload (format Gmail pour l'instant)

    Returns:
        Tuple[str, Optional[str]]: (texte brut, html ou None)
    """
    # Import local pour éviter la dépendance circulaire
    from backend.adapters.MailProvider.GMAIL.gmailBodyParser import extract_gmail_body
    return extract_gmail_body(payload)
