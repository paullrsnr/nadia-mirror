from fastapi import APIRouter, Depends, Path, Query
from fastapi.responses import RedirectResponse

from backend.api.deps import get_auth_service
from backend.api.schemas import AuthStatusResponse, AuthUrlResponse
from backend.config.settings import auth_settings
from backend.core.models.email import Provider
from backend.core.services.authService import AuthService

router = APIRouter()

_PROVIDER_DESC = f"Provider ({Provider.GMAIL.value}, {Provider.OUTLOOK.value})."


@router.get("/url/{provider}", response_model=AuthUrlResponse)
async def get_auth_url_route(
    provider: str = Path(..., description=_PROVIDER_DESC),
    service: AuthService = Depends(get_auth_service),
):
    return AuthUrlResponse(auth_url=service.get_auth_url(provider))


@router.get("/callback/gmail")
async def auth_callback_gmail_route(
    code: str = Query(..., description="Code OAuth renvoyé par Google."),
    state: str | None = Query(default=None),
    service: AuthService = Depends(get_auth_service),
):
    service.process_callback(code, Provider.GMAIL.value)
    base = auth_settings.FRONTEND_AUTH_CALLBACK_URL.rstrip("/")
    return RedirectResponse(url=f"{base}?success=1", status_code=302)


@router.get("/callback/outlook")
async def auth_callback_outlook_route(
    code: str = Query(..., description="Code OAuth renvoyé par Microsoft."),
    state: str | None = Query(default=None),
    service: AuthService = Depends(get_auth_service),
):
    service.process_callback(code, Provider.OUTLOOK.value)
    base = auth_settings.FRONTEND_AUTH_CALLBACK_URL.rstrip("/")
    return RedirectResponse(url=f"{base}?success=1", status_code=302)


@router.get("/status/{provider}", response_model=AuthStatusResponse)
async def get_auth_status_route(
    provider: str = Path(..., description=_PROVIDER_DESC),
    service: AuthService = Depends(get_auth_service),
):
    return service.get_auth_status(provider)


@router.post("/logout/{provider}")
async def logout_route(
    provider: str = Path(..., description=_PROVIDER_DESC),
    service: AuthService = Depends(get_auth_service),
):
    return service.logout(provider)
