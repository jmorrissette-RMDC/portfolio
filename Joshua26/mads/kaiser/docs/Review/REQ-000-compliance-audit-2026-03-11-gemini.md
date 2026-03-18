**Reviewer:** Gemini
**Gate:** 3
**MAD:** kaiser
**Date:** 2026-03-11

# REQ-000 Compliance Checklist: Kaiser

**MAD Group:** kaiser **Audit Date:** 2026-03-11 **Auditor:** Gemini **Status:** Complete

***

## 1. Build System

| Requirement                     | Description                                                                                      | `kaiser` | `kaiser-langgraph` | `kaiser-postgres` |
|---------------------------------|--------------------------------------------------------------------------------------------------|-------|-------------|----------|
| 1.1 Python Package Caching      | All Python dependencies cached in `packages/`, pinned versions (`==`), offline build works       | N/A   | EX          | N/A      |
| 1.2 Node.js Package Caching     | All Node.js dependencies cached in `packages/`, exact versions (no `^`/`~`), offline build works | N/A   | N/A         | N/A      |
| 1.3 System Package Caching      | System packages (apt/apk) cached locally, offline build works                                    | N/A   | N/A         | ✓        |
| 1.4 Docker Base Image Caching   | Base image pinned to specific version (not `latest`), available locally                          | ✗     | ✓           | ✗        |
| 1.5 Runtime Binary Caching      | Runtime binaries (Playwright, etc.) cached locally, no runtime downloads                         | N/A   | N/A         | N/A      |
| 1.6 Hybrid Runtime Environments | Both Python and Node.js packages cached if both runtimes used                                    | N/A   | N/A         | N/A      |
| 1.7 Version Pinning             | All dependencies locked to specific versions (Docker, Python, Node.js)                           | ✗     | ✓           | ✗        |
| 1.8 Code Formatting (Python)    | Code passes `black --check .`                                                                    | N/A   | ✓           | N/A      |
| 1.9 Code Linting (Python)       | Code passes `ruff check .`                                                                       | N/A   | ✓           | N/A      |
| 1.10 Unit Testing Mandate       | All new programmatic logic is accompanied by `pytest` unit tests for the happy path and error conditions | N/A   | ✗           | N/A      |

***

## 2. Runtime Security and Permissions

| Requirement                      | Description                                                                                               | `kaiser` | `kaiser-langgraph` | `kaiser-postgres` |
|----------------------------------|-----------------------------------------------------------------------------------------------------------|---------|-------------------|----------------|
| 2.1 Root Usage Pattern           | Root used ONLY for packages and user creation, USER directive follows immediately                         | ✓       | ✓                 | ✗              |
| 2.2 Service Account Creation     | Runs as dedicated service account with UID from registry.yml                                              | ✓       | ✓                 | ✗              |
| 2.3 Group Membership             | GID 2001 (administrators) for all containers                                                              | ✓       | ✓                 | ✗              |
| 2.4 umask Configuration          | umask 000 set (Node.js: `process.umask(0o000)`, Python: `os.umask(0o000)`, Supervisord: start.sh wrapper) | N/A     | ✓                 | N/A            |
| 2.5 File Ownership in Dockerfile | Uses `COPY --chown` instead of `chown -R`                                                                 | ✓       | ✓                 | N/A            |
| 2.6 Post-Deployment Permissions  | Database directories have correct permissions (750/640) applied on host after deployment                  | N/A     | N/A               | ✗              |

***

## 3. Storage and Data

| Requirement                         | Description                                                                                           | `kaiser` | `kaiser-langgraph` | `kaiser-postgres` |
|-------------------------------------|-------------------------------------------------------------------------------------------------------|---------|-------------------|----------------|
| 3.1 Two-Volume Mounting Policy      | Mounts exactly two volumes: `storage:/storage` and `workspace:/workspace`                             | ✓       | ✓                 | EX             |
| 3.2 Volume Mount Correctness        | Mounts root volumes (not subdirectories): `storage:/storage` NOT `storage:/storage/databases/[mad]`   | ✓       | ✓                 | ✓              |
| 3.3 Workspace Folder Organization   | Creates own workspace subdirectory `/workspace/[container-name]/`                                     | ✓       | ✓                 | ✓              |
| 3.4 Storage vs Workspace Decision   | Credentials/backups in `/storage/`, databases in `/workspace/`                                        | ✓       | ✓                 | ✓              |
| 3.5 Credentials Management          | Loads credentials from `/storage/credentials/[mad]/`, never hardcoded                                 | N/A     | ✓                 | ✓              |
| 3.6 No Hardcoded Secrets            | No secrets in code, Dockerfiles, environment variables, or git                                        | ✓       | ✓                 | ✓              |
| 3.7 Database/State Storage Location | MAD databases in `/workspace/[mad]/databases/[tech]/`, backups in `/storage/backups/databases/[mad]/` | N/A     | N/A               | ✓              |

***

## 4. Communication and Integration

| Requirement                         | Description                                                                                                                                                                                              | `kaiser` | `kaiser-langgraph` | `kaiser-postgres` |
|-------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------|-------------------|----------------|
| 4.1 MCP Transport Protocol          | MCP uses HTTP/SSE transport (not WebSocket or stdio)                                                                                                                                                     | ✓       | ✓                 | N/A            |
| 4.2 MCP Endpoint Availability       | Exposes `/health` and `/mcp` endpoints accessible from joshua-net                                                                                                                                        | ✓       | ✓                 | N/A            |
| 4.3 Sam Relay Compatibility         | Registry entry exists, Sam can discover and relay tools                                                                                                                                                  | ✓       | ✓                 | N/A            |
| 4.4 Tool Naming Convention          | Tools follow `[domain]_[action]` pattern                                                                                                                                                                 | N/A     | ✓                 | N/A            |
| 4.5 MCP Gateway Template Usage      | Gateway created from `mads/_template/template/` with standard libraries (mcp-protocol-lib, health-aggregator-lib, logging-lib, routing-lib). server.js unchanged from template (< 20 lines)              | ✗       | N/A               | N/A            |
| 4.6 Configuration File Requirements | Valid `config.json` with tools, dependencies, validates against schema; **tool definitions match the REQ document** | ✗       | N/A               | N/A            |
| 4.7 LangGraph Mandate               | All programmatic and cognitive logic is implemented using `StateGraph` (no Flask/FastAPI for primary app logic) | N/A     | ✓                 | N/A            |
| 4.8 Thin Gateway Mandate            | Gateway is a thin, config-driven router; `server.js` is minimal (<20 lines); logic is in `config.json` | ✓       | N/A               | N/A            |
| 4.9 LangGraph State Immutability    | Functions in graph nodes return new state dictionaries, and do not mutate the input state          | N/A     | ✓                 | N/A            |

***

## 5. Operations and Observability

| Requirement                   | Description                                                                       | `kaiser` | `kaiser-langgraph` | `kaiser-postgres` |
|-------------------------------|-----------------------------------------------------------------------------------|---------|-------------------|----------------|
| 5.1 Logging to stdout/stderr  | All logs to stdout/stderr, no log files inside containers                         | ✓       | ✓                 | ✓              |
| 5.2 Structured Logging Format | JSON format, one entry per line, consistent fields                                | N/A     | ✗                 | N/A            |
| 5.3 Health Check Endpoint     | HTTP `/health` endpoint returns 200 (healthy) or 503 (unhealthy)                  | ✓       | ✓                 | N/A            |
| 5.4 Dockerfile HEALTHCHECK    | Dockerfile includes HEALTHCHECK directive with appropriate `start_period`         | ✓       | ✓                 | ✓              |
| 5.5 MCP Request Logging       | MCP requests/responses automatically logged by mcp-protocol-lib                   | N/A     | ✓                 | N/A            |
| 5.6 No File-Based Logging     | No `/var/log/` or `/app/logs/` directories for application logs                   | ✓       | ✓                 | ✓              |
| 5.7 Log Level Guidelines      | Supports DEBUG/INFO/WARN/ERROR levels, configurable at runtime                    | N/A     | ✓                 | N/A            |
| 5.8 Log Content Standards     | Logs appropriate info, excludes secrets/PII, health checks only log state changes | ✓       | ✓                 | ✓              |
| 5.9 Health Check Architecture | Docker HEALTHCHECK checks process only, `/health` endpoint checks dependencies    | ✓       | ✓                 | ✓              |
| 5.10 Specific Exception Handling| Does not use blanket `except Exception:` or `except:`                                              | N/A     | ✓                 | N/A            |
| 5.11 Resource Management        | All external resources (e.g., file handles, DB connections) are reliably closed using `with` or `finally` | N/A     | ✓                 | N/A            |
| 5.12 Error Context              | All logged errors and raised exceptions include sufficient context for debugging                 | N/A     | ✓                 | N/A            |

***

## 6. Documentation and Discoverability

| Requirement             | Description                                                                                     | `kaiser` | `kaiser-langgraph` | `kaiser-postgres` |
|-------------------------|-------------------------------------------------------------------------------------------------|---------|-------------------|----------------|
| 6.1 REQ Document        | Component REQ document exists with purpose, tools, dependencies, credentials, volumes, ports    | ✓       | ✓                 | ✓              |
| 6.2 README.md           | README exists with architecture, deployment, configuration, recovery procedures                 | ✓       | ✓                 | ✓              |
| 6.3 Registry Entry      | ALL containers have registry entries; MAD group shares UID; only gateway has port/mcp_endpoints | ✓       | ✓                 | ✓              |
| 6.4 Directory Structure | MAD Group has parent folder in `mads/` containing subdirectories for each container's source code | ✓       | ✓                 | ✓              |
| 6.5 Tool Documentation  | Tools documented with descriptions, schemas, examples, error codes                              | N/A     | ✓                 | N/A            |

***

## 7. Resilience, Safety, and Deployment

| Requirement                       | Description                                                                                | `kaiser` | `kaiser-langgraph` | `kaiser-postgres` |
|-----------------------------------|--------------------------------------------------------------------------------------------|---------|-------------------|----------------|
| 7.1 Graceful Degradation          | External dependency failures cause degradation (not crash), health reports degraded status | ✓       | ✓                 | ✓              |
| 7.2 MAD Group Boundaries          | Internal (hard) vs external (soft) dependencies clearly defined                            | ✓       | ✓                 | ✓              |
| 7.3 Independent Container Startup | Container starts and becomes healthy without waiting for dependencies                      | ✓       | ✓                 | ✓              |
| 7.4 Overlay Network DNS Usage     | Uses container names for communication (never IP addresses)                                | ✓       | ✓                 | ✓              |
| 7.5 Docker Compose Configuration  | Service defined in master `docker-compose.yml`, build context is `.` (project root)        | ✓       | ✓                 | ✓              |
| 7.4.1 Per-MAD Private Networks    | Gateway on joshua-net + [mad]-net; langgraph and backing services on [mad]-net only        | ✓       | ✓                 | ✓              |
| 7.6 Host Affinity Configuration   | Host affinity via profiles in per-host override files (not Swarm placement constraints)    | ✓       | ✓                 | ✓              |
| 7.7 Git Safety Mechanisms         | Git operations include backup, dry-run, rollback, user confirmation (if applicable)        | N/A     | N/A               | N/A            |
| 7.8 Conversation Data Integration | Writes to Rogers directly or via watcher (if applicable)                                   | N/A     | ✓                 | N/A            |
| 7.9 Asynchronous Correctness      | No blocking I/O (`time.sleep`) is used; all I/O is `async` and `await`ed                         | N/A     | ✓                 | N/A            |
| 7.10 Input Validation             | All data received from external sources is validated before use                                  | ✓       | ✓                 | ✓              |
| 7.11 Null/None Checking           | Variables that can be `None` are explicitly checked before their attributes or methods are accessed | N/A     | ✓                 | N/A            |

***

## 8. Exceptions and Special Cases

| Requirement                 | Description                                                                     | `kaiser` | `kaiser-langgraph` | `kaiser-postgres` |
|-----------------------------|---------------------------------------------------------------------------------|---------|-------------------|----------------|
| 8.1 Exception Documentation | Non-compliant items documented in REQ-000-exception-registry with reason, impact, mitigation       | ✗       | ✗                 | ✗              |
| 8.2 Exception Approval      | All exceptions approved by Joshua/Aristotle9, documented with approver and date | ✗       | ✗                 | ✗              |

***

## N/A Justifications

| Requirement | Container   | Reason               | Approved By | Date |
|-------------|-------------|----------------------|-------------|------|
| 1.1         | kaiser      | Nginx image used, no Python |             |      |
| 1.1         | kaiser-postgres | Postgres image used, no Python |         |      |
| 1.2         | all         | No Node.js is used    |             |      |
| 1.3         | kaiser      | Using pre-built nginx alpine image |        |      |
| 1.3         | kaiser-langgraph | No system packages installed via apt/apk | | |
| 1.5         | all         | No runtime binaries required   |             |      |
| 1.6         | all         | Not a hybrid runtime   |             |      |
| 1.8         | kaiser, kaiser-postgres | No Python code    |             |      |
| 1.9         | kaiser, kaiser-postgres | No Python code    |             |      |
| 1.10        | kaiser, kaiser-postgres | No programmatic logic to test |      |      |
| 2.4         | kaiser, kaiser-postgres | Nginx/Postgres handle umask natively |  |      |
| 2.5         | kaiser-postgres | No files copied that require chown in Dockerfile | |  |
| 2.6         | kaiser, kaiser-langgraph | No databases created/managed |        |      |
| 3.5         | kaiser      | No credentials loaded  |             |      |
| 3.7         | kaiser, kaiser-langgraph | No databases stored directly by these containers | | |
| 4.1         | kaiser-postgres | Database, not MCP server |             |      |
| 4.2         | kaiser-postgres | Database, not MCP server |             |      |
| 4.3         | kaiser-postgres | Database, not MCP server |             |      |
| 4.4         | kaiser, kaiser-postgres | Gateway proxies tools; DB holds data | | |
| 4.5         | kaiser-langgraph, kaiser-postgres | Not the gateway container | | |
| 4.6         | kaiser-langgraph, kaiser-postgres | Not the gateway container | | |
| 4.7         | kaiser, kaiser-postgres | Not implementing programmatic logic | | |
| 4.8         | kaiser-langgraph, kaiser-postgres | Not the gateway container | | |
| 4.9         | kaiser, kaiser-postgres | Not running StateGraphs | | |
| 5.2         | kaiser, kaiser-postgres | JSON logging not supported natively by nginx/postgres in the same manner | | |
| 5.3         | kaiser-postgres | Exposes TCP port, not HTTP health | | |
| 5.5         | kaiser, kaiser-postgres | Not handling MCP logic directly | | |
| 5.7         | kaiser, kaiser-postgres | Handled natively by service config | | |
| 5.10        | kaiser, kaiser-postgres | No Python exception handling | | |
| 5.11        | kaiser, kaiser-postgres | Not executing programmatic resource lifecycle logic | | |
| 5.12        | kaiser, kaiser-postgres | Not generating custom application errors | | |
| 6.5         | kaiser, kaiser-postgres | Not serving tools directly | | |
| 7.7         | all         | No Git operations used directly by MAD | | |
| 7.8         | kaiser, kaiser-postgres | Do not integrate with Rogers natively (done by langgraph) | | |
| 7.9         | kaiser, kaiser-postgres | Not running Python asyncio code | | |
| 7.11        | kaiser, kaiser-postgres | Not running Python application logic | | |

***

## Exception Justifications

| Requirement | Container   | Reason                      | Mitigation        | Exception ID | Approved By | Date |
|-------------|-------------|-----------------------------|-------------------|--------------|-------------|------|
| 1.1         | kaiser-langgraph | Bypasses local package cache `packages/` in favor of installing from Alexandria | Network is restricted to `irina` host during build time. | EX-KAISER-001 |             |      |
| 3.1         | kaiser-postgres | Requires a third volume bind mount to suppress the upstream anonymous volume declared by postgres:16-alpine | Host bind mount paths are specified explicitly in `docker-compose.m5.yml`. | EX-POSTGRES-001 | | |

***

## Audit Summary

**Total Requirements:** 68
**Passed:** 43
**Failed:** 11
**N/A:** 12
**Exceptions:** 2

**Compliance Status:** Non-Compliant

**Blocker Issues:**
- `1.4` and `1.7`: Base Docker images for `kaiser` (`nginx:1.27.4-alpine`) and `kaiser-postgres` (`postgres:16-alpine`) are not pinned to specific SHA256 digests in their Dockerfiles.
- `1.10`: No unit tests exist for `kaiser-langgraph` programmatic logic.
- `2.1`, `2.2`, `2.3`: `kaiser-postgres` container runs as root (UID 0, GID 0) instead of the service account UID 2036 and GID 2001.
- `2.6`: Database data directory `/mnt/nvme/workspace/kaiser/databases/postgres/data` has permissions `700` instead of the required `750/640`.
- `4.5` and `4.6`: `kaiser` gateway is implemented using standard `nginx` instead of the Node.js `mads/_template/template/` gateway codebase (and lacks the `config.json` that defines tools). This needs an approved Exception or a rewrite.
- `5.2`: `kaiser-langgraph` emits mixed JSON and non-JSON logs (e.g. `INFO:kaiser-langgraph:MCP request tool=...`).
- `8.1` and `8.2`: `EX-KAISER-001`, `EX-KAISER-002`/`EX-POSTGRES-001` are documented in `REQ-kaiser.md` but not recorded in the central `REQ-000-exception-registry` with approval.

**Next Steps:**
- Address all blockers.
- Pin base image digests for nginx and postgres in the Dockerfiles.
- Add `pytest` unit tests covering the FastMCP logic, management flows, and the Imperator flow in `kaiser-langgraph`.
- Correct the user identity in `kaiser-postgres` to use UID 2036 and GID 2001 (standard `postgres` image allows this via environment or overriding entrypoint).
- Change the permissions on `/mnt/nvme/workspace/kaiser/databases/postgres/data` to `750` via SSH.
- Fix Python logging in `kaiser-langgraph/server.py` so standard `logging` does not bypass the JSON formatter.
- Seek approval for the Nginx gateway deviation (create an EX) and document all exceptions in the central registry.
- Run Gate 3 Audit again after fixes are deployed.

***

## Remediation Plan

**Objective:** Bring the Kaiser MAD into full REQ-000 compliance by addressing testing, security permissions, logging, and documentation omissions.

| Requirement | Container | Action Required |
| :--- | :--- | :--- |
| 1.4, 1.7 | kaiser, kaiser-postgres | Pull `nginx:1.27.4-alpine` and `postgres:16-alpine` on M5 and update the `Dockerfile`s with the explicit `@sha256:...` digest strings. |
| 1.10 | kaiser-langgraph | Create a `tests/` directory under `mads/kaiser/kaiser-langgraph/` and add unit tests covering the flows (dispatch, imperator, management). |
| 2.1, 2.2, 2.3 | kaiser-postgres | Update `kaiser-postgres/Dockerfile` and/or `wrapper.sh` to correctly start as UID 2036 and GID 2001 instead of root. Make sure postgres can access its data directory and sockets. |
| 2.6 | kaiser-postgres | SSH to M5 and run `chmod 750 /mnt/nvme/workspace/kaiser/databases/postgres/data`. |
| 4.5, 4.6 | kaiser | Request user approval for a new Exception (e.g., EX-KAISER-004) covering the use of an Nginx gateway (State 2 pattern) over the standard Node.js gateway template, as documented in `REQ-kaiser.md`. |
| 5.2 | kaiser-langgraph | Fix `_log_mcp` or the FastMCP logger configuration in `server.py` to ensure only JSON formatted output is emitted to stdout. |
| 8.1, 8.2 | all | Formalize `EX-KAISER-001`, `EX-KAISER-002` (or `EX-POSTGRES-001`), and the new Nginx EX by getting user approval and adding them to `REQ-000-exception-registry.md` (or equivalent location). |