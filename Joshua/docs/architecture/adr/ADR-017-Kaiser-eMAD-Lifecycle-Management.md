# ADR-017: Establish the `Kaiser` MAD for eMAD Lifecycle Management

**Status:** Accepted

**Context:**
The V6.0 architecture ("The eMAD Revolution") introduces "Intelligent eMAD Teams" as the standard mechanism for scalable, parallel, and complex task execution (ADR-010). Unlike persistent MADs, eMADs have a short lifecycle and are spawned in high frequency. This requires a dedicated, high-throughput service for their lifecycle management, a role too tactical for the strategic `Joshua` MAD (ADR-016).

**Decision:**
A new, dedicated, system-level MAD, named **`Kaiser`** (after industrialist Henry J. Kaiser), will be established as part of the **Phase 4 (eMADs) / V6.0** architecture. Its sole and exclusive responsibility will be the **tactical orchestration and lifecycle management of all ephemeral MADs (eMADs).**

1.  **Scope of Responsibility:** `Kaiser` is the expert on eMAD team composition. It is responsible for translating high-level team requests into declarative deployment orders, monitoring the health of spawned eMADs, and orchestrating their termination.

2.  **Workflow for eMAD Team Spawning (The "Delegation Model"):**
    *   A MAD (e.g., `Hopper`) sends a high-level request to `Kaiser`: `kaiser_assemble_team(roles=['Sr_Dev', 'QA'])`.
    *   `Kaiser`, the expert on eMAD roles, determines the resource requirements for this team.
    *   `Kaiser` then makes a **single, declarative request** to the `Moses` MAD (the container placement expert, ADR-018), asking it to deploy the entire team: `moses_deploy_team(containers=[{'role': 'Sr_Dev', 'requirements': {...}}, ...])`.
    *   `Kaiser`'s job is then to await a single success/fail confirmation from `Moses`. **It does not interact with `Sutherland` or the container runtime directly.**

3.  **Architectural Role:** The `Kaiser` MAD acts as the specialized, high-throughput "Team Assembler" or "Foreman," complementing the `Joshua` MAD's role as the "Strategic Commander" and `Moses`'s role as the "Master Orchestrator."

**Consequences:**

*   **Positive:**
    *   **Clear Separation of Concerns:** Perfectly separates the *tactical* deployment of eMADs (`Kaiser`) from the strategic deployment of persistent MADs (`Joshua`) and the infrastructure-level placement (`Moses`).
    *   **High Efficiency & Scalability:** As a dedicated service, `Kaiser` can handle the high-frequency spawning and termination of eMADs required for massive parallel collaboration.
    *   **Decouples Workload from Orchestration:** MADs like `Hopper` are completely decoupled from the complexity of container placement. This logic is perfectly encapsulated within `Kaiser`'s delegation to `Moses`.
    *   **Enables Scalable Collaboration:** `Kaiser` is the key enabling technology for the V6.0 vision.

*   **Negative:**
    *   **Adds a New Critical Service:** `Kaiser` becomes a new, critical piece of system infrastructure that must be highly available.

*   **Neutral:**
    *   This ADR formalizes the existence of a critical component in the V6.0 architecture, providing a clear service boundary for the management of ephemeral agents.

---
---

## Appendix A: Detailed Architectural Rationale and Context

### A.1. The Need for a Specialized "eMAD Spawner"

The eMAD pattern (ADR-010) is fundamental to Joshua's V6.0 scalability. However, the lifecycle management of these temporary agents is a high-frequency, tactical workload. Burdening the strategic `Joshua` MAD with this would be a severe bottleneck. `Kaiser` is therefore established as a dedicated, optimized service for this specific purpose.

### A.2. The Superiority of the Delegated Orchestration Model

An initial architectural model involved `Kaiser` in a complex, multi-step coordination dance: asking `Moses` for a host, then asking `Sutherland` for GPU confirmation, then issuing a final deployment command. This model was rejected as it was overly "chatty" and burdened `Kaiser` with infrastructure-level knowledge that it should not possess.

The final, accepted architecture is a clean **delegation model**.

1.  **`Hopper` (Client):** Knows *what* project needs a team.
2.  **`Kaiser` (Team Assembler):** Knows *what roles* and resources the team requires. Its expertise is in **team composition**.
3.  **`Moses` (Placement Orchestrator):** Is the expert on *where and how* to place any container. It receives the entire "order" from `Kaiser` and is solely responsible for fulfilling it.

This workflow correctly encapsulates expertise. `Kaiser` doesn't need to know that `Sutherland` exists. It just needs to declare to `Moses` that a particular eMAD requires a GPU. `Moses`, as the master of placement, is responsible for internally consulting with `Sutherland` to satisfy that constraint. This makes the APIs cleaner and the system more modular and robust. `Kaiser`'s role is simplified to translating a project need into a resource request, which is its true domain.
