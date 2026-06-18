## Context

M1–M3 delivered a fully functional FastMCP server (`cert.py`, `store.py`, `server.py`) with five tools, three resources, and two prompts. The server is runnable via `fastmcp dev` but has no installable entry point, no input validation in server tools, and the `cert-monitor://report` resource listed in the original plan was never implemented. M4 closes these gaps to make the package production-ready.

## Goals / Non-Goals

**Goals:**
- Add a `[project.scripts]` entry to `pyproject.toml` so `uv run mcp-certificate-monitor` launches the server
- Add domain and port input validation in server tools (before hitting the store)
- Add the `cert-monitor://report` resource to complete the planned resource surface
- Document Claude Desktop configuration in `README.md`
- Extend test coverage for new validation and the report resource

**Non-Goals:**
- Rate limiting, authentication, or multi-user support
- Changing the storage format or adding a database
- Adding new tools or prompts beyond the original plan

## Decisions

### Entry point: `uv_build`-compatible scripts entry

Add to `pyproject.toml`:
```toml
[project.scripts]
mcp-certificate-monitor = "mcp_certificate_monitor:main"
```

`__init__.py` already re-exports the `mcp` FastMCP instance; we add a `main()` function there that calls `mcp.run()`. This is the standard FastMCP pattern and requires no new dependencies.

Alternative considered: exporting a `__main__.py` module. Rejected — `uv run` resolves scripts entries directly; a `__main__.py` only applies to `python -m <package>`, not the `uv run <script>` form.

### Input validation: in server tools, not in store

Validation (empty domain, domain too long, invalid port) lives in server tool functions rather than `store.py`. Rationale: store functions are internal utilities; the server layer is the system boundary where external input (from an AI host) arrives. Keeping validation in server tools avoids coupling the store to MCP-specific error semantics.

Validation rules:
- `domain`: must be non-empty and ≤ 253 characters (RFC 1035 max hostname length)
- `port`: must be an integer in range 1–65535

Raise `ValueError` with a descriptive message on any violation. FastMCP converts `ValueError` to a well-formed MCP error response, so the AI host sees a readable error rather than a crash.

### cert-monitor://report resource

Add `@mcp.resource("cert-monitor://report")` to `server.py` that returns the same JSON payload as `get_expiry_report()` but as a resource (string response, not a tool call). Reuse the existing bucketing logic. This matches the plan.md and gives the AI host a read-only path to the report without invoking a tool.

## Risks / Trade-offs

- **Domain validation is intentionally minimal**: RFC 5321 hostname validation is complex. We only check non-empty and max-length, not label structure. A user can still add a malformed domain like `foo..bar`; the certificate fetch will fail and store a `CertResult` with `error` set. This is the correct behavior — the error path is well-tested and surfaces cleanly.
- **`mcp.run()` blocks**: `FastMCP.run()` is a blocking call; it must be the last statement in `main()`. This is expected for a CLI entry point.
- **`cert-monitor://report` duplicates tool logic**: The report resource and `get_expiry_report` tool share bucketing logic. They are kept as separate functions (not shared helper) to avoid coupling resource and tool lifecycles. If the logic diverges in the future, they can evolve independently.
