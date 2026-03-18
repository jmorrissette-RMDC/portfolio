# Hamilton Requirements

- **Role**: System Monitoring & Observability
- **Version**: V7.0
- **Home**: `mads/hamilton/`

---

## 1. Overview

-   **Purpose**: Hamilton provides system monitoring and observability to the ecosystem through a conversational and programmatic interface.
-   **V7.0 Scope Definition**: As a V7.0 MAD, Hamilton is a fully cognitive agent that passively monitors all bus traffic, tracks key quality and performance metrics, analyzes system health, and provides intelligent alerting and querying capabilities.

---

## 2. Tool Exposure Model

This MAD follows the Direct Tool Exposure architecture (ADR-023). Its public tools are exposed directly on its MCP server and are discoverable via the Rogers registry. Any incoming communication that is not a valid MCP call for an exposed tool is routed to the Thought Engine for conversational processing (e.g., "What's the health of the system?").

> **Note on Tool List:** The tools listed in this document are a *provisional set* based on the MAD's high-level requirements. The final, authoritative list of tools, their specific parameters, and their return schemas will be defined in a dedicated Design Document prior to implementation.

---

## 3. Public Action Engine Tools

### `hamilton_get_system_status`
- **Description:** Returns a high-level summary of the current health of the entire ecosystem.
- **Input Schema:** (no parameters)
- **Output Schema:** `{"status": "success", "system_status": "healthy", "active_alerts": 0, "mad_states": {"fiedler": "online", "hopper": "degraded", ...}}`

### `hamilton_query_logs`
- **Description:** Queries archived conversation logs for specific messages based on a filter.
- **Input Schema:**
    - `filter` (dict, required): A dictionary of filter criteria (e.g., `{"tags": ["error"], "participant_id": "hopper"}`).
    - `time_range` (string, optional, default: "1h"): The time range to search (e.g., "1h", "24h", "7d").
- **Output Schema:** `{"status": "success", "log_count": 5, "logs": [{"timestamp": "...", "participant_id": "...", "content": "..."}]}`

### `hamilton_get_metrics`
- **Description:** Retrieves a time-series for a specific performance or quality metric.
- **Input Schema:**
    - `metric_name` (string, required): The name of the metric to retrieve (e.g., "error_rate_fiedler").
    - `time_range` (string, optional, default: "1h"): The time range for the data.
- **Output Schema:** `{"status": "success", "metric_name": "...", "data_points": [{"timestamp": "...", "value": 0.1}, ...]}`

---

## 4. Future Evolution (Post-V0)

Hamilton's role as the system monitoring and observability platform evolves to become an intelligent, eMAD-aware observer of the entire Joshua ecosystem.

*   **Phase 1 (Foundation / V0.10):** Hamilton is hardened and quality-gated for flawless Direct Communication, becoming the reliable observability platform for the V0.10 Core Fleet, continuously monitoring all MAD health and system metrics.
*   **Phase 2 (Conversation / V1.0):** Hamilton is re-platformed to monitor the Rogers Conversation Bus (pure Kafka), consuming all conversation logs to track system-wide activity, error patterns, and performance metrics in real-time. All monitoring data flows through the durable conversation log.
*   **Phase 4 (eMADs / V6.0):** Hamilton becomes eMAD-aware, capable of monitoring ephemeral MAD teams, tracking their lifecycle from provisioning through termination, and aggregating metrics across dynamic populations of short-lived eMAD instances.
*   **Phase 5 (Autonomy / V7.0):** Hamilton integrates with Joshua MAD's strategic orchestration, providing top-down visibility into system health, alerting on strategic metrics, and enforcing constitutional monitoring policies across the entire ecosystem.

---