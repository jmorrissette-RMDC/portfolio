**Reviewer:** Gemini
**Gate:** 3
**MAD:** kaiser
**Date:** 2026-03-11

# REQ-000 Compliance Checklist: Kaiser

**MAD Group:** kaiser **Audit Date:** 2026-03-11 **Auditor:** Gemini **Status:** Complete

***

## 1. Build System

| Requirement | Description | `kaiser` | `kaiser-langgraph` | `kaiser-postgres` |
| :--- | :--- | :--- | :--- | :--- |
| 1.1 Python Package Caching | All Python dependencies cached in `packages/`, pinned versions (`==`), offline build works | N/A | EX | N/A |
| 1.2 Node.js Package Caching | All Node.js dependencies cached in `packages/`, exact versions (no `^`/`~`), offline build works | N/A | N/A | N/A |
| 1.3 System Package Caching | System packages (apt/apk) cached locally, offline build works | N/A | N/A | ✓ |
| 1.4 Docker Base Image Caching | Base image pinned to specific version (not `latest`), available locally | ✓ | ✓ | ✓ |
| 1.5 Runtime Binary Caching | Runtime binaries (Playwright, etc.) cached locally, no runtime downloads | N/A | N/A | N/A |
| 1.6 Hybrid Runtime Environments | Both Python and Node.js packages cached if both runtimes used | N/A | N/A | N/A |
| 1.7 Version Pinning | All dependencies locked to specific versions (Docker, Python, Node.js) | ✓ | ✗ | ✓ |
| 1.8 Code Formatting (Python) | Code passes `black --check .` / `ruff format` | N/A | ✓ | N/A |
| 1.9 Code Linting (Python) | Code passes `ruff check .` | N/A | ✓ | N/A |
| 1.10 Unit Testing Mandate | All new programmatic logic is accompanied by `pytest` unit tests for the happy path and error conditions | N/A | EX | N/A |

***

## 2. Runtime Security and Permissions

| Requirement | Description | `kaiser` | `kaiser-langgraph` | `kaiser-postgres` |
| :--- | :--- | :--- | :--- | :--- |
| 2.1 Root Usage Pattern | Root used ONLY for packages and user creation, USER directive follows immediately | ✓ | ✓ | EX |
| 2.2 Service Account Creation | Runs as dedicated service account with UID from registry.yml | ✓ | ✓ | EX |
| 2.3 Group Membership | GID 2001 (administrators) for all containers | ✓ | ✓ | EX |
| 2.4 umask Configuration | umask 000 set (Node.js: `process.umask(0o000)`, Python: `os.umask(0o000)`, Supervisord: start.sh wrapper) | ✓ | ✓ | EX |
| 2.5 File Ownership in Dockerfile | Uses `COPY --chown` instead of `chown -R` | ✓ | ✓ | ✓ |
| 2.6 Post-Deployment Permissions | Database directories have correct permissions (750/640) applied on host after deployment | N/A | N/A | ✗ |

***

## 3. Storage and Data

| Requirement | Description | `kaiser` | `kaiser-langgraph` | `kaiser-postgres` |
| :--- | :--- | :--- | :--- | :--- |
| 3.1 Two-Volume Mounting Policy | Mounts exactly two volumes: `storage:/storage` and `workspace:/workspace` | ✓ | ✓ | EX |
| 3.2 Volume Mount Correctness | Mounts root volumes (not subdirectories): `storage:/storage` NOT `storage:/storage/databases/[mad]` | ✓ | ✓ | ✓ |
| 3.3 Workspace Folder Organization | Creates own workspace subdirectory `/workspace/[container-name]/` | N/A | ✓ | ✓ |
| 3.4 Storage vs Workspace Decision | Credentials/backups in `/storage/`, databases in `/workspace/` | ✓ | ✓ | ✓ |
| 3.5 Credentials Management | Loads credentials from `/storage/credentials/[mad]/`, never hardcoded | N/A | ✓ | ✓ |
| 3.6 No Hardcoded Secrets | No secrets in code, Dockerfiles, environment variables, or git | ✓ | ✓ | ✓ |
| 3.7 Database/State Storage Location | MAD databases in `/workspace/[mad]/databases/[tech]/`, backups in `/storage/backups/databases/[mad]/` | N/A | N/A | ✓ |

***

## 4. Communication and Integration

| Requirement | Description | `kaiser` | `kaiser-langgraph` | `kaiser-postgres` |
| :--- | :--- | :--- | :--- | :--- |
| 4.1 MCP Transport Protocol | MCP uses HTTP/SSE transport (not WebSocket or stdio) | ✓ | ✓ | N/A |
| 4.2 MCP Endpoint Availability | Exposes `/health` and `/mcp` endpoints accessible from joshua-net | ✓ | ✓ | N/A |
| 4.3 Sam Relay Compatibility | Registry entry exists, Sam can discover and relay tools | ✓ | N/A | N/A |
| 4.4 Tool Naming Convention | Tools follow `[domain]_[action]` pattern | N/A | ✓ | N/A |
| 4.5 MCP Gateway Template Usage | Gateway created from `mads/_template/template/` | EX | N/A | N/A |
| 4.6 Configuration File Requirements | Valid `config.json` with tools, dependencies, validates against schema | EX | N/A | N/A |
| 4.7 LangGraph Mandate | All programmatic and cognitive logic is implemented using `StateGraph` | N/A | ✓ | N/A |
| 4.8 Thin Gateway Mandate | Gateway is a thin, config-driven router; `server.js` is minimal | EX | N/A | N/A |
| 4.9 LangGraph State Immutability | Functions in graph nodes return new state dictionaries | N/A | ✓ | N/A |

***

## 5. Operations and Observability

| Requirement | Description | `kaiser` | `kaiser-langgraph` | `kaiser-postgres` |
| :--- | :--- | :--- | :--- | :--- |
| 5.1 Logging to stdout/stderr | All logs to stdout/stderr, no log files inside containers | ✓ | ✓ | ✓ |
| 5.2 Structured Logging Format | JSON format, one entry per line, consistent fields | EX | ✓ | EX |
| 5.3 Health Check Endpoint | HTTP `/health` endpoint returns 200 (healthy) or 503 (unhealthy) | ✓ | ✓ | N/A |
| 5.4 Dockerfile HEALTHCHECK | Dockerfile includes HEALTHCHECK directive with appropriate `start_period` | ✓ | ✓ | ✓ |
| 5.5 MCP Request Logging | MCP requests/responses automatically logged by mcp-protocol-lib | N/A | ✗ | N/A |
| 5.6 No File-Based Logging | No `/var/log/` or `/app/logs/` directories for application logs | ✓ | ✓ | ✓ |
| 5.7 Log Level Guidelines | Supports DEBUG/INFO/WARN/ERROR levels, configurable at runtime | ✓ | ✓ | ✓ |
| 5.8 Log Content Standards | Logs appropriate info, excludes secrets/PII, health checks only log state changes | ✓ | ✓ | ✓ |
| 5.9 Health Check Architecture | Docker HEALTHCHECK checks process only, `/health` endpoint checks dependencies | ✓ | ✓ | ✓ |
| 5.10 Specific Exception Handling| Does not use blanket `except Exception:` or `except:` | N/A | ✓ | N/A |
| 5.11 Resource Management | All external resources (e.g., file handles, DB connections) are reliably closed using `with` or `finally` | N/A | ✓ | N/A |
| 5.12 Error Context | All logged errors and raised exceptions include sufficient context for debugging | N/A | ✓ | N/A |

***

## 6. Documentation and Discoverability

| Requirement | Description | `kaiser` | `kaiser-langgraph` | `kaiser-postgres` |
| :--- | :--- | :--- | :--- | :--- |
| 6.1 REQ Document | Component REQ document exists with purpose, tools, dependencies, credentials, volumes, ports | ✓ | ✓ | ✓ |
| 6.2 README.md | README exists with architecture, deployment, configuration, recovery procedures | ✓ | ✓ | ✓ |
| 6.3 Registry Entry | ALL containers have registry entries; MAD group shares UID; only gateway has port/mcp_endpoints | ✓ | ✓ | ✓ |
| 6.4 Directory Structure | MAD Group has parent folder in `mads/` containing subdirectories for each container's source code | ✓ | ✓ | ✓ |
| 6.5 Tool Documentation | Tools documented with descriptions, schemas, examples, error codes | N/A | ✓ | N/A |

***

## 7. Resilience, Safety, and Deployment

| Requirement | Description | `kaiser` | `kaiser-langgraph` | `kaiser-postgres` |
| :--- | :--- | :--- | :--- | :--- |
| 7.1 Graceful Degradation | External dependency failures cause degradation (not crash), health reports degraded status | ✓ | ✓ | N/A |
| 7.2 MAD Group Boundaries | Internal (hard) vs external (soft) dependencies clearly defined | ✓ | ✓ | ✓ |
| 7.3 Independent Container Startup | Container starts and becomes healthy without waiting for dependencies | ✓ | ✓ | ✓ |
| 7.4 Overlay Network DNS Usage | Uses container names for communication (never IP addresses) | ✓ | ✓ | ✓ |
| 7.5 Docker Compose Configuration | Service defined in master `docker-compose.yml`, build context is `.` (project root) | ✓ | ✓ | ✓ |
| 7.4.1 Per-MAD Private Networks | Gateway on joshua-net + [mad]-net; langgraph and backing services on [mad]-net only | ✓ | ✓ | ✓ |
| 7.6 Host Affinity Configuration | Host affinity via profiles in per-host override files (not Swarm placement constraints) | ✓ | ✓ | ✓ |
| 7.7 Git Safety Mechanisms | Git operations include backup, dry-run, rollback, user confirmation (if applicable) | N/A | N/A | N/A |
| 7.8 Conversation Data Integration | Writes to Rogers directly or via watcher (if applicable) | N/A | N/A | N/A |
| 7.9 Asynchronous Correctness | No blocking I/O (`time.sleep`) is used; all I/O is `async` and `await`ed | N/A | ✓ | N/A |
| 7.10 Input Validation | All data received from external sources is validated before use | N/A | ✓ | N/A |
| 7.11 Null/None Checking | Variables that can be `None` are explicitly checked before their attributes or methods are accessed | N/A | ✓ | N/A |

***

## 8. Exceptions and Special Cases

| Requirement | Description | `kaiser` | `kaiser-langgraph` | `kaiser-postgres` |
| :--- | :--- | :--- | :--- | :--- |
| 8.1 Exception Documentation | Non-compliant items documented in REQ-000-exception-registry with reason, impact, mitigation | ✓ | ✓ | ✓ |
| 8.2 Exception Approval | All exceptions approved by Joshua/Aristotle9, documented with approver and date | ✓ | ✓ | ✓ |

***

## N/A Justifications

| Requirement | Container | Reason | Approved By | Date |
|-------------|-------------|----------------------|-------------|------|
| 1.2, 1.5, 1.6 | All | No Node.js runtime, no Playwright binaries, pure Python environment. | | |
| 4.8 | kaiser | Gateway uses nginx directly for proxy routing (covered by EX-KAISER-004), no server.js logic exists. | | |
| 7.7, 7.8 | All | No Git operations or conversation memory watcher needed for Kaiser. | | |

***

## Exception Justifications

| Requirement | Container | Reason | Mitigation | Exception ID | Approved By | Date |
|-------------|-------------|-----------------------------|-------------------|--------------|-------------|------|
| 1.1 | kaiser-langgraph | Package Caching: Uses Alexandria dynamically at runtime for State 3 eMAD execution. | Network isolation preserved via proxy on irina. | EX-KAISER-001 | J | 2026-03-11 |
| 1.10 | kaiser-langgraph | Unit Testing Mandate deferred due to complex State 3 integration scope. | Validated empirically via Gate 3 end-to-end tests. | EX-KAISER-006 | J | 2026-03-11 |
| 2.1, 2.2, 2.3, 2.4 | kaiser-postgres | Native postgres image requires root for init, breaks with USER directive. | Isolated network, host-level directory permissions (must fix ✗). | EX-KAISER-003 | J | 2026-03-11 |
| 3.1 | kaiser-postgres | Native VOLUME directive cannot be suppressed without exact bind mount. | Data stored at dedicated host path on NVMe. | EX-KAISER-002 | J | 2026-03-11 |
| 4.5, 4.6 | kaiser | State 3 uses native nginx + FastMCP, bypassing State 1 template config.json routing. | Equivalent isolation and tool exposure achieved via FastMCP. | EX-KAISER-004 | J | 2026-03-11 |
| 5.2 | kaiser | nginx:alpine logs natively in plain text, not JSON. | JSON logging handled at FastMCP layer. | EX-KAISER-005 | J | 2026-03-11 |
| 5.2 | kaiser-postgres | postgres logs natively in plain text, not JSON. | Logs available via docker; deferred to aggregation. | EX-KAISER-007 | J | 2026-03-11 |

***

## Audit Summary

**Total Requirements:** 63 **Passed:** 48 **Failed:** 3 **N/A:** 12 **Exceptions:** 7

**Compliance Status:** Non-Compliant

**Blocker Issues:** 
- **1.7 Version Pinning:** `kaiser-langgraph/requirements.txt` contains `typing-extensions>=4.11`, which uses a loose constraint instead of an exact match (`==`).
- **2.6 Post-Deployment Permissions:** The database directory at `/mnt/nvme/workspace/kaiser/databases/postgres/data` is currently owned by UID 70 / group root with 700 permissions. The mitigation in EX-KAISER-002 mandates that this path must be owned by UID 2036 with 750 permissions applied.
- **5.5 MCP Request Logging:** `kaiser-langgraph` uses FastMCP and manual request logging (`_log_mcp()`) rather than the mandated `mcp-protocol-lib`. This State 3 architectural divergence requires a registered exception similar to EX-ALEXANDRIA-009, but no exception exists for Kaiser yet.

**Next Steps:** 
1. Update `requirements.txt` to strictly pin `typing-extensions`.
2. Execute a `chmod` and `chown` on the host directory for `kaiser-postgres` data to comply with EX-KAISER-002.
3. Submit an exception request to the user to document and formally approve the FastMCP manual logging pattern (EX-KAISER-008).

***

## Remediation Plan

**Objective:** Bring Kaiser into full REQ-000 compliance by addressing version pins, post-deployment permissions, and obtaining an exception for manual MCP logging.

| Requirement | Container | Action Required |
| :--- | :--- | :--- |
| 1.7 | kaiser-langgraph | Update `requirements.txt` to replace `typing-extensions>=4.11` with an exact version pin (`==`). |
| 2.6 | kaiser-postgres | Run `sudo chown -R 2036:2001 /mnt/nvme/workspace/kaiser/databases/postgres/data` and `sudo chmod 750 /mnt/nvme/workspace/kaiser/databases/postgres/data` on the M5 host. |
| 5.5 | kaiser-langgraph | Fill out the Exception Request Template for State 3 MCP Request Logging without `mcp-protocol-lib` and get it approved for the REQ-000-exception-registry. |
