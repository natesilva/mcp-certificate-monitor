## 1. Reorganize planning file

- [x] 1.1 Create `docs/planning/` directory
- [x] 1.2 Move `docs/plan.md` to `docs/planning/plan.md`

## 2. Write architecture documentation

- [x] 2.1 Create `docs/architecture.md` with module layout section (purpose of each file in `src/mcp_certificate_monitor/`)
- [x] 2.2 Add storage schema section to `docs/architecture.md` (JSON structure of `hosts.json` with all fields)
- [x] 2.3 Add data models section to `docs/architecture.md` (`CertResult` and `MonitoredHost` fields)
- [x] 2.4 Add key design decisions section to `docs/architecture.md` (atomic writes, no in-memory cache, risk thresholds)

## 3. Write MCP API reference

- [x] 3.1 Create `docs/tools-resources-prompts.md` with all five tools documented (parameters, return values, behavior)
- [x] 3.2 Add all three resource URIs to `docs/tools-resources-prompts.md` with example response shapes
- [x] 3.3 Add both prompts to `docs/tools-resources-prompts.md` with purpose and embedded context description

## 4. Write configuration documentation

- [x] 4.1 Create `docs/configuration.md` with platform storage paths (macOS and Linux)
- [x] 4.2 Add Claude Desktop integration section with `claude_desktop_config.json` snippet
- [x] 4.3 Add MCP Inspector launch command to `docs/configuration.md`

## 5. Write end-user usage guide

- [x] 5.1 Create `docs/usage.md` with common Claude Desktop workflows (add/remove host, scan, report, list hosts, error handling, post-renewal verification, cached vs. live data)
- [x] 5.2 Add prompt workflow examples to `docs/usage.md` (`audit_certificates` and `plan_renewal`)
- [x] 5.3 Add an end-to-end example session to `docs/usage.md`

## 6. Update README

- [x] 6.1 Add a "Documentation" section to `README.md` with relative links to `docs/usage.md`, `docs/architecture.md`, `docs/tools-resources-prompts.md`, and `docs/configuration.md`
