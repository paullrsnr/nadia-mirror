import sqlite3
import json
from datetime import datetime
from typing import List, Optional
from pathlib import Path
from backend.api.schemas import Email, EmailThread, EmailAddress
from backend.config.settings import settings


class SqliteStorage:
    """Stockage local SQLite pour les emails"""
    
    def __init__(self):
        settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.db_path = settings.DATA_DIR / "emails.db"
        self._init_database()
    
    def _init_database(self):
        """Initialise la base de données"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Table des emails
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS emails (
                id TEXT PRIMARY KEY,
                thread_id TEXT NOT NULL,
                subject TEXT,
                from_name TEXT,
                from_email TEXT,
                to_addresses TEXT,
                cc_addresses TEXT,
                bcc_addresses TEXT,
                date TEXT NOT NULL,
                body_text TEXT,
                body_html TEXT,
                attachments TEXT,
                labels TEXT,
                snippet TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Table des threads
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS threads (
                thread_id TEXT PRIMARY KEY,
                subject TEXT,
                last_message_date TEXT,
                unread_count INTEGER DEFAULT 0,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Table de synchronisation
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sync_metadata (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                last_sync_time TEXT,
                sync_count INTEGER DEFAULT 0
            )
        """)
        
        # Index pour améliorer les performances
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_thread_id ON emails(thread_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_date ON emails(date)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_from_email ON emails(from_email)")
        
        conn.commit()
        conn.close()
    
    def save_email(self, email: Email) -> bool:
        """Sauvegarde un email dans la base de données"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO emails (
                    id, thread_id, subject, from_name, from_email,
                    to_addresses, cc_addresses, bcc_addresses,
                    date, body_text, body_html, attachments, labels, snippet
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                email.id,
                email.thread_id,
                email.subject,
                email.from_address.name,
                email.from_address.email,
                json.dumps([{"name": a.name, "email": a.email} for a in email.to_addresses]),
                json.dumps([{"name": a.name, "email": a.email} for a in email.cc_addresses]),
                json.dumps([{"name": a.name, "email": a.email} for a in email.bcc_addresses]),
                email.date.isoformat(),
                email.body_text,
                email.body_html,
                json.dumps([{"filename": a.filename, "mime_type": a.mime_type, "size": a.size, "attachment_id": a.attachment_id} for a in email.attachments]),
                json.dumps(email.labels),
                email.snippet,
            ))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Erreur lors de la sauvegarde de l'email: {e}")
            return False
        finally:
            conn.close()
    
    def get_emails(
        self,
        limit: int = 50,
        offset: int = 0,
        query: Optional[str] = None,
    ) -> List[Email]:
        """Récupère les emails depuis la base de données"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        sql = "SELECT * FROM emails WHERE 1=1"
        params = []
        
        if query:
            sql += " AND (subject LIKE ? OR body_text LIKE ? OR from_email LIKE ?)"
            params.extend([f"%{query}%", f"%{query}%", f"%{query}%"])
        
        sql += " ORDER BY date DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        conn.close()
        
        emails = []
        for row in rows:
            emails.append(self._row_to_email(row))
        
        return emails
    
    def _row_to_email(self, row: sqlite3.Row) -> Email:
        """Convertit une ligne de base de données en objet Email"""
        return Email(
            id=row["id"],
            thread_id=row["thread_id"],
            subject=row["subject"] or "",
            from_address=EmailAddress(
                name=row["from_name"],
                email=row["from_email"],
            ),
            to_addresses=[
                EmailAddress(**addr) for addr in json.loads(row["to_addresses"] or "[]")
            ],
            cc_addresses=[
                EmailAddress(**addr) for addr in json.loads(row["cc_addresses"] or "[]")
            ],
            bcc_addresses=[
                EmailAddress(**addr) for addr in json.loads(row["bcc_addresses"] or "[]")
            ],
            date=datetime.fromisoformat(row["date"]),
            body_text=row["body_text"] or "",
            body_html=row["body_html"],
            attachments=[],  # TODO: Parser les attachments
            labels=json.loads(row["labels"] or "[]"),
            snippet=row["snippet"],
        )
    
    def get_threads(self, limit: int = 50, offset: int = 0) -> List[EmailThread]:
        """Récupère les threads depuis la base de données"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Récupérer les threads avec leurs emails
        cursor.execute("""
            SELECT DISTINCT thread_id FROM emails
            ORDER BY date DESC
            LIMIT ? OFFSET ?
        """, (limit, offset))
        
        thread_ids = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        threads = []
        for thread_id in thread_ids:
            thread = self.get_thread(thread_id)
            if thread:
                threads.append(thread)
        
        return threads
    
    def get_thread(self, thread_id: str) -> Optional[EmailThread]:
        """Récupère un thread spécifique"""
        emails = self.get_emails(limit=1000, query=None)
        thread_emails = [e for e in emails if e.thread_id == thread_id]
        
        if not thread_emails:
            return None
        
        thread_emails.sort(key=lambda e: e.date)
        
        # Extraire les participants
        participants = set()
        for email in thread_emails:
            participants.add(email.from_address.email)
            for addr in email.to_addresses:
                participants.add(addr.email)
        
        unread_count = sum(1 for e in thread_emails if "UNREAD" in e.labels)
        
        return EmailThread(
            thread_id=thread_id,
            subject=thread_emails[0].subject if thread_emails else "",
            emails=thread_emails,
            participants=[EmailAddress(email=email) for email in participants],
            last_message_date=thread_emails[-1].date if thread_emails else datetime.now(),
            unread_count=unread_count,
        )
    
    def get_last_sync_time(self) -> Optional[datetime]:
        """Récupère le timestamp de la dernière synchronisation"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT last_sync_time FROM sync_metadata ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        conn.close()
        
        if row and row[0]:
            return datetime.fromisoformat(row[0])
        return None
    
    def update_last_sync_time(self):
        """Met à jour le timestamp de dernière synchronisation"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO sync_metadata (last_sync_time, sync_count)
            VALUES (?, COALESCE((SELECT MAX(sync_count) FROM sync_metadata), 0) + 1)
        """, (datetime.now().isoformat(),))
        
        conn.commit()
        conn.close()
