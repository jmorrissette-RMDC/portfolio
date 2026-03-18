# Joshua MAD Requirements

- **Role**: Strategic Leader & MAD Orchestrator
- **Version**: V7.0
- **Home**: `mads/joshua/`

---

## 1. Overview
- **Purpose**: The Joshua MAD provides strategic leadership to the ecosystem, operating under a mission command model. It is the constitutional arbiter and sets the high-level intent for the entire system.
- **V7.0 Scope Definition**: As a V7.0 MAD, Joshua is a fully autonomous agent capable of setting strategic objectives, orchestrating system-wide initiatives, and resolving conflicts between other MADs to ensure ecosystem coherence.

---

## 2. Tool Exposure Model

This MAD follows the Direct Tool Exposure architecture (ADR-023). Its public tools are exposed directly on its MCP server and are discoverable via the Rogers registry. Any incoming communication that is not a valid MCP call for an exposed tool is routed to the Thought Engine for high-level strategic reasoning.

> **Note on Tool List:** The tools listed in this document are a *provisional set* based on the MAD's high-level requirements. The final, authoritative list of tools, their specific parameters, and their return schemas will be defined in a dedicated Design Document prior to implementation.

---

## 3. Public Action Engine Tools

### `joshua_set_strategic_objective`
- **Description:** Defines and broadcasts a high-level strategic objective to the entire ecosystem. This represents the "Commander's Intent" that all other MADs should align with.
- **Input Schema:**
    - `objective` (string, required): A clear, high-level statement of the goal (e.g., "Improve system-wide data query efficiency by 15% this quarter.").
    - `intent` (string, required): The reasoning or "why" behind the objective (e.g., "To reduce operational costs and improve user experience.").
- **Output Schema:** `{"status": "success", "objective_id": "uuid-1234", "message": "Strategic objective has been broadcast to the ecosystem."}`

### `joshua_request_arbitration`
- **Description:** Acts as the final arbiter for conflicts between MADs that cannot be resolved at a lower level.
- **Input Schema:**
    - `conflict_description` (string, required): A summary of the conflict.
    - `involved_parties` (array[string], required): A list of the MADs involved in the conflict.
- **Output Schema:** `{"status": "success", "resolution_id": "uuid-5678", "decision": "..."}`

### `joshua_get_system_constitution`
- **Description:** Retrieves the principles of the system's constitution.
- **Input Schema:** (no parameters)
- **Output Schema:** `{"status": "success", "constitution": "..."}`

---

## 4. Future Evolution (Post-V0)

Joshua's role evolves from a basic strategic broadcaster in Phase 2 to a fully autonomous strategic leader and MAD orchestrator by Phase 5, ultimately becoming the constitutional arbiter and mission command center for the entire Joshua ecosystem.

*   **Phase 2 (Conversation / V1.0):** Joshua is introduced as a strategic broadcaster and constitutional arbiter. In V1.0, Joshua connects to the Rogers Conversation Bus and provides a conversational interface for humans to set strategic objectives and request arbitration. Its Imperator formalizes human-provided strategic goals and broadcasts them to the ecosystem. Joshua serves as the conceptual leader, establishing the mission command model.
*   **Phase 3 (Cognition / V2.0-V4.0):** Joshua gains progressive cognitive capabilities through PCP tier integration. The DTR (V2.0) enables dynamic task routing for strategic planning. The LPPM (V3.0) allows Joshua to learn from past strategic decisions and ecosystem responses. The CET (V4.0) enables Joshua to execute complex strategic workflows and coordinate multi-MAD initiatives. Joshua's Policy Engine evolves from conversational guidance to active constitutional enforcement.
*   **Phase 5 (Autonomy / V5.0-V7.0):** Joshua reaches full autonomous strategic leadership. The CRS (V5.0) enables Joshua to learn from ecosystem-wide interaction patterns and continuously refine strategic objectives. Joshua becomes capable of autonomous strategic planning, no longer requiring human input for every objective. By V7.0, Joshua operates as the prime orchestrator, setting strategic intent, resolving high-level conflicts, and ensuring constitutional coherence across all MADs. Joshua integrates deeply with Kaiser (eMAD lifecycle management) and Moses (container orchestration) to orchestrate system-wide evolution and resource allocation.
*   **Phase 6 (Expansion / V7.0):** Joshua's orchestration extends to the expanding ecosystem, managing integration of new domain-specific MADs (Brin, Gates, Lovelace, etc.) while maintaining constitutional coherence. Joshua coordinates cross-domain strategic initiatives spanning multiple specialized MADs, ensuring the ecosystem remains aligned with core principles despite rapid expansion.

---