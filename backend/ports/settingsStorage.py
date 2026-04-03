from abc import ABC, abstractmethod


class SettingsStorage(ABC):

    @abstractmethod
    def get_setting(self, key: str) -> str | None:
        """Retourne la valeur d'un paramètre, ou None si absent."""

    @abstractmethod
    def set_setting(self, key: str, value: str) -> None:
        """Enregistre ou met à jour un paramètre."""
