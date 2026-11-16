
from abc import ABC, abstractmethod

from app.schemas.response import PlatformResult


class BasePlatform(ABC):

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique platform identifier."""
        pass

    @property
    @abstractmethod
    def is_configured(self) -> bool:
        """Check whether platform credentials are available."""
        pass

    @abstractmethod
    async def publish(self, message: str) -> PlatformResult:
        """Publish a message and return a standardized result."""
        pass
