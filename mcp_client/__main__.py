import asyncio

from mcp_client.mcp_client import MCPClient
from mcp_client.utils.cli import parse_args
from mcp_client.llm.openai_service_responses_api import OpenAIService
from mcp_client.interface import ChatInterface

async def main() -> None:
    """Starts the MCP Client."""

    args = parse_args()

    model = OpenAIService()

    try:
        async with MCPClient(server_path=str(args.server), model_service=model) as client:
            print("Success: Connection to the MCP server is established!")

            chat = ChatInterface(client)
            await chat.start_session()
    except RuntimeError as e:
        print(e)

if __name__ == "__main__":
    asyncio.run(main())