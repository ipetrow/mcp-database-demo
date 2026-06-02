import json
import os
from mcp import ClientSession
from openai import OpenAI

from mcp_client.llm.base_service import LLMService

MODEL = "" # TODO add respective model name
MAX_TOKENS = 1000
ENDPOINT = "" # TODO add azure endpoint
MAX_STEPS = 5 # maximum agentic loop iterations

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

        # context history
        context = [
            {
                "role": "user", 
                "content": [
                    {
                        "type": "input_text",
                        "text": str(query),
                    }
                ]
            }
        ]

        available_tools = await self._get_available_tools(client_session)
        final_result = []

        for _ in range(MAX_STEPS):

            tool_outputs = []
            has_function_call = False # agentic loop termination flag

            # Initial OpenAI API call
            response = self.openai.responses.create(
                model=MODEL, 
                max_output_tokens=MAX_TOKENS, 
                input=context,
                tools=available_tools
            )

            print("DEBUG: >>>>>>>>>>>")

            # hadle all output items
            for output_item in response.output:

                # handle text/message if present
                if output_item.type == "message":
                    output_text_parts = []

                    for content_item in output_item.content: # if the response contains multiple "output_text" items
                        if content_item.type == "output_text":
                            output_text_parts.append(content_item.text)

                    if output_text_parts:
                        assisstent_text = "\n".join(output_text_parts)

                        final_result.append(assisstent_text)

                        context.append(
                            {
                                "role": "assistant",
                                "content": assisstent_text
                            }
                        )
                elif output_item.type == "function_call": # handle a tool call request if present
                    has_function_call = True

                    context.append(
                        {
                            "type": "function_call",
                            "call_id": output_item.call_id, 
                            "name": output_item.name,
                            "arguments": output_item.arguments or {}
                        }
                    )

                    tool_result = await self._execute_tool(output_item, client_session)
                    final_result.append(tool_result["log"])
                    tool_outputs.append(tool_result["message"])

            if not has_function_call: # no function calls - agentic loop termination
                break

            context.extend(tool_outputs)

        else:
            raise RuntimeError("The maximum allowed interactions with the agent has been reached!") 

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

    async def _execute_tool(self, tool_item, client_session: ClientSession) -> dict:
        """
        Executes a tool by specified name and attributes.
        
        Args:
            tool_name: The name of the tool that will be executed.
            tool_args: The required arguments of the tool that will be executed.
            client_session: The mcp client session.
        Returns:
            A dictionary containing logs and the tool execution message.
        """

        tool_name = tool_item.name
        tool_args = json.loads(tool_item.arguments or "{}")

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
                "type": "function_call_output",
                "call_id": tool_item.call_id,
                "output": content
            }
        }