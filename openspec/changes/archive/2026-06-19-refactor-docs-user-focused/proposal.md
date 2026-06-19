## Why

The current docs are written for developers — they lead with architecture, configuration syntax, and MCP internals — but the primary audience is end-users who just want to connect the server to Claude Desktop and start monitoring certificates. This refactor reorients the documentation around that audience, with a clear separation between user-facing and developer-facing material.

## What Changes

- **README.md** becomes the primary setup guide: prerequisites, configuration JSON, and verification steps for a new user getting started with Claude Desktop
- **`docs/overview.md`** (new) — concise plain-language explanation of what the MCP is for, what problems it solves, and example conversation snippets to set expectations
- **`docs/reference.md`** — renames/replaces `tools-resources-prompts.md` with the same content; developer-facing MCP API reference
- **`docs/development.md`** — updated to be the sole developer setup guide; absorbs the storage paths section currently in development.md
- **`docs/architecture.md`** — **REMOVED** (no target audience in new structure)
- **`docs/configuration.md`** — **REMOVED** (content absorbed into README.md)
- **`docs/usage.md`** — **REMOVED** (conversation workflow examples move into `docs/overview.md`)

## Capabilities

### New Capabilities

- `user-documentation`: End-user facing docs — what the MCP is for (overview.md) and how to connect it to Claude Desktop (README.md)

### Modified Capabilities

- `documentation`: Existing docs structure changes; developer-facing material restructured into reference.md and development.md

## Impact

- All files under `docs/` except `docs/planning/` are modified or deleted
- `README.md` is rewritten
- No code changes; no API changes; no dependency changes
