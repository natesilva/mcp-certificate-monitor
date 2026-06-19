# Using MCP Certificate Monitor

This guide shows how to monitor SSL/TLS certificates through natural conversation in Claude Desktop once the server is connected.

## Setup

Wire up the server following the [Configuration guide](configuration.md#claude-desktop-integration), then restart Claude Desktop. You should see the `cert-monitor` server listed in Claude's tool panel.

## Workflows

### Add a domain to monitor

Tell Claude which domain to track:

> **You:** Please start monitoring the SSL certificate for example.com.

Claude will call `add_monitored_host`, fetch the certificate immediately, and report back:

> **Claude:** I've added example.com to the monitored hosts. Its certificate is issued by Let's Encrypt, expires September 1, 2026 (76 days from now), and covers example.com and www.example.com. No issues found.

To monitor a non-standard port:

> **You:** Add api.example.com on port 8443 to the monitored hosts.

### Check a certificate right now

For a one-off check without adding to the monitored list:

> **You:** What's the current SSL certificate status for github.com?

Claude calls `check_certificate` and reports the issuer, expiry date, and days remaining. This does not save anything — it's a live spot-check.

### Scan all monitored hosts

To refresh every host at once:

> **You:** Run a scan of all my monitored certificates.

Claude calls `scan_all`, which checks every host in parallel and updates the stored results. It will summarize the outcome:

> **Claude:** Scanned 8 hosts. All certificates are healthy — the soonest expiry is api.internal.example.com in 23 days (warning range).

### Get an expiry report

For a quick overview bucketed by risk:

> **You:** Show me my certificate expiry report.

Claude calls `get_expiry_report` and presents the results grouped as **critical** (≤ 14 days or errored), **warning** (15–30 days), and **ok** (> 30 days). This reads stored data — no live network calls.

### Remove a domain

> **You:** Stop monitoring staging.example.com.

### List all monitored hosts

To see everything you're tracking:

> **You:** What domains am I monitoring?

Claude reads the stored host list and summarizes them — domain, port (if non-standard), and days until expiry based on the last scan.

### Ask about a specific host

You can ask Claude to look up stored details for any monitored domain:

> **You:** When was the certificate for example.com last checked, and who issued it?

Claude reads the stored record and answers from cached data.

### Handle a host with errors

If a domain is unreachable or has a TLS problem, it shows up in the **critical** bucket of the expiry report with an error message instead of a days-remaining count. Ask Claude about it directly:

> **You:** Why is mail.example.com showing an error in the report?

> **Claude:** The last check for mail.example.com failed with "Connection refused" on port 443. This could mean the service is down, the port changed, or a firewall is blocking the check. I'd recommend verifying the domain is reachable before investigating the certificate itself.

Run a scan after the underlying issue is fixed and the error will clear.

### Verify a renewed certificate

After renewing a certificate, confirm the new expiry is live:

> **You:** I just renewed the certificate for mail.example.com — can you check it?

Claude calls `check_certificate` for a live fetch (no stored data) and reports the new expiry date. If it still shows the old date, the renewal may not have propagated yet.

### Reports vs. live scans

`get_expiry_report` reads **stored** data — it's fast but only as fresh as your last scan. If you haven't scanned recently, run a scan first:

> **You:** Scan all hosts, then give me the expiry report.

For a quick check when you know data is recent, asking for a report alone is fine.

---

## Deeper analysis with prompts

The server includes two prompt templates that prime Claude for structured analysis.

### Certificate audit

Ask Claude to audit your entire portfolio and prioritize action:

> **You:** Run a certificate audit for me.

Claude uses the `audit_certificates` prompt, which pulls the current expiry report and instructs it to:

1. Identify certificates needing immediate action (≤ 14 days or errored)
2. Prioritize warning-range certificates
3. Flag any check errors for investigation
4. Recommend a renewal order

You'll get a structured analysis rather than a raw data dump — useful when you have many domains and want to know what to tackle first.

### Renewal planning

For a specific domain, ask Claude to draft a renewal plan:

> **You:** Create a renewal plan for api.example.com.

Claude uses the `plan_renewal` prompt, which loads the full stored record for that domain (including the last certificate result) and produces:

1. An urgency assessment based on days remaining
2. Step-by-step renewal process recommendations
3. Validation steps to confirm the renewal worked
4. A suggested monitoring frequency going forward

If the domain isn't in the monitored list yet, Claude will add it first.

---

## Example session

Here's what a typical weekly check-in might look like:

> **You:** Morning! Can you scan all my certificates and tell me if anything needs attention?

> **Claude:** Running a scan now across your 12 monitored hosts…
>
> Scan complete. One host needs your attention:
>
> - **mail.example.com** — certificate expires in 11 days (critical). Issuer: Let's Encrypt.
>
> Everything else is healthy. The next-soonest expiry is api.example.com in 34 days.

> **You:** Let's plan the renewal for mail.example.com.

> **Claude:** Here's the renewal plan for mail.example.com…
>
> **Urgency:** High — certificate expires 2026-07-01 (11 days). Renew within the next 1–2 days to avoid service interruption.
>
> **Renewal steps:**
> 1. Log into your DNS/hosting provider and initiate a Let's Encrypt renewal…
> *(etc.)*

> **You:** Great. Once I've renewed it, how do I verify it worked?

> **Claude:** After renewing, ask me to check the certificate for mail.example.com. I'll fetch the live certificate and confirm the new expiry date. You can also ask me to run a full scan to update all stored results at once.
