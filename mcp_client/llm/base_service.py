from abc import ABC, abstractmethod
from mcp import ClientSession

class LLMService(ABC):

    @abstractmethod
    async def process(self, query: str, client_session: ClientSession) -> str:
        pass