from contextlib import AsyncExitStack
from typing import ClassVar, Self

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

class MCPClient:
    """A MCP Client to communicate with a MCP Server."""

    client_session: ClassVar[ClientSession]

    def __init__(self, server_script_path: str):
        self.server_script_path = server_script_path
        self.exit_stack = AsyncExitStack()
        
    async def _connect_to_server(self, server_script_path: str):
        """
        Connects the MCP Client to the MCP Server.

        Args: 
            server_script_path: The relative path to the server script containing the tools, prompts, resources. 
        """
        
        server_params = StdioServerParameters(
            command="python",
            args=[server_script_path],
            env=None
        )

        try:
            stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
            self.stdio, self.write = stdio_transport
            self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))

            await self.session.initialize()
        except Exception:
            raise RuntimeError("Error trying to connect to MCP Server")

        async def __aenter__(self) -> Self:
            cls = type(self)
            cls.client_session = await self._connect_to_server()
            return self

        async def __aexit__(self, *_) -> None:
            await self.exit_stack.aclose()

    async def list_available_tools(self) -> None:
        """Lists the available tools provided by the MCP Server"""

        response = self.session.list_tools()
        tools = response.tools
        print("\nMCP Server available tools:", [tool.name for tool in tools])

    