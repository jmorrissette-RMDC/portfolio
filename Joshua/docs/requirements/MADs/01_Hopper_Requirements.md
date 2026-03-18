# Hopper Requirements

- **Role**: Autonomous Software Engineering
- **Version**: V0.10
- **Home**: `mads/hopper/`

---

## 1. Overview

- **Purpose**: Hopper is the autonomous **Builder of any digital asset**.
- **V0.10 Scope Definition**: As the primary orchestrator of the autonomous bootstrap, Hopper's Imperator receives a high-level goal, then orchestrates other specialist MADs (e.g., Fiedler for reasoning, Starret for Git operations) to produce the desired digital asset, most notably other MADs.

---

## 2. Tool Exposure Model

This MAD follows the Direct Tool Exposure architecture (ADR-023). Its public tools are exposed directly on its MCP server and are discoverable via the Rogers registry. Any incoming communication that is not a valid MCP call for an exposed tool is routed to the Thought Engine for conversational processing.

> **Note on Tool List:** The tools listed in this document are a *provisional set* based on the MAD's high-level requirements. The final, authoritative list of tools, their specific parameters, and their return schemas will be defined in a dedicated Design Document prior to implementation.

---

## 3. Public Action Engine Tools

### `hopper_start_project`
- **Description:** Initiates a full, autonomous software engineering workflow to create a digital asset based on a high-level goal.
- **Input Schema:**
    - `goal` (string, required): A detailed natural language description of the desired asset (e.g., "Create a new MAD that provides weather forecasting services").
- **Output Schema:** `{"status": "success", "project_id": "uuid-1234", "message": "Project initiated. Status will be broadcast."}`

---

## 4. Future Evolution (Post-V0)

Hopper's role as the autonomous software engineering orchestrator evolves to become the self-improving builder with the full Progressive Cognitive Pipeline, ultimately capable of building and improving the entire Joshua ecosystem.

*   **Phase 1 (Foundation / V0.10):** Hopper is hardened and quality-gated for flawless Direct Communication, becoming the reliable autonomous builder for the V0.10 Core Fleet. It orchestrates the build-out of the essential MAD fleet (Turing, Starret, Fiedler, Deming, Malory, Grace, Henson) in sequence, self-versioning after each successful build (V0.71, V0.72, etc.).
*   **Phase 2 (Conversation / V1.0):** Hopper is re-platformed to communicate exclusively via the Rogers Conversation Bus (pure Kafka), using `Joshua_Communicator` for all inter-MAD communication. All development orchestration flows through the durable conversation log, enabling complete project history reconstruction.
*   **Phase 3 (Cognition / V2.0-V5.0):** Hopper receives the full Progressive Cognitive Pipeline in four major upgrades:
    *   **V2.0 (DTR - Tier 1):** Deterministic Task Router provides microsecond-level fast-path routing for repetitive development tasks before expensive LLM reasoning.
    *   **V3.0 (LPPM - Tier 2):** Learned Process and Procedure Memory enables execution of learned multi-step development workflows using CrewAI and LangGraph patterns, dramatically accelerating common build patterns.
    *   **V4.0 (CET - Tier 3):** Context Engineering Transformer with custom model and LoRA provides advanced, learned context assembly for development tasks, intelligently assembling relevant code, documentation, and architectural context.
    *   **V5.0 (CRS - Tier 5):** Cognitive Response System adds pattern-matching and anomaly detection for quality gate validation of all autonomous development decisions, ensuring code quality and architectural consistency.
*   **Phase 4 (eMADs / V6.0):** Hopper becomes eMAD-aware, gaining the capability to delegate complex development tasks to dynamically provisioned eMAD teams via Kaiser. This replaces direct Fiedler calls with intelligent team composition, enabling horizontal scalability for large development projects.
*   **Phase 5 (Autonomy / V7.0):** Hopper integrates with Joshua MAD's strategic orchestration, receiving top-down directives for system-wide development priorities, architectural constraints, and constitutional guidance on code generation. Hopper becomes capable of autonomous system-level improvements under Joshua's strategic direction.

---