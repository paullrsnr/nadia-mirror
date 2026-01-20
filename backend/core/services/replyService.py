# Service de réponse - Désactivé
# Ce fichier est conservé mais non utilisé

from typing import Optional
from backend.api.schemas import Email, EmailThread


class ReplyService:
    """Service pour générer des réponses d'emails"""
    
    def generate_reply(
        self,
        email: Email,
        thread: Optional[EmailThread] = None,
        tone: str = "professionnel",
        length: str = "moyen",
    ) -> str:
        """Génère une réponse à un email (fallback sans LLM)"""
        return "[Fonctionnalité de génération de réponse non disponible]"
