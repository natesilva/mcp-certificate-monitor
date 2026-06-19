import asyncio
import json
from datetime import UTC, datetime
from importlib.metadata import version

from fastmcp import FastMCP
from fastmcp.prompts import Message

from mcp_certificate_monitor import cert, store

mcp = FastMCP("Certificate Monitor", version=version("mcp-certificate-monitor"))

CRITICAL_DAYS: int = 14
WARNING_DAYS: int = 30


def _validate_domain(domain: str) -> None:
    if not domain or not domain.strip():
        raise ValueError("domain must not be empty")
    if len(domain) > 253:
        raise ValueError(f"domain must be 253 characters or fewer, got {len(domain)}")


def _validate_port(port: int) -> None:
    if port < 1 or port > 65535:
        raise ValueError(f"port must be between 1 and 65535, got {port}")


@mcp.tool()
def check_certificate(domain: str, port: int = 443) -> dict:
    """Fetch a live SSL/TLS certificate for a domain without updating stored state."""
    _validate_domain(domain)
    _validate_port(port)
    result = cert.fetch_certificate(domain, port)
    return result.model_dump(mode="json")


@mcp.tool()
def add_monitored_host(domain: str, port: int = 443) -> dict:
    """Add a domain to the monitored host list and immediately check its certificate."""
    _validate_domain(domain)
    _validate_port(port)
    store.add_host(domain, port)
    result = cert.fetch_certificate(domain, port)
    store.update_host_result(domain, result)
    host = store.get_host(domain)
    return {"domain": host.domain, "port": host.port, "last_result": result.model_dump(mode="json")}


@mcp.tool()
def remove_host(domain: str) -> str:
    """Remove a domain from the monitored host list."""
    _validate_domain(domain)
    store.remove_host(domain)
    return f"Removed {domain} from monitored hosts."


@mcp.tool()
async def scan_all() -> list[dict]:
    """Check certificates for all monitored hosts in parallel and update stored results."""
    hosts = store.list_hosts()
    if not hosts:
        return []

    loop = asyncio.get_running_loop()

    async def _check(host: store.MonitoredHost) -> dict:
        result = await loop.run_in_executor(None, cert.fetch_certificate, host.domain, host.port)
        store.update_host_result(host.domain, result)
        return {
            "domain": host.domain,
            "days_remaining": result.days_remaining if result.error is None else None,
            "error": result.error,
        }

    return list(await asyncio.gather(*(_check(h) for h in hosts)))


@mcp.resource("mcp-certificate-monitor://hosts")
def list_hosts_resource() -> str:
    """Return all monitored hosts and their last certificate results as JSON."""
    hosts = store.list_hosts()
    return json.dumps([h.model_dump(mode="json") for h in hosts])


@mcp.resource("mcp-certificate-monitor://hosts/{domain}")
def get_host_resource(domain: str) -> str:
    """Return a single monitored host's stored state as JSON."""
    try:
        host = store.get_host(domain)
        return json.dumps(host.model_dump(mode="json"))
    except ValueError:
        return json.dumps({"error": f"Host not found: {domain}"})


@mcp.resource("mcp-certificate-monitor://report")
def get_report_resource() -> str:
    """Return the certificate expiry report bucketed by risk level as JSON."""
    hosts = store.list_hosts()
    critical: list[dict] = []
    warning: list[dict] = []
    ok: list[dict] = []

    for host in hosts:
        entry: dict = {"domain": host.domain, "port": host.port, "days_remaining": None, "error": None}
        if host.last_result is None:
            entry["error"] = "never checked"
            critical.append(entry)
        elif host.last_result.error is not None:
            entry["error"] = host.last_result.error
            critical.append(entry)
        elif host.last_result.days_remaining <= CRITICAL_DAYS:
            entry["days_remaining"] = host.last_result.days_remaining
            critical.append(entry)
        elif host.last_result.days_remaining <= WARNING_DAYS:
            entry["days_remaining"] = host.last_result.days_remaining
            warning.append(entry)
        else:
            entry["days_remaining"] = host.last_result.days_remaining
            ok.append(entry)

    return json.dumps({
        "generated_at": datetime.now(UTC).isoformat(),
        "critical": critical,
        "warning": warning,
        "ok": ok,
    })


@mcp.prompt()
def audit_certificates() -> list[Message]:
    """Prompt the AI to analyze the current certificate expiry report."""
    hosts = store.list_hosts()
    critical: list[dict] = []
    warning: list[dict] = []
    ok: list[dict] = []

    for host in hosts:
        entry: dict = {"domain": host.domain, "days_remaining": None, "error": None}
        if host.last_result is None:
            entry["error"] = "never checked"
            critical.append(entry)
        elif host.last_result.error is not None:
            entry["error"] = host.last_result.error
            critical.append(entry)
        elif host.last_result.days_remaining <= CRITICAL_DAYS:
            entry["days_remaining"] = host.last_result.days_remaining
            critical.append(entry)
        elif host.last_result.days_remaining <= WARNING_DAYS:
            entry["days_remaining"] = host.last_result.days_remaining
            warning.append(entry)
        else:
            entry["days_remaining"] = host.last_result.days_remaining
            ok.append(entry)

    report = {"critical": critical, "warning": warning, "ok": ok}
    content = (
        f"Analyze the following SSL/TLS certificate expiry report and identify certificates requiring attention.\n\n"
        f"Certificate Expiry Report:\n{json.dumps(report, indent=2)}\n\n"
        f"Please identify:\n"
        f"1. Critical certificates (expired or expiring within {CRITICAL_DAYS} days) needing immediate action\n"
        f"2. Warning certificates (expiring within {WARNING_DAYS} days) to prioritize\n"
        f"3. Certificates showing errors that need investigation\n"
        f"4. Recommended renewal order"
    )
    return [Message(role="user", content=content)]


@mcp.prompt()
def plan_renewal(domain: str) -> list[Message]:
    """Prompt the AI to draft a certificate renewal action plan for a domain."""
    try:
        host = store.get_host(domain)
    except ValueError:
        return [Message(
            role="user",
            content=f"The domain '{domain}' is not currently monitored. Add it first using the add_monitored_host tool.",
        )]

    content = (
        f"Create a certificate renewal action plan for the following domain.\n\n"
        f"Domain: {domain}\n"
        f"Certificate Details:\n{json.dumps(host.model_dump(mode='json'), indent=2)}\n\n"
        f"Please provide:\n"
        f"1. An urgency assessment based on the expiry date and days remaining\n"
        f"2. Step-by-step renewal process recommendations\n"
        f"3. Validation steps to confirm the renewal succeeded\n"
        f"4. Suggested monitoring frequency going forward"
    )
    return [Message(role="user", content=content)]


@mcp.tool()
def get_expiry_report() -> dict:
    """Return stored certificate data bucketed into critical, warning, and ok categories."""
    hosts = store.list_hosts()
    critical: list[dict] = []
    warning: list[dict] = []
    ok: list[dict] = []

    for host in hosts:
        entry: dict = {"domain": host.domain, "port": host.port, "days_remaining": None, "error": None}
        if host.last_result is None:
            entry["error"] = "never checked"
            critical.append(entry)
        elif host.last_result.error is not None:
            entry["error"] = host.last_result.error
            critical.append(entry)
        elif host.last_result.days_remaining <= CRITICAL_DAYS:
            entry["days_remaining"] = host.last_result.days_remaining
            critical.append(entry)
        elif host.last_result.days_remaining <= WARNING_DAYS:
            entry["days_remaining"] = host.last_result.days_remaining
            warning.append(entry)
        else:
            entry["days_remaining"] = host.last_result.days_remaining
            ok.append(entry)

    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "critical": critical,
        "warning": warning,
        "ok": ok,
    }
