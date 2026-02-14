# pylint: disable=invalid-name
"""Repository pour les opérations CRUD sur les emails avec SQLAlchemy."""
import json
import logging
from datetime import datetime
from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from backend.config.providers import EmailProvider
from backend.core.models.email import Email, EmailAddress, EmailAttachment
from backend.database.models import EmailModel, SyncMetadataModel

logger = logging.getLogger(__name__)


class EmailRepository:
    """Repository pour gérer les emails en base de données avec SQLAlchemy.
    
    Fournit des méthodes CRUD et de conversion entre les modèles
    de domaine (Email) et les modèles de base de données (EmailModel).
    """

    def __init__(self, session: Session) -> None:
        """Initialise le repository avec une session SQLAlchemy.
        
        Args:
            session: Session SQLAlchemy à utiliser pour les opérations.
        """
        self.session = session

    def save_email(self, email: Email, provider: str = EmailProvider.GMAIL.value) -> bool:
        """Sauvegarde un email dans la base de données.
        
        Args:
            email: Email à sauvegarder.
            provider: Provider d'origine (gmail ou outlook).
        
        Returns:
            True si succès, False sinon.
        """
        try:
            email_model = EmailModel(
                id=email.id,
                thread_id=email.thread_id,
                subject=email.subject,
                from_name=email.from_address.name,
                from_email=email.from_address.email,
                to_addresses=json.dumps(
                    [{"name": a.name, "email": a.email} for a in email.to_addresses]
                ),
                cc_addresses=json.dumps(
                    [{"name": a.name, "email": a.email} for a in email.cc_addresses]
                ),
                bcc_addresses=json.dumps(
                    [{"name": a.name, "email": a.email} for a in email.bcc_addresses]
                ),
                date=email.date.isoformat(),
                body_text=email.body_text,
                body_html=email.body_html,
                attachments=json.dumps(
                    [
                        {
                            "filename": a.filename,
                            "mime_type": a.mime_type,
                            "size": a.size,
                            "attachment_id": a.attachment_id,
                        }
                        for a in email.attachments
                    ]
                ),
                labels=json.dumps(email.labels),
                snippet=email.snippet,
                provider=provider.lower(),
            )
            
            # Merge pour INSERT OR REPLACE
            self.session.merge(email_model)
            self.session.commit()
            return True
        except Exception as e:
            logger.error("Erreur lors de la sauvegarde de l'email: %s", e)
            self.session.rollback()
            return False

    def get_emails(
        self,
        max_results: int = 50,
        offset: int = 0,
        provider_filter: str | None = None,
    ) -> tuple[list[Email], int]:
        """Retourne les emails en base (paginés).
        
        Args:
            max_results: Nombre maximum de résultats.
            offset: Offset pour la pagination.
            provider_filter: Filtre par provider (gmail, outlook) ou None pour tous.
        
        Returns:
            Tuple (liste d'emails, total).
        """
        try:
            # Construire la requête de base
            query = select(EmailModel)
            count_query = select(func.count(EmailModel.id))
            
            # Appliquer le filtre provider si nécessaire
            if provider_filter and provider_filter.lower() not in ("", EmailProvider.ALL.value):
                pf = provider_filter.lower()
                query = query.where(EmailModel.provider == pf)
                count_query = count_query.where(EmailModel.provider == pf)
            
            # Compter le total
            total = self.session.execute(count_query).scalar() or 0
            
            # Récupérer les emails avec pagination
            query = query.order_by(EmailModel.date.desc()).limit(max_results).offset(offset)
            result = self.session.execute(query)
            email_models = result.scalars().all()
            
            # Convertir en objets Email
            emails = [self._model_to_email(model) for model in email_models]
            return emails, total
        except Exception as e:
            logger.error("Erreur lors de la récupération des emails: %s", e)
            return [], 0

    def get_last_sync_time(self) -> Optional[datetime]:
        """Récupère le timestamp de la dernière synchronisation.
        
        Returns:
            Datetime de la dernière sync ou None.
        """
        try:
            query = select(SyncMetadataModel).order_by(SyncMetadataModel.id.desc()).limit(1)
            result = self.session.execute(query)
            sync_metadata = result.scalars().first()
            
            if sync_metadata and sync_metadata.last_sync_time:
                return datetime.fromisoformat(sync_metadata.last_sync_time)
            return None
        except Exception as e:
            logger.error("Erreur lors de la récupération du dernier sync time: %s", e)
            return None

    def update_last_sync_time(self) -> None:
        """Met à jour le timestamp de dernière synchronisation."""
        try:
            # Récupérer le dernier count
            query = select(func.max(SyncMetadataModel.sync_count))
            max_count = self.session.execute(query).scalar() or 0
            
            # Créer un nouveau record
            sync_metadata = SyncMetadataModel(
                last_sync_time=datetime.now().isoformat(),
                sync_count=max_count + 1,
            )
            self.session.add(sync_metadata)
            self.session.commit()
        except Exception as e:
            logger.error("Erreur lors de la mise à jour du sync time: %s", e)
            self.session.rollback()

    def _model_to_email(self, model: EmailModel) -> Email:
        """Convertit un EmailModel en Email (objet de domaine).
        
        Args:
            model: EmailModel de la base de données.
        
        Returns:
            Email (objet de domaine).
        """
        def parse_addresses(data: str | None, field_name: str) -> list[EmailAddress]:
            if not data or data == "null":
                return []
            try:
                items = json.loads(data)
                
                # Gestion de la double sérialisation (anciennes données)
                if isinstance(items, str):
                    logger.warning(
                        "Double sérialisation détectée pour %s (email_id=%s), parsing à nouveau",
                        field_name, model.id
                    )
                    items = json.loads(items)
                
                return [
                    EmailAddress(email=a["email"], name=a.get("name"))
                    for a in items
                ]
            except (TypeError, KeyError) as e:
                logger.error(
                    "Erreur parse_addresses pour %s (email_id=%s): %s. Data=%r",
                    field_name, model.id, e, data
                )
                raise

        def parse_attachments(data: str | None) -> list[EmailAttachment]:
            if not data or data == "null":
                return []
            try:
                items = json.loads(data)
                
                # Gestion de la double sérialisation (anciennes données)
                if isinstance(items, str):
                    logger.warning(
                        "Double sérialisation détectée pour attachments (email_id=%s), parsing à nouveau",
                        model.id
                    )
                    items = json.loads(items)
                
                return [
                    EmailAttachment(
                        filename=a["filename"],
                        mime_type=a["mime_type"],
                        size=a["size"],
                        attachment_id=a.get("attachment_id"),
                    )
                    for a in items
                ]
            except (TypeError, KeyError) as e:
                logger.error(
                    "Erreur parse_attachments (email_id=%s): %s. Data=%r",
                    model.id, e, data
                )
                raise

        try:
            if not model.labels or model.labels == "null":
                labels_list = []
            else:
                labels_list = json.loads(model.labels)
                
                # Gestion de la double sérialisation (anciennes données)
                if isinstance(labels_list, str):
                    logger.warning(
                        "Double sérialisation détectée pour labels (email_id=%s), parsing à nouveau",
                        model.id
                    )
                    labels_list = json.loads(labels_list)
        except (TypeError, json.JSONDecodeError) as e:
            logger.error(
                "Erreur parse labels (email_id=%s): %s. Data=%r",
                model.id, e, model.labels
            )
            raise

        try:
            date_obj = datetime.fromisoformat(model.date) if model.date else datetime.now()
        except (TypeError, ValueError) as e:
            logger.error(
                "Erreur parse date (email_id=%s): %s. Data=%r",
                model.id, e, model.date
            )
            raise

        return Email(
            id=model.id,
            thread_id=model.thread_id,
            subject=model.subject or "",
            from_address=EmailAddress(email=model.from_email or "", name=model.from_name),
            to_addresses=parse_addresses(model.to_addresses, "to_addresses"),
            cc_addresses=parse_addresses(model.cc_addresses, "cc_addresses"),
            bcc_addresses=parse_addresses(model.bcc_addresses, "bcc_addresses"),
            date=date_obj,
            body_text=model.body_text or "",
            body_html=model.body_html,
            attachments=parse_attachments(model.attachments),
            labels=labels_list,
            snippet=model.snippet,
            provider=model.provider if model.provider else None,
        )
