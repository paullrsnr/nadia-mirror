# pylint: disable=invalid-name
"""Ports LLM : autant de ports et d'adapters que de modèles.

Chaque modèle a son port (réveil moteur + interface) et son adapter (récupère tout ça).
"""
from backend.ports.llm.port import LLMProvider

__all__ = ["LLMProvider"]
