import sys
from datetime import datetime

# Use the FastMCP bundled with the `mcp` SDK (1.x) rather than the standalone
# `fastmcp` package: fastmcp 4.x requires mcp 2.x, but langchain-mcp-adapters
# 0.3.2 only works with mcp 1.x.
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Time Server")

@mcp.tool()

def current_time():

    """Return the current date and time."""

    return datetime.now().strftime(
        "%d-%m-%Y %H:%M:%S"
    )


import random

@mcp.tool()

def roll_dice():

    """Roll a six-sided dice."""

    return random.randint(1,6)

import secrets
import string

@mcp.tool()

def generate_password(length: int = 12):

    """
    Generate a secure password.
    """

    alphabet = (
        string.ascii_letters
        + string.digits
        + string.punctuation
    )

    return "".join(
        secrets.choice(alphabet)
        for _ in range(length)
    )

if __name__ == "__main__":
    # stdout is the JSON-RPC channel for the stdio transport; log to stderr only.
    print("Starting MCP server..", file=sys.stderr)
    mcp.run()
