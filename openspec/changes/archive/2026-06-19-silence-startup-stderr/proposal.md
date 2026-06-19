## Why

FastMCP writes an ASCII art banner and an INFO-level startup log message to stderr, which MCP clients using stdio transport may interpret as errors. MCP servers should be silent on stderr by default.

## What Changes

- `main()` passes `show_banner=False` to `mcp.run()` to suppress the FastMCP banner
- `main()` raises the `fastmcp` logger threshold to `WARNING` before running, suppressing the "Starting MCP server..." INFO message
- No user-facing behavior changes; tools, resources, and prompts are unaffected

## Capabilities

### New Capabilities
<!-- none -->

### Modified Capabilities
- `deployment`: Entry point startup behavior changes — stderr is now silent

## Impact

- `src/mcp_certificate_monitor/__init__.py`: `main()` modified
- No new dependencies
- No API or protocol changes
