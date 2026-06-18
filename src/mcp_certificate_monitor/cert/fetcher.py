import datetime
import socket
import ssl

from .peer_cert import PeerCert, PeerCertError, PeerCertSuccess


def fetch_certificate(host: str, port: int = 443) -> PeerCert:
    """Fetch the certificate for the given host."""
    try:
        ctx = ssl.create_default_context()
        ssl_socket = ctx.wrap_socket(
            socket.create_connection((host, port)), server_hostname=host
        )
        raw = ssl_socket.getpeercert()

        if raw is None:
            raise ValueError("No certificate found")

        cert = PeerCertSuccess.model_validate(raw)

        now = datetime.datetime.now(datetime.UTC)
        days_remaining = max((cert.not_after - now).days, 0)
        cert.days_remaining = days_remaining

        return cert
    except Exception as exc:
        return PeerCertError(error=str(exc))
