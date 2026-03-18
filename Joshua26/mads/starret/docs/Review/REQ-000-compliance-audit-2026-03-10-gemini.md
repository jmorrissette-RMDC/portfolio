**Reviewer:** gemini
**Gate:** 3
**MAD:** starret
**Date:** 2026-03-10

# REQ-000 Compliance Checklist: starret

**MAD Group:** starret **Audit Date:** 2026-03-10 **Auditor:** Gemini **Status:** Complete

***

## 1. Build System

| Requirement                     | Description                                                                                      | `starret` | `starret-langgraph` | `github-runner` |
|---------------------------------|--------------------------------------------------------------------------------------------------|-------|-------------|----------|
| 1.1 Python Package Caching      | All Python dependencies cached in `packages/`, pinned versions (`==`), offline build works       | N/A   | ✗           | N/A      |
| 1.2 Node.js Package Caching     | All Node.js dependencies cached in `packages/`, exact versions (no `^`/`~`), offline build works | N/A   | N/A         | N/A      |
| 1.3 System Package Caching      | System packages (apt/apk) cached locally, offline build works                                    | N/A   | N/A         | N/A      |
| 1.4 Docker Base Image Caching   | Base image pinned to specific version (not `latest`), available locally                          | ✓     | ✓           | ✓        |
| 1.5 Runtime Binary Caching      | Runtime binaries (Playwright, etc.) cached locally, no runtime downloads                         | N/A   | N/A         | N/A      |
| 1.6 Hybrid Runtime Environments | Both Python and Node.js packages cached if both runtimes used                                    | N/A   | N/A         | N/A      |
| 1.7 Version Pinning             | All dependencies locked to specific versions (Docker, Python, Node.js)                           | ✓     | ✓           | ✓        |
| 1.8 Code Formatting (Python)    | Code passes `black --check .`                                                                    | N/A   | ✗           | N/A      |
| 1.9 Code Linting (Python)       | Code passes `ruff check .`                                                                       | N/A   | ✓           | N/A      |
| 1.10 Unit Testing Mandate       | All new programmatic logic is accompanied by `pytest` unit tests for the happy path and error conditions | N/A   | ✓           | N/A      |

***

## 2. Runtime Security and Permissions

| Requirement                      | Description                                                                                               | `starret` | `starret-langgraph` | `github-runner` |
|----------------------------------|-----------------------------------------------------------------------------------------------------------|---------|-------------------|----------------|
| 2.1 Root Usage Pattern           | Root used ONLY for packages and user creation, USER directive follows immediately                         | ✓       | ✓                 | ✗              |
| 2.2 Service Account Creation     | Runs as dedicated service account with UID from registry.yml                                              | ✓       | ✓                 | ✗              |
| 2.3 Group Membership             | GID 2001 (administrators) for all containers                                                              | ✓       | ✓                 | ✗              |
| 2.4 umask Configuration          | umask 000 set (Node.js: `process.umask(0o000)`, Python: `os.umask(0o000)`, Supervisord: start.sh wrapper) | ✗       | ✓                 | N/A            |
| 2.5 File Ownership in Dockerfile | Uses `COPY --chown` instead of `chown -R`                                                                 | ✓       | ✓                 | N/A            |
| 2.6 Post-Deployment Permissions  | Database directories have correct permissions (750/640) applied on host after deployment                  | N/A     | N/A               | N/A            |

***

## 3. Storage and Data

| Requirement                         | Description                                                                                           | `starret` | `starret-langgraph` | `github-runner` |
|-------------------------------------|-------------------------------------------------------------------------------------------------------|---------|-------------------|----------------|
| 3.1 Two-Volume Mounting Policy      | Mounts exactly two volumes: `storage:/storage` and `workspace:/workspace`                             | ✓       | ✓                 | EX             |
| 3.2 Volume Mount Correctness        | Mounts root volumes (not subdirectories): `storage:/storage` NOT `storage:/storage/databases/[mad]`   | ✓       | ✓                 | ✓              |
| 3.3 Workspace Folder Organization   | Creates own workspace subdirectory `/workspace/[container-name]/`                                     | N/A     | N/A               | N/A            |
| 3.4 Storage vs Workspace Decision   | Credentials/backups in `/storage/`, databases in `/workspace/`                                        | N/A     | ✓                 | N/A            |
| 3.5 Credentials Management          | Loads credentials from `/storage/credentials/[mad]/`, never hardcoded                                 | N/A     | ✓                 | N/A            |
| 3.6 No Hardcoded Secrets            | No secrets in code, Dockerfiles, environment variables, or git                                        | ✓       | ✓                 | ✓              |
| 3.7 Database/State Storage Location | MAD databases in `/workspace/[mad]/databases/[tech]/`, backups in `/storage/backups/databases/[mad]/` | N/A     | N/A               | N/A            |

***

## 4. Communication and Integration

| Requirement                         | Description                                                                                                                                                                                              | `starret` | `starret-langgraph` | `github-runner` |
|-------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------|-------------------|----------------|
| 4.1 MCP Transport Protocol          | MCP uses HTTP/SSE transport (not WebSocket or stdio)                                                                                                                                                     | ✓       | ✓                 | N/A            |
| 4.2 MCP Endpoint Availability       | Exposes `/health` and `/mcp` endpoints accessible from joshua-net                                                                                                                                        | ✓       | N/A               | N/A            |
| 4.3 Sam Relay Compatibility         | Registry entry exists, Sam can discover and relay tools                                                                                                                                                  | ✓       | N/A               | N/A            |
| 4.4 Tool Naming Convention          | Tools follow `[domain]_[action]` pattern                                                                                                                                                                 | N/A     | ✓                 | N/A            |
| 4.5 MCP Gateway Template Usage      | Gateway created from `mads/_template/template/` with standard libraries (mcp-protocol-lib, health-aggregator-lib, logging-lib, routing-lib). server.js unchanged from template (< 20 lines)              | ✗       | N/A               | N/A            |
| 4.6 Configuration File Requirements | Valid `config.json` with tools, dependencies, validates against schema; **tool definitions match the REQ document** | ✗       | N/A               | N/A            |
| 4.7 LangGraph Mandate               | All programmatic and cognitive logic is implemented using `StateGraph` (no Flask/FastAPI for primary app logic) | N/A     | ✓                 | N/A            |
| 4.8 Thin Gateway Mandate            | Gateway is a thin, config-driven router; `server.js` is minimal (<20 lines); logic is in `config.json` | ✗       | N/A               | N/A            |
| 4.9 LangGraph State Immutability    | Functions in graph nodes return new state dictionaries, and do not mutate the input state          | N/A     | ✓                 | N/A            |

***

## 5. Operations and Observability

| Requirement                   | Description                                                                       | `starret` | `starret-langgraph` | `github-runner` |
|-------------------------------|-----------------------------------------------------------------------------------|---------|-------------------|----------------|
| 5.1 Logging to stdout/stderr  | All logs to stdout/stderr, no log files inside containers                         | ✓       | ✓                 | ✓              |
| 5.2 Structured Logging Format | JSON format, one entry per line, consistent fields                                | ✗       | ✓                 | ✗              |
| 5.3 Health Check Endpoint     | HTTP `/health` endpoint returns 200 (healthy) or 503 (unhealthy)                  | ✓       | ✓                 | N/A            |
| 5.4 Dockerfile HEALTHCHECK    | Dockerfile includes HEALTHCHECK directive with appropriate `start_period`         | ✓       | ✓                 | N/A            |
| 5.5 MCP Request Logging       | MCP requests/responses automatically logged by mcp-protocol-lib                   | ✗       | ✓                 | N/A            |
| 5.6 No File-Based Logging     | No `/var/log/` or `/app/logs/` directories for application logs                   | ✓       | ✓                 | ✓              |
| 5.7 Log Level Guidelines      | Supports DEBUG/INFO/WARN/ERROR levels, configurable at runtime                    | ✗       | ✓                 | N/A            |
| 5.8 Log Content Standards     | Logs appropriate info, excludes secrets/PII, health checks only log state changes | ✓       | ✓                 | ✓              |
| 5.9 Health Check Architecture | Docker HEALTHCHECK checks process only, `/health` endpoint checks dependencies    | ✓       | ✓                 | N/A            |
| 5.10 Specific Exception Handling| Does not use blanket `except Exception:` or `except:`                                              | N/A     | ✓                 | N/A            |
| 5.11 Resource Management        | All external resources (e.g., file handles, DB connections) are reliably closed using `with` or `finally` | N/A     | ✓                 | N/A            |
| 5.12 Error Context              | All logged errors and raised exceptions include sufficient context for debugging                 | N/A     | ✓                 | N/A            |

***

## 6. Documentation and Discoverability

| Requirement             | Description                                                                                     | `starret` | `starret-langgraph` | `github-runner` |
|-------------------------|-------------------------------------------------------------------------------------------------|---------|-------------------|----------------|
| 6.1 REQ Document        | Component REQ document exists with purpose, tools, dependencies, credentials, volumes, ports    | ✓       | ✓                 | ✓              |
| 6.2 README.md           | README exists with architecture, deployment, configuration, recovery procedures                 | ✓       | ✓                 | ✓              |
| 6.3 Registry Entry      | ALL containers have registry entries; MAD group shares UID; only gateway has port/mcp_endpoints | ✓       | ✓                 | ✓              |
| 6.4 Directory Structure | MAD Group has parent folder in `mads/` containing subdirectories for each container's source code | ✓       | ✓                 | ✓              |
| 6.5 Tool Documentation  | Tools documented with descriptions, schemas, examples, error codes                              | ✓       | ✓                 | N/A            |

***

## 7. Resilience, Safety, and Deployment

| Requirement                       | Description                                                                                | `starret` | `starret-langgraph` | `github-runner` |
|-----------------------------------|--------------------------------------------------------------------------------------------|---------|-------------------|----------------|
| 7.1 Graceful Degradation          | External dependency failures cause degradation (not crash), health reports degraded status | ✓       | ✓                 | N/A            |
| 7.2 MAD Group Boundaries          | Internal (hard) vs external (soft) dependencies clearly defined                            | ✓       | ✓                 | ✓              |
| 7.3 Independent Container Startup | Container starts and becomes healthy without waiting for dependencies                      | ✓       | ✓                 | ✓              |
| 7.4 Overlay Network DNS Usage     | Uses container names for communication (never IP addresses)                                | ✓       | ✓                 | N/A            |
| 7.5 Docker Compose Configuration  | Service defined in master `docker-compose.yml`, build context is `.` (project root)        | ✓       | ✓                 | ✓              |
| 7.4.1 Per-MAD Private Networks    | Gateway on joshua-net + [mad]-net; langgraph and backing services on [mad]-net only        | ✓       | ✓                 | ✓              |
| 7.6 Host Affinity Configuration   | Host affinity via profiles in per-host override files (not Swarm placement constraints)    | ✓       | ✓                 | ✓              |
| 7.7 Git Safety Mechanisms         | Git operations include backup, dry-run, rollback, user confirmation (if applicable)        | N/A     | ✓                 | N/A            |
| 7.8 Conversation Data Integration | Writes to Rogers directly or via watcher (if applicable)                                   | N/A     | N/A               | N/A            |
| 7.9 Asynchronous Correctness      | No blocking I/O (`time.sleep`) is used; all I/O is `async` and `await`ed                         | N/A     | ✓                 | N/A            |
| 7.10 Input Validation             | All data received from external sources is validated before use                                  | N/A     | ✓                 | N/A            |
| 7.11 Null/None Checking           | Variables that can be `None` are explicitly checked before their attributes or methods are accessed | N/A     | ✓                 | N/A            |

***

## 8. Exceptions and Special Cases

| Requirement                 | Description                                                                     | `starret` | `starret-langgraph` | `github-runner` |
|-----------------------------|---------------------------------------------------------------------------------|---------|-------------------|----------------|
| 8.1 Exception Documentation | Non-compliant items documented in REQ-000-exception-registry with reason, impact, mitigation       | N/A     | N/A               | ✓              |
| 8.2 Exception Approval      | All exceptions approved by Joshua/Aristotle9, documented with approver and date | N/A     | N/A               | ✓              |

***

## N/A Justifications

| Requirement | Container   | Reason               | Approved By | Date |
|-------------|-------------|----------------------|-------------|------|
| 1.2, 1.3, 1.5, 1.6 | all | Not applicable to python/nginx stacks. | | |
| 1.8, 1.9, 1.10 | starret | Nginx has no programmatic logic to lint or unit test. | | |
| 2.4 | github-runner | Official GH runner image managed by actions-runner. | | |
| 2.6 | all | No external database directories mapped. | | |
| 4.2 | starret-langgraph | Endpoints are exposed on the gateway, not directly on langgraph. | | |
| 4.3 | starret-langgraph | Gateway registers with Sam Relay. | | |

***

## Exception Justifications

| Requirement | Container   | Reason                      | Mitigation        | Exception ID | Approved By | Date |
|-------------|-------------|-----------------------------|-------------------|--------------|-------------|------|
| 3.1 | github-runner | Needs docker socket for docker-in-docker image builds. | Documented in docker-compose.yml | EX-STARRET-001 | | |

***

## Audit Summary

**Total Requirements:** 63 **Passed:** 43 **Failed:** 8 **N/A:** 11 **Exceptions:** 1

**Compliance Status:** Non-Compliant

**Blocker Issues:**
- `1.1`: Python dependencies for `starret-langgraph` use Alexandria proxy instead of caching in `packages/`. (Requires formal EX record based on ADR-038).
- `1.8`: Code does not pass `black --check .` (`mads/starret/starret-langgraph/flows/github_ops.py` needs reformatting).
- `2.4`: `starret` container umask is 0022 on the live system, failing the 0000 requirement.
- `4.5` / `4.6` / `4.8`: The `starret` gateway uses Nginx (a State 2 pattern) instead of the Node.js `mads/_template/template/` standard libraries pattern mandated for State 1 by ADR-051 and REQ-000. It lacks `config.json` and standard `mcp-protocol-lib`.
- `5.2` / `5.5`: Nginx does not use structured JSON logging or standard MCP request logging.

**Next Steps:**
- Reformat python code.
- Migrate `starret` gateway to the standard Node.js `mcp-gateway` template per ADR-051 and implement bidirectional proxy using `/peer` (ADR-053) instead of custom nginx proxy rules.
- Fix umask in the new Node.js gateway container.
- Update `packages/` caching strategy or formally request an exception referencing ADR-038 for hybrid caching.

***

## Remediation Plan

**Objective:** Bring Starret into full compliance with REQ-000 and recent ADRs (ADR-051, ADR-053).

| Requirement | Container | Action Required |
| :--- | :--- | :--- |
| 1.1 | starret-langgraph | Ensure Python packages are cached locally or document EX based on ADR-038. |
| 1.8 | starret-langgraph | Run `black mads/starret/starret-langgraph/flows/github_ops.py`. |
| 2.4 | starret | Use the `start.sh` wrapper from the Node template to ensure umask `000` is applied. |
| 4.5, 4.6, 4.8 | starret | Replace Nginx container with the standard Node.js gateway template (`mads/_template/template/`). |
| 5.2, 5.5 | starret | Inherited automatically when adopting the Node.js gateway template. |