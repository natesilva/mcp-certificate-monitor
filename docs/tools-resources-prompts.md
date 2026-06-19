# MCP Tools, Resources, and Prompts

## Tools

Tools perform actions and may update stored state. All tools validate `domain` (non-empty,
≤ 253 characters) and `port` (1–65535) before proceeding.

---

### `check_certificate`

Fetches a live SSL/TLS certificate for a domain. Does **not** update stored state.

**Parameters**

| Name | Type | Default | Description |
|---|---|---|---|
| `domain` | `string` | required | Hostname to check (e.g. `example.com`) |
| `port` | `integer` | `443` | TLS port |

**Returns** — `CertResult` object:

```json
{
  "subject": "CN=example.com",
  "issuer": "CN=R10, O=Let's Encrypt, C=US",
  "not_before": "2026-01-01T00:00:00Z",
  "not_after": "2026-09-01T00:00:00Z",
  "days_remaining": 76,
  "serial": "03ABC123",
  "san": ["example.com", "www.example.com"],
  "error": null
}
```

On network or TLS failure, `error` is a non-null string and other fields hold
zero/empty sentinels.

---

### `add_monitored_host`

Adds a domain to the monitored host list and immediately runs a certificate check.

**Parameters**

| Name | Type | Default | Description |
|---|---|---|---|
| `domain` | `string` | required | Hostname to monitor |
| `port` | `integer` | `443` | TLS port |

**Returns** — Object with `domain`, `port`, and `last_result`:

```json
{
  "domain": "example.com",
  "port": 443,
  "last_result": { ... }
}
```

Raises an error if the domain is already monitored.

---

### `remove_host`

Removes a domain from the monitored host list.

**Parameters**

| Name | Type | Default | Description |
|---|---|---|---|
| `domain` | `string` | required | Hostname to remove |

**Returns** — Confirmation string: `"Removed example.com from monitored hosts."`

Raises an error if the domain is not found.

---

### `scan_all`

Checks certificates for all monitored hosts in parallel and updates stored results.
Uses `asyncio.gather` with a thread-pool executor so blocking TLS calls run concurrently.

**Parameters** — None

**Returns** — Array of summary objects, one per host:

```json
[
  { "domain": "example.com", "days_remaining": 76, "error": null },
  { "domain": "broken.example", "days_remaining": null, "error": "Connection refused" }
]
```

Returns an empty array if no hosts are monitored.

---

### `get_expiry_report`

Returns stored (not live) certificate data bucketed by risk level.

**Parameters** — None

**Returns**

```json
{
  "generated_at": "2026-06-19T12:00:00Z",
  "critical": [
    { "domain": "expired.example", "port": 443, "days_remaining": null, "error": "certificate has expired" }
  ],
  "warning": [
    { "domain": "soon.example", "port": 443, "days_remaining": 20, "error": null }
  ],
  "ok": [
    { "domain": "example.com", "port": 443, "days_remaining": 76, "error": null }
  ]
}
```

**Risk buckets**

| Bucket | Condition |
|---|---|
| `critical` | `days_remaining <= 14`, check errored, or never checked |
| `warning` | `15 <= days_remaining <= 30` |
| `ok` | `days_remaining > 30` |

---

## Resources

Resources return stored state without making live network calls. All URIs use the
`mcp-certificate-monitor://` scheme.

---

### `mcp-certificate-monitor://hosts`

Returns all monitored hosts and their last certificate results.

**Response** — JSON array of `MonitoredHost` objects:

```json
[
  {
    "domain": "example.com",
    "port": 443,
    "added_at": "2026-06-17T00:00:00Z",
    "last_checked": "2026-06-17T12:00:00Z",
    "last_result": { ... }
  }
]
```

---

### `mcp-certificate-monitor://hosts/{domain}`

Returns a single host's stored state. Replace `{domain}` with the hostname.

**Response** — Single `MonitoredHost` object, or an error object if not found:

```json
{ "error": "Host not found: unknown.example" }
```

---

### `mcp-certificate-monitor://report`

Returns the same expiry report as `get_expiry_report` but as a resource (read from
stored state). Same response shape as the tool.

---

## Prompts

Prompts return structured messages that prime the AI to perform a specific analysis.

---

### `audit_certificates`

Prompts the AI to analyze the current certificate expiry report and identify risks.

**Parameters** — None

**Embedded context** — Builds a live expiry report from stored data (same bucketing
logic as `get_expiry_report`) and injects it into the prompt. The AI is asked to:

1. Identify critical certificates needing immediate action (≤ 14 days or errored)
2. Prioritize warning certificates (≤ 30 days)
3. Flag certificates showing errors for investigation
4. Recommend a renewal order

---

### `plan_renewal`

Prompts the AI to draft a step-by-step certificate renewal plan for a specific domain.

**Parameters**

| Name | Type | Description |
|---|---|---|
| `domain` | `string` | Hostname to plan renewal for (must already be monitored) |

**Embedded context** — Injects the full stored `MonitoredHost` record (including the
last `CertResult`) into the prompt. The AI is asked to provide:

1. An urgency assessment based on the expiry date
2. Step-by-step renewal process recommendations
3. Validation steps to confirm renewal succeeded
4. Suggested monitoring frequency going forward

If the domain is not monitored, the prompt instructs the AI to add it first using
`add_monitored_host`.
