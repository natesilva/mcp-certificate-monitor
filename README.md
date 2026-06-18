# MCP Certificate Monitor

A FastMCP server that lets an AI host monitor SSL/TLS certificate expiry across a set of domains.

## Features

- **Tools**: Check live certificates, add/remove monitored hosts, scan all hosts in parallel, get an expiry report
- **Resources**: Read stored host state and expiry reports without making live network calls
- **Prompts**: Structured templates for certificate audits and renewal planning

## Running with uv

```bash
uv run mcp-certificate-monitor
```

## Claude Desktop Integration

Add the following to your Claude Desktop config file:

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "cert-monitor": {
      "command": "uv",
      "args": ["run", "mcp-certificate-monitor"],
      "cwd": "/path/to/mcp-certificate-monitor"
    }
  }
}
```

Replace `/path/to/mcp-certificate-monitor` with the absolute path to this project directory.

## Development

```bash
# Install dependencies
uv sync

# Run tests
uv run pytest

# Launch the MCP Inspector (interactive browser UI)
uv run fastmcp dev src/mcp_certificate_monitor/server.py
```
