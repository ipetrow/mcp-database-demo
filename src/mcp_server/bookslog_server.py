import sqlite3
from typing import List, Tuple
from mcp.server.fastmcp import FastMCP

DATABASE_NAME = "booklog"
DATABASE = f"{DATABASE_NAME}.db"

# Initialize FastMCP server
mcp = FastMCP(DATABASE_NAME)

@mcp.tool()
def get_books() -> List[Tuple[int, str, str, str, int]]:
    """
    Gets all the books from the database.

    Returns:
        A list with all the books in the database.
    """

    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()

    query = "SELECT * FROM books"

    table_list = [row for row in cur.execute(query)] 

    conn.commit()
    conn.close()

    return table_list

@mcp.tool()
def get_books_titles() -> List[str]:
    """
    Gets all the book titles from the database.

    Returns:
        A list with all the book titles in the database.
    """

    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()

    query = "SELECT title FROM books"

    table_list = [row[0] for row in cur.execute(query)] 

    conn.commit()
    conn.close()

    return table_list

@mcp.tool()
def insert_book(
        isbn: int,
        title: str,
        author: str,
        pages_num: int
) -> None:
    """
    Insert new book in the database.

    Args:
        isbn: The book's ISBN.
        title: The book's title.
        author: The book's author.
        pages_num: The books's number of pages.

    Returns:
        None
    """

    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()

    query="""
        INSERT INTO books (
            isbn, title, author, pages_num
        ) VALUES (?, ?, ?, ?)
    """

    cur.execute(query, (isbn, title, author, pages_num))

    conn.commit()
    conn.close()

@mcp.tool()
def delete_book(
        title: str
) -> None:
    """
    Deletes book with specified title.

    Args:
        title: The book's title.

    Returns:
        None
    """

    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()

    query="""
        DELETE FROM books 
        WHERE title = ?
    """

    cur.execute(query, (title,))

    conn.commit()
    conn.close()

@mcp.tool()
def update_book_title(
        isbn: int,
        title: str
) -> None:
    """
    Updates book data.

    Args:
        isbn: The book's ISBN.
        title: The book's title.

    Returns:
        None
    """

    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()

    query = """
        UPDATE books 
        SET title = ? 
        WHERE isbn = ?
    """

    cur.execute(query, (title, isbn))

    conn.commit()
    conn.close()

if __name__ == "__main__":
    mcp.run(transport="stdio")