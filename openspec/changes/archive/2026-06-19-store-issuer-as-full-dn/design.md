## Context

`CertResult.issuer` (and `subject`) are produced by `_normalize_dn()` in `cert.py`. That function currently short-circuits on the first `commonName` attribute it finds and returns only that string. The raw `getpeercert()` data from Python's `ssl` module exposes the full DN as a nested tuple of RDN tuples — all the information needed for a complete DN string is already available; it is simply being discarded.

## Goals / Non-Goals

**Goals:**
- `_normalize_dn()` returns a full DN string with all RDN components (e.g., `"C=US, O=Let's Encrypt, CN=R11"`) for both issuer and subject fields.
- The format is consistent and human-readable (RFC 4514-style, `key=value` pairs separated by `, `).
- Existing tests are updated to assert full DN strings.

**Non-Goals:**
- Migrating previously stored `hosts.json` data — old records keep their short CN values.
- Strict RFC 4514 ordering or escaping of special characters — the stdlib already provides the attribute names and values as strings; basic `key=value, ...` formatting is sufficient.
- Separate fields for individual DN components (C, O, OU, CN) — `issuer` and `subject` remain a single `str`.

## Decisions

**Replace the CN-extraction logic with full RDN serialization.**

Current behavior in `_normalize_dn()`:
1. Iterates RDNs looking for `commonName`, returns it immediately.
2. Falls back to joining only the *first* RDN's pairs if no CN is found.

New behavior:
1. Flatten all RDNs into a single sequence of `key=value` pairs, joined with `", "`.
2. If the sequence is empty, return `""` (unchanged sentinel behavior).

This is the minimal change that fixes the information loss. No alternative representations (e.g., slash-delimited `/C=US/O=...`) are considered because `, ` delimited RFC 4514 is the conventional format used in most certificate tooling.

**Apply the same logic to both `subject` and `issuer`.**

The proposal names only `issuer` explicitly, but `subject` goes through the same `_normalize_dn()` call and has the same problem. Fixing both is strictly more consistent, avoids a future follow-up change, and requires no extra work since it is the same code path.

## Risks / Trade-offs

- **Stored data skew**: Records in `hosts.json` written before this change will have short CN values; records written after will have full DNs. Mixed displays in MCP tool output are possible until a re-fetch is done. Mitigation: document in release notes; no automated migration needed for a personal tool.
- **Test churn**: Tests that assert exact `issuer` or `subject` strings must be updated. Mitigation: tests are the right place to assert this behavior — updating them is the intended outcome.

## Migration Plan

No deployment steps. The change takes effect on the next `fetch_certificate()` call. Existing `hosts.json` is not touched.

Rollback: revert the `_normalize_dn()` change; no schema migration needed.
