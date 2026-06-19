# MCP Certificate Monitor — Overview

## What it does

MCP Certificate Monitor lets you track SSL/TLS certificate expiry across your domains by talking to Claude. Instead of logging into dashboards or running command-line tools, you just ask Claude questions like "what certificates are expiring soon?" and it checks, stores, and reports the answers for you.

**It's useful if you:**
- Manage one or more websites or services and want to know before a certificate expires
- Have been burned by an expired certificate causing downtime
- Want a low-friction way to keep tabs on certificates without adding yet another monitoring tool

## What you can do

### Add a domain to monitor

> **You:** Please start monitoring the SSL certificate for example.com.

> **Claude:** I've added example.com to the monitored hosts. Its certificate expires September 1, 2026 (76 days from now), issued by Let's Encrypt. No issues found.

Once added, the domain stays in your list. You can have Claude check it anytime, or scan everything at once.

To monitor a non-standard port:

> **You:** Add api.example.com on port 8443 to the monitored hosts.

### Scan all your domains at once

> **You:** Scan all my monitored certificates.

> **Claude:** Scanned 8 hosts. All certificates are healthy — the soonest expiry is api.internal.example.com in 23 days.

### Get an expiry report

> **You:** Show me my certificate expiry report.

Claude groups your certificates into three buckets: **critical** (≤ 14 days or errored), **warning** (15–30 days), and **ok** (> 30 days). This reads stored data — no live network calls.

For fresh results, scan first:

> **You:** Scan all hosts, then give me the expiry report.

### Handle a certificate that's about to expire

> **You:** Morning! Can you scan all my certificates and tell me if anything needs attention?

> **Claude:** Scan complete. One host needs your attention:
>
> - **mail.example.com** — certificate expires in 11 days (critical). Issuer: Let's Encrypt.
>
> Everything else is healthy. The next-soonest expiry is api.example.com in 34 days.

> **You:** Let's plan the renewal for mail.example.com.

> **Claude:** Here's the renewal plan for mail.example.com…
>
> **Urgency:** High — certificate expires in 11 days. Renew within the next 1–2 days to avoid service interruption.
>
> **Renewal steps:**
> 1. Log into your DNS/hosting provider and initiate a Let's Encrypt renewal…

After renewing, verify it worked:

> **You:** I just renewed the certificate for mail.example.com — can you check it?

> **Claude:** The certificate for mail.example.com now expires October 14, 2026 (117 days from now). Renewal confirmed.

## Other things you can ask

- "What domains am I monitoring?" — lists all tracked hosts with days until expiry
- "Stop monitoring staging.example.com." — removes a domain
- "When was the certificate for example.com last checked?" — reads stored details
- "Run a certificate audit for me." — structured analysis that prioritizes what needs attention first
- "What's the SSL status for github.com?" — one-off live check, doesn't add to your monitored list

---

[Setup guide →](https://github.com/natesilva/mcp-certificate-monitor#setup) · [Tool & resource reference →](https://github.com/natesilva/mcp-certificate-monitor/blob/main/docs/reference.md)
