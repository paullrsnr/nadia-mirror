# pylint: disable=invalid-name
"""Dépendances API : résolution des adapters (credentials → provider concret)."""
from backend.ports.emailProvider import EmailProvider
from backend.adapters.gmailAdapter import GmailAdapter
from backend.core.services.credentialsService import get_credentials


def get_email_provider() -> EmailProvider:
    """Retourne le provider d'email (Gmail) pour l'utilisateur authentifié.
    Lève ValueError si pas de credentials."""
    credentials = get_credentials()
    if not credentials:
        raise ValueError("Non authentifié")
    return GmailAdapter()
