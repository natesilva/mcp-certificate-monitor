## MODIFIED Requirements

### Requirement: Parse X.509 certificate fields
The system SHALL parse the raw `getpeercert()` dict into structured, typed fields: full RFC 4514-style `subject` and `issuer` DN strings (all RDN components joined with `", "`), `not_before` and `not_after` as timezone-aware UTC `datetime` objects, `days_remaining` as an integer (may be negative for expired certs), `serial` as a hex string, and `san` as a list of strings.

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

#### Scenario: Issuer contains full DN
- **WHEN** `fetch_certificate(domain, port)` returns successfully
- **THEN** `CertResult.issuer` is the full Distinguished Name string with all RDN components (e.g., `"C=US, O=Let's Encrypt, CN=R11"`), not just the `commonName` value

#### Scenario: Subject contains full DN
- **WHEN** `fetch_certificate(domain, port)` returns successfully
- **THEN** `CertResult.subject` is the full Distinguished Name string with all RDN components (e.g., `"CN=example.com"`), not just the `commonName` value

#### Scenario: Issuer with no RDN components
- **WHEN** the certificate's issuer field is absent or empty
- **THEN** `CertResult.issuer` is an empty string `""`
