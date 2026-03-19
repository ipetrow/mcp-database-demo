
async def start_chat_session(handler) -> None:
    """
    Starts an interactive chat session.

    Args:
        handler: The handler for processing the queries.
    """
    
    print("\nMCP Client Started!")
    print("Type your queries or 'quit' to exit.")

    while True:
        try:
            query = input("\nQuery: ").strip()

            if query.lower() == "quit":
                break

            response = await handler.process_query(query)
            print("\n" + response)
        except Exception as e:
            print(f"\nError: {str(e)}")

    print("\nHave a good day!")