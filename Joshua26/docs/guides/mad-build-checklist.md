# pMAD Build Checklist

**Purpose:** Actionable checklist for building a REQ-000-compliant pMAD. Use during implementation and pre-deployment verification.

**Source:** Distilled from [REQ-000](../requirements/REQ-000-Joshua26-System-Requirements-Specification.md). REQ-000 is authoritative if there is any conflict.

---

## 1. Offline-First Build (REQ-000 §1)

- [ ] Python packages sourced from Alexandria devpi (`PIP_INDEX_URL=http://irina:3141/root/pypi/+simple/`), or from local `packages/` in the MAD directory for State 1 containers
- [ ] Node.js packages sourced from Alexandria verdaccio (`NPM_CONFIG_REGISTRY=http://irina:4873`), or from local `packages/` for State 1 containers
- [ ] System packages installed from local mirror or cached `.deb` files
- [ ] Base images pinned to digest (e.g., `python:3.12-slim@sha256:...`)
- [ ] `requirements.txt` / `package.json` versions pinned exactly (no ranges)

## 2. Identity and Permissions (REQ-000 §2)

- [ ] UID/GID assigned in `registry.yml` (UID unique, GID = 2001)
- [ ] Dockerfile: install as root, then `USER [uid]:[gid]` for runtime
- [ ] Service account created: `groupadd -g 2001 administrators && useradd -u [uid] -g 2001 [name]`
- [ ] `umask 000` set in entrypoint or shell profile (Node.js: `process.umask(0o000)`, Python: `os.umask(0o000)`, Supervisord: wrap with `start.sh` — see REQ-000 §2.4)
- [ ] All application files owned by service user: `COPY --chown=[name]:2001` in Dockerfile (not `chown -R` as a separate layer)
- [ ] Post-deployment: `chown -R [uid]:2001` on workspace/storage paths if needed

## 3. Storage and Volumes (REQ-000 §3)

- [ ] Two volumes mounted: `storage:/storage` and `workspace:/workspace`
- [ ] Shared data (models, wheels, certs) → `/storage/`
- [ ] Instance-specific data (databases, logs, state) → `/workspace/[mad-name]/`
- [ ] No secrets in code, config files, or images — use `/storage/creds/` or environment variables
- [ ] Database files under `/workspace/[mad-name]/data/`

## 4. MCP Protocol (REQ-000 §4) — Gateway container only

- [ ] HTTP/SSE transport on port from `registry.yml`
- [ ] `/health` endpoint returns JSON with component status
- [ ] Tool names follow `[domain]_[action]` convention (e.g., `hamilton_query_db`)
- [ ] Gateway uses 4 standard libraries: mcp-protocol-lib, health-aggregator-lib, logging-lib, routing-lib
- [ ] `config.json` defines tools, schemas, and routing targets
- [ ] `server.js` < 20 lines — all routing logic in config.json

## 5. Observability (REQ-000 §5)

- [ ] Logs to stdout/stderr only (no file-based logging)
- [ ] Structured JSON format: `{"timestamp", "level", "message", "service", ...}`
- [ ] `/health` endpoint on every container (gateway, langgraph, backing services)
- [ ] Dockerfile `HEALTHCHECK` instruction present
- [ ] MCP requests logged: tool name, duration, success/failure
- [ ] No secrets or PII in logs

## 6. Documentation (REQ-000 §6)

- [ ] `mads/[mad-name]/docs/REQ-[mad-name].md` — delta requirements (what differs from template)
- [ ] `mads/[mad-name]/README.md` — quick start and tool list
- [ ] `registry.yml` entry — UID, GID, port, host, container names
- [ ] Directory structure follows: `mads/[mad-name]/[mad-name]/`, `mads/[mad-name]/[mad-name]-langgraph/`, etc.
- [ ] Each MCP tool documented with schema, description, examples

## 7. Networking and Deployment (REQ-000 §7)

- [ ] **Private network:** `[mad]-net` defined as bridge network in docker-compose.yml
- [ ] **Gateway** on both `joshua-net` and `[mad]-net`
- [ ] **Langgraph + backing services** on `[mad]-net` only
- [ ] Container names for all communication (never IP addresses)
- [ ] Service defined in master `docker-compose.yml` (not MAD-specific compose files)
- [ ] Build context: `.` (project root); COPY paths: `mads/[mad-name]/...`
- [ ] Host affinity via profiles in per-host override files
- [ ] Graceful degradation: external dependency failures → degraded status, not crash
- [ ] Independent startup: container reaches healthy state without waiting for dependencies

## 8. Exceptions (REQ-000 §8)

- [ ] Any non-compliant items documented in exception registry with reason and mitigation
- [ ] Exceptions approved by architect

---

## Post-Deployment Verification Commands

```bash
# Health check
curl -s http://[mad-name]:PORT/health | jq .

# Container status
ssh aristotle9@[host-ip] docker ps --filter "label=mad.logical_actor=[mad-name]"

# Logs
ssh aristotle9@[host-ip] docker logs [mad-name] --tail 50
ssh aristotle9@[host-ip] docker logs [mad-name]-langgraph --tail 50

# Network isolation verification
ssh aristotle9@[host-ip] docker network inspect [mad-name]-net

# Tool test — direct MCP call (sessionless POST, no SAM required)
curl -s -X POST -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"[tool-name]","arguments":{}},"id":"1"}' \
  http://[mad-name]:PORT/mcp | jq .
```

---

**Related:** [REQ-000](../requirements/REQ-000-Joshua26-System-Requirements-Specification.md) · [Compliance Checklist](../audits/REQ-000-compliance-checklist.md) · [Template README](../../mads/_template/README.md)
