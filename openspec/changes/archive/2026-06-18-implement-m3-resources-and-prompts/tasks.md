## 1. MCP Resources

- [x] 1.1 Add `cert-monitor://hosts` list resource to `server.py` using `@mcp.resource()`, reading from `store.list_hosts()` and returning JSON
- [x] 1.2 Add `cert-monitor://hosts/{domain}` template resource to `server.py` using `@mcp.resource()`, reading from `store.get_host(domain)` and returning JSON; handle missing domain with an error JSON response

## 2. MCP Prompts

- [x] 2.1 Add `audit_certificates` prompt to `server.py` using `@mcp.prompt()`, embedding expiry report data from `store.list_hosts()` in the returned message list
- [x] 2.2 Add `plan_renewal(domain: str)` prompt to `server.py` using `@mcp.prompt()`, embedding stored host data for the given domain; handle missing domain gracefully

## 3. Tests

- [x] 3.1 Add tests for the `cert-monitor://hosts` list resource: populated store, empty store, and post-add state
- [x] 3.2 Add tests for the `cert-monitor://hosts/{domain}` template resource: known domain, unknown domain, and post-scan update
- [x] 3.3 Add tests for the `audit_certificates` prompt: returns non-empty message list, includes host data, works with empty store
- [x] 3.4 Add tests for the `plan_renewal` prompt: known domain includes cert details, unknown domain returns informative message
