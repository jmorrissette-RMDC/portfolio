# ADR-020: Define the 6-Phase System Evolution Roadmap

**Status:** Accepted

**Context:**
As architectural decisions for the Joshua ecosystem have been refined, a number of inconsistencies and ambiguities have arisen regarding the naming, ordering, and versioning of the major evolutionary phases of the project. A single, definitive, and authoritative roadmap is required to ensure all current and future architectural decisions are made from a consistent and coherent strategic plan. This ADR serves to formally establish that master roadmap, superseding all previous roadmap discussions and documents.

**Decision:**
The evolution of the Joshua ecosystem will be formally defined by the following **6-Phase Roadmap**. This roadmap serves as the single source of truth for the project's phased rollout of capabilities and the corresponding MAD-level versioning. There are no "System-Level Versions"; there are only Phases and MAD Versions.

| Phase | Phase Name | MAD Version Target | Core Activity & Architectural Change |
| :--- | :--- | :--- | :--- |
| **1** | **Foundation** | V0.10 | Build/mature the Core Fleet of persistent MADs to a "Federation Ready" state. |
| **2** | **Conversation** | V1.0 | Re-platform the Core Fleet onto the Rogers Conversation Bus. |
| **3** | **Cognition** | V5.0 | Roll out the full PCP (Tiers 1-5: DTR, LPPM, CET, CRS) to the Core Fleet. |
| **4** | **eMADs** | V6.0 | Introduce `Kaiser` & `Moses` and upgrade all Core MADs to be "eMAD-aware." |
| **5** | **Autonomy** | V7.0 | Activate `Joshua` MAD's strategic leadership and upgrade all MADs to be "Joshua-aware." |
| **6** | **Expansion** | V7.0 | Add Secondary MADs (`Muybridge`, etc.). They enter the ecosystem at the mature V7.0 standard. |

**Consequences:**

*   **Positive:**
    *   **Provides a Single Source of Truth:** Eliminates all ambiguity regarding the project's versioning and phased rollout.
    *   **Clarifies Architectural Dependencies:** The roadmap correctly sequences the rollout of capabilities, ensuring foundational layers (like the Bus and full PCP) are in place before dependent scaling and strategic layers are introduced.
    *   **Defines Clear Milestones:** Each phase represents a major, verifiable milestone for the project.
    *   **Resolves Previous Inconsistencies:** This ADR formally corrects previous errors in versioning, phase ordering, and naming conventions.

*   **Negative:**
    *   None. This ADR is a clarifying document that reduces complexity and ambiguity.

*   **Neutral:**
    *   This ADR will necessitate a review and update of all existing ADRs and core architecture documents to ensure their versioning and phase references are consistent with this master roadmap.

---
---

## Appendix A: Detailed Architectural Rationale

### A.1. The Need for a Definitive Roadmap

The process of creating the preceding ADRs revealed several inconsistencies in the project's historical documentation and our own evolving discussions. A master roadmap was required to serve as the canonical reference, and this 6-phase structure was determined to be the most logical and architecturally sound.

### A.2. Rationale for the 6-Phase Structure and Order

This specific 6-phase structure was chosen because it provides the cleanest possible separation of concerns and respects all logical dependencies for the system's evolution.

1.  **Phase 1 (Foundation):** Establishes the *components* (the Core Fleet of MADs).
2.  **Phase 2 (Conversation):** Establishes the *communication and learning substrate* (the Bus).
3.  **Phase 3 (Cognition):** Focuses on making the persistent components *cognitively complete* by rolling out the full PCP.
4.  **Phase 4 (eMADs):** Focuses on making the system *horizontally scalable* with ephemeral intelligence. This must come after the core agents are cognitively mature.
5.  **Phase 5 (Autonomy):** Activates the final layer of *top-down strategic control* from the `Joshua` MAD. This is placed before Expansion because the strategic leader should be in place to guide the system's final growth phase.
6.  **Phase 6 (Expansion):** The final phase is to *expand the skillset* of the now fully cognitive, scalable, and strategically-led system by adding new, specialized secondary MADs.

### A.3. Clarification on MAD-Level vs. System-Level Versioning

This roadmap also clarifies the two types of versioning in the project:
-   **MAD-Level Versions (V0.1, V0.5 ... V7.0):** Refer to the maturity of an individual MAD's implementation, as defined in its software and our ADRs. A MAD's version number signifies its adherence to the "Common DNA" established in a given phase.
-   **Phases:** Refer to major, system-wide architectural states or goals. There are no "System-Level Versions" (e.g., "Joshua is at V6.0"). The correct terminology is, "The Joshua ecosystem is in Phase 4 (eMADs), and the core MADs are being upgraded to the V6.0 standard."
