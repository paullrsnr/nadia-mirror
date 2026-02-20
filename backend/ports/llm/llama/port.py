# pylint: disable=invalid-name
"""Port pour le modèle Llama : réveil moteur / cerveau + interface.

L'adapter Llama (adapters/llm/llama/adapter.py) récupère tout ça
et branche la librairie (llama-cpp-python).
"""
from backend.ports.llm.port import LLMProvider

# Port du modèle Llama = même interface que LLMProvider (réveil + contrat)
LlamaPort = LLMProvider
