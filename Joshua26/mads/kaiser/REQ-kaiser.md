# REQ-kaiser: Kaiser MAD — Delta Requirements

**Version:** 0.5 (revised post Gate 1 run 2)
**Date:** 2026-03-11
**Status:** Draft — pending Gate 1 re-run

This document is a delta REQ. It describes only what differs from the standard MAD template
baseline (`mads/_template/docs/REQ-langgraph-template.md`). All template defaults apply unless
explicitly overridden here.

---

## 1. Purpose

Kaiser is the dedicated eMAD hosting MAD and the first **State 3 MAD** in the Joshua26
ecosystem. Its domain is the lifecycle, configuration, and execution of subject-domain eMADs.

An eMAD (Ephemeral Multipurpose Agentic Duo) is a subject-domain agent with an MCP endpoint but
no infrastructure of its own. It exists only during the execution of its StateGraph. Kaiser
provides the infrastructure that eMADs would otherwise lack: a gateway, a runtime, and a
registry.

**eMAD libraries** are Python packages published to Alexandria (the internal PyPI). Installing a
package makes its `build_graph(params)` function available. **eMAD instances** are named,
parameterised registrations stored in Kaiser's postgres: a name, a package, and a structured
parameter dict. The same package can be instantiated many times under different names with
different parameters — giving different behaviours without different code.

Kaiser's **Imperator** manages the eMAD lifecycle: advising on parameterisation, reasoning about
capabilities, and handling management operations. Kaiser's **programmatic flows** handle dispatch:
looking up a named instance, building its graph, invoking it, and returning the response.

**State 3** separates infrastructure from intelligence. See `docs/concepts/concept-state3-mad.md`
for the full pattern.

---

## 2. Registry Allocation

| Field | Value |
|---|---|
| Name | kaiser |
| UID | 2036 |
| GID | 2001 (administrators) |
| Port | 9226 |
| Host | m5 |

---

## 3. MCP Interface

All tool names follow the `kaiser_[action]` convention. All tools are served by
`kaiser-langgraph` via FastMCP (`mcp.http_app(stateless_http=True)`) at `/mcp`. The nginx
gateway proxies `/mcp` to `kaiser-langgraph:8000/mcp` — no tool routing in the gateway.

### 3.1 `kaiser_chat`

**Purpose:** Send a message to a named eMAD instance and receive a response. Looks up the
instance in postgres to get its package and parameters, invokes `build_graph(params)` from the
installed package, runs the StateGraph, and returns the response directly. Synchronous.

**Inputs:**
- `emad_name` (string, required) — registered instance name (e.g., `hopper`,
  `software_engineer_tester`)
- `conversation_id` (string, required) — passed to the eMAD for Rogers context continuity
- `message` (string, required) — message content

**Output:**
```json
{
  "response": "string",
  "conversation_id": "string",
  "emad_name": "string"
}
```

**Error cases:** instance not found, package not installed, StateGraph execution failure.

---

### 3.2 `kaiser_list_emads`

**Purpose:** List all registered eMAD instances with their package, parameters, and status.

**Inputs:** None

**Output:**
```json
{
  "emads": [
    {
      "emad_name": "string",
      "package_name": "string",
      "description": "string",
      "parameters": {},
      "status": "available | error"
    }
  ]
}
```

---

### 3.3 `kaiser_install_package`

**Purpose:** Install an eMAD package from Alexandria into the running Kaiser instance. Makes the
package's `build_graph` function available for instance registration. Does not create any
instances — use `kaiser_create_emad` after installation.

**Inputs:**
- `package_name` (string, required) — PyPI package name on Alexandria (e.g., `hopper-emad`)
- `version` (string, optional) — specific version; defaults to latest

**Output:**
```json
{
  "status": "installed | already_installed | error",
  "package_name": "string",
  "version": "string"
}
```

---

### 3.4 `kaiser_create_emad`

**Purpose:** Register a new named eMAD instance backed by an installed package with a given
parameter set. Creates a row in the `emad_instances` table.

**Inputs:**
- `emad_name` (string, required) — unique name for this instance
- `package_name` (string, required) — must already be installed
- `description` (string, required) — human-readable description
- `parameters` (object, optional) — parameter dict passed to `build_graph(params)`;
  defaults to `{}`

**Output:**
```json
{ "status": "created", "emad_name": "string" }
```

**Error cases:** `emad_name` already exists, `package_name` not installed.

---

### 3.5 `kaiser_update_emad`

**Purpose:** Update the parameters or description of an existing eMAD instance. Takes effect
immediately on the next `kaiser_chat` call — no restart required.

**Inputs:**
- `emad_name` (string, required)
- `description` (string, optional)
- `parameters` (object, optional) — replaces entire parameter dict if provided

**Output:**
```json
{ "status": "updated", "emad_name": "string" }
```

---

### 3.6 `kaiser_delete_emad`

**Purpose:** Remove a named eMAD instance from the registry. Does not uninstall the underlying
package — other instances using the same package are unaffected.

**Inputs:**
- `emad_name` (string, required)

**Output:**
```json
{ "status": "deleted", "emad_name": "string" }
```

---

### 3.7 `kaiser_imperator_chat`

**Purpose:** Converse with Kaiser's Imperator. The Imperator handles management-plane reasoning:
advising on eMAD parameterisation, recommending which eMAD to use for a given task, explaining
installed capabilities, and managing instance lifecycle via its internal toolset.

**Inputs:**
- `message` (string, required)
- `conversation_id` (string, optional) — for multi-turn management conversations

**Output:**
```json
{ "response": "string", "conversation_id": "string" }
```

---

### 3.8 `metrics_get`

**Purpose:** Return Prometheus-format metrics for kaiser-langgraph. Standard observability tool
required by REQ-000 §4.11 and consumed by Apgar.

**Inputs:** None

**Output:** `{ "metrics": "string" }` — Prometheus exposition format text.

Metrics exposed: request counts and latencies per tool, eMAD invocation counts and latencies
per emad_name, active eMAD instance count, installed package count, error counts.

The `/metrics` endpoint (Prometheus scrape target) is also exposed on `kaiser-langgraph:8000`.

---

## 4. Dependencies

### 4.1 Rogers (critical for eMADs)

All eMAD conversations store context in Rogers. eMAD StateGraphs call Rogers via the peer proxy.
Kaiser's health degrades (not fails) if Rogers is unreachable — dispatch continues; eMADs degrade
per their own strategy.

### 4.2 Sutherland (critical for Imperator; per-eMAD for dispatch)

Kaiser's Imperator calls Sutherland for inference. eMAD StateGraphs also call Sutherland via
the peer proxy for their own inference.

### 4.3 Alexandria (required for `kaiser_install_package`)

Required for runtime package installation only. All other tools function without Alexandria.
Accessed by `kaiser-langgraph` via the nginx PyPI proxy (see §6.3).

### 4.4 Other MADs (per-eMAD)

eMADs may call Starret, Horace, or other MADs via the peer proxy. Kaiser declares all expected
eMAD peer dependencies in nginx.conf.

---

## 5. Container List

| Container | Role | Notes |
|---|---|---|
| `kaiser` | Gateway | nginx:alpine; bridges joshua-net + kaiser-net |
| `kaiser-langgraph` | Runtime + Imperator | FastMCP + Starlette + Hypercorn; asyncpg; kaiser-net only |
| `kaiser-postgres` | eMAD registry | Stores installed packages + named instances + parameters |

**No Redis for Phase 1.** asyncio handles concurrent dispatch natively (see §6.1).

**Phase 2 (deferred):** `kaiser-redis` queue + `kaiser-langgraph-worker` pool for distributed
multi-host execution.

---

## 6. Architectural Notes

### 6.1 Concurrency Without a Queue

eMAD StateGraphs are I/O bound (inference to Sutherland, state to Rogers). Python asyncio
handles multiple concurrent `ainvoke` calls natively. `kaiser-langgraph` uses Starlette (via
FastMCP) with Hypercorn as the ASGI server. A Redis queue adds value only when workers must be
distributed across separate physical hosts — not needed for Phase 1.

### 6.2 Gateway — nginx (State 2 Pattern)

`kaiser` is a standard nginx:alpine gateway. All MCP logic lives in `kaiser-langgraph` via
FastMCP — the gateway does not perform tool routing. nginx location blocks:

- `location /mcp` → `proxy_pass http://kaiser-langgraph:8000/mcp`
- `location /health` → `proxy_pass http://kaiser-langgraph:8000/health`
- `location /metrics` → `proxy_pass http://kaiser-langgraph:8000/metrics`
- `location /peer/{peer}/{tool}` → standard peer proxy pattern (ADR-053)
- `location /pypi/` → `proxy_pass http://irina:3141/` (PyPI proxy — see §6.3)

`kaiser-langgraph` serves all MCP tools via FastMCP (`mcp.http_app(stateless_http=True)`).
Health aggregation (postgres, Rogers reachability) is implemented in the langgraph `/health`
endpoint; nginx proxies it through.

### 6.3 Alexandria Access via nginx PyPI Proxy

`kaiser-langgraph` resides on `kaiser-net` only and cannot reach `irina:3141` directly. For
runtime pip installs, the kaiser nginx gateway proxies PyPI traffic:

```
kaiser-langgraph → http://kaiser:9226/pypi/ → nginx → http://irina:3141/
```

`kaiser-langgraph` sets:
```
PIP_INDEX_URL=http://kaiser:9226/pypi/root/pypi/+simple/
PIP_TRUSTED_HOST=kaiser
```

This keeps `kaiser-langgraph` on `kaiser-net` only while satisfying the network isolation
requirement.

### 6.4 Dynamic eMAD Loading (State 3 Pattern)

**Package layer (Python entry_points):**
eMAD packages declare their `build_graph` function via `pyproject.toml`:
```toml
[project.entry-points."kaiser.emads"]
hopper = "hopper_emad.register:build_graph"
```
Kaiser scans `kaiser.emads` entry_points at startup and after each `kaiser_install_package`
call. The install flow calls `importlib.invalidate_caches()` before rescanning to ensure newly
installed packages are reliably detected without restart.

**Instance layer (postgres):**
Named instances in `emad_instances` map `emad_name → package_name + parameters`. Multiple
instances can share one package with different parameter dicts.

**Dispatch:**
`kaiser_chat("software_engineer_tester", ...)` →
1. Query `emad_instances` → `package_name = 'software_engineer'`, `parameters = {...}`
2. Look up `build_graph_func` in entry_points map by package_name
3. Call `build_graph_func(parameters)` → compiled StateGraph
4. Invoke StateGraph with initial state
5. Return `final_response`

### 6.5 Host Contract

Every eMAD package must expose:

```python
EMAD_PACKAGE_NAME: str      # matches package name on Alexandria
DESCRIPTION: str            # default description
SUPPORTED_PARAMS: dict      # optional — documents accepted params and types

def build_graph(params: dict) -> StateGraph:
    """Build and return a compiled LangGraph StateGraph.
    params: from emad_instances.parameters. Unknown keys are ignored.
    """
```

**Initial state contract:** Kaiser constructs:
```python
{
    "messages": [HumanMessage(content=message)],
    "rogers_conversation_id": conversation_id,
    "rogers_context_window_id": None,
}
```
eMAD StateGraphs must accept this initial state and populate `final_response` before returning.

### 6.6 Kaiser Imperator

The Kaiser Imperator manages the eMAD lifecycle and registry — the cognitive layer of Kaiser.

**Domain:** eMAD capability management. Understanding what each installed package does, what
parameters it accepts, and how to configure instances for different purposes.

**Internal tools:** list_packages, list_instances, create_instance, update_instance,
delete_instance, get_package_metadata (reads SUPPORTED_PARAMS from installed package).

**Sutherland alias:** `imperator-kaiser`

---

## 7. Data Models

### 7.1 `emad_packages`

```sql
CREATE TABLE emad_packages (
    package_name      VARCHAR(100) PRIMARY KEY,
    installed_version VARCHAR(50)  NOT NULL,
    installed_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    status            VARCHAR(20)  NOT NULL DEFAULT 'active'
                      CHECK (status IN ('active', 'error'))
);
```

### 7.2 `emad_instances`

```sql
CREATE TABLE emad_instances (
    emad_name    VARCHAR(100) PRIMARY KEY,
    package_name VARCHAR(100) NOT NULL REFERENCES emad_packages(package_name),
    description  TEXT         NOT NULL DEFAULT '',
    parameters   JSONB        NOT NULL DEFAULT '{}',
    status       VARCHAR(20)  NOT NULL DEFAULT 'active'
                 CHECK (status IN ('active', 'disabled')),
    created_at   TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at   TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_emad_instances_package ON emad_instances(package_name);
```

---

## 8. Volumes

| Container | Mount | Path | Purpose |
|---|---|---|---|
| `kaiser-langgraph` | `joshua26_workspace` | `/workspace` | Standard workspace mount |
| `kaiser-langgraph` | `joshua26_storage` | `/storage` | Credentials, shared storage |
| `kaiser-postgres` | `joshua26_workspace` | `/workspace` | DB data at `/workspace/kaiser/databases/postgres/data/` |
| `kaiser-postgres` | `joshua26_storage` | `/storage` | Backups at `/storage/backups/databases/kaiser/postgres/` |

---

## 9. Flow Details

### 9.1 `kaiser_chat` Flow

```python
class KaiserChatState(TypedDict):
    emad_name:       str
    conversation_id: str
    message:         str
    instance_row:    dict | None
    emad_graph:      Any  | None
    emad_result:     dict | None
    response:        str  | None
    error:           str  | None
```

**Nodes:**
1. **`lookup_instance`** — query `emad_instances`; set error if not found or disabled; verify
   package is in entry_points map.
2. **`build_and_invoke`** — call `build_graph_func(instance_row["parameters"])`, then
   `await graph.ainvoke(initial_state)`. Catch and record errors.
3. **`extract_response`** — read `emad_result["final_response"]`; fallback to
   `last_observation` or error message.

**Graph:**
```
START → lookup_instance
  ├─ error → extract_response → END
  └─ ok    → build_and_invoke → extract_response → END
```

### 9.2 Imperator Flow (`kaiser_imperator_chat`)

Standard System 3 ReAct Imperator pattern via LangGraph StateGraph. Sutherland alias:
`imperator-kaiser`. Internal tools: list_packages, list_instances, create_instance,
update_instance, delete_instance, get_package_metadata.

### 9.3 Management Flows

Single-node programmatic LangGraph StateGraphs. `kaiser_install_package` calls
`importlib.invalidate_caches()` then rescans `kaiser.emads` entry_points after pip install
completes. All flows validate input and return structured status.

### 9.4 `metrics_get` Flow

Single-node programmatic flow. Queries internal counters and returns Prometheus exposition
format text. Same text is served at `GET /metrics` for direct Prometheus scraping.

---

## 10. Health Strategy

| Dependency | On failure | Rationale |
|---|---|---|
| `kaiser-langgraph` | Hard fail | Without the runtime, Kaiser cannot function |
| `kaiser-postgres` | Hard fail | Without the registry, Kaiser cannot look up instances |
| Rogers | Degraded | eMADs degrade per their own strategy |
| Sutherland | Degraded | Imperator unavailable; dispatch continues |
| Alexandria (via `/pypi/`) | Degraded | `kaiser_install_package` fails; running instances unaffected |

---

## 11. Exceptions

### EX-KAISER-001: Alexandria for Package Installation (Build-time and Runtime)

**Deviation:** `kaiser-langgraph` installs Python dependencies from Alexandria (`irina:3141`)
at Docker build time (via `--index-url` in the Dockerfile `RUN` step) and at runtime
(via `kaiser_install_package`). Neither uses the offline `packages/` directory pattern
(REQ-000 §1.1).

**Justification:** Alexandria IS the ecosystem's approved offline package cache (deployed on
irina). Packages served by Alexandria are stored on irina's local ZFS storage — no external
network access occurs. This satisfies the spirit of REQ-000 §1 (offline-first, no internet
dependency) while enabling State 3 dynamic eMAD loading. The `packages/` directory pattern was
the pre-Alexandria approach; Alexandria is its replacement.

**Mitigation:** Build-time install uses `network: host` and is reproducible. Runtime install
(`kaiser_install_package`) requires Alexandria to be healthy — all other tools continue
operating when Alexandria is unavailable.

### EX-KAISER-002: Postgres Data Volume Bind Mount (ADR-052)

**Deviation:** `docker-compose.m5.yml` suppresses the anonymous `VOLUME /var/lib/postgresql/data`
declared by `postgres:16-alpine` using a host bind mount:
`/mnt/nvme/workspace/kaiser/databases/postgres/data:/var/lib/postgresql/data`

**Justification:** Per ADR-052, official images that declare anonymous VOLUMEs must have those
VOLUMEs explicitly bind-mounted to a known host path to prevent data loss on container removal.
This is the approved pattern used by all postgres-backed MADs in the ecosystem
(e.g., EX-ALEXANDRIA-005, EX-SUTHERLAND-001).

**Mitigation:** The bind mount path (`/mnt/nvme/workspace/kaiser/databases/postgres/data`) must
be created with `chmod 750` and owned by UID 2036 before first deployment.

### EX-KAISER-003: Unpinned Base Image Digests

**Deviation:** `kaiser/Dockerfile` uses `nginx:1.27.4-alpine` and `kaiser-postgres/Dockerfile`
uses `postgres:16-alpine` without SHA256 digest pins (REQ-000 §1.4).

**Justification:** Digest pins are obtained by pulling the image on the target host. These same
images are used without digest pins in all other ecosystem MADs (Alexandria, Starret, Henson,
Rogers, etc.). The digest pinning step is deferred to Gate 3 deployment, at which point the
actual digest is confirmed and pinned.

**Mitigation:** At deployment time, run:
```
docker pull nginx:1.27.4-alpine && docker inspect --format='{{index .RepoDigests 0}}' nginx:1.27.4-alpine
docker pull postgres:16-alpine  && docker inspect --format='{{index .RepoDigests 0}}' postgres:16-alpine
```
Pin both digests in the respective Dockerfiles before closing Gate 3.

---

## 12. Verification

1. **Health:** `curl http://m5:9226/health` → all components healthy including postgres
2. **Metrics:** `curl http://m5:9226/metrics` → Prometheus text output
3. **Empty registry:** `kaiser_list_emads` → empty list
4. **Install:** `kaiser_install_package("hopper-emad")` → `{"status": "installed", ...}`
5. **Create instance:** `kaiser_create_emad("hopper", "hopper-emad", "Engineering Department", {})` → created
6. **Create parameterised variant:** `kaiser_create_emad("hopper_fast", "hopper-emad", "Fast mode", {"temperature": 0.1, "max_steps": 2})` → created
7. **List:** `kaiser_list_emads` → both instances appear with correct parameters
8. **Chat:** `kaiser_chat("hopper", "test-001", "describe your capabilities")` → substantive response
9. **Parameterised chat:** `kaiser_chat("hopper_fast", "test-002", "same question")` → response reflecting fast-mode params
10. **Imperator:** `kaiser_imperator_chat("What eMAD should I use for writing tests?")` → reasoned recommendation
11. **Update:** `kaiser_update_emad("hopper_fast", parameters={"temperature": 0.05})` → updated, next chat reflects change
12. **Unknown instance:** `kaiser_chat("nonexistent", ...)` → `{"error": "EMAD_NOT_FOUND"}`
13. **Henson integration:** Select "Hopper" in Open WebUI → message reaches Hopper eMAD via Kaiser
