import logging
import os
import tempfile
from datetime import UTC, datetime
from pathlib import Path

import platformdirs
from pydantic import BaseModel, ValidationError

from mcp_certificate_monitor.cert import CertResult

logger = logging.getLogger(__name__)


class MonitoredHost(BaseModel):
    domain: str
    port: int
    added_at: datetime
    last_checked: datetime | None = None
    last_result: CertResult | None = None


class HostStore(BaseModel):
    hosts: dict[str, MonitoredHost] = {}


def _data_path() -> Path:
    return Path(platformdirs.user_data_dir("cert-monitor")) / "hosts.json"


def load() -> HostStore:
    path = _data_path()
    try:
        return HostStore.model_validate_json(path.read_text())
    except FileNotFoundError:
        return HostStore()
    except (ValidationError, Exception) as exc:
        logger.warning("Could not load %s: %s — starting with empty store", path, exc)
        return HostStore()


def save(store: HostStore) -> None:
    path = _data_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    try:
        with os.fdopen(fd, "w") as f:
            f.write(store.model_dump_json(indent=2))
        os.replace(tmp, path)
    except Exception:
        os.unlink(tmp)
        raise


def add_host(domain: str, port: int = 443) -> MonitoredHost:
    store = load()
    if domain in store.hosts:
        raise ValueError(f"Host already exists: {domain}")
    host = MonitoredHost(domain=domain, port=port, added_at=datetime.now(UTC))
    store.hosts[domain] = host
    save(store)
    return host


def remove_host(domain: str) -> None:
    store = load()
    if domain not in store.hosts:
        raise ValueError(f"Host not found: {domain}")
    del store.hosts[domain]
    save(store)


def get_host(domain: str) -> MonitoredHost:
    store = load()
    if domain not in store.hosts:
        raise ValueError(f"Host not found: {domain}")
    return store.hosts[domain]


def list_hosts() -> list[MonitoredHost]:
    return list(load().hosts.values())


def update_host_result(domain: str, result: CertResult) -> None:
    store = load()
    if domain not in store.hosts:
        raise ValueError(f"Host not found: {domain}")
    store.hosts[domain].last_checked = datetime.now(UTC)
    store.hosts[domain].last_result = result
    save(store)
