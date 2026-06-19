import logging

from mcp_certificate_monitor import cert, store
from mcp_certificate_monitor.server import mcp


def main() -> None:
    logging.getLogger("fastmcp").setLevel(logging.WARNING)
    mcp.run(show_banner=False)


__all__ = ["cert", "main", "mcp", "store"]
