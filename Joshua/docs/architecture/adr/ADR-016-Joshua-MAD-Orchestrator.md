# ADR-016: Designate the `Joshua` MAD as the Orchestrator for Persistent MAD Deployments

**Status:** Accepted

**Context:**
The deployment of a new, persistent Multipurpose Agentic Duo (MAD) is a significant architectural event. It adds a permanent, long-lived capability to the "Cellular Monolith," impacting the entire ecosystem. This action is strategic, infrequent, and carries high impact. It requires deliberate oversight to ensure it aligns with the system's long-term roadmap and architectural principles. A formal process and a designated authority are needed to govern these strategic deployments. As discussed in ADR-015, this decision was deferred to a dedicated ADR.

**Decision:**
The **`Joshua` MAD**, in its established role as the system's "Strategic Leadership" and "Constitutional Arbiter," is formally designated as the **orchestrator for the lifecycle of all persistent MADs.**

1.  **Scope of Responsibility:** The `Joshua` MAD is responsible for approving, planning, and executing the deployment, upgrade, and decommissioning of all permanent, long-lived MADs.
2.  **Workflow for New Deployments:**
    *   A proposal to add a new persistent MAD is submitted to the `Joshua` MAD (initially by a human architect).
    *   `Joshua`'s internal PCP/Imperator evaluates the proposal against the system roadmap, resource availability, and architectural principles.
    *   Upon approval, `Joshua` reads the new MAD's deployment manifest to understand its resource requirements (e.g., `data_heavy_gpu`, storage affinity).
    *   If specialized resources are needed, `Joshua` queries the relevant expert MAD (e.g., `Sutherland` for GPU placement, as per ADR-015) for a placement recommendation.
    *   `Joshua` then issues the final command to the underlying container orchestrator to deploy the MAD container to the appropriate host.
3.  **Frequency:** This is a low-frequency, high-deliberation process, reflecting the strategic importance of adding a permanent component to the ecosystem.
4.  **Architectural Phasing:** The full activation of the `Joshua` MAD's strategic, autonomous leadership is a capstone capability of the ecosystem, formally targeted for **Phase 6 (Autonomy)**, corresponding to **MAD Version V7.0**. Prior to this, its orchestration functions may be handled manually or by a precursor version.

**Consequences:**

*   **Positive:**
    *   **Architectural Governance:** Centralizes strategic deployment decisions in the MAD best equipped for them, ensuring the long-term architectural coherence of the ecosystem.
    *   **Clear Separation of Concerns:** Perfectly separates the *strategic* deployment of permanent infrastructure (Joshua's role) from the *tactical* deployment of ephemeral agents (`Kaiser`'s role).
    *   **Aligns with `Joshua` MAD's Identity:** This responsibility is a natural extension of the `Joshua` MAD's documented role as the system's leader and constitutional guardian.

*   **Negative:**
    *   **Not an Agile Process:** The deployment of new, permanent MADs is intentionally a deliberate and gated process, which could slow down rapid, experimental additions of permanent components. This is accepted as a necessary trade-off for architectural stability.

*   **Neutral:**
    *   This ADR formalizes a critical piece of the system's self-management and governance model, clarifying how the "Cellular Monolith" grows and evolves at a strategic level.
---
---

## Appendix A: Detailed Architectural Rationale

### A.1. `Joshua` as the Strategic Apex

The `Joshua` MAD is envisioned as the highest level of the system's cognitive hierarchy—the "CEO" or "Commander" of the ecosystem. Its role is not to engage in day-to-day tactical operations, but to provide long-term strategic direction and ensure the system's actions align with its core principles (its "constitution"). The deployment of new, permanent MADs is a strategic act that directly shapes the future capabilities of the ecosystem, and therefore falls squarely within `Joshua`'s domain.

### A.2. Rationale for V7.0 "Autonomy" Phasing

Placing the full activation of `Joshua`'s strategic leadership in the final phase (Phase 6, V7.0) is a deliberate and critical architectural decision, driven by logical dependencies:

1.  **A Complete "Organization" Must Exist First:** For a strategic leader to be effective, it must have a complete and capable "organization" to lead. This means the full ecosystem of cognitively complete, scalable, and fully-featured MADs must be in place first.
2.  **Cognitive Maturity is a Prerequisite (Phase 3 - V5.0):** The Core Fleet must be cognitively complete with the full PCP, including the CRS, so they can understand and act on nuanced strategic directives.
3.  **Scalable Infrastructure is a Prerequisite (Phase 4 - V6.0):** The eMAD infrastructure (`Kaiser`, `Moses`) must be operational, as `Joshua`'s strategic plans will almost certainly involve the dynamic allocation of eMAD teams.
4.  **Full Capability Set is a Prerequisite (Phase 5 - V6.x):** The secondary, specialist MADs (`Muybridge`, `Bass`, etc.) should be in place, so `Joshua` has a full palette of capabilities to draw upon when formulating its strategies.

Activating `Joshua`'s leadership before these pieces are in place would be like a general trying to command an army that hasn't been fully trained or equipped. V7.0 marks the point where the ecosystem is mature enough to be led, not just managed.
