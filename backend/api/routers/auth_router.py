from fastapi import APIRouter, Depends, Path, Query
from fastapi.responses import RedirectResponse

from backend.api.deps import get_auth_service
from backend.api.schemas import AuthStatusResponse, AuthUrlResponse
from backend.config.settings import auth_settings
from backend.core.models.email import Provider
from backend.core.services.authService import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])

_PROVIDER_DESC = f"Provider ({Provider.GMAIL.value}, {Provider.OUTLOOK.value})."


@router.get("/url/{provider}", response_model=AuthUrlResponse)
def get_auth_url_route(
    provider: str = Path(..., description=_PROVIDER_DESC),
    service: AuthService = Depends(get_auth_service),
):
    return AuthUrlResponse(auth_url=service.get_auth_url(provider))


@router.get("/callback/{provider}")
def auth_callback_route(
    provider: str = Path(..., description=_PROVIDER_DESC),
    code: str = Query(..., description="Code OAuth renvoyé par le provider."),
    state: str = Query(..., description="State OAuth renvoyé par le provider."),
    service: AuthService = Depends(get_auth_service),
):
    redirect_url = service.process_callback(code, provider, state=state)
    return RedirectResponse(url=redirect_url, status_code=302)


@router.get("/status/{provider}", response_model=AuthStatusResponse)
def get_auth_status_route(
    provider: str = Path(..., description=_PROVIDER_DESC),
    service: AuthService = Depends(get_auth_service),
):
    return service.get_auth_status(provider)


@router.post("/logout/{provider}")
def logout_route(
    provider: str = Path(..., description=_PROVIDER_DESC),
    service: AuthService = Depends(get_auth_service),
):
    return service.logout(provider)
