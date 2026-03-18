# HLD: pMAD Container Composition Architecture

**Version:** 5.0 **Date:** 2026-03-13 **Status:** Active **Related Documents:**

-   ADR-039: Radical Simplification
-   ADR-045: MAD Template Standard
-   ADR-053: Bidirectional Gateway as Network Boundary with Peer Proxy
-   ADR-054: AE/TE Framework and Agent Taxonomy
-   HLD-state3-mad.md
-   full-composition-migration-plan.md

***

## Executive Summary

This HLD defines the container composition architecture of pMADs (Persistent MADs) in the Joshua26 ecosystem. A pMAD is a MAD that owns its own Action Engine (AE) — the physical infrastructure of containers, gateways, databases, and networking — and its own Thought Engine (TE) — the cognitive intelligence that reasons over its domain. eMADs (Ephemeral MADs) have no container architecture; they are TE library packages hosted by a pMAD. This document concerns pMADs exclusively.

The document describes the evolution from the original hybrid model (State 0) through an intermediate decomposed state (State 1) to the current deployed architecture (State 2): OTS infrastructure, graph-native logic, built-in observability, and the Imperator pattern. State 3 is the target architecture, extending State 2 with dynamic loading of both AE and TE as versioned Python packages from Alexandria.

**State 3 is the target architecture.** State 3 reduces the container to a bootstrap kernel — an irreducible core (Python runtime, web server, connection pool management, `install_stategraph()`, entry_points scanner). Everything else — both AE StateGraphs (infrastructure wiring, MCP tool handlers, message routing) and TE StateGraphs (Imperator, PCP, inference flows, domain reasoning) — is dynamically loaded from Alexandria at runtime. What makes a container *this particular pMAD* comes entirely from Alexandria packages. The container itself is interchangeable. Kaiser is the first State 3 pMAD. State 2 is the current state of deployed platform pMADs. State 0 and State 1 are historical or transitional. See `HLD-state3-mad.md` for the full State 3 pattern.

The architecture is designed to validate a research hypothesis: agents can autonomously build and maintain systems structured as LangGraph StateGraphs, because the graph is the right level of abstraction for agent cognition.

**Scope:** All pMADs in the ecosystem and the architectural pattern for pMAD container development. eMADs are out of scope — they have no containers.

**Key Principle:** Network transparency — external consumers see no changes as pMADs evolve internally.

***

## Understanding pMADs

### What is a pMAD?

A pMAD (Persistent MAD) is a MAD that owns its own infrastructure — containers, gateways, databases, networking — and runs persistently as a deployed service. It is the physical instantiation of the MAD pattern, combining an Action Engine (AE) for infrastructure and tool capabilities with a Thought Engine (TE) for cognitive intelligence over its system domain.

The **AE** is the physical system: all containers, the gateway, databases, caches, sidecars, observability, and the bootstrap kernel. It provides direct tool capabilities and, via joshua-net, access to the full tool set of every other pMAD in the ecosystem. AE logic is implemented as LangGraph StateGraphs — infrastructure wiring, MCP tool handlers, message routing, and Executor-driven processes.

The **TE** is the cognitive intelligence: the Imperator and its cognitive apparatus (PCP, inference, conversation-as-state). The Imperator is a System 3 ReAct agent that owns the pMAD's cognitive operations — planning, reasoning, multi-step orchestration, and goal-directed behaviour. It is composed of a Reasoning Component and an Execution Component, each a collection of components bound together by process. TE logic is also implemented as LangGraph StateGraphs.

Both AE and TE StateGraphs run in the same langgraph container. There is no separate deployment boundary between them. The AE calls into the TE, not the other way around — all external communication arrives through the AE.

**eMADs** (Ephemeral MADs) have no AE of their own. They are TE library packages — subject matter domain intelligence — hosted by a pMAD. They have no containers, no gateway, no infrastructure. This document does not apply to them. See `a5-the-mad-pattern.md` and `HLD-state3-mad.md` for the eMAD concept.

### Technology: LangGraph

-   **LangGraph:** Python-based graph library powering the langgraph container in every pMAD (StateGraph, nodes, edges, checkpointing). All pMAD logic — both AE and TE flows — is implemented as LangGraph StateGraphs.

***

## Container Architecture Evolution: Four States

### State 0: Hybrid Container Model (Legacy)

Some legacy pMADs bundle all functionality into a single monolithic container.

**Example: Codd (legacy, deprecated)**

-   Single container runs PostgreSQL + Node.js MCP server + custom code
-   Dockerfile starts FROM postgres, layers on runtime and code
-   Startup script launches database, then MCP server
-   All functionality in one deployment unit

**Container naming:** `codd`, `babbage`, etc. (single container per pMAD)

**Why This Was Correct Initially:**

-   Simplicity during bootstrap phase
-   Single deployment unit per capability
-   Fast enough for initial development

**Limitations as ecosystem matures:**

-   Slow rebuild cycles (must rebuild database + runtime + code for any change)
-   Cannot use official images (custom base images required)
-   Violates separation of concerns
-   Makes testing and updates difficult

### State 1: Full Composition (Intermediate)

State 1 applies functional decomposition to separate concerns into specialized containers orchestrated by a thin composition root.

**Functional Components:**

1.  **MCP Gateway (**`[mad]`**)** - Composition root + MCP API layer
    -   Thin wiring layer that exposes MCP tools to joshua network
    -   Handles MCP tool requests from peers and clients
    -   Routes requests to langgraph container
    -   Configuration-driven (config.json) with standard libraries
    -   Node.js or Python runtime for MCP protocol
2.  **LangGraph Container (**`[mad]-langgraph`**)** - Flow execution runtime
    -   Runs LangGraph flow definitions
    -   Both AE and TE logic implemented as flows here
    -   Runs StateGraph definitions with nodes, edges, and checkpointing
    -   ALL programmatic logic lives here
3.  **Backing Services (**`[mad]-[technology]`**)** - Infrastructure (as needed)
    -   Uses official images with technology names: postgres, redis, playwright, etc.
    -   NOT all MADs need backing services
    -   Examples: codd-postgres, rogers-redis, malory-playwright

**Container Naming Convention:**

-   MCP Gateway: `[mad]` (e.g., `codd`, `malory`)
-   LangGraph runtime: `[mad]-langgraph` (e.g., `codd-langgraph`, `malory-langgraph`)
-   Backing services: `[mad]-[technology]` (e.g., `codd-postgres`, `rogers-redis`, `malory-playwright`)

**Docker Labels:**

```yaml
labels:
  - "mad.logical_actor=[mad-name]"
  - "mad.component=[mcp|langgraph|postgres|redis|playwright...]"
```

**Registry Entry:** Each pMAD has one registry entry (the gateway). Sub-container topology is defined in docker-compose.yml. All containers in a pMAD group share the same UID — see ADR-043 for identity and UID assignment rules.

**Note:** State 1 was not an intentional design target. It was an intermediate state where agents built the correct container decomposition but failed to use LangGraph as intended — constructing custom HTTP clients, helper service modules, and programmatic logic outside the graph. All pMADs are being migrated to State 2.

***

### State 2: Agentic Composition (Current Deployed Architecture)

State 2 is the correct architecture for Joshua26 pMADs. It is defined by four mandatory principles.

#### Why State 2 Exists — The Research Premise

Joshua26 is a research lab testing a specific hypothesis:

> **Agents can autonomously build and maintain a system structured as a collection of LangGraph StateGraphs, because the graph structure is the right level of abstraction for agent cognition.**

The hypothesis is validated when agents can build, extend, and maintain the system themselves with minimal user input. Hopper is the proof-of-concept: it is being built by agents, on agents, using the State 2 pattern.

State 1 was a mistake, not a design alternative. Agents defaulted to custom procedural code — Flask apps on LangGraph containers, custom HTTP clients, service wrapper libraries — instead of using LangGraph as designed. State 2 enforces the pattern that makes the hypothesis testable. All MADs will be State 2. There is no comparison group; State 1 is temporary scaffolding to be removed.

---

#### Principle 1: OTS Infrastructure

The pMAD is assembled from Off-The-Shelf images. The only custom-built container is `[mad]-langgraph`.

```
[mad]               # nginx:alpine — pure reverse proxy, zero custom logic
[mad]-langgraph     # Python — LangGraph StateGraph + standard LangChain components
[mad]-[technology]  # Official images: postgres:16-alpine, redis:7-alpine, etc.
```

The consequence is critical: **there is exactly one place to look for custom logic — the StateGraph.** When an agent reads a pMAD codebase, Nginx, Postgres, and Redis are commodities. The intelligence is in the graph. Bugs, features, and changes are always in the graph.

Building a custom container is a rare, explicitly justified decision — only when nothing OTS exists for the purpose. We innovate based on what the graph does, not by building software that someone else has already built.

---

#### Principle 2: Graph is the App

All programmatic logic lives in the LangGraph StateGraph using standard LangChain components. Nothing else.

**What this means concretely:**

- **Nodes** — small, single-purpose Python functions. Read from State, do one thing, write to State.
- **Edges and Conditional Edges** — all control flow decisions. Not `if/else` blocks inside nodes.
- **Tools** (`BaseTool`, `@tool`) — all external interactions: peer pMAD calls, database operations, API calls.
- **Peer calls** — `langchain-mcp-adapters` (`MultiServerMCPClient`). No manual JSON-RPC construction. No `peer_client.py`.
- **State** — the only thing that flows between nodes.

**Explicitly forbidden in State 2:**

- Custom HTTP client wrapper modules (e.g., `peer_client.py`, `services/` helpers)
- Custom gateway routing libraries (e.g., Node.js `routing-lib`, `mcp-protocol-lib`)
- Manual JSON-RPC payload construction
- Programmatic logic living outside the StateGraph

**Why this serves the research premise:**

When an agent reads a State 2 pMAD, it sees a graph — a complete, accurate map of what the system does, in what order, with what decision points. Each node is small enough to reason about in isolation. The agent can modify one node without understanding the whole system. This is fundamentally different from reading hundreds of lines of custom helper code spread across multiple files with implicit dependencies and hidden control flow.

---

#### Principle 3: Built-in Observability (Apgar)

Observability is not bolted on after the fact. It is a first-class requirement, built in at design time.

Every State 2 pMAD exposes two mandatory endpoints on the LangGraph container. Both are implemented as compiled StateGraphs — Sutherland (`mads/sutherland/sutherland-langgraph/server.py`) is the reference implementation:

- `GET /metrics` — Prometheus exposition format text, scraped directly by Prometheus
- `POST /metrics_get` — MCP tool returning `{"metrics": "..."}` JSON, called by Apgar scraper via peer proxy

**Required standard metrics (every pMAD):**

| Metric | Type | Labels |
|---|---|---|
| `mcp_requests_total` | Counter | `mad`, `tool`, `status` |
| `mcp_request_duration_seconds` | Histogram | `mad`, `tool` |
| `mcp_requests_errors_total` | Counter | `mad`, `tool`, `error_type` |

pMAD-specific metrics (queue depths, DB record counts, etc.) are encouraged on top of the three above.

**Implementation rule:** Route handlers for `/metrics` and `/metrics_get` must be thin wrappers calling `StateGraph.ainvoke()`. Logic goes in the graph node, not in the route handler. This is consistent with Principle 2. See `docs/guides/mad-prometheus-metrics-guide.md` for the full authoring guide.

**How Apgar consumes this:** The Apgar metrics scraper calls `POST apgar:[port]/peer/{mad}/metrics_get` for each registered peer pMAD. It extracts the Prometheus text, adds an `instance` label, and aggregates for Prometheus. In an ecosystem where pMADs call each other, a silent failure in one pMAD cascades into mysterious failures in others. Observability makes the ecosystem debuggable.

**Apgar compliance is a gate, not a suggestion.** A pMAD without working `/metrics` and `/metrics_get` is not State 2 compliant.

---

#### Principle 4: Imperator Pattern

Every State 2 pMAD includes an **Imperator** — the prime agent within the TE, a System 3 ReAct agent that owns the pMAD's complex, multi-step, non-deterministic operations. The Imperator possesses its own Identity, Purpose, and Autonomy, and generates its own Intent from its Purpose meeting current circumstances.

The pMAD exposes two categories of interface:

**Category 1: Direct MCP Tools** — deterministic, well-defined, repeatable

The caller invokes these like a function call. The result is predictable. The caller knows exactly what it is asking for.

Examples: `llm_embeddings` (Sutherland), `conv_store_message` (Rogers), `create_github_issue` (Starret)

**Category 2: Imperator Chat** — complex, multi-step, requires judgment

The caller sends a natural language goal. The Imperator uses the pMAD's own tools internally to accomplish it. The caller does not need to know the steps.

Examples:
- **Starret:** *"Commit and push my work."* The Imperator handles stashing, rebasing, conflict resolution, retry — all the complexity of a real git workflow. The calling agent should not need to know how git conflict resolution works.
- **Malory:** *"Test the login flow."* The Imperator orchestrates a multi-step browser automation sequence, handles failures, retries, and takes screenshots. The calling agent just delegates the goal.
- **Rogers:** *"Summarize what this user has been working on this week."* The Imperator queries history, searches memory, assembles context, and synthesizes — steps that require judgment about relevance.

**Design rule:** When designing a pMAD capability, ask: *"Is this a function call or a conversation?"*
- Predictable, single-outcome → MCP Tool
- Multi-step, conditional, requires judgment → Imperator

The Imperator is what makes a pMAD **autonomous**. Without it, a pMAD is a well-organized set of tools. With it, the pMAD can be delegated a goal rather than a command.

---

#### State 2 Container Architecture

```
[mad]               # nginx:alpine — sole network boundary (ingress AND egress proxy)
[mad]-langgraph     # Python — LangGraph StateGraph + langchain-mcp-adapters + Imperator
[mad]-[technology]  # Official images — postgres, redis, etc. (if needed)
```

**Network assignments:**

| Container | `joshua-net` | `[mad]-net` | Notes |
|---|---|---|---|
| Nginx (`[mad]`) | ✓ | ✓ | Sole network boundary — ingress AND egress |
| LangGraph (`[mad]-langgraph`) | | ✓ | Never on joshua-net |
| Backing services | | ✓ | Never on joshua-net |

**Outbound peer calls — Nginx as egress proxy:**

LangGraph calls peers via Nginx on `[mad]-net`. Nginx forwards to the peer on `joshua-net`. LangGraph never has direct access to `joshua-net`.

Nginx config (per peer):
```nginx
location /proxy/sutherland/ {
    proxy_pass http://sutherland:11435/;
}
```

`langchain-mcp-adapters` initialization in LangGraph:
```python
from langchain_mcp_adapters.client import MultiServerMCPClient
mcp_client = MultiServerMCPClient({
    "sutherland": {
        "url": "http://[mad]:6380/proxy/sutherland/mcp",  # via Nginx on [mad]-net
        "transport": "streamable_http",
    }
})
tools = await mcp_client.get_tools()
```

Peer call chain:
```
[mad]-langgraph  →  POST http://[mad]:[port]/proxy/sutherland/mcp   ([mad]-net)
Nginx gateway    →  POST http://sutherland:11435/mcp                (joshua-net)
```

**State 2 Invariants (violations are architectural failures):**

1. No custom HTTP clients in `[mad]-langgraph`. Use `langchain-mcp-adapters`.
2. No programmatic logic in the gateway. Nginx config only.
3. All peer calls route through Nginx (`/proxy/{peer}/`). LangGraph never on `joshua-net`.
4. `/metrics` and `/metrics_get` endpoints must exist and be Apgar-compatible.
5. Every pMAD has an Imperator node/subgraph.

#### Note on Deprecated pMADs

Not every legacy pMAD will become State 2. Some State 0 pMADs were built as thin wrappers around a single technology with no real agentic capability (e.g., Codd wrapping Postgres). These are deprecated — databases are backing services, not pMADs. They will be absorbed as backing services inside the pMADs that actually use them. The decision criterion: does this pMAD have a meaningful Imperator? If not, it is infrastructure, not a pMAD.

***

### State 3: Dynamic AE/TE Loading (Target Architecture)

State 3 is the target architecture for all pMADs. It extends State 2 by making both the AE and TE dynamically loadable — the container reduces to a bootstrap kernel, and everything that makes it *this particular pMAD* comes from Alexandria packages installed at runtime.

#### The Bootstrap Kernel

The State 3 container is an irreducible core:

```
Bootstrap kernel (container)
    ├── Python runtime
    ├── Web server
    ├── Connection pool management
    ├── install_stategraph() tool
    └── Entry_points scanner (discovers AE and TE packages)
```

The kernel is the one piece that cannot be dynamically loaded — it is the loader. It provides the runtime environment and the mechanism to discover and install everything else.

#### Dynamic StateGraph Loading

Both AE and TE are published to Alexandria as versioned Python packages and installed at runtime via `install_stategraph()`. Two kinds of StateGraph packages, distinguished by entry_points group:

- **AE StateGraph** — infrastructure wiring, MCP tool handlers, message routing, Executor-driven processes. The bootstrap wires these into the web server routing table.
- **TE StateGraph** — Imperator, PCP, inference flows, domain reasoning. The bootstrap makes these available for internal invocation by the AE.

The entry_points group tells the bootstrap what kind of package it is. `install_stategraph` is a single command for both. See `HLD-state3-mad.md` for the full dynamic loading architecture, host contract, and CI/CD implications.

#### Sidecars

State 3 introduces the **sidecar pattern** for capabilities that require dedicated containers beyond the standard backing services. A sidecar is a standard OTS image adapted for use within the pMAD — for example, wrapping a CLI-only tool with an API, or mounting Docker socket access for container management.

Sidecars carry whatever privileges and mounts their job requires, keeping the kernel generic and unprivileged. The AE StateGraph knows how to talk to sidecars; the kernel does not. Sidecars are declared in docker-compose alongside the kernel and backing services.

The sidecar pattern preserves the OTS principle: use standard images, adapt them for the pMAD's needs, wire them together via the AE StateGraph.

#### Container Architecture

```
[mad]               # Bootstrap kernel — Python runtime, web server, install_stategraph()
[mad]-[technology]  # Official images — postgres, redis, etc. (if needed)
[mad]-[sidecar]     # Sidecar containers (if needed) — adapted OTS images
```

The langgraph container distinction from State 1/2 dissolves — the kernel IS the runtime. AE and TE StateGraphs are loaded into it as packages.

#### AE Stability

AE stability depends on the pMAD's domain. Core infrastructure pMADs (context broker, inference broker, observability) approach near-zero AE changes over time — their containers are largely prebuilt images wired together via the AE StateGraph. Capability-oriented pMADs (media generation, desktop automation) see active AE growth as new containers are added to increase capabilities. Custom container builds remain rare, reserved for capabilities where no standard image exists.

#### Migration from State 2

All pMADs migrate toward State 3 as their infrastructure stabilises. The migration path: extract AE logic into an Alexandria package, extract TE logic into an Alexandria package, replace the monolithic langgraph container with the bootstrap kernel. Kaiser is the first State 3 pMAD.

***

## State 1 Architecture Examples

### Example 1: Codd (Database-backed pMAD)

Codd needs a database backing service.

**Containers:**

```
codd                    # MCP Gateway (composition root + MCP API)
codd-langgraph         # LangGraph runtime (AE + TE flows)
codd-postgres          # Official postgres:16 image
```

**Why this structure:**

-   MCP Gateway (codd) handles tool protocol and routing
-   LangGraph container runs SQL query flows (AE logic) and planning flows (TE logic)
-   PostgreSQL runs in official image (security, updates, community support)

### Example 2: Malory (Simple Service pMAD)

Malory is a browser automation service. It might need Playwright, or might not need any backing services.

**Option A: With Playwright as backing service:**

```
malory                  # MCP Gateway (composition root + MCP API)
malory-langgraph       # LangGraph runtime (browser automation flows)
malory-playwright      # Playwright browser runtime
```

**Option B: Without separate backing (simpler):**

```
malory                  # MCP Gateway (composition root + MCP API)
malory-langgraph       # LangGraph runtime with Playwright installed
```

**Why different options:** Different pMADs have different needs. Not prescriptive — use the structure that makes sense for each pMAD.

### Example 3: Rogers (Cache Service)

Rogers wraps Redis caching.

**Containers:**

```
rogers                  # MCP Gateway (composition root + MCP API)
rogers-langgraph       # LangGraph runtime (cache operation flows)
rogers-redis           # Official redis:7-alpine image
```

***

## Why State 1 (Full Composition)

### Benefits

**1. Deployment Velocity**

-   Rebuild only changed components
-   MCP Gateway changes: rebuild [mad] container only (\~15-30s)
-   Flow changes: rebuild langgraph container only (\~15-30s)
-   No need to rebuild databases/infrastructure

**2. Official Images**

-   Backing services use official, unmodified images
-   Security patches from upstream
-   Community support
-   Predictable behavior

**3. Separation of Concerns**

-   Each container has single responsibility
-   Clear boundaries between API, execution, and infrastructure
-   Independent testing and monitoring
-   Different update cycles

**4. Development Flexibility**

-   LangGraph flows can be updated independently of the gateway and backing services
-   LangGraph flows shared across pMADs via common patterns

### Trade-offs

**Increased Complexity:**

-   More containers to orchestrate (2-3 per pMAD vs 1)
-   Docker Compose orchestration required
-   More complex deployment topology

**Mitigation:** Docker Compose handles orchestration. From operator perspective, still deploy/manage as single logical unit.

**Note:** Pure service pMADs may not need separate backing services, but benefit from functional decomposition (composition + mcp + langgraph).

***

## Migration Strategy

### Overview

Migration is per-pMAD, not ecosystem-wide. Each pMAD follows its own path: State 0 → State 1 → State 2 → State 3.

**Per-pMAD Migration:**

-   Each pMAD migrates independently
-   No flag day
-   Network transparency maintained
-   Independent rollback

**Generic Procedure:** See `full-composition-migration-plan.md` for detailed step-by-step migration process applicable to any pMAD.

**Order Determination:** Migration order determined dynamically based on:

-   Development priorities
-   Dependencies
-   Risk assessment
-   Ecosystem needs at execution time

### Network Transparency

**Critical principle:** External interface remains unchanged during migration.

**What stays the same:**

-   pMAD hostname (e.g., `codd`)
-   MCP port (from registry.yml)
-   MCP endpoints and tool schemas
-   Tool behavior

**What changes (internal only):**

-   Container topology (1 container → 2-3+ containers)
-   Internal communication patterns
-   Deployment process

**Result:** Other pMADs and clients require zero configuration changes.

***

## Creating New pMADs (Current Template — State 1 Structure)

### Base Template Pattern

**Location:** `mads/_template/`

New pMADs are created by **copying and customizing** the base template, not by manually assembling files. The template currently implements State 1 structure (Node.js gateway + LangGraph + backing services). New pMADs should target State 2 (nginx gateway, langchain-mcp-adapters) and migrate to State 3 as their infrastructure stabilises.

**What the Template Provides:**

The base template (`mads/_template/`) is a fully working State 1 pMAD that demonstrates:
- MCP gateway container with all 4 standard libraries (logging, routing, health, protocol)
- LangGraph backend container with database integration
- PostgreSQL container with production patterns (health checks, backups)
- End-to-end MCP tool flow: client → gateway → langgraph → postgres

**Template Containers:**

1. **`template/`** - MCP gateway container
   - Generic server.js (< 20 lines, configuration-driven)
   - config.json with example tools (query_db, template_query)
   - Dependencies on all 4 gateway libraries
   - Production Dockerfile

2. **`template-langgraph/`** - LangGraph backend container
   - HTTP server for receiving tool requests
   - Graph definitions for database query flows
   - Shows pattern for implementing programmatic logic

3. **`template-postgres/`** - PostgreSQL database container (optional)
   - Based on official postgres:16 image
   - Includes cron-based backup infrastructure
   - Test schema (users table) for demonstration

4. **`template-service/`** - Generic backing service container (optional)
   - For non-database backing services (Redis, Playwright, custom services)
   - Lightweight base with health check and standard patterns

**Copy-Paste Workflow:**

```bash
# 1. Copy entire container directories
cp -r mads/_template/template mads/[mad-name]/[mad-name]
cp -r mads/_template/template-langgraph mads/[mad-name]/[mad-name]-langgraph
cp -r mads/_template/template-postgres mads/[mad-name]/[mad-name]-postgres  # If needed
cp -r mads/_template/template-service mads/[mad-name]/[mad-name]-service    # If needed

# 2. Customize config.json (define pMAD-specific tools and dependencies)
vim mads/[mad-name]/[mad-name]/config.json

# 3. Implement programmatic logic in LangGraph backend
vim mads/[mad-name]/[mad-name]-langgraph/server.py

# 4. Customize database schema (if applicable)
vim mads/[mad-name]/[mad-name]-postgres/init.sql

# 5. Add to docker-compose.yml (copy template services and rename)
```

**Key Benefits:**

- **No manual file creation:** All infrastructure pre-built
- **Production-ready patterns:** Health checks, logging, backups included
- **Working example:** Template runs immediately, demonstrates integration
- **Copy-paste simplicity:** Duplicate containers → customize config → deploy

**For Template Usage:** See `mads/_template/README.md` for copy-paste workflow.
**For Implementation Patterns:** See `docs/guides/mad-implementation-guide.md` for detailed guidance.

***

## Design Principles

### 1. Functional Decomposition

Separate concerns by function:

-   **MCP Gateway ([mad]):** Thin wiring + MCP protocol + tool exposure
-   **LangGraph:** Flow execution (AE + TE logic)
-   **Backing:** Infrastructure services as needed

### 2. Official Images Where Possible

Use official, unmodified images for backing services:

-   postgres:16-alpine, mongo:7, redis:7-alpine
-   qdrant/qdrant:latest, playwright, etc.

Only create custom images for MCP gateway ([mad]) and langgraph containers.

### 3. Container Naming Consistency

-   MCP Gateway: `[mad]` (e.g., codd, malory, rogers)
-   LangGraph runtime: `[mad]-langgraph` (e.g., codd-langgraph, malory-langgraph)
-   Backing services: `[mad]-[technology]` (postgres, redis, playwright)

Use technology names (not generic names) for backing services to indicate official images.

### 4. Progressive Migration

-   pMADs migrate individually
-   Mixed states supported (some State 0, some State 1, some State 2)
-   Learn from each migration
-   No ecosystem-wide rollout

### 5. Labels for Tracking

All containers labeled for discovery and tracking:

```yaml
labels:
  - "mad.logical_actor=[mad-name]"
  - "mad.component=[mcp|langgraph|composition|postgres|redis...]"
```

These labels support inventory and health tracking.

***

## Network Architecture

Per ADR-046, each pMAD group operates on two networks. Per ADR-053, the gateway is the **bidirectional** network boundary — it handles both inbound and outbound cross-network traffic.

### Two-Network Pattern

1. **`joshua-net` (public)** — Ecosystem-wide overlay network. Cross-pMAD communication and external access traverse this network.
2. **`[mad]-net` (private)** — Per-pMAD private network (e.g., `hamilton-net`, `rogers-net`). Internal containers communicate exclusively on this network.

### Network Assignments

The gateway is the **sole network boundary** in all states — for both inbound tool calls and outbound peer calls. LangGraph is always only on `[mad]-net`.

**State 1:**

| Container | `joshua-net` | `[mad]-net` | Notes |
|---|---|---|---|
| Node.js Gateway (`[mad]`) | ✓ | ✓ | Sole network boundary — ingress and egress |
| LangGraph (`[mad]-langgraph`) | | ✓ | Calls peers via gateway `/peer` proxy — never on joshua-net |
| Backing services | | ✓ | Never on joshua-net |

**State 2:**

| Container | `joshua-net` | `[mad]-net` | Notes |
|---|---|---|---|
| Nginx (`[mad]`) | ✓ | ✓ | Sole network boundary — ingress AND egress proxy |
| LangGraph (`[mad]-langgraph`) | | ✓ | Calls peers via Nginx `/proxy/{peer}/` — never on joshua-net |
| Backing services | | ✓ | Never on joshua-net |

### Outbound Calls from LangGraph (Peer Proxy)

**State 1 — Peer Proxy Pattern:**

The Node.js gateway exposes `POST /peer/{peer-name}/{tool-name}`. LangGraph calls the gateway on `[mad]-net`; the gateway wraps the call in MCP JSON-RPC and proxies to the peer on `joshua-net`.

```
[mad]-langgraph  →  POST http://[mad]:[port]/peer/sutherland/llm_embeddings  ([mad]-net)
[mad] gateway    →  POST http://sutherland:[port]/mcp  (tools/call JSON-RPC)  (joshua-net)
```

*This pattern required custom gateway code to do the JSON-RPC wrapping, introducing fragility (connection pooling deadlocks, opaque failures).*

**State 2 — Nginx Egress Proxy:**

Nginx proxies outbound peer calls from LangGraph to peers on `joshua-net`. LangGraph uses `langchain-mcp-adapters` pointing at the Nginx proxy URL. No custom code. No manual JSON-RPC construction. LangChain talking to LangChain over MCP — the intended design of `joshua-net`. LangGraph never touches `joshua-net` directly.

```
[mad]-langgraph  →  POST http://[mad]:[port]/proxy/sutherland/mcp  ([mad]-net)
Nginx gateway    →  POST http://sutherland:[port]/mcp              (joshua-net)
```

Nginx config addition (per peer):
```nginx
location /proxy/sutherland/ {
    proxy_pass http://sutherland:11435/;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
}
```

**State 2 initialization (in LangGraph startup):**
```python
from langchain_mcp_adapters.client import MultiServerMCPClient

mcp_client = MultiServerMCPClient({
    "sutherland": {
        "url": "http://[mad]:6380/proxy/sutherland/mcp",  # via Nginx on [mad]-net
        "transport": "streamable_http",
    }
})
tools = await mcp_client.get_tools()
# tools is a list of standard LangChain BaseTool instances — no custom code
```

**Invariant (all states):** LangGraph containers must never be on `joshua-net`. The gateway is always the sole network boundary for all cross-network traffic in both directions.

### Why Private Networks

- **Isolation:** Backing services (databases, caches) are not exposed to the ecosystem
- **Security:** Only the gateway is addressable from outside the pMAD group
- **Clarity:** Hard dependencies (within pMAD group) vs soft dependencies (across pMAD groups) map directly to network boundaries
- **Consistency:** The bidirectional gateway pattern applies uniformly — no pMAD needs special network treatment

### docker-compose.yml Pattern

```yaml
networks:
  joshua-net:
    external: true
  hamilton-net:
    driver: bridge

services:
  hamilton:
    networks:
      - joshua-net
      - hamilton-net
  hamilton-langgraph:
    networks:
      - hamilton-net
  hamilton-postgres:
    networks:
      - hamilton-net
```

***

## Impact Analysis

### On Other pMADs

**Zero impact** — pMADs interact via direct MCP on joshua-net. Internal composition invisible to peers.

### On Clients

**Zero impact** — Clients connect to pMAD gateways directly. Internal composition invisible.

### On Storage

Backing services continue to mount /storage for persistence. No data layout changes.

### On ADRs

**Updates required:**

-   ADR-045 (pMAD Template Standard): Add State 1 architecture patterns
-   ADR-054 (AE/TE Framework and Agent Taxonomy): Documents AE/TE separation and State 3 architecture

***

## Success Criteria

### Technical Metrics

-   pMAD container rebuild time: \< 30 seconds (Node.js/Python)
-   LangGraph container rebuild time: \< 1 minute
-   Network latency overhead: \< 1ms
-   All existing MCP tools function identically

### Operational Metrics

-   Zero ecosystem configuration changes
-   Zero ecosystem integration changes
-   Successful deployment without downtime
-   Documented migration procedure applicable to all pMADs

### Architectural Metrics

-   Clear separation of concerns (API, execution, infrastructure)
-   Official images used for backing services
-   Deployment velocity improvement (measurable)
-   Foundation for LangGraph-based autonomy

***

## Future Considerations

### CI/CD Integration

State 2/3 architecture enables automated CI/CD with three independent tracks:

-   **Kernel track** — very rare changes, brief restart required
-   **AE package track** — varies by domain, zero downtime via `install_stategraph`
-   **TE package track** — frequent changes, zero downtime via `install_stategraph`

See `HLD-state3-mad.md` for the full CI/CD architecture under State 3.

### Autonomy Development

State 3 provides the foundation for autonomous ecosystem evolution:

-   Both AE and TE are dynamically loadable — pMADs can evolve without restarts
-   pMADs learn interaction patterns via Rogers memory
-   Agents can modify and deploy their own StateGraph packages via Alexandria
-   The bootstrap kernel is stable enough that the focus shifts entirely to graph-level intelligence

***

**Document Status:** v5.0 — Updated 2026-03-13 for AE/TE framework, pMAD terminology, State 3 bootstrap kernel, and sidecar pattern.
