## 1. Update DN Normalization Logic

- [x] 1.1 Rewrite `_normalize_dn()` in `cert.py` to join all RDN components across all RDNs as `key=value` pairs separated by `", "`, returning `""` only when the sequence is empty

## 2. Update Tests

- [x] 2.1 Update any existing test fixtures or assertions that expect only the `commonName` value for `issuer` or `subject` to expect the full DN string instead
- [x] 2.2 Add a unit test for `_normalize_dn()` covering: multi-component DN (C + O + CN), single-component DN (CN only), and empty input
