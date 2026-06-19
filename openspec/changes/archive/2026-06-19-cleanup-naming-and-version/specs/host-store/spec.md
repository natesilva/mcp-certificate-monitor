## MODIFIED Requirements

### Requirement: Load store from disk
The system SHALL provide a `load() -> HostStore` function that reads `hosts.json` from `platformdirs.user_data_dir("mcp-certificate-monitor")` and returns a validated `HostStore`. It SHALL use `HostStore.model_validate_json()` for parsing so that ISO 8601 datetimes are coerced automatically.

#### Scenario: Load existing valid JSON
- **WHEN** `hosts.json` exists and contains valid JSON matching the `HostStore` schema
- **THEN** `load()` returns a `HostStore` with all hosts populated and datetimes parsed as UTC-aware `datetime` objects

#### Scenario: Load missing file
- **WHEN** `hosts.json` does not exist
- **THEN** `load()` returns an empty `HostStore()` without raising an exception

#### Scenario: Load corrupt JSON
- **WHEN** `hosts.json` exists but contains invalid or schema-mismatched JSON
- **THEN** `load()` logs a warning and returns an empty `HostStore()` without raising an exception
