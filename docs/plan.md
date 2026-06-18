# MCP Certificate Monitor — Implementation Plan

## Overview

Build an MCP server using FastMCP that lets an AI host monitor SSL/TLS certificate expiry across a set of domains. The server exposes tools for live certificate checks and host management, resources for reading stored state, and prompt templates for structured audit/renewal workflows.

---

## Stack

- **Runtime**: Python 3.14
- **MCP framework**: FastMCP 3.x (already installed)
- **Certificate fetching**: `ssl` + `socket` from stdlib — no third-party HTTP client needed
- **Storage**: JSON file via `platformdirs.user_data_dir("cert-monitor")` (e.g. `~/Library/Application Support/cert-monitor/hosts.json` on macOS, `~/.local/share/cert-monitor/hosts.json` on Linux)

---

## Storage Schema

The JSON file holds the full monitor state. It is read on every request and written on every mutation (no in-memory caching — file is source of truth).

```json
{
  "hosts": {
    "example.com": {
      "domain": "example.com",
      "port": 443,
      "added_at": "2026-06-17T00:00:00Z",
      "last_checked": "2026-06-17T12:00:00Z",
      "last_result": {
        "subject": "CN=example.com",
        "issuer": "CN=Let's Encrypt Authority X3",
        "not_before": "2026-01-01T00:00:00Z",
        "not_after": "2026-09-01T00:00:00Z",
        "days_remaining": 76,
        "serial": "ABC123",
        "san": ["example.com", "www.example.com"],
        "error": null
      }
    }
  }
}
```

`last_result` is `null` until the host has been checked at least once. `error` is a string if the check failed (unreachable, TLS handshake error, etc.); other fields may be absent in that case.

---

## Module Layout

```
src/mcp_certificate_monitor/
├── __init__.py          # re-exports main, mcp
├── server.py            # FastMCP app, tool/resource/prompt registration
├── cert.py              # certificate fetching and parsing
└── store.py             # JSON read/write, host CRUD
```

---

## Data Models

Use Pydantic models. FastMCP already depends on Pydantic, so it costs nothing, and `store.load()` is a system boundary (untrusted data from disk) where validation and automatic datetime coercion are valuable.

```python
# cert.py
class CertResult(BaseModel):
    subject: str
    issuer: str
    not_before: datetime
    not_after: datetime
    days_remaining: int
    serial: str
    san: list[str]
    error: str | None = None

# store.py
class MonitoredHost(BaseModel):
    domain: str
    port: int
    added_at: datetime
    last_checked: datetime | None = None
    last_result: CertResult | None = None

class HostStore(BaseModel):
    hosts: dict[str, MonitoredHost] = {}
```

`store.load()` calls `HostStore.model_validate_json(text)` — Pydantic parses ISO 8601 datetimes automatically and raises a clear `ValidationError` on corrupt data.

---

## `cert.py` — Certificate Fetching

Use `ssl.create_default_context()` + `socket.create_connection()` to open a TLS connection and call `getpeercert()`. This returns a dict with `subject`, `issuer`, `notBefore`, `notAfter`, `subjectAltName`, `serialNumber`.

Key behaviors:
- Connect with a 10-second timeout.
- Parse `notAfter` via `datetime.fromtimestamp(ssl.cert_time_to_seconds(value), tz=timezone.utc)`.
- Compute `days_remaining = (not_after - datetime.now(UTC)).days`.
- On any exception, return a `CertResult` with only `error` set.

---

## `store.py` — Persistent Storage

```python
STORE_PATH = Path(platformdirs.user_data_dir("cert-monitor")) / "hosts.json"

def load() -> dict[str, MonitoredHost]: ...
def save(hosts: dict[str, MonitoredHost]) -> None: ...
def add_host(domain: str, port: int = 443) -> MonitoredHost: ...
def remove_host(domain: str) -> None: ...        # raises KeyError if not found
def update_result(domain: str, result: CertResult) -> None: ...
```

`save()` creates the data directory (via `platformdirs`) if it doesn't exist. Writes atomically: write to a `.tmp` file, then `os.replace()`.

---

## `server.py` — FastMCP Registration

### Tools

#### `check_certificate(domain: str, port: int = 443) -> dict`
Fetches a live certificate for the given host. Does **not** update stored state — purely informational. Returns the `CertResult` as a dict.

#### `add_monitored_host(domain: str, port: int = 443) -> dict`
Adds the host to `hosts.json` (error if already present). Immediately runs a certificate check and stores the result.

#### `remove_host(domain: str) -> str`
Removes the host from `hosts.json`. Returns a confirmation string. Raises a descriptive error if not found.

#### `scan_all() -> list[dict]`
Checks every monitored host in parallel (use `asyncio.gather` or `concurrent.futures.ThreadPoolExecutor` since `ssl`/`socket` is blocking). Updates each result in the store. Returns a list of `{domain, days_remaining, error}` summaries.

#### `get_expiry_report() -> dict`
Reads stored (not live) data and buckets hosts by risk:
- `critical`: ≤14 days or errored
- `warning`: 15–30 days  
- `ok`: >30 days

Returns `{generated_at, critical: [...], warning: [...], ok: [...]}`.

---

### Resources

#### `cert://hosts`
Returns a list of all monitored domains with their port, `added_at`, `last_checked`, and `days_remaining` (from stored result, not live).

#### `cert://host/{domain}`
Returns full stored details for a single host. 404-style error if not found.

#### `cert://report`
Returns the same payload as `get_expiry_report()` but as a resource (read from stored state, not live).

---

### Prompts

#### `cert_audit`
A structured prompt that asks the AI to audit the certificate inventory. It embeds the current `cert://report` resource content and instructs the model to identify risks, flag expiring certs, and ask about any domains that look missing.

#### `renewal_plan`
A prompt that takes the `cert://report` content and asks the AI to produce a prioritized, step-by-step renewal checklist ordered by urgency, with estimated lead time notes for common CAs.

---

## Risk Thresholds

| Label    | Days remaining | Meaning                              |
|----------|----------------|--------------------------------------|
| critical | ≤ 14           | Immediate action needed              |
| warning  | 15 – 30        | Schedule renewal this week           |
| ok       | > 30           | No action required                   |
| error    | N/A            | Could not reach host or parse cert   |

These are module-level constants in `server.py` so they're easy to adjust.

---

## Error Handling

- **Network/TLS failure** on `check_certificate`: return a result with `error` set, not a raised exception. Tools should never crash the MCP session for a single bad host.
- **Host not found** in `remove_host` / `cert://host/{domain}`: raise `ValueError` / return an MCP error response.
- **Corrupt `hosts.json`**: log and treat as empty; do not crash on startup.

---

## Implementation Order

1. `cert.py` — certificate fetching (testable in isolation with `python -c`)
2. `store.py` — JSON persistence with atomic writes
3. `server.py` tools: `check_certificate` → `add_monitored_host` → `remove_host` → `scan_all` → `get_expiry_report`
4. `server.py` resources: `cert://hosts` → `cert://host/{domain}` → `cert://report`
5. `server.py` prompts: `cert_audit` → `renewal_plan`
6. Manual smoke test via `fastmcp dev` (opens the MCP Inspector UI)

---

## Testing the Server Manually

```bash
# FastMCP's built-in inspector (opens a browser UI)
uv run fastmcp dev src/mcp_certificate_monitor/server.py

# Or wire it into Claude Desktop's config:
# ~/Library/Application Support/Claude/claude_desktop_config.json
{
  "mcpServers": {
    "cert-monitor": {
      "command": "uv",
      "args": ["run", "mcp-certificate-monitor"]
    }
  }
}
```
