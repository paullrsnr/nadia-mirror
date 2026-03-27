from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional


class LlmPort(ABC):
    """Interface abstraite pour les clients LLM."""

    @abstractmethod
    def is_available(self) -> bool:
        """Vérifie si le backend LLM est disponible."""
        ...

    @abstractmethod
    def load_model(self, model_path: Path) -> bool:
        """Charge un modèle depuis le chemin spécifié."""
        ...

    @abstractmethod
    def unload_model(self) -> None:
        """Décharge le modèle actuellement chargé."""
        ...

    @abstractmethod
    def is_loaded(self) -> bool:
        """Vérifie si un modèle est actuellement chargé."""
        ...

    @abstractmethod
    def get_loaded_model_path(self) -> Optional[Path]:
        """Retourne le chemin du modèle chargé, ou None."""
        ...

    @abstractmethod
    def chat(self, messages: list[dict]) -> str:
        """Envoie des messages au modèle et retourne la réponse."""
        ...
