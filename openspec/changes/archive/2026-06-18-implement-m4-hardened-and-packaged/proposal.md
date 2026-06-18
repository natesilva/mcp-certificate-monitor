## Why

M1–M3 delivered a fully functional server, but the package lacks an installable entry point and the tools do not validate inputs or surface errors cleanly to the AI host. M4 completes the project by hardening error paths, adding input validation, wiring up the package entry point for `uv run`, and documenting Claude Desktop configuration.

## What Changes

- Add `[project.scripts]` entry in `pyproject.toml` so `uv run mcp-certificate-monitor` launches the server
- Add domain and port input validation in all server tools (reject empty domain, invalid port range, domain too long)
- Ensure `ValueError` from store operations surfaces as a user-readable MCP error (not a crash)
- Add `get_expiry_report` as a MCP resource at `cert-monitor://report` (referenced in plan but not yet implemented)
- Update `README.md` with Claude Desktop JSON configuration and `uv run` usage
- Add tests covering input validation and error surfacing

## Capabilities

### New Capabilities
- `deployment`: Package entry point (`pyproject.toml` scripts entry) and Claude Desktop configuration spec — defines how the server is installed, launched, and wired into Claude Desktop.

### Modified Capabilities
- `mcp-tools`: Add input validation requirements (domain format, port range) and specify how tool errors (ValueError, store failures) must surface as readable MCP error messages rather than unhandled exceptions.

## Impact

- **Modified files**: `pyproject.toml` (add scripts entry), `src/mcp_certificate_monitor/server.py` (input validation, error surfacing, `cert-monitor://report` resource), `README.md` (Claude Desktop config), `tests/test_server.py` (new validation and error tests)
- **Dependencies**: No new runtime dependencies
- **No breaking changes** — existing tool signatures and resource URIs are unchanged
