import datetime
import os
import tempfile
from pathlib import Path

from mcp.server.fastmcp.server import logger
from platformdirs import user_data_dir
from pydantic import BaseModel, ValidationError

from mcp_certificate_monitor.cert.peer_cert import PeerCert

STORE_DIR = Path(user_data_dir("cert-monitor"))
STORE_PATH = STORE_DIR / "hosts.json"


class MonitoredHost(BaseModel):
    domain: str
    port: int
    added_at: datetime.datetime
    last_checked: datetime.datetime | None = None
    last_result: PeerCert | None = None


class HostStore(BaseModel):
    hosts: dict[str, MonitoredHost] = {}


def load() -> dict[str, MonitoredHost]:
    if not STORE_PATH.exists():
        return {}

    try:
        return HostStore.model_validate_json(STORE_PATH.read_text("utf-8")).hosts
    except (ValidationError, ValueError):
        logger.warning("Corrupt hosts.json, starting empty")
        return {}


def save(hosts: dict[str, MonitoredHost]) -> None:
    STORE_DIR.mkdir(parents=True, exist_ok=True)
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            dir=STORE_DIR,
            encoding="utf-8",
            suffix=".tmp",
            prefix=".output-json-",
            delete=False,
        ) as tmp:
            tmp_path = tmp.name
            data = HostStore(hosts=hosts).model_dump_json(indent=2)
            tmp.write(data)
            tmp.flush()
            os.fsync(tmp.fileno())

        os.replace(tmp_path, STORE_PATH)
    except Exception:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)
        raise


def add_host(domain: str, port: int = 443) -> MonitoredHost:
    hosts = load()
    if domain in hosts:
        raise KeyError(f"Domain {domain} is already monitored")

    new_host = MonitoredHost(
        domain=domain,
        port=port,
        added_at=datetime.datetime.now(datetime.UTC),
        last_checked=None,
        last_result=None,
    )

    hosts[domain] = new_host
    save(hosts)

    return new_host


def remove_host(domain: str) -> None:
    hosts = load()
    if domain not in hosts:
        raise KeyError(f"Domain {domain} is not monitored")
    del hosts[domain]
    save(hosts)


def update_result(domain: str, result: PeerCert) -> None:
    hosts = load()
    if domain not in hosts:
        raise KeyError(f"Domain {domain} is not monitored")

    hosts[domain].last_checked = datetime.datetime.now(datetime.UTC)
    hosts[domain].last_result = result
    save(hosts)
