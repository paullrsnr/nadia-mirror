"""Point d'entrée principal de l'API FastAPI."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routers import auth_router, emails_router, llm_router

app = FastAPI(title="Nadia API")

# Inclure les routers
app.include_router(auth_router.router, prefix="/auth", tags=["auth"])
app.include_router(emails_router.router, tags=["emails"])
app.include_router(llm_router.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    """Endpoint de vérification de santé de l'API."""
    return {"status": "ok"}
