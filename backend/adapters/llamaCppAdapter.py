# Adaptateur LLaMA - Désactivé
# Ce fichier est conservé mais non utilisé

from backend.ports.llmClient import LLMClient


class LlamaCppAdapter(LLMClient):
    """Adaptateur pour llama-cpp-python"""
    
    def __init__(self):
        pass
    
    def generate(
        self,
        prompt: str,
        max_tokens: int = 512,
        temperature: float = 0.7,
        stop: list[str] = None,
    ) -> str:
        """Génère du texte à partir d'un prompt"""
        return "[Modèle LLM non disponible]"
    
    def is_available(self) -> bool:
        """Vérifie si le modèle LLM est disponible"""
        return False
