import json
import subprocess
import sys
from pathlib import Path


class MCPClientError(RuntimeError):
    pass


def call_mcp_tool(tool_name: str, arguments: dict | None = None) -> str:
    """
    Appelle un outil MCP local expose par mcp_server/server.py via JSON-RPC stdio.
    """
    arguments = arguments or {}
    server_path = Path(__file__).resolve().parents[3] / "mcp_server" / "server.py"

    messages = [
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "clientInfo": {"name": "medical-multiagents", "version": "0.1.0"},
                "capabilities": {},
            },
        },
        {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {"name": tool_name, "arguments": arguments},
        },
    ]

    payload = "\n".join(json.dumps(message) for message in messages) + "\n"

    try:
        process = subprocess.Popen(
            [sys.executable, str(server_path)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
        )
        stdout, stderr = process.communicate(payload, timeout=8)
    except Exception as exc:
        raise MCPClientError(f"Impossible d'appeler le serveur MCP: {exc}") from exc

    if process.returncode not in (0, None):
        raise MCPClientError(stderr.strip() or "Erreur MCP inconnue")

    responses = [json.loads(line) for line in stdout.splitlines() if line.strip()]
    tool_response = next((item for item in responses if item.get("id") == 2), None)

    if not tool_response or "error" in tool_response:
        error = tool_response.get("error") if tool_response else "Aucune reponse MCP"
        raise MCPClientError(str(error))

    content = tool_response.get("result", {}).get("content", [])
    return content[0].get("text", "") if content else ""
