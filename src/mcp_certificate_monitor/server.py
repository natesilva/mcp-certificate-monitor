import asyncio
from datetime import UTC, datetime

from fastmcp import FastMCP

from mcp_certificate_monitor import cert, store

mcp = FastMCP("Certificate Monitor")

CRITICAL_DAYS: int = 14
WARNING_DAYS: int = 30


@mcp.tool()
def check_certificate(domain: str, port: int = 443) -> dict:
    """Fetch a live SSL/TLS certificate for a domain without updating stored state."""
    result = cert.fetch_certificate(domain, port)
    return result.model_dump(mode="json")


@mcp.tool()
def add_monitored_host(domain: str, port: int = 443) -> dict:
    """Add a domain to the monitored host list and immediately check its certificate."""
    store.add_host(domain, port)
    result = cert.fetch_certificate(domain, port)
    store.update_host_result(domain, result)
    host = store.get_host(domain)
    return {"domain": host.domain, "port": host.port, "last_result": result.model_dump(mode="json")}


@mcp.tool()
def remove_host(domain: str) -> str:
    """Remove a domain from the monitored host list."""
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
