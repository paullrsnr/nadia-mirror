# pylint: disable=invalid-name
"""Service pour les appels à l'API Gmail de Google."""
from typing import Optional

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build


# Version de l'API Gmail (seule version stable officielle de Google)
GMAIL_API_VERSION = "v1"
GMAIL_API_NAME = "gmail"


def get_user_email_address(credentials: Credentials) -> Optional[str]:
    """Récupère l'adresse email de l'utilisateur via l'API Gmail.

    Args:
        credentials: Credentials Google OAuth2

    Returns:
        Optional[str]: Adresse email ou None en cas d'erreur
    """
    try:
        service = build(GMAIL_API_NAME, GMAIL_API_VERSION, credentials=credentials)
        profile = service.users().getProfile(userId="me").execute()
        return profile.get("emailAddress")
    except Exception:
        return None


def build_gmail_service(credentials: Credentials):
    """Construit un service Gmail API.

    Args:
        credentials: Credentials Google OAuth2

    Returns:
        Service Gmail API prêt à l'emploi

    Raises:
        Exception: En cas d'erreur lors de la construction du service
    """
    # pylint: disable=no-member
    return build(GMAIL_API_NAME, GMAIL_API_VERSION, credentials=credentials)
