## Context

The project has six documentation files written during initial development. They were authored with a developer mindset: architecture diagrams, module layouts, MCP internals, and configuration syntax are all front-and-center. The actual primary audience — end-users who want to connect the server to Claude Desktop and start monitoring certificates — has to dig through developer material to find what they need.

The chosen restructuring is **Option B**: README becomes the setup guide, and a new `overview.md` answers "what is this for?"

## Goals / Non-Goals

**Goals:**
- Rewrite README.md as a step-by-step Claude Desktop setup guide
- Create `docs/overview.md` as a concise, plain-language explanation of what the MCP does
- Rename `docs/tools-resources-prompts.md` → `docs/reference.md` (shorter, clearer for developers)
- Consolidate developer setup into the existing `docs/development.md`
- Delete `docs/architecture.md`, `docs/configuration.md`, and `docs/usage.md`

**Non-Goals:**
- Changes to server code, tools, resources, or prompts
- Changes to `docs/planning/`
- Preserving architecture documentation (no target audience in new structure)

## Decisions

### README.md = setup guide

**Decision**: README becomes the primary setup guide (prerequisites → config JSON → verification → first steps), not the "what is this?" overview.

**Rationale**: GitHub visitors who find the repo already have some intent — they want to use it. The most useful first thing they can see is how to get it working. The "what is this for?" question is answered by the repo description and the new overview.md. Option A (README = overview) would require visitors to click through to a second doc before they can do anything.

**Alternative considered**: README as a minimal overview with links. Rejected — adds a navigation hop for the most common case (someone who wants to install it).

### docs/overview.md = what it's for + example conversation

**Decision**: `overview.md` contains: the problem it solves, who it's for, a sample conversation, and links to setup and reference.

**Rationale**: Separating "what/why" from "how to install" lets each doc do one thing well. The overview can be conversational and motivating; the README can be procedural.

### docs/architecture.md deleted

**Decision**: Remove without replacement.

**Rationale**: Architecture documentation is for contributors modifying the codebase. The new structure has no contributor-facing doc category — `docs/development.md` covers running/testing, and code architecture is better understood by reading the source. The file had 130 lines but is not referenced by any user-facing workflow.

### docs/configuration.md deleted, content absorbed into README

**Decision**: The 24-line configuration doc (just the JSON snippet) moves into README.md and is no longer a standalone file.

**Rationale**: The only content was the Claude Desktop JSON — which belongs in the setup guide.

### docs/usage.md deleted, workflow examples move to docs/overview.md

**Decision**: Conversation workflow examples (add host, scan, report, etc.) move into `overview.md`.

**Rationale**: The workflows exist to show what's possible, which is a "what is this for?" concern. A developer reading `reference.md` doesn't need them; a new user reading `overview.md` does.

### docs/tools-resources-prompts.md → docs/reference.md

**Decision**: Rename the file; keep the content.

**Rationale**: `reference.md` is a standard name that signals "API reference" to developers. The old name was descriptive but long.

## Risks / Trade-offs

- [External links to old doc filenames will break] → Acceptable: this is a personal/open-source project without a published docs site; no known inbound links to specific doc pages.
- [Deleting architecture.md loses institutional context] → Mitigation: content is preserved in git history; the information it contained is also derivable from reading the source code.
- [README as setup guide may feel long for a GitHub landing page] → Mitigation: keep it tight — prerequisites, JSON snippet, restart instruction, verification step. Should be under 50 lines.
