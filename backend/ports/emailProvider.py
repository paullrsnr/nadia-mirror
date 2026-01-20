from abc import ABC, abstractmethod
from typing import List, Optional
from backend.api.schemas import Email, EmailThread


class EmailProvider(ABC):
    """Interface pour les fournisseurs d'email"""
    
    @abstractmethod
    def get_emails(
        self,
        max_results: int = 50,
        query: Optional[str] = None,
        page_token: Optional[str] = None,
    ) -> tuple[List[Email], Optional[str]]:
        """Récupère une liste d'emails"""
        pass
    
    @abstractmethod
    def get_email(self, email_id: str) -> Email:
        """Récupère un email spécifique"""
        pass
    
    @abstractmethod
    def get_thread(self, thread_id: str) -> EmailThread:
        """Récupère un thread de conversation"""
        pass
    
    @abstractmethod
    def get_threads(
        self,
        max_results: int = 50,
        query: Optional[str] = None,
        page_token: Optional[str] = None,
    ) -> tuple[List[EmailThread], Optional[str]]:
        """Récupère une liste de threads"""
        pass
    
    @abstractmethod
    def send_email(
        self,
        to: List[str],
        subject: str,
        body_text: str,
        body_html: Optional[str] = None,
        thread_id: Optional[str] = None,
    ) -> str:
        """Envoie un email"""
        pass
    
    @abstractmethod
    def archive_email(self, email_id: str) -> bool:
        """Archive un email"""
        pass
    
    @abstractmethod
    def mark_as_read(self, email_id: str) -> bool:
        """Marque un email comme lu"""
        pass
