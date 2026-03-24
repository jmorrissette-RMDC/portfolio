**Reviewer:** gemini
**Gate:** 2
**MAD:** alexandria
**Date:** 2026-03-08

## Gate 2: FAILED

The implementation of the Alexandria MAD has a critical architectural flaw regarding the MCP protocol interface. The LangGraph logic engine fails to expose an actual MCP-compliant endpoint, relying instead on bespoke HTTP routes. Additionally, there is a violation of the container independence mandate in `docker-compose.yml`.

### Blockers

1.  **Missing MCP Protocol Implementation (`server.py`):** The `alexandria-langgraph` container (`server.py`) defines Quart HTTP endpoints for each tool (e.g., `/alex_cache_status`, `/alex_warm_pypi`) instead of implementing the MCP protocol (JSON-RPC 2.0) on the `/mcp` route. The `alexandria` (nginx) gateway is configured to proxy `/mcp` to `http://alexandria-langgraph:8000/mcp`, but this route does not exist. All tools must be served through a standard MCP endpoint per REQ-000 §4.4.
2.  **Violation of Container Independence (`docker-compose.yml`):** The `alexandria` gateway service in `docker-compose.yml` uses `depends_on` for `alexandria-langgraph`, `alexandria-devpi`, `alexandria-verdaccio`, and `alexandria-registry`. Per REQ-000 §7.3 and the explicit instruction at the top of the compose file, containers must start independently and handle unavailable dependencies via graceful degradation. The `depends_on` block must be removed.

### Observations

1.  **umask Compliance:** `umask 000` is correctly implemented at the top of the relevant entry points (`alexandria-devpi/entrypoint.sh`, `alexandria-langgraph/server.py`, `alexandria-langgraph/start.sh`, `alexandria/start.sh`) per REQ-000 §2.4.
2.  **Identity Constraints:** The custom containers correctly use UID 2017 and GID 2001 (`administrators`), aligning with the findings from the Gate 1 review.
3.  **Health Aggregation:** The `/health` endpoint in `alexandria-langgraph/server.py` correctly aggregates the statuses of `devpi`, `verdaccio`, and `registry`, and handles unreachability gracefully (REQ-000 §5.9).
4.  **Host-Bound Exceptions:** The caching ports (3141, 4873, 5000) are correctly bound to the host in `docker-compose.yml`, consistent with EX-ALEXANDRIA-001.

### Recommendations

1.  **Adopt an MCP Server Library:** Instead of writing raw Quart routes for each tool, integrate an MCP server library (like `fastmcp` or the internal equivalent used by other Python MADs) in `server.py` to handle the JSON-RPC boilerplate, SSE streaming, and tool registration automatically on the `/mcp` route.
2.  **Gateway Resilience:** Once `depends_on` is removed, the Nginx gateway will naturally provide graceful degradation by returning `502 Bad Gateway` if `alexandria-langgraph` or any of the cache containers are temporarily down, which perfectly satisfies the offline-tolerant design mandate.
