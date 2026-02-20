"""Routeur LLM : modèles (liste / téléchargement / chargement)."""
from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from backend.api.schemas import (
    LLMStatusResponse,
    InstalledModelResponse,
    CatalogModelResponse,
    DownloadModelRequest,
    LoadModelRequest,
)
from backend.api.utils import handle_service_errors
from backend.core.services.llm import (
    get_llm_service,
    list_catalog,
    stream_download_sse,
    load_model,
)

router = APIRouter(prefix="/llm", tags=["llm"])


@router.get("/status", response_model=LLMStatusResponse)
def llm_status():
    """Indique si le modèle LLM est disponible et liste les modèles installés."""
    status = get_llm_service().get_status()
    return LLMStatusResponse(
        available=status.available,
        message=status.message,
        resolved_model_path=status.resolved_model_path,
        resolved_model_exists=status.resolved_model_exists,
        resources_path=status.resources_path,
        selected_model_id=status.selected_model_id,
        installed_models=[
            InstalledModelResponse(id=m.id, name=m.name, path=m.path)
            for m in status.installed_models
        ],
    )


@router.get("/models/catalog")
def models_catalog():
    """Liste les modèles proposés au téléchargement (catalogue)."""
    catalog = list_catalog()
    return {
        "models": [
            CatalogModelResponse(
                id=m.id,
                name=m.name,
                repo=m.repo,
                filename=m.filename,
                description=m.description,
                category=m.category,
            )
            for m in catalog
        ]
    }


@router.post("/models/download/stream")
async def models_download_stream(payload: DownloadModelRequest):
    """Télécharge un modèle et envoie la progression en SSE."""
    return StreamingResponse(
        stream_download_sse(payload.repo, payload.filename),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.post("/models/load")
def models_load(payload: LoadModelRequest):
    """Sélectionne et charge un modèle."""
    def _load():
        ok = load_model(payload.model_id)
        if not ok:
            raise ValueError("Modèle introuvable ou chargement impossible")
        return {"model_id": payload.model_id, "message": "Modèle chargé"}
    return handle_service_errors(_load)
