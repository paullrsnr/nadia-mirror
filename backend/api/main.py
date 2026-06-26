import asyncio

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.api.routers import auth_router, emails_router, llm_router
from backend.api.routers import auto_archive_router, drafts_router
from backend.api.deps import get_llm_service
from backend.config.settings import api_settings
from backend.core.exceptions import AuthError, NotFoundError, ProviderError, ValidationError

app = FastAPI(title="Nadia API")


@app.on_event("startup")
async def auto_load_llm_model():
    asyncio.create_task(asyncio.to_thread(get_llm_service().auto_load_last_model))


@app.exception_handler(ProviderError)
def provider_error_handler(_, exc: ProviderError):
    return JSONResponse(status_code=400, content={"detail": str(exc)})


@app.exception_handler(AuthError)
def auth_error_handler(_, exc: AuthError):
    return JSONResponse(status_code=401, content={"detail": str(exc)})


@app.exception_handler(NotFoundError)
def not_found_error_handler(_, exc: NotFoundError):
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(ValidationError)
def validation_error_handler(_, exc: ValidationError):
    return JSONResponse(status_code=400, content={"detail": str(exc)})

app.include_router(auth_router.router)
app.include_router(emails_router.router, tags=["emails"])
app.include_router(llm_router.router)
app.include_router(auto_archive_router.router)
app.include_router(drafts_router.router, tags=["drafts"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=[api_settings.FRONTEND_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}
