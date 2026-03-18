# ADR-014: LLM Selection as a Dynamic Cognitive Step within the PCP

**Status:** Accepted (Updated execution model per ADR-034/ADR-035)

**⚠️ ARCHITECTURAL UPDATE (2025-12-21):**
This ADR's **core principle** (dynamic LLM selection as a cognitive step) remains fully valid. However, the **execution model** has been updated by ADR-035: Direct Access AI Model Nodes.

**What Changed:**
- **Before:** MADs accessed external LLMs "via Fiedler" (implied proxy/gateway execution)
- **After:** MADs use `joshua_ai_access` library nodes to access LLMs **directly** (no Fiedler execution)
- **Still Valid:** Fiedler's role as **recommender** via `fiedler_recommend_model` (advisory, not execution)

**Current Flow:**
1. MAD's PCP queries Fiedler: `fiedler_recommend_model(constraints={...})`
2. Fiedler recommends model(s) via its own PCP reasoning
3. MAD uses `AiderNode` or provider-specific node to **directly** access the recommended LLM

See ADR-034, ADR-035, and ADR-036 for complete architecture.

**Context:**
The Joshua ecosystem will have access to a heterogeneous set of cognitive resources: powerful, expensive external LLMs (via Fiedler) and fast, cheap local LLMs running on available hardware. A key architectural question is how a MAD decides which resource to use for a given task. A static configuration (e.g., "always use local LLM for planning") would be brittle and suboptimal. Furthermore, Fiedler's role in this selection process needs precise definition to align with its identity as a specialist MAD with its own Progressive Cognitive Pipeline (PCP).

**Decision:**
The selection of which LLM to use for a cognitive task will be treated as a **dynamic, deliberative step within the calling MAD's own PCP loop**. This makes "cognitive resource allocation" a first-class reasoning task. Fiedler's role is to act as an expert consultant in this process, with its own internal PCP to optimize how it provides recommendations.

1.  **LLM Selection is a Cognitive Act:** A MAD's PCP (Imperator or LPPM) will actively reason about which cognitive resource is appropriate for each sub-task. It will use a fast, local LLM for internal "thinking" steps like planning and decomposition, and will strategically choose to use powerful, external LLMs only for the final, high-value, creative, or knowledge-intensive steps.

2.  **Fiedler as the "Compute-Aware" Recommender:** Fiedler's primary cognitive function is to provide expert recommendations on model selection. A MAD's PCP will query Fiedler with abstract constraints (e.g., `constraints={'latency': 'low', 'cost': 'zero'}` or `constraints={'capability': 'state_of_the_art'}`).

3.  **Fiedler's Internal PCP for Recommendations:** Fiedler itself will have its own PCP to handle these recommendation requests efficiently:
    *   **Fiedler's DTR/LPPM:** Will learn to handle common, repetitive recommendation requests (e.g., "give me a fast, cheap model") by providing a standard, cached, or rule-based answer in milliseconds.
    *   **Fiedler's Imperator:** Will only be engaged for novel or complex recommendation requests (e.g., "what is the best model for a novel multi-modal analysis task balancing energy efficiency and output quality?"), where it can perform its own deep reasoning or web research.

**Consequences:**

*   **Positive:**
    *   **Massive Cost & Latency Reduction:** The bulk of a MAD's internal "thinking" and orchestration can be done using near-free, instantaneous local LLM calls, dramatically reducing the number of expensive external API calls.
    *   **Truly Adaptive Cognition:** MADs can dynamically manage their own cognitive resources, using powerful models only when necessary. This makes the entire system more efficient and scalable.
    *   **Reinforces Fiedler's Expert Role:** Fiedler's expertise in the LLM landscape is fully utilized, but its own cognitive load is also optimized by its internal PCP. This is a perfect example of the Cellular Monolith pattern.
    *   **Enhances PCP Power:** The PCP is no longer just routing tasks, but actively managing cognitive resource allocation, a significant step up in sophistication.

*   **Negative:**
    *   **Increased Local Hardware Dependency:** The effectiveness of this pattern is highly dependent on the availability and capability of the local inference hardware.
    *   **Increased Orchestration Complexity:** The calling MAD's PCP must be sophisticated enough to manage this two-level (local vs. external) cognitive process.

*   **Neutral:**
    *   This decision formalizes a highly sophisticated, multi-level cognitive architecture for the entire Joshua ecosystem, leveraging heterogeneous compute resources.

---
---

## Appendix A: Detailed Architectural Rationale

### A.1. The Shift to Heterogeneous Cognitive Computing

This decision moves Joshua's architecture beyond simply using LLMs to actively managing a *portfolio of cognitive resources*. The availability of powerful local inference hardware is a game-changer. It introduces a new axis for optimization: `(local, fast, cheap)` vs. `(external, slow, expensive)`. An intelligent agent must be able to navigate this trade-off dynamically.

### A.2. The "Cognitive Choice" within the Loop

The core innovation is making the choice of LLM an explicit step *within* the cognitive loop. A MAD's Imperator doesn't just have a single "think" function; it has a palette of thinking tools.

**Example Workflow for a Complex Task:**
1.  **Decomposition (Local LLM):** The Imperator receives a complex goal. It makes a fast, local call to break the goal into a plan of sub-tasks.
2.  **Sub-Task Analysis (Local LLM):** For each sub-task, the Imperator makes another fast, local call to reason about the resources needed. "Sub-task A is research -> needs web access + powerful external LLM. Sub-task B is file I/O -> needs Horace tool."
3.  **Execution:** The Imperator orchestrates the execution, making cheap local calls for its own internal state management and expensive external calls only for the specific sub-tasks that require world-class reasoning or knowledge.

This solves the primary drawback of agentic loops: the high cost and latency of the "thinking" steps. With this architecture, thinking becomes cheap; only the final, high-value actions are expensive.

### A.3. Fiedler's PCP: An Expert in its Own Domain

This ADR clarifies that the PCP is a universal pattern for *all* MADs, including specialists like Fiedler. Fiedler's "domain" is the LLM market. Its PCP becomes an expert at navigating this domain efficiently.

-   **Fiedler's DTR** might learn a reflex: "If request contains `cost: zero`, and local models are available, route to local model."
-   **Fiedler's LPPM** might learn a workflow: "If request is for `code_generation`, and the user has not specified a model, the standard process is to recommend `gpt-5` first, with `deepseek-coder` as a fallback."
-   **Fiedler's Imperator** is reserved for the truly hard questions that require it to synthesize information about new models, complex pricing structures, or novel benchmarks, potentially using Malory to perform web research.

This ensures that Fiedler itself is a highly efficient agent, providing fast, cheap recommendations for common cases and deep, reasoned analysis for novel ones, perfectly mirroring the cognitive philosophy of the entire Joshua system.
