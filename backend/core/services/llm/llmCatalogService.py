# pylint: disable=invalid-name
"""Service de gestion du catalogue de modèles LLM depuis HuggingFace."""
import logging
from typing import TYPE_CHECKING

from backend.core.models.llm.catalogModel import CatalogModel

if TYPE_CHECKING:
    from huggingface_hub import HfApi

logger = logging.getLogger(__name__)

# Liste des repos HuggingFace à scanner pour trouver les modèles disponibles
_REPOS_TO_SCAN = [
    "QuantFactory/Meta-Llama-3-8B-GGUF",
    # Ajouter d'autres repos ici au fur et à mesure
]

_GGUF_EXTENSION = ".gguf"


def _extract_quantization(filename: str) -> str:
    """Extrait le type de quantization depuis le nom de fichier."""
    quantizations = ["Q8_0", "Q6_K", "Q5_K_M", "Q5_K_S", "Q4_K_M", "Q4_K_S", "Q3_K_M", "Q3_K_S", "Q2_K"]
    for q in quantizations:
        if q in filename:
            return q
    return ""


def _generate_model_name(base_name: str, quantization: str) -> str:
    """Génère un nom lisible pour le modèle."""
    if quantization:
        # Retirer la quantization du nom de base pour éviter la duplication
        name_base = base_name.replace(f".{quantization}", "").replace(f"-{quantization}", "")
        return f"{name_base} ({quantization})"
    return base_name


def _generate_category(quantization: str) -> str:
    """Génère la catégorie selon le type de quantization."""
    if quantization.startswith("Q2") or quantization.startswith("Q3"):
        return "Très léger"
    if quantization == "Q4_K_S":
        return "Léger"
    if quantization == "Q4_K_M":
        return "Moyen"
    if quantization.startswith("Q5"):
        return "Haute qualité"
    if quantization.startswith("Q6") or quantization.startswith("Q8"):
        return "Très haute qualité"
    return "Autre"


def _generate_description(quantization: str) -> str:
    """Génère une description selon le type de quantization."""
    descriptions = {
        "Q4_K_M": "Bon compromis taille/performance, ~5 Go",
        "Q3_K_M": "Plus léger, ~3.8 Go",
        "Q4_K_S": "Léger, ~4.4 Go",
    }
    if quantization in descriptions:
        return descriptions[quantization]
    if quantization.startswith("Q5"):
        return "Meilleure qualité, ~6 Go"
    if quantization.startswith("Q6"):
        return "Très haute qualité, ~7 Go"
    if quantization.startswith("Q8"):
        return "Qualité maximale, ~9 Go"
    if quantization.startswith("Q2"):
        return "Très léger, ~2.5 Go"
    if quantization.startswith("Q3"):
        return "Léger, ~3.5-4 Go"
    return f"Modèle quantifié ({quantization})" if quantization else ""


def _create_catalog_model_from_filename(filename: str, repo_id: str) -> CatalogModel:
    """Crée un CatalogModel à partir d'un nom de fichier."""
    base_name = filename.replace(_GGUF_EXTENSION, "")
    model_id = base_name.lower().replace(".", "-").replace("_", "-")
    quantization = _extract_quantization(filename)
    name = _generate_model_name(base_name, quantization)
    description = _generate_description(quantization)
    category = _generate_category(quantization)
    
    return CatalogModel(
        id=model_id,
        name=name,
        repo=repo_id,
        filename=filename,
        description=description,
        category=category,
    )


def _scan_repo_for_models(api: "HfApi", repo_id: str) -> list[CatalogModel]:
    """Scanne un repo HuggingFace pour trouver les modèles .gguf."""
    try:
        files = api.list_repo_files(repo_id=repo_id, repo_type="model")
        gguf_files = [f for f in files if f.endswith(_GGUF_EXTENSION)]
        return [_create_catalog_model_from_filename(f, repo_id) for f in gguf_files]
    except Exception as e:
        logger.warning("Impossible de scanner le repo %s: %s", repo_id, e)
        return []


def list_catalog() -> list[CatalogModel]:
    """Liste les modèles du catalogue (téléchargeables) depuis HuggingFace."""
    try:
        from huggingface_hub import HfApi
        
        api = HfApi()
        catalog: list[CatalogModel] = []
        
        # Scanner chaque repo pour trouver les fichiers .gguf
        for repo_id in _REPOS_TO_SCAN:
            models = _scan_repo_for_models(api, repo_id)
            catalog.extend(models)
        
        if not catalog:
            logger.warning("Aucun modèle trouvé via l'API HuggingFace")
        
        return catalog
    except Exception as e:
        logger.error("Erreur lors de la récupération du catalogue depuis HuggingFace: %s", e)
        return []
