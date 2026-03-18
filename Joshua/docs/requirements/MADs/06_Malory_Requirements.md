# Malory Requirements

- **Role**: Web Browser Automation & UI Testing
- **Version**: V0.10
- **Home**: `mads/malory/`

---

## 1. Overview

-   **Purpose**: Malory is the browser automation and UI testing MAD, acting as the ecosystem's interface to the web.
-   **V0.10 Scope Definition**: Perform any browser-based task autonomously, including web research, application interaction, and providing UI testing services for other MADs.
-   **Note**: Malory is the official replacement for the v0 `Marco` MAD.

---

## 2. Implementation Architecture (Polyglot Sidecar Pattern)

Per **ADR-024**, Malory is a polyglot MAD that requires a non-Python component for its core functionality. It **must** be implemented using the three-layer sidecar pattern:

1.  **Layer 1: MCP Server (Python)**: The primary interface of the MAD will be a standard Python MCP server built with the `joshua_communicator` library. This layer exposes all public tools, handles all communication with the rest of the Joshua ecosystem, and contains the MAD's Thought Engine.

2.  **Layer 2: Action Engine Subsystem (Node.js)**: The browser automation capabilities will be implemented as a separate Node.js application using the **Playwright** library. This subsystem will run as an isolated sidecar or subprocess.

3.  **Layer 3: IPC Bridge (Python)**: The Python Action Engine tool handlers (e.g., `malory_browse`) will act as a bridge. They will receive MCP calls, translate them into commands for the Node.js subsystem (e.g., via stdin/stdout or a simple HTTP interface), execute the subprocess, and then format the result into a valid MCP response.

This architecture ensures Malory remains a compliant and discoverable citizen of the Python-based Joshua ecosystem while leveraging the best-in-class technology (Playwright) for its specific domain.

---

## 3. Tool Exposure Model

This MAD follows the Direct Tool Exposure architecture (ADR-023). Its public tools are exposed directly on its Python-based MCP server and are discoverable via the Rogers registry. Any incoming communication that is not a valid MCP call for an exposed tool is routed to the Thought Engine for conversational processing (e.g., "Find me the latest news on AI").

> **Note on Tool List:** The tools listed in this document are a *provisional set* based on the MAD's high-level requirements. The final, authoritative list of tools, their specific parameters, and their return schemas will be defined in a dedicated Design Document prior to implementation.

---

## 4. Public Action Engine Tools

### `malory_browse`
- **Description:** A general-purpose tool to perform a complex web-based task described in natural language. The Thought Engine will decompose the goal into a series of browser actions.
- **Input Schema:**
    - `goal` (string, required): A detailed description of the task to perform (e.g., "Log into my Gmail account, find the email with the subject 'Project Phoenix', and extract the attachment.").
- **Output Schema:** `{"status": "success", "summary": "Task completed. Found 1 attachment.", "results": [{"file_path": "/path/to/attachment.pdf"}]}`

### `malory_research`
- **Description:** Performs web research on a given topic and returns a synthesized summary.
- **Input Schema:**
    - `topic` (string, required): The research topic.
- **Output Schema:** `{"status": "success", "summary": "...", "sources": ["url1", "url2"]}`

### `malory_run_ui_test`
- **Description:** Executes a UI/E2E test scenario against a target URL. Primarily used by `Deming`.
- **Input Schema:**
    - `target_url` (string, required): The URL of the web application to test.
    - `scenarios` (array[dict], required): A list of test scenarios, each with steps to perform and assertions to check.
- **Output Schema:** `{"status": "success", "results": [{"scenario": "Login", "status": "passed", "steps": [...]}]}`

---

## 5. Future Evolution (Post-V0)

Malory's role as the browser automation platform evolves to become an intelligent, eMAD-aware browser orchestrator capable of managing browser resources for the entire Joshua ecosystem.

*   **Phase 1 (Foundation / V0.10):** Malory is hardened and quality-gated for flawless Direct Communication, becoming the reliable browser automation platform for the V0.10 Core Fleet. Malory provides critical UI/E2E testing services for Gateway MADs (Grace, Sam) via integration with Deming.
*   **Phase 2 (Conversation / V1.0):** Malory is re-platformed to communicate exclusively via the Rogers Conversation Bus (pure Kafka), using `Joshua_Communicator` for all inter-MAD communication. All browser automation requests and results flow through the durable conversation log.
*   **Phase 4 (eMADs / V6.0):** Malory becomes eMAD-aware, capable of managing browser contexts for ephemeral MAD teams, providing isolated browser environments for short-lived eMAD workloads, and efficiently pooling browser resources across dynamic MAD populations.
*   **Phase 5 (Autonomy / V7.0):** Malory integrates with Joshua MAD's strategic orchestration, receiving top-down directives for system-wide browser automation policies, constitutional constraints on web interactions, and strategic prioritization of browser resource allocation across the ecosystem.

---
