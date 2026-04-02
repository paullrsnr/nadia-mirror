from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.api.routers import auth_router, emails_router, llm_router
from backend.api.routers import auto_archive_router
from backend.config.settings import api_settings
from backend.core.exceptions import AuthError, ProviderError

app = FastAPI(title="Nadia API")


@app.exception_handler(ProviderError)
def provider_error_handler(_, exc: ProviderError):
    return JSONResponse(status_code=400, content={"detail": str(exc)})


@app.exception_handler(AuthError)
def auth_error_handler(_, exc: AuthError):
    return JSONResponse(status_code=401, content={"detail": str(exc)})

app.include_router(auth_router.router)
app.include_router(emails_router.router, tags=["emails"])
app.include_router(llm_router.router)
app.include_router(auto_archive_router.router)

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
