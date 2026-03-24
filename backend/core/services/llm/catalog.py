from dataclasses import dataclass


@dataclass
class CatalogModel:
    id: str
    name: str
    repo: str
    filename: str
    description: str
    category: str


CATALOG: list[CatalogModel] = [
    CatalogModel(
        id="tinyllama-1.1b",
        name="TinyLlama 1.1B Chat",
        repo="TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF",
        filename="tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf",
        description="Modèle ultra-léger et rapide (1.1B params) - Idéal pour démarrer",
        category="general",
    ),
    CatalogModel(
        id="phi-3-mini",
        name="Phi-3 Mini 4K Instruct",
        repo="microsoft/Phi-3-mini-4k-instruct-gguf",
        filename="Phi-3-mini-4k-instruct-q4.gguf",
        description="Modèle compact et performant de Microsoft (3.8B params)",
        category="general",
    ),
    CatalogModel(
        id="llama-3.2-1b",
        name="Llama 3.2 1B Instruct",
        repo="hugging-quants/Llama-3.2-1B-Instruct-Q4_K_M-GGUF",
        filename="llama-3.2-1b-instruct-q4_k_m.gguf",
        description="Modèle très léger de Meta (1B params)",
        category="general",
    ),
    CatalogModel(
        id="llama-3.2-3b",
        name="Llama 3.2 3B Instruct",
        repo="hugging-quants/Llama-3.2-3B-Instruct-Q4_K_M-GGUF",
        filename="llama-3.2-3b-instruct-q4_k_m.gguf",
        description="Modèle léger de Meta (3B params)",
        category="general",
    ),
    CatalogModel(
        id="mistral-7b",
        name="Mistral 7B Instruct v0.3",
        repo="MaziyarPanahi/Mistral-7B-Instruct-v0.3-GGUF",
        filename="Mistral-7B-Instruct-v0.3.Q4_K_M.gguf",
        description="Excellent modèle polyvalent de Mistral AI (7B params)",
        category="general",
    ),
    CatalogModel(
        id="qwen2.5-3b",
        name="Qwen 2.5 3B Instruct",
        repo="Qwen/Qwen2.5-3B-Instruct-GGUF",
        filename="qwen2.5-3b-instruct-q4_k_m.gguf",
        description="Modèle performant d'Alibaba (3B params)",
        category="general",
    ),
]


def list_catalog() -> list[CatalogModel]:
    """Retourne la liste des modèles disponibles au téléchargement."""
    return CATALOG


def get_catalog_model(model_id: str) -> CatalogModel | None:
    """Récupère un modèle du catalogue par son ID."""
    for model in CATALOG:
        if model.id == model_id:
            return model
    return None
