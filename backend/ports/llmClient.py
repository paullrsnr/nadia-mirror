# Interface LLM Client - Désactivée
# Ce fichier est conservé mais non utilisé

from abc import ABC, abstractmethod
from typing import Optional


class LLMClient(ABC):
    """Interface pour les clients LLM"""
    
    @abstractmethod
    def generate(
        self,
        prompt: str,
        max_tokens: int = 512,
        temperature: float = 0.7,
        stop: Optional[list[str]] = None,
    ) -> str:
        """Génère du texte à partir d'un prompt"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Vérifie si le modèle LLM est disponible"""
        pass
