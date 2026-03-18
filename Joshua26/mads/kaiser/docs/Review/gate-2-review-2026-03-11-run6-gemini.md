**Reviewer:** Gemini
**Gate:** 2
**MAD:** kaiser
**Date:** 2026-03-11

- **Gate 2: FAILED**

**Blockers:**
1. **Starlette Lifespan Misconfiguration (`mads/kaiser/kaiser-langgraph/server.py`):**
   The Starlette app is instantiated with `lifespan=_mcp_app.lifespan`, and then immediately afterward, `_mcp_app.lifespan` is reassigned to the custom `_lifespan` function. Because Python passes the function reference at instantiation time, the custom `_lifespan` handler (which correctly calls `init_pool()` and `registry.scan()`) is never executed by Starlette. Consequently, `get_pool()` will always raise a `RuntimeError` on the first tool invocation. Fix this by passing `lifespan=_lifespan` directly to the `Starlette()` constructor.
2. **PyPI Proxy DNS Resolution Failure (`mads/kaiser/kaiser/nginx.conf`):**
   The PyPI proxy block sets `$devpi "irina:3141";` while relying on Docker's embedded DNS (`resolver 127.0.0.11`). Since `irina` is the physical host machine and not a container on the `kaiser-net` or `joshua-net` Docker networks, the resolver will fail with a host not found error. This breaks the runtime `kaiser_install_package` flow. Use the explicit host IP `192.168.1.110:3141` or ensure `irina` is injected into the container via `extra_hosts` in the compose file.
3. **Missing `asyncpg` JSONB Codec Configuration (`mads/kaiser/kaiser-langgraph/flows/db.py`):**
   The `asyncpg` connection pool is created without registering type codecs. In `flows/management.py` and `flows/imperator.py`, Python `dict` objects are passed directly into SQL queries as parameters for the `JSONB` column `parameters`. Without a registered JSON codec, `asyncpg` will raise an `asyncpg.exceptions.DataError`. Furthermore, querying the column will return a JSON string instead of a `dict`, causing the `dict(row["parameters"])` casts in `dispatch.py` and `management.py` to crash with a `ValueError`. Implement an `init` function on the `asyncpg` pool to register `jsonb` encoders and decoders (`await conn.set_type_codec(...)`).

**Observations:**
1. **Nginx PID Redundancy (`mads/kaiser/kaiser/Dockerfile` & `nginx.conf`):**
   The Dockerfile creates and explicitly chowns `/var/run/nginx.pid` for non-root execution, but `nginx.conf` ignores this and correctly defines `pid /tmp/nginx.pid;`. The Dockerfile step is redundant and could cause confusion.
2. **Postgres Volume Permissions (`EX-KAISER-002`):**
   As a reminder for Gate 3 deployment, ensure the host directory `/mnt/nvme/workspace/kaiser/databases/postgres/data` is manually created with `chmod 750` and owned by UID 2036 on M5 prior to starting the containers, otherwise Postgres will fail to initialise or save data correctly.
3. **Build-time Hostname Resolution (`mads/kaiser/kaiser-langgraph/Dockerfile`):**
   The Dockerfile uses `--index-url http://irina:3141/root/pypi/+simple/` which relies on `irina` being resolvable during the `network: host` build step on M5. Ensure M5's `/etc/hosts` or network DNS correctly maps `irina` to `192.168.1.110` during the compose build phase.

**Recommendations:**
1. **Digest Pinning:** As defined in `EX-KAISER-003`, the unpinned digests for `nginx:1.27.4-alpine` and `postgres:16-alpine` must be resolved and pinned in their respective Dockerfiles prior to or during Gate 3 deployment.
2. **Defensive Dict Casting (`mads/kaiser/kaiser-langgraph/flows/dispatch.py`):**
   When `row["parameters"]` is retrieved and the `asyncpg` JSONB codec is correctly configured, it will inherently return a `dict`. The extra `dict(...)` wrapper is unnecessary and can be removed, reducing clutter and mitigating edge cases.
