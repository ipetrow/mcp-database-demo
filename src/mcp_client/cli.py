import argparse
import pathlib

def parse_args():
    """
    Parses the command-line arguments.

    Returns:
        argparse.Namespace: Parsed command-line arguments containing the attributes defined by the argument parser.
    """

    parser = argparse.ArgumentParser("Simple MCP Client")
    parser.add_argument(
        "server_script_path",
        type=pathlib.Path,
        help="the MCP Server script path",
    )

    return parser.parse_args()

