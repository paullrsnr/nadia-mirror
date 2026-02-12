# pylint: disable=invalid-name
"""Espace utilisateur courant : un répertoire de données par personne sur la même machine.

Permet à une autre personne de se connecter sur le même PC avec son compte :
chaque espace a sa propre BDD (emails.db) et ses propres tokens (Gmail/Outlook).
L’espace actif est stocké dans DATA_DIR / "current_user_space".
"""
import logging
from pathlib import Path

from backend.config.settings import storage_settings

logger = logging.getLogger(__name__)

USER_SPACE_DEFAULT = "default"
_CURRENT_USER_SPACE_FILENAME = "current_user_space"


def get_current_user_space_id() -> str:
    """Retourne l’identifiant de l’espace utilisateur courant (ex: "default", "alice").
    Si aucun fichier n’existe, retourne "default" et le crée.
    """
    storage_settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
    path = storage_settings.DATA_DIR / _CURRENT_USER_SPACE_FILENAME
    if path.exists():
        try:
            raw = path.read_text(encoding="utf-8").strip()
            if raw and _is_safe_user_space_id(raw):
                return raw
        except OSError as e:
            logger.warning("Impossible de lire l’espace utilisateur courant: %s", e)
    _write_current_user_space_id(USER_SPACE_DEFAULT)
    return USER_SPACE_DEFAULT


def set_current_user_space_id(user_space_id: str) -> None:
    """Définit l’espace utilisateur courant (pour « changer d’utilisateur »)."""
    if not _is_safe_user_space_id(user_space_id):
        raise ValueError(f"Identifiant d’espace invalide: {user_space_id!r}")
    _write_current_user_space_id(user_space_id)


def _write_current_user_space_id(user_space_id: str) -> None:
    """Écrit le fichier current_user_space."""
    path = storage_settings.DATA_DIR / _CURRENT_USER_SPACE_FILENAME
    path.write_text(user_space_id, encoding="utf-8")
    try:
        path.chmod(0o600)
    except OSError:
        pass


def _is_safe_user_space_id(user_space_id: str) -> bool:
    """Accepte uniquement des identifiants sans caractères spéciaux (sécurité chemin)."""
    return bool(user_space_id) and user_space_id.isalnum() and len(user_space_id) <= 64


def get_current_user_space_dir() -> Path:
    """Répertoire des données de l’espace courant (emails.db, tokens_*.json, etc.)."""
    return storage_settings.user_space_dir(get_current_user_space_id())
