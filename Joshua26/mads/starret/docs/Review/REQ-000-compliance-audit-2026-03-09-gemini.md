**Reviewer:** gemini
**Gate:** 3
**MAD:** starret
**Date:** 2026-03-09

# REQ-000 Compliance Checklist: starret

**MAD Group:** starret
**Audit Date:** 2026-03-09
**Auditor:** gemini
**Status:** Complete

***

## Instructions

(Reference docs/audits/REQ-000-compliance-checklist.md)

***

## 1. Build System

| Requirement                     | Description                                                                                      | `starret` | `starret-langgraph` | `github-runner` |
|---------------------------------|--------------------------------------------------------------------------------------------------|-------|-------------|----------|
| 1.1 Python Package Caching      | All Python dependencies cached in `packages/`, pinned versions (`==`), offline build works       | N/A   | ✗<br>2026-03-09 | N/A      |
| 1.2 Node.js Package Caching     | All Node.js dependencies cached in `packages/`, exact versions (no `^`/`~`), offline build works | N/A   | N/A         | N/A      |
| 1.3 System Package Caching      | System packages (apt/apk) cached locally, offline build works                                    | N/A   | N/A         | N/A      |
| 1.4 Docker Base Image Caching   | Base image pinned to specific version (not `latest`), available locally                          | ✓<br>2026-03-09 | ✓<br>2026-03-09 | N/A      |
| 1.5 Runtime Binary Caching      | Runtime binaries (Playwright, etc.) cached locally, no runtime downloads                         | N/A   | N/A         | N/A      |
| 1.6 Hybrid Runtime Environments | Both Python and Node.js packages cached if both runtimes used                                    | N/A   | N/A         | N/A      |
| 1.7 Version Pinning             | All dependencies locked to specific versions (Docker, Python, Node.js)                           | ✓<br>2026-03-09 | ✓<br>2026-03-09 | ✓<br>2026-03-09 |
| 1.8 Code Formatting (Python)    | Code passes `black --check .`                                                                    | N/A   | ✗<br>2026-03-09 | N/A      |
| 1.9 Code Linting (Python)       | Code passes `ruff check .`                                                                       | N/A   | ✗<br>2026-03-09 | N/A      |
| 1.10 Unit Testing Mandate       | All new programmatic logic is accompanied by `pytest` unit tests for the happy path and error conditions | N/A   | ✗<br>2026-03-09 | N/A      |

***

## 2. Runtime Security and Permissions

| Requirement                      | Description                                                                                               | `starret` | `starret-langgraph` | `github-runner` |
|----------------------------------|-----------------------------------------------------------------------------------------------------------|---------|-------------------|----------------|
| 2.1 Root Usage Pattern           | Root used ONLY for packages and user creation, USER directive follows immediately                         | ✓<br>2026-03-09 | ✓<br>2026-03-09 | ✓<br>2026-03-09 |
| 2.2 Service Account Creation     | Runs as dedicated service account with UID from registry.yml                                              | ✓<br>2026-03-09 | ✓<br>2026-03-09 | EX<br>2026-03-09 |
| 2.3 Group Membership             | GID 2001 (administrators) for all containers                                                              | ✓<br>2026-03-09 | ✓<br>2026-03-09 | EX<br>2026-03-09 |
| 2.4 umask Configuration          | umask 000 set (Node.js: `process.umask(0o000)`, Python: `os.umask(0o000)`, Supervisord: start.sh wrapper) | ✗<br>2026-03-09 | ✓<br>2026-03-09 | N/A      |
| 2.5 File Ownership in Dockerfile | Uses `COPY --chown` instead of `chown -R`                                                                 | ✓<br>2026-03-09 | ✓<br>2026-03-09 | N/A      |
| 2.6 Post-Deployment Permissions  | Database directories have correct permissions (750/640) applied on host after deployment                  | N/A   | N/A         | N/A      |

***

## 3. Storage and Data

| Requirement                         | Description                                                                                           | `starret` | `starret-langgraph` | `github-runner` |
|-------------------------------------|-------------------------------------------------------------------------------------------------------|---------|-------------------|----------------|
| 3.1 Two-Volume Mounting Policy      | Mounts exactly two volumes: `storage:/storage` and `workspace:/workspace`                             | ✓<br>2026-03-09 | ✓<br>2026-03-09 | EX<br>2026-03-09 |
| 3.2 Volume Mount Correctness        | Mounts root volumes (not subdirectories): `storage:/storage` NOT `storage:/storage/databases/[mad]`   | ✓<br>2026-03-09 | ✓<br>2026-03-09 | ✓<br>2026-03-09 |
| 3.3 Workspace Folder Organization   | Creates own workspace subdirectory `/workspace/[container-name]/`                                     | ✗<br>2026-03-09 | ✗<br>2026-03-09 | ✗<br>2026-03-09 |
| 3.4 Storage vs Workspace Decision   | Credentials/backups in `/storage/`, databases in `/workspace/`                                        | ✓<br>2026-03-09 | ✓<br>2026-03-09 | ✓<br>2026-03-09 |
| 3.5 Credentials Management          | Loads credentials from `/storage/credentials/[mad]/`, never hardcoded                                 | N/A   | ✗<br>2026-03-09 | N/A      |
| 3.6 No Hardcoded Secrets            | No secrets in code, Dockerfiles, environment variables, or git                                        | ✓<br>2026-03-09 | ✓<br>2026-03-09 | ✓<br>2026-03-09 |
| 3.7 Database/State Storage Location | MAD databases in `/workspace/[mad]/databases/[tech]/`, backups in `/storage/backups/databases/[mad]/` | N/A   | N/A         | N/A      |

***

## 4. Communication and Integration

| Requirement                         | Description                                                                                                                                                                                              | `starret` | `starret-langgraph` | `github-runner` |
|-------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------|-------------------|----------------|
| 4.1 MCP Transport Protocol          | MCP uses HTTP/SSE transport (not WebSocket or stdio)                                                                                                                                                     | ✓<br>2026-03-09 | ✓<br>2026-03-09 | N/A      |
| 4.2 MCP Endpoint Availability       | Exposes `/health` and `/mcp` endpoints accessible from joshua-net                                                                                                                                        | ✓<br>2026-03-09 | ✓<br>2026-03-09 | N/A      |
| 4.3 Sam Relay Compatibility         | Registry entry exists, Sam can discover and relay tools                                                                                                                                                  | ✓<br>2026-03-09 | N/A         | N/A      |
| 4.4 Tool Naming Convention          | Tools follow `[domain]_[action]` pattern                                                                                                                                                                 | ✓<br>2026-03-09 | ✓<br>2026-03-09 | N/A      |
| 4.5 MCP Gateway Template Usage      | Gateway created from `mads/_template/template/` with standard libraries (mcp-protocol-lib, health-aggregator-lib, logging-lib, routing-lib). server.js unchanged from template (< 20 lines)              | N/A   | N/A         | N/A      |
| 4.6 Configuration File Requirements | Valid `config.json` with tools, dependencies, validates against schema; **tool definitions match the REQ document** | N/A   | N/A         | N/A      |
| 4.7 LangGraph Mandate               | All programmatic and cognitive logic is implemented using `StateGraph` (no Flask/FastAPI for primary app logic) | N/A   | ✓<br>2026-03-09 | N/A      |
| 4.8 Thin Gateway Mandate            | Gateway is a thin, config-driven router; `server.js` is minimal (<20 lines); logic is in `config.json` | ✓<br>2026-03-09 | N/A         | N/A      |
| 4.9 LangGraph State Immutability    | Functions in graph nodes return new state dictionaries, and do not mutate the input state          | N/A   | ✓<br>2026-03-09 | N/A      |

***

## 5. Operations and Observability

| Requirement                   | Description                                                                       | `starret` | `starret-langgraph` | `github-runner` |
|-------------------------------|-----------------------------------------------------------------------------------|---------|-------------------|----------------|
| 5.1 Logging to stdout/stderr  | All logs to stdout/stderr, no log files inside containers                         | ✓<br>2026-03-09 | ✓<br>2026-03-09 | ✓<br>2026-03-09 |
| 5.2 Structured Logging Format | JSON format, one entry per line, consistent fields                                | ✓<br>2026-03-09 | ✓<br>2026-03-09 | N/A      |
| 5.3 Health Check Endpoint     | HTTP `/health` endpoint returns 200 (healthy) or 503 (unhealthy)                  | ✓<br>2026-03-09 | ✓<br>2026-03-09 | N/A      |
| 5.4 Dockerfile HEALTHCHECK    | Dockerfile includes HEALTHCHECK directive with appropriate `start_period`         | ✓<br>2026-03-09 | ✓<br>2026-03-09 | N/A      |
| 5.5 MCP Request Logging       | MCP requests/responses automatically logged by mcp-protocol-lib                   | N/A   | ✓<br>2026-03-09 | N/A      |
| 5.6 No File-Based Logging     | No `/var/log/` or `/app/logs/` directories for application logs                   | ✓<br>2026-03-09 | ✓<br>2026-03-09 | ✓<br>2026-03-09 |
| 5.7 Log Level Guidelines      | Supports DEBUG/INFO/WARN/ERROR levels, configurable at runtime                    | ✓<br>2026-03-09 | ✓<br>2026-03-09 | N/A      |
| 5.8 Log Content Standards     | Logs appropriate info, excludes secrets/PII, health checks only log state changes | ✓<br>2026-03-09 | ✓<br>2026-03-09 | N/A      |
| 5.9 Health Check Architecture | Docker HEALTHCHECK checks process only, `/health` endpoint checks dependencies    | ✓<br>2026-03-09 | ✓<br>2026-03-09 | N/A      |
| 5.10 Specific Exception Handling| Does not use blanket `except Exception:` or `except:`                                              | N/A   | ✓<br>2026-03-09 | N/A      |
| 5.11 Resource Management        | All external resources (e.g., file handles, DB connections) are reliably closed using `with` or `finally` | N/A   | ✓<br>2026-03-09 | N/A      |
| 5.12 Error Context              | All logged errors and raised exceptions include sufficient context for debugging                 | N/A   | ✓<br>2026-03-09 | N/A      |

***

## 6. Documentation and Discoverability

| Requirement             | Description                                                                                     | `starret` | `starret-langgraph` | `github-runner` |
|-------------------------|-------------------------------------------------------------------------------------------------|---------|-------------------|----------------|
| 6.1 REQ Document        | Component REQ document exists with purpose, tools, dependencies, credentials, volumes, ports    | ✓<br>2026-03-09 | ✓<br>2026-03-09 | ✓<br>2026-03-09 |
| 6.2 README.md           | README exists with architecture, deployment, configuration, recovery procedures                 | ✓<br>2026-03-09 | ✓<br>2026-03-09 | ✓<br>2026-03-09 |
| 6.3 Registry Entry      | ALL containers have registry entries; MAD group shares UID; only gateway has port/mcp_endpoints | ✓<br>2026-03-09 | ✓<br>2026-03-09 | ✓<br>2026-03-09 |
| 6.4 Directory Structure | MAD Group has parent folder in `mads/` containing subdirectories for each container's source code | ✓<br>2026-03-09 | ✓<br>2026-03-09 | ✓<br>2026-03-09 |
| 6.5 Tool Documentation  | Tools documented with descriptions, schemas, examples, error codes                              | ✓<br>2026-03-09 | ✓<br>2026-03-09 | N/A      |

***

## 7. Resilience, Safety, and Deployment

| Requirement                       | Description                                                                                | `starret` | `starret-langgraph` | `github-runner` |
|-----------------------------------|--------------------------------------------------------------------------------------------|---------|-------------------|----------------|
| 7.1 Graceful Degradation          | External dependency failures cause degradation (not crash), health reports degraded status | ✓<br>2026-03-09 | ✓<br>2026-03-09 | N/A      |
| 7.2 MAD Group Boundaries          | Internal (hard) vs external (soft) dependencies clearly defined                            | ✓<br>2026-03-09 | ✓<br>2026-03-09 | ✓<br>2026-03-09 |
| 7.3 Independent Container Startup | Container starts and becomes healthy without waiting for dependencies                      | ✓<br>2026-03-09 | ✓<br>2026-03-09 | ✗<br>2026-03-09 |
| 7.4 Overlay Network DNS Usage     | Uses container names for communication (never IP addresses)                                | ✓<br>2026-03-09 | ✓<br>2026-03-09 | ✓<br>2026-03-09 |
| 7.5 Docker Compose Configuration  | Service defined in master `docker-compose.yml`, build context is `.` (project root)        | ✓<br>2026-03-09 | ✓<br>2026-03-09 | ✓<br>2026-03-09 |
| 7.4.1 Per-MAD Private Networks    | Gateway on joshua-net + [mad]-net; langgraph and backing services on [mad]-net only        | ✓<br>2026-03-09 | ✓<br>2026-03-09 | ✓<br>2026-03-09 |
| 7.6 Host Affinity Configuration   | Host affinity via profiles in per-host override files (not Swarm placement constraints)    | ✓<br>2026-03-09 | ✓<br>2026-03-09 | ✓<br>2026-03-09 |
| 7.7 Git Safety Mechanisms         | Git operations include backup, dry-run, rollback, user confirmation (if applicable)        | N/A   | ✓<br>2026-03-09 | N/A      |
| 7.8 Conversation Data Integration | Writes to Rogers directly or via watcher (if applicable)                                   | N/A   | N/A         | N/A      |
| 7.9 Asynchronous Correctness      | No blocking I/O (`time.sleep`) is used; all I/O is `async` and `await`ed                         | N/A   | ✓<br>2026-03-09 | N/A      |
| 7.10 Input Validation             | All data received from external sources is validated before use                                  | N/A   | ✓<br>2026-03-09 | N/A      |
| 7.11 Null/None Checking           | Variables that can be `None` are explicitly checked before their attributes or methods are accessed | N/A   | ✓<br>2026-03-09 | N/A      |

***

## 8. Exceptions and Special Cases

| Requirement                 | Description                                                                     | `starret` | `starret-langgraph` | `github-runner` |
|-----------------------------|---------------------------------------------------------------------------------|---------|-------------------|----------------|
| 8.1 Exception Documentation | Non-compliant items documented in REQ-000-exception-registry with reason, impact, mitigation       | ✓<br>2026-03-09 | ✓<br>2026-03-09 | ✓<br>2026-03-09 |
| 8.2 Exception Approval      | All exceptions approved by Joshua/Aristotle9, documented with approver and date | ✓<br>2026-03-09 | ✓<br>2026-03-09 | ✓<br>2026-03-09 |

***

## N/A Justifications

| Requirement | Container | Reason | Approved By | Date |
|-------------|-----------|--------|-------------|------|
| 1.1 | starret, github-runner | Python is not used in these containers. | J | 2026-03-09 |
| 1.2, 1.3, 1.5, 1.6 | All | Node.js, apt, and external binaries are not used; purely Python + Nginx base images. | J | 2026-03-09 |
| 1.8, 1.9, 1.10 | starret, github-runner | Python code formatting/linting/testing applies only to `starret-langgraph`. | J | 2026-03-09 |
| 2.4 | github-runner | Not custom built via Dockerfile in this repo (external image). | J | 2026-03-09 |
| 2.5 | github-runner | Not custom built via Dockerfile in this repo. | J | 2026-03-09 |
| 2.6 | All | No databases in this MAD group. | J | 2026-03-09 |
| 3.5 | starret, github-runner | Credentials are required only by the langgraph container. | J | 2026-03-09 |
| 3.7 | All | Stateless MAD group. | J | 2026-03-09 |
| 4.1, 4.2 | github-runner | Backing container; does not expose MCP endpoints. | J | 2026-03-09 |
| 4.3 | starret-langgraph, github-runner | Only the gateway exposes tools to the Sam Relay. | J | 2026-03-09 |
| 4.4 | github-runner | Backing container; no MCP tools. | J | 2026-03-09 |
| 4.5, 4.6 | All | Starret is a State 2 MAD using an Nginx reverse proxy instead of a Node.js gateway template. Compliant per REQ-starret §4.3. | J | 2026-03-09 |
| 4.7, 4.9 | starret, github-runner | LangGraph mandate applies only to the `starret-langgraph` container. | J | 2026-03-09 |
| 4.8 | starret-langgraph, github-runner | Thin gateway mandate applies only to the `starret` gateway container. | J | 2026-03-09 |
| 5.2 | github-runner | Not a custom app; uses official GitHub runner logging. | J | 2026-03-09 |
| 5.3, 5.4 | github-runner | No HTTP endpoint or Dockerfile HEALTHCHECK managed in this repo for the official runner image. | J | 2026-03-09 |
| 5.5 | starret, github-runner | Request logging handled inside `starret-langgraph`. | J | 2026-03-09 |
| 5.7, 5.8 | starret, github-runner | App-level log guidelines apply to the Python container. | J | 2026-03-09 |
| 5.10, 5.11, 5.12 | starret, github-runner | Applies only to Python programmatic logic. | J | 2026-03-09 |
| 6.5 | github-runner | Backing container; no MCP tools to document. | J | 2026-03-09 |
| 7.1 | github-runner | Concept applies to the external-facing services in the MAD. | J | 2026-03-09 |
| 7.7, 7.9, 7.10, 7.11 | starret, github-runner | Applies to Python programmatic logic. | J | 2026-03-09 |
| 7.8 | All | Starret does not produce conversation data (per REQ-starret §7.8). | J | 2026-03-09 |

***

## Exception Justifications

| Requirement | Container   | Reason                      | Mitigation        | Exception ID | Approved By | Date |
|-------------|-------------|-----------------------------|-------------------|--------------|-------------|------|
| 3.1 | github-runner | Requires Docker socket to build/push Docker images locally. | Docker socket access limited to isolated starret-net. | EX-STARRET-001 | J | 2026-03-09 |
| 2.2, 2.3 | github-runner | Official `ghcr.io/actions/actions-runner` image breaks if UID/GID 2001 is forced. | Runner isolated on starret-net. | EX-STARRET-002 | J | 2026-03-09 |

***

## Audit Summary

**Total Requirements:** 73 **Passed:** 55 **Failed:** 9 **N/A:** 32 **Exceptions:** 2

**Compliance Status:** Non-Compliant

**Blocker Issues:** 
- 1.1 Python Package Caching: The `mads/starret/starret-langgraph/packages/` folder does not contain any cached `.whl` files (only `pip/` and `download-packages.sh`).
- 1.8 Code Formatting: Fails `black --check .`
- 1.9 Code Linting: Fails `ruff check .` with unused imports (`flows.metrics.record_error`, `httpx`).
- 1.10 Unit Testing: The `pytest` library is not installed in the container environment. Tests cannot be executed.
- 2.4 umask Configuration: `starret` container `start.sh` does not have `umask 000` set.
- 3.3 Workspace Folder Organization: `/workspace/starret/` does not exist on the target host/container.
- 3.5 Credentials Management: `starret-langgraph` fails to load `/storage/credentials/starret/github_token.txt` (file missing).
- 7.3 Independent Container Startup: The `github-runner` container is missing/not deployed on the `irina` host.

**Next Steps:** Implement the remediation plan below and rerun the audit.

***

## Remediation Plan

**Objective:** Bring Starret into full compliance with REQ-000 by fixing build artifacts, formatting, secrets management, and missing containers.

| Requirement | Container | Action Required |
| :--- | :--- | :--- |
| 1.1 | starret-langgraph | Run `download-packages.sh` to populate the `packages/` folder with `.whl` files for offline caching. |
| 1.8 | starret-langgraph | Run `black mads/starret/starret-langgraph/` to format Python files. |
| 1.9 | starret-langgraph | Run `ruff check --fix mads/starret/starret-langgraph/` to remove unused imports. |
| 1.10 | starret-langgraph | Add `pytest` to `requirements.txt` (or a dedicated `requirements-test.txt` / virtualenv) so it can run during builds, and ensure tests pass. |
| 2.4 | starret | Add `umask 000` to the top of `mads/starret/starret/start.sh` before `exec nginx`. |
| 3.3 | starret, starret-langgraph, github-runner | Create `/mnt/storage/workspace/starret/` on the irina host so that volume mappings result in the correct workspace directory existing. |
| 3.5 | starret-langgraph | Provision the GitHub token to `/mnt/storage/credentials/starret/github_token.txt` on the irina host. |
| 7.3 | github-runner | Deploy the `github-runner` container on the `irina` host using `docker compose`. |