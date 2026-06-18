## 1. Project Setup

- [x] 1.1 Add `fastmcp`, `pydantic`, `cryptography`, and `platformdirs` as explicit dependencies in `pyproject.toml` (do not rely on transitive deps)
- [x] 1.2 Create `src/mcp_certificate_monitor/` package directory with `__init__.py` (empty or re-exporting stubs)

## 2. CertResult Model

- [x] 2.1 Create `src/mcp_certificate_monitor/cert.py` with `CertResult` Pydantic `BaseModel` (fields: `subject`, `issuer`, `not_before`, `not_after`, `days_remaining`, `serial`, `san`, `error`)
- [x] 2.2 Add a module-level sentinel `_EMPTY_CERT_RESULT` helper or factory used when returning error results (all zero/empty values, `error` populated)

## 3. Certificate Fetching

- [x] 3.1 Implement `fetch_certificate(domain: str, port: int = 443) -> CertResult` using `ssl.create_default_context()` + `socket.create_connection()` with 10-second timeout
- [x] 3.2 Parse `getpeercert()` dict: extract `subject` (CN normalized), `issuer` (CN normalized), `notBefore`/`notAfter` via `ssl.cert_time_to_seconds`, `serialNumber`, `subjectAltName`
- [x] 3.3 Compute `days_remaining = (not_after - datetime.now(UTC)).days`
- [x] 3.4 Wrap entire fetch in `try/except` — catch `socket.timeout`, `ssl.SSLError`, `OSError`, and any other exception; return a `CertResult` with `error` set (never raise)

## 4. Pydantic Store Models

- [x] 4.1 Create `src/mcp_certificate_monitor/store.py` with `MonitoredHost` Pydantic `BaseModel` (fields: `domain`, `port`, `added_at`, `last_checked`, `last_result`)
- [x] 4.2 Add `HostStore` Pydantic `BaseModel` with `hosts: dict[str, MonitoredHost] = {}`

## 5. Store Persistence

- [x] 5.1 Implement `_data_path() -> Path` returning `Path(platformdirs.user_data_dir("cert-monitor")) / "hosts.json"`
- [x] 5.2 Implement `load() -> HostStore`: read file if exists, call `HostStore.model_validate_json(text)`, catch `FileNotFoundError` and `ValidationError` and return empty `HostStore()` with a logged warning
- [x] 5.3 Implement `save(store: HostStore) -> None`: create parent dir, write `store.model_dump_json(indent=2)` to a `.tmp` sibling file, then `os.replace()` to finalize atomically

## 6. Host CRUD

- [x] 6.1 Implement `add_host(domain: str, port: int = 443) -> MonitoredHost`: load store, raise `ValueError` if already present, add with `added_at=datetime.now(UTC)`, save, return new host
- [x] 6.2 Implement `remove_host(domain: str) -> None`: load store, raise `ValueError` if not found, delete key, save
- [x] 6.3 Implement `get_host(domain: str) -> MonitoredHost`: load store, raise `ValueError` if not found, return host
- [x] 6.4 Implement `list_hosts() -> list[MonitoredHost]`: load store, return `list(store.hosts.values())`
- [x] 6.5 Implement `update_host_result(domain: str, result: CertResult) -> None`: load store, raise `ValueError` if not found, set `last_checked=datetime.now(UTC)` and `last_result=result`, save

## 7. Tests

- [x] 7.1 Write `tests/test_cert.py`: test `CertResult` model construction, serialization, and the error-result factory
- [x] 7.2 Write `tests/test_cert.py`: test `fetch_certificate` with a mocked `ssl`/`socket` returning a valid cert dict — assert all fields parsed correctly
- [x] 7.3 Write `tests/test_cert.py`: test `fetch_certificate` error paths — socket timeout, SSLError, OSError — assert error field set and no exception raised
- [x] 7.4 Write `tests/test_store.py`: test `load()` on missing file returns empty `HostStore`
- [x] 7.5 Write `tests/test_store.py`: test `load()` on corrupt JSON returns empty `HostStore` with no exception
- [x] 7.6 Write `tests/test_store.py`: test `save()`/`load()` round-trip preserves all fields including nested `CertResult`
- [x] 7.7 Write `tests/test_store.py`: test `add_host`, `get_host`, `list_hosts`, `remove_host`, and `update_host_result` — including error cases (`ValueError` on duplicate add, missing host remove/get/update)
- [x] 7.8 Run `pytest` — all tests pass

## 8. Verification

- [x] 8.1 Smoke test: `python -c "from mcp_certificate_monitor.cert import fetch_certificate; import pprint; pprint.pprint(fetch_certificate('example.com').model_dump())"` produces valid output
- [x] 8.2 Confirm `__init__.py` imports don't error (`python -c "import mcp_certificate_monitor"`)
