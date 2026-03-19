import os
import json

from mcp import ClientSession
from openai from OpenAI

MODEL = ""
MAX_TOKENS = 1000

class OpenAIQueryHandler:
    """TODO"""

    def __init__(self, client_session: ClientSession):
        self.client_session = client_session

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError(
                "OPENAI_API_KEY environment variable is empty."
            )
        self.openai = OpenAI(api_key=api_key)

    async def process_query(self, query: str) -> str:
        """
        Process query using OpenAI Chat Completions and available tools.
        
        Args:
            query: A query provided by the User.

        Returns:
            A string representing the history of all exchanged messages for processing the query (e.g., logs, final answer).
        
        """

        messages = [{"role": "user", "content": query}]

        # Initial OpenAI API call
        initial_response = self.openai.chat.completions.create(
            model=MODEL, 
            max_tokens=MAX_TOKENS, 
            messages=messages, 
            tools=await self._get_available_tools()
        )

        response_message = initial_response.choices[0].message
        final_result = []

        # Appends the model message content if present
        response_message_content = response_message.content
        if response_message_content:
            final_result.append(response_message_content)
        
        # Handles a tool call request if present
        if tool_calls := response_message.tool_calls:
            messages.append(
                {
                    "role": "assistant",
                    "content": response_message_content or "",
                    "tool_calls": tool_calls,
                }
            )

            # Executes all tool calls
            for tool_call in tool_calls:
                tool_result = await self._execute_tool(tool_call)
                final_result.append(tool_result["log"])
                messages.append(tool_result["message"])

            # Gets the final model's response after providing it with tool execution response
            final_response = self.openai.chat.completions.create(
                model=MODEL,
                max_tokens=MAX_TOKENS,
                messages=messages
            )

            if content := final_response.choices[0].message.content:
                final_result.append(content)

            return "Assistant: " + "\n".join(final_result)

    async def _get_available_tools(self) -> list:
        """
        Gets the available tools provided by the MCP Server.

        Returns:
            A list with all available tools.
        """
        
        tools_response = await self.client_session.list_tools()
        tools = [
            {
                "type": "function",
                "name": tool.name,
                "description": tool.description,
                "parameters": getattr(
                    tool,
                    "inputSchema",
                    {"type": "object", "properties": {}}
                )
            }
            for tool in tools_response.tools
        ]

        return tools
    
    async def _execute_tool(self, tool_call) -> dict:
        """
        Executes a tool by specified name and attributes.
        
        Args:
            tool_call: A tool that will be executed.

        Returns:
            A dictionary containing logs and the tool execution message.
        """

        tool_name = tool_call.function.name
        tool_args = json.loads(tool_call.function.arguments or "{}")

        try:
            result = await self.client_session.call_tool(tool_name, tool_args)
            content = result.content[0].text if result.content else ""
            log = f"[Log: Calling tool {tool_name} with args {tool_args}]]"
        except Exception as e:
            content = f"Error: {e}"
            log = f"[{content}]"

        return {
            "log": log,
            "message": {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": content
            }
        }
