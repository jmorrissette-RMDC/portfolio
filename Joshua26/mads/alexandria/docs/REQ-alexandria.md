# REQ: Alexandria MAD

**Document ID:** REQ-alexandria
**Version:** 1.0
**Date:** 2026-03-08
**Status:** Draft
**Host:** Irina (192.168.1.110)
**Related Documents:** HLD-unified-package-caching.md, HLD-software-factory-core.md, REQ-018-delphi-pypi-mirror.md, REQ-019-pergamum-npm-mirror.md, REQ-022-nineveh-docker-registry.md, REQ-000-exception-registry.md

---

## Purpose

Alexandria is the **Supply Chain Wall** for the Joshua26 ecosystem. It provides self-hosted, transparent caching for all three external dependency types used by the Software Factory:

- **PyPI packages** (via Devpi) — `pip install` from cache
- **NPM packages** (via Verdaccio) — `npm install` from cache
- **Docker images** (via Docker Registry 2.0) — `docker push/pull` from local registry

Alexandria eliminates per-project package duplication, enables offline-capable builds, and gives the ecosystem a single, central artifact store. Without it, every build hits the internet and is subject to outages, rate limits, and slow WAN throughput.

**Scope:** PyPI, NPM, Docker image caching. HuggingFace / ML model caching is owned by **Sutherland** — `HF_ENDPOINT` never points at Alexandria.

---

## Container Group

All five containers are deployed on **irina** only.

| Container | Image | Role | Networks | Host ports |
|-----------|-------|------|----------|------------|
| `alexandria` | nginx:1.27.4-alpine (custom) | MCP gateway only | joshua-net, alexandria-net | — |
| `alexandria-langgraph` | python:3.12-slim (custom) | LangGraph + Imperator + MCP logic | alexandria-net only | — |
| `alexandria-devpi` | python:3.12-slim (custom) | Devpi PyPI cache | alexandria-net only | 3141 (EX-ALEXANDRIA-001) |
| `alexandria-verdaccio` | verdaccio/verdaccio:5.31.1 (official) | Verdaccio NPM cache | alexandria-net only | 4873 (EX-ALEXANDRIA-001) |
| `alexandria-registry` | registry:2.8.3 (official) | Docker Registry 2.0 | alexandria-net only | 5000 (EX-ALEXANDRIA-001) |

**Custom containers:** HLD State 2 Principle 1 states the only custom-built container should be `[mad]-langgraph`. `alexandria` (nginx) and `alexandria-devpi` are additional custom containers. Nginx is justified as the gateway technology required by State 2. Devpi is justified because no official devpi-server Docker image exists — a custom build is the only option. Both cases fall within the HLD's explicit allowance: *"Building a custom container is a rare, explicitly justified decision — only when nothing OTS exists for the purpose."*

**UID:** 2017 (all custom containers share one UID per MAD group)
**GID:** 2001 (administrators)

---

## Network Model

Alexandria serves two distinct traffic types on different ports. This is a deliberate architectural decision, not a compliance gap.

**MCP traffic (joshua-net, NOT host-bound):**
```
Port 9229 — MCP gateway for tool calls and Imperator chat
```

**Cache proxy traffic (host-bound, EX-ALEXANDRIA-001):**
```
Port 3141 — PyPI proxy — exposed DIRECTLY by alexandria-devpi (not nginx)
Port 4873 — NPM proxy — exposed DIRECTLY by alexandria-verdaccio (not nginx)
Port 5000 — Docker registry — exposed DIRECTLY by alexandria-registry (not nginx)
```

pip/npm/docker traffic is raw HTTP — it is **not MCP** and cannot traverse `joshua-net` (MCP-only). Docker build processes run outside any overlay network and cannot resolve container names. The host-bound ports are the only viable mechanism. This is documented in EX-ALEXANDRIA-001.

**Why nginx does NOT proxy cache ports (architectural decision, 2026-03-08):** The original design had nginx proxying ports 3141/4873/5000. This failed because devpi-web (bundled with devpi-server) detects proxy context and returns its HTML web UI instead of the PEP 503 simple index when accessed through an HTTP intermediary. Multiple nginx proxy configurations were attempted; all triggered devpi-web's proxy-awareness. The only correct fix is to have `alexandria-devpi` expose port 3141 directly to the host. The same direct-exposure pattern was applied to verdaccio and registry for consistency. **nginx handles MCP only.**

**nginx configuration (MCP gateway, port 9229 only):**
```nginx
server {
    listen 9229;

    # MCP SSE streaming — buffering must be off or the stream hangs
    location /mcp {
        proxy_pass http://$langgraph/mcp;
        proxy_buffering off;
        proxy_http_version 1.1;
        proxy_set_header Connection '';
        proxy_read_timeout 3600s;
    }

    location /health {
        proxy_pass http://$langgraph/health;
    }

    # Peer proxy — Sutherland for Imperator LLM calls (REQ-000 §4.10)
    location /proxy/sutherland/ {
        proxy_pass http://sutherland:11435/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
    }
}
```

Note: Variable-based upstream (`$langgraph`) with `resolver 127.0.0.11` is used so nginx starts even if `alexandria-langgraph` is not yet healthy.

**Peer dependencies:** `alexandria-langgraph` calls Sutherland for Imperator LLM inference. Per REQ-000 §4.10, all LLM calls route through Sutherland. The call chain is:
```
alexandria-langgraph → POST http://alexandria:9229/proxy/sutherland/mcp  (alexandria-net)
alexandria nginx     → POST http://sutherland:11435/mcp                   (joshua-net)
```

---

## Identity and Permissions

| Container | UID | GID | Notes |
|-----------|-----|-----|-------|
| `alexandria` | 2017 | 2001 | nginx can run non-root (ports >1024) |
| `alexandria-langgraph` | 2017 | 2001 | Full control — custom image |
| `alexandria-devpi` | 2017 | 2001 | Full control — custom image |
| `alexandria-verdaccio` | 10001 (verdaccio) | N/A | EX-ALEXANDRIA-002 — official image |
| `alexandria-registry` | root | N/A | EX-ALEXANDRIA-003 — official image |

---

## Storage

| Path | Owner | Purpose |
|------|-------|---------|
| `/storage/packages/pypi/` | alexandria-devpi | Devpi cache (wheels, sdists, metadata) |
| `/storage/packages/npm/` | alexandria-verdaccio | Verdaccio cache (tarballs) |
| `/storage/images/alexandria-registry/` | alexandria-registry | Docker Registry image layers |
| `/workspace/alexandria/` | alexandria-langgraph | Runtime state (Prometheus registry, etc.) |

**Volume mounts (custom containers):** `storage:/storage` and `workspace:/workspace` per REQ-000 §3.1.

**Official image containers** use bind mounts at their declared VOLUME paths (EX-ALEXANDRIA-004, EX-ALEXANDRIA-005):
- `alexandria-verdaccio`: `/storage/packages/npm:/verdaccio/storage`
- `alexandria-registry`: `/storage/images/alexandria-registry:/var/lib/registry`

---

## MCP Tools

All tools served by `alexandria-langgraph` via the nginx gateway on port 9229.

Tool naming convention: `alex_` domain prefix.

### Direct Tools (Programmatic Flows)

#### `alex_cache_status`
Aggregate status for all three caches.

```json
{
  "input": {},
  "output": {
    "pypi": {
      "package_count": "integer",
      "cache_size_bytes": "integer",
      "cache_size_human": "string",
      "status": "string"
    },
    "npm": {
      "package_count": "integer",
      "cache_size_bytes": "integer",
      "cache_size_human": "string",
      "status": "string"
    },
    "docker": {
      "repository_count": "integer",
      "total_size_bytes": "integer",
      "total_size_human": "string",
      "status": "string"
    }
  }
}
```

#### `alex_warm_pypi`
Pre-warm the PyPI cache from a requirements.txt content string. Downloads packages through Devpi so they are available offline.

```json
{
  "input": {
    "requirements": { "type": "string", "required": true, "description": "Contents of a requirements.txt file" },
    "python_version": { "type": "string", "required": false, "default": "3.12", "description": "Target Python version for wheel selection" }
  },
  "output": {
    "warmed": { "type": "array", "items": "string", "description": "Package names successfully cached" },
    "failed": { "type": "array", "items": "string", "description": "Packages that could not be fetched" }
  }
}
```

#### `alex_warm_npm`
Pre-warm the NPM cache from a package.json content string.

```json
{
  "input": {
    "package_json": { "type": "string", "required": true, "description": "Contents of a package.json file" }
  },
  "output": {
    "warmed": { "type": "array", "items": "string" },
    "failed": { "type": "array", "items": "string" }
  }
}
```

#### `alex_list_packages`
List cached packages for a given cache type.

```json
{
  "input": {
    "cache": { "type": "string", "required": true, "enum": ["pypi", "npm"], "description": "Which cache to list" },
    "search": { "type": "string", "required": false, "description": "Optional substring filter" }
  },
  "output": {
    "packages": {
      "type": "array",
      "items": { "name": "string", "versions": ["string"] }
    }
  }
}
```

#### `alex_registry_list_images`
List all stored Docker image repositories.

```json
{
  "input": {},
  "output": {
    "repositories": { "type": "array", "items": "string" }
  }
}
```

#### `alex_registry_list_tags`
List tags for a Docker image repository.

```json
{
  "input": {
    "image": { "type": "string", "required": true, "description": "Repository name (e.g., 'hopper')" }
  },
  "output": {
    "image": "string",
    "tags": { "type": "array", "items": "string" }
  }
}
```

#### `alex_registry_get_image_info`
Get metadata for a specific image:tag.

```json
{
  "input": {
    "image": { "type": "string", "required": true },
    "tag": { "type": "string", "required": true }
  },
  "output": {
    "image": "string",
    "tag": "string",
    "digest": "string",
    "size_bytes": "integer",
    "size_human": "string",
    "layers": "integer",
    "created": "string (ISO 8601)"
  }
}
```

#### `alex_registry_delete_tag`
Delete a specific image tag. Blocks deletion of `latest`.

```json
{
  "input": {
    "image": { "type": "string", "required": true },
    "tag": { "type": "string", "required": true }
  },
  "output": {
    "success": "boolean",
    "deleted": { "image": "string", "tag": "string" }
  },
  "errors": {
    "latest_protected": "Cannot delete the 'latest' tag",
    "not_found": "Image or tag does not exist"
  }
}
```

#### `alex_registry_storage_stats`
Docker registry storage usage.

```json
{
  "input": {},
  "output": {
    "total_size_bytes": "integer",
    "total_size_human": "string",
    "repository_count": "integer",
    "tag_count": "integer"
  }
}
```

#### `metrics_get`
Prometheus metrics in exposition format. Required by REQ-000 §4.11. Implemented as a compiled LangGraph StateGraph — the route handler calls `_metrics_graph.ainvoke(state)`, a graph node generates the metrics text. See `docs/guides/mad-prometheus-metrics-guide.md`.

```json
{
  "input": {},
  "output": {
    "metrics": { "type": "string", "description": "Prometheus exposition format text" }
  }
}
```

**Standard metrics exposed:** `mcp_requests_total`, `mcp_request_duration_seconds`, `mcp_requests_errors_total` with labels `mad=alexandria`, `tool`, `error_type`.

### Imperator Tool

#### `alex_imperator_chat`
Multi-step cache operations requiring judgment. Examples: "pre-warm the cache for this new service given its requirements.txt and package.json", "diagnose why this package isn't being served from cache", "clean up Docker images older than 30 days keeping latest tags".

```json
{
  "input": {
    "message": { "type": "string", "required": true },
    "session_id": { "type": "string", "required": false }
  },
  "output": {
    "response": "string",
    "session_id": "string"
  }
}
```

---

## LangGraph Flows

All logic in `alexandria-langgraph` is implemented as LangGraph StateGraphs per REQ-000 §4.7.

| Flow | File | Tools served | Type |
|------|------|-------------|------|
| cache_ops | `flows/cache_ops.py` | alex_cache_status, alex_warm_pypi, alex_warm_npm, alex_list_packages | Programmatic |
| registry_ops | `flows/registry_ops.py` | alex_registry_* (5 tools) | Programmatic |
| metrics | `flows/metrics.py` | metrics_get | Programmatic |
| imperator | `flows/imperator.py` | alex_imperator_chat | Cognitive (ReAct) |

`registry_ops` calls the Docker Registry HTTP API (`http://alexandria-registry:5000/v2/`) via httpx. No direct Docker daemon access required.

---

## Backing Service Specifications

Backing service configuration details are embedded in this document. REQ-018, REQ-019, and REQ-022 have been archived — REQ-alexandria.md is the authoritative specification.

---

## Client Configuration (Post-Deployment)

After Alexandria is deployed, update all base images and Docker daemons:

**Python base images:**
```dockerfile
ENV PIP_INDEX_URL=http://irina:3141/root/pypi/+simple/
ENV PIP_TRUSTED_HOST=irina
```

**Node.js base images:**
```dockerfile
ENV NPM_CONFIG_REGISTRY=http://irina:4873
```

**Docker daemon on all three hosts (irina, m5, hymie):**
```json
{ "insecure-registries": ["irina:5000"] }
```
Restart Docker daemon after adding insecure-registries.

**CI/CD (Starret runner) image push:**
```bash
docker tag my-image:latest irina:5000/my-image:latest
docker push irina:5000/my-image:latest
```

---

## Devpi Initialization (One-Time, Auto-Detected)

The `alexandria-devpi` entrypoint must detect whether the server directory has been initialized and run `devpi-server --init` automatically if not. It must never require manual intervention on first run. This is required by REQ-000 §7.3 — the container must reach a healthy state independently without operator action.

```bash
# entrypoint logic (pseudocode)
if [ ! -f /storage/packages/pypi/.serverversion ]; then
    devpi-server --init --serverdir /storage/packages/pypi
fi
exec devpi-server --host 0.0.0.0 --port 3141 --serverdir /storage/packages/pypi
```

---

## Runtime Configuration

Verdaccio and Nineveh require config files that must **not** live in the repository. They belong in the workspace, which is local to irina and already mounted on every container.

| Service | Config path in workspace |
|---------|--------------------------|
| `alexandria-verdaccio` | `/workspace/alexandria/config/verdaccio/config.yaml` |
| `alexandria-registry` | `/workspace/alexandria/config/registry/config.yml` |

Both containers are pointed at these paths via command override — no extra bind mounts, no repo files:

```yaml
alexandria-verdaccio:
  command: verdaccio --config /workspace/alexandria/config/verdaccio/config.yaml

alexandria-registry:
  command: /entrypoint.sh /workspace/alexandria/config/registry/config.yml
```

The deployment step creates these files in workspace before the containers start. Template versions live in `mads/alexandria/config-templates/` for reference only.

## umask

All custom containers (`alexandria`, `alexandria-langgraph`, `alexandria-devpi`) must set `umask 000` per REQ-000 §2.4:

- `alexandria-langgraph` and `alexandria-devpi`: `os.umask(0o000)` at the top of the entry point, before any imports
- `alexandria` (nginx): set via `start.sh` wrapper: `umask 000 && exec nginx -g 'daemon off;'`

Official image containers (`alexandria-verdaccio`, `alexandria-registry`) are exempt — EX-ALEXANDRIA-002, EX-ALEXANDRIA-003.

## Health Aggregation

Per REQ-000 §5.9, the `/health` endpoint must actively test all dependencies and return an aggregated status. In State 2, nginx proxies `/health` to `alexandria-langgraph:8000/health`. Therefore `alexandria-langgraph` is responsible for implementing the aggregated health check.

The health endpoint in `alexandria-langgraph` must test:

| Dependency | Check |
|------------|-------|
| `alexandria-devpi` | `GET http://alexandria-devpi:3141/+api/` returns 200 |
| `alexandria-verdaccio` | `GET http://alexandria-verdaccio:4873/-/ping` returns 200 |
| `alexandria-registry` | `GET http://alexandria-registry:5000/v2/` returns 200 or 401 |

Response format:
```json
{
  "status": "healthy|degraded|unhealthy",
  "devpi": "ok|unreachable",
  "verdaccio": "ok|unreachable",
  "registry": "ok|unreachable"
}
```

All three are hard dependencies — if any are unreachable, status is `degraded`. The langgraph container itself being up is the gateway's Docker HEALTHCHECK concern.

## Bootstrap Problem

Alexandria cannot use itself during its own build. The langgraph and delphi containers depend on Python packages that would normally be fetched from Alexandria. Before the first build, wheels must be pre-downloaded directly on irina:

```bash
# LangGraph container wheels
pip download quart httpx langgraph langchain-core prometheus-client \
  -d mads/alexandria/alexandria-langgraph/packages/ \
  --platform linux_x86_64 --python-version 3.12 --only-binary=:all:

# Delphi container wheels
pip download devpi-server \
  -d mads/alexandria/alexandria-devpi/packages/ \
  --platform linux_x86_64 --python-version 3.12 --only-binary=:all:
```

After Alexandria is deployed, all subsequent builds use it.

---

## Exceptions

| Exception | Container | Requirement | See |
|-----------|-----------|-------------|-----|
| EX-ALEXANDRIA-001 | `alexandria` (nginx) | §7.4.1 Per-MAD Private Networks | Host-bound ports required for non-MCP traffic |
| EX-ALEXANDRIA-002 | `alexandria-verdaccio` | §2.2, §2.3, §2.4 Identity | Official verdaccio/verdaccio image |
| EX-ALEXANDRIA-003 | `alexandria-registry` | §2.2, §2.3, §2.4 Identity | Official registry:2 image |
| EX-ALEXANDRIA-004 | `alexandria-verdaccio` | §3.1 Two-Volume Policy | VOLUME /verdaccio/storage — bind mount required |
| EX-ALEXANDRIA-005 | `alexandria-registry` | §3.1 Two-Volume Policy | VOLUME /var/lib/registry — bind mount required |
| EX-ALEXANDRIA-006 | `alexandria-verdaccio` | §5.2 Structured Logging | Verdaccio native log format |
| EX-ALEXANDRIA-007 | `alexandria-registry` | §5.2 Structured Logging | Registry 2.0 Go-style logs |
| EX-ALEXANDRIA-008 | `alexandria` (nginx) | §5.2 Structured Logging | nginx:alpine error_log is plain text — no native JSON support without forking |

All seven exceptions are registered in `docs/requirements/REQ-000-exception-registry.md`.

---

## Verification

| Check | Command |
|-------|---------|
| MCP health | `curl http://irina:9229/health` |
| PyPI proxy | `pip install --index-url http://irina:3141/root/pypi/+simple/ requests` |
| NPM proxy | `npm install --registry http://irina:4873 express` |
| Docker push | `docker tag hello-world irina:5000/test:latest && docker push irina:5000/test:latest` |
| Docker pull | `docker pull irina:5000/test:latest` |
| MCP tool | `curl -X POST http://irina:9229/mcp -d '{"method":"tools/call","params":{"name":"alex_cache_status"}}'` |
| Metrics | `curl http://irina:9229/metrics_get` |

---

*Version: 1.0 | Created: 2026-03-08 | Status: Draft*
