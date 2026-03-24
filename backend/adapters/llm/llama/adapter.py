import logging
import os
from pathlib import Path
from typing import Optional

try:
    from llama_cpp import Llama
except ImportError:
    Llama = None  # type: ignore

from backend.ports.llm.llama import LlamaPort
from backend.config.settings import llm_settings

logger = logging.getLogger(__name__)


class LlamaCppAdapter(LlamaPort):

    def __init__(self, resources_dir: Path | None = None):
        self._resources_dir = resources_dir or Path(llm_settings.MODELS_DIR)
        self._model: Optional[Llama] = None
        self._model_path: Optional[Path] = None

    def is_available(self) -> bool:
        return Llama is not None

    def load_model(self, model_path: Path) -> bool:
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
        if self._model is not None:
            del self._model
            self._model = None
            self._model_path = None
            logger.info("Modèle déchargé")

    def is_loaded(self) -> bool:
        return self._model is not None

    def get_loaded_model_path(self) -> Optional[Path]:
        return self._model_path
