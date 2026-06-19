# Architecture

## Module Layout

```
src/mcp_certificate_monitor/
├── __init__.py   # exports main() entry point and mcp server instance
├── server.py     # FastMCP app; registers all tools, resources, and prompts
├── cert.py       # certificate fetching and parsing via stdlib ssl + socket
└── store.py      # JSON persistence; host CRUD and result updates
```

### `cert.py`

Handles all TLS connections. `fetch_certificate(domain, port)` opens a socket with a
10-second timeout, performs a TLS handshake, and calls `getpeercert()` to read the
certificate. Dates are parsed via `ssl.cert_time_to_seconds()`. The `_normalize_dn()`
helper converts the nested RDN tuple structure returned by `getpeercert()` into a
readable string (e.g., `CN=example.com, O=Example Inc`). On any network or parsing
error, it returns a `CertResult` with only `error` set rather than raising.

### `store.py`

Reads and writes `hosts.json` on every call — no in-memory cache. The file is source
of truth. Writes are atomic: data is written to a `.tmp` file in the same directory,
then renamed via `os.replace()`, so a crash mid-write never corrupts the store. On
startup (or any read), a missing or corrupt file is treated as an empty store with a
warning log; the server never crashes due to bad persisted state.

### `server.py`

Registers the FastMCP app with five tools, three resources, and two prompts. Risk
thresholds (`CRITICAL_DAYS = 14`, `WARNING_DAYS = 30`) are module-level constants.
`scan_all()` uses `asyncio.gather` with a thread-pool executor to run blocking
`ssl`/`socket` calls concurrently without blocking the event loop.

## Data Models

Defined in `cert.py` and `store.py` using Pydantic v2.

### `CertResult`

Returned by `fetch_certificate()` and stored inside `MonitoredHost.last_result`.

| Field | Type | Description |
|---|---|---|
| `subject` | `str` | Normalized DN string, e.g. `CN=example.com` |
| `issuer` | `str` | Normalized DN string, e.g. `CN=R10, O=Let's Encrypt` |
| `not_before` | `datetime` | Certificate validity start (UTC) |
| `not_after` | `datetime` | Certificate expiry (UTC) |
| `days_remaining` | `int` | `(not_after - now).days`; can be negative for expired certs |
| `serial` | `str` | Certificate serial number as hex string |
| `san` | `list[str]` | DNS Subject Alternative Names |
| `error` | `str \| None` | Error message if the check failed; `None` on success |

When `error` is set, all other fields are populated with zero/empty sentinels. Callers
must check `error` before reading certificate fields.

### `MonitoredHost`

One entry per tracked domain in `hosts.json`.

| Field | Type | Description |
|---|---|---|
| `domain` | `str` | Hostname (e.g. `example.com`) |
| `port` | `int` | TLS port (default 443) |
| `added_at` | `datetime` | When the host was first added (UTC) |
| `last_checked` | `datetime \| None` | Time of last certificate check; `None` if never checked |
| `last_result` | `CertResult \| None` | Most recent result; `None` if never checked |

### `HostStore`

Top-level wrapper persisted to `hosts.json`.

| Field | Type | Description |
|---|---|---|
| `hosts` | `dict[str, MonitoredHost]` | Keyed by domain name |

## Storage Schema

`hosts.json` is written by `store.save()` using `model_dump_json(indent=2)`.

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
        "issuer": "CN=R10, O=Let's Encrypt, C=US",
        "not_before": "2026-01-01T00:00:00Z",
        "not_after": "2026-09-01T00:00:00Z",
        "days_remaining": 76,
        "serial": "03ABC123",
        "san": ["example.com", "www.example.com"],
        "error": null
      }
    }
  }
}
```

`last_result` is `null` until the host has been checked at least once. When a check
fails, `error` is a non-null string and the other certificate fields hold zero/empty
sentinels.

## Key Design Decisions

**No in-memory cache** — The file is read on every request and written on every
mutation. This keeps the implementation simple and correct under concurrent MCP calls
without needing locks or cache-invalidation logic.

**Atomic writes** — `os.replace()` is used after writing to a `.tmp` file in the same
directory. On all supported platforms this is an atomic rename, so the store is never
partially written.

**Risk thresholds** — `CRITICAL_DAYS = 14` and `WARNING_DAYS = 30` are module-level
constants in `server.py`. Hosts with `days_remaining <= 14` or with errors are
`critical`; hosts with `days_remaining <= 30` are `warning`; the rest are `ok`.

**Error containment** — `fetch_certificate()` never raises; it always returns a
`CertResult`. A bad host (unreachable, expired TLS handshake, etc.) only affects its
own entry — the rest of `scan_all()` continues normally.

**No third-party TLS library** — stdlib `ssl` + `socket` is sufficient for connecting
to real servers and extracting certificate metadata. This avoids a `cryptography`
dependency.
