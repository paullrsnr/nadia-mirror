# pylint: disable=invalid-name
"""Registre centralisé des adapters email par provider."""
from enum import Enum
from typing import Type

from backend.config.providers import EmailProvider
from backend.adapters.MailProvider.GMAIL.gmailAdapter import GmailAdapter
from backend.adapters.MailProvider.Outlook.outlookAdapter import OutlookAdapter
from backend.ports.emailProvider import EmailProvider as EmailProviderInterface


class AdapterRegistry(Enum):
    """Enum : provider → classe d'adapter email."""

    GMAIL = (EmailProvider.GMAIL.value, GmailAdapter)
    OUTLOOK = (EmailProvider.OUTLOOK.value, OutlookAdapter)

    def __init__(self, provider_value: str, adapter_class: Type[EmailProviderInterface]):
        self.provider_value = provider_value
        self.adapter_class = adapter_class

    @classmethod
    def get_adapter_class(cls, provider: str) -> Type[EmailProviderInterface] | None:
        """Retourne la classe d'adapter pour un provider donné."""
        for member in cls:
            if member.provider_value == provider:
                return member.adapter_class
        return None
