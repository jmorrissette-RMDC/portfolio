**Reviewer:** Gemini
**Gate:** 2
**MAD:** kaiser
**Date:** 2026-03-11

**Gate 2: FAILED**

**Blockers:**
1. **Missing `network: host` in `docker-compose.yml` build block for `kaiser-langgraph`:** The delta REQ (EX-KAISER-001) states that the build-time install from Alexandria (`irina:3141`) requires host networking to resolve the hostname. However, `docker-compose.yml` does not configure `network: "host"` in the `build` dictionary for `kaiser-langgraph`. Consequently, `RUN pip install` will fail with a DNS resolution error during `docker compose build`.
2. **`pip install` permission failures (Runtime and Build):** The `kaiser-langgraph` container runs as a non-root user (UID 2036). While the Dockerfile adds `~/.local/bin` to `PATH`, the `RUN pip install` command in the Dockerfile and the runtime `kaiser_install_package` command in `flows/management.py` both lack the `--user` flag. This will result in "Permission denied" errors when `pip` attempts to write to the system `site-packages` directory owned by root. You must add `--user` to both `pip install` invocations, or implement a virtualenv owned by the user.
3. **`kaiser-postgres` CMD override breaks entrypoint init:** `kaiser-postgres/Dockerfile` overrides `CMD` to `["sh", "-c", "crond && docker-entrypoint.sh postgres"]`. Because the base `postgres:16-alpine` uses `ENTRYPOINT ["docker-entrypoint.sh"]`, passing this string to `CMD` causes the entrypoint script to execute `exec sh -c ...` instead of recognizing `postgres` as the first argument. This skips the database initialization logic completely. Wrap the execution in a custom entrypoint script or restructure it so the postgres init script correctly receives `postgres` as `$1`.

**Observations:**
1. **Unpinned Base Image Digests:** `nginx:1.27.4-alpine` and `postgres:16-alpine` lack SHA256 digest pins. As explicitly documented in EX-KAISER-003, this is acceptable for Gate 2 and is tracked to be resolved during Gate 3 deployment.
2. **PostgreSQL data directory permissions:** As mandated by EX-KAISER-002, remember that the host path `/mnt/nvme/workspace/kaiser/databases/postgres/data` on `m5` must be manually created with `chmod 750` and ownership set to UID 2036 before deploying.
3. **Nginx PID path inconsistency:** `nginx.conf` sets `pid /tmp/nginx.pid;`, but the `Dockerfile` touches and chowns `/var/run/nginx.pid`. While it functions, the Dockerfile setup for `/var/run/nginx.pid` is redundant.

**Recommendations:**
1. **Virtualenv for Python Packages:** Instead of using `pip install --user`, the most robust approach for non-root Python applications is to create a virtual environment (`python -m venv /app/venv`) owned by `kaiser-langgraph` and append it to `PATH`. This avoids relying on the user site-packages fallback and keeps eMAD installations cleanly isolated.
2. **Robust Postgres Entrypoint:** For the postgres backup cron, consider providing a `wrapper.sh` script that starts `crond` in the background and ends with `exec docker-entrypoint.sh "$@"`. Setting this wrapper as the `ENTRYPOINT` is cleaner than fighting the default entrypoint's argument parsing via a convoluted `CMD` override.