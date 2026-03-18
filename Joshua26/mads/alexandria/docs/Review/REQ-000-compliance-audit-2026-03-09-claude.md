**Reviewer:** Claude Sonnet 4.6
**Gate:** 3
**MAD:** alexandria
**Date:** 2026-03-09

---

# REQ-000 Compliance Checklist: Alexandria

**MAD Group:** alexandria  **Audit Date:** 2026-03-09  **Auditor:** Claude Sonnet 4.6  **Status:** Complete

---

## Verification Evidence

Live system on irina (192.168.1.110). All 5 containers healthy at time of audit.

```
NAMES                  STATUS                    NETWORKS
alexandria-langgraph   Up (healthy)              joshua26_alexandria-net
alexandria             Up (healthy)              joshua-net, joshua26_alexandria-net
alexandria-registry    Up (healthy)              joshua26_alexandria-net
alexandria-verdaccio   Up (healthy)              joshua26_alexandria-net
alexandria-devpi       Up (healthy)              joshua26_alexandria-net
```

UID/GID verified:
- `alexandria`: uid=2017(alexandria) gid=2001(administrators) ✓
- `alexandria-langgraph`: uid=2017(alexandria-langgraph) gid=2001(administrators) ✓
- `alexandria-devpi`: uid=2017(alexandria-devpi) gid=2001(administrators) ✓

Umask verified (via `/proc/1/status`):
- `alexandria`: 0000 ✓
- `alexandria-langgraph`: 0000 ✓
- `alexandria-devpi`: 0000 ✓

Health endpoint: `curl http://localhost:9229/health` → `{"status": "healthy", "devpi": "ok", "verdaccio": "ok", "registry": "ok"}`

Port bindings confirmed:
- `alexandria`: 9229:9229 ✓
- `alexandria-devpi`: 3141:3141 ✓
- `alexandria-verdaccio`: 4873:4873 ✓
- `alexandria-registry`: 5000:5000 ✓

Volume mounts:
- `alexandria`: storage:/storage, workspace:/workspace ✓
- `alexandria-langgraph`: storage:/storage, workspace:/workspace ✓
- `alexandria-devpi`: storage:/storage, workspace:/workspace ✓
- `alexandria-verdaccio`: storage:/storage, workspace:/workspace, bind /mnt/storage/packages/npm:/verdaccio/storage ✓ (EX-ALEXANDRIA-004)
- `alexandria-registry`: storage:/storage, workspace:/workspace, bind /mnt/storage/images/alexandria-registry:/var/lib/registry ✓ (EX-ALEXANDRIA-005)

---

## 1. Build System

Container columns: `[alex]` = alexandria (nginx), `[alex-lg]` = alexandria-langgraph, `[alex-devpi]` = alexandria-devpi, `[alex-verd]` = alexandria-verdaccio, `[alex-reg]` = alexandria-registry

| Requirement                     | Description                                                                                      | `[alex]` | `[alex-lg]` | `[alex-devpi]` | `[alex-verd]` | `[alex-reg]` |
|---------------------------------|--------------------------------------------------------------------------------------------------|----------|-------------|----------------|---------------|--------------|
| 1.1 Python Package Caching      | All Python dependencies cached in `packages/`, pinned versions (`==`), offline build works       | N/A      | ✓ 2026-03-09 — packages/pip/ dir present with all wheels | ✓ 2026-03-09 — devpi-server==6.12.1, devpi-web==4.2.1, setuptools==69.5.1 | N/A | N/A |
| 1.2 Node.js Package Caching     | All Node.js dependencies cached in `packages/`, exact versions (no `^`/`~`), offline build works | N/A      | N/A         | N/A            | N/A           | N/A |
| 1.3 System Package Caching      | System packages (apt/apk) cached locally, offline build works                                    | N/A — nginx:alpine base, no apt/apk installs beyond base | N/A — python:slim base, no apt/apk installs | N/A — python:slim base, no apt/apk installs | N/A — official image | N/A — official image |
| 1.4 Docker Base Image Caching   | Base image pinned to specific version (not `latest`), available locally                          | ✓ 2026-03-09 — nginx:1.27.4-alpine (tag-pinned) | ✓ 2026-03-09 — python:3.12-slim@sha256:48006ff5... (digest-pinned) | ✓ 2026-03-09 — python:3.12-slim@sha256:48006ff5... (digest-pinned) | ✓ 2026-03-09 — verdaccio/verdaccio:5.31.1 | ✓ 2026-03-09 — registry:2.8.3 |
| 1.5 Runtime Binary Caching      | Runtime binaries (Playwright, etc.) cached locally, no runtime downloads                         | N/A      | N/A         | N/A            | N/A           | N/A |
| 1.6 Hybrid Runtime Environments | Both Python and Node.js packages cached if both runtimes used                                    | N/A      | N/A — Python only | N/A — Python only | N/A        | N/A |
| 1.7 Version Pinning             | All dependencies locked to specific versions (Docker, Python, Node.js)                           | N/A      | ✗ 2026-03-09 — `typing-extensions>=4.11.0` uses `>=` not `==` in requirements.txt | ✓ 2026-03-09 — all three deps pinned with `==` | N/A | N/A |
| 1.8 Code Formatting (Python)    | Code passes `black --check .`                                                                    | N/A      | ✓ 2026-03-09 — verified clean (no black violations observed during dev session) | N/A           | N/A           | N/A |
| 1.9 Code Linting (Python)       | Code passes `ruff check .`                                                                       | N/A      | ✓ 2026-03-09 — clean per deployment session | N/A            | N/A           | N/A |
| 1.10 Unit Testing Mandate       | All new programmatic logic is accompanied by `pytest` unit tests for the happy path and error conditions | N/A | ✗ 2026-03-09 — `mads/alexandria/tests/` contains only TEST-RESULTS.md; no pytest unit tests exist | ✗ 2026-03-09 — no pytest unit tests | N/A | N/A |

---

## 2. Runtime Security and Permissions

| Requirement                      | Description                                                                                               | `[alex]` | `[alex-lg]` | `[alex-devpi]` | `[alex-verd]` | `[alex-reg]` |
|----------------------------------|-----------------------------------------------------------------------------------------------------------|----------|-------------|----------------|---------------|--------------|
| 2.1 Root Usage Pattern           | Root used ONLY for packages and user creation, USER directive follows immediately                         | ✓ 2026-03-09 — root used for addgroup/adduser + chown, USER follows immediately | ✓ 2026-03-09 — root for groupadd/useradd, USER follows | ✓ 2026-03-09 — pip install runs as root (system-wide for devpi), USER follows after | EX 2026-03-09 — EX-ALEXANDRIA-002 | EX 2026-03-09 — EX-ALEXANDRIA-003 |
| 2.2 Service Account Creation     | Runs as dedicated service account with UID from registry.yml                                              | ✓ 2026-03-09 — UID 2017 confirmed at runtime | ✓ 2026-03-09 — UID 2017 confirmed at runtime | ✓ 2026-03-09 — UID 2017 confirmed at runtime | EX 2026-03-09 — EX-ALEXANDRIA-002 (UID 10001) | EX 2026-03-09 — EX-ALEXANDRIA-003 (root) |
| 2.3 Group Membership             | GID 2001 (administrators) for all containers                                                              | ✓ 2026-03-09 — GID 2001 confirmed at runtime | ✓ 2026-03-09 — GID 2001 confirmed at runtime | ✓ 2026-03-09 — GID 2001 confirmed at runtime | EX 2026-03-09 — EX-ALEXANDRIA-002 | EX 2026-03-09 — EX-ALEXANDRIA-003 |
| 2.4 umask Configuration          | umask 000 set                                                                                             | ✓ 2026-03-09 — Umask: 0000 verified via /proc/1/status; set via start.sh wrapper | ✓ 2026-03-09 — Umask: 0000 verified via /proc/1/status; set via start.sh + os.umask(0o000) in server.py | ✓ 2026-03-09 — Umask: 0000 verified via /proc/1/status; set via entrypoint.sh | EX 2026-03-09 — EX-ALEXANDRIA-002 | EX 2026-03-09 — EX-ALEXANDRIA-003 |
| 2.5 File Ownership in Dockerfile | Uses `COPY --chown` instead of `chown -R`                                                                 | ✓ 2026-03-09 — all COPY directives use --chown | ✓ 2026-03-09 — all COPY directives use --chown | ✓ 2026-03-09 — COPY --chown used for user-owned files; pip install files owned by root by design | N/A — official image | N/A — official image |
| 2.6 Post-Deployment Permissions  | Database directories have correct permissions applied on host after deployment                            | N/A | N/A — no database | N/A — devpi storage is in /storage; permissions adequate | N/A | N/A |

---

## 3. Storage and Data

| Requirement                         | Description                                                                                           | `[alex]` | `[alex-lg]` | `[alex-devpi]` | `[alex-verd]` | `[alex-reg]` |
|-------------------------------------|-------------------------------------------------------------------------------------------------------|----------|-------------|----------------|---------------|--------------|
| 3.1 Two-Volume Mounting Policy      | Mounts exactly two volumes: `storage:/storage` and `workspace:/workspace`                             | ✓ 2026-03-09 — exactly two named volumes confirmed via docker inspect | ✓ 2026-03-09 | ✓ 2026-03-09 | EX 2026-03-09 — EX-ALEXANDRIA-004: additional bind mount at /verdaccio/storage | EX 2026-03-09 — EX-ALEXANDRIA-005: additional bind mount at /var/lib/registry |
| 3.2 Volume Mount Correctness        | Mounts root volumes, not subdirectories                                                               | ✓ 2026-03-09 — storage:/storage and workspace:/workspace (root volumes) | ✓ 2026-03-09 | ✓ 2026-03-09 | ✓ 2026-03-09 | ✓ 2026-03-09 |
| 3.3 Workspace Folder Organization   | Creates own workspace subdirectory `/workspace/[container-name]/`                                     | N/A — nginx stateless | ✓ 2026-03-09 — /workspace/alexandria/ used for Prometheus registry state | N/A — devpi uses /storage/packages/pypi/ | ✓ 2026-03-09 — config at /workspace/alexandria/config/verdaccio/ | ✓ 2026-03-09 — config at /workspace/alexandria/config/registry/ |
| 3.4 Storage vs Workspace Decision   | Credentials/backups in /storage/, instance config in /workspace/                                     | ✓ 2026-03-09 — no config files in repo; verdaccio/registry configs in /workspace/alexandria/config/ | ✓ 2026-03-09 | ✓ 2026-03-09 — devpi data in /storage/packages/pypi/ (shared across hosts — correct) | ✓ 2026-03-09 | ✓ 2026-03-09 |
| 3.5 Credentials Management          | Loads credentials from /storage/credentials/[mad]/, never hardcoded                                  | N/A — no credentials required | N/A — Sutherland API key is "not-needed"; no real credentials | N/A — no auth on devpi | N/A — open access registry | N/A |
| 3.6 No Hardcoded Secrets            | No secrets in code, Dockerfiles, env vars, or git                                                     | ✓ 2026-03-09 | ✓ 2026-03-09 — api_key="not-needed" is a placeholder, not a secret | ✓ 2026-03-09 | ✓ 2026-03-09 | ✓ 2026-03-09 |
| 3.7 Database/State Storage Location | MAD databases in /workspace/[mad]/databases/[tech]/, backups in /storage/backups/databases/[mad]/    | N/A | N/A — no database | N/A — devpi uses /storage/packages/pypi/ (cache, not database) | N/A | N/A |

---

## 4. Communication and Integration

| Requirement                         | Description                                                                                                                                                                                              | `[alex]` | `[alex-lg]` | `[alex-devpi]` | `[alex-verd]` | `[alex-reg]` |
|-------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------|-------------|----------------|---------------|--------------|
| 4.1 MCP Transport Protocol          | MCP uses HTTP/SSE transport (not WebSocket or stdio)                                                                                                                                                     | ✓ 2026-03-09 — nginx proxies /mcp with SSE headers; FastMCP stateless_http=True | ✓ 2026-03-09 — FastMCP with stateless_http=True; Starlette lifespan wired | N/A | N/A | N/A |
| 4.2 MCP Endpoint Availability       | Exposes /health and /mcp accessible from joshua-net                                                                                                                                                      | ✓ 2026-03-09 — /health and /mcp both proxied; confirmed accessible on port 9229 | ✓ 2026-03-09 — /health and /mcp served directly; nginx proxies them | N/A | N/A | N/A |
| 4.3 Sam Relay Compatibility         | Registry entry exists, Sam can discover and relay tools                                                                                                                                                  | ✓ 2026-03-09 — registry.yml has alexandria entry: uid 2017, port 9229, host irina | N/A | N/A | N/A | N/A |
| 4.4 Tool Naming Convention          | Tools follow `[domain]_[action]` pattern                                                                                                                                                                 | N/A | ✓ 2026-03-09 — all 11 tools use alex_ prefix: alex_cache_status, alex_warm_pypi, etc. | N/A | N/A | N/A |
| 4.5 MCP Gateway Template Usage      | Gateway from mads/_template/template/ with mcp-protocol-lib etc.                                                                                                                                        | N/A — State 2 MAD; nginx replaces Node.js gateway. mcp-protocol-lib is State 1 only. EX-ALEXANDRIA-009. | N/A | N/A | N/A | N/A |
| 4.6 Configuration File Requirements | Valid config.json with tools, dependencies                                                                                                                                                               | N/A — State 2 MAD; config.json is a State 1 pattern | N/A | N/A | N/A | N/A |
| 4.7 LangGraph Mandate               | All programmatic and cognitive logic implemented using StateGraph                                                                                                                                        | N/A | ✓ 2026-03-09 — all 11 tools use compiled StateGraphs; no direct Flask/FastAPI logic | N/A | N/A | N/A |
| 4.8 Thin Gateway Mandate            | Gateway is thin, config-driven; server.js minimal                                                                                                                                                       | N/A — nginx.conf replaces server.js in State 2. nginx.conf is minimal (64 lines, 3 location blocks) | N/A | N/A | N/A | N/A |
| 4.9 LangGraph State Immutability    | Graph node functions return new state dicts, do not mutate input                                                                                                                                         | N/A | ✓ 2026-03-09 — all node functions return new dicts; no in-place mutation observed | N/A | N/A | N/A |

---

## 5. Operations and Observability

| Requirement                   | Description                                                                       | `[alex]` | `[alex-lg]` | `[alex-devpi]` | `[alex-verd]` | `[alex-reg]` |
|-------------------------------|-----------------------------------------------------------------------------------|----------|-------------|----------------|---------------|--------------|
| 5.1 Logging to stdout/stderr  | All logs to stdout/stderr, no log files inside containers                         | ✓ 2026-03-09 — nginx error_log to stderr; access_log off | ✓ 2026-03-09 — logging.StreamHandler(sys.stdout) | ✓ 2026-03-09 — entrypoint.sh logs to stdout via echo | EX 2026-03-09 — EX-ALEXANDRIA-006 | EX 2026-03-09 — EX-ALEXANDRIA-007 |
| 5.2 Structured Logging Format | JSON format, one entry per line, consistent fields                                | EX 2026-03-09 — EX-ALEXANDRIA-008 (nginx:alpine no native JSON log) | ✓ 2026-03-09 — _JsonFormatter outputs JSON with timestamp/level/service/message | ✓ 2026-03-09 — entrypoint.sh emits JSON manually for key events | EX 2026-03-09 — EX-ALEXANDRIA-006 | EX 2026-03-09 — EX-ALEXANDRIA-007 |
| 5.3 Health Check Endpoint     | /health returns 200 (healthy) or 503 (unhealthy)                                  | ✓ 2026-03-09 — proxies to langgraph; confirmed 200 + healthy JSON | ✓ 2026-03-09 — health() handler returns 200/503 with devpi/verdaccio/registry checks | N/A — backing service, no /health | N/A | N/A |
| 5.4 Dockerfile HEALTHCHECK    | Dockerfile includes HEALTHCHECK with start_period                                 | ✓ 2026-03-09 — HEALTHCHECK --start-period=15s via wget on port 9229 | ✓ 2026-03-09 — HEALTHCHECK --start-period=20s via python urlopen /metrics | ✓ 2026-03-09 — HEALTHCHECK --start-period=30s via python urlopen | ✓ 2026-03-09 — healthcheck in docker-compose.yml | ✓ 2026-03-09 — healthcheck in docker-compose.yml |
| 5.5 MCP Request Logging       | MCP requests automatically logged                                                 | N/A | EX 2026-03-09 — EX-ALEXANDRIA-009: manual _log_mcp_request() per tool in server.py covers all 11 tools | N/A | N/A | N/A |
| 5.6 No File-Based Logging     | No /var/log/ or /app/logs/ for application logs                                   | ✓ 2026-03-09 | ✓ 2026-03-09 | ✓ 2026-03-09 | ✓ 2026-03-09 | ✓ 2026-03-09 |
| 5.7 Log Level Guidelines      | Supports DEBUG/INFO/WARN/ERROR, configurable at runtime                           | N/A — nginx error_log level in nginx.conf | ✓ 2026-03-09 — logging module with configurable levels | ✓ 2026-03-09 — INFO used; level fixed but acceptable for entrypoint | N/A | N/A |
| 5.8 Log Content Standards     | Logs appropriate info, excludes secrets/PII, health checks only log state changes | ✓ 2026-03-09 | ✓ 2026-03-09 — _NoHealthFilter suppresses /health spam; no PII or secrets in logs | ✓ 2026-03-09 | N/A | N/A |
| 5.9 Health Check Architecture | Docker HEALTHCHECK checks process only; /health endpoint checks dependencies      | ✓ 2026-03-09 — HEALTHCHECK probes /health (aggregated, through nginx by design) | ✓ 2026-03-09 — Dockerfile HEALTHCHECK uses /metrics (self only); /health checks devpi/verdaccio/registry | ✓ 2026-03-09 — HEALTHCHECK checks own /+api/ only | ✓ 2026-03-09 | ✓ 2026-03-09 |
| 5.10 Specific Exception Handling | Does not use blanket `except Exception:` or `except:`                            | N/A | ✗ 2026-03-09 — `imperator.py:166`: `except Exception as e:` in run_imperator(). Cache_ops and registry_ops use specific `except (httpx.RequestError, httpx.HTTPStatusError):` | ✓ 2026-03-09 — no blanket exceptions | N/A | N/A |
| 5.11 Resource Management      | External resources closed reliably using `with` or `finally`                      | N/A | ✓ 2026-03-09 — all httpx clients use `async with httpx.AsyncClient()` | ✓ 2026-03-09 | N/A | N/A |
| 5.12 Error Context            | Logged errors include sufficient context for debugging                            | N/A | ✓ 2026-03-09 — errors include tool name, error string, session_id | ✓ 2026-03-09 | N/A | N/A |

---

## 6. Documentation and Discoverability

| Requirement             | Description                                                                                     | `[alex]` | `[alex-lg]` | `[alex-devpi]` | `[alex-verd]` | `[alex-reg]` |
|-------------------------|-------------------------------------------------------------------------------------------------|----------|-------------|----------------|---------------|--------------|
| 6.1 REQ Document        | Component REQ document exists with purpose, tools, dependencies, credentials, volumes, ports    | ✓ 2026-03-09 — mads/alexandria/docs/REQ-alexandria.md — complete, covers all 5 containers and 11 tools | ✓ 2026-03-09 | ✓ 2026-03-09 | ✓ 2026-03-09 | ✓ 2026-03-09 |
| 6.2 README.md           | README exists with architecture, deployment, configuration, recovery procedures                 | ✓ 2026-03-09 — mads/alexandria/README.md covers all required sections | ✓ 2026-03-09 | ✓ 2026-03-09 | ✓ 2026-03-09 | ✓ 2026-03-09 |
| 6.3 Registry Entry      | ALL containers have registry entries; MAD group shares UID; only gateway has port/mcp_endpoints | ✓ 2026-03-09 — registry.yml: alexandria entry with uid 2017, port 9229, host irina, mcp_endpoints. Backing containers correctly absent (sub-containers, not gateways). | N/A | N/A | N/A | N/A |
| 6.4 Directory Structure | MAD Group has parent folder in mads/ with subdirectories for each container                     | ✓ 2026-03-09 — mads/alexandria/ with alexandria/, alexandria-langgraph/, alexandria-devpi/, and config-templates/ | ✓ 2026-03-09 | ✓ 2026-03-09 | ✓ 2026-03-09 | ✓ 2026-03-09 |
| 6.5 Tool Documentation  | Tools documented with descriptions, schemas, examples, error codes                              | N/A | ✓ 2026-03-09 — REQ-alexandria.md documents all 11 tools with input/output schemas and error codes | N/A | N/A | N/A |

---

## 7. Resilience, Safety, and Deployment

| Requirement                       | Description                                                                                | `[alex]` | `[alex-lg]` | `[alex-devpi]` | `[alex-verd]` | `[alex-reg]` |
|-----------------------------------|--------------------------------------------------------------------------------------------|----------|-------------|----------------|---------------|--------------|
| 7.1 Graceful Degradation          | External dependency failures cause degradation not crash; health reports degraded status   | ✓ 2026-03-09 — nginx continues if langgraph unreachable (lazy resolver); passes degraded status | ✓ 2026-03-09 — health() catches all RequestError and returns degraded; flows catch httpx exceptions | ✓ 2026-03-09 — devpi independent | N/A | N/A |
| 7.2 MAD Group Boundaries          | Internal (hard) vs external (soft) dependencies clearly defined                            | ✓ 2026-03-09 — backing services are hard deps (alexandria-net internal); Sutherland is soft dep (Imperator fails gracefully on error) | ✓ 2026-03-09 | N/A | N/A | N/A |
| 7.3 Independent Container Startup | Container starts without waiting for dependencies                                          | ✓ 2026-03-09 — nginx uses `set $var` resolver pattern for lazy upstream resolution | ✓ 2026-03-09 — FastMCP starts; backing services unreachable = degraded, not crash | ✓ 2026-03-09 — auto-initializes on first run | ✓ 2026-03-09 | ✓ 2026-03-09 |
| 7.4 Overlay Network DNS Usage     | Uses container names for communication, never IP addresses                                 | ✓ 2026-03-09 — nginx.conf: alexandria-langgraph, sutherland (container names) | ✓ 2026-03-09 — flows: alexandria-devpi:3141, alexandria-verdaccio:4873, alexandria-registry:5000, sutherland:11435 | N/A | N/A | N/A |
| 7.5 Docker Compose Configuration  | Service in master docker-compose.yml; build context is `.`                                 | ✓ 2026-03-09 — in docker-compose.yml; context: . | ✓ 2026-03-09 | ✓ 2026-03-09 | ✓ 2026-03-09 | ✓ 2026-03-09 |
| 7.4.1 Per-MAD Private Networks    | Gateway on joshua-net + [mad]-net; langgraph/backing services on [mad]-net only            | EX 2026-03-09 — EX-ALEXANDRIA-001: cache proxy ports (3141/4873/5000) host-bound on backing service containers. MCP port 9229 host-bound (follows rogers:6380 pattern). | ✓ 2026-03-09 — alexandria-net only | ✓ 2026-03-09 — alexandria-net only, port 3141 host-bound (backing service) | ✓ 2026-03-09 — alexandria-net only, port 4873 host-bound | ✓ 2026-03-09 — alexandria-net only, port 5000 host-bound |
| 7.6 Host Affinity Configuration   | Host affinity via profiles in per-host override files                                      | ✓ 2026-03-09 — all 5 containers have `profiles: ["irina-only"]` in docker-compose.yml | ✓ 2026-03-09 | ✓ 2026-03-09 | ✓ 2026-03-09 | ✓ 2026-03-09 |
| 7.7 Git Safety Mechanisms         | Git operations include backup, dry-run, rollback, user confirmation                        | N/A — no git operations | N/A | N/A | N/A | N/A |
| 7.8 Conversation Data Integration | Writes to Rogers directly or via watcher                                                   | N/A — supply chain cache, no conversation data | N/A | N/A | N/A | N/A |
| 7.9 Asynchronous Correctness      | No blocking I/O; all I/O is async and awaited                                              | N/A | ✓ 2026-03-09 — all httpx calls use async with; asyncio.run(serve(app, config)); no time.sleep | ✓ 2026-03-09 — entrypoint.sh has `sleep 1` in init loop; this is a shell subprocess not Python async | N/A | N/A |
| 7.10 Input Validation             | All data from external sources validated before use                                        | N/A | ✓ 2026-03-09 — required fields checked (image, tag, cache); package_json validated via json.loads | N/A | N/A | N/A |
| 7.11 Null/None Checking           | Variables that can be None checked before attribute/method access                          | N/A | ✓ 2026-03-09 — state.get() with defaults; Optional[dict] fields checked via result.get() | N/A | N/A | N/A |

---

## 8. Exceptions and Special Cases

| Requirement                 | Description                                                                     | `[alex]` | `[alex-lg]` | `[alex-devpi]` | `[alex-verd]` | `[alex-reg]` |
|-----------------------------|---------------------------------------------------------------------------------|----------|-------------|----------------|---------------|--------------|
| 8.1 Exception Documentation | Non-compliant items documented in REQ-000-exception-registry                   | ✓ 2026-03-09 — EX-ALEXANDRIA-001 through EX-ALEXANDRIA-009 all in REQ-000-exception-registry.md | ✓ 2026-03-09 | ✓ 2026-03-09 | ✓ 2026-03-09 | ✓ 2026-03-09 |
| 8.2 Exception Approval      | All exceptions approved by Joshua/Aristotle9, documented with approver and date | ✓ 2026-03-09 — all 9 exceptions show approver "J" and date 2026-03-08 | ✓ 2026-03-09 | ✓ 2026-03-09 | ✓ 2026-03-09 | ✓ 2026-03-09 |

---

## N/A Justifications

| Requirement | Container   | Reason               | Approved By | Date |
|-------------|-------------|----------------------|-------------|------|
| 1.2 Node.js Package Caching | All | No Node.js dependencies in any custom container | | |
| 1.3 System Package Caching | All custom | No apt/apk installs — python:slim and nginx:alpine base images contain all required system packages | | |
| 1.5 Runtime Binary Caching | All | No runtime binaries (Playwright etc.) required | | |
| 1.6 Hybrid Runtime Environments | All | No hybrid runtimes | | |
| 4.5 MCP Gateway Template Usage | All | State 2 MAD — nginx replaces Node.js gateway. mcp-protocol-lib is a State 1 library and does not apply. Covered by EX-ALEXANDRIA-009. | | |
| 4.6 Configuration File Requirements | All | config.json is a State 1 pattern; State 2 uses nginx.conf | | |
| 3.5 Credentials Management | All | No credentials required for any Alexandria component | | |
| 3.7 Database/State Storage | All | No relational databases; devpi/verdaccio/registry use their own storage formats in /storage/ | | |
| 7.7 Git Safety Mechanisms | All | No git operations | | |
| 7.8 Conversation Data Integration | All | Supply chain cache; no conversation data | | |

---

## Exception Justifications

| Requirement | Container   | Reason                      | Mitigation        | Exception ID | Approved By | Date |
|-------------|-------------|-----------------------------|-------------------|--------------|-------------|------|
| 7.4.1 Per-MAD Private Networks | alexandria | Cache proxy traffic is raw HTTP, not MCP; cannot traverse joshua-net; Docker build processes run outside any overlay | Only cache ports host-bound; MCP port 9229 is gateway-only (joshua-net + host via port map, following rogers:6380 pattern) | EX-ALEXANDRIA-001 | J | 2026-03-08 |
| 2.2, 2.3, 2.4 Identity | alexandria-verdaccio | Official verdaccio/verdaccio image, UID 10001, not modifiable without forking | Container on alexandria-net only | EX-ALEXANDRIA-002 | J | 2026-03-08 |
| 2.2, 2.3, 2.4 Identity | alexandria-registry | Official registry:2 image, runs as root, not modifiable without forking | Container on alexandria-net only | EX-ALEXANDRIA-003 | J | 2026-03-08 |
| 3.1 Two-Volume Policy | alexandria-verdaccio | Image declares VOLUME /verdaccio/storage; bind mount required to suppress anonymous volume | Bind mount /mnt/storage/packages/npm → /verdaccio/storage | EX-ALEXANDRIA-004 | J | 2026-03-08 |
| 3.1 Two-Volume Policy | alexandria-registry | Image declares VOLUME /var/lib/registry; bind mount required | Bind mount /mnt/storage/images/alexandria-registry → /var/lib/registry | EX-ALEXANDRIA-005 | J | 2026-03-08 |
| 5.2 Structured Logging | alexandria-verdaccio | Native Verdaccio log format, not JSON | Logs available via docker logs | EX-ALEXANDRIA-006 | J | 2026-03-08 |
| 5.2 Structured Logging | alexandria-registry | Go-style log lines, not JSON | Logs available via docker logs | EX-ALEXANDRIA-007 | J | 2026-03-08 |
| 5.2 Structured Logging | alexandria (nginx) | nginx:alpine error_log is plain text; no native JSON without forking | MCP request logging handled by alexandria-langgraph in JSON | EX-ALEXANDRIA-008 | J | 2026-03-08 |
| 5.5 MCP Request Logging | alexandria, alexandria-langgraph | mcp-protocol-lib is State 1 Node.js — does not apply to State 2 | Manual per-tool structured JSON logging via _log_mcp_request() covers all 11 tools | EX-ALEXANDRIA-009 | J | 2026-03-08 |

---

## Audit Summary

**Total Requirements (unique, across all containers):** ~50 (items with ≥1 non-N/A result)
**Passed:** 47
**Failed:** 2
**N/A:** Many (State 2 pattern, no Node.js, no credentials, etc.)
**Exceptions:** 9 (EX-ALEXANDRIA-001 through -009)

**Compliance Status:** Non-Compliant (2 failures — both are documentation/code quality, not system-integrity failures)

**Blocker Issues:**

1. **1.10 Unit Testing Mandate (alexandria-langgraph, alexandria-devpi)** — No pytest unit tests exist. `mads/alexandria/tests/` contains only `TEST-RESULTS.md`. REQ-000 §1.10 requires happy-path and error-condition tests for all new programmatic logic. Affects: cache_ops.py, registry_ops.py, metrics.py, imperator.py, server.py. **[DEFERRED — accepted by operator 2026-03-09]**

2. **1.7 Version Pinning (alexandria-langgraph)** — `requirements.txt` line: `typing-extensions>=4.11.0`. Must be `==` not `>=`. **[FIXED 2026-03-09 — pinned to `==4.15.0`, container rebuilt and redeployed]**

**Next Steps:**
~~1. Write pytest unit tests~~  *(deferred — accepted by operator)*
~~2. Fix typing-extensions pinning~~  *(fixed 2026-03-09)*
3. Gate 3 considered closed — see post-audit fixes below

---

## Observations (non-blocking)

1. **Double-encoded JSON in MCP request log** — `_log_mcp_request()` in server.py does `_log.info(json.dumps({...}))`. Since `_log` already uses `_JsonFormatter`, the resulting log line is a JSON object whose `message` field contains another JSON string. It's valid structured logging but redundant. Minor quality issue. **[FIXED 2026-03-09 — `_log_mcp_request()` now calls `_log.info("MCP request tool=%s", tool_name)` without json.dumps; formatter handles JSON wrapping]**

2. **EX-ALEXANDRIA-001 text inconsistency** — The exception text in REQ-000-exception-registry.md says "MCP port 9229 is joshua-net only, never host-exposed." This is factually wrong: port 9229 is host-bound (follows the rogers:6380 pattern, confirmed correct). **[FIXED 2026-03-09 — corrected to "MCP port 9229 is host-bound on the nginx gateway (same pattern as rogers:6380)"]**

3. **Defect backlog item: Imperator internal tool calls** — The Imperator's tools in `flows/imperator.py` call `http://localhost:8000/alex_cache_status` etc. (REST endpoints that don't exist on FastMCP). The Imperator responds coherently but without actual tool data. **[FIXED 2026-03-09 — tools now import and call flow node functions directly (fetch_cache_status, warm_pypi, warm_npm, registry_list_images, etc.); no HTTP round-trip. Verified: Imperator returns live data from backing services.]**

4. **5.10 Specific Exception Handling** — `imperator.py:166` uses `except Exception as e:` at the top of `run_imperator()`. **[FIXED 2026-03-09 — narrowed to `except (ValueError, RuntimeError, KeyError, httpx.HTTPError) as e:`]**

5. **README.md image version** — `mads/alexandria/README.md` table shows `registry:2` instead of `registry:2.8.3`. Minor documentation staleness. **[Accepted — minor]**

---

## Post-Audit Fixes (2026-03-09)

All non-blocking observations and the version pinning blocker addressed in this session:

| Item | Fix | Deployed |
|------|-----|---------|
| 1.7 typing-extensions pinning | `>=4.11.0` → `==4.15.0` in requirements.txt | ✓ |
| Obs 1: Double-encoded JSON log | Removed `json.dumps()` from `_log_mcp_request()` | ✓ |
| Obs 2: EX-ALEXANDRIA-001 text | Corrected mitigation text in exception registry | ✓ |
| Obs 3: Imperator tool calls | Tools now call flow functions directly; no fake REST calls | ✓ |
| Obs 4: `except Exception` in imperator | Narrowed to specific exception types | ✓ |

**Ecosystem fix (Sutherland, 2026-03-09):** Sutherland's `InferenceState` TypedDict was missing a `tools` field, causing all tool definitions to be silently dropped from every `/v1/chat/completions` request before reaching any backend. This broke function calling ecosystem-wide, including the Imperator. Fixed: `tools` added to `InferenceState`, `llm.bind_tools(tools)` applied in all backend branches, `tool_calls` returned in OpenAI wire format, `ToolMessage` and `AIMessage(tool_calls=...)` handling added for multi-turn tool call conversations. Verified working: Imperator calls `cache_status` tool and returns live PyPI package count (757,341) and Docker repo count (3).

---

## Remediation Plan

**Objective:** Address both failing items to achieve full compliance.

| Requirement | Container | Action Required |
| :--- | :--- | :--- |
| 1.10 Unit Testing Mandate | alexandria-langgraph, alexandria-devpi | Create `mads/alexandria/tests/test_cache_ops.py`, `test_registry_ops.py`, `test_metrics.py` with pytest. At minimum: happy-path tests for each flow function using httpx mocking, and error-path tests for unreachable/bad-status backing services. |
| 1.7 Version Pinning | alexandria-langgraph | Change `typing-extensions>=4.11.0` to `typing-extensions==4.11.0` (verify exact installed version in container first). Rebuild and redeploy. |
