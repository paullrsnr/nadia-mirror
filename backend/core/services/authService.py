# pylint: disable=invalid-name
"""Service d'authentification OAuth (flux Gmail, URL, callback, statut)."""
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

from backend.config.settings import auth_settings
from backend.core.models.auth import AuthStatus
from backend.core.services.credentialsService import (
    load_credentials,
    save_credentials,
    clear_credentials,
)


def _get_flow() -> Flow:
    """Crée le flux OAuth2 pour Gmail."""
    if not auth_settings.GMAIL_CLIENT_ID or not auth_settings.GMAIL_CLIENT_SECRET:
        raise ValueError(
            "GMAIL_CLIENT_ID et GMAIL_CLIENT_SECRET doivent être configurés"
        )

    client_config = {
        "web": {
            "client_id": auth_settings.GMAIL_CLIENT_ID,
            "client_secret": auth_settings.GMAIL_CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [auth_settings.GMAIL_REDIRECT_URI],
        }
    }

    try:
        return Flow.from_client_config(
            client_config,
            scopes=auth_settings.GMAIL_SCOPES,
            redirect_uri=auth_settings.GMAIL_REDIRECT_URI,
        )
    except Exception as e:
        raise ValueError(f"Erreur lors de la création du flux OAuth2: {str(e)}") from e


def get_auth_url() -> str:
    """Génère l'URL d'authentification OAuth2."""
    flow = _get_flow()
    auth_url, _ = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",
    )
    return auth_url


def process_callback(code: str) -> None:
    """Échange le code OAuth contre des tokens et sauvegarde les credentials."""
    flow = _get_flow()
    flow.fetch_token(code=code)
    save_credentials(flow.credentials)


def get_auth_status() -> AuthStatus:
    """Retourne le statut d'authentification (connecté ou non, email si disponible)."""
    credentials = load_credentials()

    if not credentials:
        return AuthStatus(is_authenticated=False)

    if credentials.expired and credentials.refresh_token:
        try:
            credentials.refresh(Request())
            save_credentials(credentials)
        except Exception:
            return AuthStatus(is_authenticated=False)

    try:
        service = build("gmail", "v1", credentials=credentials)
        profile = service.users().getProfile(userId="me").execute()
        user_email = profile.get("emailAddress")
        return AuthStatus(is_authenticated=True, email=user_email)
    except Exception:
        return AuthStatus(is_authenticated=True, email=None)


def logout() -> None:
    """Déconnecte l'utilisateur en supprimant les tokens."""
    clear_credentials()
