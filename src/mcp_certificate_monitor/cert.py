import socket
import ssl
from datetime import UTC, datetime
from typing import TypeGuard

from pydantic import BaseModel

_RDNSequence = tuple[tuple[tuple[str, str], ...], ...]
_SANList = tuple[tuple[str, str], ...]


class CertResult(BaseModel):
    subject: str
    issuer: str
    not_before: datetime
    not_after: datetime
    days_remaining: int
    serial: str
    san: list[str]
    error: str | None = None


_EPOCH = datetime.fromtimestamp(0, tz=UTC)


def _error_result(message: str) -> CertResult:
    return CertResult(
        subject="",
        issuer="",
        not_before=_EPOCH,
        not_after=_EPOCH,
        days_remaining=0,
        serial="",
        san=[],
        error=message,
    )


def _is_rdn_sequence(val: object) -> TypeGuard[_RDNSequence]:
    if not isinstance(val, tuple):
        return False
    if not val:
        return True
    first = val[0]
    return isinstance(first, tuple) and (not first or isinstance(first[0], tuple))


def _is_san_list(val: object) -> TypeGuard[_SANList]:
    if not isinstance(val, tuple):
        return False
    if not val:
        return True
    first = val[0]
    return isinstance(first, tuple) and (not first or isinstance(first[0], str))


def _normalize_dn(rdns: _RDNSequence) -> str:
    pairs = [f"{k}={v}" for rdn in rdns for k, v in rdn]
    return ", ".join(pairs)


def fetch_certificate(domain: str, port: int = 443) -> CertResult:
    try:
        ctx = ssl.create_default_context()
        with socket.create_connection((domain, port), timeout=10) as sock:
            with ctx.wrap_socket(sock, server_hostname=domain) as tls:
                raw = tls.getpeercert()

        if raw is None:
            return _error_result("no certificate returned")

        not_before_val = raw.get("notBefore")
        if not isinstance(not_before_val, str):
            return _error_result("certificate missing notBefore")

        not_after_val = raw.get("notAfter")
        if not isinstance(not_after_val, str):
            return _error_result("certificate missing notAfter")

        not_before = datetime.fromtimestamp(ssl.cert_time_to_seconds(not_before_val), tz=UTC)
        not_after = datetime.fromtimestamp(ssl.cert_time_to_seconds(not_after_val), tz=UTC)
        days_remaining = (not_after - datetime.now(UTC)).days

        subject_val = raw.get("subject")
        subject_rdns: _RDNSequence = subject_val if _is_rdn_sequence(subject_val) else ()
        issuer_val = raw.get("issuer")
        issuer_rdns: _RDNSequence = issuer_val if _is_rdn_sequence(issuer_val) else ()

        san_val = raw.get("subjectAltName")
        san_list: _SANList = san_val if _is_san_list(san_val) else ()
        san = [value for kind, value in san_list if kind == "DNS"]

        serial_val = raw.get("serialNumber")

        return CertResult(
            subject=_normalize_dn(subject_rdns),
            issuer=_normalize_dn(issuer_rdns),
            not_before=not_before,
            not_after=not_after,
            days_remaining=days_remaining,
            serial=serial_val if isinstance(serial_val, str) else "",
            san=san,
            error=None,
        )
    except Exception as exc:
        return _error_result(str(exc) or type(exc).__name__)
