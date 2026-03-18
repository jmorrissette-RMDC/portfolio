# ADR-033: Metaprogramming via Hopper-Orchestrated Optimization

**Status:** Accepted
**Date:** 2025-12-20
**Deciders:** System Architect

## Context and Problem Statement

The adoption of a fully flow-based architecture (ADR-032) enables a new paradigm for metaprogramming and system self-improvement. Rather than agents directly modifying their own code—a high-risk activity—we can establish a safer, more robust, and centrally-managed optimization loop. A formal decision is needed to define the roles and responsibilities within this new metaprogramming model, clarifying who identifies the need for change and who executes it.

## Decision

We will adopt a **Hopper-centric metaprogramming model**. In this model, `Hopper` is responsible for **proactively identifying optimization opportunities** across the entire ecosystem and then **executing the necessary modifications**, whether at the flow or code level. Individual MADs are not responsible for discovering their own metaprogramming requirements.

This creates a clear, safe, and auditable "Observe -> Analyze -> Improve" loop, orchestrated by specialist MADs:

1.  **Observation (`Hamilton`):** The `Hamilton` MAD (System Monitoring) is responsible for passively observing all system activity on the conversation bus and collecting performance metrics (e.g., flow execution times, error rates, resource usage).

2.  **Analysis and Identification (`Hopper`):**
    *   `Hopper` will have a core, scheduled, internal capability to **periodically review system performance**.
    *   This process will involve `Hopper` making a service request to `Hamilton` (e.g., `hamilton_get_performance_bottlenecks()`) to identify the least performant or most error-prone workflows in the ecosystem.

3.  **Execution (`Hopper`):**
    *   Upon receiving the list of bottlenecks from `Hamilton`, `Hopper`'s Thought Engine will analyze each case and decide on the appropriate modification strategy. This decision is divided into two primary types:
        *   **Flow-Based Modification (for Workflows and Logic):** If the analysis suggests a flaw in the workflow logic, `Hopper` will generate a new, optimized `flow_v2.json` for the target MAD.
        *   **Code-Based Modification (for New Components and Optimization):** If the analysis suggests a stable flow is a performance bottleneck, or if a new, non-existent capability is needed, `Hopper` will perform complex code generation to create a new, high-performance Python custom component.

4.  **Deployment (Hopper, Starret, Deming):** After generating the new artifact (`.json` or `.py`), `Hopper` will orchestrate the deployment by making service calls to `Starret` (for Git operations and PRs) and `Deming` (for testing and quality assurance), ensuring all changes are safely integrated.

## Consequences

*   **Positive:**
    *   **Centralized Expertise:** `Hopper` becomes the single, specialized agent responsible for system-wide performance optimization and software engineering, preventing this complex logic from being duplicated across all MADs.
    *   **Global Optimization:** By analyzing data from `Hamilton`, `Hopper` has a global view and can identify systemic or cross-MAD optimization opportunities that individual MADs would miss.
    *   **Extremely Safe Metaprogramming:** The MADs themselves are not self-modifying. All changes are managed by a specialist (`Hopper`) through a formal, auditable process involving version control (`Starret`) and QA (`Deming`). This is a highly robust and low-risk model for an evolving system.
    *   **Clear Separation of Concerns:** MADs focus on their domain tasks. `Hamilton` observes. `Hopper` analyzes and improves.

*   **Negative:**
    *   This architecture creates a tight dependency loop between `Hopper` and `Hamilton` for proactive optimization. The quality of `Hopper`'s improvements is dependent on the quality of `Hamilton`'s metrics.
