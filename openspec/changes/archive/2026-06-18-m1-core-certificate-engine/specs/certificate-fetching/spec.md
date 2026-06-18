## ADDED Requirements

### Requirement: Fetch live certificate for a domain
The system SHALL open a TLS connection to a given domain and port using stdlib `ssl.create_default_context()` and `socket.create_connection()` with a 10-second timeout, retrieve the peer certificate via `getpeercert()`, and return a fully populated `CertResult` model.

#### Scenario: Successful certificate fetch
- **WHEN** `fetch_certificate(domain, port)` is called with a reachable HTTPS host
- **THEN** the function returns a `CertResult` with non-None `subject`, `issuer`, `not_before`, `not_after`, `serial`, `san` list, `days_remaining` integer, and `error` equal to `None`

#### Scenario: Unreachable host
- **WHEN** `fetch_certificate(domain, port)` is called with a host that cannot be connected to
- **THEN** the function returns a `CertResult` where `error` is a non-empty string describing the failure and all other fields are set to sentinel/default values (not raised as an exception)

#### Scenario: TLS handshake failure
- **WHEN** `fetch_certificate(domain, port)` is called with a host that rejects the TLS handshake
- **THEN** the function returns a `CertResult` where `error` is a non-empty string and no exception propagates to the caller

### Requirement: Parse X.509 certificate fields
The system SHALL parse the raw `getpeercert()` dict into structured, typed fields: normalized `subject` and `issuer` strings (CN-first), `not_before` and `not_after` as timezone-aware UTC `datetime` objects, `days_remaining` as an integer (may be negative for expired certs), `serial` as a hex string, and `san` as a list of strings.

#### Scenario: Parse notAfter into UTC datetime
- **WHEN** the peer certificate's `notAfter` field is present
- **THEN** `not_after` in `CertResult` is a UTC-aware `datetime` parsed via `ssl.cert_time_to_seconds`

#### Scenario: Compute days_remaining
- **WHEN** the certificate has a valid `not_after` datetime
- **THEN** `days_remaining` equals `(not_after - datetime.now(UTC)).days` rounded down to the nearest integer

#### Scenario: Parse Subject Alternative Names
- **WHEN** the certificate contains a `subjectAltName` extension
- **THEN** `san` contains all DNS name entries as plain strings (without `DNS:` prefix)

#### Scenario: Missing SAN extension
- **WHEN** the certificate has no `subjectAltName` extension
- **THEN** `san` is an empty list and no exception is raised

### Requirement: CertResult data model
The system SHALL define a `CertResult` Pydantic `BaseModel` with fields: `subject: str`, `issuer: str`, `not_before: datetime`, `not_after: datetime`, `days_remaining: int`, `serial: str`, `san: list[str]`, `error: str | None = None`. When `error` is set, the other fields SHALL still be present with zero/empty/epoch sentinel values to allow uniform handling by callers.

#### Scenario: CertResult serializes to JSON
- **WHEN** `CertResult.model_dump_json()` is called
- **THEN** the result is valid JSON with all fields present, datetimes in ISO 8601 format

#### Scenario: CertResult with error
- **WHEN** a `CertResult` is constructed with a non-None `error`
- **THEN** the model validates without raising an exception
