# ADR-019: Refine `Kaiser`'s Role as a Delegating eMAD Orchestrator

**Status:** Accepted

**Context:**
The `Kaiser` MAD is responsible for the lifecycle of ephemeral eMADs (ADR-017). Initial drafts of its workflow involved `Kaiser` in the low-level details of placement, including querying `Sutherland` and issuing final deployment commands. However, with the formalization of the `Moses` MAD as the true container placement and lifecycle orchestrator (ADR-018), `Kaiser`'s role must be refined to be a pure delegator, focusing on its core expertise of team composition and not on infrastructure specifics.

**Decision:**
The `Kaiser` MAD's role is refined to be the **"Team Composition Expert" and "Tactical eMAD Orchestrator."** Its primary responsibility is to translate a high-level team request into a declarative deployment order for `Moses`. `Kaiser` will **delegate all placement and execution logic** to `Moses`.

1.  **`Kaiser`'s Core Expertise:** `Kaiser` is the expert on *what* an eMAD team should look like. It receives a high-level goal from a MAD like `Hopper` (e.g., `kaiser_assemble_team(project_id='proj-123', roles=['Sr_Dev', 'QA'])`). `Kaiser`'s responsibility is to look up the templates for these roles and determine their specific resource requirements (CPU, RAM, GPU needs, etc.).

2.  **Delegation to `Moses`:** `Kaiser`'s primary action is to make a **single, declarative, high-level request** to the `Moses` MAD. It does not recommend hosts or query `Sutherland`. It simply provides the full "order" for the team it needs.
    *   **Example Request to `Moses`:**
        ```
        moses_deploy_team(
          team_id='team-abc',
          containers=[
            {'role': 'Sr_Dev', 'requirements': {'cpu': 4, 'ram': 16, 'gpu_needed': true}},
            {'role': 'QA', 'requirements': {'cpu': 2, 'ram': 8, 'gpu_needed': false}}
          ]
        )
        ```

3.  **No Direct Container Interaction:** `Kaiser` **will not** interact with the underlying container runtime (e.g., Docker) in any way. It will not issue `deploy` or `terminate` commands to local `Moses` instances. Its entire interaction with the infrastructure is abstracted away through the high-level API provided by `Moses`.

4.  **Awaiting Confirmation:** After delegating the deployment task to `Moses`, `Kaiser`'s job is to wait for a single `team_deployment_successful` or `team_deployment_failed` confirmation from `Moses`. It then forwards this status to the original requesting MAD.

**Consequences:**

*   **Positive:**
    *   **Perfect Separation of Concerns:** This creates a perfectly clean architectural boundary. `Kaiser` is the expert on *eMADs and teams*. `Moses` is the expert on *hosts and containers*.
    *   **Simplified `Kaiser` Logic:** `Kaiser`'s internal logic is now much simpler. It no longer needs to know about hardware topology, GPU availability, or even the existence of `Sutherland`. This makes it more robust and easier to maintain.
    *   **Enables True Orchestration:** By making `Moses` the sole authority for container deployment, we create a true, reliable orchestration layer and prevent the conflicts that would arise from multiple MADs trying to control the same resources.
    *   **Enhanced Scalability:** `Kaiser` can fire off dozens of high-level `moses_deploy_team` requests in parallel, and `Moses`'s federated, intelligent system will handle the complex scheduling and placement efficiently.

*   **Negative:**
    *   None. This decision simplifies `Kaiser`'s architecture while improving the overall robustness and clarity of the ecosystem's orchestration model.

*   **Neutral:**
    *   This ADR provides the final clarification for the Joshua ecosystem's multi-layered orchestration hierarchy, solidifying the precise roles and interactions of `Kaiser`, `Moses`, and `Sutherland`.

---
---

## Appendix A: Detailed Architectural Rationale

### A.1. The Flaw in the Previous Model

An earlier iteration of this workflow had `Kaiser` performing a multi-step process: first querying `Moses` for a recommendation, then querying `Sutherland` for confirmation, and finally issuing a deployment command to a local `Moses` instance. This was correctly identified as a flawed architecture. It made `Kaiser` too "chatty" and burdened it with placement logic that rightly belongs to `Moses`. It violated the principle of clean delegation to the true domain expert.

### A.2. The Superiority of the Declarative, Delegated Model

The final, accepted architecture is far superior due to its clean encapsulation of expertise.

-   **`Kaiser` as the "Team Assembler":** Its role is analogous to a factory manager who decides *what* products need to be built and *what components* they require. `Kaiser` knows a `Sr_Dev_eMAD` needs a "high-power compute chassis" (a GPU).
-   **`Moses` as the "Master Orchestrator":** Its role is analogous to the factory's automated floor manager. It receives the full bill of materials from `Kaiser` and is solely responsible for the complex logistics of *where and how* to assemble the products. When `Moses` sees a component that needs the "high-power chassis," it knows, internally, that it must consult with its specialist (`Sutherland`) to get one.

This delegation means `Kaiser`'s API with `Moses` is clean, high-level, and declarative. `Kaiser` states the desired end-state ("I need this team deployed with these requirements"), and `Moses` is responsible for making that state a reality. This is a robust and scalable interaction model that perfectly reflects the distributed cognition of the Joshua ecosystem.