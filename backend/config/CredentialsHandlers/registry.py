# pylint: disable=invalid-name
"""Enregistrement des handlers de credentials pour chaque provider.

Ce module initialise les handlers en important les fonctions nécessaires
et en les enregistrant dans les enums appropriés.
"""
from google.oauth2.credentials import Credentials

from backend.config.providers import EmailProvider
from backend.config.CredentialsHandlers.saveCredentialsHandler import SaveCredentialsHandler
from backend.config.CredentialsHandlers.loadCredentialsHandler import LoadCredentialsHandler
from backend.config.CredentialsHandlers.clearCredentialsHandler import ClearCredentialsHandler
from backend.core.models.Auth import OutlookTokens


def _get_gmail_handlers():
    """Importe et retourne les handlers Gmail (import tardif pour éviter la circularité)."""
    from backend.core.services.Credentials.gmailCredentialsService import (
        _save_gmail_credentials,
        _load_gmail_credentials,
        _clear_gmail_credentials,
    )
    return _save_gmail_credentials, _load_gmail_credentials, _clear_gmail_credentials


def _get_outlook_handlers():
    """Importe et retourne les handlers Outlook (import tardif pour éviter la circularité)."""
    from backend.core.services.Credentials.outlookCredentialsService import (
        _save_outlook_credentials,
        _load_outlook_credentials,
        _clear_outlook_credentials,
    )
    return _save_outlook_credentials, _load_outlook_credentials, _clear_outlook_credentials


def register_all_handlers():
    """Enregistre tous les handlers de credentials pour chaque provider."""
    # Gmail handlers
    save_gmail, load_gmail, clear_gmail = _get_gmail_handlers()
    SaveCredentialsHandler.register(
        EmailProvider.GMAIL.value,
        save_gmail,
        Credentials,
        "Gmail attend un objet Credentials",
    )
    LoadCredentialsHandler.register(EmailProvider.GMAIL.value, load_gmail)
    ClearCredentialsHandler.register(EmailProvider.GMAIL.value, clear_gmail)

    # Outlook handlers
    save_outlook, load_outlook, clear_outlook = _get_outlook_handlers()
    SaveCredentialsHandler.register(
        EmailProvider.OUTLOOK.value,
        save_outlook,
        OutlookTokens,
        "Outlook attend un OutlookTokens",
    )
    LoadCredentialsHandler.register(EmailProvider.OUTLOOK.value, load_outlook)
    ClearCredentialsHandler.register(EmailProvider.OUTLOOK.value, clear_outlook)


# L'enregistrement est fait de manière lazy lors du premier appel aux handlers
# pour éviter les imports circulaires
