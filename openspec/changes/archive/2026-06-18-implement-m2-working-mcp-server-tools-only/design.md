## Context

M1 delivered `cert.py` (live certificate fetching, `CertResult` model) and `store.py` (JSON-backed host CRUD, `MonitoredHost`/`HostStore` models). The FastMCP framework is already declared as a dependency. M2 wires these modules into a working MCP server by introducing `server.py` with five registered tools.

No new external dependencies are needed. The blocking nature of `ssl`/`socket` I/O means asyncio alone won't provide concurrency for `scan_all`; a thread pool is required.

## Goals / Non-Goals

**Goals:**
- Five working MCP tools: `check_certificate`, `add_monitored_host`, `remove_host`, `scan_all`, `get_expiry_report`
- Parallel host scanning via `ThreadPoolExecutor`
- Risk bucketing constants (`CRITICAL_DAYS = 14`, `WARNING_DAYS = 30`) defined in `server.py`
- Runnable via `uv run fastmcp dev src/mcp_certificate_monitor/server.py`
- Full pytest coverage for all five tools

**Non-Goals:**
- MCP resources (`cert://hosts`, `cert://host/{domain}`, `cert://report`) — M3
- MCP prompts (`cert_audit`, `renewal_plan`) — M3
- Claude Desktop wiring / `[project.scripts]` entrypoint — M4

## Decisions

### FastMCP tool registration with typed parameters
Use `@mcp.tool()` decorator with fully typed function signatures. FastMCP automatically generates the JSON schema from the type hints and docstring, so no separate schema definition is needed.

*Alternative considered*: Raw MCP SDK with manual schema — more boilerplate, no benefit here.

### ThreadPoolExecutor for `scan_all`
`ssl.create_connection()` and `ssl.wrap_socket()` are blocking calls. `asyncio.to_thread` or `concurrent.futures.ThreadPoolExecutor` both work; `ThreadPoolExecutor` is chosen for explicitness and to avoid mixing sync/async in `server.py`.

Use `asyncio.get_event_loop().run_in_executor(None, fetch_certificate, domain, port)` inside an `async def scan_all()` tool so FastMCP can remain async while I/O runs on the default thread pool.

*Alternative considered*: `asyncio.gather` with `asyncio.to_thread` — equivalent but slightly less explicit about the thread pool.

### `check_certificate` is purely informational (no store update)
The tool performs a live fetch but does not call `update_host_result`. This keeps it safe to call for any arbitrary domain at any time, including domains not in the store.

### `add_monitored_host` immediately runs a certificate check
After `add_host()`, `fetch_certificate()` is called and the result is stored via `update_host_result()`. This ensures the host has a populated `last_result` immediately after being added, rather than requiring a separate `scan_all` call.

### Risk thresholds as module-level constants
`CRITICAL_DAYS = 14` and `WARNING_DAYS = 30` are defined at the top of `server.py`. This makes them easy to find and change without hunting through logic.

### `get_expiry_report` reads stored state only
This tool reads `list_hosts()` and classifies based on `last_result.days_remaining`. It does not trigger live fetches. Hosts with `last_result is None` or `last_result.error is not None` are bucketed into `critical`.

## Risks / Trade-offs

- **Thread pool exhaustion**: `scan_all` on a large host list could saturate the default executor. Acceptable for M2 given the monitoring use case; can add `max_workers` cap in M4 if needed.
- **Store load on every tool call**: Each tool calls `load()` which reads `hosts.json` from disk. For a monitoring server with a small host list this is fine; would need caching for high-frequency use.
- **`add_monitored_host` fetch failure**: If the immediate cert fetch fails, the host is still added to the store with a `last_result` containing `error`. This is intentional — the host is monitored even if currently unreachable.
