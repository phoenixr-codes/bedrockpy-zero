__all__ = ["CommandParser"]

from abc import ABC, abstractmethod
from .context import Context

class CommandParser(ABC):
    @abstractmethod
    async def parse(
        self,
        ctx: Context,
        string: str
    ) -> None:
        """parse the command input string without the prefix"""

