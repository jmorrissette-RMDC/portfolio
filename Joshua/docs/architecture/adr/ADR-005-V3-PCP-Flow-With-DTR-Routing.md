# ADR-005: Define V3 PCP Cognitive Flow with DTR Multi-Path Routing

**Status:** Accepted

**Context:**
With the introduction of the Learned Prose-to-Process Mapper (LPPM, Tier 2) in Joshua's V3.0 architecture, the system gains the ability to automate multi-step workflows. A clear architectural decision is needed on how requests are triaged and routed between the DTR (Tier 1), the new LPPM (Tier 2), and the existing Imperator (Tier 4). The efficiency of the entire PCP hinges on the DTR's ability to act as an intelligent, high-speed gatekeeper, protecting the more expensive cognitive tiers from unnecessary load.

**Decision:**
The V3.0 PCP cognitive flow will be orchestrated by the **Decision Tree Router (DTR)**, which will function as an **intelligent, three-path dispatcher** for all incoming requests. Based on its analysis of an incoming request, the DTR will route it down one of three exclusive paths:

1.  **Path 1: The Reflex Arc (DTR -> Action Engine)**
    *   **Trigger:** The DTR identifies the request as a deterministic command or highly unambiguous, short "CLI-like" prose with extremely high confidence (>99%). This includes direct tool invocations (e.g., `horace_read_file`) or simple natural language mappings (e.g., "list files in /data").
    *   **Action:** The request **bypasses the entire Thought Engine cascade** (LPPM, CET, Imperator) and is sent directly to the MAD's Action Engine for execution.
    *   **Purpose:** To provide microsecond-level, lowest-cost responses for routine, high-frequency operations. This is the "spinal reflex" of the system.

2.  **Path 2: The Instinctive Workflow (DTR -> LPPM)**
    *   **Trigger:** The DTR identifies the request as more complex prose that does not map to a single command but has a high confidence match (>90%) to a known, multi-step *process pattern* that the LPPM has learned (e.g., "Generate X Report," "Onboard Y Data Source").
    *   **Action:** The request is routed to the **LPPM (Tier 2)**. The LPPM then takes responsibility for recognizing and executing the corresponding workflow (e.g., via its internal LangGraph engine).
    *   **Purpose:** To automate complex but repetitive tasks in milliseconds to a few seconds, acting as the "learned motor pattern" of the system.

3.  **Path 3: The Deliberative Thought (DTR -> CET -> Imperator)**
    *   **Trigger:** The DTR cannot match the request to a deterministic command or a known LPPM process with sufficient confidence. This includes novel, ambiguous, or strategically complex requests (e.g., "Design a new agentic framework").
    *   **Action:** The request is escalated up the full cognitive cascade, first to the **CET (Tier 3)** for strategic context engineering, and then to the **Imperator (Tier 4)** for deliberative, first-principles reasoning.
    *   **Purpose:** Reserves the system's most powerful (and expensive) cognitive resources only for tasks that genuinely require deep LLM-based understanding and creative problem-solving.

**Consequences:**

*   **Positive:**
    *   **Maximized Efficiency & Cost-Effectiveness:** This multi-path routing is fundamental to the PCP's ability to minimize LLM usage and computational costs by ensuring tasks are handled by the cheapest capable tier.
    *   **Improved Responsiveness:** The system provides varied response times tailored to task complexity, leading to a more natural and satisfying user experience.
    *   **Clear Tier Responsibilities:** Explicitly defines the boundaries and hand-offs between the DTR, LPPM, and Imperator, enhancing architectural clarity.
    *   **Foundational for Learning:** Provides the structured feedback necessary for the DTR to learn its routing rules and for the LPPM to learn its workflow patterns.

*   **Negative:**
    *   **DTR Criticality:** The accuracy and performance of the DTR become paramount. Misrouting by the DTR could lead to inefficiency (escalating simple tasks) or failure (misinterpreting complex tasks as simple).
    *   **"Cold Start" Performance:** Until the DTR has learned sufficient routing patterns, a higher proportion of tasks will fall to the more expensive Imperator path, impacting initial system efficiency.

*   **Neutral:**
    *   This decision formally specifies the V3.0 cognitive flow, building upon the DTR's design (ADR-006) and LPPM's architecture (ADR-004) to realize the PCP's core principles.

---
---

## Appendix A: Detailed Rationale & Context for V3 PCP Cognitive Flow

### A.1. The "Why": Optimizing Cognitive Load

The Progressive Cognitive Pipeline (PCP) is inspired by biological cognition, where simple reflexes bypass the brain, and learned behaviors operate automatically, reserving conscious thought for true novelty. The V3.0 cognitive flow is designed to directly embody this principle, creating clear "fast paths" for routine tasks and reserving expensive LLM cycles for truly deliberative reasoning.

In V1 and V2, a significant portion of tasks requiring multi-step automation or even moderately complex commands would still fall to the Imperator. This is computationally expensive and slow. The V3.0 flow aims to drastically reduce this burden.

### A.2. DTR's Role as the Central Dispatcher

The DTR (Decision Tree Router) is not a simple filter. It's an intelligent, data-driven dispatcher that makes the initial routing decision for *every* incoming request. Its goal is to minimize the computational cost of processing a request while maximizing accuracy. It leverages the following aspects:

*   **High-Speed Feature Analysis:** As discussed in ADR-006, the DTR performs NIDS-style feature extraction to rapidly classify message patterns without deep semantic understanding. This allows it to operate at microsecond latencies.
*   **Learned Confidence:** The DTR's underlying online ML model (e.g., Hoeffding Tree) provides a confidence score for each classification. This score is critical for deciding which path to take:
    *   **Very High Confidence:** Directly execute via Action Engine (Path 1).
    *   **High Confidence (Process Match):** Route to LPPM (Path 2).
    *   **Low Confidence (Novel/Ambiguous):** Escalate to CET/Imperator (Path 3).

### A.3. Interaction Between Tiers (The "Cascade")

The V3 flow establishes the sequential cascade that defines the PCP:

*   **DTR as Gatekeeper:** Every request passes through the DTR first. This prevents the LPPM, CET, or Imperator from wasting resources on tasks that could be handled more cheaply.
*   **LPPM as Instinctive Executor:** If the DTR identifies a process, the LPPM takes over. This is the "instinctive" layer. It executes pre-learned LangGraph workflows (as defined in ADR-004). If the LPPM itself fails or encounters a novel element *within* a learned process, it will escalate to the CET/Imperator.
*   **CET/Imperator as Deliberative Brain:** Only if the DTR cannot confidently route, or if the LPPM escalates, does the request reach the full power of the Imperator, with the CET ensuring it receives the most optimized context possible (V4 feature, but the path is established here).

### A.4. The Learning Feedback Loop

This explicit three-path routing is crucial for the PCP's long-term learning:

*   **DTR Learning:** The DTR's online learning model constantly refines its decision tree based on the observed outcomes of its routing choices. A successful LPPM execution after a DTR route reinforces that pattern. An Imperator execution after a DTR route (due to low confidence or LPPM failure) provides valuable feedback for the DTR to adjust its confidence thresholds or even learn new patterns.
*   **LPPM Learning:** The LPPM learns its workflow patterns by observing the Imperator's successful orchestrations (downward knowledge distillation). The DTR now acts as the trigger for these learned patterns.
*   **LPPM to DTR Bypass:** Crucially, as the DTR observes repeated, successful LPPM executions for specific trigger phrases, it will learn to bypass the LPPM entirely, effectively compiling the LPPM's workflow directly into a DTR reflex (as detailed in ADR-006 Appendix A.4).

This V3 cognitive flow is a major step in realizing Joshua's vision of a self-optimizing, adaptive, and highly efficient multi-agent system.