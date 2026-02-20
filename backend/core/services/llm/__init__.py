# pylint: disable=invalid-name
"""Services LLM : moteur, prompts, modèles."""
from backend.core.services.llm.llmService import get_llm_service, LLMService
from backend.core.services.llm.llmEngine import get_adapter, is_available, get_status, load_model, shutdown
from backend.core.services.llm.llmModelService import (
    get_first_available_model_id,
    list_installed_models,
)
from backend.core.services.llm.llmPaths import get_resources_dir
from backend.core.services.llm.llmCatalogService import list_catalog
from backend.core.services.llm.llmDownloadService import stream_download_sse
from backend.core.services.llm.llmSelectionService import get_selected_model_id, set_selected_model_id

__all__ = [
    "get_llm_service",
    "LLMService",
    "get_adapter",
    "is_available",
    "get_status",
    "load_model",
    "shutdown",
    "list_installed_models",
    "list_catalog",
    "stream_download_sse",
    "set_selected_model_id",
    "get_selected_model_id",
    "get_first_available_model_id",
    "get_resources_dir",
]
