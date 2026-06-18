from mcp_certificate_monitor import cert, store
from mcp_certificate_monitor.server import mcp


def main() -> None:
    mcp.run()


__all__ = ["cert", "main", "mcp", "store"]
