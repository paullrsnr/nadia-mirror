from typing import List, Optional
from datetime import datetime, timedelta
from backend.adapters.gmailAdapter import GmailAdapter
from backend.adapters.sqliteStorage import SqliteStorage
from backend.api.schemas import Email, EmailThread
from backend.api.routers.auth_router import get_credentials


class MailboxService:
    """Service pour gérer la synchronisation et le stockage des emails"""
    
    def __init__(self):
        self.storage = SqliteStorage()
        self._gmail_adapter = None
    
    def _get_gmail_adapter(self) -> GmailAdapter:
        """Récupère l'adaptateur Gmail"""
        if not self._gmail_adapter:
            credentials = get_credentials()
            if not credentials:
                raise ValueError("Non authentifié")
            self._gmail_adapter = GmailAdapter()
        return self._gmail_adapter
    
    def sync_emails(
        self,
        max_results: int = 100,
        query: Optional[str] = None,
        force: bool = False,
    ) -> dict:
        """Synchronise les emails depuis Gmail vers le stockage local"""
        try:
            adapter = self._get_gmail_adapter()
            
            # Si force=False, ne synchroniser que les nouveaux emails
            if not force:
                last_sync = self.storage.get_last_sync_time()
                if last_sync:
                    # Synchroniser seulement les emails des 7 derniers jours
                    query = f"after:{(datetime.now() - timedelta(days=7)).strftime('%Y/%m/%d')}"
            
            emails, _ = adapter.get_emails(max_results=max_results, query=query)
            
            # Sauvegarder les emails dans le stockage local
            saved_count = 0
            for email in emails:
                if self.storage.save_email(email):
                    saved_count += 1
            
            # Mettre à jour le timestamp de dernière synchronisation
            self.storage.update_last_sync_time()
            
            return {
                "status": "success",
                "synced": len(emails),
                "saved": saved_count,
                "timestamp": datetime.now().isoformat(),
            }
        except ValueError as e:
            return {"status": "error", "message": str(e)}
        except Exception as e:
            return {"status": "error", "message": f"Erreur de synchronisation: {str(e)}"}
    
    def get_local_emails(
        self,
        limit: int = 50,
        offset: int = 0,
        query: Optional[str] = None,
    ) -> List[Email]:
        """Récupère les emails depuis le stockage local"""
        return self.storage.get_emails(limit=limit, offset=offset, query=query)
    
    def get_local_threads(
        self,
        limit: int = 50,
        offset: int = 0,
    ) -> List[EmailThread]:
        """Récupère les threads depuis le stockage local"""
        return self.storage.get_threads(limit=limit, offset=offset)
    
    def get_email_from_gmail(self, email_id: str) -> Email:
        """Récupère un email directement depuis Gmail"""
        adapter = self._get_gmail_adapter()
        return adapter.get_email(email_id)
    
    def get_thread_from_gmail(self, thread_id: str) -> EmailThread:
        """Récupère un thread directement depuis Gmail"""
        adapter = self._get_gmail_adapter()
        return adapter.get_thread(thread_id)
