# REQ-000 Exception Registry

**Document ID:** REQ-000-exception-registry
**Version:** 1.0
**Date:** [YYYY-MM-DD]
**Status:** Active

---

## Purpose

This registry tracks all approved exceptions to REQ-000 System Requirements Specification across the Joshua26 ecosystem.

**Exception vs N/A:**
- **Exception (EX):** Component cannot comply with requirement, needs formal approval and mitigation
- **N/A:** Requirement does not apply to component (e.g., Python requirements for Node.js-only container)

---

## Active Exceptions

| Exception ID | MAD/Component | Requirement | Reason | Mitigation | Approved By | Date | Status |
|--------------|---------------|-------------|--------|------------|-------------|------|--------|
| EX-POSTGRES-001 | template-postgres (all postgres containers) | 3.1 Two-Volume Mounting Policy | Official postgres image declares VOLUME /var/lib/postgresql/data; suppressing anonymous volume creation requires a bind mount at that exact path, replacing the workspace named volume | Bind mount at /var/lib/postgresql/data points to host NVMe path; data is persistent, inspectable, and backed up per ADR-052 | J | 2026-02-19 | Active |
| EX-NEO4J-001 | All neo4j containers (e.g. rogers-neo4j) | 3.1 Two-Volume Mounting Policy | Official neo4j image declares VOLUME /data and VOLUME /logs; suppressing anonymous volume creation requires bind mounts at both paths, replacing the workspace named volume | Bind mounts at /data and /logs point to host NVMe paths; data is persistent and inspectable per ADR-052 | J | 2026-02-20 | Active |
| EX-REDIS-001 | All redis containers (e.g. rogers-redis) | 3.1 Two-Volume Mounting Policy | Official redis image declares VOLUME /data; suppressing anonymous volume creation requires a bind mount at that exact path, replacing the workspace named volume | Bind mount at /data points to host NVMe path; data is persistent and inspectable per ADR-052 | J | 2026-02-20 | Active |
| EX-ROGERS-001 | rogers-postgres, rogers-neo4j, rogers-redis | 2.2 Service Account Creation, 2.3 Group Membership, 2.4 umask Configuration | Official postgres/neo4j/redis images run as their own native users (postgres/neo4j/redis). UID 2002/GID 2001/umask cannot be applied without forking the images. Entrypoint scripts depend on native users for data directory setup. | Containers isolated on rogers-net only — no direct external access. Database data directories protected by host-level permissions (chmod 750 per §2.6). | J | 2026-02-21 | Active |
| EX-ROGERS-002 | rogers-postgres, rogers-neo4j, rogers-redis | 5.2 Structured Logging Format | Official postgres/neo4j/redis images emit native log formats (SQL logs, neo4j logs, redis logs), not JSON. Cannot be changed without forking the images. | All container logs reach Docker stdout/stderr and are available via docker logs. JSON normalization deferred to future log aggregation layer. | J | 2026-02-21 | Active |
| EX-SAM-001 | sam | 3.1 Two-Volume Mounting Policy | Sam only needs workspace volume (not storage), has no network-shared data needing storage mount | Config stored in /workspace/sam-[host]/backends.yaml (local to each host) | J | 2026-02-01 | Active |
| EX-SAM-002 | sam | 4.1 MCP Transport Protocol | Sam supports DUAL transport: stdio (local Claude Code) AND HTTP/SSE (remote clients), not deprecating stdio | Stdio transport for local use, HTTP/SSE transport for remote clients. Both remain functional and supported. | J | 2026-02-01 | Active |
| EX-SAM-003 | sam | 4.5 MCP Gateway Template Usage | Sam is custom relay implementation, not template-based MCP Gateway | Well-tested relay logic, follows MCP protocol spec | J | 2026-02-01 | Active |
| EX-SAM-004 | sam | 4.6 Configuration File Requirements | Sam uses backends.yaml instead of config.json | backends.yaml is schema-validated, registry sync tool ensures validity | J | 2026-02-01 | Active |
| EX-SAM-005 | sam | 5.5 MCP Request Logging | Sam has custom logging, not using mcp-protocol-lib | Logging covers all MCP operations, includes request/response data | J | 2026-02-01 | Active |
| EX-SAM-006 | sam | 7.2 MAD Group Boundaries | Sam has no MAD group (is a standalone relay with no backing services) | Sam IS the infrastructure, all backends are "external" | J | 2026-02-01 | Active |
| EX-HENSON-005 | mcp-protocol-lib (henson gateway) | 4.8 Thin Gateway Mandate | `/stream/{peer}/{apiPath}` SSE pipe transport route added to shared gateway library for Gunner streaming. Transport infrastructure alongside existing peer proxy and ui_proxy patterns. | Route is now config-gated — only active when at least one peer declares `openai_port` in config.json. Governed by config, not hardcoded. Follows same pattern as ui_proxy (config-enabled) and peer proxy (config-declared peers). | J | 2026-02-26 | Active |
| EX-SUTHERLAND-001 | sutherland-postgres | 2.2 Service Account Creation, 2.3 Group Membership, 2.4 umask Configuration | Official postgres:16-alpine image entrypoint requires root to run chown on PGDATA and /var/run/postgresql before exec-ing the postgres process. Setting user: overrides this and breaks initialisation. Same constraint as EX-ROGERS-001. | Container isolated on sutherland-net only. PGDATA on host NVMe protected by host-level permissions. | J | 2026-02-28 | Active |
| EX-SUTHERLAND-002 | sutherland-vllm | 2.2 Service Account Creation, 2.3 Group Membership, 2.4 umask Configuration | vLLM/PyTorch TorchInductor calls getpass.getuser() → pwd.getpwuid(uid) at startup to construct its compile cache path. UID 2007 has no /etc/passwd entry in the vllm/vllm-openai image; the call raises KeyError and vLLM crashes. Cannot add a passwd entry without forking the image. | Container isolated on sutherland-net only. No direct external access. | J | 2026-02-28 | Active |
| EX-SUTHERLAND-003 | sutherland-postgres, sutherland-vllm, sutherland-llamacpp-imperator, sutherland-llamacpp-agent-small | 5.2 Structured Logging Format | Official postgres:16-alpine, vllm/vllm-openai, and ollama/ollama images emit native log formats (PostgreSQL log lines, uvicorn access logs, GIN HTTP logs), not JSON. Cannot be changed without forking the images. Same constraint as EX-ROGERS-002. | All container logs reach Docker stdout/stderr and are available via docker logs. JSON normalization deferred to future log aggregation layer. | J | 2026-02-28 | Active |

| EX-ALEXANDRIA-001 | alexandria (nginx gateway) | 7.4.1 Per-MAD Private Networks | pip/npm/docker traffic is raw HTTP — not MCP. joshua-net is MCP-only. Docker build processes and docker push/pull commands run outside any overlay network and cannot reach joshua-net container names. Alexandria must expose cache proxy ports (3141, 4873, 5000) host-bound on backing service containers. MCP port 9229 is host-bound on the nginx gateway following the same pattern as rogers:6380. | Cache proxy ports (3141/4873/5000) are host-bound on backing service containers only. MCP port 9229 is host-bound on the nginx gateway (same pattern as rogers:6380). All ports restricted to LAN (x.x.x.0/24). | J | 2026-03-08 | Active |
| EX-ALEXANDRIA-002 | alexandria-verdaccio | 2.2 Service Account Creation, 2.3 Group Membership, 2.4 umask Configuration | Official verdaccio/verdaccio image runs as verdaccio user (UID 10001). Cannot apply UID 2017 / GID 2001 without forking the image. Same constraint as EX-ROGERS-001. | Container isolated on alexandria-net only — no direct external access. | J | 2026-03-08 | Active |
| EX-ALEXANDRIA-003 | alexandria-registry | 2.2 Service Account Creation, 2.3 Group Membership, 2.4 umask Configuration | Official registry:2 image runs as root internally. Cannot apply UID 2017 / GID 2001 without forking. Same constraint as EX-ROGERS-001. | Container isolated on alexandria-net only — no direct external access. | J | 2026-03-08 | Active |
| EX-ALEXANDRIA-004 | alexandria-verdaccio | 3.1 Two-Volume Mounting Policy | Official verdaccio/verdaccio image declares VOLUME /verdaccio/storage. Must use bind mount at that path to suppress anonymous volume creation. Same constraint as EX-POSTGRES-001. | Bind mount /storage/packages/npm → /verdaccio/storage. Data persistent and inspectable. | J | 2026-03-08 | Active |
| EX-ALEXANDRIA-005 | alexandria-registry | 3.1 Two-Volume Mounting Policy | Official registry:2 image declares VOLUME /var/lib/registry. Must use bind mount at that path. Same constraint as EX-POSTGRES-001. | Bind mount /storage/images/alexandria-registry → /var/lib/registry. Data persistent and inspectable. | J | 2026-03-08 | Active |
| EX-ALEXANDRIA-006 | alexandria-verdaccio | 5.2 Structured Logging Format | Official verdaccio/verdaccio emits native Verdaccio log format, not structured JSON. Cannot change without forking. Same constraint as EX-ROGERS-002. | Logs available via docker logs. JSON normalization deferred to future log aggregation layer. | J | 2026-03-08 | Active |
| EX-ALEXANDRIA-007 | alexandria-registry | 5.2 Structured Logging Format | Official registry:2 emits Go-style log lines, not JSON. Same constraint as EX-ROGERS-002. | Logs available via docker logs. JSON normalization deferred to future log aggregation layer. | J | 2026-03-08 | Active |
| EX-ALEXANDRIA-008 | alexandria (nginx) | 5.2 Structured Logging Format | nginx:alpine error_log emits plain text, not structured JSON. Access log is disabled (access_log off). nginx does not support native JSON log formatting without a third-party module. Cannot change without forking the image. Same constraint as EX-ROGERS-002. | Error logs available via docker logs. MCP request logging handled by alexandria-langgraph (structured JSON). | J | 2026-03-08 | Active |
| EX-ALEXANDRIA-009 | alexandria (nginx) + alexandria-langgraph | 5.5 MCP Request Logging | §5.5 specifies mcp-protocol-lib (Node.js) for automatic MCP request logging. Alexandria is a State 2 pMAD using nginx + FastMCP (Python). mcp-protocol-lib is a State 1 Node.js library and does not apply to State 2. Manual structured JSON logging is implemented per-tool in server.py via _log_mcp_request(). | Per-tool structured JSON logging covers all 11 MCP tools. Logs include tool name and timestamp. | J | 2026-03-08 | Active |

| EX-KAISER-001 | kaiser-langgraph | 1.1 Python Package Caching (build-time) + 1.1 runtime | Kaiser installs Python packages from Alexandria (internal PyPI at irina:3141) at both build time (network: host) and runtime (kaiser_install_package). This is the defining capability of State 3 pMAD architecture — runtime eMAD installation without rebuild. Alexandria IS the ecosystem offline cache; no external network is accessed. | Alexandria must be healthy for runtime installs. Build-time uses network: host with direct irina access. kaiser_chat and all registry tools continue without Alexandria. | J | 2026-03-11 | Active |
| EX-KAISER-002 | kaiser-postgres | 3.1 Two-Volume Mounting Policy + 2.6 Post-Deployment Permissions | Official postgres:16-alpine declares VOLUME /var/lib/postgresql/data; suppressing anonymous volume creation requires a bind mount at that exact path. Same constraint as EX-POSTGRES-001. During postgres initialization, the entrypoint chowns PGDATA to the postgres user (UID 70) and sets permissions to 700 (drwx------). Postgres refuses to start if PGDATA has wider permissions — 700 is postgres's own security requirement, identical to how rogers-postgres and sutherland-postgres are deployed. §2.6 mandates 750/640 but postgres requires 700 for its data directory. | Bind mount at /var/lib/postgresql/data points to /mnt/nvme/workspace/kaiser/databases/postgres/data on M5. Data persistent and inspectable per ADR-052. Container isolated on kaiser-net only (no direct external access). Same pattern as EX-POSTGRES-001 across all postgres-backed MADs. | J | 2026-03-11 | Active |
| EX-KAISER-003 | kaiser-postgres | 2.1 Root Usage, 2.2 Service Account, 2.3 Group Membership | Official postgres:16-alpine entrypoint requires root to run chown on PGDATA and /var/run/postgresql before exec-ing the postgres process. Setting USER directive breaks initialisation. Same constraint as EX-ROGERS-001 and EX-SUTHERLAND-001. | Container isolated on kaiser-net only — no direct external access. PGDATA on host NVMe protected by host-level permissions (chmod 750 applied at deployment). | J | 2026-03-11 | Active |
| EX-KAISER-004 | kaiser (nginx gateway) | 4.5 MCP Gateway Template Usage + 4.6 Configuration File Requirements | Kaiser is a State 3 pMAD using nginx:alpine as its gateway, not the State 1 Node.js template. State 2/3 explicitly mandates nginx:alpine as the gateway. mcp-protocol-lib and config.json tool routing are State 1 patterns. All MCP tool routing is in kaiser-langgraph (FastMCP). Same architectural basis as EX-ALEXANDRIA-009. | nginx proxies /mcp, /health, /metrics, /peer/*, /pypi/ to kaiser-langgraph. FastMCP exposes all tools at /mcp with full tool routing. Functionally equivalent to State 1 gateway pattern. | J | 2026-03-11 | Active |
| EX-KAISER-005 | kaiser (nginx) | 5.2 Structured Logging Format | nginx:alpine error_log emits plain text, not structured JSON. Access log is disabled (access_log off). nginx does not support native JSON formatting without a third-party module. Same constraint as EX-ALEXANDRIA-008. | Error logs available via docker logs. MCP request logging handled by kaiser-langgraph (structured JSON) via _log_mcp() per tool. | J | 2026-03-11 | Active |
| EX-KAISER-008 | kaiser (nginx) + kaiser-langgraph | 5.5 MCP Request Logging | §5.5 specifies mcp-protocol-lib (Node.js) for automatic MCP request logging. Kaiser is a State 3 MAD using nginx + FastMCP (Python). mcp-protocol-lib is a State 1 Node.js library and does not apply to State 2/3. Manual structured JSON logging is implemented per-tool in server.py via _log_mcp(). Same architectural basis as EX-ALEXANDRIA-009. | Per-tool structured JSON logging covers all 7 MCP tools. Logs include tool name and timestamp. | J | 2026-03-11 | Active |
| EX-KAISER-007 | kaiser-postgres | 5.2 Structured Logging Format | Official postgres:16-alpine emits native PostgreSQL log format, not structured JSON. Cannot be changed without forking the image. Same constraint as EX-ROGERS-002 and EX-SUTHERLAND-003. | All container logs reach Docker stdout/stderr and are available via docker logs. JSON normalization deferred to future log aggregation layer. | J | 2026-03-11 | Active |
| EX-KAISER-006 | kaiser-langgraph | 1.10 Unit Testing Mandate | No pytest unit tests written for Kaiser's programmatic flows. Kaiser is a novel State 3 architecture requiring integration testing against running Alexandria, postgres, and Sutherland — not easily unit-testable in isolation. | Deferred per operator decision. End-to-end testing performed via MCP tool calls against the live system during Gate 3. | J | 2026-03-11 | Active |
| EX-STARRET-001 | github-runner | 3.1 Two-Volume Mounting Policy | GitHub Actions runner requires /var/run/docker.sock to build Docker images locally before pushing to Alexandria registry. This is a raw host path mount, not a named volume. REQ-023 §FR-02 explicitly requires Docker socket access for the runner. No alternative exists — docker buildx and docker push require the daemon socket. | Runner isolated on starret-net only (no joshua-net). Docker socket access limited to build/push operations by workflow definition. Workflow files are code-reviewed before merge (enforced by Starret Imperator branch protection). | J | 2026-03-09 | Active |
| EX-STARRET-002 | github-runner | 2.2 Service Account Creation, 2.3 Group Membership | Official ghcr.io/actions/actions-runner image runs as its own internal runner user (UID 1001). Applying user: 2001:2001 breaks the runner's entrypoint and registration flow. Cannot be changed without forking the image. Same constraint as EX-ROGERS-001. | Runner isolated on starret-net only. No direct external access. Runner workspace at /workspace/starret/_work is owned by the runner user on the host filesystem. | J | 2026-03-09 | Active |

---

## Resolved Exceptions

| Exception ID | MAD/Component | Requirement | Reason | Resolution | Resolved By | Date |
|--------------|---------------|-------------|--------|------------|-------------|------|
| | | | | | | |

---

## Exception Request Template

**Exception ID:** EX-[###]
**MAD/Component:** [mad-name]
**Container:** [container-name]
**Requirement:** [requirement-id]
**Reason:** [Detailed explanation why compliance is impossible]
**Impact:** [What risks does this create]
**Mitigation:** [How risks are reduced]
**Requested By:** [Name]
**Date:** [YYYY-MM-DD]

**Approval:**
- [ ] Approved by Joshua/Aristotle9
- [ ] Date: [YYYY-MM-DD]
- [ ] Added to Active Exceptions table
