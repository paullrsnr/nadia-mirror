import logging
from pathlib import Path
from typing import Optional

from backend.core.models.llm import LLMStatusResponse, InstalledModelResponse, CatalogModelResponse
from backend.core.services.llm.download import get_models_dir
from backend.core.services.llm.catalog import CATALOG, get_catalog_model
from backend.ports.llm import LlmPort

logger = logging.getLogger(__name__)

_llm_service: Optional["LlmService"] = None


class LlmService:
    """Service de gestion des modèles LLM."""

    def __init__(self, llm_adapter: LlmPort):
        self._adapter = llm_adapter
        self._selected_model_id: str | None = None

    def get_status(self) -> LLMStatusResponse:
        """Retourne le statut actuel du service LLM."""
        models_dir = get_models_dir()
        installed = self._list_installed_models(models_dir)

        loaded_path = self._adapter.get_loaded_model_path()
        resolved_path = str(loaded_path) if loaded_path else None

        return LLMStatusResponse(
            available=self._adapter.is_available(),
            message="LLM disponible" if self._adapter.is_available() else "LLM non disponible",
            resolved_model_path=resolved_path,
            resolved_model_exists=loaded_path.exists() if loaded_path else None,
            resources_path=str(models_dir),
            selected_model_id=self._selected_model_id,
            installed_models=installed,
        )

    def get_catalog(self) -> list[CatalogModelResponse]:
        """Retourne la liste des modèles disponibles au téléchargement."""
        return [
            CatalogModelResponse(
                id=m.id,
                name=m.name,
                repo=m.repo,
                filename=m.filename,
                description=m.description,
                category=m.category,
            )
            for m in CATALOG
        ]

    def _list_installed_models(self, models_dir: Path) -> list[InstalledModelResponse]:
        """Liste les modèles GGUF installés dans le répertoire."""
        installed = []
        if models_dir.exists():
            for f in models_dir.glob("*.gguf"):
                model_id = f.stem
                installed.append(InstalledModelResponse(
                    id=model_id,
                    name=f.name,
                    path=str(f),
                ))
        return installed

    def load_model_by_id(self, model_id: str) -> dict:
        """
        Charge un modèle par son ID.
        Retourne un dict avec le résultat.
        Lève ValueError si le modèle est introuvable.
        """
        models_dir = get_models_dir()

        catalog_model = get_catalog_model(model_id)
        if catalog_model:
            model_path = models_dir / catalog_model.filename
        else:
            model_path = models_dir / f"{model_id}.gguf"
            if not model_path.exists():
                model_path = models_dir / model_id

        if not model_path.exists():
            logger.error("Modèle introuvable: %s (cherché à %s)", model_id, model_path)
            raise ValueError(f"Modèle introuvable: {model_id}")

        success = self._load_model_from_path(model_path)
        if not success:
            raise ValueError("Impossible de charger le modèle")

        return {"model_id": model_id, "message": "Modèle chargé"}

    def _load_model_from_path(self, model_path: Path) -> bool:
        """Charge un modèle depuis le chemin spécifié."""
        success = self._adapter.load_model(model_path)
        if success:
            self._selected_model_id = model_path.stem
        return success

    def unload_model(self) -> None:
        """Décharge le modèle actuellement chargé."""
        self._adapter.unload_model()
        self._selected_model_id = None

def get_llm_service() -> LlmService:
    """Retourne l'instance singleton du service LLM."""
    global _llm_service
    if _llm_service is None:
        raise RuntimeError("LlmService non initialisé. Appelez init_llm_service() d'abord.")
    return _llm_service


def init_llm_service(adapter: LlmPort) -> LlmService:
    """Initialise le service LLM avec l'adapter fourni."""
    global _llm_service
    _llm_service = LlmService(adapter)
    return _llm_service
