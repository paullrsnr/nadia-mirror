# pylint: disable=invalid-name
"""Modèle métier pour le catalogue de modèles téléchargeables."""
from dataclasses import dataclass


@dataclass
class CatalogModel:
    """Entrée du catalogue : modèle téléchargeable depuis HuggingFace."""
    id: str
    name: str
    repo: str
    filename: str
    description: str = ""
    category: str = ""  # Catégorie : "Très léger", "Léger", "Moyen", "Haute qualité", "Très haute qualité"
