from backend.core.models.llm import CatalogModelResponse, LLMStatusResponse


def map_llm_status(status: LLMStatusResponse) -> LLMStatusResponse:
    return status


def map_catalog(models: list[CatalogModelResponse]) -> list[CatalogModelResponse]:
    return models
