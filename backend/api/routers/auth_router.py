"""Routeur d'authentification : délègue au AuthService, ne fait que le routing."""

from fastapi import APIRouter, Query

from backend.api.schemas import AuthStatusResponse, AuthUrlResponse
from backend.core.services.authService import (
    get_auth_url,
    process_callback,
    get_auth_status,
    logout as auth_logout,
)

router = APIRouter()

_PROVIDER_QUERY_DESC = "Provider (gmail, etc.). Défaut = config."


@router.get("/url", response_model=AuthUrlResponse)
async def get_auth_url_route(
    provider: str | None = Query(default=None, description=_PROVIDER_QUERY_DESC),
):
    """Génère l'URL d'authentification OAuth2 pour le provider."""
    return AuthUrlResponse(auth_url=get_auth_url(provider))


@router.get("/callback")
async def auth_callback_route(
    code: str,
    state: str | None = Query(default=None, description="Provider renvoyé par OAuth (gmail, outlook)."),
    provider: str | None = Query(default=None, description=_PROVIDER_QUERY_DESC),
):
    """Échange le code OAuth, sauvegarde les tokens, redirige vers le frontend."""
    # state est renvoyé par Google/Microsoft après redirection ; il contient le provider
    resolved = (state or provider or "").strip().lower() or None
    return process_callback(code, resolved)


@router.get("/status", response_model=AuthStatusResponse)
async def get_auth_status_route(
    provider: str | None = Query(default=None, description=_PROVIDER_QUERY_DESC),
):
    """Vérifie le statut d'authentification pour le provider."""
    return get_auth_status(provider)


@router.post("/logout")
async def logout_route(
    provider: str | None = Query(default=None, description=_PROVIDER_QUERY_DESC),
):
    """Déconnecte l'utilisateur pour le provider (supprime les tokens)."""
    return auth_logout(provider)
