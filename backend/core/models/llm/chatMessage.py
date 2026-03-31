from dataclasses import dataclass

from backend.core.models.llm.chatRole import ChatRole


@dataclass
class ChatMessage:
    role: ChatRole
    content: str

    def to_dict(self) -> dict:
        return {"role": self.role.value, "content": self.content}
