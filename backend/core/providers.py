from backend.core.models.Email import Provider

CONNECTABLE_PROVIDERS = (Provider.GMAIL.value, Provider.OUTLOOK.value)

LIST_PROVIDERS = (Provider.GMAIL.value, Provider.OUTLOOK.value, Provider.ALL.value)

DEFAULT_PROVIDER = Provider.GMAIL.value

MSG_UNAUTHENTICATED = "Non authentifié"
MSG_INVALID_PROVIDER = "Provider invalide"
MSG_PROVIDER_REQUIRED = "Provider requis (gmail ou outlook)"
