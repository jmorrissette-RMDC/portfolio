# Gates Requirements

- **Role**: Microsoft Ecosystem Manager
- **Version**: V7.0
- **Home**: `mads/gates/`

---

## 1. Overview

-   **Purpose**: `Gates` is the specialized MAD responsible for all integration and interaction with Microsoft ecosystem services and APIs within the Joshua system. It acts as the system's unified interface to Microsoft technologies.
-   **V7.0 Scope Definition**: As a V7.0 MAD, Gates is a fully cognitive agent capable of orchestrating complex multi-service workflows across Microsoft Azure, Microsoft 365, and Microsoft AI services, while managing authentication, quotas, and costs.

---

## 2. Tool Exposure Model

This MAD follows the Direct Tool Exposure architecture (ADR-023). Its public tools are exposed directly on its MCP server and are discoverable via the Rogers registry. Any incoming communication that is not a valid MCP call for an exposed tool is routed to the Thought Engine for conversational processing (e.g., "Manage my Azure resources to optimize cost.").

> **Note on Tool List:** The tools listed in this document are a *provisional set* based on the MAD's high-level requirements. The final, authoritative list of tools, their specific parameters, and their return schemas will be defined in a dedicated Design Document prior to implementation.

---

## 3. Public Action Engine Tools

### `gates_authenticate_service`
- **Description:** Handles Azure AD authentication, OAuth flows, and credential management for any Microsoft service.
- **Input Schema:**
    - `service_name` (string, required): The name of the Microsoft service (e.g., "Microsoft 365", "Azure OpenAI").
    - `scopes` (array[string], required): A list of OAuth scopes required for access.
- **Output Schema:** `{"status": "success", "access_token": "...", "expires_in": 3600}`

### `gates_execute_azure_command`
- **Description:** Executes operations on Microsoft Azure resources (e.g., Azure CLI commands or Azure API calls).
- **Input Schema:**
    - `subscription_id` (string, required): The Azure subscription ID.
    - `command` (string, required): The Azure command to execute (e.g., "vm start my-vm").
    - `parameters` (dict, optional): Command-specific parameters.
- **Output Schema:** `{"status": "success", "output": "...", "azure_logs": [...]}`

### `gates_query_microsoft_api`
- **Description:** A generic interface for calling any Microsoft API endpoint with a specified service, endpoint, method, and payload.
- **Input Schema:**
    - `service` (string, required): The Microsoft API service name (e.g., "graph", "outlook").
    - `endpoint` (string, required): The API endpoint path (e.g., "v1.0/users").
    - `method` (string, required): The HTTP method (e.g., "GET", "POST").
    - `payload` (dict, optional): The request body for POST/PUT/PATCH methods.
- **Output Schema:** `{"status": "success", "api_response": {...}}`

### `gates_check_quota_status`
- **Description:** Monitors API quota usage and limits for Microsoft services.
- **Input Schema:**
    - `service_name` (string, required): The name of the Microsoft service (e.g., "Azure OpenAI Service").
- **Output Schema:** `{"status": "success", "quotas": [{"metric": "tokens_per_minute", "usage": 50000, "limit": 100000}, ...]}`

---

## 4. Future Evolution (Post-V0)

Gates is introduced in Phase 6 (Expansion) at V7.0 as the centralized Microsoft ecosystem integration hub for the mature Joshua system.

*   **Phase 6 (Expansion / V7.0):** Gates enters the ecosystem as a fully-capable V7.0 MAD with complete PCP (DTR, LPPM, CET, CRS), pure Kafka conversation bus integration, and eMAD awareness. As the Microsoft ecosystem manager, Gates provides unified access to Azure, Microsoft 365, Microsoft AI services, and all other Microsoft technologies. Gates's Thought Engine orchestrates complex multi-service workflows (e.g., data flow from SharePoint → Azure Synapse → Azure OpenAI → Power BI), while its PCP enables learning optimal integration patterns and adapting to Azure API evolution. Gates consolidates all Microsoft-related capabilities, eliminating redundant Azure AD authentication and service client implementations across the MAD fleet.
*   **Post-V7.0 Enhancements:** Future evolution focuses on expanding breadth and depth of Microsoft service integration. As Joshua adopts new Microsoft technologies (Power Platform enhancements, new Azure AI services, Dynamics 365 modules, Microsoft Graph extensions, etc.), they are seamlessly added as tools within Gates. Gates's CRS learns cross-service optimization patterns, automatically routing requests to the most cost-effective and performant Azure service combinations. Integration with Lovelace enables sophisticated data science workflows leveraging Azure ML, while collaboration with Fiedler allows intelligent model selection between local and Azure-hosted LLMs based on cost, latency, and capability requirements. Gates may also develop advanced Azure resource management capabilities, coordinating with Moses for optimal container placement on Azure Kubernetes Service.

---