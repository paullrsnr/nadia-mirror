# pylint: disable=invalid-name
"""Service de gestion des modèles LLM : liste, sélection automatique, chargement."""
import logging
from pathlib import Path
from typing import Optional

from backend.config.llmRegistry import LLMAdapterRegistry
from backend.core.models.llm.installedModel import InstalledModel
from backend.core.services.llm.llmPaths import get_resources_dir
from backend.core.services.llm.llmSelectionService import (
    get_selected_model_id,
    resolve_model_path,
    set_selected_model_id,
)

logger = logging.getLogger(__name__)


def list_installed_models() -> list[InstalledModel]:
    """Liste les modèles présents dans resources/."""
    engine = LLMAdapterRegistry.get_default_engine()
    adapter_class = LLMAdapterRegistry.get_adapter_class(engine)
    if not adapter_class:
        return []
    adapter = adapter_class(get_resources_dir())
    return adapter.list_local_models(get_resources_dir())


def get_first_available_model_id() -> Optional[str]:
    """Retourne l'id (nom de fichier) du premier modèle disponible dans resources/."""
    models = list_installed_models()
    if not models:
        return None
    def score(m: InstalledModel) -> int:
        name = (m.name or m.id or "").lower()
        s = 0
        if "llama" in name:
            s += 2
        if "8b" in name:
            s += 1
        if "q4" in name:
            s += 1
        return s
    best = max(models, key=score)
    return best.id or best.name


def validate_and_select_model(model_id: str) -> bool:
    """Vérifie que le modèle existe et persiste la sélection (sans charger dans l'adapter)."""
    path = resolve_model_path(model_id)
    if not path:
        logger.error("Modèle introuvable: %s", model_id)
        return False
    set_selected_model_id(model_id)
    return True
