# Documentation

## Purpose

Defines requirements for the project's user-facing and contributor-facing documentation. Covers the placement of planning artifacts, architecture reference, MCP API reference, configuration guide, end-user usage guide, and README linkage.

## Requirements

### Requirement: Planning file is relocated to docs/planning/
The project SHALL move `docs/plan.md` to `docs/planning/plan.md` so that user-facing
documentation and internal planning artifacts are not mixed at the same directory level.

#### Scenario: plan.md exists at new path
- **WHEN** the change is applied
- **THEN** `docs/planning/plan.md` SHALL exist and `docs/plan.md` SHALL not exist

### Requirement: Architecture documentation exists
The project SHALL provide `docs/architecture.md` covering module layout, data models,
storage schema, and key design decisions so that contributors can understand the system
without reading all source code.

#### Scenario: Architecture doc covers module layout
- **WHEN** a user reads `docs/architecture.md`
- **THEN** it SHALL describe the purpose of each file in `src/mcp_certificate_monitor/`

#### Scenario: Architecture doc covers storage schema
- **WHEN** a user reads `docs/architecture.md`
- **THEN** it SHALL document the JSON structure of `hosts.json` including all fields

#### Scenario: Architecture doc covers data models
- **WHEN** a user reads `docs/architecture.md`
- **THEN** it SHALL describe `CertResult` and `MonitoredHost` Pydantic models and their fields

### Requirement: MCP API reference documentation exists
The project SHALL provide `docs/tools-resources-prompts.md` documenting every MCP tool,
resource URI, and prompt template exposed by the server.

#### Scenario: All five tools are documented
- **WHEN** a user reads `docs/tools-resources-prompts.md`
- **THEN** it SHALL document `check_certificate`, `add_monitored_host`, `remove_host`,
  `scan_all`, and `get_expiry_report` with parameters and return values

#### Scenario: All three resources are documented
- **WHEN** a user reads `docs/tools-resources-prompts.md`
- **THEN** it SHALL document `mcp-certificate-monitor://hosts`, `mcp-certificate-monitor://hosts/{domain}`, and `mcp-certificate-monitor://report`
  with example response shapes

#### Scenario: Both prompts are documented
- **WHEN** a user reads `docs/tools-resources-prompts.md`
- **THEN** it SHALL document `audit_certificates` and `plan_renewal` prompts with their purpose
  and the context they embed

### Requirement: Configuration documentation exists
The project SHALL provide `docs/configuration.md` covering platform-specific storage
paths, Claude Desktop integration config, and the MCP Inspector launch command.

#### Scenario: Storage paths documented per platform
- **WHEN** a user reads `docs/configuration.md`
- **THEN** it SHALL list the default `hosts.json` path for macOS and Linux

#### Scenario: Claude Desktop config is documented
- **WHEN** a user reads `docs/configuration.md`
- **THEN** it SHALL include the JSON snippet for `claude_desktop_config.json` with the
  correct `command` and `args` for `uv run mcp-certificate-monitor`

### Requirement: End-user usage guide exists
The project SHALL provide `docs/usage.md` showing how to monitor certificates through
natural conversation in Claude Desktop, covering common workflows and example interactions.

#### Scenario: Common workflows are documented
- **WHEN** a user reads `docs/usage.md`
- **THEN** it SHALL cover adding/removing monitored hosts, running a scan, getting an
  expiry report, listing monitored hosts, handling errors, verifying a renewed certificate,
  and the difference between reports (cached) and live scans

#### Scenario: Prompt workflows are documented
- **WHEN** a user reads `docs/usage.md`
- **THEN** it SHALL show how to invoke `audit_certificates` and `plan_renewal` through
  natural language and describe what output to expect

#### Scenario: Example session is included
- **WHEN** a user reads `docs/usage.md`
- **THEN** it SHALL include an end-to-end example conversation showing a realistic
  weekly certificate check-in workflow

### Requirement: README links to documentation
`README.md` SHALL include a Documentation section with relative Markdown links to
`docs/usage.md`, `docs/architecture.md`, `docs/tools-resources-prompts.md`, and `docs/configuration.md`.

#### Scenario: Documentation section present in README
- **WHEN** a user opens `README.md`
- **THEN** it SHALL contain a section titled "Documentation" with links to each doc file

#### Scenario: Links use relative paths
- **WHEN** a user views the README on GitHub or locally
- **THEN** each documentation link SHALL resolve correctly using a relative path
