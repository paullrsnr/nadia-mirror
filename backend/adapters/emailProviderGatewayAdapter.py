from backend.core.exceptions import ProviderError
from backend.core.models.Email import Provider
from backend.ports.emailProvider import EmailProvider
from backend.ports.emailProviderGateway import EmailProviderGateway
from backend.adapters.mailProvider.GMAIL.gmailAdapter import GmailAdapter
from backend.adapters.mailProvider.Outlook.outlookAdapter import OutlookAdapter


class EmailProviderGatewayAdapter(EmailProviderGateway):
    def create(self, provider: str) -> EmailProvider:
        if provider == Provider.GMAIL.value:
            return GmailAdapter()
        if provider == Provider.OUTLOOK.value:
            return OutlookAdapter()
        raise ProviderError(f"Provider inconnu : {provider!r}")
