# pylint: disable=invalid-name
"""Utilitaires pour les chemins des modèles LLM."""
from pathlib import Path

from backend.config.Settings import llm_settings, storage_settings


def get_resources_dir() -> Path:
    """Dossier ressources où sont les modèles (.gguf)."""
    return llm_settings.get_llm_resources_dir(storage_settings.DATA_DIR)
