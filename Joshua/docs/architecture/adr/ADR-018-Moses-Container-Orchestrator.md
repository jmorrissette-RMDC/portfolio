# ADR-018: Establish the `Moses` MAD as the Federated Container Placement Orchestrator

**Status:** Accepted

**Context:**
The V6.0 architecture ("The eMAD Revolution") requires a mechanism for the intelligent placement of both persistent MADs and high-frequency ephemeral eMADs across a distributed cluster of host machines. This core infrastructure function, previously handled by a vague "underlying orchestrator," needs to be formalized as an intelligent, resilient, and autonomous service. This MAD will serve as the single gateway for all container lifecycle operations, as discussed in the context of `Kaiser` (ADR-017).

**Decision:**
A new, dedicated, system-level MAD, named **`Moses`** (after Robert Moses, the master builder), will be established as part of the **Phase 4 (eMADs) / V6.0** architecture. Its core responsibility will be the **lifecycle and intelligent placement orchestration of all MAD and eMAD containers** across the Joshua compute cluster.

`Moses` will operate on a **fully decentralized, federated "gossip" model**.

1.  **Federated Deployment Model ("Local Warden"):**
    *   A dedicated **`Moses` MAD instance will be deployed on *every host* that is capable of running MAD containers.**
    *   Each `Moses` instance is the **sole and exclusive master of its local host's container resources.** It interacts directly with the local container runtime (e.g., via the Docker socket).

2.  **Global Awareness via "Gossip Protocol":**
    *   All `Moses` instances are equal peers and independently maintain a near real-time, in-memory copy of the **entire cluster's global host state** by gossiping and subscribing to a shared `system.moses.heartbeats` topic.

3.  **`Moses`'s Cognitive Role (Intelligent Placement Orchestrator):**
    *   Higher-level orchestrators (`Joshua` or `Kaiser`) will delegate placement decisions by sending a single, declarative request, e.g., `moses_deploy_team(containers=[{...}])`.
    *   The receiving `Moses` instance's own PCP/Imperator will use its global cluster view to create an optimal placement plan. **Crucially, if a placement request includes a GPU requirement, it is `Moses`'s internal responsibility to consult with `Sutherland` (ADR-015) to satisfy that constraint.** This complexity is entirely encapsulated within `Moses`.

4.  **Container Lifecycle Execution:**
    *   `Moses` is the **only MAD authorized to interact with the underlying container runtime.** After determining the placement plan, the responsible `Moses` instance issues commands to the appropriate *local `Moses` instances* on the target hosts, which then execute the low-level `docker run` commands.

**Consequences:**

*   **Positive:**
    *   **Maximal Resilience & Scalability:** The federated gossip model provides high availability and scales horizontally.
    *   **Intelligent Resource Allocation:** `Moses` makes optimal placement decisions by centrally managing all host-level constraints, including the delegation to `Sutherland` for GPU specifics.
    *   **Perfect Separation of Concerns:** `Kaiser` is the expert on *teams*. `Moses` is the expert on *placement*. `Sutherland` is the expert on *GPUs*. The delegation hierarchy is clean and efficient.
    *   **High Security & Reliability:** Eliminates insecure SSH/remote Docker API calls and provides a single, reliable gateway for all container operations.

*   **Negative:**
    *   **Adds a New Critical Service:** `Moses` becomes a fundamental component of the Joshua infrastructure.

*   **Neutral:**
    *   This ADR formalizes a critical infrastructure management component for the V6.0 architecture.

---
---

## Appendix A: Detailed Architectural Rationale

### A.1. `Moses` as the True Container Orchestrator

This architecture was chosen to create a single, authoritative service for all container lifecycle and placement operations. As correctly identified during architectural discussions, allowing multiple MADs (`Kaiser`, `Joshua`) to issue deployment commands would violate the principle of orchestration and lead to chaos. `Moses` is established as the sole and exclusive gateway to the container runtime, ensuring that all deployments are managed, tracked, and optimized through a single, intelligent point of control.

### A.2. The Superiority of the Delegated, Encapsulated Model

An initial architectural model involved `Kaiser` first asking `Moses` for a host, and then separately asking `Sutherland` to confirm GPU capacity. This was rejected as an inefficient and "leaky" abstraction.

The final, accepted architecture is a clean **delegation model where expertise is perfectly encapsulated**:

1.  **`Kaiser` (Client):** Knows *what* team of eMADs it needs and their abstract requirements (e.g., this one needs a GPU).
2.  **`Moses` (Orchestrator):** Is the expert on **all placement logic**. It receives the full order from `Kaiser`. When `Moses`'s internal Imperator sees a `gpu_needed: true` requirement, it knows that fulfilling this part of the contract requires consulting another specialist: `Sutherland`.
3.  **`Sutherland` (Consultant):** Provides GPU-specific advice *to Moses*.

This is a much cleaner API. `Kaiser` does not need to know that `Sutherland` exists. It simply gives its complete order to the master placement orchestrator, `Moses`, and trusts `Moses` to figure out the details. This perfect encapsulation is a core tenet of the Cellular Monolith design.

### A.3. The Federated "Local Warden" Model

The decision to deploy a `Moses` instance on every host is a crucial design choice for resilience and security. It avoids a single point of failure and eliminates the need for insecure remote access protocols like SSH, as all container commands are executed by a local `Moses` instance on the target machine. This model, which mirrors the `Sutherland` architecture, is fundamental to Joshua's distributed and resilient design.