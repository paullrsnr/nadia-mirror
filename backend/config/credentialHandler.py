# python
"""Orchestrateur de gestion des credentials : délègue vers les handlers spécifiques par provider."""
from backend.config.providers import CONNECTABLE_PROVIDERS
from backend.core.services.Credentials.credentialsOrchestrator import save_credentials, load_credentials, \
    clear_credentials


class CreditentialsHandler:
    """Handler générique pour gérer les credentials d'un provider."""

    ACTIONS = {
        "save": save_credentials,
        "load": load_credentials,
        "clear": clear_credentials,
    }

    @staticmethod
    def get_handler(action: str, provider: str):
        """
        Retourne la fonction correspondant à l'action pour le provider.

        :param action: Action à effectuer ('save', 'load', 'clear').
        :param provider: Nom du provider.
        :return: Fonction correspondante ou None si non trouvée.
        """
        if provider not in CONNECTABLE_PROVIDERS:
            raise ValueError(f"Provider '{provider}' non supporté.")
        if action not in CreditentialsHandler.ACTIONS:
            raise ValueError(f"Action '{action}' non supportée.")
        return CreditentialsHandler.ACTIONS[action]