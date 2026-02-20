# pylint: disable=invalid-name
"""Moteur LLM : gestion de l'adapter (singleton) et génération brute."""
import logging
from typing import Optional

from backend.config.llmRegistry import LLMAdapterRegistry
from backend.core.models.llm.llmStatus import LLMStatus
from backend.ports.llm import LLMProvider
from backend.core.services.llm.llmModelService import get_first_available_model_id, list_installed_models
from backend.core.services.llm.llmPaths import get_resources_dir
from backend.core.services.llm.llmSelectionService import get_selected_model_id, resolve_model_path, set_selected_model_id

logger = logging.getLogger(__name__)

_current_adapter: Optional[LLMProvider] = None


def _try_load_selected_model(adapter: LLMProvider) -> bool:
    """Tente de charger le modèle sélectionné. Retourne True si chargé avec succès."""
    selected = get_selected_model_id()
    if not selected:
        return False
    
    path = resolve_model_path(selected)
    if not path or not path.exists():
        logger.warning("Modèle sélectionné %s introuvable, désélection", selected)
        set_selected_model_id(None)
        return False
    
    if adapter.load_model(path):
        return True
    
    # Le modèle existe mais n'a pas pu être chargé
    logger.warning("Modèle sélectionné %s existe mais n'a pas pu être chargé, désélection", selected)
    set_selected_model_id(None)
    return False


def _try_load_first_available_model(adapter: LLMProvider) -> bool:
    """Tente de charger le premier modèle disponible. Retourne True si chargé avec succès."""
    selected = get_first_available_model_id()
    if not selected:
        return False
    
    set_selected_model_id(selected)
    path = resolve_model_path(selected)
    if path and path.exists() and adapter.load_model(path):
        return True
    return False


def get_adapter() -> Optional[LLMProvider]:
    """Retourne l'adapter courant (créé et chargé si un modèle est sélectionné ou trouvé)."""
    global _current_adapter
    if _current_adapter is not None:
        return _current_adapter
    
    engine = LLMAdapterRegistry.get_default_engine()
    adapter_class = LLMAdapterRegistry.get_adapter_class(engine)
    if not adapter_class:
        return None
    
    resources_dir = get_resources_dir()
    adapter = adapter_class(resources_dir)
    if not adapter.is_available():
        return None
    
    # Essayer de charger le modèle sélectionné, sinon le premier disponible
    if _try_load_selected_model(adapter) or _try_load_first_available_model(adapter):
        _current_adapter = adapter
        return adapter
    
    _current_adapter = adapter
    return adapter


def ensure_loaded() -> LLMProvider:
    """Retourne l'adapter avec un modèle chargé, ou lève RuntimeError."""
    adapter = get_adapter()
    if not adapter:
        raise RuntimeError("Moteur LLM non disponible (llama-cpp-python absent ou modèle non sélectionné).")
    if not adapter.is_loaded():
        raise RuntimeError("Aucun modèle chargé. Choisissez un modèle dans ressources/ et chargez-le.")
    return adapter


def initialize() -> bool:
    """Initialise le service : charge le modèle sélectionné si présent."""
    adapter = get_adapter()
    if not adapter or adapter.is_loaded():
        return adapter is not None and adapter.is_loaded()
    selected = get_selected_model_id()
    if not selected:
        return False
    return load_model(selected)


def is_available() -> bool:
    """Indique si le moteur est disponible et qu'un modèle est chargé."""
    adapter = get_adapter()
    return adapter is not None and adapter.is_loaded()


def load_model(model_id: str) -> bool:
    """Charge le modèle dont l'id est donné et le persiste comme sélectionné."""
    global _current_adapter
    path = resolve_model_path(model_id)
    if not path:
        logger.error("Modèle introuvable: %s", model_id)
        return False
    engine = LLMAdapterRegistry.get_default_engine()
    adapter_class = LLMAdapterRegistry.get_adapter_class(engine)
    if not adapter_class:
        return False
    adapter = adapter_class(get_resources_dir())
    if not adapter.load_model(path):
        return False
    set_selected_model_id(model_id)
    _current_adapter = adapter
    return True


def shutdown() -> None:
    """Décharge le modèle et réinitialise l'adapter."""
    global _current_adapter
    if _current_adapter is not None:
        _current_adapter.unload_model()
        _current_adapter = None
    logger.info("Service LLM arrêté")


def get_status() -> LLMStatus:
    """Statut détaillé du service LLM."""
    resources_dir = get_resources_dir()
    selected_id = get_selected_model_id()
    adapter = get_adapter()
    installed_models = list_installed_models()

    if adapter is None:
        return LLMStatus(
            available=False,
            message="Moteur LLM non disponible (llama-cpp-python absent).",
            resources_path=str(resources_dir),
            resolved_model_path=None,
            resolved_model_exists=None,
            selected_model_id=selected_id,
            installed_models=installed_models,
        )

    resolved = resolve_model_path(selected_id) if selected_id else None
    is_loaded = adapter.is_loaded()
    
    # Message plus informatif
    if is_loaded:
        message = "Modèle prêt"
    elif installed_models:
        if selected_id:
            if resolved and resolved.exists():
                message = "Modèle sélectionné mais non chargé. Rechargez la page ou sélectionnez-le à nouveau."
            else:
                message = f"Modèle sélectionné '{selected_id}' introuvable. Choisissez-en un autre."
        else:
            message = f"{len(installed_models)} modèle(s) disponible(s). Sélectionnez-en un pour l'utiliser."
    else:
        message = "Aucun modèle installé. Téléchargez-en un depuis le catalogue."
    
    return LLMStatus(
        available=is_loaded,
        message=message,
        resources_path=str(resources_dir),
        resolved_model_path=str(resolved) if resolved else None,
        resolved_model_exists=resolved.exists() if resolved else False,
        selected_model_id=selected_id,
        installed_models=installed_models,
    )
