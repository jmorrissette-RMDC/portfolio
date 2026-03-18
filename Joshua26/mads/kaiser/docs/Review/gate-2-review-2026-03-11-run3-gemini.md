**Reviewer:** gemini
**Gate:** 2
**MAD:** kaiser
**Date:** 2026-03-11

- **Gate 2: FAILED**

**Blockers:**
1. **Missing Docker base image digest pinning (REQ-000 §1.4, §1.7):**
   - `mads/kaiser/kaiser/Dockerfile` uses `FROM nginx:1.27.4-alpine` without a sha256 digest.
   - `mads/kaiser/kaiser-postgres/Dockerfile` uses `FROM postgres:16-alpine` without a sha256 digest.
2. **Missing formal exception for Gateway pattern (REQ-000 §4.5, §4.6, §4.8 vs. REQ-kaiser §6.2):**
   - The Kaiser implementation uses an NGINX container directly for its gateway instead of the `mads/_template` node.js implementation. While this "State 2 pattern" is documented in REQ-kaiser §6.2, it directly violates REQ-000 §4.5, §4.6, and §4.8 (Thin Gateway Mandate). This architectural deviation requires a formally approved exception registered in `REQ-000-exception-registry` and documented in REQ-kaiser §11 (Exceptions).
3. **Missing formal exception for volume bind mounts (REQ-000 §3.1, §3.2 vs. ADR-052):**
   - `docker-compose.m5.yml` uses a direct host bind mount (`/mnt/nvme/workspace/kaiser/databases/postgres/data:/var/lib/postgresql/data`) instead of the standard `workspace:/workspace` mount. Per REQ-000 §3.1, using bind mounts to override declared VOLUME paths in official images like `postgres` requires a formal approved exception registered in `REQ-000-exception-registry` before deployment. This must be formally documented as an exception.
4. **Offline build violation for package caching (REQ-000 §1.1):**
   - `mads/kaiser/kaiser-langgraph/Dockerfile` installs Python dependencies at build time directly from the Alexandria proxy over the host network (`--index-url http://irina:3141/root/pypi/+simple/`) instead of from a local `packages/` directory using `--find-links=/tmp/packages/`. While runtime `pip install` has a registered exception (EX-KAISER-001), the build-time installation must still follow the offline caching rules, or the exception must be broadened to explicitly cover build-time dependency fetching.
5. **System package caching fallback network hit (REQ-000 §1.3):**
   - `mads/kaiser/kaiser-postgres/Dockerfile` uses `apk add --no-cache dcron` as a fallback. While it attempts to use a local cache (`/tmp/apk-cache/*.apk`), if the `.apk` files are missing from the commit, it will silently fetch from the internet, breaking the offline build guarantee. The build should fail if the packages are missing locally.

**Observations:**
1. **LangGraph implementation compliance:** `mads/kaiser/kaiser-langgraph/server.py` properly wires FastMCP tools into LangGraph flows, satisfying the REQ-000 §4.7 LangGraph mandate.
2. **Metrics implementation compliance:** Metrics are properly generated via a StateGraph (`_metrics_flow.ainvoke`), compliant with REQ-000 §4.11.
3. **Structured logging compliance:** `server.py` implements a `_JsonFormatter` for structured logging, in compliance with REQ-000 §5.2.
4. **Health check implementation:** The custom `/health` endpoint effectively tests dependencies (`postgres`, `rogers`, `sutherland`) according to the two-layer health check system (REQ-000 §5.9).

**Recommendations:**
1. Replace the fallback `|| apk add --no-cache dcron` in the postgres Dockerfile with an offline-only installation that explicitly fails if the `.apk` is missing, to strictly enforce REQ-000 §1.3.
2. Ensure you have the `dcron` package downloaded into `mads/kaiser/kaiser-postgres/packages/apk/` before modifying the Dockerfile to fail on missing `.apk` files.
3. If the build-time fetching exception from Alexandria is approved, broaden EX-KAISER-001 in `REQ-kaiser.md` section 11 to reflect it. Also, update section 11 to include exceptions for the NGINX gateway and the postgres bind mount.
4. Ensure `pip install` strictly enforces pinned versions during build by providing all dependencies in `packages/` if the exception for build-time network fetching is not approved.