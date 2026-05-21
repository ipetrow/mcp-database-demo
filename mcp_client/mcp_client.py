from contextlib import AsyncExitStack
from typing import Self, Optional

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from mcp_client.llm.base_service import LLMService

class MCPClient:
    """A MCP Client to communicate with a MCP Server."""

    def __init__(self, server_path: str, model_service: LLMService):
        self.session: Optional[ClientSession] = None
        self.server_path = server_path
        self.model_service = model_service
        self.exit_stack = AsyncExitStack()
        
    async def _connect_to_server(self) -> ClientSession:
        """
        Connects the MCP Client to the MCP Server.

        Args: 
            server_path: The relative path to the server file path containing the tools, prompts, resources. 
        """
        
        server_params = StdioServerParameters(
            command="uv",
            args=["run", self.server_path],
            env=None
        )

        try:
            stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
            self.stdio, self.write = stdio_transport
            client_session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))

            await client_session.initialize()
            return client_session
        except Exception as e:
            raise RuntimeError(f"Error trying to connect to MCP Server {self.server_path}: {e}")
    
    async def __aenter__(self) -> Self:
            self.session = await self._connect_to_server()
            await self._list_available_tools()
            return self

    async def __aexit__(self, *_) -> None:
        await self.exit_stack.aclose()

    async def process(self, query: str) -> str:
        """
        Processes a query.
        
        Args:
            query: A query provided by the User.

        Returns:
            A string representing the history of all exchanged messages for processing the query (e.g., logs, final answer).
        """

        if not self.session:
            raise RuntimeError("There isn't an active mcp client session!")
        
        return await self.model_service.process(query, self.session)

    async def _list_available_tools(self) -> None:
        """Lists the available tools provided by the MCP Server."""

        try:
             tools_response = await self.session.list_tools()
             if tools_response and tools_response.tools:
                print("\nMCP Server available tools:", [tool.name for tool in tools_response.tools])
        except Exception as e:
            print(f"Error {e}")