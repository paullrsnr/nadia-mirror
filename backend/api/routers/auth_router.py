"""Routeur d'authentification : délègue au AuthService, ne fait que le routing."""
from urllib.parse import quote

from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse

from backend.config.settings import auth_settings
from backend.api.schemas import AuthStatusResponse, AuthUrlResponse
from backend.core.services.authService import (
    get_auth_url,
    process_callback,
    get_auth_status,
    logout as auth_logout,
)

router = APIRouter()


@router.get("/url", response_model=AuthUrlResponse)
async def get_auth_url_route():
    """Génère l'URL d'authentification OAuth2."""
    try:
        auth_url = get_auth_url()
        return AuthUrlResponse(auth_url=auth_url)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la génération de l'URL d'authentification: {str(e)}",
        ) from e


@router.get("/callback")
async def auth_callback_route(code: str):
    """Échange le code OAuth, sauvegarde les tokens, redirige vers le frontend."""
    base = auth_settings.FRONTEND_AUTH_CALLBACK_URL.rstrip("/")
    try:
        process_callback(code)
        return RedirectResponse(url=f"{base}?success=1", status_code=302)
    except Exception as e:
        return RedirectResponse(
            url=f"{base}?error={quote(str(e))}",
            status_code=302,
        )


@router.get("/status", response_model=AuthStatusResponse)
async def get_auth_status_route():
    """Vérifie le statut d'authentification."""
    return get_auth_status()


@router.post("/logout")
async def logout_route():
    """Déconnecte l'utilisateur en supprimant les tokens."""
    auth_logout()
    return {"status": "success", "message": "Déconnexion réussie"}
