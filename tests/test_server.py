import asyncio
from datetime import UTC, datetime

import pytest

from mcp_certificate_monitor import cert, store
from mcp_certificate_monitor.server import (
    CRITICAL_DAYS,
    WARNING_DAYS,
    add_monitored_host,
    check_certificate,
    get_expiry_report,
    remove_host,
    scan_all,
)

_EPOCH = datetime.fromtimestamp(0, tz=UTC)


def _fake_result(days_remaining: int = 90, error: str | None = None) -> cert.CertResult:
    return cert.CertResult(
        subject="example.com",
        issuer="Test CA",
        not_before=_EPOCH,
        not_after=datetime(2030, 1, 1, tzinfo=UTC),
        days_remaining=days_remaining,
        serial="ABC123",
        san=["example.com"],
        error=error,
    )


@pytest.fixture(autouse=True)
def isolated_store(tmp_path, monkeypatch):
    data_file = tmp_path / "cert-monitor" / "hosts.json"
    import mcp_certificate_monitor.store as store_module
    monkeypatch.setattr(store_module, "_data_path", lambda: data_file)
    return data_file


class TestCheckCertificate:
    def test_success_returns_dict_with_expected_keys(self, monkeypatch):
        monkeypatch.setattr(cert, "fetch_certificate", lambda d, p=443: _fake_result())
        result = check_certificate("example.com")
        assert isinstance(result, dict)
        assert "subject" in result
        assert "days_remaining" in result
        assert result["error"] is None

    def test_error_result_surfaces_error_in_dict(self, monkeypatch):
        monkeypatch.setattr(cert, "fetch_certificate", lambda d, p=443: _fake_result(error="connection refused"))
        result = check_certificate("unreachable.example.com")
        assert result["error"] == "connection refused"

    def test_does_not_mutate_store(self, monkeypatch):
        monkeypatch.setattr(cert, "fetch_certificate", lambda d, p=443: _fake_result())
        check_certificate("example.com")
        assert store.list_hosts() == []


class TestAddMonitoredHost:
    def test_adds_host_and_populates_last_result(self, monkeypatch):
        monkeypatch.setattr(cert, "fetch_certificate", lambda d, p=443: _fake_result(days_remaining=60))
        result = add_monitored_host("example.com")
        assert result["domain"] == "example.com"
        assert result["last_result"]["days_remaining"] == 60
        host = store.get_host("example.com")
        assert host.last_result is not None
        assert host.last_result.days_remaining == 60

    def test_duplicate_raises_value_error(self, monkeypatch):
        monkeypatch.setattr(cert, "fetch_certificate", lambda d, p=443: _fake_result())
        add_monitored_host("example.com")
        with pytest.raises(ValueError, match="already exists"):
            add_monitored_host("example.com")

    def test_failed_fetch_still_adds_host(self, monkeypatch):
        monkeypatch.setattr(cert, "fetch_certificate", lambda d, p=443: _fake_result(error="timeout"))
        add_monitored_host("example.com")
        host = store.get_host("example.com")
        assert host.last_result is not None
        assert host.last_result.error == "timeout"


class TestRemoveHost:
    def test_removes_existing_host(self, monkeypatch):
        monkeypatch.setattr(cert, "fetch_certificate", lambda d, p=443: _fake_result())
        add_monitored_host("example.com")
        msg = remove_host("example.com")
        assert isinstance(msg, str)
        assert len(msg) > 0
        assert store.list_hosts() == []

    def test_missing_host_raises_value_error(self):
        with pytest.raises(ValueError, match="not found"):
            remove_host("missing.example.com")


class TestScanAll:
    def test_scan_returns_summary_for_all_hosts(self, monkeypatch):
        store.add_host("a.example.com")
        store.add_host("b.example.com")
        monkeypatch.setattr(cert, "fetch_certificate", lambda d, p=443: _fake_result(days_remaining=50))
        results = asyncio.run(scan_all())
        assert len(results) == 2
        domains = {r["domain"] for r in results}
        assert domains == {"a.example.com", "b.example.com"}
        for r in results:
            assert r["days_remaining"] == 50
            assert r["error"] is None

    def test_scan_updates_stored_results(self, monkeypatch):
        store.add_host("example.com")
        monkeypatch.setattr(cert, "fetch_certificate", lambda d, p=443: _fake_result(days_remaining=30))
        asyncio.run(scan_all())
        host = store.get_host("example.com")
        assert host.last_result is not None
        assert host.last_checked is not None
        assert host.last_result.days_remaining == 30

    def test_empty_store_returns_empty_list(self):
        results = asyncio.run(scan_all())
        assert results == []

    def test_unreachable_host_does_not_abort_scan(self, monkeypatch):
        store.add_host("ok.example.com")
        store.add_host("bad.example.com")

        def _fake_fetch(domain: str, port: int = 443) -> cert.CertResult:
            if domain == "bad.example.com":
                return _fake_result(error="connection refused")
            return _fake_result(days_remaining=90)

        monkeypatch.setattr(cert, "fetch_certificate", _fake_fetch)
        results = asyncio.run(scan_all())
        assert len(results) == 2
        by_domain = {r["domain"]: r for r in results}
        assert by_domain["bad.example.com"]["error"] == "connection refused"
        assert by_domain["ok.example.com"]["error"] is None


class TestGetExpiryReport:
    def _add_with_result(self, domain: str, days_remaining: int | None = None, error: str | None = None) -> None:
        store.add_host(domain)
        if days_remaining is not None or error is not None:
            result = _fake_result(days_remaining=days_remaining or 0, error=error)
            store.update_host_result(domain, result)

    def test_buckets_hosts_by_days_remaining(self):
        self._add_with_result("critical.example.com", days_remaining=CRITICAL_DAYS)
        self._add_with_result("warning.example.com", days_remaining=WARNING_DAYS)
        self._add_with_result("ok.example.com", days_remaining=WARNING_DAYS + 1)
        report = get_expiry_report()
        critical_domains = {h["domain"] for h in report["critical"]}
        warning_domains = {h["domain"] for h in report["warning"]}
        ok_domains = {h["domain"] for h in report["ok"]}
        assert "critical.example.com" in critical_domains
        assert "warning.example.com" in warning_domains
        assert "ok.example.com" in ok_domains

    def test_errored_host_lands_in_critical(self):
        self._add_with_result("bad.example.com", error="tls failure")
        report = get_expiry_report()
        critical_domains = {h["domain"] for h in report["critical"]}
        assert "bad.example.com" in critical_domains
        entry = next(h for h in report["critical"] if h["domain"] == "bad.example.com")
        assert entry["error"] == "tls failure"

    def test_never_checked_host_lands_in_critical(self):
        store.add_host("new.example.com")
        report = get_expiry_report()
        critical_domains = {h["domain"] for h in report["critical"]}
        assert "new.example.com" in critical_domains
        entry = next(h for h in report["critical"] if h["domain"] == "new.example.com")
        assert entry["error"] == "never checked"
        assert entry["days_remaining"] is None

    def test_report_has_generated_at(self):
        before = datetime.now(UTC)
        report = get_expiry_report()
        after = datetime.now(UTC)
        generated_at = datetime.fromisoformat(report["generated_at"])
        assert before <= generated_at <= after

    def test_empty_store_returns_empty_buckets(self):
        report = get_expiry_report()
        assert report["critical"] == []
        assert report["warning"] == []
        assert report["ok"] == []
