# pylint: disable=invalid-name
"""Schémas Pydantic pour la sérialisation API des modèles Email.

Ces schémas sont utilisés par FastAPI pour la sérialisation JSON.
Les modèles métier (dataclasses) restent dans le dossier parent.
"""
from backend.core.models.Email.API.emailAddressSchema import EmailAddressSchema
from backend.core.models.Email.API.emailAttachmentSchema import EmailAttachmentSchema
from backend.core.models.Email.API.emailSchema import EmailSchema
from backend.core.models.Email.API.emailListResponseSchema import EmailListResponseSchema

__all__ = [
    "EmailAddressSchema",
    "EmailAttachmentSchema",
    "EmailSchema",
    "EmailListResponseSchema",
]
