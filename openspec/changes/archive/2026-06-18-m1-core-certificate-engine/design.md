## Context

The MCP Certificate Monitor is a FastMCP server with no implementation yet. M1 lays the foundation: a certificate-fetching module (`cert.py`) and a persistent host store (`store.py`). Both must be independently testable before MCP tooling is layered on top in M2. The stack is Python 3.12+, FastMCP 3.x, Pydantic, `cryptography`, and `platformdirs` — all declared explicitly in `pyproject.toml`.

## Goals / Non-Goals

**Goals:**
- Implement `cert.py`: blocking TLS connect via stdlib `ssl`/`socket`, `getpeercert()` parsing, `CertResult` Pydantic model, graceful error capture.
- Implement `store.py`: `HostStore`/`MonitoredHost` Pydantic models, `load()`/`save()` with atomic writes, host CRUD (`add`, `remove`, `get`, `list`).
- Wire `__init__.py` to re-export `mcp` and `main` for entry point compatibility (even though `server.py` doesn't exist yet in M1).
- All code importable and testable with a `python -c` one-liner against a real domain.

**Non-Goals:**
- MCP tool/resource/prompt registration — that's M2/M3.
- Async certificate scanning — M2 (`scan_all` tool).
- Caching or in-memory state beyond a single function call.
- Authentication or mTLS support.

## Decisions

### D1 — Use `ssl.create_default_context()` + `socket.create_connection()` (not `requests` or `httpx`)
The plan spec calls this out explicitly. Avoids a third-party HTTP client dep and keeps the TLS handshake transparent. `getpeercert()` returns a stdlib dict with everything we need.

*Alternative*: `cryptography`'s `x509.load_der_x509_certificate` after reading the raw DER bytes. More powerful but overkill — `getpeercert()` + `ssl.cert_time_to_seconds` is sufficient for our fields and avoids DER byte manipulation.

### D2 — Pydantic models for both `CertResult` and `HostStore`
Pydantic is declared as a direct dependency (not relied on as a FastMCP transitive dep). Using models for storage (not raw dicts) gives free ISO 8601 datetime coercion on `load()`, clear `ValidationError` on corrupt JSON, and type safety across the codebase. `store.load()` calls `HostStore.model_validate_json(text)`.

*Alternative*: Plain dataclasses + manual JSON coercion. More code, less validation, inconsistent with the rest of the FastMCP ecosystem.

### D3 — Atomic writes via `tempfile` + `os.replace()`
Write to a `.tmp` sibling file then rename atomically. Prevents a half-written `hosts.json` from corrupting the store if the process is killed mid-write.

*Alternative*: Direct `open("hosts.json", "w")`. Simpler, but risks data loss on crash.

### D4 — `platformdirs.user_data_dir("cert-monitor")` for storage location
Cross-platform: `~/Library/Application Support/cert-monitor/` on macOS, `~/.local/share/cert-monitor/` on Linux. Consistent with the plan spec and avoids hardcoded paths.

### D5 — Custom `_normalize_dn()` for DN normalization (no `cryptography` dep)
`getpeercert()` returns subject/issuer as tuples of tuples. A small `_normalize_dn()` helper walks the RDN tuple and extracts the `commonName` value (falling back to a formatted first RDN if no CN is present). This avoids a third-party dep for a single formatting call.

*Alternative*: `cryptography`'s `x509.Name` formatting. More expressive but adds a dependency for a call we can do with three lines of stdlib iteration.

### D6 — `days_remaining` computed at fetch time, stored as-is
Stored `days_remaining` reflects when the check ran, not today. Tools that need a fresh value re-check live. This keeps the store simple and deterministic.

## Risks / Trade-offs

- **Blocking I/O in cert.py** → `ssl`/`socket` are synchronous. M1 is single-threaded by design; `scan_all` in M2 will use `ThreadPoolExecutor`. Risk: if called naively in async context, it will block the event loop. Mitigation: document that `fetch_certificate()` is blocking; M2 will wrap it with `asyncio.to_thread`.
- **`getpeercert()` only returns leaf cert** → We don't validate the chain depth or parse intermediate certs. Mitigation: acceptable for expiry monitoring; chain issues surface as TLS handshake errors in `error`.
- **Corrupt `hosts.json`** → `model_validate_json` raises `ValidationError`. Mitigation: `store.load()` catches this, logs a warning, and returns an empty `HostStore` to avoid crashing the server.
- **platformdirs data dir may not exist** → `store.save()` calls `data_dir.mkdir(parents=True, exist_ok=True)` before writing.

## Migration Plan

No migration needed — this is a greenfield implementation. No existing data on disk to handle.

## Open Questions

None. The plan doc fully specifies the storage schema, data models, and module layout.
