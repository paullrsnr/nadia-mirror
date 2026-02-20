# pylint: disable=invalid-name
"""Service de sélection et persistance des modèles LLM."""
import logging
from pathlib import Path
from typing import Optional

from backend.config.Settings import storage_settings
from backend.core.services.llm.llmPaths import get_resources_dir

logger = logging.getLogger(__name__)

_GGUF_EXTENSION = ".gguf"
_SELECTED_MODEL_FILE = "llm_selected_model.txt"


def _selected_model_path() -> Path:
    """Fichier où est persisté l'id du modèle sélectionné."""
    d = storage_settings.DATA_DIR
    d.mkdir(parents=True, exist_ok=True)
    return d / _SELECTED_MODEL_FILE


def get_selected_model_id() -> Optional[str]:
    """Retourne l'id du modèle actuellement sélectionné (persisté)."""
    p = _selected_model_path()
    if not p.exists():
        return None
    try:
        return p.read_text(encoding="utf-8").strip() or None
    except Exception:
        return None


def set_selected_model_id(model_id: Optional[str]) -> None:
    """Persiste l'id du modèle sélectionné."""
    p = _selected_model_path()
    if model_id:
        p.write_text(model_id, encoding="utf-8")
    elif p.exists():
        p.unlink()


def resolve_model_path(model_id: str) -> Optional[Path]:
    """Résout model_id (nom de fichier ou id) vers un chemin dans resources/."""
    resources = get_resources_dir()
    if not resources.exists():
        return None
    
    # Normaliser l'ID pour la comparaison (minuscules, sans extension)
    model_id_normalized = model_id.lower().replace(".gguf", "").replace("-", "").replace("_", "").replace(".", "")
    
    # 1. Recherche exacte par nom de fichier
    by_name = resources / model_id
    if by_name.exists() and by_name.is_file():
        return by_name
    
    # 2. Ajouter l'extension si absente
    if not model_id.endswith(_GGUF_EXTENSION):
        by_name = resources / f"{model_id}{_GGUF_EXTENSION}"
        if by_name.exists() and by_name.is_file():
            return by_name
    
    # 3. Recherche récursive avec correspondance exacte du nom
    for path in resources.rglob(f"*{_GGUF_EXTENSION}"):
        if path.is_file():
            # Correspondance exacte du nom (avec ou sans extension)
            if model_id == path.name or model_id == path.stem:
                return path
            # Correspondance normalisée (ignore casse, tirets, underscores, points)
            path_normalized = path.stem.lower().replace("-", "").replace("_", "").replace(".", "")
            if model_id_normalized == path_normalized:
                return path
    
    # 4. Recherche par sous-chaîne (fallback)
    for path in resources.rglob(f"*{_GGUF_EXTENSION}"):
        if path.is_file() and model_id.lower() in path.name.lower():
            return path
    
    return None
