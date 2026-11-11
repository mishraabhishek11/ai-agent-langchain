import sys
from pathlib import Path

from langchain_mcp_adapters.client import MultiServerMCPClient

# Absolute path so the server is found regardless of the current working directory.
SERVER_PATH = Path(__file__).resolve().parent / "server.py"

client = MultiServerMCPClient(
    {
        "time_server": {
            "transport": "stdio",
            # sys.executable = the interpreter running this app (the venv),
            # not whatever "python" resolves to on PATH (which may lack fastmcp).
            "command": sys.executable,
            "args": [str(SERVER_PATH)],
        }
    }
)
