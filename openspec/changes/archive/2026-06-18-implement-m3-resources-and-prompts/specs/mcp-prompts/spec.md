## ADDED Requirements

### Requirement: audit_certificates prompt
The system SHALL expose an MCP Prompt named `audit_certificates` (no arguments) that returns a list of messages priming the AI to analyze the current certificate expiry report. The prompt SHALL embed the current expiry report (fetched via `get_expiry_report()` logic or `store.list_hosts()`) directly in the message content so the AI can act without calling additional tools.

#### Scenario: Prompt returns a non-empty message list
- **WHEN** the `audit_certificates` prompt is requested
- **THEN** the response is a non-empty list of messages containing certificate expiry data and instructions to identify critical and warning hosts

#### Scenario: Prompt content includes host status data
- **WHEN** monitored hosts are in the store and the `audit_certificates` prompt is requested
- **THEN** the message content includes domain names and their days-remaining or error status

#### Scenario: Prompt works with empty store
- **WHEN** no hosts are in the store and the `audit_certificates` prompt is requested
- **THEN** the response is a valid message list without error (content may note that no hosts are monitored)

### Requirement: plan_renewal prompt
The system SHALL expose an MCP Prompt named `plan_renewal` with a required `domain: str` argument that returns a list of messages priming the AI to draft a certificate renewal action plan for that specific domain. The prompt SHALL embed the stored certificate data for the requested domain (from `store.get_host(domain)`) in the message content. If the domain is not in the store, the prompt SHALL return a message indicating the domain is not monitored.

#### Scenario: Prompt returns renewal guidance for a known domain
- **WHEN** the `plan_renewal` prompt is requested with a domain present in the store
- **THEN** the response is a non-empty list of messages containing that domain's certificate details and a request for the AI to produce a renewal action plan

#### Scenario: Prompt for unknown domain returns informative message
- **WHEN** the `plan_renewal` prompt is requested with a domain not in the store
- **THEN** the response is a valid message list with content indicating the domain is not currently monitored, and no exception propagates

#### Scenario: Prompt includes stored certificate details
- **WHEN** a host has a `last_result` with `not_after` and `days_remaining` and the `plan_renewal` prompt is requested
- **THEN** the message content includes the certificate expiry date and days remaining for that domain
