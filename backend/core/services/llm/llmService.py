# pylint: disable=invalid-name
"""Façade du service LLM : délègue au moteur et au modèle."""
from typing import Optional

from backend.core.models.llm.llmStatus import LLMStatus
from backend.ports.llm import LLMProvider
from backend.core.services.llm.llmEngine import (
    get_adapter,
    initialize,
    is_available,
    get_status,
    load_model,
    shutdown,
)


class LLMService:
    """Façade du service LLM (singleton)."""

    @property
    def _adapter(self) -> Optional[LLMProvider]:
        return get_adapter()

    def initialize(self) -> bool:
        return initialize()

    def is_available(self) -> bool:
        return is_available()

    def get_status(self) -> LLMStatus:
        return get_status()

    def shutdown(self) -> None:
        shutdown()


def get_llm_service() -> LLMService:
    """Retourne la façade du service LLM (singleton)."""
    return _LLM_SERVICE_INSTANCE


_LLM_SERVICE_INSTANCE = LLMService()
