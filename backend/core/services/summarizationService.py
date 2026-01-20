# Service de résumé - Désactivé
# Ce fichier est conservé mais non utilisé

from backend.api.schemas import Email


class SummarizationService:
    """Service pour générer des résumés d'emails"""
    
    def summarize_email(self, email: Email) -> str:
        """Génère un résumé d'un email (fallback sans LLM)"""
        snippet = email.snippet or ""
        if len(snippet) > 150:
            return snippet[:150] + "..."
        return snippet or "Aucun résumé disponible"
    
    def extract_key_subject(self, email: Email) -> str:
        """Extrait le sujet clé de l'email"""
        return email.subject or "[Sans objet]"
    
    def extract_important_elements(self, email: Email) -> dict:
        """Extrait les éléments importants (dates, personnes, actions)"""
        return {
            "dates": [],
            "people": [email.from_address.email],
            "actions": [],
        }
    
    def detect_tone(self, email: Email) -> str:
        """Détecte le ton de l'email"""
        return "neutre"
