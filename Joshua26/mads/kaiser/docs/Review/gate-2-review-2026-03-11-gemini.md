**Reviewer:** gemini
**Gate:** 2
**MAD:** kaiser
**Date:** 2026-03-11

- **Gate 2: FAILED**

**Blockers:**
1. **Unpinned Base Image (REQ-000 §1.4)**: `mads/kaiser/kaiser/Dockerfile` uses `FROM nginx:1.27-alpine` without a digest (SHA256). The base image must be pinned explicitly.
2. **Build-time Offline-First Violation / Network Resolution**: `mads/kaiser/kaiser-langgraph/Dockerfile` sets `ENV PIP_INDEX_URL=http://kaiser:9226/pypi/...` and then executes `RUN pip install`. During `docker build` with `network: host`, the `kaiser` Docker DNS alias will not resolve natively via the host's `/etc/resolv.conf`. The build will fail because it cannot reach the Alexandria proxy. The build-time installation must use an explicit IP address (e.g., Irina's host IP: `http://192.168.1.110:3141/...`) or an ARG, while preserving the `ENV` for runtime use by `kaiser_install_package`.
3. **Blanket Exception Handling (REQ-000 §5.10)**: Widespread use of `except Exception as exc:` across `kaiser-langgraph/flows/` (found 16 instances in `registry.py`, `metrics.py`, `management.py`, `imperator.py`, and `dispatch.py`). The requirements explicitly forbid blanket exception blocks. Specific exceptions (e.g., `asyncpg.PostgresError`, `json.JSONDecodeError`) must be caught, and unhandled exceptions must be allowed to propagate.

**Observations:**
1. **Root cron in PostgreSQL container**: `mads/kaiser/kaiser-postgres/Dockerfile` runs `crond` as root at startup. While acceptable for backing services using official images, REQ-000 §2.1 prefers avoiding root for runtime tasks. If possible, configure `cron` to run as the `postgres` user.

**Recommendations:**
1. **Build vs. Runtime `PIP_INDEX_URL`**: Separate the build-time index URL from the runtime environment variable. Use `pip install --index-url=...` during the `RUN` step to point directly to Alexandria on the host network, and define `ENV PIP_INDEX_URL=http://kaiser:9226/...` *after* the `RUN` step so that runtime eMAD installations correctly use the nginx proxy.
2. **Defensive Umask in `start.sh`**: While `os.umask(0o000)` is correctly set at the top of `server.py`, consider also setting `umask 000` defensively inside `start.sh` before executing python.