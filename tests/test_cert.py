import socket
import ssl
from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

import pytest

from mcp_certificate_monitor.cert import CertResult, _error_result, _normalize_dn, fetch_certificate

_FAKE_CERT = {
    "subject": ((("commonName", "example.com"),),),
    "issuer": ((("commonName", "Test CA"),),),
    "notBefore": "Jan  1 00:00:00 2025 GMT",
    "notAfter": "Jan  1 00:00:00 2030 GMT",
    "serialNumber": "DEADBEEF",
    "subjectAltName": (("DNS", "example.com"), ("DNS", "www.example.com")),
}


class TestNormalizeDN:
    def test_multi_component_dn(self):
        rdns = (
            (("countryName", "US"),),
            (("organizationName", "Let's Encrypt"),),
            (("commonName", "R11"),),
        )
        assert _normalize_dn(rdns) == "countryName=US, organizationName=Let's Encrypt, commonName=R11"

    def test_single_component_dn(self):
        rdns = ((("commonName", "example.com"),),)
        assert _normalize_dn(rdns) == "commonName=example.com"

    def test_empty_input(self):
        assert _normalize_dn(()) == ""


class TestCertResult:
    def test_construction(self):
        now = datetime.now(UTC)
        result = CertResult(
            subject="example.com",
            issuer="Test CA",
            not_before=now,
            not_after=now,
            days_remaining=100,
            serial="ABC",
            san=["example.com"],
        )
        assert result.error is None
        assert result.san == ["example.com"]

    def test_serializes_to_json(self):
        now = datetime.now(UTC)
        result = CertResult(
            subject="s", issuer="i", not_before=now, not_after=now,
            days_remaining=5, serial="S", san=[],
        )
        data = result.model_dump_json()
        assert '"subject"' in data
        assert '"error"' in data

    def test_error_result_factory(self):
        result = _error_result("connection refused")
        assert result.error == "connection refused"
        assert result.subject == ""
        assert result.san == []

    def test_error_result_validates(self):
        result = _error_result("boom")
        assert isinstance(result, CertResult)


class TestFetchCertificate:
    def _make_mock_tls(self, cert=None):
        mock_tls = MagicMock()
        mock_tls.getpeercert.return_value = cert or _FAKE_CERT
        mock_tls.__enter__ = MagicMock(return_value=mock_tls)
        mock_tls.__exit__ = MagicMock(return_value=False)
        return mock_tls

    def _make_mock_sock(self, mock_tls):
        mock_sock = MagicMock()
        mock_sock.__enter__ = MagicMock(return_value=mock_sock)
        mock_sock.__exit__ = MagicMock(return_value=False)
        return mock_sock

    def test_successful_fetch(self):
        mock_tls = self._make_mock_tls()
        mock_sock = self._make_mock_sock(mock_tls)

        with patch("socket.create_connection", return_value=mock_sock):
            with patch.object(
                ssl.SSLContext, "wrap_socket", return_value=mock_tls
            ):
                result = fetch_certificate("example.com")

        assert result.error is None
        assert result.subject == "commonName=example.com"
        assert result.issuer == "commonName=Test CA"
        assert result.serial == "DEADBEEF"
        assert "example.com" in result.san
        assert "www.example.com" in result.san
        assert result.not_before.tzinfo is not None
        assert result.not_after.tzinfo is not None

    def test_days_remaining_computed(self):
        mock_tls = self._make_mock_tls()
        mock_sock = self._make_mock_sock(mock_tls)

        with patch("socket.create_connection", return_value=mock_sock):
            with patch.object(ssl.SSLContext, "wrap_socket", return_value=mock_tls):
                result = fetch_certificate("example.com")

        expected = (result.not_after - datetime.now(UTC)).days
        assert abs(result.days_remaining - expected) <= 1

    def test_missing_san_returns_empty_list(self):
        cert = dict(_FAKE_CERT)
        del cert["subjectAltName"]
        mock_tls = self._make_mock_tls(cert)
        mock_sock = self._make_mock_sock(mock_tls)

        with patch("socket.create_connection", return_value=mock_sock):
            with patch.object(ssl.SSLContext, "wrap_socket", return_value=mock_tls):
                result = fetch_certificate("example.com")

        assert result.san == []
        assert result.error is None

    def test_socket_timeout_returns_error(self):
        with patch("socket.create_connection", side_effect=socket.timeout("timed out")):
            result = fetch_certificate("unreachable.example.com")

        assert result.error is not None
        assert "timed out" in result.error

    def test_ssl_error_returns_error(self):
        with patch(
            "socket.create_connection",
            side_effect=ssl.SSLError("certificate verify failed"),
        ):
            result = fetch_certificate("bad-cert.example.com")

        assert result.error is not None
        assert result.subject == ""

    def test_os_error_returns_error(self):
        with patch("socket.create_connection", side_effect=OSError("connection refused")):
            result = fetch_certificate("closed.example.com")

        assert result.error is not None

    def test_never_raises(self):
        with patch("socket.create_connection", side_effect=RuntimeError("unexpected")):
            result = fetch_certificate("example.com")

        assert result.error is not None
