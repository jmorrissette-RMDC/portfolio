# ADR-010: Deprecate "Dumb LLM Calls" and Mandate "Intelligent eMAD Teams" for V6

**Status:** Accepted

**Context:**
Throughout its V0.x to V4.x evolution, Joshua's architecture has supported a pragmatic but suboptimal pattern for multi-entity collaboration, referred to as a "Dumb LLM Consulting Team" (defined in ADR-009). This pattern involves a MAD making parallel, raw LLM calls via `fiedler_send` and bearing the full cognitive load of synthesizing the results. While necessary as a bootstrap, this pattern is inefficient, does not foster collective learning, and places a high cognitive burden on the calling agent.

The V6.0 architecture introduces the "Intelligent eMAD Team" pattern, which uses autonomous, learning, ephemeral agents (eMADs) for true multi-agent collaboration. As the system evolves to V6.0, the "Enterprise Hardening" phase, it is critical to eliminate architectural ambiguities and enforce the most robust, efficient, and scalable patterns. The coexistence of both "dumb" and "intelligent" team patterns creates inconsistency and represents a legacy approach that must be formally addressed.

**Decision:**
Effective with the V6.0 architecture, the "Dumb LLM Consulting Team" pattern is officially **deprecated**, and the "Intelligent eMAD Team" pattern is **mandated** as the sole, standard mechanism for all multi-entity collaboration and complex task decomposition.

1.  **Deprecation of "Dumb LLM Consulting Teams":** The practice of a single MAD's Imperator making multiple, parallel `fiedler_send` calls to simulate a team is no longer an acceptable architectural pattern for new development. Existing instances of this pattern are to be flagged as high-priority technical debt and scheduled for refactoring.

2.  **Mandate of "Intelligent eMAD Teams":** All new and refactored workflows requiring the collaboration of multiple specialized entities MUST be implemented using the eMAD pattern. This involves a calling MAD requesting a specialized team of eMADs from a system service, which then collaborate as autonomous agents on the conversation bus.

3.  **Formalization of the "MAD Spawner" Service:** The V6.0 architecture will include a formal, production-grade, system-level **"MAD Spawner"** service. This service will be responsible for the entire lifecycle management of eMADs, including secure instantiation from role-based templates, health monitoring, resource management, and graceful termination.

4.  **Core Documentation Update:** This decision will trigger a formal update to core architecture documents, including the `Joshua_System_Roadmap.md`, to reflect that eMAD-based collaboration is the definitive, standard operational mode for V6 and beyond.

**Consequences:**

*   **Positive:**
    *   **Architectural Consistency:** Enforces a single, superior, and unified pattern for multi-agent collaboration across the entire ecosystem.
    *   **Maximizes Collective Learning:** Guarantees that all collaborative work contributes to the persistent, role-based learning models of the eMADs, accelerating system-wide improvement.
    *   **System-wide Efficiency and Scalability:** Drastically reduces the cognitive load on individual MADs. The system scales by instantiating intelligent, autonomous teams, which is a more robust and efficient scaling model.
    *   **Enhanced Predictability and Stability:** Standardizing on the eMAD pattern makes the system's behavior for complex tasks more predictable, observable, and reliable, which is a core requirement of an "Enterprise Ready" system.

*   **Negative:**
    *   **Increased Overhead for Simple Collaboration:** A developer can no longer quickly script a "dumb" parallel LLM call for a simple brainstorming task. They must use the more formal eMAD instantiation process, which carries a higher initial overhead. This is deemed an acceptable trade-off for a mature, production-grade system.
    *   **Refactoring Effort:** Creates a clear mandate to refactor any remaining legacy implementations of the "dumb" pattern.
    *   **Critical Dependency:** Elevates the "MAD Spawner" to a critical, Tier-1 infrastructure service that must be highly available and robust.

*   **Neutral:**
    *   This ADR marks a significant milestone in Joshua's maturity, formally transitioning from flexible, early-stage patterns to hardened, standardized, and scalable architectural commitments.

---
---

## Appendix A: Detailed Architectural Rationale

### A.1. The "Why Now?": V6 as the Enterprise Hardening Phase

The Joshua roadmap designates V6 as the "Enterprise Hardening" phase. This implies a shift in architectural philosophy from *flexibility and experimentation* (characteristic of V0-V4) to *stability, predictability, and standardization*.

At this stage of maturity, the existence of two competing patterns for a core function like multi-agent collaboration is no longer acceptable. The "dumb" pattern, while a useful bootstrap, is a liability in a production system due to its inefficiency and lack of learning. Mandating the eMAD pattern is a classic hardening decision, ensuring the entire ecosystem adopts the architecturally superior and more scalable model.

### A.2. The Shift from "Simulated Teams" to "True Collaboration"

This decision formalizes the move away from what is essentially a **single-agent simulation of a team** to **true multi-agent collaboration**.

*   **Deprecated Pattern:** A single Imperator *pretends* it is working with a team by calling multiple stateless LLMs. The entire cognitive process—synthesis, conflict resolution, iteration—is centralized in one agent's thought process. This is a performance bottleneck and a single point of cognitive failure.

*   **Mandated Pattern:** A team of multiple, autonomous, learning agents is instantiated. Each eMAD has its own PCP and contributes its specialized intelligence. The cognitive process is **distributed**. The `Lead_Engineer_eMAD` plans, the `QA_Engineer_eMAD` critiques, and they resolve conflicts through genuine dialogue on the conversation bus. This is a more resilient, scalable, and intelligent model.

### A.3. Fiedler's Role Solidified

This decision reinforces the outcome of ADR-009. Fiedler's role is to be an expert **consultant on LLMs**, not an orchestrator of agent teams.

*   In the deprecated pattern, Fiedler was tangentially involved in "team" creation by serving the raw LLM calls.
*   In the mandated V6 architecture, Fiedler's role is clear and distinct: it serves as a critical service *to* the individual eMADs that form a team. An eMAD, upon instantiation, will consult Fiedler to determine the best LLM to power its own internal Imperator for the task at hand. This respects the distributed cognition model of the Joshua ecosystem.

By formalizing this, we are making a clear statement about the architecture: Joshua's intelligence is in its **community of agents**, not in a central orchestrator. This ADR makes that principle manifest for multi-agent collaboration.
