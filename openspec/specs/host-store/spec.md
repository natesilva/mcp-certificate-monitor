# Host Store

## Purpose

Defines requirements for persisting monitored host configuration and certificate check results to disk, including Pydantic models, atomic file I/O, and host CRUD operations.

## Requirements

### Requirement: Persistent host storage with Pydantic models
The system SHALL define `MonitoredHost` and `HostStore` Pydantic `BaseModel` classes. `MonitoredHost` SHALL have fields: `domain: str`, `port: int`, `added_at: datetime`, `last_checked: datetime | None = None`, `last_result: CertResult | None = None`. `HostStore` SHALL have field: `hosts: dict[str, MonitoredHost] = {}` keyed by domain string.

#### Scenario: MonitoredHost validates on construction
- **WHEN** a `MonitoredHost` is constructed with valid fields
- **THEN** the model validates without error and `last_result` defaults to `None`

#### Scenario: HostStore defaults to empty hosts dict
- **WHEN** `HostStore()` is constructed with no arguments
- **THEN** `hosts` is an empty dict

### Requirement: Load store from disk
The system SHALL provide a `load() -> HostStore` function that reads `hosts.json` from `platformdirs.user_data_dir("cert-monitor")` and returns a validated `HostStore`. It SHALL use `HostStore.model_validate_json()` for parsing so that ISO 8601 datetimes are coerced automatically.

#### Scenario: Load existing valid JSON
- **WHEN** `hosts.json` exists and contains valid JSON matching the `HostStore` schema
- **THEN** `load()` returns a `HostStore` with all hosts populated and datetimes parsed as UTC-aware `datetime` objects

#### Scenario: Load missing file
- **WHEN** `hosts.json` does not exist
- **THEN** `load()` returns an empty `HostStore()` without raising an exception

#### Scenario: Load corrupt JSON
- **WHEN** `hosts.json` exists but contains invalid or schema-mismatched JSON
- **THEN** `load()` logs a warning and returns an empty `HostStore()` without raising an exception

### Requirement: Save store to disk atomically
The system SHALL provide a `save(store: HostStore) -> None` function that serializes the store to JSON and writes it atomically to `hosts.json` using a temporary file and `os.replace()`. It SHALL create the parent directory with `mkdir(parents=True, exist_ok=True)` if it does not exist.

#### Scenario: Save creates file
- **WHEN** `save(store)` is called with a populated `HostStore`
- **THEN** `hosts.json` exists afterward and its content round-trips back to an equivalent `HostStore` via `load()`

#### Scenario: Atomic write on crash
- **WHEN** the process is killed after the temp file is written but before `os.replace()` completes
- **THEN** the original `hosts.json` (if it existed) is not corrupted (temp file is a sibling, not in-place overwrite)

### Requirement: Host CRUD operations
The system SHALL provide functions for adding, removing, getting, and listing monitored hosts. All mutations SHALL call `save()` immediately after modifying the in-memory store.

#### Scenario: Add a new host
- **WHEN** `add_host(domain, port)` is called with a domain not already in the store
- **THEN** the host appears in the store with `added_at` set to the current UTC time, `last_checked` and `last_result` as `None`, and the store is persisted to disk

#### Scenario: Add duplicate host
- **WHEN** `add_host(domain, port)` is called with a domain already in the store
- **THEN** the function raises a `ValueError` indicating the host already exists

#### Scenario: Remove existing host
- **WHEN** `remove_host(domain)` is called with a domain in the store
- **THEN** the host is no longer present in the store and the store is persisted to disk

#### Scenario: Remove missing host
- **WHEN** `remove_host(domain)` is called with a domain not in the store
- **THEN** the function raises a `ValueError` indicating the host was not found

#### Scenario: Get existing host
- **WHEN** `get_host(domain)` is called with a domain in the store
- **THEN** the function returns the `MonitoredHost` for that domain

#### Scenario: Get missing host
- **WHEN** `get_host(domain)` is called with a domain not in the store
- **THEN** the function raises a `ValueError` indicating the host was not found

#### Scenario: List all hosts
- **WHEN** `list_hosts()` is called
- **THEN** the function returns a list of all `MonitoredHost` objects currently in the store (empty list if none)

### Requirement: Update host result after check
The system SHALL provide an `update_host_result(domain, result: CertResult) -> None` function that sets `last_checked` to the current UTC time and `last_result` to the given `CertResult` on the matching host, then persists the store.

#### Scenario: Update result for existing host
- **WHEN** `update_host_result(domain, result)` is called with a domain in the store
- **THEN** `last_checked` is set to the current UTC time, `last_result` equals the provided `CertResult`, and the store is persisted

#### Scenario: Update result for missing host
- **WHEN** `update_host_result(domain, result)` is called with a domain not in the store
- **THEN** the function raises a `ValueError` indicating the host was not found
