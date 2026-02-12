# pylint: disable=invalid-name
"""Use case : archivage d'un email (délègue à l'adapter Gmail ou Outlook)."""
from backend.ports.emailProvider import EmailProvider


class EmailsService:
    """Archive un email via l'adapter du provider (Gmail ou Outlook)."""

    def __init__(self, adapter: EmailProvider) -> None:
        self._adapter = adapter

    def archive_email(self, email_id: str) -> bool:
        """Archive l'email et retourne True si succès."""
        return self._adapter.archive_email(email_id)

    def archive_email_response(self, email_id: str) -> dict:
        """Archive l'email et retourne un dict prêt pour la réponse API."""
        success = self.archive_email(email_id)
        return (
            {"status": "success", "email_id": email_id}
            if success
            else {"status": "error"}
        )
