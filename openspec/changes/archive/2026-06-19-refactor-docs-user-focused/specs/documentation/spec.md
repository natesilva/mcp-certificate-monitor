## REMOVED Requirements

### Requirement: Architecture documentation exists
**Reason**: No target audience in the new documentation structure. Developer-facing architecture context is better understood by reading the source code. Contributor onboarding is not an active use case.
**Migration**: Content is preserved in git history. No replacement file.

### Requirement: Configuration documentation exists
**Reason**: The standalone `docs/configuration.md` contained only the Claude Desktop JSON snippet. That content is absorbed into `README.md` as part of the setup guide.
**Migration**: Claude Desktop configuration is documented in `README.md`.

### Requirement: End-user usage guide exists
**Reason**: `docs/usage.md` is replaced by `docs/overview.md`, which covers the same workflows in a more accessible format alongside the "what is this for?" context.
**Migration**: Workflow examples and conversation patterns move to `docs/overview.md`.

## MODIFIED Requirements

### Requirement: MCP API reference documentation exists
The project SHALL provide `docs/reference.md` documenting every MCP tool, resource URI, and prompt template exposed by the server.

#### Scenario: All five tools are documented
- **WHEN** a developer reads `docs/reference.md`
- **THEN** it SHALL document `check_certificate`, `add_monitored_host`, `remove_host`, `scan_all`, and `get_expiry_report` with parameters and return values

#### Scenario: All three resources are documented
- **WHEN** a developer reads `docs/reference.md`
- **THEN** it SHALL document `mcp-certificate-monitor://hosts`, `mcp-certificate-monitor://hosts/{domain}`, and `mcp-certificate-monitor://report` with example response shapes

#### Scenario: Both prompts are documented
- **WHEN** a developer reads `docs/reference.md`
- **THEN** it SHALL document `audit_certificates` and `plan_renewal` prompts with their purpose and the context they embed

### Requirement: README links to documentation
`README.md` SHALL include a Documentation section with relative Markdown links to `docs/overview.md` and `docs/reference.md`.

#### Scenario: Documentation section present in README
- **WHEN** a user opens `README.md`
- **THEN** it SHALL contain a section with links to `docs/overview.md` and `docs/reference.md`

#### Scenario: Links use relative paths
- **WHEN** a user views the README on GitHub or locally
- **THEN** each documentation link SHALL resolve correctly using a relative path
