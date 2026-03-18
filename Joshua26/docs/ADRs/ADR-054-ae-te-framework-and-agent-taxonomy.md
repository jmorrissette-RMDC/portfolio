# ADR-054: AE/TE Framework, Agent Taxonomy, and Dynamic StateGraph Loading

**Status:** Accepted
**Date:** 2026-03-13
**Deciders:** System Architect
**Related:** ADR-051 (MCP Gateway Library Pattern), ADR-053 (Bidirectional Gateway Peer Proxy), HLD-state3-mad.md, HLD-joshua26-agent-architecture.md, a5-the-mad-pattern.md

---

## Context

As the Joshua26 ecosystem matured — particularly through the development of State 3 and the Kaiser eMAD host — several conceptual ambiguities became untenable:

1. **MAD terminology was overloaded.** "MAD" referred simultaneously to the pattern (the Multipurpose Agentic Duo concept) and to persistent running services with container infrastructure. This conflation made it impossible to discuss ephemeral agents clearly.

2. **The agent/infrastructure boundary was undefined.** The cognitive intelligence (agent reasoning, PCP, inference) and the physical infrastructure (containers, gateways, databases) were conceptually fused. Papers described them as aspects of the same thing, but State 3's dynamic loading proved they are separable — and that separating them enables eMADs.

3. **The Effector agent class was an artifact of tight coupling.** The Imperator/Effector distinction assumed that pMAD agents and eMAD agents were structurally different — Imperators for pMADs, Effectors for eMADs. Once the TE is decoupled from the AE, both are structurally identical library packages. The distinction collapses.

4. **`install_flows` was misleadingly named.** The bootstrap command loaded TE packages, but the name suggested generic flow installation. With the recognition that both AE and TE packages are dynamically loaded via the same mechanism, a unified name was needed.

---

## Decisions

### 1. AE/TE Separation

Every MAD is now understood as composed of two conceptually distinct aspects:

**Action Engine (AE)** — the physical system. All containers: gateway, databases, caches, sidecars, observability, the bootstrap kernel. Provides direct tool capabilities and, via joshua-net, access to the full tool set of every other MAD in the ecosystem. Also hosts Executor-driven processes. Both AE and TE use LangGraph for programmatic logic — LangGraph is a tool, not a layer.

**Thought Engine (TE)** — the cognitive intelligence. The Imperator and its cognitive apparatus: PCP, inference, conversation-as-state. Runs within the pMAD, supported by the AE, but conceptually distinct from it.

The AE calls into the TE, not the other way around. All external communication arrives through the AE. The TE has access to the AE's capabilities via the host contract.

### 2. pMAD/eMAD Terminology

**MAD** remains the umbrella term for the pattern — the concept of an autonomous actor that is simultaneously server and client.

**pMAD (Persistent MAD)** — owns its own AE and its own TE, plus potentially many Executors. System domain. Always running. Has a container infrastructure body.

**eMAD (Ephemeral MAD)** — has its own TE but no AE of its own. Relies on its host pMAD's AE. Subject matter domain. Exists only during StateGraph execution.

The eMAD is a direct consequence of AE/TE separation: once the TE is a library package independent of infrastructure, an autonomous agent can exist without owning any containers.

### 3. Effector Retirement

The Effector agent class is retired. All agents — in pMADs and eMADs alike — that possess Identity, Purpose, and Autonomy are Imperators. The difference between a pMAD Imperator and an eMAD Imperator is domain type (system vs subject) and lifecycle (persistent vs ephemeral), not structure.

### 4. Agent Taxonomy Grounded in Primitives

Two agent classes, grounded in the primitives from `a1-conversationally-cognizant-ai-systems.md`:

**Imperator** — possesses Identity, Purpose, and Autonomy. Generates its own Intent (the dynamic expression of Purpose meeting circumstances). Self-directing. The prime agent within any TE.

**Executor** — possesses none of these. Its intent is entirely derivative of the calling system. Cognitive but never independent. Can take many forms: sub-agents, AE tools, StateGraph workers. Not addressable externally.

### 5. Dynamic AE and TE Loading via `install_stategraph`

State 3 reduces the container to a **bootstrap kernel** — an irreducible core: Python runtime, web server, connection pool management, `install_stategraph()` tool, entry_points scanner. Everything else is dynamically loaded from Alexandria as versioned Python packages.

Two kinds of StateGraph packages, distinguished by entry_points group:
- **AE StateGraph** — infrastructure wiring, MCP tool handlers, message routing. Wired into the web server routing table by the bootstrap.
- **TE StateGraph** — Imperator, PCP, inference flows, domain reasoning. Made available for internal invocation by the AE.

`install_stategraph` replaces the former `install_flows`. A single command handles both AE and TE packages — the entry_points group tells the bootstrap what kind of package it is.

---

## Consequences

- All existing documentation must be reviewed for terminology alignment. Papers scoped to persistent container architecture use "pMAD" explicitly. The umbrella "MAD" is reserved for the pattern itself.
- All references to "Effector" as an agent class are removed. Replaced with "Imperator" for autonomous agents and "Executor" for non-autonomous cognitive workers.
- Existing ADRs are not modified (they are historical records reflecting the state of understanding at the time they were written). This ADR supersedes the relevant portions.
- `install_flows` in the Kaiser codebase is renamed to `install_stategraph`.
- `HLD-MAD-container-composition.md` requires update for the sidecar pattern and State 3 bootstrap kernel concept.
- The four key papers have been rewritten to reflect this framework: `HLD-state3-mad.md` v2.0, `a5-the-mad-pattern.md`, `HLD-joshua26-agent-architecture.md` v2.0, `d1-system-3-react.md`.

---

## Papers Defining This Framework

- `a5-the-mad-pattern.md` — the MAD pattern, AE/TE as defining concepts, two forms, two agent classes
- `HLD-state3-mad.md` — AE/TE separation architecture, bootstrap kernel, dynamic StateGraph loading
- `HLD-joshua26-agent-architecture.md` — primitives, agent classes, anatomy of the TE, development workflow
- `d1-system-3-react.md` — ReAct execution modes, Reasoning/Execution Component naming (disambiguated from AE/TE)
- `a1-conversationally-cognizant-ai-systems.md` — the primitives: Identity, Purpose, Intent, Autonomy, Persona, Domain
