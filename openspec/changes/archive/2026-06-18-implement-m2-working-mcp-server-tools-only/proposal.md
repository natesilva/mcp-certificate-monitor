## Why

M1 delivered the core certificate engine (`cert.py`, `store.py`) but nothing is yet exposed to an AI host. M2 wires those modules into a FastMCP server with five tools so that an AI can add domains, check certificates, scan all hosts, remove hosts, and read an expiry report — making the server functional end-to-end for the tools-only milestone.

## What Changes

- Introduce `server.py`: FastMCP app with five tools registered — `check_certificate`, `add_monitored_host`, `remove_host`, `scan_all`, and `get_expiry_report`.
- `check_certificate` performs a live cert fetch without mutating stored state.
- `add_monitored_host` adds a domain to the store and immediately fetches its certificate.
- `remove_host` removes a domain from the store.
- `scan_all` checks every monitored host in parallel (via `ThreadPoolExecutor`) and updates stored results.
- `get_expiry_report` buckets stored (not live) results into `critical` (≤14 days or errored), `warning` (15–30 days), and `ok` (>30 days) with a `generated_at` timestamp.
- Update `__init__.py` to re-export the FastMCP `mcp` app instance so `uv run mcp-certificate-monitor` works.
- Add pytest tests covering all five tools (happy paths, error paths, edge cases).

## Capabilities

### New Capabilities
- `mcp-tools`: FastMCP server with five tools for live certificate checking and host management; the primary interface between an AI host and the certificate monitoring system.

### Modified Capabilities
<!-- None — server.py does not yet exist; no existing specs are affected. -->

## Impact

- **New files**: `src/mcp_certificate_monitor/server.py`
- **Modified files**: `src/mcp_certificate_monitor/__init__.py` (re-export `mcp` app), `pyproject.toml` (add `[project.scripts]` entry point)
- **Dependencies**: No new runtime dependencies; `fastmcp` and `pydantic` are already declared
- **No breaking changes** — `cert.py` and `store.py` APIs are unchanged
