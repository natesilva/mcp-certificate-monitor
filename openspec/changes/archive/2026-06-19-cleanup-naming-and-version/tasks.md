## 1. Storage Path

- [x] 1.1 In `src/mcp_certificate_monitor/store.py`, change `platformdirs.user_data_dir("cert-monitor")` to `platformdirs.user_data_dir("mcp-certificate-monitor")`

## 2. Server Version and Resource URIs

- [x] 2.1 In `src/mcp_certificate_monitor/server.py`, add `from importlib.metadata import version` import
- [x] 2.2 Change `FastMCP("Certificate Monitor")` to `FastMCP("Certificate Monitor", version=version("mcp-certificate-monitor"))`
- [x] 2.3 Rename `@mcp.resource("cert-monitor://hosts")` → `@mcp.resource("mcp-certificate-monitor://hosts")`
- [x] 2.4 Rename `@mcp.resource("cert-monitor://hosts/{domain}")` → `@mcp.resource("mcp-certificate-monitor://hosts/{domain}")`
- [x] 2.5 Rename `@mcp.resource("cert-monitor://report")` → `@mcp.resource("mcp-certificate-monitor://report")`

## 3. Tests

- [x] 3.1 In `tests/test_store.py`, update the fixture path assertion from `"cert-monitor"` to `"mcp-certificate-monitor"`
- [x] 3.2 In `tests/test_server.py`, update the fixture path assertion from `"cert-monitor"` to `"mcp-certificate-monitor"`
- [x] 3.3 Run `pytest` and confirm all tests pass
