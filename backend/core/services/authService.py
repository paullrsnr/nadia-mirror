# pylint: disable=invalid-name
"""Service d'authentification OAuth par provider (Gmail, Outlook)."""
from urllib.parse import quote

from fastapi import HTTPException
from fastapi.responses import RedirectResponse
from google.auth.transport.requests import Request

from backend.config.settings import auth_settings, email_settings
from backend.config.providers import EmailProvider
from backend.config.AuthHandlers import (
    AuthUrlHandler,
    CallbackHandler,
    AuthStatusHandler,
)
from backend.core.models.auth import AuthIdentity
from backend.core.services.connectionOrchestrator import (
    get_connection_credentials,
    save_connection_credentials,
    clear_connection_credentials,
)
from backend.core.services.external import (
    generate_gmail_auth_url,
    generate_outlook_auth_url,
    exchange_gmail_code_for_credentials,
    exchange_outlook_code_for_tokens,
    get_gmail_user_email,
    get_outlook_user_email,
)


def _resolve_provider(provider: str | None) -> str:
    """Retourne le provider à utiliser (défaut = config)."""
    return (provider or email_settings.DEFAULT_PROVIDER).lower()


def _get_gmail_auth_url(resolved_provider: str) -> str:
    """Génère l'URL d'authentification OAuth2 pour Gmail."""
    return generate_gmail_auth_url(state=resolved_provider)


def _get_outlook_auth_url(resolved_provider: str) -> str:
    """Construit l'URL d'authentification Microsoft (Outlook)."""
    return generate_outlook_auth_url(state=resolved_provider)


def _process_gmail_callback(code: str, resolved_provider: str) -> None:
    """Traite le callback OAuth Gmail : échange le code contre des credentials."""
    credentials = exchange_gmail_code_for_credentials(code)
    save_connection_credentials(credentials, resolved_provider)


def _process_outlook_callback(code: str, resolved_provider: str) -> None:
    """Traite le callback OAuth Outlook : échange le code contre des tokens."""
    tokens = exchange_outlook_code_for_tokens(code)
    save_connection_credentials(tokens, resolved_provider)


def get_auth_url(provider: str | None = None) -> str:
    """Génère l'URL d'authentification OAuth2 pour le provider (défaut = config)."""
    try:
        resolved_provider = _resolve_provider(provider)
        handler = AuthUrlHandler.get_handler(resolved_provider)
        if not handler:
            raise ValueError(f"Provider non supporté: {resolved_provider}")
        return handler(resolved_provider)
    except ValueError as error:
        raise HTTPException(status_code=500, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la génération de l'URL d'authentification: {error!s}",
        ) from error


def process_callback(code: str, provider: str | None = None) -> RedirectResponse:
    """Échange le code OAuth contre des tokens, sauvegarde les credentials
    pour le provider, puis renvoie la redirection vers le frontend.
    """
    frontend_callback_base = auth_settings.FRONTEND_AUTH_CALLBACK_URL.rstrip("/")
    resolved_provider = _resolve_provider(provider)
    try:
        handler = CallbackHandler.get_handler(resolved_provider)
        if not handler:
            raise ValueError(f"Provider non supporté: {resolved_provider}")
        handler(code, resolved_provider)
        return RedirectResponse(url=f"{frontend_callback_base}?success=1", status_code=302)
    except Exception as error:
        return RedirectResponse(
            url=f"{frontend_callback_base}?error={quote(str(error))}",
            status_code=302,
        )


def _get_gmail_auth_status(credentials) -> AuthIdentity:
    """Retourne le statut d'authentification pour Gmail."""
    if credentials.expired and credentials.refresh_token:
        try:
            credentials.refresh(Request())
            save_connection_credentials(credentials, EmailProvider.GMAIL.value)
        except Exception:
            return AuthIdentity(is_authenticated=False)
    
    user_email = get_gmail_user_email(credentials)
    return AuthIdentity(is_authenticated=True, email=user_email)


def _get_outlook_auth_status(tokens) -> AuthIdentity:
    """Retourne le statut d'authentification pour Outlook."""
    user_email = get_outlook_user_email(tokens)
    return AuthIdentity(is_authenticated=True, email=user_email)


def _get_all_auth_status() -> AuthIdentity:
    """Retourne le statut d'authentification agrégé (au moins une boîte connectée)."""
    creds_gmail = get_connection_credentials(EmailProvider.GMAIL.value)
    creds_outlook = get_connection_credentials(EmailProvider.OUTLOOK.value)
    
    if not creds_gmail and not creds_outlook:
        return AuthIdentity(is_authenticated=False)
    
    # Essaye d'obtenir un email depuis Gmail d'abord, puis Outlook
    email = None
    if creds_gmail:
        status = _get_gmail_auth_status(creds_gmail)
        if status.is_authenticated:
            email = status.email
    
    if not email and creds_outlook:
        status = _get_outlook_auth_status(creds_outlook)
        if status.is_authenticated:
            email = status.email
    
    return AuthIdentity(is_authenticated=True, email=email or "Plusieurs boîtes")


def get_auth_status(provider: str | None = None) -> AuthIdentity:
    """Retourne l'identité auth pour le provider (connecté ou non, email si dispo)."""
    resolved_provider = _resolve_provider(provider)
    
    # Cas spécial : agrégation multi-providers
    if resolved_provider == EmailProvider.ALL.value:
        return _get_all_auth_status()
    
    # Récupération des credentials
    credentials = get_connection_credentials(resolved_provider)
    if not credentials:
        return AuthIdentity(is_authenticated=False)
    
    # Dispatch vers le handler approprié
    handler = AuthStatusHandler.get_handler(resolved_provider)
    if not handler:
        return AuthIdentity(is_authenticated=False)
    
    return handler(credentials)


def logout(provider: str | None = None) -> None:
    """Déconnecte l'utilisateur pour le provider (supprime les tokens)."""
    resolved_provider = _resolve_provider(provider)
    clear_connection_credentials(resolved_provider)
