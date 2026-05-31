# Overview
The repository presents an Agentic AI MCP Client-Server workflow that allows to manipulate a database data by using a natural language.

# Prerequisites
- Installed Python `uv` package and project management tool. A basic understanding of how the tool works would be helpful for a better insight of how the project is set up and executed.
- Installed Python version 3.14.2 or higher.
- An OpenAI API key included in the environment variables.

# Project Details
## Structure
The project consists of 3 main directories. The essence of the MCP demo are `mcp_client` and the `mcp_server`. If the purpose is to only try the example, they are the only ones needed attention.
- `mcp_client`: the Python module includes all the code related to the MCP Client and the integration of the MCP Server and the LLM.
- `mcp_server`: the directory includes the MCP Server related code, the tools definitions and the database itself.- `database` is the third directory. It is a standalone Python module which is used to create the `bookslog.db` file used by the MCP Server. It is included in this project for the purpose of flexibility, allowing to create a new `bookslog.db` with a different or more extensive initial data.

# MCP Server
The MCP Server is created using `FastMCP` with `stdio` as transport layer. It exposes only one primitive type - tools. There are five of them, allowing manipulation of a local database.

## Available Tools
1. `get_books() -> str`: Getting all books.
2. `get_books_titles() -> List[str]`: Getting all book titles.
3. `insert_book(isbn: int, title: str, author: str, pages_num: int) -> None`: Inserting a new book.
4. `delete_book(title: str) -> None`: Delete a book.
5. `update_book_title(isbn: int, title: str) -> None`: Updating a book title by an ISBN.

# Database
It is a simplistic sqlite database named ***bookslog***, consisting of only one table - ***books***. The main idea is to store books information - ***isbn***, ***title***, ***author*** and ***number of pages***. For convenience and simplicity of the demo, a book can have only one author stored as a string.

## Database Creation
The database directory is created as a Python module. It is used for creating the database - `bookslog.db`.

The file is already included in the project and situated in the `mcp_server` directory.

If you would like to experiement and create a new `bookslog.db` the following command should be uesd: 
- Option 1: with `uv` - `uv run python -m database`.
- Option 2: without `uv` - `python -m database`.

**Note**: The command will create the file in the main project directory. It is necessary to move the file to the MCP Server directory.

## Database Data
For the purpose of the demo, sample data is automatically being inserted in the database right after its creation. The data can be manipulated from the `initial_data.py` file.

# Large Language Model
In this example, OpenAI `gpt-5-mini` model is used from Azure - The GPT model was deployed in Azure and the Azure OpenAI API key used for the connection with the LLM. This integration allows the User to interact on an abstract level with the tools exposed from the MCP Server.

## Integration Details
- OpenAI Python API: the library provides access to the OpenAI REST API.
- Chat Completions API: an interface for interacting with the LLM.

# Running the Example
## Setup
1. Clone the repository: `git clone git@github.com:ipetrow/mcp-database-demo.git`.
2. [Optional] Generate a new database with updated data. Ensure to move the newly generated `bookslog.db` file in the `mcp_server` directory.
3. Sync the project in order to download and install all the required project dependencies and they are up to date: `uv sync`. This will create the project virtual environment (`.venv`) as well.
4. Update the model name in `mcp_client/llm/openai_service.py` by providing a value for the `MODEL` constant.
5. Update the Azure endpoint in `mcp_client/llm/openai_service.py` by providing a value for the `ENDPOINT` constant.
6. Double check the OpenAI API key is added in the environment variables. The name of the variable is `OPENAI_API_KEY` and retrieved in `mcp_client/llm/openai_service.py`.

## Execution
Start the MCP Client and connect to the MCP Server by: `uv run python -m mcp_client --server ./mcp_server/sqlite_server.py`.

## Prompt Examples
**Simple Prompts (using single tools)**
- "List all the available books"
- "Update the title of the book with ISBN to 'Book New Title'"
- "Remove the book with a title 'Book Title'"
- "Add a new book with ISBN = 9781408855683, title = 'Harry Potter and the Goblet of Fire', author = 'J.K. Rowling', pages = 640"

**Advanced Prompts**
- "Can you recommend me 3 books that match my interests? For a reference, use the titles in the database."

# References
- Build an MCP server: https://modelcontextprotocol.io/docs/develop/build-server
- Build an MCP client: https://modelcontextprotocol.io/docs/develop/build-client
- Build a Python MCP Client to Test Servers From Your Terminal: https://realpython.com/python-mcp-client/