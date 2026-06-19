## Context

The project is complete and working, but documentation lives in two inconvenient
places: `docs/plan.md` is an original planning file (internal artifact) that was
never reorganized, and `README.md` stops at "how to run." Users and contributors
need clear reference material without digging into source code.

## Goals / Non-Goals

**Goals:**
- Relocate `docs/plan.md` to `docs/planning/plan.md` to signal it is a planning artifact
- Write three purpose-built docs under `docs/`: architecture, MCP API reference, configuration
- Update `README.md` with a Documentation section linking to those files

**Non-Goals:**
- Changing any source code, tests, or dependencies
- Auto-generating docs from docstrings (no tooling change)
- Writing a changelog or contribution guide

## Decisions

### D1: Flat `docs/` with a `planning/` subdirectory

Move `plan.md` under `docs/planning/` so the root of `docs/` only holds user-facing
material. Alternative (delete `plan.md`) was rejected — the planning file has historical
value and is already referenced in the OpenSpec workflow.

### D2: Three separate docs files, not one large one

- `architecture.md` — module layout, data models, storage schema, design decisions
- `tools-resources-prompts.md` — complete MCP API reference (tools, resources, prompts)
- `configuration.md` — storage paths per OS, Claude Desktop config, env/port options

Splitting keeps each file focused. Alternative (single `docs/reference.md`) would grow
unwieldy as the server evolves.

### D3: README links use relative Markdown paths

Links in `README.md` are relative (e.g., `docs/architecture.md`) so they work on
GitHub and locally without needing an absolute URL.

## Risks / Trade-offs

- [Stale docs] Docs written today may drift from code as features change → Mitigation: keep docs at the spec level (what the system does, not line-by-line) so they remain accurate longer
- [plan.md move breaks any existing links] → Mitigation: the file has no inbound links yet; the openspec planning system references it only by path which will be updated
