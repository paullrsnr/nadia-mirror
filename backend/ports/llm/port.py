# pylint: disable=invalid-name
"""Interface commune des ports LLM (réveil moteur + contrat).

Chaque modèle a son propre port (ports/llm/<model>/port.py) qui définit
réveil moteur / cerveau et interface. L'adapter correspondant récupère tout ça.
"""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

from backend.core.models.llm.installedModel import InstalledModel


class LLMProvider(ABC):
    """Interface commune : réveil moteur / cerveau + contrat (load_model, is_loaded, etc.)."""

    @abstractmethod
    def is_available(self) -> bool:
        """Vérifie si la librairie du moteur est disponible."""

    @abstractmethod
    def load_model(self, model_path: Path) -> bool:
        """Charge le modèle depuis le chemin donné. Returns True si succès."""

    @abstractmethod
    def unload_model(self) -> None:
        """Décharge le modèle de la mémoire."""

    @abstractmethod
    def is_loaded(self) -> bool:
        """Indique si un modèle est actuellement chargé."""

    @abstractmethod
    def get_loaded_model_path(self) -> Optional[Path]:
        """Retourne le chemin du modèle actuellement chargé, ou None."""

    def list_local_models(self, resources_dir: Path) -> list[InstalledModel]:
        """Liste les modèles présents localement. Implémentation par défaut (.gguf)."""
        models: list[InstalledModel] = []
        if not resources_dir.exists():
            return models
        for path in resources_dir.rglob("*.gguf"):
            if path.is_file():
                models.append(InstalledModel(
                    id=path.name,
                    name=path.stem,
                    path=str(path),
                ))
        return sorted(models, key=lambda m: m.name)
