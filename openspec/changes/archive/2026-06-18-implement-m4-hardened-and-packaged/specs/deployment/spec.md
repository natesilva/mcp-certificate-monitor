# Deployment

## Purpose

Defines requirements for packaging and deploying the MCP Certificate Monitor server, including the installable entry point and Claude Desktop integration configuration.

## ADDED Requirements

### Requirement: Package entry point
The system SHALL define a console script entry point `mcp-certificate-monitor` in `pyproject.toml` that resolves to a `main()` function in `mcp_certificate_monitor/__init__.py`. The `main()` function SHALL call `mcp.run()` to start the FastMCP server. Running `uv run mcp-certificate-monitor` SHALL launch the server without additional arguments.

#### Scenario: Entry point resolves and runs
- **WHEN** `uv run mcp-certificate-monitor` is executed in the project directory
- **THEN** the FastMCP server starts and listens for MCP connections without error

#### Scenario: main() is importable
- **WHEN** `from mcp_certificate_monitor import main` is executed
- **THEN** a callable `main` is returned without error

### Requirement: Claude Desktop configuration
The `README.md` SHALL document how to wire the server into Claude Desktop by adding a `cert-monitor` entry to `claude_desktop_config.json`. The documented configuration SHALL use `uv` as the command with `["run", "mcp-certificate-monitor"]` as args, enabling zero-install usage from the project directory.

#### Scenario: README contains Claude Desktop JSON
- **WHEN** `README.md` is read
- **THEN** it contains a JSON snippet showing a `cert-monitor` MCP server entry with `"command": "uv"` and `"args": ["run", "mcp-certificate-monitor"]`
