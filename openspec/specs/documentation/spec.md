# Documentation

## Purpose

Defines requirements for the project's user-facing and contributor-facing documentation. Covers the placement of planning artifacts, MCP API reference, and README linkage.

## Requirements

### Requirement: Planning file is relocated to docs/planning/
The project SHALL move `docs/plan.md` to `docs/planning/plan.md` so that user-facing
documentation and internal planning artifacts are not mixed at the same directory level.

#### Scenario: plan.md exists at new path
- **WHEN** the change is applied
- **THEN** `docs/planning/plan.md` SHALL exist and `docs/plan.md` SHALL not exist

### Requirement: MCP API reference documentation exists
The project SHALL provide `docs/reference.md` documenting every MCP tool, resource URI, and prompt template exposed by the server.

#### Scenario: All five tools are documented
- **WHEN** a developer reads `docs/reference.md`
- **THEN** it SHALL document `check_certificate`, `add_monitored_host`, `remove_host`,
  `scan_all`, and `get_expiry_report` with parameters and return values

#### Scenario: All three resources are documented
- **WHEN** a developer reads `docs/reference.md`
- **THEN** it SHALL document `mcp-certificate-monitor://hosts`, `mcp-certificate-monitor://hosts/{domain}`, and `mcp-certificate-monitor://report`
  with example response shapes

#### Scenario: Both prompts are documented
- **WHEN** a developer reads `docs/reference.md`
- **THEN** it SHALL document `audit_certificates` and `plan_renewal` prompts with their purpose
  and the context they embed

### Requirement: README links to documentation
`README.md` SHALL include a Documentation section with relative Markdown links to
`docs/overview.md` and `docs/reference.md`.

#### Scenario: Documentation section present in README
- **WHEN** a user opens `README.md`
- **THEN** it SHALL contain a section with links to `docs/overview.md` and `docs/reference.md`

#### Scenario: Links use relative paths
- **WHEN** a user views the README on GitHub or locally
- **THEN** each documentation link SHALL resolve correctly using a relative path
