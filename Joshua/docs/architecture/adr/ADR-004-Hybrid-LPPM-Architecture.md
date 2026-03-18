# ADR-004: Adopt a Hybrid CrewAI + LangGraph Architecture for V3 LPPM

**Status:** Accepted

**Context:**
The Learned Prose-to-Process Mapper (LPPM) for Joshua's V3.0 is designed to automate common multi-step workflows by learning patterns from the Imperator's operational history. The architectural challenge is to define a robust and efficient mechanism for both **recognizing** these process patterns from user requests and **executing** them effectively. A purely custom-coded approach would be complex and brittle. We need a solution that leverages mature frameworks for declarative definition and stateful execution.

**Decision:**
The V3.0 LPPM (Tier 2) will be implemented as a hybrid system that leverages **CrewAI's declarative vocabulary for process definition** and **LangGraph as the stateful execution engine** for those learned workflows.

This involves two primary components within the LPPM's design:

1.  **Process Pattern Recognition (ML Component):**
    *   **Goal:** To classify an incoming user request (prose) into a recognized multi-step process.
    *   **Inspiration (CrewAI Concepts):** The LPPM's machine learning model will be trained to identify and map user requests to specific, CrewAI-inspired process patterns (e.g., `Process.sequential`, `Process.hierarchical`). It will also learn to extract the necessary parameters for these processes.
    *   **Learning:** This ML component will be trained via **downward knowledge distillation**, observing successful multi-step orchestrations performed by the Imperator (Tier 4) in the conversation bus history.

2.  **Workflow Execution (LangGraph Engine):**
    *   **Goal:** To reliably execute the multi-step process identified by the recognition component.
    *   **Implementation (LangGraph):** Upon successful classification, the LPPM will dynamically construct and execute a **LangGraph**. This graph will represent the learned workflow, with nodes corresponding to specific `Action Engine` tool calls and edges defining the flow, conditions, and cycles.
    *   **State Management:** LangGraph's `StateGraph` will manage the state of the executing workflow, providing inspectability, debuggability, and robust handling of conditional logic.

**Consequences:**

*   **Positive:**
    *   **Structured Learning Target:** CrewAI's clear process vocabulary provides a well-defined, declarative target for the LPPM's ML model, making pattern learning more effective.
    *   **Robust & Inspectable Execution:** LangGraph provides a powerful, explicit, and visual engine for executing stateful workflows, improving reliability and debuggability.
    *   **Supports Downward Knowledge Distillation:** This architecture directly supports the core PCP principle of compiling expensive Imperator reasoning into efficient, automated LPPM workflows.
    *   **Leverages Framework Strengths:** Optimally utilizes each framework: CrewAI for conceptual patterns and LangGraph for resilient execution.

*   **Negative:**
    *   **Integration Complexity:** Requires integrating a LangGraph runtime within the LPPM's Thought Engine.
    *   **Learning Curve:** MAD developers may need to understand LangGraph's graph-based model for advanced debugging or template design.

*   **Neutral:**
    *   This decision positions the LPPM as a key intermediate cognitive tier, significantly reducing the load on the Imperator for routine multi-step tasks.
---
---

## Appendix A: Detailed Rationale & Inspirations for the LPPM Architecture

### A.1. The Problem: Automating "Instinctive" Workflows

The LPPM (Tier 2) is designed to solve a specific problem: many complex tasks are not novel enough to require the full, expensive reasoning of the Imperator (Tier 4), but are too complex to be handled by a simple DTR reflex (Tier 1). These are the "instinctive" or "learned motor pattern" workflows of the system, such as "Generate a weekly status report" or "Onboard a new data source."

The challenge is to create a system that can **learn** these multi-step processes by observing the Imperator, and then **execute** them reliably and efficiently. This led to a two-part architectural solution.

### A.2. CrewAI's Role: The "Vocabulary" of Collaboration

The first part of the problem is pattern recognition. How does the LPPM learn to recognize a "report generation" task? It needs a structured target for its learning model.

This is where the concepts from **CrewAI** are invaluable. CrewAI provides a simple, declarative vocabulary for describing multi-agent processes. We will leverage this as a conceptual framework:

-   **Process Templates:** The LPPM's learning goal will be to classify an incoming prose request into a specific, CrewAI-inspired process type, such as:
    -   `Process.sequential`: For linear, step-by-step tasks.
    -   `Process.hierarchical`: For tasks requiring a "manager" agent to decompose a goal and delegate to "worker" agents.
-   **Role Mapping:** The LPPM will also learn to map the required roles in the process to specific Joshua MADs (e.g., a `Researcher` role maps to the `Malory` MAD).

By using CrewAI's vocabulary as the *target* for the LPPM's classification model, we give the learning process a clear, structured, and proven set of patterns to aim for.

### A.3. LangGraph's Role: The State-of-the-Art "Execution Engine"

Once the LPPM has recognized the required workflow (e.g., "This is a hierarchical report generation task"), it needs to execute it. A simple script is insufficient for workflows that can be long-running, have conditional branches, require error handling, or loop.

**LangGraph** is the perfect fit for this execution role. It is a state-of-the-art library specifically designed for building stateful, multi-agent applications as graphs.

-   **Dynamic Graph Construction:** After classifying the process, the LPPM will dynamically build a LangGraph that represents the workflow. A sequential process becomes a linear graph; a hierarchical process becomes a graph with a manager node and edges fanning out to worker nodes.
-   **Resilient, Inspectable State:** The state of the workflow (e.g., intermediate results, error counts) is explicitly managed in the LangGraph's `StateGraph`. This makes the entire process highly transparent, debuggable (we can inspect the state at any point), and resilient (we can resume a workflow from a saved state checkpoint).
-   **Natural Handling of Cycles:** LangGraph is designed to handle cycles, which is essential for workflows that require iteration and refinement (e.g., a "writer" agent loops with a "critic" agent until the output is satisfactory).

### A.4. The Learning Loop: Downward Knowledge Distillation

The synthesis of these frameworks is powered by Joshua's core learning principle. The LPPM's library of process templates is not manually coded; it is **distilled from the operational history of the Imperator.**

1.  A background process analyzes the conversation bus for successful, multi-step orchestrations performed by the Imperator.
2.  It clusters similar orchestrations to find recurring patterns.
3.  For each recurring pattern, it generalizes a **CrewAI-style process template** (e.g., `sequential` with roles `A`, `B`, `C`).
4.  This template and its trigger phrases are used to train the LPPM's ML classifier.

This creates a powerful feedback loop: the expensive, deliberate reasoning of the Imperator is gradually "compiled down" into fast, cheap, and reliable automated workflows executed by the LPPM's LangGraph engine.
