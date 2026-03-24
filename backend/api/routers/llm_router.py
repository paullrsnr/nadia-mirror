"""Routeur LLM : modèles (liste / téléchargement / chargement)."""
from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from backend.core.models.llm import (
    LLMStatusResponse,
    DownloadModelRequest,
    LoadModelRequest,
)
from backend.api.mappers import map_llm_status, map_catalog
from backend.core.services.llm import get_llm_service, stream_download_sse

router = APIRouter(prefix="/llm", tags=["llm"])


@router.get("/status", response_model=LLMStatusResponse)
def llm_status():
    return map_llm_status(get_llm_service().get_status())


@router.get("/models/catalog")
def models_catalog():
    return {"models": map_catalog(get_llm_service().get_catalog())}


@router.post("/models/download/stream")
async def models_download_stream(payload: DownloadModelRequest):
    return StreamingResponse(
        stream_download_sse(payload.repo, payload.filename),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.post("/models/load")
def models_load(payload: LoadModelRequest):
    return get_llm_service().load_model_by_id(payload.model_id)
