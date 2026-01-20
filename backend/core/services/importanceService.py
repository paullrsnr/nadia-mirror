# Service d'importance - Désactivé
# Ce fichier est conservé mais non utilisé

from typing import Optional
from backend.api.schemas import Email
from backend.core.services.summarizationService import SummarizationService


class ImportanceService:
    """Service pour déterminer l'importance des emails"""
    
    def __init__(self, summarization_service: Optional[SummarizationService] = None):
        self.summarization_service = summarization_service or SummarizationService()
    
    def calculate_importance(self, email: Email) -> dict:
        """Calcule un score d'importance pour un email (sans LLM)"""
        score = 0
        factors = []
        
        # Facteur 1: Labels Gmail (IMPORTANT, STARRED, etc.)
        if "IMPORTANT" in email.labels:
            score += 30
            factors.append("Label IMPORTANT")
        if "STARRED" in email.labels:
            score += 20
            factors.append("Étoilé")
        if "UNREAD" in email.labels:
            score += 10
            factors.append("Non lu")
        
        # Facteur 2: Mots-clés d'urgence dans le sujet
        urgent_keywords = ["urgent", "important", "asap", "immédiat", "délai", "deadline"]
        subject_lower = (email.subject or "").lower()
        if any(keyword in subject_lower for keyword in urgent_keywords):
            score += 15
            factors.append("Mots-clés d'urgence")
        
        # Normaliser le score entre 0 et 100
        score = min(score, 100)
        
        # Déterminer le niveau d'importance
        if score >= 70:
            level = "haute"
        elif score >= 40:
            level = "moyenne"
        else:
            level = "faible"
        
        return {
            "score": score,
            "level": level,
            "factors": factors,
            "tone": "neutre",
            "important_elements": {
                "dates": [],
                "people": [email.from_address.email],
                "actions": [],
            },
        }
