from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

from backend.core.models.llm.chatMessage import ChatMessage


class LlmPort(ABC):

    @abstractmethod
    def is_available(self) -> bool:
        ...

    @abstractmethod
    def load_model(self, model_path: Path) -> bool:
        ...

    @abstractmethod
    def unload_model(self) -> None:
        ...

    @abstractmethod
    def is_loaded(self) -> bool:
        ...

    @abstractmethod
    def get_loaded_model_path(self) -> Optional[Path]:
        ...

    @abstractmethod
    def get_short_answer(self, messages: list[ChatMessage]) -> str:
        ...
