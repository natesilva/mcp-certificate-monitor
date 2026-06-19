# MCP Certificate Monitor

Monitor SSL/TLS certificate expiry across your domains by asking Claude — no dashboards, no command-line tools.

## Prerequisites

- [uv](https://docs.astral.sh/uv/) installed
- [Claude Desktop](https://claude.ai/download) installed

## Setup

**1. Clone this repository**

```bash
git clone https://github.com/natesilva/mcp-certificate-monitor
cd mcp-certificate-monitor
```

**2. Add the server to your Claude Desktop config**

Open the Claude Desktop configuration file:

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

Add the following (replace the path with the absolute path to this directory):

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

**3. Restart Claude Desktop**

After saving the config file, restart Claude Desktop. The server starts automatically when Claude needs it.

**4. Verify the connection**

Open a new conversation in Claude Desktop and ask:

> What certificate monitoring tools do you have available?

Claude should describe the tools exposed by this server (check certificate, add host, scan all, etc.).

## Documentation

- [What it does and example conversations](docs/overview.md)
- [Tool, resource & prompt reference](docs/reference.md)
