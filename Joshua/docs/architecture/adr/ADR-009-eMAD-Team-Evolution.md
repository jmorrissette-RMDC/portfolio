# ADR-009: Formalize the Evolution from "Dumb LLM Consulting Teams" to "Intelligent eMAD Teams"

**Status:** Accepted (Superseded by ADR-034/ADR-035 for LLM access pattern)

**⚠️ ARCHITECTURAL UPDATE (2025-12-21):**
This ADR describes Fiedler's role as an **LLM proxy** that MADs call via `fiedler_send` for LLM provisioning. This execution model has been **superseded by ADR-035: Direct Access AI Model Nodes**.

**Current Architecture (per ADR-035):**
- MADs use `joshua_ai_access` library nodes to access LLMs **directly** (no `fiedler_send` proxy)
- Fiedler provides **recommendations** via `fiedler_recommend_model` (advisor, not executor)
- The eMAD evolution roadmap described here remains valid, but LLM access is now direct

See ADR-034, ADR-035, and ADR-036 for the complete architectural pivot and node library architecture.

**Context:**
Joshua's vision includes complex multi-agent collaboration, often requiring the input or coordinated action of multiple specialized entities. An initial concept involved a "consulting team" where a MAD's Imperator would query multiple LLMs in parallel to gather diverse opinions. However, these raw LLM calls are "dumb"—the LLMs themselves do not learn from the interaction, retain state, or participate as autonomous agents, placing the entire cognitive burden of synthesis on the calling MAD. Joshua's roadmap includes intelligent, learning **eMADs (Ephemeral Multipurpose Agentic Duos)** for scalable, task-specific teams. A clear architectural decision is needed to delineate the transition from the temporary "dumb" pattern to the target "intelligent" pattern, and to clarify Fiedler's role in this evolution.

**Decision:**
Joshua's architecture will explicitly manage a two-stage evolution for multi-entity collaboration, moving from a temporary "Dumb LLM Consulting Team" pattern to a permanent "Intelligent eMAD Team" pattern. Fiedler's role will be consistently defined as an LLM Provisioning and Recommendation Service, serving individual MADs and eMADs, but **not** as an orchestrator of multi-agent teams.

**1. Stage 1: The "Dumb LLM Consulting Team" Pattern (Pre-eMADs Era)**
    *   **Context:** In the period before the eMAD architecture is fully implemented (i.e., V0.5 through V5.0).
    *   **Mechanism:** A calling MAD's Imperator will make multiple, parallel, independent LLM calls via `fiedler_send`.
    *   **Fiedler's Role (Proxy):** Fiedler acts as a **dumb proxy** or **LLM provisioner**, routing the calls and returning raw, independent responses.
    *   **Cognitive Burden:** The **calling MAD's own Imperator** bears the full cognitive burden of synthesizing these multiple, raw LLM responses.
    *   **Learning:** The individual LLM calls do not learn. However, the calling MAD's successful synthesis and subsequent actions contribute to its own PCP's learning via the conversation bus.

**2. Stage 2: The "Intelligent eMAD Team" Pattern (Post-eMADs Era, V6.0+)**
    *   **Context:** Once the eMAD architecture is fully implemented (Phase 4, MAD Version V6.0+), the "Dumb LLM Consulting Team" pattern will be deprecated.
    *   **Mechanism:** When a MAD requires team collaboration, it will request a **"MAD Spawner"** service (`Kaiser`) to instantiate a team of intelligent, learning **eMADs** tailored to the task (e.g., `Lead_Engineer_eMAD`, `QA_Engineer_eMAD`).
    *   **eMAD Nature:** Each eMAD is a full, autonomous agent with its own Thought Engine (PCP) and role-based learning. They collaborate as true participants on the Rogers bus.
    *   **Fiedler's Role (Consultant to eMADs):** Fiedler does **not** provision teams. Instead, it serves as a specialized **LLM Provisioning and Recommendation Service** to the individual eMADs. An eMAD's Imperator will query Fiedler (`fiedler_recommend_model`) to intelligently select the best LLM for its own internal reasoning tasks.

**Consequences:**

*   **Positive:**
    *   **Enables True Multi-Agent Collaboration:** The eMAD pattern facilitates genuine, distributed intelligence where each participant is an autonomous, learning agent.
    *   **Scalable Intelligence:** eMADs provide a highly scalable solution for burst workloads with zero idle resource consumption and persistent collective learning.
    *   **Reduces Cognitive Burden:** The complex task of synthesis is distributed among the expert eMAD team, rather than being centralized in the calling MAD.
    *   **Clarifies Fiedler's Role:** Fiedler's function is precisely defined as the system's "LLM expert," respecting the distributed cognition of other MADs.
    *   **Aligns with Joshua's Vision:** This evolution is a core step toward unbounded capability through self-evolving, collaborative agents.

*   **Negative:**
    *   **Significant Infrastructure Development:** The implementation of the eMAD pattern itself (`Kaiser`, `Moses`, and the eMAD framework) is a substantial V6.0+ engineering effort.

*   **Neutral:**
    *   This decision provides a clear architectural roadmap for managing multi-entity collaboration, from initial temporary solutions to the target state of intelligent eMADs.

---
---

## Appendix A: Detailed Architectural Rationale

### A.1. The Fundamental Flaw of "Dumb LLM Calls" for Team Collaboration

The initial concept of a "consulting team" using parallel `fiedler_send` calls, while a pragmatic bootstrap, is architecturally flawed for a true multi-agent system.

-   **Statelessness:** Each raw LLM call is stateless. The LLM has no memory of previous turns in the "team" interaction and does not learn from the outcome.
-   **No Autonomy:** The raw LLMs are text-in, text-out functions, not agents. They cannot take initiative, adapt their role, or engage in genuine dialogue.
-   **Centralized Cognitive Burden:** The entire overhead of synthesizing disparate opinions, identifying contradictions, managing a simulated multi-turn discussion, and iterating on a plan falls on the single Imperator of the calling MAD. This is inefficient and does not scale.
-   **No Collective Learning:** The "team" does not get smarter. Each "consulting" session is a fresh, expensive, and manually orchestrated event from the perspective of the calling MAD.

This pattern violates the spirit of Joshua's self-evolving, learning ecosystem.

### A.2. The Transformative Power of Intelligent eMAD Teams

The eMAD (Ephemeral Multipurpose Agentic Duo) pattern is Joshua's native solution for scalable, intelligent teams.

-   **Autonomous & Learning:** Each eMAD is a complete MAD instance with its own Thought Engine (PCP) and Action Engine. It loads a "role-based model" that improves over time from the collective experience of all eMADs in that role.
-   **Distributed Cognition:** The cognitive burden is distributed. A `Lead_Engineer_eMAD` plans, a `Junior_Engineer_eMAD` codes, and a `QA_Engineer_eMAD` tests. This is true collaboration.
-   **Contextual & Stateful:** eMADs are first-class participants on the Rogers bus, retaining context and state throughout their (ephemeral) lifecycle.
-   **Scalable:** eMADs are instantiated on-demand and terminated upon task completion, consuming resources only when active and enabling massive parallelization.

### A.3. Fiedler's Refined Role: The Specialized LLM Consultant

This evolutionary shift clarifies Fiedler's position. It is not a "team manager." Fiedler's expertise is the **LLM landscape itself.**

-   **Pre-eMADs:** Fiedler is a generic proxy for individual LLM calls.
-   **Post-eMADs:** Fiedler becomes a **specialized consultant to the eMADs themselves.** When an eMAD (e.g., a `Technical_Writer_eMAD`) needs to generate text, its internal Imperator will ask Fiedler, "Which LLM is best for writing clear, concise technical documentation?" Fiedler, using its unique knowledge base of model capabilities and historical performance, provides an intelligent recommendation. The eMAD then uses that recommended LLM via Fiedler's Action Engine.

This ensures Fiedler maintains its critical, specialized role as the "LLM expert" without usurping the distributed cognitive roles of other MADs or the emergent nature of eMAD team collaboration. This ADR formalizes this crucial separation and architectural growth path.
