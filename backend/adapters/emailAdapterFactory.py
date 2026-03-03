# pylint: disable=invalid-name
"""Factory : instancie l'adapter email pour un provider donné."""
from backend.core.models.Email import Provider
from backend.ports.emailProvider import EmailProvider as IEmailProvider
from backend.adapters.MailProvider.GMAIL.gmailAdapter import GmailAdapter
from backend.adapters.MailProvider.Outlook.outlookAdapter import OutlookAdapter


def create_email_adapter(provider: str) -> IEmailProvider:
    """Retourne l'adapter instancié pour le provider (gmail ou outlook).

    Raises:
        ValueError: Si le provider est inconnu.
    """
    if provider == Provider.GMAIL.value:
        return GmailAdapter()
    if provider == Provider.OUTLOOK.value:
        return OutlookAdapter()
    raise ValueError(f"Provider inconnu : {provider!r}")
