## Why

The `issuer` field currently stores only the `commonName` component of the issuer's Distinguished Name (e.g., `"R11"` instead of `"C=US, O=Let's Encrypt, CN=R11"`). This loses organizational identity — two CAs from different organizations can share the same CN, making the stored issuer ambiguous and less useful for auditing or grouping certificates by CA.

## What Changes

- `_normalize_dn()` in `cert.py` is replaced with a function that formats the **full RFC 4514-style DN string** (e.g., `"C=US, O=Let's Encrypt, CN=R11"`) rather than extracting only the CN value.
- The `subject` field follows the same rule for consistency — it will also become the full DN.
- The `certificate-fetching` spec is updated to reflect the new string format for `subject` and `issuer`.

## Capabilities

### New Capabilities

*(none)*

### Modified Capabilities

- `certificate-fetching`: The `subject` and `issuer` fields of `CertResult` now contain the full RFC 4514 DN string (all RDN components joined with `, `) instead of only the `commonName` value.

## Impact

- **`cert.py`**: `_normalize_dn()` logic changes — no field additions or removals.
- **`store.py`**: No changes; `CertResult` is stored as-is, so existing stored records will still deserialize correctly (the `issuer` field remains `str`).
- **Tests**: Any test asserting a specific `subject` or `issuer` string value must be updated to expect the full DN.
- **Stored data**: Records already written to `hosts.json` will retain their old short CN values; they are not migrated. Fresh fetches will populate the full DN going forward.
