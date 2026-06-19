## Why

The project is missing user-facing documentation: `docs/plan.md` is an internal
planning artifact that has been left at the root of `docs/`, and `README.md` only
covers the bare minimum to run the server. Developers and users need a clean docs
directory with purpose-built documentation, and the planning file should be
co-located with other planning artifacts.

## What Changes

- Move `docs/plan.md` → `docs/planning/plan.md` (reclassifies it as a planning artifact)
- Create `docs/architecture.md` — module layout, data models, storage schema, and design decisions
- Create `docs/tools-resources-prompts.md` — reference for all MCP tools, resources, and prompts exposed by the server
- Create `docs/configuration.md` — deployment options, storage paths, integration config (Claude Desktop, etc.)
- Update `README.md` to link to each new doc page

## Capabilities

### New Capabilities

- `documentation`: User-facing docs covering architecture, MCP API reference, and configuration

### Modified Capabilities

<!-- No existing capability specs have requirement changes — this is purely additive documentation. -->

## Impact

- `docs/` directory structure changes (one file moved, three new files added)
- `README.md` gains a "Documentation" section with links
- No source code changes; no API changes
