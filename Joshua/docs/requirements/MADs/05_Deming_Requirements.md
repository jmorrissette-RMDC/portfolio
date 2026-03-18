# Deming Requirements

- **Role**: CI/CD, Quality & Test Management
- **Version**: V0.7
- **Home**: `mads/deming/`

---

## 1. Overview

-   **Purpose**: Deming provides comprehensive quality assurance and continuous integration services to the Joshua ecosystem.
-   **V0.7 Scope Definition**: Orchestrate multi-pronged testing strategies for other MADs to validate them against their V0.10 quality gate requirements. Deming's development is a blocker for the V0.10 milestone.
-   **Note on Vision**: The immutable vision for Deming is CI/CD and Quality Management. Previous documentation describing Deming as an Object Definition Table (ODT) service is incorrect and superseded by this document.

---

## 2. Tool Exposure Model

This MAD follows the Direct Tool Exposure architecture (ADR-023). Its public tools are exposed directly on its MCP server and are discoverable via the Rogers registry. Any incoming communication that is not a valid MCP call for an exposed tool is routed to the Thought Engine for conversational processing (e.g., "What is the quality status of the Fiedler MAD?").

> **Note on Tool List:** The tools listed in this document are a *provisional set* based on the MAD's high-level requirements. The final, authoritative list of tools, their specific parameters, and their return schemas will be defined in a dedicated Design Document prior to implementation.

---

## 3. Public Action Engine Tools

### `deming_generate_test_strategy`
- **Description:** Generates a comprehensive, multi-agent test strategy for a given MAD based on its role, features, and source code.
- **Input Schema:**
    - `mad_name` (string, required): The name of the MAD to generate a test strategy for.
    - `source_repo_url` (string, required): The URL to the MAD's source code repository.
- **Output Schema:** `{"status": "success", "strategy_id": "uuid-5678", "message": "Test strategy generation initiated."}` (The final strategy document path will be broadcast).

### `deming_execute_test_suite`
- **Description:** Executes a full testing suite against a MAD, including unit, integration, and other tests as defined by a strategy. This is the primary tool for V0.10 quality gate validation.
- **Input Schema:**
    - `mad_name` (string, required): The name of the MAD to test.
    - `strategy_id` (string, required): The ID of the test strategy to execute.
    - `include_ui_tests` (boolean, optional, default: false): Whether to orchestrate `Malory` for UI testing (applicable for gateway MADs like `Grace`).
- **Output Schema:** `{"status": "success", "test_run_id": "uuid-9101", "message": "Comprehensive test suite initiated."}` (Progress and final results will be broadcast).

### `deming_get_test_results`
- **Description:** Retrieves the results of a specific test run.
- **Input Schema:**
    - `test_run_id` (string, required): The ID of the test run to retrieve.
- **Output Schema:** `{"status": "success", "results": {"summary": "...", "passed": 47, "failed": 2, ...}}`

---

## 4. Future Evolution (Post-V0)

Deming's role as the CI/CD and quality assurance platform evolves to become the comprehensive testing orchestrator for the entire Joshua ecosystem, including ephemeral MAD teams.

*   **Phase 1 (Foundation / V0.7 -> V0.10):** Deming is built and hardened for flawless Direct Communication, becoming the reliable CI/CD and quality gate validation platform for the V0.10 Core Fleet. All Phase 1 MADs must pass Deming's comprehensive V0.10 quality gate before progressing to V1.0.
*   **Phase 2 (Conversation / V1.0):** Deming is re-platformed to communicate exclusively via the Rogers Conversation Bus (pure Kafka), using `Joshua_Communicator` for all inter-MAD communication. All test orchestration and quality validation flows through the durable conversation log.
*   **Phase 4 (eMADs / V6.0):** Deming becomes eMAD-aware, capable of orchestrating testing for ephemeral MAD teams, validating short-lived eMAD instances, and managing specialized test environments for dynamically provisioned MAD populations.
*   **Phase 5 (Autonomy / V7.0):** Deming integrates with Joshua MAD's strategic orchestration, receiving top-down directives for system-wide quality policies, constitutional constraints on test coverage requirements, and strategic prioritization of testing resources across the entire ecosystem.

---