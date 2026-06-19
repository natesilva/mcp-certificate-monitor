# Development

## Setup

```bash
uv sync
```

## Running Tests

```bash
uv run pytest
```

## MCP Inspector

The FastMCP Inspector provides an interactive browser UI for testing tools, resources,
and prompts without a full AI host:

```bash
uv run fastmcp dev inspector src/mcp_certificate_monitor/server.py
```

This opens the Inspector at `http://localhost:5173` (or the next available port).
Use it to call tools directly, browse resource URIs, and preview prompt output.

## Running the Server Directly

```bash
uv run mcp-certificate-monitor
```

The server speaks the MCP protocol over stdio and is intended to be launched by an
MCP host (such as Claude Desktop). Running it directly in a terminal will show the
server waiting for JSON-RPC input.

## Storage

The server persists monitored hosts to a JSON file managed by
[platformdirs](https://pypi.org/project/platformdirs/). The path depends on the OS:

| Platform | Path |
|---|---|
| macOS | `~/Library/Application Support/mcp-certificate-monitor/hosts.json` |
| Linux | `~/.local/share/mcp-certificate-monitor/hosts.json` |
| Windows | `%LOCALAPPDATA%\mcp-certificate-monitor\hosts.json` |

The directory is created automatically on first write. The file is human-readable JSON
and can be inspected or backed up directly.
