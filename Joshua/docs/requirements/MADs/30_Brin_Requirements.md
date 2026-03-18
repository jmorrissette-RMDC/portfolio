# Brin Requirements

- **Role**: Google Ecosystem Manager
- **Version**: V7.0
- **Home**: `mads/brin/`

---

## 1. Overview

-   **Purpose**: `Brin` is the specialized MAD responsible for all integration and interaction with Google ecosystem services and APIs within the Joshua system. It acts as the system's unified interface to Google technologies.
-   **V7.0 Scope Definition**: As a V7.0 MAD, Brin is a fully cognitive agent capable of orchestrating complex multi-service workflows across Google Cloud Platform, Google Workspace, and Google AI services, while managing authentication, quotas, and costs.

---

## 2. Tool Exposure Model

This MAD follows the Direct Tool Exposure architecture (ADR-023). Its public tools are exposed directly on its MCP server and are discoverable via the Rogers registry. Any incoming communication that is not a valid MCP call for an exposed tool is routed to the Thought Engine for conversational processing (e.g., "Analyze my Google Cloud costs for the last month.").

> **Note on Tool List:** The tools listed in this document are a *provisional set* based on the MAD's high-level requirements. The final, authoritative list of tools, their specific parameters, and their return schemas will be defined in a dedicated Design Document prior to implementation.

---

## 3. Public Action Engine Tools

### `brin_authenticate_service`
- **Description:** Handles OAuth authentication and credential management for any Google service.
- **Input Schema:**
    - `service_name` (string, required): The name of the Google service (e.g., "Google Drive", "Vertex AI").
    - `scopes` (array[string], required): A list of OAuth scopes required for access.
- **Output Schema:** `{"status": "success", "access_token": "...", "expires_in": 3600}`

### `brin_execute_gcp_command`
- **Description:** Executes operations on Google Cloud Platform resources (e.g., `gcloud` commands or API calls).
- **Input Schema:**
    - `project_id` (string, required): The GCP project ID.
    - `command` (string, required): The GCP command to execute (e.g., "compute instances start instance-1").
    - `parameters` (dict, optional): Command-specific parameters.
- **Output Schema:** `{"status": "success", "output": "...", "gcp_logs": [...]}`

### `brin_query_google_api`
- **Description:** A generic interface for calling any Google API endpoint with a specified service, endpoint, method, and payload.
- **Input Schema:**
    - `service` (string, required): The Google API service name (e.g., "drive", "gmail").
    - `endpoint` (string, required): The API endpoint path (e.g., "v3/files").
    - `method` (string, required): The HTTP method (e.g., "GET", "POST").
    - `payload` (dict, optional): The request body for POST/PUT/PATCH methods.
- **Output Schema:** `{"status": "success", "api_response": {...}}`

### `brin_check_quota_status`
- **Description:** Monitors API quota usage and limits for Google services.
- **Input Schema:**
    - `service_name` (string, required): The name of the Google service (e.g., "Google Cloud Vision API").
- **Output Schema:** `{"status": "success", "quotas": [{"metric": "requests_per_minute", "usage": 120, "limit": 300}, ...]}`

---

## 4. Future Evolution (Post-V0)

Brin is introduced in Phase 6 (Expansion) at V7.0 as the centralized Google ecosystem integration hub for the mature Joshua system.

*   **Phase 6 (Expansion / V7.0):** Brin enters the ecosystem as a fully-capable V7.0 MAD with complete PCP (DTR, LPPM, CET, CRS), pure Kafka conversation bus integration, and eMAD awareness. As the Google ecosystem manager, Brin provides unified access to GCP, Google Workspace, Google AI/ML services, and all other Google technologies. Brin's Thought Engine orchestrates complex multi-service workflows (e.g., data pipeline from Google Sheets → BigQuery → Vertex AI → Cloud Storage), while its PCP enables learning optimal integration patterns and adapting to API changes. Brin consolidates all Google-related capabilities, eliminating redundant authentication and API client implementations across the MAD fleet.

*   **Post-V7.0 Enhancements:** Future evolution focuses on expanding breadth and depth of Google service integration. As Joshua adopts new Google technologies (Firebase real-time features, new Gemini model variants, Google Ads API, YouTube Data API, etc.), they are seamlessly added as tools within Brin. Brin's CRS learns cross-service optimization patterns, automatically routing requests to the most cost-effective and performant Google service combinations. Integration with Lovelace enables sophisticated data science workflows leveraging Google's AI platform, while collaboration with Fiedler allows intelligent model selection between local and Google-hosted LLMs based on cost, latency, and capability requirements.

---