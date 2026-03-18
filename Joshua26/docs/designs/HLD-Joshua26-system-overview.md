# HLD: Joshua26 System Overview

**Version:** 2.0 **Date:** 2026-03-13 **Status:** Active **Purpose:** System overview, core concepts, and document navigation

***

## Executive Summary

Joshua26 is a distributed AI agent ecosystem built to test a specific research hypothesis:

> **Agents can autonomously build and maintain a system structured as a collection of LangGraph StateGraphs, because the graph structure is the right level of abstraction for agent cognition.**

The ecosystem runs on Docker Compose across 3 bare-metal hosts (Swarm for overlay networking only), providing modular MCP-connected services. This is a one-man lab environment — enterprise concerns are not needed here. We focus on the ability to move quickly over security concern or overengineering. The architect does not code or modify systems directly. Rather he uses LLMs via apps, CLIs and agents to do this work, acting as the architect and technical director.

**For the authoritative specification:** See [REQ-000 System Requirements](../requirements/REQ-000-Joshua26-System-Requirements-Specification.md)

**For physical setup:** See [INF-001 Bare Metal Configuration](./INF-001-bare-metal-machine-configuration.md)

**Registry:** `registry.yml` at repository root is the single source of truth for all containers and services — UIDs, GIDs, ports, and deployment hosts.

***

## Core Concepts

These are the foundational ideas that define how Joshua26 works. Understanding them is essential before reading any other document.

### The MAD Pattern

The **Multipurpose Agentic Duo (MAD)** is the fundamental architectural pattern of the Joshua26 ecosystem. A MAD is an autonomous actor that is simultaneously a server (exposing capabilities to others) and a client (using capabilities from others). The "Duo" is the inseparable combination of serving and using — a MAD that only serves is just a microservice; a MAD that only uses is just a client. The combination, governed by shared domain intelligence in both directions, is what makes it an autonomous actor.

See `docs/concepts/a5-the-mad-pattern.md` for the full concept.

### AE and TE

Every MAD is composed of two conceptually distinct aspects:

**Action Engine (AE)** — the physical system. All containers: gateway, databases, caches, sidecars, observability, the bootstrap kernel. Provides direct tool capabilities and, via joshua-net, access to the full tool set of every other MAD in the ecosystem. Also hosts Executor-driven processes. Both AE and TE use LangGraph for programmatic logic — LangGraph is a tool, not a layer.

**Thought Engine (TE)** — the cognitive intelligence. The Imperator and its cognitive apparatus: Progressive Cognitive Pipeline (PCP), inference, conversation-as-state. Conceptually distinct from the AE, though both run within the same pMAD. The AE calls into the TE, not the other way around.

See `docs/designs/HLD-state3-mad.md` for the AE/TE separation architecture and `ADR-054` for the framework decision record.

### pMAD and eMAD

**pMAD (Persistent MAD)** — a MAD that owns its own AE and its own TE. System domain (infrastructure). Always running as a deployed service with containers, gateway, and networking. Examples: the context broker, the inference broker, the observability service.

**eMAD (Ephemeral MAD)** — a MAD that has its own TE but no AE of its own. Subject matter domain (expertise). Exists only during StateGraph execution, hosted by a pMAD. An eMAD is a library package — pure cognitive intelligence with no infrastructure. Examples: the engineering agent, the security analyst.

The eMAD is a direct consequence of the AE/TE separation: once the TE is a library package independent of infrastructure, an autonomous agent can exist without owning any containers.

### Agent Classes

Two agent classes, grounded in the primitives defined in `docs/concepts/a1-conversationally-cognizant-ai-systems.md`:

**Imperator** — the prime agent within any TE. Possesses Identity, Purpose, and Autonomy. Generates its own Intent. Self-directing. Both pMADs and eMADs have Imperators. The difference is domain type (system vs subject) and lifecycle (persistent vs ephemeral), not structure.

**Executor** — no Identity, Purpose, or Autonomy of its own. Cognitive but never independent. Many forms: sub-agents, AE tools, StateGraph workers. Not addressable externally.

See `docs/designs/HLD-joshua26-agent-architecture.md` for the full agent architecture.

***

## Architecture Patterns

### Container Architecture

State 3 is the target architecture. The container reduces to a **bootstrap kernel** — an irreducible core (Python runtime, web server, connection pool management, `install_stategraph()`, entry_points scanner). Everything else — both AE StateGraphs (infrastructure wiring, MCP tool handlers) and TE StateGraphs (Imperator, PCP, inference) — is dynamically loaded from Alexandria as versioned Python packages at runtime. Kaiser is the first State 3 pMAD.

State 2 (OTS infrastructure + LangGraph + Imperator in one image) is the current state of deployed platform pMADs. State 1 (Node.js gateway template) is transitional. State 0 (monolithic) is legacy and deprecated. All pMADs migrate toward State 3 as their infrastructure stabilises.

See `docs/designs/HLD-MAD-container-composition.md` for the full container architecture and `docs/designs/HLD-state3-mad.md` for the State 3 pattern.

### Package Caching

Alexandria pMAD (deployed 2026-03-09) provides transparent network caching proxies for PyPI (`alexandria-devpi`, irina:3141), NPM (`alexandria-verdaccio`, irina:4873), and Docker images (`alexandria-registry`, irina:5000). Alexandria also serves as the internal PyPI for StateGraph packages. HuggingFace / ML model caching is owned by Sutherland. See `docs/designs/HLD-unified-package-caching.md`.

### Storage

Two-volume pattern: all containers mount `/storage` (NFS shared) and `/workspace` (local per-host). See REQ-000 Section 3.

### Identity

Each service has unique UID from registry.yml, all use GID 2001 (administrators), non-root runtime. See REQ-000 Section 2.

### MCP Protocol

HTTP/SSE transport, domain-prefixed tool naming, config-driven gateway pattern. See REQ-000 Section 4.

### Resilience

Graceful recovery for internal dependencies, graceful degradation for external dependencies. See REQ-000 Section 7.

### Observability

Structured JSON logging to stdout/stderr, two-layer health checks. See REQ-000 Section 5.

***

## Key Documents

### Conceptual Foundations

These define the intellectual framework — what the system is and why it's built this way.

-   [a1-conversationally-cognizant-ai-systems.md](../concepts/a1-conversationally-cognizant-ai-systems.md) — The primitives: Identity, Purpose, Intent, Autonomy, Persona, Domain
-   [a5-the-mad-pattern.md](../concepts/a5-the-mad-pattern.md) — The MAD pattern, AE/TE, pMAD/eMAD, agent classes
-   [d1-system-3-react.md](../concepts/d1-system-3-react.md) — System 3 ReAct: three cognitive roles in the reasoning loop
-   [a2-conversation-as-state.md](../concepts/a2-conversation-as-state.md) — Conversation as the substrate of state
-   [d2-progressive-cognitive-pipeline.md](../concepts/d2-progressive-cognitive-pipeline.md) — Inbound cognitive processing pipeline
-   [b1-the-quorum-pattern.md](../concepts/b1-the-quorum-pattern.md) — Parallel generation and ensemble reasoning

The full set of concept papers is in `docs/concepts/`. These are original research — the conceptual framework behind everything the system does.

### Architecture (System-Wide HLDs)

These define how the system is built.

-   [HLD-state3-mad.md](./HLD-state3-mad.md) — AE/TE separation, bootstrap kernel, dynamic StateGraph loading
-   [HLD-joshua26-agent-architecture.md](./HLD-joshua26-agent-architecture.md) — Agent classes, TE anatomy, ReAct modes, development workflow
-   [HLD-MAD-container-composition.md](./HLD-MAD-container-composition.md) — pMAD container architecture (State 0 → State 1 → State 2 → State 3)
-   [HLD-conversational-core.md](./HLD-conversational-core.md) — The conversational infrastructure trio (Henson, Rogers, Sutherland)
-   [HLD-software-factory-core.md](./HLD-software-factory-core.md) — Software factory macro-architecture (engineering agent, version control, Alexandria, build sequence)
-   [HLD-cicd-architecture.md](./HLD-cicd-architecture.md) — CI/CD pipeline architecture
-   [HLD-unified-package-caching.md](./HLD-unified-package-caching.md) — Package caching strategy (Alexandria pMAD)

### Specifications

-   [REQ-000 System Requirements](../requirements/REQ-000-Joshua26-System-Requirements-Specification.md) — Authoritative specification (ALL components must comply)
-   [registry.yml](../../registry.yml) — Single source of truth for all containers and services

### Practitioner Guides

In `docs/guides/`:

-   `mad-design-guide.md` — Designing a new pMAD (requirements, backing services, ports)
-   `mad-implementation-guide.md` — Implementing from template (containers, config, StateGraph)
-   `mad-build-checklist.md` — Build verification checklist
-   `mad-testing-guide.md` — Testing deployed pMADs (black-box and gray-box)
-   `mad-deployment-guide.md` — Deploying to target infrastructure
-   `mad-gate-reviewer-guide.md` — Gate review process
-   `mad-prometheus-metrics-guide.md` — Apgar-compatible metrics implementation
-   `docker-compose-file-strategy.md` — Compose file organisation and conventions
-   `gemini-analysis-workflow.md` — Gemini-finds/Claude-fixes loop for large-scale analysis

### Architecture Decision Records

In `docs/ADRs/`. ADRs are historical records of decisions — they are not modified after acceptance. Key recent ADRs:

-   `ADR-054` — AE/TE framework, Effector retirement, agent taxonomy, `install_stategraph`
-   `ADR-053` — Bidirectional gateway as network boundary with peer proxy
-   `ADR-051` — MCP gateway library pattern

### Infrastructure

-   [INF-001](./INF-001-bare-metal-machine-configuration.md) — Physical host setup and configuration

### pMAD-Specific Documentation

See `mads/[mad-name]/docs/` for:

-   HLD files (pMAD-specific architecture)
-   REQ files (pMAD-specific requirements)
-   README (quick start)

***

## Compliance

All pMADs must comply with [REQ-000](../requirements/REQ-000-Joshua26-System-Requirements-Specification.md).

**Verification:**

-   [REQ-000 Compliance Checklist](../audits/REQ-000-compliance-checklist.md)
-   [Exception Registry](../requirements/REQ-000-exception-registry.md)

***

## Document Metadata

**Version:** 2.0 **Created:** 2026-02-01 **Last Updated:** 2026-03-13 (Core concepts, AE/TE framework, restructured document navigation) **Change Control:** Updates require System Architect approval
