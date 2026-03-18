# pMAD Design Guide

**Purpose:** Guide for a design session producing a delta REQ document for a new pMAD.

**Output:** `mads/[mad-name]/docs/REQ-[mad-name].md` — a delta REQ describing only what differs from the template baseline.

***

## Plan File

The plan file is the MAD's build log — it persists across all phases (design → implementation → deployment). Cursor does not have a built-in plan file system; you designate which file is the plan and work from it.

**Recommended location:** `mads/[mad-name]/docs/[mad-name]-plan.md`

**At session start (design creates the plan):** Create the plan file at the path above, copy the template (end of this guide) into it, and fill it in. Tell Cursor this is the plan file to read and update.

**During the session:** Update the plan file as you work:

-   Mark completed steps with timestamps
-   Log key decisions and their rationale
-   Record any issues encountered and how they were resolved
-   Note deviations from the original plan and why

**The plan file is a retrospective log.** Anyone reading it after all phases are complete should be able to understand the full history of the MAD build — what happened, what decisions were made, and why.

**Hand-off:** At the end of this phase, tell the next session the plan file path so it can continue from it.

***

## What You Need to Know

### Required Reading (in this order)

1.  `docs/designs/HLD-Joshua26-system-overview.md` — and all documents linked within it
2.  `docs/requirements/REQ-000-Joshua26-System-Requirements-Specification.md` — authoritative specification
3.  `mads/_template/README.md` — template overview and copy-paste workflow
4.  `mads/_template/docs/REQ-langgraph-template.md` — full LangGraph pattern (1061 lines). This is the baseline your delta REQ builds on.
5.  `registry.yml` — UIDs, ports, host assignments
6.  `docs/guides/mad-build-checklist.md` — actionable compliance checklist
7.  **docs/designs/HLD-MAD-container-composition.md** – how to build a pMAD container group

### Key Concepts

**Delta REQ:** Your pMAD's REQ document describes ONLY what differs from the template. The templates already handle gateway wiring, health checks, logging, MCP protocol, and container structure. Your delta covers:

-   pMAD purpose and capability
-   MCP tool definitions (names, schemas, routing)
-   Backing service choices and justification
-   LangGraph flow architecture (AE and TE flows)
-   Data models (schemas, relationships)
-   pMAD-specific deployment notes

**Flow types:**

-   **AE flows:** Deterministic execution (database queries, API calls, infrastructure wiring) — exposed as MCP tools in the AE StateGraph
-   **TE flows:** Cognitive reasoning via the Imperator (planning, analysis, multi-step orchestration) — loaded into the TE StateGraph and invoked by the AE
-   Both are LangGraph StateGraphs; in State 1/2 they coexist in the same langgraph container, in State 3 they are separate packages

**Container types:** Gateway (`[mad]`), LangGraph (`[mad]-langgraph`), backing services (`[mad]-postgres`, `[mad]-redis`, etc.). Not all pMADs need backing services.

**Networking:** Gateway bridges `joshua-net` + `[mad]-net`. All internal containers on `[mad]-net` only. See REQ-000 §7.4.1.

***

## What You Need to Do

### Phase A: High-Level Requirements

Define the pMAD's purpose and scope:

1.  **Purpose** — What capability does this MAD provide? What problem does it solve?
2.  **MCP tools** — List tool names (`[domain]_[action]` convention), brief descriptions, expected inputs/outputs
3.  **Dependencies** — What backing services? What other MADs does this depend on?
4.  **Registry allocation** — UID, port, host from `registry.yml` (or request new ones)

Write these to `mads/[mad-name]/docs/REQ-[mad-name].md`.

### Phase B: Architecture Decisions

Expand the REQ with architectural choices:

1.  **Backing services** — Choose and justify: PostgreSQL (structured data, ACID), Redis (caching, ephemeral state), Neo4j (graph traversals), none (stateless). Document WHY.
2.  **Container list** — Which containers this pMAD group includes
3.  **Flow types** — Which tools are programmatic flows (deterministic) vs Imperator flows (cognitive)?
4.  **Health strategy** — Critical dependencies (hard fail) vs optional dependencies (graceful degradation)

### Phase C: Detailed Design

Fill in implementation-ready specifications:

1.  **Tool schemas** — Full JSON schemas for each tool (input/output, validation rules, error cases)
2.  **Data models** — Tables, columns, types, constraints, indexes, relationships
3.  **Flow details** — State definitions, node implementations, edge conditions, endpoint mappings to config.json
4.  **Configuration** — config.json structure, port assignments, dependency hostnames, routing timeouts
5.  **Verification** — How to test each tool, health check validation, integration scenarios

### Phase D: Build Checklist + Gate Reviewer (Gate 1)

1.  **Build checklist verification** — run through `docs/guides/mad-build-checklist.md` against the delta REQ. Verify that the design is compliant with REQ-000 before handing off to the gate reviewer. The checklist covers offline builds, identity/permissions, storage, MCP protocol, observability, documentation, and networking. Fix any gaps in the REQ.
2.  **Discuss your checklist findings with the user** — Once fixes are applied per the user's direction, ask the user for authorization to move to the Gate 1 review.
3.  **Gate reviewer runs Gate 1** — Invoke external reviewer (Gemini, Claude, or Codex) via CLI. Use this prompt (substitute `[mad-name]` and `[YYYY-MM-DD]`):

    > Run Gate 1 (post-design) review for [mad-name]. Read and follow `docs/guides/mad-gate-reviewer-guide.md` in full — it contains the Reading List, approach, and output format. Write your review to `mads/[mad-name]/docs/Review/gate-1-review-[YYYY-MM-DD]-[reviewer].md`. Use the write tool to save the file. Substitute [reviewer] with claude, gemini, or codex.

    Consider running multiple models for broader coverage.
4.  **Discuss findings** — the gate reviewer's findings (blockers and observations) are discussed with the user before any changes are made. The user decides which items to address.
5.  **Address blockers** — fix any blockers in the delta REQ before proceeding to implementation. Record changes and rationale in the plan file.
6.  **Documentation alignment** — check if any system-wide docs need updating (HLDs, guides, registry.yml).

***

## Plan File Template

Copy this into your plan file and adapt. This plan file will carry through all three phases.

```markdown
# [MAD-NAME] Build Plan

## pMAD Overview
[Brief description of capability]

---

## Design Phase

### Required Reading
- [ ] HLD-Joshua26-system-overview.md (and linked docs)
- [ ] REQ-000 (authoritative spec)
- [ ] Template README + REQ-langgraph-template.md
- [ ] registry.yml
- [ ] mad-build-checklist.md

### Design Steps
1. Phase A: Purpose, tool list, dependencies, registry allocation
2. Phase B: Backing services, container list, flow types, health strategy
3. Phase C: Tool schemas, data models, flow details, config, verification
4. Phase D: Gate reviewer (Gate 1) — external reviewer (Gemini/Claude/Codex) via CLI, findings discussed with user

### Design Output
- mads/[mad-name]/docs/REQ-[mad-name].md (delta REQ)
- Gate 1 findings addressed

### Design Progress Log
<!-- Update as you work -->
```

***

## Session Wrap-Up

When the design phase is complete (Gate 1 passed):

**Do NOT move the plan file yet** — it continues into implementation and deployment. Tell the gate reviewer the plan file name for hand-off.

***

## Common Design Patterns

| Pattern                  | Backing Services   | Use Case                                 |
|--------------------------|--------------------|------------------------------------------|
| Stateless transformation | None               | Text processing, format conversion       |
| Database-backed          | PostgreSQL         | CRUD operations, structured data         |
| Cache-enhanced           | PostgreSQL + Redis | Read-heavy workloads, lookups            |
| Graph relationship       | Neo4j              | Knowledge graphs, traversals             |
| Cognitive reasoning      | Minimal/none       | LLM planning, analysis, decision support |

***

## Next Step

Once design is approved → **implementation phase**: `docs/guides/mad-implementation-guide.md`

***

**Related:** [REQ-000](../requirements/REQ-000-Joshua26-System-Requirements-Specification.md) · [Build Checklist](./mad-build-checklist.md) · [Template README](../../mads/_template/README.md) · [Gate Reviewer Guide](./mad-gate-reviewer-guide.md)
