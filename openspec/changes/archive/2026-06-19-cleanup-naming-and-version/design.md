## Context

The project has two naming inconsistencies introduced during initial development:

1. The on-disk storage directory is `cert-monitor` (via `platformdirs.user_data_dir("cert-monitor")`), while the package is named `mcp-certificate-monitor`. A generic name like `cert-monitor` risks colliding with unrelated tools on the same system.

2. The `FastMCP` server constructor is called without a `version` argument. FastMCP defaults to its own library version (`3.4.2`) when none is provided, so the MCP server advertises the wrong version to AI hosts.

The project is pre-1.0 and unpublished, so there are no backward compatibility constraints.

## Goals / Non-Goals

**Goals:**

- Storage directory name matches the project package name (`mcp-certificate-monitor`)
- MCP resource URI scheme matches the project name (`mcp-certificate-monitor://`)
- Server advertises the project's own version, not FastMCP's version
- `pyproject.toml` remains the single source of truth for the version number

**Non-Goals:**

- Data migration for existing installations
- Changing any functional behavior of the store, server tools, or prompts

## Decisions

### Use `importlib.metadata.version()` for the server version

Alternatives considered:
- **Hardcode `"0.1.0"` in `server.py`**: Simple but creates a second place to update on every release — will drift.
- **Read `pyproject.toml` at runtime**: Works but adds file I/O and path resolution complexity for no benefit.
- **`importlib.metadata.version("mcp-certificate-monitor")`**: Stdlib, zero-cost at import time, always in sync with the installed package version. Chosen.

The call goes in `server.py` at module level so it fails fast if the package metadata is missing (e.g., editable install without metadata).

### Rename both the storage directory and resource URI scheme

The `cert-monitor` string appears in two distinct roles: the filesystem path (via `platformdirs`) and the MCP URI scheme (`cert-monitor://`). Both are renamed to `mcp-certificate-monitor` for consistency with the package name.

Alternative: rename only the storage path and leave the URI scheme unchanged. Rejected — having two different names for the same project adds unnecessary cognitive overhead with no benefit.

## Risks / Trade-offs

- **URI scheme change breaks hardcoded clients** → Acceptable: no published deployments, pre-1.0.
- **Storage path change loses existing data** → Acceptable: same reasoning; explicitly out of scope per proposal.
- **`importlib.metadata` raises `PackageNotFoundError` in some dev environments** → Mitigation: standard `uv` / `pip install -e .` installs populate metadata correctly; document in CLAUDE.md if it becomes an issue.
