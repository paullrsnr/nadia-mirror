from backend.core.services.llm.service import get_llm_service


def load_model(model_id: str) -> dict:
    return get_llm_service().load_model_by_id(model_id)
