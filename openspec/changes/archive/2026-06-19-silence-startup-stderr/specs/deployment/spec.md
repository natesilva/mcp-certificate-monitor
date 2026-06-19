## MODIFIED Requirements

### Requirement: Package entry point
The system SHALL define a console script entry point `mcp-certificate-monitor` in `pyproject.toml` that resolves to a `main()` function in `mcp_certificate_monitor/__init__.py`. The `main()` function SHALL call `mcp.run(show_banner=False)` to start the FastMCP server with the startup banner suppressed. Before calling `mcp.run()`, `main()` SHALL raise the `fastmcp` Python logger threshold to `WARNING` to suppress INFO-level startup messages. Running `uv run mcp-certificate-monitor` SHALL launch the server without writing anything to stderr under normal conditions.

#### Scenario: Entry point resolves and runs
- **WHEN** `uv run mcp-certificate-monitor` is executed in the project directory
- **THEN** the FastMCP server starts and listens for MCP connections without error

#### Scenario: main() is importable
- **WHEN** `from mcp_certificate_monitor import main` is executed
- **THEN** a callable `main` is returned without error

#### Scenario: No stderr output on startup
- **WHEN** `uv run mcp-certificate-monitor` is launched via stdio transport
- **THEN** nothing is written to stderr during startup under normal conditions
