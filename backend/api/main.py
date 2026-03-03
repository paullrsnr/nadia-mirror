"""Point d'entrée principal de l'API FastAPI."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routers import auth_router, emails_router
from backend.config.settings import api_settings

app = FastAPI(title="Nadia API")

app.include_router(auth_router.router, prefix="/auth", tags=["auth"])
app.include_router(emails_router.router, tags=["emails"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=[api_settings.FRONTEND_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    """Endpoint de vérification de santé de l'API."""
    return {"status": "ok"}
