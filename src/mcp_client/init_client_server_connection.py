import asyncio

from mcp_client.mcp_client import MCPClient
from mcp_client.cli import parse_args


async def main() -> None:
    """Starts the MCP Client."""

    args = parse_args()

    if not args.server_script_path.exists():
        print(f"Error: Server script '{args.server_script_path}' not found")
        return

    try:
        async with MCPClient("./mcp/library_server.py") as client:
            print("Success: Connection to the MCP server is established!")
            await client.list_available_tools()
    except RuntimeError as e:
        print(e)

if __name__ == "__main__":
    asyncio.run(main())