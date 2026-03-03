"""Modèles bruts de l'API Microsoft Graph (JSON responses)."""
from backend.adapters.MailProvider.Outlook.models.graphEmailAddress import GraphEmailAddress
from backend.adapters.MailProvider.Outlook.models.graphMessageBody import GraphMessageBody
from backend.adapters.MailProvider.Outlook.models.graphRecipient import GraphRecipient
from backend.adapters.MailProvider.Outlook.models.graphMessage import GraphMessage

__all__ = ["GraphEmailAddress", "GraphMessageBody", "GraphRecipient", "GraphMessage"]
