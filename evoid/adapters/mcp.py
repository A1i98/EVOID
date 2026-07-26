"""MCP Adapter — Expose Intents as MCP tools for AI agents.

IOP: MCP adapter converts Intents to MCP tool format.
AI agents can discover, understand, and invoke Intents.

Supports MCP protocol via JSON-RPC 2.0:
- tools/list → list all available tools
- tools/call → execute an Intent
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ..core.intent import Intent, Level
from ..core.runtime import execute
from ..core.schema import export_schemas, IntentSchema


# ============================================================
# MCP Data Structures
# ============================================================

@dataclass(frozen=True)
class MCPTool:
    """MCP tool definition — pure data."""
    name: str
    description: str
    input_schema: dict[str, Any]
    intent_name: str
    level: str


@dataclass
class MCPServer:
    """MCP server — exposes Intents as tools."""
    name: str
    tools: dict[str, MCPTool] = field(default_factory=dict)


# ============================================================
# Server Creation
# ============================================================

def create_mcp_server(name: str = "evoid", visible_only: bool = True) -> MCPServer:
    """Create an MCP server from registered Intents.

    Args:
        name: Server name
        visible_only: If True, only expose Intents with mcp_visible=True
    """
    server = MCPServer(name=name)
    schemas = export_schemas()

    for intent_name, schema in schemas.items():
        if visible_only:
            from ..core.intent import resolve
            intent = resolve(intent_name)
            if intent and not intent.metadata.get("mcp_visible", False):
                continue

        tool = _schema_to_tool(schema)
        server.tools[intent_name] = tool

    return server


def _schema_to_tool(schema: IntentSchema) -> MCPTool:
    """Convert IntentSchema to MCPTool."""
    properties = {}
    required = []

    for f in schema.metadata_fields:
        prop: dict[str, Any] = {"type": f.type}
        if f.description:
            prop["description"] = f.description
        if f.default is not None:
            prop["default"] = f.default
        properties[f.name] = prop
        if f.required:
            required.append(f.name)

    input_schema = {
        "type": "object",
        "properties": properties,
        "required": required if required else [],
    }

    return MCPTool(
        name=schema.name,
        description=schema.description,
        input_schema=input_schema,
        intent_name=schema.name,
        level=schema.level,
    )


# ============================================================
# MCP Protocol (JSON-RPC 2.0)
# ============================================================

async def handle_mcp_request(server: MCPServer, request: dict[str, Any]) -> dict[str, Any]:
    """Handle a JSON-RPC 2.0 MCP request.

    Supported methods:
    - tools/list: list all tools
    - tools/call: execute an Intent
    - initialize: handshake
    - ping: health check
    """
    method = request.get("method", "")
    params = request.get("params", {})
    request_id = request.get("id")

    # Build response envelope
    response: dict[str, Any] = {"jsonrpc": "2.0", "id": request_id}

    try:
        if method == "initialize":
            result = {
                "protocolVersion": "2025-03-26",
                "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": {"name": server.name, "version": "1.0.0"},
            }
            response["result"] = result

        elif method == "ping":
            response["result"] = {}

        elif method == "tools/list":
            tools = list_tools(server)
            response["result"] = {"tools": tools}

        elif method == "tools/call":
            tool_name = params.get("name", "")
            arguments = params.get("arguments", {})
            result = await handle_tool_call(server, tool_name, arguments)
            response["result"] = {
                "content": [{"type": "text", "text": str(result)}],
                "isError": False,
            }

        else:
            response["error"] = {
                "code": -32601,
                "message": f"Method not found: {method}",
            }

    except Exception as e:
        response["error"] = {
            "code": -32603,
            "message": str(e),
        }

    return response


# ============================================================
# Tool Operations
# ============================================================

async def handle_tool_call(server: MCPServer, tool_name: str, arguments: dict[str, Any]) -> Any:
    """Handle an MCP tool call by executing the corresponding Intent."""
    tool = server.tools.get(tool_name)
    if tool is None:
        raise ValueError(f"Unknown tool: {tool_name}")

    intent = Intent(
        name=tool.intent_name,
        level=Level(tool.level),
        metadata=arguments,
    )

    result = await execute(intent)

    if result.success:
        return result.value
    else:
        raise result.error


def list_tools(server: MCPServer) -> list[dict[str, Any]]:
    """List all tools in MCP format."""
    tools = []
    for name, tool in server.tools.items():
        tools.append({
            "name": name,
            "description": tool.description,
            "inputSchema": tool.input_schema,
        })
    return tools


def get_tool(server: MCPServer, tool_name: str) -> dict[str, Any] | None:
    """Get a single tool in MCP format."""
    tool = server.tools.get(tool_name)
    if tool is None:
        return None
    return {
        "name": tool.name,
        "description": tool.description,
        "inputSchema": tool.input_schema,
    }
