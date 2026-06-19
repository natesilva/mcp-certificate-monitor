## 1. Silence startup stderr

- [x] 1.1 In `src/mcp_certificate_monitor/__init__.py`, import `logging` and add `logging.getLogger("fastmcp").setLevel(logging.WARNING)` before calling `mcp.run()`
- [x] 1.2 Change `mcp.run()` to `mcp.run(show_banner=False)` in `main()`

## 2. Verify

- [x] 2.1 Run the server manually and confirm nothing appears on stderr at startup
- [x] 2.2 Confirm WARNING/ERROR messages still surface (e.g., a deliberate bad config)
