from mcp_client.mcp_client import MCPClient

class ChatInterface:

    def __init__(self, client: MCPClient):
        self.client = client

    async def start_session(self):
        """Starts an interactive chat session."""
        
        print("Type your queries or 'quit' to exit.")

        while True:
            try:
                query = input("\nQuery: ").strip()

                if query.lower() == "quit":
                    break

                response = await self.client.process(query)
                print("\n" + response)
            except Exception as e:
                print(f"\nError: {str(e)}")

        print("\nPlease let me know if I can provide further assistance!")
