## ADDED Requirements

### Requirement: FastMCP server instance
The system SHALL define a `FastMCP` app instance named `mcp` in `server.py` with the name `"Certificate Monitor"`. The module SHALL define `CRITICAL_DAYS: int = 14` and `WARNING_DAYS: int = 30` as module-level constants used by risk classification.

#### Scenario: Server instance is importable
- **WHEN** `from mcp_certificate_monitor.server import mcp` is executed
- **THEN** a `FastMCP` instance is returned without error

### Requirement: check_certificate tool
The system SHALL expose a `check_certificate(domain: str, port: int = 443) -> dict` MCP tool that fetches a live certificate for the given host via `cert.fetch_certificate()` and returns the `CertResult` as a dict. It SHALL NOT read from or write to the host store.

#### Scenario: Successful live certificate check
- **WHEN** `check_certificate` is called with a reachable HTTPS domain
- **THEN** the tool returns a dict with non-None `subject`, `issuer`, `not_after`, `days_remaining`, `san`, and `error` equal to `None`

#### Scenario: Unreachable host returns error dict
- **WHEN** `check_certificate` is called with a domain that cannot be reached
- **THEN** the tool returns a dict where `error` is a non-empty string and no exception propagates to the MCP session

#### Scenario: Does not mutate host store
- **WHEN** `check_certificate` is called for any domain
- **THEN** the stored state in `hosts.json` is not modified

### Requirement: add_monitored_host tool
The system SHALL expose an `add_monitored_host(domain: str, port: int = 443) -> dict` MCP tool that adds the domain to the store via `store.add_host()`, immediately fetches its certificate via `cert.fetch_certificate()`, persists the result via `store.update_host_result()`, and returns a dict with `domain`, `port`, and `last_result`.

#### Scenario: Add new host and fetch certificate
- **WHEN** `add_monitored_host` is called with a domain not already in the store
- **THEN** the domain appears in the store with `last_result` populated (success or error) and the tool returns a dict containing `domain` and `last_result`

#### Scenario: Add duplicate host raises error
- **WHEN** `add_monitored_host` is called with a domain already present in the store
- **THEN** the tool raises an exception (propagating the `ValueError` from `store.add_host()`) and the store is not modified

### Requirement: remove_host tool
The system SHALL expose a `remove_host(domain: str) -> str` MCP tool that removes the domain from the store via `store.remove_host()` and returns a confirmation string.

#### Scenario: Remove existing host
- **WHEN** `remove_host` is called with a domain present in the store
- **THEN** the domain is removed from the store and the tool returns a non-empty confirmation string

#### Scenario: Remove missing host raises error
- **WHEN** `remove_host` is called with a domain not in the store
- **THEN** the tool raises an exception (propagating the `ValueError` from `store.remove_host()`) and the store is unchanged

### Requirement: scan_all tool
The system SHALL expose an `async def scan_all() -> list[dict]` MCP tool that fetches live certificates for every monitored host in parallel using `asyncio` and the default thread pool executor, updates each result in the store via `store.update_host_result()`, and returns a list of summary dicts each containing `domain`, `days_remaining`, and `error`.

#### Scenario: Scan returns summary for all hosts
- **WHEN** `scan_all` is called with hosts in the store
- **THEN** the returned list has one entry per stored host, each with `domain`, `days_remaining` (int or None), and `error` (str or None)

#### Scenario: Scan updates stored results
- **WHEN** `scan_all` completes
- **THEN** each host in the store has `last_checked` updated to the current UTC time and `last_result` set to the fetched `CertResult`

#### Scenario: Scan with empty store returns empty list
- **WHEN** `scan_all` is called with no hosts in the store
- **THEN** the tool returns an empty list and no exception is raised

#### Scenario: Unreachable host does not abort scan
- **WHEN** `scan_all` is called and one or more hosts are unreachable
- **THEN** the scan completes for all hosts, the unreachable hosts have `error` set in their summary and stored result, and no exception propagates

### Requirement: get_expiry_report tool
The system SHALL expose a `get_expiry_report() -> dict` MCP tool that reads stored (not live) host data via `store.list_hosts()` and classifies each host into `critical` (≤`CRITICAL_DAYS` days remaining, errored, or never checked), `warning` (`CRITICAL_DAYS < days_remaining ≤ WARNING_DAYS`), or `ok` (>`WARNING_DAYS` days remaining). It SHALL return a dict with `generated_at` (ISO 8601 UTC string) and lists `critical`, `warning`, `ok` each containing dicts with `domain`, `port`, `days_remaining`, and `error`.

#### Scenario: Report buckets hosts by days remaining
- **WHEN** `get_expiry_report` is called with hosts having varied `last_result.days_remaining` values
- **THEN** hosts with ≤14 days appear in `critical`, hosts with 15–30 days appear in `warning`, and hosts with >30 days appear in `ok`

#### Scenario: Errored host appears in critical
- **WHEN** a monitored host has `last_result.error` set to a non-None string
- **THEN** that host appears in the `critical` list of the report

#### Scenario: Never-checked host appears in critical
- **WHEN** a monitored host has `last_result` equal to `None`
- **THEN** that host appears in the `critical` list with `days_remaining` as `None` and `error` as `"never checked"`

#### Scenario: Report includes generated_at timestamp
- **WHEN** `get_expiry_report` is called
- **THEN** the returned dict contains `generated_at` as a UTC ISO 8601 string representing the current time

#### Scenario: Empty store returns empty report
- **WHEN** `get_expiry_report` is called with no hosts in the store
- **THEN** the tool returns `{"generated_at": "<timestamp>", "critical": [], "warning": [], "ok": []}` without error
