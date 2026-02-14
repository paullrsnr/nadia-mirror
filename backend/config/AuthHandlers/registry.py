# pylint: disable=invalid-name
"""Enregistrement des handlers d'authentification pour chaque provider.

Ce module initialise les handlers en important les fonctions nécessaires
et en les enregistrant dans les enums appropriés.
"""
from backend.config.providers import EmailProvider
from backend.config.AuthHandlers.authUrlHandler import AuthUrlHandler
from backend.config.AuthHandlers.callbackHandler import CallbackHandler
from backend.config.AuthHandlers.authStatusHandler import AuthStatusHandler


def _get_gmail_handlers():
    """Importe et retourne les handlers Gmail (import tardif pour éviter la circularité)."""
    from backend.core.services.authService import (
        _get_gmail_auth_url,
        _process_gmail_callback,
        _get_gmail_auth_status,
    )
    return _get_gmail_auth_url, _process_gmail_callback, _get_gmail_auth_status


def _get_outlook_handlers():
    """Importe et retourne les handlers Outlook (import tardif pour éviter la circularité)."""
    from backend.core.services.authService import (
        _get_outlook_auth_url,
        _process_outlook_callback,
        _get_outlook_auth_status,
    )
    return _get_outlook_auth_url, _process_outlook_callback, _get_outlook_auth_status


def register_all_handlers():
    """Enregistre tous les handlers d'authentification pour chaque provider."""
    # Gmail handlers
    gmail_url, gmail_callback, gmail_status = _get_gmail_handlers()
    AuthUrlHandler.register(EmailProvider.GMAIL.value, gmail_url)
    CallbackHandler.register(EmailProvider.GMAIL.value, gmail_callback)
    AuthStatusHandler.register(EmailProvider.GMAIL.value, gmail_status)

    # Outlook handlers
    outlook_url, outlook_callback, outlook_status = _get_outlook_handlers()
    AuthUrlHandler.register(EmailProvider.OUTLOOK.value, outlook_url)
    CallbackHandler.register(EmailProvider.OUTLOOK.value, outlook_callback)
    AuthStatusHandler.register(EmailProvider.OUTLOOK.value, outlook_status)


# L'enregistrement est fait de manière lazy lors du premier appel aux handlers
# pour éviter les imports circulaires
