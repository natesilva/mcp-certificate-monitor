## Context

M2 produced a server with five tools covering live certificate checks and host management. The MCP protocol also defines Resources (readable data endpoints) and Prompts (reusable message templates). The project overview specifies all three surface areas: tools (done), resources for reading stored state, and prompt templates for audit/renewal workflows. FastMCP 3.x has first-class decorators for all three.

## Goals / Non-Goals

**Goals:**
- Expose stored host state via two MCP Resources using a `cert-monitor://` URI scheme
- Provide two MCP Prompt templates for recurring workflows (audit and renewal planning)
- Keep implementation entirely within `server.py` — no new modules or data models

**Non-Goals:**
- Writing to the store via resources (resources are read-only)
- Streaming or pagination of large host lists
- New external dependencies

## Decisions

### Resource URI scheme: `cert-monitor://`
Using a namespaced URI scheme (`cert-monitor://hosts`, `cert-monitor://hosts/{domain}`) avoids collisions with other MCP servers and clearly scopes the resource to this server. FastMCP supports URI template syntax for parameterized resources.

**Alternative considered**: flat path style (e.g., `hosts`, `hosts/{domain}`) — rejected because URI schemes provide clearer namespacing in multi-server AI hosts.

### Resource return format: JSON string via `store.list_hosts()` / `store.get_host()`
Resources return a JSON-serialized string of the stored `MonitoredHost` data. This keeps the data model consistent with what tools already return (`model_dump(mode="json")`), and JSON is the natural wire format for AI consumption.

**Alternative considered**: Returning a `TextContent` with a formatted summary — rejected because raw JSON is more flexible and the AI can format it as needed.

### Prompt return type: `list[Message]` with embedded context
Each prompt returns a list of messages that prime the AI with relevant stored data (e.g., the expiry report for `audit_certificates`, and a host's stored result for `plan_renewal`). This is richer than a bare text string and matches FastMCP's `@mcp.prompt()` convention.

**Alternative considered**: Returning a plain string — rejected because embedding live data in the prompt (fetched at prompt-request time from the store) makes the templates immediately actionable without requiring the AI to call tools first.

### `plan_renewal` takes `domain: str` as argument
The renewal prompt is parameterized by domain so it can target a specific certificate. FastMCP prompts support typed arguments natively.

## Risks / Trade-offs

- **Stale data in prompts**: Resources and prompts read from the store (not live). If `scan_all` hasn't been called recently, the AI may work from outdated certificate data. Mitigation: prompt text should remind the AI to call `scan_all` first if data freshness matters.
- **Missing domain in `plan_renewal`**: If the requested domain is not in the store, `store.get_host()` raises `KeyError`. Mitigation: the resource handler should catch this and return a clear error message rather than propagating the exception.
