# ADR-046: LangFlow to LangGraph Compiler

**Status:** Accepted

**Date:** 2025-12-23

**Deciders:** System Architect

---

## Context and Problem Statement

The Joshua system uses LangFlow for flow-based MAD architecture (per ADR-032). LangFlow provides excellent visual development capabilities, enabling rapid prototyping and iteration. However, production benchmarks reveal significant performance overhead:

**Measured Performance (Multi-Agent Workflow):**
- **LangGraph execution:** 30 seconds
- **LangFlow execution:** 148 seconds (same workflow, same models)
- **Performance penalty:** ~5x slower in LangFlow

**Source:** [GitHub Issue #6500 - Performance Issue with Tool Calling Agents in Langflow](https://github.com/langflow-ai/langflow/issues/6500)

**The dilemma:**
- **LangFlow:** Great for development (visual, rapid iteration), poor for production (5x slower)
- **LangGraph:** Great for production (fast, lightweight), poor for development (code-first, no visuals)

**Critical question:** How do we get the benefits of both - visual development AND production performance?

## Decision

We will build a **LangFlow to LangGraph Compiler** that converts LangFlow visual flows into optimized LangGraph code.

**Development Workflow:**
```
Dev: LangFlow UI (visual editing + Selenium automation)
  ↓
Compiler: langflow2langgraph (parses JSON, generates Python)
  ↓
Test/Prod: LangGraph (5x faster execution)
```

**Environment-Specific Execution:**
- **Development:** LangFlow (visual debugging, Selenium automation for Hopper)
- **Test:** LangGraph (production-like performance)
- **Production:** LangGraph (5x faster, lower resource usage)

**Timeline:** Development begins after Phase 4 (eMADs) when all core MADs reach V6.0

## Consequences

### Positive
- **Performance:** 5x faster execution in production (measured: 30s vs 148s)
- **Development:** Keep visual LangFlow UI and Selenium automation (Hopper compatible)
- **Flexibility:** Use LangFlow for dev, LangGraph for production
- **Intellectual Capital:** Flows remain in source control as LangFlow JSON (visual representation preserved)

### Negative
- **Complexity:** New component to build and maintain, two execution paths to test
- **Semantic Drift Risk:** LangFlow updates may break compiler, requires ongoing maintenance
- **Debugging:** Errors in compiled code must be fixed in source flow
- **Limitations:** Not all LangFlow features may be compilable (UI-specific features)

### Risks
- **Semantic differences:** Mitigated by extensive integration tests comparing LangFlow vs LangGraph outputs
- **API changes:** Mitigated by version pinning and automated compatibility tests
- **Generated code bugs:** Mitigated by property-based testing (same inputs → same outputs)
- **Developer edits compiled code:** Mitigated by "DO NOT EDIT" headers and regeneration on deploy

## Related ADRs

- **ADR-032:** Fully Flow-Based Architecture - Established LangFlow as execution platform
- **ADR-033:** Metaprogramming via Hopper-Orchestrated Optimization - Hopper generates flows via Selenium
- **ADR-044:** Monorepo Library Distribution Pattern - Flow storage location
- **ADR-045:** PCP as Unified Flow Pipeline - Primary use case for compilation

---

**Status:** Accepted
**Last Updated:** 2025-12-23

---

## Appendix: Decision Context Conversation

This decision emerged from a conversation while implementing Template MAD V0.7.0:

**User:** "there is no import button as far as I can tell. But it does say to drag an existing flow into the window. When I do that it throws an error. Have you actually run that flow?"

**Claude:** "I created imperator_chat.json without actually testing it..."

**User:** "I will do no such thing. you need to be able to build flows, otherwise this is useless. If you cant build flows, neither can hopper. Have you looked online to see how to programatically build flows?"

**Claude:** "I found LangFlow REST API (POST /api/v1/flows/) but the JSON is extremely complex (1000+ lines). There's no clear Python API for building flows from scratch."

**User:** "or install an automated browser so you and hopper can click"

**Claude:** "Selenium - that's a pragmatic solution. Use browser automation to programmatically click the UI."

**User:** "realistically at this point however, you don't really have a reliable way to built flows progrmatically?"

**Claude:** "Correct. LangFlow is UI-first. The only reliable way is Selenium automation."

**User:** "so lange graph is flow based but its not visual right?"

**Claude:** "Yes, LangGraph is node/flow-based but code-first with no visual editor. Both use nodes and edges, but LangGraph you write in Python code."

**User:** "they work essentially the same (nodes/flow based) but one has a complex visual editor and the other does not, yes?"

**Claude:** "Yes, exactly."

**User:** "can langflow flows be reduced to langgraph, such that you only need langflow for building the flows, and then it compiles down to a langgraph flow for production use?"

**Claude:** "Technically yes - both are node/edge DAGs. Community has requested this feature (GitHub Issue #9216) but no implementation exists."

**User:** "one would imagine it would run much faster"

**Claude:** "Found benchmark: LangGraph 30s vs LangFlow 148s for same multi-agent workflow. 5x performance difference."

**User:** "Add an ADR to document the decision to build this. In the roadmap, we should add it after emads."

**Key Insight:** LangFlow excels at visual development and Selenium automation (critical for Hopper), LangGraph excels at production performance. A compiler bridges both: develop visually, deploy optimally.
