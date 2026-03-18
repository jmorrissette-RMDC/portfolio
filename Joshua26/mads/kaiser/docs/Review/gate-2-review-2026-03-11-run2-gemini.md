**Reviewer:** gemini
**Gate:** 2
**MAD:** kaiser
**Date:** 2026-03-11

**Gate 2: FAILED**

**Blockers:**
1.  **REQ-000 §1.4 / REQ-000 §1.7 Version Pinning (Digest Pinning)**: `mads/kaiser/kaiser/Dockerfile` uses `nginx:1.27.4-alpine`. As noted in the implementation plan ("nginx digest pinning deferred"), this must be pinned to a specific SHA256 digest (e.g., `nginx:1.27.4-alpine@sha256:...`) to guarantee deterministic offline builds and prevent unexpected upstream changes, matching the standard correctly applied in `kaiser-langgraph/Dockerfile`.
2.  **Unused/Conflicting Dependency**: `mads/kaiser/kaiser-langgraph/requirements.txt` includes `quart==0.19.9`. However, `mads/kaiser/kaiser-langgraph/server.py` is implemented using `Starlette` (which is correctly installed via `starlette==0.41.3` and utilized by `FastMCP`). The unused `quart` dependency must be removed from `requirements.txt` to maintain a minimal, secure attack surface and avoid confusion.

**Observations:**
1.  **REQ-kaiser §6.1 Discrepancy**: `mads/kaiser/docs/REQ-kaiser.md` section 6.1 explicitly states "kaiser-langgraph uses Quart (async ASGI) as its web framework". The implementation uses `Starlette`. Given that `FastMCP.http_app()` natively returns a Starlette app, the implementation is correct, cleaner, and avoids unnecessary abstraction. `REQ-kaiser.md` should be updated to reflect the use of Starlette instead of Quart.
2.  **Network Isolation for Runtime Installs (EX-KAISER-001)**: The implementation of the `nginx` PyPI proxy at `http://kaiser:9226/pypi/` paired with `kaiser-langgraph` setting `PIP_INDEX_URL` and `PIP_TRUSTED_HOST` as runtime `ENV` variables in its Dockerfile is an excellent, secure architectural solution. It perfectly fulfills the requirement of keeping `kaiser-langgraph` isolated on `kaiser-net` while dynamically providing Alexandria access.
3.  **ADR-052 Bind Mount Pattern**: The explicit bind mount for the `kaiser-postgres` data volume defined in `docker-compose.m5.yml` (`/mnt/nvme/workspace/kaiser/databases/postgres/data:/var/lib/postgresql/data`) correctly suppresses the anonymous volume declared by the official `postgres:16-alpine` image, fully adhering to ADR-052.

**Recommendations:**
1.  **Code Quality (Exception Handling)**: In `mads/kaiser/kaiser-langgraph/server.py`, the `health()` endpoint correctly catches specific, anticipated exceptions (`asyncpg.PostgresError`, `asyncpg.InterfaceError`, `OSError`, `httpx.RequestError`, `httpx.HTTPStatusError`). This is exactly what REQ-000 §5.10 dictates. The codebase exhibits strong adherence to the standard.
2.  **File Permissions Verification**: Prior to initial deployment on the M5 host, verify that the host directory `/mnt/nvme/workspace/kaiser/databases/postgres/data` is explicitly secured with `chmod 750` or `chmod 700` ownership per REQ-000 §2.6, as the application runs with `umask 000`.
