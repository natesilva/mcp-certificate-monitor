## 1. Package Entry Point

- [x] 1.1 Add `[project.scripts]` entry `mcp-certificate-monitor = "mcp_certificate_monitor:main"` to `pyproject.toml`
- [x] 1.2 Add `main()` function to `src/mcp_certificate_monitor/__init__.py` that calls `mcp.run()`

## 2. Input Validation

- [x] 2.1 Add `_validate_domain(domain: str) -> None` helper in `server.py` that raises `ValueError` for empty/whitespace or >253-char domains
- [x] 2.2 Add `_validate_port(port: int) -> None` helper in `server.py` that raises `ValueError` for ports outside 1–65535
- [x] 2.3 Call `_validate_domain` and `_validate_port` at the top of `check_certificate`, `add_monitored_host`, and `remove_host` (before any store or cert call)

## 3. Report Resource

- [x] 3.1 Add `@mcp.resource("cert-monitor://report")` handler in `server.py` that returns the expiry report as a JSON string (same bucketing logic as `get_expiry_report`)

## 4. Tests

- [x] 4.1 Add tests for empty domain rejection in `check_certificate`, `add_monitored_host`, and `remove_host`
- [x] 4.2 Add tests for >253-char domain rejection in `check_certificate`, `add_monitored_host`, and `remove_host`
- [x] 4.3 Add tests for out-of-range port rejection (port=0, port=65536) in `check_certificate` and `add_monitored_host`
- [x] 4.4 Add tests for `cert-monitor://report` resource: bucketed output, empty store, and no live fetch

## 5. Documentation

- [x] 5.1 Update `README.md` to include Claude Desktop JSON configuration snippet with `"command": "uv"` and `"args": ["run", "mcp-certificate-monitor"]`
