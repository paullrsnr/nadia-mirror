# pylint: disable=invalid-name
"""Adapter pour le modèle Llama : récupère le port (réveil moteur + interface).

Comme pour Outlook : le port définit réveil moteur / cerveau et interface,
l'adapter récupère tout ça et branche llama-cpp-python.
"""
import logging
import os
from pathlib import Path
from typing import Optional

try:
    from llama_cpp import Llama
except ImportError:
    Llama = None  # type: ignore

from backend.ports.llm.llama import LlamaPort
from backend.config.Settings import llm_settings

logger = logging.getLogger(__name__)


class LlamaCppAdapter(LlamaPort):
    """Adapter Llama : récupère le port (réveil + interface) et branche llama-cpp-python."""

    def __init__(self, resources_dir: Path):
        """
        Args:
            resources_dir: Dossier où sont stockés les modèles (.gguf), ex. backend/ressources
        """
        self._resources_dir = resources_dir
        self._model: Optional[Llama] = None
        self._model_path: Optional[Path] = None

    def is_available(self) -> bool:
        """Vérifie si llama-cpp-python est disponible."""
        return Llama is not None

    def load_model(self, model_path: Path) -> bool:
        """Charge le modèle GGUF depuis le chemin donné."""
        if not self.is_available():
            logger.error("llama-cpp-python n'est pas installé")
            return False

        if self._model is not None:
            if self._model_path == model_path:
                logger.info("Modèle déjà chargé")
                return True
            self.unload_model()

        if not model_path.exists():
            logger.error("Modèle introuvable à %s", model_path)
            return False

        try:
            logger.info("Chargement du modèle depuis %s...", model_path)
            n_threads = llm_settings.DEFAULT_N_THREADS
            if llm_settings.AUTO_THREADS:
                try:
                    n_threads = os.cpu_count() or 4
                except Exception:
                    pass

            self._model = Llama(
                model_path=str(model_path),
                n_ctx=llm_settings.DEFAULT_N_CTX,
                n_threads=n_threads,
                verbose=False,
            )
            self._model_path = model_path
            logger.info("Modèle chargé avec succès")
            return True
        except Exception as e:
            logger.error("Erreur lors du chargement du modèle: %s", e, exc_info=True)
            self._model = None
            self._model_path = None
            return False

    def unload_model(self) -> None:
        """Décharge le modèle de la mémoire."""
        if self._model is not None:
            del self._model
            self._model = None
            self._model_path = None
            logger.info("Modèle déchargé")

    def is_loaded(self) -> bool:
        """Vérifie si un modèle est chargé."""
        return self._model is not None

    def get_loaded_model_path(self) -> Optional[Path]:
        """Retourne le chemin du modèle chargé."""
        return self._model_path
