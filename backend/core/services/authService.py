# pylint: disable=invalid-name
"""Service d'authentification OAuth par provider (Gmail, Outlook)."""
import time
from urllib.parse import quote, urlencode

import httpx
from fastapi import HTTPException
from fastapi.responses import RedirectResponse
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

from backend.config.settings import auth_settings, email_settings
from backend.core.models.auth import AuthIdentity
from backend.core.services.connectionOrchestrator import (
    get_connection_credentials,
    save_connection_credentials,
    clear_connection_credentials,
)


def _resolve_provider(provider: str | None) -> str:
    """Retourne le provider à utiliser (défaut = config)."""
    return (provider or email_settings.DEFAULT_PROVIDER).lower()


def _get_gmail_flow() -> Flow:
    """Crée le flux OAuth2 pour Gmail."""
    if not auth_settings.GMAIL_CLIENT_ID or not auth_settings.GMAIL_CLIENT_SECRET:
        raise ValueError(
            "GMAIL_CLIENT_ID et GMAIL_CLIENT_SECRET doivent être configurés"
        )

    redirect_uri = auth_settings.GMAIL_REDIRECT_URI.strip()
    client_config = {
        "web": {
            "client_id": auth_settings.GMAIL_CLIENT_ID,
            "client_secret": auth_settings.GMAIL_CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
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


def _get_flow(provider: str) -> Flow:
    """Crée le flux OAuth2 pour le provider (Gmail uniquement ; Outlook a son propre flux)."""
    resolved_provider = _resolve_provider(provider)
    if resolved_provider == "gmail":
        return _get_gmail_flow()
    raise ValueError(f"Provider non supporté pour _get_flow: {resolved_provider}")


def _build_outlook_auth_url(resolved_provider: str) -> str:
    """Construit l'URL d'authentification Microsoft (Outlook)."""
    if not auth_settings.OUTLOOK_CLIENT_ID:
        raise ValueError("OUTLOOK_CLIENT_ID doit être configuré")
    tenant = auth_settings.OUTLOOK_TENANT
    redirect_uri = auth_settings.OUTLOOK_REDIRECT_URI.strip()
    base = f"https://login.microsoftonline.com/{tenant}/oauth2/v2.0/authorize"
    scopes = " ".join(auth_settings.OUTLOOK_SCOPES)
    params = {
        "client_id": auth_settings.OUTLOOK_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": redirect_uri,
        "scope": scopes,
        "state": resolved_provider,
        "response_mode": "query",
    }
    return f"{base}?{urlencode(params)}"


def _exchange_outlook_code(code: str) -> dict:
    """Échange le code OAuth Outlook contre des tokens (Microsoft token endpoint)."""
    tenant = auth_settings.OUTLOOK_TENANT
    redirect_uri = auth_settings.OUTLOOK_REDIRECT_URI.strip()
    url = f"https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token"
    data = {
        "client_id": auth_settings.OUTLOOK_CLIENT_ID,
        "client_secret": auth_settings.OUTLOOK_CLIENT_SECRET,
        "code": code,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code",
    }
    with httpx.Client() as client:
        response = client.post(url, data=data)
        response.raise_for_status()
    body = response.json()
    expires_in = int(body.get("expires_in", 3600))
    return {
        "access_token": body["access_token"],
        "refresh_token": body.get("refresh_token", ""),
        "expires_at": time.time() + expires_in,
    }


def get_auth_url(provider: str | None = None) -> str:
    """Génère l'URL d'authentification OAuth2 pour le provider (défaut = config)."""
    try:
        resolved_provider = _resolve_provider(provider)
        if resolved_provider == "gmail":
            flow = _get_gmail_flow()
            auth_url, _ = flow.authorization_url(
                access_type="offline",
                include_granted_scopes="true",
                prompt="consent",
                state=resolved_provider,
            )
            return auth_url
        if resolved_provider == "outlook":
            return _build_outlook_auth_url(resolved_provider)
        raise ValueError(f"Provider non supporté: {resolved_provider}")
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
        if resolved_provider == "gmail":
            flow = _get_gmail_flow()
            flow.fetch_token(code=code)
            save_connection_credentials(flow.credentials, resolved_provider)
        elif resolved_provider == "outlook":
            tokens = _exchange_outlook_code(code)
            save_connection_credentials(tokens, resolved_provider)
        else:
            raise ValueError(f"Provider non supporté: {resolved_provider}")
        return RedirectResponse(url=f"{frontend_callback_base}?success=1", status_code=302)
    except Exception as error:
        return RedirectResponse(
            url=f"{frontend_callback_base}?error={quote(str(error))}",
            status_code=302,
        )


def _get_email_from_gmail(credentials) -> str | None:
    """Récupère l'email utilisateur via l'API Gmail."""
    try:
        service = build("gmail", "v1", credentials=credentials)
        profile = service.users().getProfile(userId="me").execute()
        return profile.get("emailAddress")
    except Exception:
        return None


def _get_email_from_outlook(tokens: dict) -> str | None:
    """Récupère l'email utilisateur via Microsoft Graph /me."""
    try:
        with httpx.Client() as client:
            response = client.get(
                "https://graph.microsoft.com/v1.0/me",
                headers={"Authorization": f"Bearer {tokens['access_token']}"},
            )
            response.raise_for_status()
        data = response.json()
        return data.get("mail") or data.get("userPrincipalName")
    except Exception:
        return None


def get_auth_status(provider: str | None = None) -> AuthIdentity:
    """Retourne l'identité auth pour le provider (connecté ou non, email si dispo)."""
    resolved_provider = (provider or "").strip().lower() or email_settings.DEFAULT_PROVIDER
    if resolved_provider == "all":
        # Au moins une boîte connectée
        creds_g = get_connection_credentials("gmail")
        creds_o = get_connection_credentials("outlook")
        if not creds_g and not creds_o:
            return AuthIdentity(is_authenticated=False)
        email = None
        if creds_g:
            try:
                if creds_g.expired and creds_g.refresh_token:
                    creds_g.refresh(Request())
                    save_connection_credentials(creds_g, "gmail")
                email = _get_email_from_gmail(creds_g)
            except Exception:
                pass
        if not email and creds_o:
            email = _get_email_from_outlook(creds_o)
        return AuthIdentity(is_authenticated=True, email=email or "Plusieurs boîtes")

    credentials = get_connection_credentials(resolved_provider)
    if not credentials:
        return AuthIdentity(is_authenticated=False)

    user_email = None
    if resolved_provider == "gmail":
        if credentials.expired and credentials.refresh_token:
            try:
                credentials.refresh(Request())
                save_connection_credentials(credentials, resolved_provider)
            except Exception:
                return AuthIdentity(is_authenticated=False)
        user_email = _get_email_from_gmail(credentials)
    elif resolved_provider == "outlook":
        user_email = _get_email_from_outlook(credentials)

    return AuthIdentity(is_authenticated=True, email=user_email)


def logout(provider: str | None = None) -> None:
    """Déconnecte l'utilisateur pour le provider (supprime les tokens)."""
    resolved_provider = _resolve_provider(provider)
    clear_connection_credentials(resolved_provider)
