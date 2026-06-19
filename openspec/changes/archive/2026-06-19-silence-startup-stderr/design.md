## Context

FastMCP outputs two things to stderr on every startup via stdio transport:
1. An ASCII art banner with server name, version, and a "Deploy free" advertisement — rendered via `rich.console.Console(stderr=True)` in `fastmcp/utilities/cli.py`
2. An INFO-level log message `"Starting MCP server 'Certificate Monitor' with transport 'stdio'"` — emitted via FastMCP's `fastmcp` logger, which is wired to `RichHandler(console=Console(stderr=True))`

MCP clients using stdio transport share stderr with the server process. Noise on stderr is often surfaced to the user as errors or warnings. Both outputs are benign in a terminal context but problematic for embedded use.

FastMCP exposes first-class controls for both:
- `mcp.run(show_banner=False)` suppresses the banner (also readable from `FASTMCP_SHOW_SERVER_BANNER`)
- The `fastmcp` Python logger can be raised to `WARNING` to suppress INFO-level startup messages

## Goals / Non-Goals

**Goals:**
- Eliminate all FastMCP stderr output during normal stdio startup
- Require no configuration from the deployer (silent by default)
- Preserve WARNING and ERROR log output (useful for genuine problems)

**Non-Goals:**
- Silencing HTTP transport startup output (different context, banner is fine there)
- Configuring a log file or alternative log sink
- Changing FastMCP defaults (we control only our entry point)

## Decisions

**D1: Suppress the banner via `show_banner=False` in `main()`**

`mcp.run()` accepts `show_banner=False` directly. This is the blessed API — no monkey-patching or env vars required at the call site.

Alternative considered: `FASTMCP_SHOW_SERVER_BANNER=false` as an env var in the Claude Desktop config. Rejected because it requires deployer action and is invisible to users who install the package without reading the README.

**D2: Suppress INFO logs by raising the `fastmcp` logger to `WARNING` in `main()`**

```python
import logging
logging.getLogger("fastmcp").setLevel(logging.WARNING)
```

This is done after FastMCP is imported (FastMCP configures its logger at import time, but `setLevel` overrides that). We preserve the handler wiring so that genuine WARNING/ERROR messages still reach stderr.

Alternative considered: `FASTMCP_LOG_ENABLED=false` (disables all FastMCP logging). Rejected — too blunt; we still want warnings and errors to surface.

Alternative considered: `FASTMCP_LOG_LEVEL=WARNING` env var. Rejected for the same reason as D1 — requires deployer action.

## Risks / Trade-offs

- **Lost "server started" confirmation** → Acceptable: the server is confirmed running when the MCP client completes the initialize handshake. The log message adds no operational value in stdio mode.
- **Harder to debug startup issues** → Mitigation: users can set `FASTMCP_LOG_LEVEL=DEBUG` externally if they need verbose output; our `setLevel` call only raises the floor to WARNING, it doesn't disable the handler.
