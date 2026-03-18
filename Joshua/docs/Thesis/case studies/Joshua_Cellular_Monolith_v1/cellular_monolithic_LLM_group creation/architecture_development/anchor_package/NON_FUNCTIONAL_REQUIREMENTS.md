## 1. Overview

This document defines the global, non-functional requirements (NFRs) that apply to the entire Joshua Cellular Monolith ecosystem and all individual MADs within it. These cross-cutting concerns are foundational to ensure the system is performant, secure, observable, and maintainable. All MAD architecture and implementation must adhere to these standards.

---

## 2. Performance Targets

Performance expectations evolve with the architectural version of each MAD, reflecting the progressive cognitive filtering model. These are targets for the internal processing time of a MAD's Thinking Engine after receiving a message.

*   **V1 - Conversational (Imperator only):**
    *   **Target:** Median response time of **< 5 seconds** for standard reasoning tasks.
    *   **Rationale:** V1 relies entirely on the Imperator LLM for all cognitive tasks. This latency is acceptable for the initial phase of establishing conversational collaboration. Tasks are expected to be deliberative.

*   **V2 - Process Learning (+ LPPM):**
    *   **Target (Learned Patterns):** Median response time of **< 200 milliseconds** for workflows handled by the LPPM.
    *   **Target (Imperator Fallback):** Remains at < 5 seconds.
    *   **Rationale:** The LPPM intercepts and executes common, learned workflows, bypassing the slow Imperator. This provides a significant speedup for routine operations, making the MAD feel more responsive.

*   **V3 - Speed Optimization (+ DTR):**
    *   **Target (Routed Content):** Median processing time of **< 10 microseconds** for deterministic content routed by the DTR directly to the Action Engine.
    *   **Target (LPPM/Imperator):** Unchanged.
    *   **Rationale:** The DTR is a lightweight classifier that handles the majority of structured traffic (commands, data payloads). Its microsecond performance ensures that deterministic operations are near-instantaneous, freeing up cognitive resources for tasks that truly require them.

*   **V4 - Context Optimization (+ CET):**
    *   **Target:** While the CET adds a processing step, the overall *task completion time* for complex, multi-step problems requiring historical context should decrease by **20-40%**.
    *   **Rationale:** The CET optimizes the *quality* of the context provided to the Imperator. This results in more accurate, single-shot reasoning, reducing the need for conversational turns, error correction, and re-prompting. The goal is cognitive efficiency, not just raw speed.

---

## 3. Security Standards

The security posture for V1-V4 is defined by the "trusted research lab" environment. The focus is on secure access and internal integrity, not external threat hardening.

*   **Network Exposure:**
    *   **Requirement:** No MAD service shall expose a port directly to any network other than the internal Docker network (`joshua_net`).
    *   **Exception:** Grace may have a port mapped to the host machine for user access, but this host must not be exposed to the public internet.
*   **Diagnostic Access:**
    *   **Requirement:** All diagnostic access to MAD containers must be performed via SSH through a dedicated, hardened SSH gateway service.
    *   **Requirement:** Direct `docker exec` access is forbidden for routine diagnostics.
    *   **Requirement:** The SSH server within each MAD container must use `ForceCommand` to restrict users to a limited set of read-only diagnostic commands (e.g., `mad-status`, `mad-logs`). All SSH sessions must be logged as conversations.
*   **Key & Secret Management:**
    *   **Requirement:** All secrets (API keys, passwords, private keys) must be managed by the **Turing** MAD.
    *   **Requirement:** Secrets must not be stored in configuration files, source code, or Docker images. MADs must request secrets from Turing at startup or on-demand.
    *   **Requirement:** Turing itself will use a master key stored in a secure, restricted location (e.g., a hardware security module or an encrypted file on the host with strict permissions) for its initial bootstrap.
*   **Data Security:**
    *   **Requirement:** All data in transit on the Conversation Bus is considered trusted within the internal network. Encryption is not required for V1-V4.
    *   **Requirement:** Sensitive data at rest (e.g., secrets in Turing's database) must be encrypted using industry-standard algorithms (e.g., AES-256).

---

## 4. Logging Requirements

Logging is a fundamental aspect of the system's memory and observability. The principle is "log as conversation."

*   **Format:**
    *   **Requirement:** All logs, without exception, must be formatted as JSON-RPC 2.0 messages and published to a dedicated conversation on the Conversation Bus. The `joshua_logger` library is the standard implementation for this.
    *   **Requirement:** Each MAD must log to its own versioned conversation (e.g., `#logs-dewey-v1`).
*   **Content:**
    *   **Prose Logs:** Human-readable logs (e.g., "Initializing connection to database") should be used for key lifecycle events and diagnostic information.
    *   **Structured Logs:** Machine-readable logs containing key-value pairs (e.g., `{"event": "db_query", "duration_ms": 150, "rows_returned": 10}`) must be used for performance metrics, events, and any data intended for automated analysis.
*   **Log Retention:**
    *   **Requirement:** Rogers will retain logs in its "hot" database for **7 days**.
    *   **Requirement:** Dewey is responsible for archiving all log conversations from Rogers into the long-term data lake before they are purged. Long-term retention is defined as **indefinite** within the storage capacity of the NAS.

---

## 5. Data Handling

*   **Conversation Immutability:**
    *   **Requirement:** Conversations are append-only records. Once a message is added to a conversation by Rogers, it cannot be altered or deleted. This guarantees the integrity of the system's memory.
*   **Archivist Pattern:**
    *   **Requirement:** The **Dewey** MAD is the sole archivist for the ecosystem. It continuously monitors the Conversation Bus for conversations that become inactive or exceed a certain length/age.
    *   **Requirement:** Dewey copies these conversations to the long-term data lake (on the NAS) and then notifies Rogers that the conversation can be safely purged from the primary database.
*   **Data Lake (Winnipesaukee):**
    *   **Requirement:** The data lake, managed by Dewey, is the single source of truth for all historical data in the ecosystem.
    *   **Requirement:** Data in the lake should be organized and indexed to allow for efficient searching and retrieval by MADs (e.g., for the V4 CET).

---

## 6. Scalability Expectations

The architecture is designed for research-scale deployment in V1-V4, with features that enable future growth.

*   **V1-V2 Deployment:**
    *   **Expectation:** The entire ecosystem is expected to run on a single, powerful server or a small, tightly-coupled cluster. Vertical scaling (more RAM/CPU) is the primary method for performance improvement.
*   **V3-V4 Efficiency:**
    *   **Expectation:** The efficiency gains from the DTR and LPPM will allow the system to handle a significantly higher volume of conversations and tasks on the same hardware. This phase focuses on "doing more with less."
*   **eMAD Elasticity:**
    *   **Expectation:** The primary mechanism for horizontal scaling is the **Ephemeral MAD (eMAD)** pattern. For tasks that are highly parallelizable (e.g., code generation, data analysis), multiple eMAD instances (like Hopper or Playfair) can be spun up on demand.
    *   **Requirement:** The architecture must support the dynamic instantiation and termination of eMAD containers and the persistence of their shared, role-based ML models.

---

## 7. Observability

The system must be able to report on its own health and status.

*   **MAD Health:**
    *   **Requirement:** Every MAD must expose a `mad-status` command via its SSH diagnostic interface, which returns its current state (e.g., `RUNNING`, `DEGRADED`), version, and key metrics (e.g., active connections, memory usage).
*   **Ecosystem Monitoring:**
    *   **Requirement:** The **McNamara** MAD is responsible for overall ecosystem health monitoring.
    *   **Requirement:** McNamara actively monitors all logging conversations for error patterns, performance degradation, and security anomalies.
    *   **Requirement:** When a critical issue is detected, McNamara must initiate a high-priority conversation in an `#ops-alerts` channel, tagging the relevant MADs and potentially Grace to notify the user.

---
---