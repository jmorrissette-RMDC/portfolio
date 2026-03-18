**Reviewer:** gemini
**Gate:** 3
**MAD:** kaiser
**Date:** 2026-03-11

# REQ-000 Compliance Checklist: kaiser

**MAD Group:** kaiser **Audit Date:** 2026-03-11 **Auditor:** Gemini **Status:** Complete

***

## Instructions

**Location:** Create each audit file in `mads/[mad-name]/docs/Review/`. All gate outputs (reviews and audits) for a MAD live in that Review subfolder.

**Naming convention:** `REQ-000-compliance-audit-[YYYY-MM-DD].md`

Example: `REQ-000-compliance-audit-2026-02-28.md`

For multiple runs the same day, append `-run2`, `-run3`, or `-v2`, `-v3`.

**Dated snapshots — do not update in place:** Each audit run produces a new file. If the audit finds failures and you fix them, run the audit again and create a *new* dated file. Never modify a previous audit file. This preserves traceability: you can see what was found in each run and how compliance improved.

**Cell Values:**

-   ✓ = Pass
-   ✗ = Fail
-   N/A = Not Applicable (requires justification below)
-   EX = Exception (requires justification below and REQ-000-exception-registry entry)

**Date Format:** Mark with date below symbol (e.g., `✓ 2026-01-31`)

**Containers or Libraries:** Add columns for each backing service container or library in your MAD group

Fully inspected positive affirmation must be made for a passing mark. Nothing may be skipped.

If you feel that something does not apply, NA mark must be approved.

If something requires an exception, EX marks must be approved. Only after approval should it be recorded in REQ-000-exception-registry

The user is the approver for all NA and EX marks. Fill out the request at the bottom and then seek approval.

Do not update a previous audit file. Fix issues, then create a new dated audit file for the re-run.

***

## 1. Build System

| Requirement                     | Description                                                                                      | `kaiser` | `kaiser-langgraph` | `kaiser-postgres` |
|---------------------------------|--------------------------------------------------------------------------------------------------|-------|-------------|----------|
| 1.1 Python Package Caching      | All Python dependencies cached in `packages/`, pinned versions (`==`), offline build works       | N/A <br> 2026-03-11 | EX <br> 2026-03-11 | N/A <br> 2026-03-11 |
| 1.2 Node.js Package Caching     | All Node.js dependencies cached in `packages/`, exact versions (no `^`/`~`), offline build works | N/A <br> 2026-03-11 | N/A <br> 2026-03-11 | N/A <br> 2026-03-11 |
| 1.3 System Package Caching      | System packages (apt/apk) cached locally, offline build works                                    | N/A <br> 2026-03-11 | N/A <br> 2026-03-11 | ✓ <br> 2026-03-11 |
| 1.4 Docker Base Image Caching   | Base image pinned to specific version (not `latest`), available locally                          | ✓ <br> 2026-03-11 | ✓ <br> 2026-03-11 | ✓ <br> 2026-03-11 |
| 1.5 Runtime Binary Caching      | Runtime binaries (Playwright, etc.) cached locally, no runtime downloads                         | N/A <br> 2026-03-11 | N/A <br> 2026-03-11 | N/A <br> 2026-03-11 |
| 1.6 Hybrid Runtime Environments | Both Python and Node.js packages cached if both runtimes used                                    | N/A <br> 2026-03-11 | N/A <br> 2026-03-11 | N/A <br> 2026-03-11 |
| 1.7 Version Pinning             | All dependencies locked to specific versions (Docker, Python, Node.js)                           | ✓ <br> 2026-03-11 | ✓ <br> 2026-03-11 | ✓ <br> 2026-03-11 |
| 1.8 Code Formatting (Python)    | Code passes `black --check .`                                                                    | N/A <br> 2026-03-11 | ✓ <br> 2026-03-11 | N/A <br> 2026-03-11 |
| 1.9 Code Linting (Python)       | Code passes `ruff check .`                                                                       | N/A <br> 2026-03-11 | ✓ <br> 2026-03-11 | N/A <br> 2026-03-11 |
| 1.10 Unit Testing Mandate       | All new programmatic logic is accompanied by `pytest` unit tests for the happy path and error conditions | N/A <br> 2026-03-11 | EX <br> 2026-03-11 | N/A <br> 2026-03-11 |

***

## 2. Runtime Security and Permissions

| Requirement                      | Description                                                                                               | `kaiser` | `kaiser-langgraph` | `kaiser-postgres` |
|----------------------------------|-----------------------------------------------------------------------------------------------------------|---------|-------------------|----------------|
| 2.1 Root Usage Pattern           | Root used ONLY for packages and user creation, USER directive follows immediately                         | ✓ <br> 2026-03-11 | ✓ <br> 2026-03-11 | EX <br> 2026-03-11 |
| 2.2 Service Account Creation     | Runs as dedicated service account with UID from registry.yml                                              | ✓ <br> 2026-03-11 | ✓ <br> 2026-03-11 | EX <br> 2026-03-11 |
| 2.3 Group Membership             | GID 2001 (administrators) for all containers                                                              | ✓ <br> 2026-03-11 | ✓ <br> 2026-03-11 | EX <br> 2026-03-11 |
| 2.4 umask Configuration          | umask 000 set (Node.js: `process.umask(0o000)`, Python: `os.umask(0o000)`, Supervisord: start.sh wrapper) | N/A <br> 2026-03-11 | ✓ <br> 2026-03-11 | EX <br> 2026-03-11 |
| 2.5 File Ownership in Dockerfile | Uses `COPY --chown` instead of `chown -R`                                                                 | ✓ <br> 2026-03-11 | ✓ <br> 2026-03-11 | ✓ <br> 2026-03-11 |
| 2.6 Post-Deployment Permissions  | Database directories have correct permissions (750/640) applied on host after deployment                  | N/A <br> 2026-03-11 | N/A <br> 2026-03-11 | ✗ <br> 2026-03-11 |

***

## 3. Storage and Data

| Requirement                         | Description                                                                                           | `kaiser` | `kaiser-langgraph` | `kaiser-postgres` |
|-------------------------------------|-------------------------------------------------------------------------------------------------------|---------|-------------------|----------------|
| 3.1 Two-Volume Mounting Policy      | Mounts exactly two volumes: `storage:/storage` and `workspace:/workspace`                             | ✓ <br> 2026-03-11 | ✓ <br> 2026-03-11 | EX <br> 2026-03-11 |
| 3.2 Volume Mount Correctness        | Mounts root volumes (not subdirectories): `storage:/storage` NOT `storage:/storage/databases/[mad]`   | ✓ <br> 2026-03-11 | ✓ <br> 2026-03-11 | ✓ <br> 2026-03-11 |
| 3.3 Workspace Folder Organization   | Creates own workspace subdirectory `/workspace/[container-name]/`                                     | ✓ <br> 2026-03-11 | ✓ <br> 2026-03-11 | ✓ <br> 2026-03-11 |
| 3.4 Storage vs Workspace Decision   | Credentials/backups in `/storage/`, databases in `/workspace/`                                        | ✓ <br> 2026-03-11 | ✓ <br> 2026-03-11 | ✓ <br> 2026-03-11 |
| 3.5 Credentials Management          | Loads credentials from `/storage/credentials/[mad]/`, never hardcoded                                 | ✓ <br> 2026-03-11 | ✓ <br> 2026-03-11 | ✓ <br> 2026-03-11 |
| 3.6 No Hardcoded Secrets            | No secrets in code, Dockerfiles, environment variables, or git                                        | ✓ <br> 2026-03-11 | ✓ <br> 2026-03-11 | ✓ <br> 2026-03-11 |
| 3.7 Database/State Storage Location | MAD databases in `/workspace/[mad]/databases/[tech]/`, backups in `/storage/backups/databases/[mad]/` | N/A <br> 2026-03-11 | N/A <br> 2026-03-11 | ✓ <br> 2026-03-11 |

***

## 4. Communication and Integration

| Requirement                         | Description                                                                                                                                                                                              | `kaiser` | `kaiser-langgraph` | `kaiser-postgres` |
|-------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------|-------------------|----------------|
| 4.1 MCP Transport Protocol          | MCP uses HTTP/SSE transport (not WebSocket or stdio)                                                                                                                                                     | N/A <br> 2026-03-11 | ✓ <br> 2026-03-11 | N/A <br> 2026-03-11 |
| 4.2 MCP Endpoint Availability       | Exposes `/health` and `/mcp` endpoints accessible from joshua-net                                                                                                                                        | ✓ <br> 2026-03-11 | ✓ <br> 2026-03-11 | N/A <br> 2026-03-11 |
| 4.3 Sam Relay Compatibility         | Registry entry exists, Sam can discover and relay tools                                                                                                                                                  | ✓ <br> 2026-03-11 | N/A <br> 2026-03-11 | N/A <br> 2026-03-11 |
| 4.4 Tool Naming Convention          | Tools follow `[domain]_[action]` pattern                                                                                                                                                                 | N/A <br> 2026-03-11 | ✓ <br> 2026-03-11 | N/A <br> 2026-03-11 |
| 4.5 MCP Gateway Template Usage      | Gateway created from `mads/_template/template/` with standard libraries (mcp-protocol-lib, health-aggregator-lib, logging-lib, routing-lib). server.js unchanged from template (< 20 lines)              | EX <br> 2026-03-11 | N/A <br> 2026-03-11 | N/A <br> 2026-03-11 |
| 4.6 Configuration File Requirements | Valid `config.json` with tools, dependencies, validates against schema; **tool definitions match the REQ document** | EX <br> 2026-03-11 | N/A <br> 2026-03-11 | N/A <br> 2026-03-11 |
| 4.7 LangGraph Mandate               | All programmatic and cognitive logic is implemented using `StateGraph` (no Flask/FastAPI for primary app logic) | N/A <br> 2026-03-11 | ✓ <br> 2026-03-11 | N/A <br> 2026-03-11 |
| 4.8 Thin Gateway Mandate            | Gateway is a thin, config-driven router; `server.js` is minimal (<20 lines); logic is in `config.json` | EX <br> 2026-03-11 | N/A <br> 2026-03-11 | N/A <br> 2026-03-11 |
| 4.9 LangGraph State Immutability    | Functions in graph nodes return new state dictionaries, and do not mutate the input state          | N/A <br> 2026-03-11 | ✓ <br> 2026-03-11 | N/A <br> 2026-03-11 |

***

## 5. Operations and Observability

| Requirement                   | Description                                                                       | `kaiser` | `kaiser-langgraph` | `kaiser-postgres` |
|-------------------------------|-----------------------------------------------------------------------------------|---------|-------------------|----------------|
| 5.1 Logging to stdout/stderr  | All logs to stdout/stderr, no log files inside containers                         | ✓ <br> 2026-03-11 | ✓ <br> 2026-03-11 | ✓ <br> 2026-03-11 |
| 5.2 Structured Logging Format | JSON format, one entry per line, consistent fields                                | EX <br> 2026-03-11 | ✓ <br> 2026-03-11 | EX <br> 2026-03-11 |
| 5.3 Health Check Endpoint     | HTTP `/health` endpoint returns 200 (healthy) or 503 (unhealthy)                  | ✓ <br> 2026-03-11 | ✓ <br> 2026-03-11 | N/A <br> 2026-03-11 |
| 5.4 Dockerfile HEALTHCHECK    | Dockerfile includes HEALTHCHECK directive with appropriate `start_period`         | ✓ <br> 2026-03-11 | ✓ <br> 2026-03-11 | ✓ <br> 2026-03-11 |
| 5.5 MCP Request Logging       | MCP requests/responses automatically logged by mcp-protocol-lib                   | EX <br> 2026-03-11 | EX <br> 2026-03-11 | N/A <br> 2026-03-11 |
| 5.6 No File-Based Logging     | No `/var/log/` or `/app/logs/` directories for application logs                   | ✓ <br> 2026-03-11 | ✓ <br> 2026-03-11 | ✓ <br> 2026-03-11 |
| 5.7 Log Level Guidelines      | Supports DEBUG/INFO/WARN/ERROR levels, configurable at runtime                    | N/A <br> 2026-03-11 | ✓ <br> 2026-03-11 | N/A <br> 2026-03-11 |
| 5.8 Log Content Standards     | Logs appropriate info, excludes secrets/PII, health checks only log state changes | N/A <br> 2026-03-11 | ✓ <br> 2026-03-11 | N/A <br> 2026-03-11 |
| 5.9 Health Check Architecture | Docker HEALTHCHECK checks process only, `/health` endpoint checks dependencies    | N/A <br> 2026-03-11 | ✓ <br> 2026-03-11 | N/A <br> 2026-03-11 |
| 5.10 Specific Exception Handling| Does not use blanket `except Exception:` or `except:`                                              | N/A <br> 2026-03-11 | ✓ <br> 2026-03-11 | N/A <br> 2026-03-11 |
| 5.11 Resource Management        | All external resources (e.g., file handles, DB connections) are reliably closed using `with` or `finally` | N/A <br> 2026-03-11 | ✓ <br> 2026-03-11 | N/A <br> 2026-03-11 |
| 5.12 Error Context              | All logged errors and raised exceptions include sufficient context for debugging                 | N/A <br> 2026-03-11 | ✓ <br> 2026-03-11 | N/A <br> 2026-03-11 |

***

## 6. Documentation and Discoverability

| Requirement             | Description                                                                                     | `kaiser` | `kaiser-langgraph` | `kaiser-postgres` |
|-------------------------|-------------------------------------------------------------------------------------------------|---------|-------------------|----------------|
| 6.1 REQ Document        | Component REQ document exists with purpose, tools, dependencies, credentials, volumes, ports    | ✓ <br> 2026-03-11 | ✓ <br> 2026-03-11 | ✓ <br> 2026-03-11 |
| 6.2 README.md           | README exists with architecture, deployment, configuration, recovery procedures                 | ✓ <br> 2026-03-11 | ✓ <br> 2026-03-11 | ✓ <br> 2026-03-11 |
| 6.3 Registry Entry      | ALL containers have registry entries; MAD group shares UID; only gateway has port/mcp_endpoints | ✓ <br> 2026-03-11 | ✓ <br> 2026-03-11 | ✓ <br> 2026-03-11 |
| 6.4 Directory Structure | MAD Group has parent folder in `mads/` containing subdirectories for each container's source code | ✓ <br> 2026-03-11 | ✓ <br> 2026-03-11 | ✓ <br> 2026-03-11 |
| 6.5 Tool Documentation  | Tools documented with descriptions, schemas, examples, error codes                              | N/A <br> 2026-03-11 | ✓ <br> 2026-03-11 | N/A <br> 2026-03-11 |

***

## 7. Resilience, Safety, and Deployment

| Requirement                       | Description                                                                                | `kaiser` | `kaiser-langgraph` | `kaiser-postgres` |
|-----------------------------------|--------------------------------------------------------------------------------------------|---------|-------------------|----------------|
| 7.1 Graceful Degradation          | External dependency failures cause degradation (not crash), health reports degraded status | N/A <br> 2026-03-11 | ✓ <br> 2026-03-11 | N/A <br> 2026-03-11 |
| 7.2 MAD Group Boundaries          | Internal (hard) vs external (soft) dependencies clearly defined                            | ✓ <br> 2026-03-11 | ✓ <br> 2026-03-11 | ✓ <br> 2026-03-11 |
| 7.3 Independent Container Startup | Container starts and becomes healthy without waiting for dependencies                      | ✓ <br> 2026-03-11 | ✓ <br> 2026-03-11 | ✓ <br> 2026-03-11 |
| 7.4 Overlay Network DNS Usage     | Uses container names for communication (never IP addresses)                                | ✓ <br> 2026-03-11 | ✓ <br> 2026-03-11 | ✓ <br> 2026-03-11 |
| 7.5 Docker Compose Configuration  | Service defined in master `docker-compose.yml`, build context is `.` (project root)        | ✓ <br> 2026-03-11 | ✓ <br> 2026-03-11 | ✓ <br> 2026-03-11 |
| 7.4.1 Per-MAD Private Networks    | Gateway on joshua-net + [mad]-net; langgraph and backing services on [mad]-net only        | ✓ <br> 2026-03-11 | ✓ <br> 2026-03-11 | ✓ <br> 2026-03-11 |
| 7.6 Host Affinity Configuration   | Host affinity via profiles in per-host override files (not Swarm placement constraints)    | ✓ <br> 2026-03-11 | ✓ <br> 2026-03-11 | ✓ <br> 2026-03-11 |
| 7.7 Git Safety Mechanisms         | Git operations include backup, dry-run, rollback, user confirmation (if applicable)        | N/A <br> 2026-03-11 | N/A <br> 2026-03-11 | N/A <br> 2026-03-11 |
| 7.8 Conversation Data Integration | Writes to Rogers directly or via watcher (if applicable)                                   | N/A <br> 2026-03-11 | N/A <br> 2026-03-11 | N/A <br> 2026-03-11 |
| 7.9 Asynchronous Correctness      | No blocking I/O (`time.sleep`) is used; all I/O is `async` and `await`ed                         | N/A <br> 2026-03-11 | ✓ <br> 2026-03-11 | N/A <br> 2026-03-11 |
| 7.10 Input Validation             | All data received from external sources is validated before use                                  | N/A <br> 2026-03-11 | ✓ <br> 2026-03-11 | N/A <br> 2026-03-11 |
| 7.11 Null/None Checking           | Variables that can be `None` are explicitly checked before their attributes or methods are accessed | N/A <br> 2026-03-11 | ✓ <br> 2026-03-11 | N/A <br> 2026-03-11 |

***

## 8. Exceptions and Special Cases

| Requirement                 | Description                                                                     | `kaiser` | `kaiser-langgraph` | `kaiser-postgres` |
|-----------------------------|---------------------------------------------------------------------------------|---------|-------------------|----------------|
| 8.1 Exception Documentation | Non-compliant items documented in REQ-000-exception-registry with reason, impact, mitigation       | ✓ <br> 2026-03-11 | ✓ <br> 2026-03-11 | ✓ <br> 2026-03-11 |
| 8.2 Exception Approval      | All exceptions approved by Joshua/Aristotle9, documented with approver and date | ✓ <br> 2026-03-11 | ✓ <br> 2026-03-11 | ✓ <br> 2026-03-11 |

***

## N/A Justifications

| Requirement | Container | Reason | Approved By | Date |
| :--- | :--- | :--- | :--- | :--- |
| 1.1 | kaiser, kaiser-postgres | Do not use Python dependencies | J | 2026-03-11 |
| 1.2 | All | Do not use Node.js dependencies | J | 2026-03-11 |
| 1.3 | kaiser, kaiser-langgraph | Do not use apk add for system packages | J | 2026-03-11 |
| 1.5 | All | No runtime binaries downloaded | J | 2026-03-11 |
| 1.6 | All | No hybrid runtimes used | J | 2026-03-11 |
| 1.8, 1.9 | kaiser, kaiser-postgres | Not Python codebases | J | 2026-03-11 |
| 1.10 | kaiser, kaiser-postgres | Not programmatic logic containers | J | 2026-03-11 |
| 2.4 | kaiser | nginx:alpine proxy gateway does not support explicit umask | J | 2026-03-11 |
| 2.6 | kaiser, kaiser-langgraph | Not database containers | J | 2026-03-11 |
| 3.7 | kaiser, kaiser-langgraph | Not database containers | J | 2026-03-11 |
| 4.1 | kaiser, kaiser-postgres | Not MCP runtime servers (nginx proxy / DB) | J | 2026-03-11 |
| 4.2 | kaiser-postgres | Internal backend service only | J | 2026-03-11 |
| 4.3 | kaiser-langgraph, kaiser-postgres | Service registry entry applies to the MAD group via the gateway | J | 2026-03-11 |
| 4.4, 4.5, 4.6, 4.7, 4.8, 4.9 | Various | State 3 architectural divergence, handled primarily by EX or inapplicable to specific component types | J | 2026-03-11 |
| 5.3, 5.5, 5.7, 5.8, 5.9, 5.10, 5.11, 5.12 | Various | Features specific to LangGraph runtime, inapplicable to gateway/DB | J | 2026-03-11 |
| 6.5 | kaiser, kaiser-postgres | No MCP tools directly defined | J | 2026-03-11 |
| 7.1, 7.7, 7.8, 7.9, 7.10, 7.11 | Various | Inapplicable due to container type or lack of Git/Rogers-ingestion requirements | J | 2026-03-11 |

***

## Exception Justifications

| Requirement | Container | Reason | Mitigation | Exception ID | Approved By | Date |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1.1 | kaiser-langgraph | Installs Python packages from Alexandria at build/runtime (State 3 eMAD pattern) | Alexandria is the ecosystem offline cache (on irina) | EX-KAISER-001 | J | 2026-03-11 |
| 3.1 | kaiser-postgres | Suppresses anonymous volume with bind mount | Bind mount to host NVMe persistent path | EX-KAISER-002 | J | 2026-03-11 |
| 2.1, 2.2, 2.3, 2.4 | kaiser-postgres | postgres:16-alpine requires root init to chown PGDATA | Host-level permissions applied (but currently 700 instead of 750) | EX-KAISER-003 | J | 2026-03-11 |
| 4.5, 4.6, 4.8 | kaiser | State 3 uses nginx gateway, not Node.js template | LangGraph FastMCP handles routing natively | EX-KAISER-004 | J | 2026-03-11 |
| 5.2 | kaiser | nginx error_log is plain text | Standard logging via docker logs | EX-KAISER-005 | J | 2026-03-11 |
| 1.10 | kaiser-langgraph | No unit tests for State 3 integration flows | End-to-end testing via MCP tool calls at Gate 3 | EX-KAISER-006 | J | 2026-03-11 |
| 5.2 | kaiser-postgres | Native PostgreSQL logs are not JSON | Standard logging via docker logs | EX-KAISER-007 | J | 2026-03-11 |
| 5.5 | kaiser, kaiser-langgraph | Uses FastMCP, not Node.js mcp-protocol-lib | Manual structured JSON logging in _log_mcp() | EX-KAISER-008 | J | 2026-03-11 |

***

## Audit Summary

**Total Requirements:** 63 **Passed:** 41 **Failed:** 1 **N/A:** 15 **Exceptions:** 6

**Compliance Status:** Non-Compliant

**Blocker Issues:**
- `2.6 Post-Deployment Permissions`: `kaiser-postgres` data directory `/mnt/nvme/workspace/kaiser/databases/postgres/data` on M5 has permissions `700` (`drwx------`), but the mitigation for `EX-KAISER-003` and requirement `2.6` mandate `750` or `640`.

**Next Steps:**
- Fix permissions on M5: `chmod 750 /mnt/nvme/workspace/kaiser/databases/postgres/data`
- Re-run Gate 3 audit.

***

## Remediation Plan

**Objective:** Bring Kaiser MAD into full deployment compliance.

| Requirement | Container | Action Required |
| :--- | :--- | :--- |
| 2.6 | kaiser-postgres | SSH into M5 and run `chmod 750 /mnt/nvme/workspace/kaiser/databases/postgres/data` to satisfy `EX-KAISER-003` mitigation requirements. |