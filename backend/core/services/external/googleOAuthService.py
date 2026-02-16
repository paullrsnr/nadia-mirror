# pylint: disable=invalid-name
"""Service pour les appels à l'API OAuth Google."""
from google_auth_oauthlib.flow import Flow

from backend.config.settings import auth_settings


# URLs OAuth Google
GOOGLE_AUTH_URI = "https://accounts.google.com/o/oauth2/auth"
GOOGLE_TOKEN_URI = "https://oauth2.googleapis.com/token"


def create_gmail_oauth_flow() -> Flow:
    """Crée le flux OAuth2 pour Gmail.

    Returns:
        Flow: Flux OAuth2 configuré pour Gmail

    Raises:
        ValueError: Si les credentials Gmail ne sont pas configurés
    """
    if not auth_settings.GMAIL_CLIENT_ID or not auth_settings.GMAIL_CLIENT_SECRET:
        raise ValueError(
            "GMAIL_CLIENT_ID et GMAIL_CLIENT_SECRET doivent être configurés"
        )

    redirect_uri = auth_settings.GMAIL_REDIRECT_URI.strip()
    client_config = {
        "web": {
            "client_id": auth_settings.GMAIL_CLIENT_ID,
            "client_secret": auth_settings.GMAIL_CLIENT_SECRET,
            "auth_uri": GOOGLE_AUTH_URI,
            "token_uri": GOOGLE_TOKEN_URI,
            "redirect_uris": [redirect_uri],
        }
    }

    try:
        return Flow.from_client_config(
            client_config,
            scopes=auth_settings.GMAIL_SCOPES,
            redirect_uri=redirect_uri,
        )
    except Exception as error:
        raise ValueError(f"Erreur lors de la création du flux OAuth2: {error!s}") from error


def generate_gmail_auth_url(state: str) -> str:
    """Génère une URL d'authentification OAuth2 pour Gmail.

    Args:
        state: État à inclure dans l'URL (généralement le nom du provider)

    Returns:
        str: URL d'authentification complète
    """
    flow = create_gmail_oauth_flow()
    auth_url, _ = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",
        state=state,
    )
    return auth_url


def exchange_gmail_code_for_credentials(code: str):
    """Échange un code OAuth contre des credentials Gmail.

    Args:
        code: Code OAuth retourné par Google

    Returns:
        Credentials: Credentials Google OAuth2
    """
    flow = create_gmail_oauth_flow()
    flow.fetch_token(code=code)
    return flow.credentials
