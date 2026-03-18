# Cerf Requirements

- **Role**: API Gateway & Network Monitor
- **Version**: V7.0
- **Home**: `mads/cerf/`

---

## 1. Overview

-   **Purpose**: Cerf is the ecosystem's API Gateway, providing secure and managed external access to MAD capabilities. In V7.0, it also acts as an intelligent network monitor for the conversation bus.
-   **V7.0 Scope Definition**: As a V7.0 MAD, Cerf provides a fully cognitive API gateway service, exposing a unified API, enforcing security policies, and actively monitoring bus traffic for anomalies. In earlier versions (e.g., V1.0), Cerf's role is primarily conceptual or limited to passive monitoring.

---

## 2. Tool Exposure Model

This MAD follows the Direct Tool Exposure architecture (ADR-023). Its public tools are exposed directly on its MCP server and are discoverable via the Rogers registry. Any incoming communication that is not a valid MCP call for an exposed tool is routed to the Thought Engine for conversational processing (e.g., "Analyze the recent traffic patterns for any security threats.").

> **Note on Tool List:** The tools listed in this document are a *provisional set* based on the MAD's high-level requirements. The final, authoritative list of tools, their specific parameters, and their return schemas will be defined in a dedicated Design Document prior to implementation.

---

## 3. Public Action Engine Tools

### `cerf_route_api_request`
- **Description:** Routes an incoming external API request to the appropriate internal MAD, translating protocols as necessary.
- **Input Schema:**
    - `external_endpoint` (string, required): The external API endpoint being called.
    - `mad_target_tool` (string, required): The target MAD's tool to invoke (e.g., "horace_file_read").
    - `payload` (dict, required): The payload of the request to forward.
- **Output Schema:** `{"status": "success", "response": {...}}`

### `cerf_get_api_metrics`
- **Description:** Retrieves metrics related to API gateway traffic, performance, and errors.
- **Input Schema:**
    - `time_range` (string, optional, default: "1h"): The time range for the metrics.
- **Output Schema:** `{"status": "success", "metrics": {"total_requests": 1000, "error_rate": 0.01, ...}}`

### `cerf_query_network_traffic`
- **Description:** Queries observed conversation bus traffic patterns for metadata analysis (e.g., communication frequency between MADs).
- **Input Schema:**
    - `filter` (dict, optional): Filter criteria for traffic (e.g., `{"source_mad": "hopper"}`).
    - `time_range` (string, optional, default: "1h"): The time range for the traffic data.
- **Output Schema:** `{"status": "success", "traffic_data": [...], "anomalies": [...]}`

---

## 4. Future Evolution (Post-V0)

Cerf is introduced in Phase 6 (Expansion) at V7.0 as the API Gateway providing secure external access to the mature Joshua ecosystem.

*   **Phase 6 (Expansion / V7.0):** Cerf enters the ecosystem as a fully-capable V7.0 MAD with complete PCP (DTR, LPPM, CET, CRS), pure Kafka conversation bus integration, and eMAD awareness. As the API Gateway, Cerf provides the primary ingress/egress point for all external Joshua integrations. It exposes a unified REST/GraphQL API for selective MAD capabilities, manages API keys and OAuth flows (coordinating with Bace), implements rate limiting and quota management (with Hamilton), and coordinates with McNamara for threat detection. Cerf's CET orchestrates complex request/response workflows across multiple internal MADs for external API consumers, while CRS learns optimal routing patterns and security threats.
*   **Post-V7.0 Enhancements:** Future evolution includes advanced API versioning strategies, GraphQL federation across MAD capabilities, WebSocket/gRPC support for real-time APIs, sophisticated caching strategies, API monetization features, and developer portal integration. Cerf's eMAD awareness enables intelligent routing to specialized MAD teams for complex external requests.

---