# MCP Certificate Monitor

Monitor SSL/TLS certificate expiry across your domains by asking Claude — no dashboards, no command-line tools.

## Prerequisites

- [uv](https://docs.astral.sh/uv/) installed
- [Claude Desktop](https://claude.ai/download) installed

## Setup

**1. Add the server to your Claude Desktop config**

Open the Claude Desktop configuration file:

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

Add the following:

```json
{
  "mcpServers": {
    "cert-monitor": {
      "command": "uvx",
      "args": ["mcp-certificate-monitor"]
    }
  }
}
```

`uvx` downloads and runs the package automatically — no cloning or installation step needed.

**2. Restart Claude Desktop**

After saving the config file, restart Claude Desktop. The server starts automatically when Claude needs it.

**3. Verify the connection**

Open a new conversation in Claude Desktop and ask:

> What certificate monitoring tools do you have available?

Claude should describe the tools exposed by this server (check certificate, add host, scan all, etc.).

## Alternative: run from source

If you prefer to run from a local clone:

```bash
git clone https://github.com/natesilva/mcp-certificate-monitor
cd mcp-certificate-monitor
```

Then use this config instead:

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

## Documentation

- [What it does and example conversations](https://github.com/natesilva/mcp-certificate-monitor/blob/main/docs/overview.md)
- [Tool, resource & prompt reference](https://github.com/natesilva/mcp-certificate-monitor/blob/main/docs/reference.md)
