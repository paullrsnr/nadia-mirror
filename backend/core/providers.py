"""Constantes et règles domaine pour les providers d'email."""
from backend.core.models.Email import Provider

# Providers connectables (excluant "all")
CONNECTABLE_PROVIDERS = (Provider.GMAIL.value, Provider.OUTLOOK.value)

# Providers valides pour liste/sync (incluant "all")
LIST_PROVIDERS = (Provider.GMAIL.value, Provider.OUTLOOK.value, Provider.ALL.value)

# Valeur par défaut
DEFAULT_PROVIDER = Provider.GMAIL.value

# Messages d'erreur domaine
MSG_UNAUTHENTICATED = "Non authentifié"
MSG_INVALID_PROVIDER = "Provider invalide"
MSG_PROVIDER_REQUIRED = "Provider requis (gmail ou outlook)"
