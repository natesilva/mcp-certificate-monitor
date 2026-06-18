# CLAUDE.md

This file provides guidance to Claude Code when working in this repository.

## Project

MCP Certificate Monitor — a FastMCP server that lets an AI host monitor SSL/TLS
certificate expiry across a set of domains. It exposes tools for live certificate
checks and host management, resources for reading stored state, and prompt
templates for structured audit/renewal workflows.

## Stack

- **Runtime**: Python 3.12+
- **MCP framework**: FastMCP 3.x
- **Certificate fetching**: stdlib `ssl` + `socket` (no third-party HTTP client)
- **X.509 parsing**: `cryptography` (for DN normalization)
- **Storage**: JSON file via `platformdirs.user_data_dir("cert-monitor")`
  (e.g. `~/Library/Application Support/cert-monitor/hosts.json` on macOS,
  `~/.local/share/cert-monitor/hosts.json` on Linux)
