# MCP Tools (Delta)

## ADDED Requirements

### Requirement: Tool input validation
All server tools that accept `domain` and `port` parameters (`check_certificate`, `add_monitored_host`, `remove_host`) SHALL validate inputs before any store or cert operation. A `domain` SHALL be rejected if it is empty or exceeds 253 characters. A `port` SHALL be rejected if it is outside the range 1–65535. On validation failure, the tool SHALL raise a `ValueError` with a descriptive message; FastMCP converts this to a well-formed MCP error so no exception propagates to the MCP session as a crash.

#### Scenario: Empty domain rejected
- **WHEN** any domain-accepting tool is called with `domain=""` or `domain="   "` (whitespace-only)
- **THEN** the tool raises `ValueError` with a message indicating the domain is invalid, and no store or cert operation is performed

#### Scenario: Domain too long rejected
- **WHEN** any domain-accepting tool is called with a `domain` exceeding 253 characters
- **THEN** the tool raises `ValueError` with a message indicating the domain is too long, and no store or cert operation is performed

#### Scenario: Port out of range rejected
- **WHEN** any port-accepting tool is called with `port` less than 1 or greater than 65535
- **THEN** the tool raises `ValueError` with a message indicating the port is invalid, and no store or cert operation is performed

#### Scenario: Valid inputs pass through to store/cert
- **WHEN** a tool is called with a non-empty domain of ≤253 characters and a port in 1–65535
- **THEN** the tool proceeds to its store or cert operation without raising a validation error

### Requirement: cert-monitor://report resource
The system SHALL expose a `cert-monitor://report` MCP resource that reads stored host data from `store.list_hosts()` and returns a JSON string with the same structure as `get_expiry_report()`: a dict with `generated_at` (ISO 8601 UTC string) and lists `critical`, `warning`, and `ok`, each containing dicts with `domain`, `port`, `days_remaining`, and `error`. This resource SHALL NOT trigger live certificate fetches.

#### Scenario: Report resource returns bucketed JSON
- **WHEN** the `cert-monitor://report` resource is read with hosts in the store
- **THEN** the resource returns a JSON string with `critical`, `warning`, and `ok` lists matching the same risk classification as the `get_expiry_report` tool

#### Scenario: Report resource with empty store
- **WHEN** the `cert-monitor://report` resource is read with no hosts in the store
- **THEN** the resource returns a JSON string with `critical`, `warning`, and `ok` as empty lists and a valid `generated_at` timestamp

#### Scenario: Report resource does not fetch live certificates
- **WHEN** the `cert-monitor://report` resource is read
- **THEN** no network connection is made to any domain; only stored data is used
