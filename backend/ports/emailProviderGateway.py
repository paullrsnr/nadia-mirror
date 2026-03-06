from abc import ABC, abstractmethod

from backend.ports.emailProvider import EmailProvider


class EmailProviderGateway(ABC):
    @abstractmethod
    def create(self, provider: str) -> EmailProvider: ...
