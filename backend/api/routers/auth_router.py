"""Routeur d'authentification : délègue au AuthService, ne fait que le routing."""

from fastapi import APIRouter, Path, Query

from backend.api.schemas import AuthStatusResponse, AuthUrlResponse
from backend.config.providers import EmailProvider
from backend.core.services.authService import (
    get_auth_url,
    process_callback,
    get_auth_status,
    logout as auth_logout,
)

router = APIRouter()

_PROVIDER_PATH_DESC = f"Provider ({EmailProvider.GMAIL.value}, {EmailProvider.OUTLOOK.value})."


@router.get("/url/{provider}", response_model=AuthUrlResponse)
async def get_auth_url_route(
    provider: str = Path(..., description=_PROVIDER_PATH_DESC),
):
    """Génère l'URL d'authentification OAuth2 pour le provider."""
    return AuthUrlResponse(auth_url=get_auth_url(provider))


@router.get("/callback/gmail")
async def auth_callback_gmail_route(
    code: str = Query(..., description="Code OAuth renvoyé par Google."),
    state: str | None = Query(default=None, description="State renvoyé par Google (ignoré, provider = gmail)."),
):
    """Callback OAuth Gmail : échange le code, sauvegarde les tokens, redirige vers le frontend."""
    return process_callback(code, EmailProvider.GMAIL.value)


@router.get("/callback/outlook")
async def auth_callback_outlook_route(
    code: str = Query(..., description="Code OAuth renvoyé par Microsoft."),
    state: str | None = Query(default=None, description="State renvoyé par Microsoft (ignoré, provider = outlook)."),
):
    """Callback OAuth Outlook : échange le code, sauvegarde les tokens, redirige vers le frontend."""
    return process_callback(code, EmailProvider.OUTLOOK.value)


@router.get("/status/{provider}", response_model=AuthStatusResponse)
async def get_auth_status_route(
    provider: str = Path(..., description=_PROVIDER_PATH_DESC),
):
    """Vérifie le statut d'authentification pour le provider."""
    return get_auth_status(provider)


@router.post("/logout/{provider}")
async def logout_route(
    provider: str = Path(..., description=_PROVIDER_PATH_DESC),
):
    """Déconnecte l'utilisateur pour le provider (supprime les tokens)."""
    return auth_logout(provider)
