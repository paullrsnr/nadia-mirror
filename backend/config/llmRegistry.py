# pylint: disable=invalid-name
"""Registre : autant de ports et d'adapters que de modèles.

Port = réveil moteur / cerveau et interface. Adapter = récupère tout ça (comme Outlook).
"""
from typing import Type

from backend.ports.llm import LLMProvider
from backend.adapters.llm.llama import LlamaCppAdapter


class LLMAdapterRegistry:
    """Registre modèle (moteur) -> classe d'adapter. Un port + un adapter par modèle."""

    _adapters: dict[str, Type[LLMProvider]] = {
        "llama-cpp": LlamaCppAdapter,
    }

    @classmethod
    def get_adapter_class(cls, engine: str) -> Type[LLMProvider] | None:
        """Retourne la classe d'adapter pour un moteur donné."""
        return cls._adapters.get(engine)

    @classmethod
    def get_default_engine(cls) -> str:
        """Moteur par défaut (llama-cpp)."""
        return "llama-cpp"

    @classmethod
    def list_engines(cls) -> list[str]:
        """Liste les moteurs enregistrés."""
        return list(cls._adapters.keys())
