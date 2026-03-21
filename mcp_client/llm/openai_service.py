import json
import os
from mcp import ClientSession
from openai import OpenAI

from mcp_client.llm.base_service import LLMService

MODEL = "" # TODO add respective model name
MAX_TOKENS = 1000
ENDPOINT = "" # TODO add azure endpoint

class OpenAIService(LLMService):
    """Handles the communication between the OpenAI Chat Completion API and the MCP tool execution."""

    def __init__(self):
        api_key = os.getenv("AZURE_OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError(
                "AZURE_OPENAI_API_KEY environment variable is empty."
            )
        
        self.openai = OpenAI(
            api_key=api_key,
            base_url=ENDPOINT
        )

    async def process(self, query: str, client_session: ClientSession) -> str:
        """
        Processes query using OpenAI Chat Completions and available tools.
        
        Args:
            query: A query provided by the User.
            client_session: The mcp client session.

        Returns:
            A string representing the history of all exchanged messages for processing the query (e.g., logs, final answer).
        """

        messages = [
            {
                "role": "user", 
                "content": query
            }
        ]

        available_tools = await self._get_available_tools(client_session)

        # Initial OpenAI API call
        initial_response = self.openai.chat.completions.create(
            model=MODEL, 
            max_completion_tokens=MAX_TOKENS, 
            messages=messages, 
            tools=available_tools
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
                    "tool_calls": tool_calls
                }
            )

            # Executes all tool calls
            for tool_call in tool_calls:
                tool_result = await self._execute_tool(tool_call, client_session)
                final_result.append(tool_result["log"])
                messages.append(tool_result["message"])

            # Gets the final model's response after providing it with tool execution response
            final_response = self.openai.chat.completions.create(
                model=MODEL,
                max_completion_tokens=MAX_TOKENS,
                messages=messages
            )

            if content := final_response.choices[0].message.content:
                final_result.append(content)

        return "Assistant: " + "\n".join(final_result)

    async def _get_available_tools(self, client_session: ClientSession) -> list:
        """
        Gets the available tools provided by the MCP Server.

        Args:
            client_session: The mcp client session.

        Returns:
            A list with all available tools.
        """
        
        tools_response = await client_session.list_tools()
        tools = [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": getattr(
                        tool,
                        "inputSchema",
                        {"type": "object", "properties": {}}
                    )
                }
            }
            for tool in tools_response.tools
        ]

        return tools
    
    async def _execute_tool(self, tool_call, client_session: ClientSession) -> dict:
        """
        Executes a tool by specified name and attributes.
        
        Args:
            tool_call: A tool that will be executed.
            client_session: The mcp client session.

        Returns:
            A dictionary containing logs and the tool execution message.
        """

        tool_name = tool_call.function.name
        tool_args = json.loads(tool_call.function.arguments or "{}")

        try:
            log = f"[Log: Calling tool with name = {tool_name} and args = {tool_args}]]"
            result = await client_session.call_tool(tool_name, tool_args)
            content = result.content[0].text if result.content else ""
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