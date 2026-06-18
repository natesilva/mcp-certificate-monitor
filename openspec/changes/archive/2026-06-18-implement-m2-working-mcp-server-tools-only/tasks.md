## 1. Create server.py with FastMCP app and constants

- [x] 1.1 Create `src/mcp_certificate_monitor/server.py` with `FastMCP("Certificate Monitor")` instance named `mcp` and `CRITICAL_DAYS = 14`, `WARNING_DAYS = 30` constants
- [x] 1.2 Import `cert` and `store` modules; verify imports resolve cleanly

## 2. Implement check_certificate tool

- [x] 2.1 Implement `check_certificate(domain: str, port: int = 443) -> dict` with `@mcp.tool()` decorator; call `cert.fetch_certificate()` and return `result.model_dump()`
- [x] 2.2 Verify the tool does not touch the host store

## 3. Implement add_monitored_host tool

- [x] 3.1 Implement `add_monitored_host(domain: str, port: int = 443) -> dict` with `@mcp.tool()` decorator; call `store.add_host()`, fetch certificate, call `store.update_host_result()`, return dict with `domain`, `port`, and `last_result`
- [x] 3.2 Confirm `ValueError` from `store.add_host()` propagates when domain is duplicate

## 4. Implement remove_host tool

- [x] 4.1 Implement `remove_host(domain: str) -> str` with `@mcp.tool()` decorator; call `store.remove_host()` and return a confirmation string
- [x] 4.2 Confirm `ValueError` from `store.remove_host()` propagates when domain is not found

## 5. Implement scan_all tool

- [x] 5.1 Implement `async def scan_all() -> list[dict]` with `@mcp.tool()` decorator; use `asyncio.get_event_loop().run_in_executor(None, fetch_certificate, domain, port)` to fetch all hosts in parallel
- [x] 5.2 After each fetch, call `store.update_host_result()` and append `{"domain": ..., "days_remaining": ..., "error": ...}` to the result list
- [x] 5.3 Confirm scan with empty store returns `[]` and scan with unreachable hosts completes without raising

## 6. Implement get_expiry_report tool

- [x] 6.1 Implement `get_expiry_report() -> dict` with `@mcp.tool()` decorator; call `store.list_hosts()` and classify each host into `critical`, `warning`, or `ok` using `CRITICAL_DAYS` and `WARNING_DAYS`
- [x] 6.2 Handle `last_result is None` (never checked) → `critical` with `error = "never checked"`
- [x] 6.3 Handle `last_result.error is not None` (errored) → `critical`
- [x] 6.4 Return `{"generated_at": datetime.now(UTC).isoformat(), "critical": [...], "warning": [...], "ok": [...]}`

## 7. Wire up __init__.py and verify server runs

- [x] 7.1 Update `src/mcp_certificate_monitor/__init__.py` to re-export the `mcp` app instance from `server.py`
- [x] 7.2 Run `python -c "from mcp_certificate_monitor.server import mcp; print(mcp)"` to verify the server module imports cleanly

## 8. Write tests for all five tools

- [x] 8.1 Create `tests/test_server.py` with fixtures for a temp store directory (patch `store._data_path`)
- [x] 8.2 Test `check_certificate`: mock `cert.fetch_certificate` to return a success result; assert returned dict has correct keys
- [x] 8.3 Test `check_certificate` with error: mock `fetch_certificate` to return a `CertResult` with `error` set; assert error is surfaced in dict
- [x] 8.4 Test `add_monitored_host`: mock `fetch_certificate`; assert host appears in store and `last_result` is populated
- [x] 8.5 Test `add_monitored_host` duplicate: call twice with same domain; assert `ValueError` is raised on second call
- [x] 8.6 Test `remove_host`: add a host, remove it, assert it's gone from store
- [x] 8.7 Test `remove_host` missing: assert `ValueError` is raised
- [x] 8.8 Test `scan_all`: populate store with 2 hosts, mock `fetch_certificate`, run `scan_all`, assert result list has 2 entries and store results are updated
- [x] 8.9 Test `scan_all` empty store: assert returns `[]`
- [x] 8.10 Test `get_expiry_report` bucketing: add hosts with mocked results at 7, 20, and 60 days; assert each lands in the correct bucket
- [x] 8.11 Test `get_expiry_report` with errored host: assert it lands in `critical`
- [x] 8.12 Test `get_expiry_report` with never-checked host: assert it lands in `critical` with `error = "never checked"`
- [x] 8.13 Run `pytest` and confirm all tests pass
