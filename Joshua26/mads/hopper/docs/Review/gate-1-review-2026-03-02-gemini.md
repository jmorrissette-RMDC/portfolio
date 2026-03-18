**Reviewer:** Gemini
**Gate:** 1
**MAD:** hopper
**Date:** 2026-03-02

## Gate 1: FAILED

The Hopper design provides a highly sophisticated and agentic architectural plan that successfully breaks away from single-agent typing loops. However, the document misses several strict ecosystem compliance requirements regarding volume mounting, network routing isolation, and the thin gateway mandate. These architectural issues must be addressed before implementation begins.

### Blockers

1. **Missing Registry Entry Definition (REQ-000 §6.3)**
   `REQ-hopper.md` fails to define the expected `registry.yml` entry. All MADs must have their network identity, port, UID, GID, and host affinity explicitly defined in the design phase.

2. **Incorrect Volume for Source Code & Missing Two-Volume Policy (REQ-000 §3.1, §3.4)**
   Section 12 states: "Hopper requires `/workspace` mount for source file read/write during code generation." In the Joshua26 architecture, the persistent project repository lives on shared storage (e.g., `/storage/projects/Joshua26`), while `/workspace` is for local host-bound, high-speed ephemeral or database storage. Furthermore, REQ-000 §3.1 mandates that BOTH `storage` and `workspace` volumes be mounted. Hopper must mount `/storage` to access the codebase and `/workspace` for local temporary execution artifacts.

3. **Missing Peer Proxy Declarations for Network Isolation (REQ-000 §7.4.1)**
   Sections 7.3 and 8.1 describe Hopper calling `starret` (for deployment), `rogers` (for context), and `sutherland` (for models). However, per REQ-000 §7.4.1, `hopper-langgraph` is strictly isolated on `hopper-net` and cannot reach `joshua-net` directly. The REQ must explicitly state that `starret`, `rogers`, and `sutherland` will be declared in the gateway's `config.json` `peers` section, allowing `hopper-langgraph` to route outbound calls securely through the gateway's `/peer/{peer}/{tool}` endpoint.

4. **Thin Gateway Mandate Violation for Custom SSE Endpoint (REQ-000 §4.8)**
   Section 2.3 states Hopper exposes "a streaming SSE endpoint wrapping LangGraph's native .astream_events()". REQ-000 §4.8 strictly mandates that the gateway `server.js` remain minimal (< 20 lines) and unmodified from the `mads/_template`. Exposing a custom SSE stream endpoint directly on the gateway would require custom routing code, directly violating this rule. The design must clarify how this stream is exposed (e.g., proxying an endpoint from the langgraph container via `config.json` routing, wrapping it in a standard MCP tool, or registering a formally approved exception).

### Observations

1. **Instruction Set Library Path:**
   Section 7.2 places the version-controlled instruction sets at `/workspace/hopper/instruction-sets/`. If these instruction sets are version-controlled with the codebase, they should either be read from the source repository at `/storage/projects/Joshua26/mads/hopper/instruction-sets/` or built into the container image at `/app/instruction-sets/`. Writing permanent files to `/workspace` risks data loss, as it is meant for host-local or temporary data.
2. **Stateless Nature:**
   Section 9 correctly identifies Hopper as stateless (no databases), relying entirely on Rogers and GitHub for state. This perfectly aligns with the ecosystem's philosophy of minimizing redundant persistence layers.

### Recommendations

1. **Context Window Limitations for Lead Synthesizer:**
   Section 5 states the Lead (Gemini Pro) will ingest all revised drafts simultaneously, noting it "requires massive context". While models like Gemini 1.5 Pro support massive token contexts, consider implementing a token-counting safety check or chunking strategy in `develop_tech_asset` before sending the prompt to avoid hard API failures on exceptionally large modules.
2. **Execution Safety & Test Loop Limits:**
   In Section 7.4 (The Fix and Deploy Loop), there is a risk of infinite loops if tests are consistently flaky or the escalation fails repeatedly. The "Graduated Safety Valve" (Section 8.4) appropriately applies to the Quorum, but `software_engineer`'s execution loop should also have a strict retry limit (e.g., max 5 iterations) before halting and generating a `quorum-impasse` issue.
3. **Review/Audit Output Pathing:**
   For reviews generated via `develop_doc` (Section 7.5), ensure the system prompt explicitly instructs the LLM to write to `mads/[target-mad]/docs/Review/` adhering to the reviewer guide naming patterns (e.g., `gate-X-review-YYYY-MM-DD-[model].md`), rather than dropping them in generic workspace directories.