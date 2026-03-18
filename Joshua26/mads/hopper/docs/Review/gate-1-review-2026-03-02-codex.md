**Reviewer:** Codex
**Gate:** 1
**MAD:** hopper
**Date:** 2026-03-02

- **Gate 1: FAILED** — the Hopper delta REQ has strong architectural direction, but it is not yet implementation-ready and does not yet satisfy key Gate 1 design requirements.

## Blockers

1. **Missing required plan file for phase continuity**
   - `mads/hopper/docs/hopper-plan.md` is not present.
   - `docs/guides/mad-design-guide.md` defines the plan file as a required artifact created in design and carried through implementation/deployment.
   - **Why blocker:** Gate 1 requires traceable design rationale and handoff continuity before implementation starts.

2. **Registry allocation and deployment identity are incomplete**
   - `mads/hopper/docs/REQ-hopper.md` does not define explicit UID/GID/port/host assignment for Hopper.
   - `registry.yml` has no `hopper` service entry.
   - **Why blocker:** REQ-000 and the design/build guides require registry-backed identity and host placement before implementation/deployment.

3. **Phase C detailed design content is missing**
   - The REQ is high-level, but it does not provide implementation-ready detail required by `docs/guides/mad-design-guide.md` Phase C:
     - MCP tool input/output JSON schema for `hopper_chat`
     - LangGraph state definitions and node/edge-level flow specification
     - `config.json` structure and routing/dependency declarations
     - concrete verification plan per tool/flow
   - **Why blocker:** Implementation cannot be performed deterministically from the current document.

4. **REQ-000 compliance deltas are not explicitly specified**
   - The REQ does not define concrete deltas for mandatory implementation constraints (identity, volumes, networking pattern, health checks, observability expectations, and error handling behavior) in a way that can be audited pre-implementation.
   - **Why blocker:** Gate 1 must catch compliance gaps before code exists; current text is conceptual but not auditable.

5. **Related-document references are unresolved**
   - `mads/hopper/docs/REQ-hopper.md` references documents that are not present at the referenced paths (for example, `HLD-joshua26-agent-architecture.md` and `HLD-software-factory-core.md`).
   - **Why blocker:** Normative references must resolve for implementers and reviewers to validate design assumptions.

## Observations

1. **Strong architectural intent**
   - The document clearly defines Hopper's role boundaries (Hopper vs Starret vs Rogers), stateless direction, and Quorum-oriented workflow philosophy.

2. **Current REQ reads like an HLD narrative more than a delta REQ**
   - The content is rich conceptually, but not structured enough yet as a "template delta" artifact for build execution.

3. **Model roster is specific but should remain alias-driven**
   - The REQ correctly points to aliases via Sutherland, but also embeds concrete model-family choices that may drift quickly.

4. **Instruction-set library vs dynamic orchestration needs one authoritative statement**
   - The REQ should state a single source of truth for how `software_engineer` receives task-specific instructions to avoid implementation ambiguity.

## Recommendations

1. **Add an implementation appendix to REQ-hopper**
   - Include:
     - `hopper_chat` JSON schema (input/output, error shape)
     - expected `config.json` skeleton
     - LangGraph state typing and node contract summaries
     - endpoint map (`/health`, `/mcp`, SSE stream behavior)

2. **Add a REQ-000 compliance matrix section**
   - For each relevant requirement family (build, identity, storage, MCP, observability, networking, resilience), state:
     - baseline inherited from template
     - Hopper-specific delta
     - planned verification method

3. **Create and maintain `mads/hopper/docs/hopper-plan.md` immediately**
   - Backfill design decisions and rationale already made.
   - Record Gate 1 findings and disposition decisions there before implementation.

4. **Resolve all document references in REQ-hopper**
   - Either create/move the referenced HLD files to the cited paths or update references to existing canonical paths.

5. **Promote deployment identity to explicit requirements**
   - Add Hopper's UID/GID/port/host requirements to REQ-hopper and align `registry.yml` before implementation starts.

