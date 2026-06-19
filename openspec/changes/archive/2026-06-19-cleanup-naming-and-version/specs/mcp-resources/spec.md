## MODIFIED Requirements

### Requirement: cert-monitor://hosts list resource
The system SHALL expose an MCP Resource at URI `mcp-certificate-monitor://hosts` that reads all monitored hosts from the store via `store.list_hosts()` and returns their serialized state as a JSON string. Each host entry SHALL include `domain`, `port`, `last_checked`, and `last_result` (or `null` if never checked).

#### Scenario: List resource returns all hosts
- **WHEN** an AI host reads the resource at `mcp-certificate-monitor://hosts`
- **THEN** the response is a JSON array where each element contains `domain`, `port`, `last_checked`, and `last_result` for every monitored host

#### Scenario: List resource with empty store
- **WHEN** no hosts are in the store and `mcp-certificate-monitor://hosts` is read
- **THEN** the response is a JSON array `[]` without error

#### Scenario: List resource reflects current store state
- **WHEN** `add_monitored_host` is called and then `mcp-certificate-monitor://hosts` is read
- **THEN** the newly added domain appears in the resource response

### Requirement: cert-monitor://hosts/{domain} template resource
The system SHALL expose an MCP Resource template at URI `mcp-certificate-monitor://hosts/{domain}` that reads a single host's stored state from the store via `store.get_host(domain)` and returns it as a JSON string. If the domain is not in the store, the resource SHALL return a JSON object with an `error` key describing the missing host.

#### Scenario: Template resource returns single host data
- **WHEN** an AI host reads `mcp-certificate-monitor://hosts/example.com` and that domain is in the store
- **THEN** the response is a JSON object with `domain`, `port`, `last_checked`, and `last_result` for that host

#### Scenario: Template resource for unknown domain returns error
- **WHEN** an AI host reads `mcp-certificate-monitor://hosts/unknown.example` and that domain is not in the store
- **THEN** the response is a JSON object with an `error` key and no exception propagates to the MCP session

#### Scenario: Template resource reflects updated results
- **WHEN** `scan_all` is called and then `mcp-certificate-monitor://hosts/{domain}` is read
- **THEN** the `last_result` field reflects the result from the most recent scan
