## Why

M2 delivered a fully functional FastMCP server with five tools, but the server exposes no MCP Resources or Prompts. Resources allow an AI host to read stored state directly (without calling tools), and Prompts provide structured templates for recurring workflows like auditing expiring certificates and planning renewals — completing the MCP surface area defined in the project overview.

## What Changes

- Add MCP Resources to `server.py` for reading stored host data:
  - `cert-monitor://hosts` — a list resource returning all monitored hosts and their last-checked certificate results
  - `cert-monitor://hosts/{domain}` — a template resource returning a single host's stored state by domain
- Add MCP Prompt templates to `server.py` for structured workflows:
  - `audit_certificates` — prompts the AI to analyze the current expiry report and surface critical/warning hosts
  - `plan_renewal` — given a domain, prompts the AI to draft a renewal action plan for that certificate
- Add pytest tests covering the new resources and prompts

## Capabilities

### New Capabilities
- `mcp-resources`: MCP Resources exposing stored host state for direct read access by an AI host, using the `cert-monitor://` URI scheme.
- `mcp-prompts`: MCP Prompt templates for structured certificate audit and renewal workflows.

### Modified Capabilities
<!-- None — resources and prompts are additive; no existing specs require behavior changes. -->

## Impact

- **Modified files**: `src/mcp_certificate_monitor/server.py` (add resources and prompts), `tests/test_server.py` (add resource and prompt tests)
- **Dependencies**: No new runtime dependencies
- **No breaking changes** — existing tools are unchanged
