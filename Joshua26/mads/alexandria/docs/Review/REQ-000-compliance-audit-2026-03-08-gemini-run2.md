**Reviewer:** Gemini
**Gate:** 3
**MAD:** alexandria
**Date:** 2026-03-08

# REQ-000 Compliance Checklist: Alexandria

**MAD Group:** alexandria **Audit Date:** 2026-03-08 **Auditor:** Gemini **Status:** Complete

***

## Instructions

**Location:** Create each audit file in `mads/[mad-name]/docs/Review/`. All gate outputs (reviews and audits) for a MAD live in that Review subfolder.

**Naming convention:** `REQ-000-compliance-audit-[YYYY-MM-DD].md`

**Cell Values:**
-   ✓ = Pass
-   ✗ = Fail
-   N/A = Not Applicable (requires justification below)
-   EX = Exception (requires justification below and REQ-000-exception-registry entry)

***

## 1. Build System

| Requirement                     | Description                                                                                      | `alexandria` | `langgraph` | `devpi` | `verdaccio` | `registry` |
|---------------------------------|--------------------------------------------------------------------------------------------------|--------------|-------------|---------|-------------|------------|
| 1.1 Python Package Caching      | All Python dependencies cached in `packages/`, pinned versions (`==`), offline build works       | N/A | N/A | N/A | N/A | N/A |
| 1.2 Node.js Package Caching     | All Node.js dependencies cached in `packages/`, exact versions (no `^`/`~`), offline build works | N/A | N/A | N/A | N/A | N/A |
| 1.3 System Package Caching      | System packages (apt/apk) cached locally, offline build works                                    | N/A | N/A | N/A | N/A | N/A |
| 1.4 Docker Base Image Caching   | Base image pinned to specific version (not `latest`), available locally                          | N/A | N/A | N/A | N/A | N/A |
| 1.5 Runtime Binary Caching      | Runtime binaries (Playwright, etc.) cached locally, no runtime downloads                         | N/A | N/A | N/A | N/A | N/A |
| 1.6 Hybrid Runtime Environments | Both Python and Node.js packages cached if both runtimes used                                    | N/A | N/A | N/A | N/A | N/A |
| 1.7 Version Pinning             | All dependencies locked to specific versions (Docker, Python, Node.js)                           | N/A | N/A | N/A | N/A | N/A |
| 1.8 Code Formatting (Python)    | Code passes `black --check .`                                                                    | N/A | N/A | N/A | N/A | N/A |
| 1.9 Code Linting (Python)       | Code passes `ruff check .`                                                                       | N/A | N/A | N/A | N/A | N/A |
| 1.10 Unit Testing Mandate       | All new programmatic logic is accompanied by `pytest` unit tests for the happy path and error conditions | N/A | N/A | N/A | N/A | N/A |

***

## 2. Runtime Security and Permissions

| Requirement                      | Description                                                                                               | `alexandria` | `langgraph` | `devpi` | `verdaccio` | `registry` |
|----------------------------------|-----------------------------------------------------------------------------------------------------------|--------------|-------------|---------|-------------|------------|
| 2.1 Root Usage Pattern           | Root used ONLY for packages and user creation, USER directive follows immediately                         | N/A          | N/A         | N/A     | EX          | EX         |
| 2.2 Service Account Creation     | Runs as dedicated service account with UID from registry.yml                                              | ✓            | ✓           | ✓       | EX          | EX         |
| 2.3 Group Membership             | GID 2001 (administrators) for all containers                                                              | ✓            | ✓           | ✓       | EX          | EX         |
| 2.4 umask Configuration          | umask 000 set (Node.js: `process.umask(0o000)`, Python: `os.umask(0o000)`, Supervisord: start.sh wrapper) | ✗            | ✗           | ✗       | EX          | EX         |
| 2.5 File Ownership in Dockerfile | Uses `COPY --chown` instead of `chown -R`                                                                 | N/A          | N/A         | N/A     | N/A         | N/A        |
| 2.6 Post-Deployment Permissions  | Database directories have correct permissions (750/640) applied on host after deployment                  | N/A          | N/A         | N/A     | N/A         | N/A        |

***

## 3. Storage and Data

| Requirement                         | Description                                                                                           | `alexandria` | `langgraph` | `devpi` | `verdaccio` | `registry` |
|-------------------------------------|-------------------------------------------------------------------------------------------------------|--------------|-------------|---------|-------------|------------|
| 3.1 Two-Volume Mounting Policy      | Mounts exactly two volumes: `storage:/storage` and `workspace:/workspace`                             | ✓            | ✓           | ✓       | EX          | EX         |
| 3.2 Volume Mount Correctness        | Mounts root volumes (not subdirectories): `storage:/storage` NOT `storage:/storage/databases/[mad]`   | ✓            | ✓           | ✓       | EX          | EX         |
| 3.3 Workspace Folder Organization   | Creates own workspace subdirectory `/workspace/[container-name]/`                                     | N/A          | ✓           | N/A     | N/A         | N/A        |
| 3.4 Storage vs Workspace Decision   | Credentials/backups in `/storage/`, databases in `/workspace/`                                        | N/A          | ✓           | N/A     | N/A         | N/A        |
| 3.5 Credentials Management          | Loads credentials from `/storage/credentials/[mad]/`, never hardcoded                                 | N/A          | N/A         | N/A     | N/A         | N/A        |
| 3.6 No Hardcoded Secrets            | No secrets in code, Dockerfiles, environment variables, or git                                        | N/A          | N/A         | N/A     | N/A         | N/A        |
| 3.7 Database/State Storage Location | MAD databases in `/workspace/[mad]/databases/[tech]/`, backups in `/storage/backups/databases/[mad]/` | N/A          | N/A         | N/A     | N/A         | N/A        |

***

## 4. Communication and Integration

| Requirement                         | Description                                                                                                                                                                                              | `alexandria` | `langgraph` | `devpi` | `verdaccio` | `registry` |
|-------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------|-------------|---------|-------------|------------|
| 4.1 MCP Transport Protocol          | MCP uses HTTP/SSE transport (not WebSocket or stdio)                                                                                                                                                     | ✓            | ✓           | N/A     | N/A         | N/A        |
| 4.2 MCP Endpoint Availability       | Exposes `/health` and `/mcp` endpoints accessible from joshua-net                                                                                                                                        | ✗            | ✓           | N/A     | N/A         | N/A        |
| 4.3 Sam Relay Compatibility         | Registry entry exists, Sam can discover and relay tools                                                                                                                                                  | ✓            | N/A         | N/A     | N/A         | N/A        |
| 4.4 Tool Naming Convention          | Tools follow `[domain]_[action]` pattern                                                                                                                                                                 | N/A          | N/A         | N/A     | N/A         | N/A        |
| 4.5 MCP Gateway Template Usage      | Gateway created from `mads/_template/template/` with standard libraries (mcp-protocol-lib, health-aggregator-lib, logging-lib, routing-lib). server.js unchanged from template (< 20 lines)              | N/A          | N/A         | N/A     | N/A         | N/A        |
| 4.6 Configuration File Requirements | Valid `config.json` with tools, dependencies, validates against schema; **tool definitions match the REQ document** | N/A          | N/A         | N/A     | N/A         | N/A        |
| 4.7 LangGraph Mandate               | All programmatic and cognitive logic is implemented using `StateGraph` (no Flask/FastAPI for primary app logic) | N/A          | N/A         | N/A     | N/A         | N/A        |
| 4.8 Thin Gateway Mandate            | Gateway is a thin, config-driven router; `server.js` is minimal (<20 lines); logic is in `config.json` | N/A          | N/A         | N/A     | N/A         | N/A        |
| 4.9 LangGraph State Immutability    | Functions in graph nodes return new state dictionaries, and do not mutate the input state          | N/A          | N/A         | N/A     | N/A         | N/A        |

***

## 5. Operations and Observability

| Requirement                   | Description                                                                       | `alexandria` | `langgraph` | `devpi` | `verdaccio` | `registry` |
|-------------------------------|-----------------------------------------------------------------------------------|--------------|-------------|---------|-------------|------------|
| 5.1 Logging to stdout/stderr  | All logs to stdout/stderr, no log files inside containers                         | ✓            | ✓           | ✓       | ✓           | ✓          |
| 5.2 Structured Logging Format | JSON format, one entry per line, consistent fields                                | EX           | ✓           | ✓       | EX          | EX         |
| 5.3 Health Check Endpoint     | HTTP `/health` endpoint returns 200 (healthy) or 503 (unhealthy)                  | ✗            | ✓           | N/A     | N/A         | N/A        |
| 5.4 Dockerfile HEALTHCHECK    | Dockerfile includes HEALTHCHECK directive with appropriate `start_period`         | N/A          | N/A         | N/A     | N/A         | N/A        |
| 5.5 MCP Request Logging       | MCP requests/responses automatically logged by mcp-protocol-lib                   | N/A          | N/A         | N/A     | N/A         | N/A        |
| 5.6 No File-Based Logging     | No `/var/log/` or `/app/logs/` directories for application logs                   | ✓            | ✓           | ✓       | ✓           | ✓          |
| 5.7 Log Level Guidelines      | Supports DEBUG/INFO/WARN/ERROR levels, configurable at runtime                    | N/A          | N/A         | N/A     | N/A         | N/A        |
| 5.8 Log Content Standards     | Logs appropriate info, excludes secrets/PII, health checks only log state changes | N/A          | N/A         | N/A     | N/A         | N/A        |
| 5.9 Health Check Architecture | Docker HEALTHCHECK checks process only, `/health` endpoint checks dependencies    | N/A          | N/A         | N/A     | N/A         | N/A        |
| 5.10 Specific Exception Handling| Does not use blanket `except Exception:` or `except:`                                              | N/A          | N/A         | N/A     | N/A         | N/A        |
| 5.11 Resource Management        | All external resources (e.g., file handles, DB connections) are reliably closed using `with` or `finally` | N/A          | N/A         | N/A     | N/A         | N/A        |
| 5.12 Error Context              | All logged errors and raised exceptions include sufficient context for debugging                 | N/A          | N/A         | N/A     | N/A         | N/A        |

***

## 6. Documentation and Discoverability

| Requirement             | Description                                                                                     | `alexandria` | `langgraph` | `devpi` | `verdaccio` | `registry` |
|-------------------------|-------------------------------------------------------------------------------------------------|--------------|-------------|---------|-------------|------------|
| 6.1 REQ Document        | Component REQ document exists with purpose, tools, dependencies, credentials, volumes, ports    | ✓            | ✓           | ✓       | ✓           | ✓          |
| 6.2 README.md           | README exists with architecture, deployment, configuration, recovery procedures                 | N/A          | N/A         | N/A     | N/A         | N/A        |
| 6.3 Registry Entry      | ALL containers have registry entries; MAD group shares UID; only gateway has port/mcp_endpoints | ✓            | ✓           | ✓       | ✓           | ✓          |
| 6.4 Directory Structure | MAD Group has parent folder in `mads/` containing subdirectories for each container's source code | ✓            | ✓           | ✓       | ✓           | ✓          |
| 6.5 Tool Documentation  | Tools documented with descriptions, schemas, examples, error codes                              | N/A          | N/A         | N/A     | N/A         | N/A        |

***

## 7. Resilience, Safety, and Deployment

| Requirement                       | Description                                                                                | `alexandria` | `langgraph` | `devpi` | `verdaccio` | `registry` |
|-----------------------------------|--------------------------------------------------------------------------------------------|--------------|-------------|---------|-------------|------------|
| 7.1 Graceful Degradation          | External dependency failures cause degradation (not crash), health reports degraded status | N/A          | N/A         | N/A     | N/A         | N/A        |
| 7.2 MAD Group Boundaries          | Internal (hard) vs external (soft) dependencies clearly defined                            | ✓            | ✓           | ✓       | ✓           | ✓          |
| 7.3 Independent Container Startup | Container starts and becomes healthy without waiting for dependencies                      | ✓            | ✓           | ✓       | ✓           | ✓          |
| 7.4 Overlay Network DNS Usage     | Uses container names for communication (never IP addresses)                                | N/A          | N/A         | N/A     | N/A         | N/A        |
| 7.5 Docker Compose Configuration  | Service defined in master `docker-compose.yml`, build context is `.` (project root)        | N/A          | N/A         | N/A     | N/A         | N/A        |
| 7.4.1 Per-MAD Private Networks    | Gateway on joshua-net + [mad]-net; langgraph and backing services on [mad]-net only        | ✗            | ✓           | ✗       | ✗           | ✗          |
| 7.6 Host Affinity Configuration   | Host affinity via profiles in per-host override files (not Swarm placement constraints)    | N/A          | N/A         | N/A     | N/A         | N/A        |
| 7.7 Git Safety Mechanisms         | Git operations include backup, dry-run, rollback, user confirmation (if applicable)        | N/A          | N/A         | N/A     | N/A         | N/A        |
| 7.8 Conversation Data Integration | Writes to Rogers directly or via watcher (if applicable)                                   | N/A          | N/A         | N/A     | N/A         | N/A        |
| 7.9 Asynchronous Correctness      | No blocking I/O (`time.sleep`) is used; all I/O is `async` and `await`ed                   | N/A          | N/A         | N/A     | N/A         | N/A        |
| 7.10 Input Validation             | All data received from external sources is validated before use                            | N/A          | N/A         | N/A     | N/A         | N/A        |
| 7.11 Null/None Checking           | Variables that can be `None` are explicitly checked before their attributes or methods are accessed | N/A          | N/A         | N/A     | N/A         | N/A        |

***

## 8. Exceptions and Special Cases

| Requirement                 | Description                                                                     | `alexandria` | `langgraph` | `devpi` | `verdaccio` | `registry` |
|-----------------------------|---------------------------------------------------------------------------------|--------------|-------------|---------|-------------|------------|
| 8.1 Exception Documentation | Non-compliant items documented in REQ-000-exception-registry with reason, impact, mitigation       | ✓            | ✓           | ✓       | ✓           | ✓          |
| 8.2 Exception Approval      | All exceptions approved by Joshua/Aristotle9, documented with approver and date | ✓            | ✓           | ✓       | ✓           | ✓          |

***

## N/A Justifications

| Requirement | Container   | Reason               | Approved By | Date |
|-------------|-------------|----------------------|-------------|------|
| 1.x, 2.1, 2.5, 3.6, 4.4-4.9, 5.4-5.12, 6.2, 6.5, 7.x (Code-level) | All | Gate 3 is a live post-deployment audit. Build-time, repository structure, and code-level logic requirements are verified during Gate 2 and cannot be dynamically inspected on the live production containers. | Auto-applied | 2026-03-08 |

***

## Exception Justifications

| Requirement | Container   | Reason                      | Mitigation        | Exception ID | Approved By | Date |
|-------------|-------------|-----------------------------|-------------------|--------------|-------------|------|
| 2.2, 2.3, 2.4 | `verdaccio` | Official verdaccio/verdaccio image | Deployed per official docs | EX-ALEXANDRIA-002 | Joshua | 2026-03-08 |
| 2.2, 2.3, 2.4 | `registry`  | Official registry:2 image | Deployed per official docs | EX-ALEXANDRIA-003 | Joshua | 2026-03-08 |
| 3.1, 3.2    | `verdaccio` | Official volume requires host bind mount | Bind mounts allowed for official services | EX-ALEXANDRIA-004 | Joshua | 2026-03-08 |
| 3.1, 3.2    | `registry`  | Official volume requires host bind mount | Bind mounts allowed for official services | EX-ALEXANDRIA-005 | Joshua | 2026-03-08 |
| 5.2         | `verdaccio` | Verdaccio native log format | - | EX-ALEXANDRIA-006 | Joshua | 2026-03-08 |
| 5.2         | `registry`  | Registry 2.0 Go-style logs | - | EX-ALEXANDRIA-007 | Joshua | 2026-03-08 |
| 5.2         | `alexandria` | nginx:alpine plain text error_log | - | EX-ALEXANDRIA-008 | Joshua | 2026-03-08 |

***

## Audit Summary

**Total Requirements:** 55 **Passed:** 15 **Failed:** 3 **N/A:** 37 **Exceptions:** 7
*(Note: Total requirements counts vary due to N/A items for Gate 3.)*

**Compliance Status:** Non-Compliant

**Blocker Issues:** 
- **✗ 4.2 / 5.3 (Missing Port Bindings):** The `alexandria` container is not binding the required MCP port (9229) to the host. `/health` and `/mcp` endpoints are completely inaccessible.
- **✗ 7.4.1 (Network Bypass):** Backing service containers (`devpi`, `verdaccio`, `registry`) are mapping ports directly to the host (`0.0.0.0:3141`, `4873`, `5000`). This completely bypasses the gateway, violating the REQ rule that the nginx gateway is the sole network boundary and backing services must only exist on `alexandria-net`.
- **✗ 2.4 (umask Violation):** Live inspection reveals `alexandria-langgraph`, `alexandria-devpi`, and `alexandria` are running with umask `0o22` / `0022` instead of the mandated `0o000` (`umask 000`).

**Next Steps:** Implement the remediation plan to address network proxy mappings and umask failures.

***

## Remediation Plan

**Objective:** Correct the severe network routing issues to enforce the nginx gateway boundary and apply the correct file permission mask.

| Requirement | Container | Action Required |
| :--- | :--- | :--- |
| 7.4.1 | `devpi`, `verdaccio`, `registry` | Remove port mappings (`3141:3141`, `4873:4873`, `5000:5000`) from the backing services in `docker-compose.yml`. |
| 7.4.1 / 4.2 | `alexandria` (nginx) | Add the host port mappings for MCP (`9229:9229`) and all proxied caches (`3141:3141`, `4873:4873`, `5000:5000`) to the `alexandria` service in `docker-compose.yml`. |
| 2.4 | `langgraph`, `devpi` | Update the Python entrypoints to ensure `os.umask(0o000)` is correctly evaluated before starting the application. |
| 2.4 | `alexandria` | Fix `start.sh` wrapper to guarantee `umask 000` persists into the `exec nginx` context. |