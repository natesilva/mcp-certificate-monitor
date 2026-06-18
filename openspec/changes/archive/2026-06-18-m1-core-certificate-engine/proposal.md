## Why

The MCP Certificate Monitor needs a reliable, testable foundation for SSL/TLS certificate inspection and persistent host tracking before any MCP tooling can be built on top of it. M1 delivers the two core modules — `cert.py` and `store.py` — that all subsequent milestones depend on.

## What Changes

- Introduce `cert.py`: connects to a host via stdlib `ssl`/`socket`, retrieves the peer certificate, and returns a validated `CertResult` Pydantic model with parsed fields (subject, issuer, SANs, validity dates, days remaining, serial number).
- Introduce `store.py`: reads and writes `hosts.json` via `platformdirs.user_data_dir("cert-monitor")`, exposes a `HostStore` Pydantic model with host CRUD, and performs atomic file writes to prevent corruption.
- Add `CertResult` and `MonitoredHost`/`HostStore` Pydantic models used by both modules and later by `server.py`.
- Wire up the `src/mcp_certificate_monitor/__init__.py` package entry point.
- Write pytest tests covering `cert.py` and `store.py` (happy paths, error returns, and edge cases).

## Capabilities

### New Capabilities

- `certificate-fetching`: Live SSL/TLS certificate retrieval and X.509 field parsing for a given domain and port, returning a structured result or a graceful error value.
- `host-store`: JSON-backed persistent storage of monitored hosts with Pydantic validation, CRUD operations, and atomic writes.

### Modified Capabilities

<!-- None — this is the initial implementation; no existing specs to delta. -->

## Impact

- **New files**: `src/mcp_certificate_monitor/cert.py`, `src/mcp_certificate_monitor/store.py`, `src/mcp_certificate_monitor/__init__.py`
- **Dependencies**: `fastmcp`, `pydantic`, `cryptography` (DN normalization), `platformdirs` (data directory) — all declared explicitly in `pyproject.toml`
- **No breaking changes** — nothing exists yet in implementation
