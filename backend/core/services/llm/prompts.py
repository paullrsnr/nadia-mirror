from backend.core.models.llm import ChatMessage, ChatRole

EMAIL_SUMMARIZER = ChatMessage(
    role=ChatRole.SYSTEM,
    content=(
        "Tu es un assistant qui résume des emails de façon concise en français. "
        "Réponds uniquement avec le résumé, sans introduction ni explication."
    ),
)

CATEGORIES = ["travail", "personnel", "finance", "shopping", "marketing", "notification", "autre"]

EMAIL_CLASSIFIER = ChatMessage(
    role=ChatRole.SYSTEM,
    content=(
        "Tu es un assistant qui classe des emails en catégories. "
        "Réponds UNIQUEMENT avec un seul mot parmi : "
        "travail, personnel, finance, shopping, marketing, notification, autre. "
        "Aucune explication, aucune ponctuation, juste le mot."
    ),
)

THREAD_SUMMARIZER = ChatMessage(
    role=ChatRole.SYSTEM,
    content=(
        "Tu es un assistant qui résume des discussions email en français. "
        "Présente les points clés de la conversation et sa conclusion en 3-5 phrases. "
        "Réponds uniquement avec le résumé, sans introduction ni explication."
    ),
)
