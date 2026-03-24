**Reviewer:** gemini
**Gate:** 3
**MAD:** kaiser
**Date:** 2026-03-11

# REQ-000 Compliance Checklist: kaiser

**MAD Group:** kaiser **Audit Date:** 2026-03-11 **Auditor:** Gemini **Status:** Draft

***

## Instructions

(Instructions omitted for brevity, following standard REQ-000 structure)

***

## 1. Build System

| Requirement                     | Description                                                                                      | `kaiser` | `kaiser-langgraph` | `kaiser-postgres` |
|---------------------------------|--------------------------------------------------------------------------------------------------|-------|-------------|----------|
| 1.1 Python Package Caching      | All Python dependencies cached in `packages/`, pinned versions (`==`), offline build works       | N/A   | EX          | N/A      |
| 1.2 Node.js Package Caching     | All Node.js dependencies cached in `packages/`, exact versions (no `^`/`~`), offline build works | N/A   | N/A         | N/A      |
| 1.3 System Package Caching      | System packages (apt/apk) cached locally, offline build works                                    | N/A   | N/A         | ✓        |
| 1.4 Docker Base Image Caching   | Base image pinned to specific version (not `latest`), available locally                          | ✓     | ✓           | ✓        |
| 1.5 Runtime Binary Caching      | Runtime binaries (Playwright, etc.) cached locally, no runtime downloads                         | N/A   | N/A         | N/A      |
| 1.6 Hybrid Runtime Environments | Both Python and Node.js packages cached if both runtimes used                                    | N/A   | N/A         | N/A      |
| 1.7 Version Pinning             | All dependencies locked to specific versions (Docker, Python, Node.js)                           | ✓     | ✓           | ✓        |
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
| 2.4 umask Configuration          | umask 000 set (Node.js: `process.umask(0o000)`, Python: `os.umask(0o000)`, Supervisord: start.sh wrapper) | ✓       | ✓                 | N/A            |
| 2.5 File Ownership in Dockerfile | Uses `COPY --chown` instead of `chown -R`                                                                 | ✓       | ✓                 | N/A            |
| 2.6 Post-Deployment Permissions  | Database directories have correct permissions (750/640) applied on host after deployment                  | N/A     | N/A               | ✗              |

***

## 3. Storage and Data

| Requirement                         | Description                                                                                           | `kaiser` | `kaiser-langgraph` | `kaiser-postgres` |
|-------------------------------------|-------------------------------------------------------------------------------------------------------|---------|-------------------|----------------|
| 3.1 Two-Volume Mounting Policy      | Mounts exactly two volumes: `storage:/storage` and `workspace:/workspace`                             | ✓       | ✓                 | EX             |
| 3.2 Volume Mount Correctness        | Mounts root volumes (not subdirectories): `storage:/storage` NOT `storage:/storage/databases/[mad]`   | ✓       | ✓                 | ✓              |
| 3.3 Workspace Folder Organization   | Creates own workspace subdirectory `/workspace/[container-name]/`                                     | N/A     | N/A               | ✓              |
| 3.4 Storage vs Workspace Decision   | Credentials/backups in `/storage/`, databases in `/workspace/`                                        | N/A     | N/A               | ✓              |
| 3.5 Credentials Management          | Loads credentials from `/storage/credentials/[mad]/`, never hardcoded                                 | N/A     | N/A               | N/A            |
| 3.6 No Hardcoded Secrets            | No secrets in code, Dockerfiles, environment variables, or git                                        | ✓       | ✓                 | ✓              |
| 3.7 Database/State Storage Location | MAD databases in `/workspace/[mad]/databases/[tech]/`, backups in `/storage/backups/databases/[mad]/` | N/A     | N/A               | ✓              |

***

## 4. Communication and Integration

| Requirement                         | Description                                                                                                                                                                                              | `kaiser` | `kaiser-langgraph` | `kaiser-postgres` |
|-------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------|-------------------|----------------|
| 4.1 MCP Transport Protocol          | MCP uses HTTP/SSE transport (not WebSocket or stdio)                                                                                                                                                     | ✓       | ✓                 | N/A            |
| 4.2 MCP Endpoint Availability       | Exposes `/health` and `/mcp` endpoints accessible from joshua-net                                                                                                                                        | ✓       | ✓                 | N/A            |
| 4.3 Sam Relay Compatibility         | Registry entry exists, Sam can discover and relay tools                                                                                                                                                  | ✓       | N/A               | N/A            |
| 4.4 Tool Naming Convention          | Tools follow `[domain]_[action]` pattern                                                                                                                                                                 | N/A     | ✓                 | N/A            |
| 4.5 MCP Gateway Template Usage      | Gateway created from `mads/_template/template/` with standard libraries (mcp-protocol-lib, health-aggregator-lib, logging-lib, routing-lib). server.js unchanged from template (< 20 lines)              | N/A     | N/A               | N/A            |
| 4.6 Configuration File Requirements | Valid `config.json` with tools, dependencies, validates against schema; **tool definitions match the REQ document** | N/A     | N/A               | N/A            |
| 4.7 LangGraph Mandate               | All programmatic and cognitive logic is implemented using `StateGraph` (no Flask/FastAPI for primary app logic) | N/A     | ✓                 | N/A            |
| 4.8 Thin Gateway Mandate            | Gateway is a thin, config-driven router; `server.js` is minimal (<20 lines); logic is in `config.json` | ✓       | N/A               | N/A            |
| 4.9 LangGraph State Immutability    | Functions in graph nodes return new state dictionaries, and do not mutate the input state          | N/A     | ✓                 | N/A            |

***

## 5. Operations and Observability

| Requirement                   | Description                                                                       | `kaiser` | `kaiser-langgraph` | `kaiser-postgres` |
|-------------------------------|-----------------------------------------------------------------------------------|---------|-------------------|----------------|
| 5.1 Logging to stdout/stderr  | All logs to stdout/stderr, no log files inside containers                         | ✓       | ✓                 | ✓              |
| 5.2 Structured Logging Format | JSON format, one entry per line, consistent fields                                | ✓       | ✓                 | N/A            |
| 5.3 Health Check Endpoint     | HTTP `/health` endpoint returns 200 (healthy) or 503 (unhealthy)                  | ✓       | ✓                 | N/A            |
| 5.4 Dockerfile HEALTHCHECK    | Dockerfile includes HEALTHCHECK directive with appropriate `start_period`         | ✓       | ✓                 | ✓              |
| 5.5 MCP Request Logging       | MCP requests/responses automatically logged by mcp-protocol-lib                   | N/A     | N/A               | N/A            |
| 5.6 No File-Based Logging     | No `/var/log/` or `/app/logs/` directories for application logs                   | ✓       | ✓                 | ✓              |
| 5.7 Log Level Guidelines      | Supports DEBUG/INFO/WARN/ERROR levels, configurable at runtime                    | ✓       | ✓                 | ✓              |
| 5.8 Log Content Standards     | Logs appropriate info, excludes secrets/PII, health checks only log state changes | ✓       | ✓                 | ✓              |
| 5.9 Health Check Architecture | Docker HEALTHCHECK checks process only, `/health` endpoint checks dependencies    | ✓       | ✓                 | N/A            |
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
| 7.1 Graceful Degradation          | External dependency failures cause degradation (not crash), health reports degraded status | N/A     | ✓                 | N/A            |
| 7.2 MAD Group Boundaries          | Internal (hard) vs external (soft) dependencies clearly defined                            | ✓       | ✓                 | ✓              |
| 7.3 Independent Container Startup | Container starts and becomes healthy without waiting for dependencies                      | ✓       | ✓                 | ✓              |
| 7.4 Overlay Network DNS Usage     | Uses container names for communication (never IP addresses)                                | ✓       | ✓                 | N/A            |
| 7.5 Docker Compose Configuration  | Service defined in master `docker-compose.yml`, build context is `.` (project root)        | ✓       | ✓                 | ✓              |
| 7.4.1 Per-MAD Private Networks    | Gateway on joshua-net + [mad]-net; langgraph and backing services on [mad]-net only        | ✓       | ✓                 | ✓              |
| 7.6 Host Affinity Configuration   | Host affinity via profiles in per-host override files (not Swarm placement constraints)    | ✓       | ✓                 | ✓              |
| 7.7 Git Safety Mechanisms         | Git operations include backup, dry-run, rollback, user confirmation (if applicable)        | N/A     | N/A               | N/A            |
| 7.8 Conversation Data Integration | Writes to Rogers directly or via watcher (if applicable)                                   | N/A     | N/A               | N/A            |
| 7.9 Asynchronous Correctness      | No blocking I/O (`time.sleep`) is used; all I/O is `async` and `await`ed                         | N/A     | ✓                 | N/A            |
| 7.10 Input Validation             | All data received from external sources is validated before use                                  | N/A     | ✓                 | N/A            |
| 7.11 Null/None Checking           | Variables that can be `None` are explicitly checked before their attributes or methods are accessed | N/A     | ✓                 | N/A            |

***

## 8. Exceptions and Special Cases

| Requirement                 | Description                                                                     | `kaiser` | `kaiser-langgraph` | `kaiser-postgres` |
|-----------------------------|---------------------------------------------------------------------------------|---------|-------------------|----------------|
| 8.1 Exception Documentation | Non-compliant items documented in REQ-000-exception-registry with reason, impact, mitigation       | ✓       | ✓                 | ✓              |
| 8.2 Exception Approval      | All exceptions approved by Joshua/Aristotle9, documented with approver and date | N/A     | N/A               | N/A            |

***

## N/A Justifications

| Requirement | Container   | Reason               | Approved By | Date |
|-------------|-------------|----------------------|-------------|------|
| 1.1/1.3     | gateway, db | Not building python components, apk caching is used for DB. |             |      |
| 1.8/1.9     | gateway, db | Not python containers. |             |      |
| 2.4/2.5     | postgres    | Native postgres mechanisms. |             |      |
| 4.5/4.6/4.8 | langgraph, db | Standard gateway requirements don't apply to backend components. |             |      |

***

## Exception Justifications

| Requirement | Container   | Reason                      | Mitigation        | Exception ID | Approved By | Date |
|-------------|-------------|-----------------------------|-------------------|--------------|-------------|------|
| 1.1         | kaiser-langgraph | Needs to dynamically install python packages from Alexandria. | Pulls exclusively from internal Alexandria (offline). | EX-KAISER-001 |             |      |
| 3.1         | kaiser-postgres  | Official postgres image defines anonymous VOLUMEs requiring bind mounts | EX documented | EX-KAISER-002 |             |      |

***

## Audit Summary

**Total Requirements:** 72 (approx) **Passed:** 50 **Failed:** 3 **N/A:** 17 **Exceptions:** 2

**Compliance Status:** Non-Compliant

**Blocker Issues:**

1.  **1.10 Unit Testing Mandate:** `mads/kaiser/` has no unit tests. The testing requirement mandates pytest unit tests for all programmatic logic.
2.  **2.1 Root Usage / 2.2 Service Account:** `kaiser-postgres` runs as root (PID 1). There is no `USER postgres` (or `USER kaiser`) directive in the Dockerfile, and no exception has been documented for it.
3.  **2.6 Post-Deployment Permissions:** The postgres host path (`/mnt/nvme/workspace/kaiser/databases/postgres/data`) is owned by `70:0` with `700` permissions. It must be owned by `2036:2001` with `750` permissions per EX-KAISER-002 and REQ 2.6.
4.  **Tier 2 Integration Test Failure:** Testing the live system's MCP tools revealed that `kaiser_install_package("hopper-emad")` fails because `hopper-emad` is not published to Alexandria. This blocks testing of all subsequent eMAD lifecycle tools.

**Next Steps:** Implement missing unit tests. Correct the `kaiser-postgres` Dockerfile or document an exception if root PID 1 is explicitly desired for postgres init scripts. Correct the directory permissions on M5. Ensure `hopper-emad` is published to Alexandria so testing can complete.

***

## Remediation Plan

**Objective:** Bring Kaiser into full compliance with REQ-000 and enable complete State 3 Tier-2 testing.

| Requirement | Container | Action Required |
| :--- | :--- | :--- |
| 1.10 | kaiser-langgraph | Write and commit `pytest` unit tests for the FastMCP tool logic and LangGraph nodes. |
| 2.1 | kaiser-postgres | Refactor the Dockerfile to run as the dedicated kaiser service account or seek an explicit exception (like `EX-POSTGRES-001` if standard postgres container behavior is maintained). |
| 2.6 | Host Environment | Run `sudo chown -R 2036:2001 /mnt/nvme/workspace/kaiser/databases/postgres/data` and `sudo chmod 750` on the M5 host directory to satisfy EX-KAISER-002. |
| Tier 2 | System Ecosystem | Publish the `hopper-emad` package to Alexandria so `kaiser_install_package` can succeed during the Gate 3 live testing verification. |