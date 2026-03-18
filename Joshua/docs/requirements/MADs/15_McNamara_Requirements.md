# McNamara Requirements

- **Role**: Security Operations
- **Version**: V7.0
- **Home**: `mads/mcnamara/`

---

## 1. Overview

-   **Purpose**: McNamara is the Security Operations Center (SOC) for the Joshua ecosystem, responsible for monitoring, analyzing, and responding to security events.
-   **V7.0 Scope Definition**: As a V7.0 MAD, McNamara provides a comprehensive and cognitive suite of tools for threat detection, incident response, and security auditing, with an Imperator capable of real-time threat analysis and strategic response planning.

---

## 2. Tool Exposure Model

This MAD follows the Direct Tool Exposure architecture (ADR-023). Its public tools are exposed directly on its MCP server and are discoverable via the Rogers registry. Any incoming communication that is not a valid MCP call for an exposed tool is routed to the Thought Engine for conversational processing (e.g., "Analyze the recent login failures from external IPs for potential threats.").

> **Note on Tool List:** The tools listed in this document are a *provisional set* based on the MAD's high-level requirements. The final, authoritative list of tools, their specific parameters, and their return schemas will be defined in a dedicated Design Document prior to implementation.

---

## 3. Public Action Engine Tools

### `mcnamara_get_security_posture`
- **Description:** Returns a summary of the current security posture of the ecosystem, including active alerts and identified vulnerabilities.
- **Input Schema:** (no parameters)
- **Output Schema:** `{"status": "success", "posture": "medium_risk", "active_incidents": 2, "vulnerabilities_found": 5}`

### `mcnamara_query_security_events`
- **Description:** Queries historical security-related events from the conversation bus based on specified filters.
- **Input Schema:**
    - `filter` (dict, required): Filter criteria for events (e.g., `{"tags": ["security_alert"], "severity": "high"}`).
    - `time_range` (string, optional, default: "24h"): The time range to search.
- **Output Schema:** `{"status": "success", "events": [{"timestamp": "...", "source": "bace", "description": "Failed login attempt"}, ...]}`

### `mcnamara_initiate_incident_response`
- **Description:** Initiates an automated incident response workflow for a detected security event.
- **Input Schema:**
    - `incident_id` (string, required): The ID of the incident to respond to.
    - `response_plan` (string, optional): A specific response plan to follow (e.g., "containment_plan_1").
- **Output Schema:** `{"status": "success", "response_status": "in_progress", "incident_id": "..."}`

---

## 4. Future Evolution (Post-V0)

McNamara is introduced in Phase 6 (Expansion) at V7.0 as the Security Operations Center for the mature Joshua ecosystem.

*   **Phase 6 (Expansion / V7.0):** McNamara enters the ecosystem as a fully-capable V7.0 MAD with complete PCP (DTR, LPPM, CET, CRS), pure Kafka conversation bus integration, and eMAD awareness. As the security operations specialist, McNamara monitors conversation bus traffic for security events and threats, coordinating with Bace (authentication/authorization), Cerf (network gateway), Clarke (cryptography), and domain-specific MADs. McNamara's CET enables complex incident response workflows (detect → analyze → contain → remediate → report), while CRS learns from historical security incidents to continuously improve threat detection models and response strategies. McNamara's LPPM learns normal operational patterns for accurate anomaly detection.

*   **Post-V7.0 Enhancements:** Future evolution includes real-time threat intelligence integration, automated penetration testing, vulnerability scanning and patch management coordination, security information and event management (SIEM) capabilities, compliance monitoring and reporting (SOC2, GDPR, HIPAA), proactive threat hunting, and strategic security planning aligned with Joshua's constitutional principles. McNamara becomes the autonomous SOC for the entire ecosystem.

---