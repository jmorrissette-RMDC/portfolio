**Reviewer:** Gemini
**Gate:** 2
**MAD:** kaiser
**Date:** 2026-03-11

- **Gate 2: FAILED**

### Blockers
1. **Programmatic Logic Outside StateGraph (`server.py`):** The `/health` endpoint handler in `server.py` imperatively executes database queries (`asyncpg`) and external HTTP requests (`httpx`). Per REQ-000 §4.7 (LangGraph Mandate), all programmatic logic in the langgraph container MUST be implemented as a `StateGraph`. This logic must be refactored into a compiled health-check StateGraph, similar to how `/metrics` was correctly implemented via `_metrics_flow`. Route handlers must only invoke graphs.

### Observations
1. **Unpinned Base Image Digests (EX-KAISER-003):** `kaiser/Dockerfile` uses `nginx:1.27.4-alpine` and `kaiser-postgres/Dockerfile` uses `postgres:16-alpine` without SHA256 digest pins. As noted in the REQ exception, these must be pinned before Gate 3 sign-off.
2. **Pip Install Subprocess:** The `kaiser_install_package` flow correctly uses `asyncio.create_subprocess_exec` for the `pip install` command, fulfilling the Asynchronous Correctness requirement (REQ-000 §7.9).
3. **Peer Proxy Adherence:** `kaiser-langgraph` correctly routes outbound peer calls (e.g., to Sutherland in `imperator.py`) through the `kaiser` nginx gateway on `kaiser-net`, maintaining strict network isolation (ADR-053).
4. **Valid Exception Handling:** The exception handling across the flows avoids blanket `except Exception:` statements and specifically targets anticipated exceptions like `asyncpg.PostgresError`, complying with REQ-000 §5.10.

### Recommendations
1. **Use Official Prometheus Client:** While `metrics.py` manually constructs valid Prometheus exposition text, it is highly recommended to use the official `prometheus_client` library (e.g., `prometheus_client.generate_latest(REGISTRY)`) to avoid formatting edge cases, handle text escaping properly, and simplify counter/histogram management.
2. **Graceful Error Handling for DB Pool:** In the health check logic (once moved to a StateGraph), consider catching `RuntimeError` alongside `asyncpg.PostgresError` in case the `get_pool()` initialization failed during startup, ensuring it degrades cleanly to `unhealthy` rather than causing an unhandled server error.