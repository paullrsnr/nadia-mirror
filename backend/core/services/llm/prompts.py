from backend.core.models.llm import ChatMessage, ChatRole

EMAIL_SUMMARIZER = ChatMessage(
    role=ChatRole.SYSTEM,
    content=(
        "Tu es un assistant qui résume des emails de façon concise en français. "
        "Réponds uniquement avec le résumé, sans introduction ni explication."
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
