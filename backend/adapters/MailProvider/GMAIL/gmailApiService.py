# pylint: disable=invalid-name
"""Client Gmail API (construction du service, récupération de l'email utilisateur)."""
from typing import Optional

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build


_GMAIL_API_NAME = "gmail"
_GMAIL_API_VERSION = "v1"


def build_gmail_service(credentials: Credentials):
    """Construit et retourne le service Gmail API prêt à l'emploi."""
    # pylint: disable=no-member
    return build(_GMAIL_API_NAME, _GMAIL_API_VERSION, credentials=credentials)


def get_gmail_user_email(credentials: Credentials) -> Optional[str]:
    """Récupère l'adresse email de l'utilisateur connecté via l'API Gmail."""
    try:
        service = build_gmail_service(credentials)
        profile = service.users().getProfile(userId="me").execute()  # pylint: disable=no-member
        return profile.get("emailAddress")
    except Exception:
        return None
