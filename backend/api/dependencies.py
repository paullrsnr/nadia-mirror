# pylint: disable=invalid-name
"""Dépendances API : résolution du provider et des adapters email (Gmail, Outlook)."""
from fastapi import HTTPException, Request

from backend.ports.emailProvider import EmailProvider
from backend.adapters.gmailAdapter import GmailAdapter
from backend.adapters.outlookAdapter import OutlookAdapter
from backend.core.services.connectionOrchestrator import get_connection_credentials

# Valeurs possibles pour le paramètre ?provider=
PROVIDERS_LIST = ("gmail", "outlook", "all")  # liste d'emails peut être "all"
PROVIDERS_SINGLE = ("gmail", "outlook")  # archive / sync ciblé
MSG_UNAUTHENTICATED = "Non authentifié"


def _provider_from_query(request: Request, default: str = "gmail") -> str:
    """Lit et normalise le paramètre provider en query (?provider=)."""
    raw = (request.query_params.get("provider") or "").strip().lower()
    return raw if raw else default


def get_provider_for_list(request: Request) -> str:
    """Retourne le provider pour la liste d'emails : gmail, outlook ou all.

    - Si provider=all : exige au moins une boîte connectée.
    - Sinon : exige que la boîte correspondante soit connectée.
    """
    provider = _provider_from_query(request)
    if provider not in PROVIDERS_LIST:
        provider = "gmail"

    if provider == "all":
        credentials_gmail = get_connection_credentials("gmail")
        credentials_outlook = get_connection_credentials("outlook")
        if not credentials_gmail and not credentials_outlook:
            raise HTTPException(status_code=401, detail=f"{MSG_UNAUTHENTICATED} (aucune boîte)")
        return "all"

    credentials = get_connection_credentials(provider)
    if not credentials:
        raise HTTPException(status_code=401, detail=MSG_UNAUTHENTICATED)
    return provider


def get_provider_for_archive(request: Request) -> str:
    """Retourne le provider pour l'archivage (gmail ou outlook). Refuse 'all'."""
    provider = _provider_from_query(request)
    if provider not in PROVIDERS_SINGLE:
        raise HTTPException(
            status_code=400,
            detail=(
                "Pour archiver, indiquer provider=gmail ou provider=outlook"
            ),
        )
    credentials = get_connection_credentials(provider)
    if not credentials:
        raise HTTPException(status_code=401, detail=MSG_UNAUTHENTICATED)
    return provider


def get_email_adapter(provider: str) -> EmailProvider:
    """Retourne l'adapter email (gmail/outlook). Lève si invalide ou non connecté."""
    if provider not in PROVIDERS_SINGLE:
        raise HTTPException(
            status_code=400,
            detail="Provider doit être gmail ou outlook",
        )
    credentials = get_connection_credentials(provider)
    if not credentials:
        raise HTTPException(status_code=401, detail=MSG_UNAUTHENTICATED)
    return GmailAdapter() if provider == "gmail" else OutlookAdapter()
