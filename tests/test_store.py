from datetime import UTC, datetime
from pathlib import Path

import pytest

from mcp_certificate_monitor.cert import CertResult
from mcp_certificate_monitor.store import (
    HostStore,
    MonitoredHost,
    add_host,
    get_host,
    list_hosts,
    load,
    remove_host,
    save,
    update_host_result,
)

_EPOCH = datetime.fromtimestamp(0, tz=UTC)


def _fake_result(error: str | None = None) -> CertResult:
    return CertResult(
        subject="example.com",
        issuer="Test CA",
        not_before=_EPOCH,
        not_after=datetime(2030, 1, 1, tzinfo=UTC),
        days_remaining=1000,
        serial="ABC",
        san=["example.com"],
        error=error,
    )


@pytest.fixture(autouse=True)
def isolated_store(tmp_path, monkeypatch):
    """Redirect store to a temp directory for every test."""
    data_file = tmp_path / "cert-monitor" / "hosts.json"

    import mcp_certificate_monitor.store as store_module
    monkeypatch.setattr(store_module, "_data_path", lambda: data_file)
    return data_file


class TestLoad:
    def test_missing_file_returns_empty_store(self):
        store = load()
        assert isinstance(store, HostStore)
        assert store.hosts == {}

    def test_corrupt_json_returns_empty_store(self, isolated_store):
        isolated_store.parent.mkdir(parents=True, exist_ok=True)
        isolated_store.write_text("not valid json {{{{")
        store = load()
        assert store.hosts == {}

    def test_schema_mismatch_returns_empty_store(self, isolated_store):
        isolated_store.parent.mkdir(parents=True, exist_ok=True)
        isolated_store.write_text('{"hosts": {"x": {"bad_field": 1}}}')
        store = load()
        assert store.hosts == {}


class TestSave:
    def test_round_trip_preserves_all_fields(self, isolated_store):
        result = _fake_result()
        host = MonitoredHost(
            domain="example.com",
            port=443,
            added_at=datetime(2026, 1, 1, tzinfo=UTC),
            last_checked=datetime(2026, 6, 1, tzinfo=UTC),
            last_result=result,
        )
        store = HostStore(hosts={"example.com": host})
        save(store)

        reloaded = load()
        assert "example.com" in reloaded.hosts
        h = reloaded.hosts["example.com"]
        assert h.domain == "example.com"
        assert h.port == 443
        assert h.last_result is not None
        assert h.last_result.serial == "ABC"
        assert h.last_result.not_after.tzinfo is not None

    def test_save_creates_parent_directory(self, tmp_path, monkeypatch):
        deep = tmp_path / "a" / "b" / "c" / "hosts.json"
        import mcp_certificate_monitor.store as store_module
        monkeypatch.setattr(store_module, "_data_path", lambda: deep)
        save(HostStore())
        assert deep.exists()


class TestCRUD:
    def test_add_host_appears_in_list(self):
        add_host("example.com", 443)
        hosts = list_hosts()
        assert len(hosts) == 1
        assert hosts[0].domain == "example.com"
        assert hosts[0].port == 443
        assert hosts[0].last_result is None

    def test_add_host_sets_added_at(self):
        before = datetime.now(UTC)
        host = add_host("example.com")
        after = datetime.now(UTC)
        assert before <= host.added_at <= after

    def test_add_duplicate_raises(self):
        add_host("example.com")
        with pytest.raises(ValueError, match="already exists"):
            add_host("example.com")

    def test_get_existing_host(self):
        add_host("example.com", 8443)
        host = get_host("example.com")
        assert host.port == 8443

    def test_get_missing_host_raises(self):
        with pytest.raises(ValueError, match="not found"):
            get_host("missing.example.com")

    def test_list_hosts_empty(self):
        assert list_hosts() == []

    def test_list_hosts_multiple(self):
        add_host("a.example.com")
        add_host("b.example.com")
        domains = {h.domain for h in list_hosts()}
        assert domains == {"a.example.com", "b.example.com"}

    def test_remove_host(self):
        add_host("example.com")
        remove_host("example.com")
        assert list_hosts() == []

    def test_remove_missing_host_raises(self):
        with pytest.raises(ValueError, match="not found"):
            remove_host("missing.example.com")

    def test_update_host_result(self):
        add_host("example.com")
        result = _fake_result()

        before = datetime.now(UTC)
        update_host_result("example.com", result)
        after = datetime.now(UTC)

        host = get_host("example.com")
        assert host.last_result is not None
        assert host.last_result.serial == "ABC"
        assert host.last_checked is not None
        assert before <= host.last_checked <= after

    def test_update_missing_host_raises(self):
        with pytest.raises(ValueError, match="not found"):
            update_host_result("missing.example.com", _fake_result())

    def test_update_persists_to_disk(self):
        add_host("example.com")
        update_host_result("example.com", _fake_result())
        reloaded = get_host("example.com")
        assert reloaded.last_result is not None
        assert reloaded.last_result.serial == "ABC"
