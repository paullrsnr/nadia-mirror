from backend.core.models.llm import CatalogModelResponse, LLMStatusResponse


def map_llm_status(status: LLMStatusResponse) -> LLMStatusResponse:
    """Mappe le statut LLM pour la couche API."""
    return status


def map_catalog(models: list[CatalogModelResponse]) -> list[CatalogModelResponse]:
    """Mappe le catalogue LLM pour la couche API."""
    return models
