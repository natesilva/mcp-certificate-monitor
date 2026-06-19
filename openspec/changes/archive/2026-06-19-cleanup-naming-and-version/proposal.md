## Why

The project uses `cert-monitor` as its storage directory name and MCP resource URI scheme — too generic and prone to collision with other tools. The server also reports FastMCP's own version number instead of the project's version, making it impossible to distinguish releases.

## What Changes

- Rename `platformdirs.user_data_dir("cert-monitor")` → `user_data_dir("mcp-certificate-monitor")` in `store.py`
- Rename MCP resource URI scheme from `cert-monitor://` → `mcp-certificate-monitor://` in `server.py` (3 URIs)
- Update test fixtures that assert the old storage path (`cert-monitor/hosts.json`)
- Wire the project version into the `FastMCP(...)` constructor using `importlib.metadata.version("mcp-certificate-monitor")` so `pyproject.toml` remains the single source of truth

## Capabilities

### New Capabilities

- None

### Modified Capabilities

- `host-store`: storage directory path changes from `cert-monitor` to `mcp-certificate-monitor`
- `mcp-resources`: resource URI scheme changes from `cert-monitor://` to `mcp-certificate-monitor://`

## Impact

- `src/mcp_certificate_monitor/store.py`: storage path string
- `src/mcp_certificate_monitor/server.py`: 3 resource URI decorators + FastMCP constructor
- `tests/test_store.py`, `tests/test_server.py`: path assertions in fixtures
- No dependency changes; `importlib.metadata` is stdlib
- No migration needed — pre-1.0, not published, no existing deployments
