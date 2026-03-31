from pathlib import Path
from typing import Optional

from backend.ports.llm import LlmPort, ChatMessage
from backend.adapters.llm.llama import LlamaCppAdapter


class LlmGatewayAdapter(LlmPort):

    def __init__(self):
        self._adapter: LlmPort = LlamaCppAdapter()

    def is_available(self) -> bool:
        return self._adapter.is_available()

    def load_model(self, model_path: Path) -> bool:
        return self._adapter.load_model(model_path)

    def unload_model(self) -> None:
        self._adapter.unload_model()

    def is_loaded(self) -> bool:
        return self._adapter.is_loaded()

    def get_loaded_model_path(self) -> Optional[Path]:
        return self._adapter.get_loaded_model_path()

    def get_short_answer(self, messages: list[ChatMessage]) -> str:
        return self._adapter.get_short_answer(messages)
