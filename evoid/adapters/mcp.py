"""MCP Adapter — Expose Intents as MCP tools for AI agents.

IOP: MCP adapter converts Intents to MCP tool format.
AI agents can discover, understand, and invoke Intents.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ..core.intent import Intent
from ..core.runtime import execute
from ..core.schema import export_schemas, IntentSchema


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


def create_mcp_server(name: str = "evoid", visible_only: bool = True) -> MCPServer:
    """Create an MCP server from registered Intents.

    Args:
        name: Server name
        visible_only: If True, only expose Intents with mcp_visible=True in metadata
    """
    server = MCPServer(name=name)
    schemas = export_schemas()

    for intent_name, schema in schemas.items():
        # Check visibility
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
    # Build input schema from metadata fields
    properties = {}
    required = []

    for field in schema.metadata_fields:
        prop: dict[str, Any] = {"type": field.type}
        if field.description:
            prop["description"] = field.description
        if field.default is not None:
            prop["default"] = field.default
        properties[field.name] = prop
        if field.required:
            required.append(field.name)

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


async def handle_tool_call(server: MCPServer, tool_name: str, arguments: dict[str, Any]) -> Any:
    """Handle an MCP tool call by executing the corresponding Intent."""
    tool = server.tools.get(tool_name)
    if tool is None:
        raise ValueError(f"Unknown tool: {tool_name}")

    # Build Intent from arguments
    from ..core.intent import Intent, Level

    intent = Intent(
        name=tool.intent_name,
        level=Level(tool.level),
        metadata=arguments,
    )

    # Execute
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
