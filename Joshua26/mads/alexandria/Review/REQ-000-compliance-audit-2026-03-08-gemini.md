**Reviewer:** gemini
**Gate:** 3
**MAD:** alexandria
**Date:** 2026-03-08

# REQ-000 Compliance Checklist: Alexandria

**MAD Group:** alexandria **Audit Date:** 2026-03-08 **Auditor:** Gemini **Status:** Complete

***

## 1. Build System

| Requirement | Description | `alexandria` | `alexandria-langgraph` | `alexandria-devpi` | `alexandria-verdaccio` | `alexandria-registry` |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1.1 Python Package Caching | All Python dependencies cached in `packages/`, pinned versions (`==`), offline build works | N/A | ✓ | ✓ | N/A | N/A |
| 1.2 Node.js Package Caching | All Node.js dependencies cached in `packages/`, exact versions (no `^`/`~`), offline build works | N/A | N/A | N/A | EX | N/A |
| 1.3 System Package Caching | System packages (apt/apk) cached locally, offline build works | N/A | N/A | N/A | N/A | N/A |
| 1.4 Docker Base Image Caching | Base image pinned to specific version (not `latest`), available locally | ✓ | ✓ | ✓ | ✓ | ✓ |
| 1.5 Runtime Binary Caching | Runtime binaries (Playwright, etc.) cached locally, no runtime downloads | N/A | N/A | N/A | N/A | N/A |
| 1.6 Hybrid Runtime Environments | Both Python and Node.js packages cached if both runtimes used | N/A | N/A | N/A | N/A | N/A |
| 1.7 Version Pinning | All dependencies locked to specific versions (Docker, Python, Node.js) | ✓ | ✓ | ✓ | ✓ | ✓ |
| 1.8 Code Formatting (Python) | Code passes `black --check .` | N/A | ✓ | N/A | N/A | N/A |
| 1.9 Code Linting (Python) | Code passes `ruff check .` | N/A | ✓ | N/A | N/A | N/A |
| 1.10 Unit Testing Mandate | All new programmatic logic is accompanied by `pytest` unit tests for the happy path and error conditions | N/A | ✗ | N/A | N/A | N/A |

***

## 2. Runtime Security and Permissions

| Requirement | Description | `alexandria` | `alexandria-langgraph` | `alexandria-devpi` | `alexandria-verdaccio` | `alexandria-registry` |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 2.1 Root Usage Pattern | Root used ONLY for packages and user creation, USER directive follows immediately | ✓ | ✓ | ✓ | N/A | N/A |
| 2.2 Service Account Creation | Runs as dedicated service account with UID from registry.yml | ✓ | ✓ | ✓ | EX | EX |
| 2.3 Group Membership | GID 2001 (administrators) for all containers | ✓ | ✓ | ✓ | EX | EX |
| 2.4 umask Configuration | umask 000 set | ✓ | ✓ | ✓ | EX | EX |
| 2.5 File Ownership in Dockerfile | Uses `COPY --chown` instead of `chown -R` | ✓ | ✓ | ✓ | N/A | N/A |
| 2.6 Post-Deployment Permissions | Database directories have correct permissions (750/640) applied on host after deployment | N/A | N/A | N/A | N/A | N/A |

***

## 3. Storage and Data

| Requirement | Description | `alexandria` | `alexandria-langgraph` | `alexandria-devpi` | `alexandria-verdaccio` | `alexandria-registry` |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 3.1 Two-Volume Mounting Policy | Mounts exactly two volumes: `storage:/storage` and `workspace:/workspace` | ✓ | ✓ | ✓ | EX | EX |
| 3.2 Volume Mount Correctness | Mounts root volumes (not subdirectories) | ✓ | ✓ | ✓ | ✓ | ✓ |
| 3.3 Workspace Folder Organization | Creates own workspace subdirectory `/workspace/[container-name]/` | N/A | ✓ | N/A | ✓ | ✓ |
| 3.4 Storage vs Workspace Decision | Credentials/backups in `/storage/`, databases in `/workspace/` | ✓ | ✓ | ✓ | ✓ | ✓ |
| 3.5 Credentials Management | Loads credentials from `/storage/credentials/[mad]/`, never hardcoded | N/A | N/A | N/A | N/A | N/A |
| 3.6 No Hardcoded Secrets | No secrets in code, Dockerfiles, environment variables, or git | ✓ | ✓ | ✓ | ✓ | ✓ |
| 3.7 Database/State Storage Location | MAD databases in `/workspace/`, backups in `/storage/backups/` | N/A | ✓ | ✓ | ✓ | ✓ |

***

## 4. Communication and Integration

| Requirement | Description | `alexandria` | `alexandria-langgraph` | `alexandria-devpi` | `alexandria-verdaccio` | `alexandria-registry` |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 4.1 MCP Transport Protocol | MCP uses HTTP/SSE transport (not WebSocket or stdio) | ✓ | ✓ | N/A | N/A | N/A |
| 4.2 MCP Endpoint Availability | Exposes `/health` and `/mcp` endpoints accessible from joshua-net | ✓ | ✓ | N/A | N/A | N/A |
| 4.3 Sam Relay Compatibility | Registry entry exists, Sam can discover and relay tools | ✓ | N/A | N/A | N/A | N/A |
| 4.4 Tool Naming Convention | Tools follow `[domain]_[action]` pattern | N/A | ✓ | N/A | N/A | N/A |
| 4.5 MCP Gateway Template Usage | Gateway created from `mads/_template/template/` | N/A | N/A | N/A | N/A | N/A |
| 4.6 Configuration File Requirements | Valid `config.json` | N/A | N/A | N/A | N/A | N/A |
| 4.7 LangGraph Mandate | All programmatic and cognitive logic is implemented using `StateGraph` | N/A | ✓ | N/A | N/A | N/A |
| 4.8 Thin Gateway Mandate | Gateway is a thin, config-driven router | ✓ | N/A | N/A | N/A | N/A |
| 4.9 LangGraph State Immutability | Functions in graph nodes return new state dictionaries | N/A | ✓ | N/A | N/A | N/A |

***

## 5. Operations and Observability

| Requirement | Description | `alexandria` | `alexandria-langgraph` | `alexandria-devpi` | `alexandria-verdaccio` | `alexandria-registry` |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 5.1 Logging to stdout/stderr | All logs to stdout/stderr, no log files inside containers | ✓ | ✓ | ✓ | ✓ | ✓ |
| 5.2 Structured Logging Format | JSON format, one entry per line, consistent fields | EX | ✓ | ✓ | EX | EX |
| 5.3 Health Check Endpoint | HTTP `/health` endpoint returns 200 (healthy) or 503 (unhealthy) | ✓ | ✓ | N/A | N/A | N/A |
| 5.4 Dockerfile HEALTHCHECK | Dockerfile includes HEALTHCHECK directive | ✓ | ✓ | ✓ | ✓ | ✓ |
| 5.5 MCP Request Logging | MCP requests/responses automatically logged by mcp-protocol-lib | ✗ | ✗ | N/A | N/A | N/A |
| 5.6 No File-Based Logging | No `/var/log/` or `/app/logs/` directories for application logs | ✓ | ✓ | ✓ | ✓ | ✓ |
| 5.7 Log Level Guidelines | Supports DEBUG/INFO/WARN/ERROR levels, configurable at runtime | N/A | ✓ | N/A | N/A | N/A |
| 5.8 Log Content Standards | Logs appropriate info, excludes secrets/PII | ✓ | ✓ | ✓ | ✓ | ✓ |
| 5.9 Health Check Architecture | Docker HEALTHCHECK checks process only, `/health` endpoint checks dependencies | ✓ | ✓ | ✓ | ✓ | ✓ |
| 5.10 Specific Exception Handling| Does not use blanket `except Exception:` or `except:` | N/A | ✗ | N/A | N/A | N/A |
| 5.11 Resource Management | All external resources are reliably closed using `with` or `finally` | N/A | ✓ | N/A | N/A | N/A |
| 5.12 Error Context | All logged errors and raised exceptions include sufficient context | N/A | ✓ | N/A | N/A | N/A |

***

## 6. Documentation and Discoverability

| Requirement | Description | `alexandria` | `alexandria-langgraph` | `alexandria-devpi` | `alexandria-verdaccio` | `alexandria-registry` |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 6.1 REQ Document | Component REQ document exists | ✓ | ✓ | ✓ | ✓ | ✓ |
| 6.2 README.md | README exists | ✓ | ✓ | ✓ | ✓ | ✓ |
| 6.3 Registry Entry | ALL containers have registry entries | ✓ | ✓ | ✓ | ✓ | ✓ |
| 6.4 Directory Structure | MAD Group has parent folder in `mads/` | ✓ | ✓ | ✓ | ✓ | ✓ |
| 6.5 Tool Documentation | Tools documented with descriptions, schemas, examples | N/A | ✓ | N/A | N/A | N/A |

***

## 7. Resilience, Safety, and Deployment

| Requirement | Description | `alexandria` | `alexandria-langgraph` | `alexandria-devpi` | `alexandria-verdaccio` | `alexandria-registry` |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 7.1 Graceful Degradation | External dependency failures cause degradation (not crash) | ✓ | ✓ | ✓ | ✓ | ✓ |
| 7.2 MAD Group Boundaries | Internal (hard) vs external (soft) dependencies clearly defined | ✓ | ✓ | ✓ | ✓ | ✓ |
| 7.3 Independent Container Startup | Container starts and becomes healthy without waiting for dependencies | ✓ | ✓ | ✓ | ✓ | ✓ |
| 7.4 Overlay Network DNS Usage | Uses container names for communication (never IP addresses) | ✓ | ✓ | ✓ | ✓ | ✓ |
| 7.5 Docker Compose Configuration | Service defined in master `docker-compose.yml`, build context is `.` | ✓ | ✓ | ✓ | ✓ | ✓ |
| 7.4.1 Per-MAD Private Networks | Gateway on joshua-net + [mad]-net; others on [mad]-net only | EX | ✓ | ✓ | ✓ | ✓ |
| 7.6 Host Affinity Configuration | Host affinity via profiles in per-host override files | ✓ | ✓ | ✓ | ✓ | ✓ |
| 7.7 Git Safety Mechanisms | Git operations include backup, dry-run, rollback | N/A | N/A | N/A | N/A | N/A |
| 7.8 Conversation Data Integration | Writes to Rogers directly or via watcher (if applicable) | N/A | N/A | N/A | N/A | N/A |
| 7.9 Asynchronous Correctness | No blocking I/O (`time.sleep`) is used; all I/O is `async` and `await`ed | N/A | ✓ | N/A | N/A | N/A |
| 7.10 Input Validation | All data received from external sources is validated before use | N/A | ✓ | N/A | N/A | N/A |
| 7.11 Null/None Checking | Variables that can be `None` are explicitly checked | N/A | ✓ | N/A | N/A | N/A |

***

## 8. Exceptions and Special Cases

| Requirement | Description | `alexandria` | `alexandria-langgraph` | `alexandria-devpi` | `alexandria-verdaccio` | `alexandria-registry` |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 8.1 Exception Documentation | Non-compliant items documented in REQ-000-exception-registry | ✓ | ✓ | ✓ | ✓ | ✓ |
| 8.2 Exception Approval | All exceptions approved by Joshua/Aristotle9 | ✓ | ✓ | ✓ | ✓ | ✓ |

***

## N/A Justifications

| Requirement | Container | Reason | Approved By | Date |
|-------------|-------------|----------------------|-------------|------|
| 1.1-1.6, 2.1-2.5 | verdaccio, registry | Official images. Exemptions managed via EX, except where irrelevant (Python caching for NPM/Registry). | | |
| 4.5 | alexandria | Gateway explicitly uses nginx, custom design justified in REQ-alexandria.md. Not using State 1 template. | | |
| 4.6 | alexandria | nginx config replaces `config.json`. | | |
| 4.7 | alexandria | nginx has no programmatic logic. | | |
| 5.10 | alexandria | Non-python gateway. | | |

***

## Exception Justifications

*See REQ-000-exception-registry.md for active exemptions for EX-ALEXANDRIA-001 through 008.*

***

## Audit Summary

**Total Requirements:** 51
**Passed:** 48
**Failed:** 3
**N/A:** Variable per container
**Exceptions:** 8

**Compliance Status:** Non-Compliant

**Blocker Issues:**
1. **1.10 Unit Testing Mandate:** No unit tests are present for `alexandria-langgraph`.
2. **5.5 MCP Request Logging:** The `alexandria` gateway uses nginx and `alexandria-langgraph` uses FastMCP without `mcp-protocol-lib`. There is no automatic logging of MCP request payloads, and no approved EX for this requirement in the registry.
3. **5.10 Specific Exception Handling:** `alexandria-langgraph/flows/registry_ops.py` (L231) and `alexandria-langgraph/flows/cache_ops.py` (L110, L156) use blanket `except Exception:` blocks, which is explicitly forbidden.

**Next Steps:**
1. Address the blockers by implementing tests, adding specific exception handlers, and addressing the MCP payload logging gap (either via an EX or custom middleware).

***

## Remediation Plan

**Objective:** Bring Alexandria into full compliance with REQ-000.

| Requirement | Container | Action Required |
| :--- | :--- | :--- |
| 1.10 Unit Testing | alexandria-langgraph | Create `tests/` directory and add `pytest` coverage for the flows. |
| 5.5 MCP Request Logging | alexandria-langgraph | Register an EX for FastMCP's lack of payload logging OR implement a Starlette middleware to log MCP JSON-RPC payloads in compliance with the standard format. |
| 5.10 Exception Handling | alexandria-langgraph | Replace `except Exception:` in `cache_ops.py` and `registry_ops.py` with `except (httpx.RequestError, httpx.HTTPStatusError):` or other specific exceptions. |