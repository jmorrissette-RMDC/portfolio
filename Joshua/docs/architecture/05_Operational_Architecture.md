# Operational Architecture

**Version**: 1.0 (Unified)
**Status:** Authoritative

---

## 1. Overview

The operational architecture of the Joshua ecosystem is built on the principle of **"Operations as a Service."** Key operational functions like logging, CI/CD, security, and secrets management are not handled by external tooling but by specialist MADs that are first-class citizens of the ecosystem. These MADs leverage the communication infrastructure to monitor, analyze, and act on system events in real-time.

This document describes the evolution of these operational services from the V0 direct-communication model to the V1+ bus-centric model.

## 2. Observability and Logging

The logging architecture evolves from a simple, direct model in V0 to a highly sophisticated, observable, bus-based system in V1+. All logging across the MAD ecosystem is standardized and centrally managed by the `Joshua_Communicator` library, as defined in **ADR-021 (Unified I/O and Logging Hub)**, which also mandates structured logging (see **ADR-028: Core Coding Practice Standards**).

### 2.1. V0 Logging: `Joshua_Communicator` to `stdout`

In the V0 architecture, logging is a unified function of the mandatory `Joshua_Communicator` library.
-   **Unified Interface:** Each MAD uses the integrated logger provided by its `Communicator` instance (e.g., `communicator.log.info(...)`).
-   **Standardized Output:** The `Joshua_Communicator` formats logs as structured JSON and writes them directly to `stdout`.
-   **External Collection:** Docker captures the `stdout` from all MAD containers, making logs accessible via `docker logs`. This allows for centralized collection by external tools (e.g., Logstash, Fluentd).
-   **Limitation:** This model provides logs but lacks a central, in-ecosystem way to query or correlate them. Observability is external, not an intrinsic property of the system.

### 2.2. V1+ Logging: The Bus as the Source of Truth

The V1+ architecture revolutionizes observability by making the **conversation bus the ultimate source of truth**.
-   **Bus-First Logging:** The `Joshua_Communicator`'s logger is configured to publish log messages directly to dedicated Kafka topics on the bus.
-   **Passive Monitoring:** Specialist MADs (`Hamilton` for performance/health, `McNamara` for security) subscribe to these log topics. They passively listen to the firehose of messages, filtering, aggregating, and analyzing them in real-time.
-   **Central Archival:** `Babbage` also subscribes to all log topics, creating a permanent, queryable archive of all system logs as part of its CQRS read models.
-   **Conversational Queries:** Instead of external dashboards, operators can directly ask `hamilton_query_logs` or `mcnamara_query_security_events` to get insights.
-   **Fallback Mechanism:** If the bus is unavailable, the `Joshua_Communicator` automatically falls back to writing logs to a local mounted volume, ensuring no data is lost. This local log can then be ingested by `Deming` for gap filling once the bus is restored.

## 3. Programming, CI/CD and Testing

The CI/CD process is managed conversationally by **`Starret`** and orchestrated by **`Hopper`**. The core pattern remains consistent, but the communication method evolves.

-   **V0:** `Hopper` makes a **direct tool call** to `starret_test_pr` using its `Joshua_Communicator` client to initiate a test run.
-   **V1+:** `Hopper` **publishes a request** (e.g., `test_package`) to a `testing` topic on the conversation bus, which `Starret` is subscribed to. `Starret` then executes the tests in isolated Docker containers.
-   **Reporting:** `Starret` broadcasts `test_result` messages to the project conversation. `Hopper` listens for this to decide the next step (e.g., deployment).

## 4. Secrets Management

Secrets management is provided as a service by the **`Turing`** MAD. It ensures no other MAD ever needs to handle raw credentials. **ADR-028 (Core Coding Practice Standards)** explicitly mandates no hardcoded secrets and details a temporary exception for environment variables until `Turing` is fully operational.

-   **Centralized Store:** `Turing` manages an encrypted vault for all secrets.
-   **Interaction Evolution:**
    *   In **V0**, a MAD like `Fiedler` makes a **direct tool call** to `turing_retrieve_secret` via its `Joshua_Communicator`. `Turing`'s Action Engine authorizes the request based on the caller's network identity.
    *   In **V1+**, `Fiedler` **publishes a request** (e.g., `secrets_retrieve`) for a secret to a private topic on the bus. `Turing` authorizes based on the `participant_id` in the message.
-   **Audit Trail:** In V1+, every secret access request and response is a message on the bus, creating a complete, immutable audit trail for `McNamara` to monitor.

## 5. Security Operations Architecture

Security is a collaborative, conversation-based process managed by a team of specialist MADs, with **`McNamara`** (the Security Operations Center) at the hub. This architecture promotes real-time threat analysis and coordinated response.

-   **Monitoring (McNamara):** As the SOC, `McNamara` listens for security-related broadcasts (e.g., `user_login_failed`, `secret_accessed`, `network_anomaly_detected`) from other MADs (`Bace`, `Turing`, `Cerf`).
-   **Identity & Access (`Bace`):** Handles all authentication/authorization and broadcasts critical events.
-   **Secrets (`Turing`):** Manages all secrets and broadcasts audit events like `secret_accessed`.
-   **Cryptography (`Clarke`):** Provides cryptographic primitives as a service.
-   **Network (`Cerf`):** In V1.0, `Cerf` passively monitors conversation metadata for network anomalies and broadcasts alerts; it evolves into an active API Gateway in later phases.
-   **SSH Backdoor:** Every MAD container provides an SSH backdoor for emergency debugging. SSH access attempts are logged locally and, when the bus is operational, broadcast as audit events for `McNamara`.
-   **Local LLM Failover:** Each MAD's ability to operate autonomously using a local Small Language Model (SLM) when external LLM services are unavailable (as detailed in **ADR-029: Local Ollama Failover Architecture**) significantly enhances system resilience and security by preventing complete service outages.

## 6. Key Decisions and Constraints

### Key Decisions
-   **Operations as a Service:** Treating operational functions as conversational services provided by specialist MADs keeps the architecture clean and consistent.
-   **Bus as a Sensor Grid (V1+):** The conversation bus acts as a rich source of real-time operational data, enabling powerful, context-aware monitoring and security analysis.
-   **Unified `Joshua_Communicator` for Logging (ADR-021, ADR-028):** Centralizing all logging within the `Joshua_Communicator` library simplifies architecture, developer experience, and enhances system-wide observability.
-   **Environment-Specific Storage (ADR-025):** Ensures strict isolation of data across development, testing, and production environments, and formalizes the code promotion model.

### Constraints and Limitations
-   **V0 Observability Gaps:** Without a central bus, it's impossible to capture the full picture of inter-MAD communication. Only what is explicitly logged is visible.
-   **Brittle CI/CD Orchestration (V0):** The CI/CD process relies on a hard-coded sequence of direct tool calls.
-   **Complex Security Auditing (V0):** Auditing requires manual collation of logs from multiple sources.
-   **Observability Latency (V1+):** There is a slight delay in observability as events must be broadcast, routed, and processed by `Deming`/`McNamara`.
-   **Centralized Test Runner (V1+):** `Starret` could become a bottleneck if many tests are run concurrently.
-   **Secret Security:** The security of the entire system's credentials relies on the correct implementation and security of `Turing`.