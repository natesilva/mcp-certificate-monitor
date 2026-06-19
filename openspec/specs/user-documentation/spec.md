# User Documentation

## Purpose

Defines requirements for end-user facing documentation: the overview document explaining what the MCP does, and README.md serving as the Claude Desktop setup guide.

## Requirements

### Requirement: Overview document explains the MCP in plain language
The project SHALL provide `docs/overview.md` that explains what the MCP Certificate Monitor is, what problems it solves, and what a user can do with it — written for a non-developer audience with no prior knowledge of MCP or certificate management tooling.

#### Scenario: Overview answers "what is this for?"
- **WHEN** a user reads `docs/overview.md`
- **THEN** it SHALL explain in plain language that the server lets Claude monitor SSL/TLS certificate expiry across a list of domains through natural conversation

#### Scenario: Overview includes a sample conversation
- **WHEN** a user reads `docs/overview.md`
- **THEN** it SHALL include at least one example exchange showing a realistic user message and Claude's response

#### Scenario: Overview covers common workflows
- **WHEN** a user reads `docs/overview.md`
- **THEN** it SHALL describe how to add a domain, run a scan, get an expiry report, and handle a certificate close to expiry

#### Scenario: Overview links to setup and reference
- **WHEN** a user reads `docs/overview.md`
- **THEN** it SHALL include a relative link to `README.md` for setup and to `docs/reference.md` for the full tool/resource/prompt reference

### Requirement: README serves as the Claude Desktop setup guide
`README.md` SHALL function as the primary getting-started guide for end-users, covering prerequisites, installation, Claude Desktop configuration, and a verification step.

#### Scenario: README includes prerequisites
- **WHEN** a user reads `README.md`
- **THEN** it SHALL list what the user needs before starting (uv, Claude Desktop)

#### Scenario: README includes the Claude Desktop config snippet
- **WHEN** a user reads `README.md`
- **THEN** it SHALL include the JSON block for `claude_desktop_config.json` with the correct `command`, `args`, and `cwd` for `uv run mcp-certificate-monitor`

#### Scenario: README explains how to verify the connection
- **WHEN** a user reads `README.md`
- **THEN** it SHALL describe how to confirm the server is connected after restarting Claude Desktop

#### Scenario: README links to overview and developer docs
- **WHEN** a user reads `README.md`
- **THEN** it SHALL include relative links to `docs/overview.md` and `docs/reference.md`
