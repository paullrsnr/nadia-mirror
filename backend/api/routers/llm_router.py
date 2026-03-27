from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from backend.core.models.llm import (
    LLMStatusResponse,
    CatalogModelResponse,
    DownloadModelRequest,
    LoadModelRequest,
)
from backend.core.services.llm import stream_download_sse
from backend.core.services.llm.service import LlmService
from backend.api.deps import get_llm_service

router = APIRouter(prefix="/llm", tags=["llm"])


@router.get("/status", response_model=LLMStatusResponse)
def llm_status(service: LlmService = Depends(get_llm_service)):
    return service.get_status()


@router.get("/models/catalog", response_model=list[CatalogModelResponse])
def models_catalog(service: LlmService = Depends(get_llm_service)):
    return service.get_catalog()


@router.post("/models/download/stream")
async def models_download_stream(payload: DownloadModelRequest):
    return StreamingResponse(
        stream_download_sse(payload.repo, payload.filename),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.post("/models/load")
def models_load(payload: LoadModelRequest, service: LlmService = Depends(get_llm_service)):
    return service.load_model_by_id(payload.model_id)
