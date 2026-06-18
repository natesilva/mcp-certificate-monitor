import datetime

import pytest

from mcp_certificate_monitor.cert import PeerCert
from mcp_certificate_monitor.cert.peer_cert import PeerCertSuccess
from mcp_certificate_monitor.store import HostStore, MonitoredHost


@pytest.fixture
def sample_host_store() -> HostStore:
    host = MonitoredHost(
        domain="example.com",
        port=443,
        added_at=datetime.datetime.fromisoformat("2026-06-17T00:00:00Z"),
    )
    return HostStore(hosts={"example.com": host})


@pytest.fixture
def sample_peer_cert() -> PeerCert:
    cert = PeerCertSuccess.model_validate(
        {
            "type": "success",
            "subject": "example.com",
            "issuer": "CN=Example CA",
            "serial": "abcdef012345",
            "not_before": "Jan 01 00:00:00 2026 GMT",
            "not_after": "Dec 31 00:00:00 2026 GMT",
        }
    )
    return cert
