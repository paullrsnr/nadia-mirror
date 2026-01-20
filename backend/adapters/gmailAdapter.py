from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from typing import List, Optional, Tuple
from datetime import datetime
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import parsedate_to_datetime

from backend.ports.emailProvider import EmailProvider
from backend.api.schemas import Email, EmailThread, EmailAddress, EmailAttachment
from backend.api.routers.auth_router import get_credentials
from backend.utils.emailParser import parse_email_address, extract_email_body


class GmailAdapter(EmailProvider):
    """Adaptateur pour l'API Gmail"""
    
    def __init__(self):
        self.service = None
        self._ensure_service()
    
    def _ensure_service(self):
        """Initialise le service Gmail si les credentials sont disponibles"""
        credentials = get_credentials()
        if credentials:
            self.service = build("gmail", "v1", credentials=credentials)
        else:
            raise ValueError("Credentials Gmail non disponibles. Authentification requise.")
    
    def get_emails(
        self,
        max_results: int = 50,
        query: Optional[str] = None,
        page_token: Optional[str] = None,
    ) -> Tuple[List[Email], Optional[str]]:
        """Récupère une liste d'emails depuis Gmail"""
        if not self.service:
            self._ensure_service()
        
        try:
            results = (
                self.service.users()
                .messages()
                .list(
                    userId="me",
                    maxResults=max_results,
                    q=query,
                    pageToken=page_token,
                )
                .execute()
            )
            
            messages = results.get("messages", [])
            next_page_token = results.get("nextPageToken")
            
            emails = []
            for msg in messages:
                email_obj = self.get_email(msg["id"])
                emails.append(email_obj)
            
            return emails, next_page_token
        except Exception as e:
            raise Exception(f"Erreur lors de la récupération des emails: {str(e)}")
    
    def get_email(self, email_id: str) -> Email:
        """Récupère un email spécifique depuis Gmail"""
        if not self.service:
            self._ensure_service()
        
        try:
            message = (
                self.service.users()
                .messages()
                .get(userId="me", id=email_id, format="full")
                .execute()
            )
            
            return self._parse_gmail_message(message)
        except Exception as e:
            raise Exception(f"Erreur lors de la récupération de l'email: {str(e)}")
    
    def _parse_gmail_message(self, message: dict) -> Email:
        """Parse un message Gmail en objet Email"""
        payload = message["payload"]
        headers = payload.get("headers", [])
        
        # Extraire les headers
        header_dict = {h["name"].lower(): h["value"] for h in headers}
        
        # Parser les adresses
        from_addr = parse_email_address(header_dict.get("from", ""))
        to_addrs = [
            parse_email_address(addr)
            for addr in header_dict.get("to", "").split(",")
            if addr.strip()
        ]
        cc_addrs = [
            parse_email_address(addr)
            for addr in header_dict.get("cc", "").split(",")
            if addr.strip()
        ] if header_dict.get("cc") else []
        
        # Parser la date (format RFC 2822)
        date_str = header_dict.get("date", "")
        try:
            date = parsedate_to_datetime(date_str) if date_str else datetime.now()
        except (ValueError, TypeError):
            date = datetime.now()
        
        # Extraire le corps de l'email
        body_text, body_html = extract_email_body(payload)
        
        # Extraire les pièces jointes
        attachments = []
        if "parts" in payload:
            for part in payload["parts"]:
                if part.get("filename") and part.get("body", {}).get("attachmentId"):
                    attachments.append(
                        EmailAttachment(
                            filename=part["filename"],
                            mime_type=part.get("mimeType", "application/octet-stream"),
                            size=part.get("body", {}).get("size", 0),
                            attachment_id=part["body"]["attachmentId"],
                        )
                    )
        
        return Email(
            id=message["id"],
            thread_id=message["threadId"],
            subject=header_dict.get("subject", ""),
            from_address=from_addr,
            to_addresses=to_addrs,
            cc_addresses=cc_addrs,
            bcc_addresses=[],  # Gmail ne retourne pas les BCC dans les messages reçus
            date=date,
            body_text=body_text,
            body_html=body_html,
            attachments=attachments,
            labels=message.get("labelIds", []),
            snippet=message.get("snippet"),
        )
    
    def get_thread(self, thread_id: str) -> EmailThread:
        """Récupère un thread de conversation"""
        if not self.service:
            self._ensure_service()
        
        try:
            thread = (
                self.service.users()
                .threads()
                .get(userId="me", id=thread_id)
                .execute()
            )
            
            messages = thread.get("messages", [])
            emails = [self._parse_gmail_message(msg) for msg in messages]
            emails.sort(key=lambda e: e.date)
            
            # Extraire les participants
            participants = set()
            for email_obj in emails:
                participants.add(email_obj.from_address.email)
                for addr in email_obj.to_addresses:
                    participants.add(addr.email)
            
            # Compter les non lus
            unread_count = sum(1 for e in emails if "UNREAD" in e.labels)
            
            return EmailThread(
                thread_id=thread_id,
                subject=emails[0].subject if emails else "",
                emails=emails,
                participants=[EmailAddress(email=email) for email in participants],
                last_message_date=emails[-1].date if emails else datetime.now(),
                unread_count=unread_count,
            )
        except Exception as e:
            raise Exception(f"Erreur lors de la récupération du thread: {str(e)}")
    
    def get_threads(
        self,
        max_results: int = 50,
        query: Optional[str] = None,
        page_token: Optional[str] = None,
    ) -> Tuple[List[EmailThread], Optional[str]]:
        """Récupère une liste de threads"""
        if not self.service:
            self._ensure_service()
        
        try:
            results = (
                self.service.users()
                .threads()
                .list(
                    userId="me",
                    maxResults=max_results,
                    q=query,
                    pageToken=page_token,
                )
                .execute()
            )
            
            threads = results.get("threads", [])
            next_page_token = results.get("nextPageToken")
            
            thread_objects = []
            for thread in threads:
                thread_obj = self.get_thread(thread["id"])
                thread_objects.append(thread_obj)
            
            return thread_objects, next_page_token
        except Exception as e:
            raise Exception(f"Erreur lors de la récupération des threads: {str(e)}")
    
    def send_email(
        self,
        to: List[str],
        subject: str,
        body_text: str,
        body_html: Optional[str] = None,
        thread_id: Optional[str] = None,
    ) -> str:
        """Envoie un email via Gmail"""
        if not self.service:
            self._ensure_service()
        
        try:
            message = MIMEMultipart("alternative")
            message["to"] = ", ".join(to)
            message["subject"] = subject
            
            if thread_id:
                message["In-Reply-To"] = thread_id
                message["References"] = thread_id
            
            # Ajouter le texte et HTML
            message.attach(MIMEText(body_text, "plain"))
            if body_html:
                message.attach(MIMEText(body_html, "html"))
            
            # Encoder et envoyer
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
            
            send_message = {"raw": raw_message}
            if thread_id:
                send_message["threadId"] = thread_id
            
            result = (
                self.service.users()
                .messages()
                .send(userId="me", body=send_message)
                .execute()
            )
            
            return result["id"]
        except Exception as e:
            raise Exception(f"Erreur lors de l'envoi de l'email: {str(e)}")
    
    def archive_email(self, email_id: str) -> bool:
        """Archive un email (supprime le label INBOX)"""
        if not self.service:
            self._ensure_service()
        
        try:
            self.service.users().messages().modify(
                userId="me",
                id=email_id,
                body={"removeLabelIds": ["INBOX"]},
            ).execute()
            return True
        except Exception as e:
            raise Exception(f"Erreur lors de l'archivage: {str(e)}")
    
    def mark_as_read(self, email_id: str) -> bool:
        """Marque un email comme lu"""
        if not self.service:
            self._ensure_service()
        
        try:
            self.service.users().messages().modify(
                userId="me",
                id=email_id,
                body={"removeLabelIds": ["UNREAD"]},
            ).execute()
            return True
        except Exception as e:
            raise Exception(f"Erreur lors du marquage comme lu: {str(e)}")
