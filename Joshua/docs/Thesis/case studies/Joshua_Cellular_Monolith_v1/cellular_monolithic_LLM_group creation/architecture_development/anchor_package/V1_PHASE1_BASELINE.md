## 1. Overview

This document specifies the components, libraries, and infrastructure that have been successfully implemented, tested, and deployed as part of the **V1 Phase 1 Baseline**. This baseline represents the current, stable state of the Joshua Cellular Monolith architecture. All future development for V1 Phase 2 and beyond will build upon this foundation.

---

## 2. Completed MAD Implementations (V1)

The following MADs are implemented to a V1 standard, meaning they are fully integrated with the Conversation Bus and possess a functional Imperator for reasoning.

### 2.1. Rogers V1 Phase 1 Complete

*   **Component:** Conversation Bus Manager
*   **Status:** **OPERATIONAL**
*   **Backend:** PostgreSQL 15, `rogers` schema. Manages `conversations` and `messages` tables.
*   **Network:**
    *   WebSocket server listening on internal port `9000`.
    *   SSH diagnostic server listening on internal port `2222`.
*   **Integration:**
    *   Successfully integrated with Dewey for the Archivist pattern.
    *   Serves as the central communication hub for all MAD-to-MAD traffic.
    *   Imperator instance configured for self-diagnosis and status reporting.
*   **Proven MAD Commands (via SSH):**
    *   `mad-status`: Reports operational status, connected clients, and message counts.
    *   `mad-config`: Displays current (redacted) configuration.
    *   `mad-state`: Dumps internal state metrics.
    *   `mad-conversations`: Lists active conversations.
    *   `mad-connections`: Lists currently connected MAD clients.

### 2.2. Dewey V1 Phase 1 Complete

*   **Component:** Data Lake Manager / Librarian
*   **Status:** **OPERATIONAL**
*   **Backend:** PostgreSQL 15, `dewey` schema. Manages archival metadata.
*   **Network:**
    *   WebSocket server for communication, listening on internal port `9001`.
    *   SSH diagnostic server listening on internal port `2222`.
*   **Integration:**
    *   Imperator instance configured for managing archival tasks.
    *   Continuously monitors Rogers for inactive conversations.
    *   Successfully archives conversations from Rogers' DB to the NAS-backed data lake.
*   **Proven MAD Commands (via SSH):**
    *   `mad-status`: Reports status of the archivist process and data lake size.
    *   `mad-config`: Displays current (redacted) configuration.
    *   `mad-state`: Reports metrics on last run, conversations archived, etc.
    *   `mad-archives`: Provides statistics on the contents of the data lake.

---

## 3. Shared Libraries

These standardized Python libraries have been developed and are used by all baseline MADs to ensure consistency and reliability.

*   **`Joshua_Communicator` v1.2.0:**
    *   **Purpose:** Provides a robust client and server implementation of JSON-RPC 2.0 over WebSockets.
    *   **Features:** Handles message serialization/deserialization, request/response matching, and connection management.
    *   **Status:** Stable and in use by Rogers and Dewey.

*   **`joshua_logger` v1.0.0:**
    *   **Purpose:** Implements the "logging as conversation" pattern.
    *   **Features:** A logging handler that formats log records into valid `Joshua_Communicator` messages and sends them to a specified logging conversation on the bus.
    *   **Status:** Stable and integrated into all baseline MADs.

*   **`joshua_ssh` v0.1.0:**
    *   **Purpose:** Provides a secure, standardized diagnostic backdoor for MADs.
    *   **Features:** Sets up an SSH server that uses a `ForceCommand` script to expose a safe, read-only subset of diagnostic commands. All access is logged.
    *   **Status:** Deployed and functional in Rogers and Dewey.

---

## 4. Deployed Infrastructure

The following infrastructure components are deployed and configured.

*   **Containerization:** All MADs and services are deployed as Docker containers. `docker-compose` is used for orchestration in the lab environment.
*   **Database:** A single PostgreSQL 15 container is deployed, providing database services to all MADs that require them.
*   **Networking:** A dedicated Docker network, `joshua_net`, has been created. All MAD-to-MAD and MAD-to-DB communication occurs exclusively on this network, isolating it from the host.

---

## 5. What Works: Proven Capabilities and Patterns

This baseline has successfully proven the viability of the core architectural concepts.

*   **MAD-to-MAD Communication:** Rogers and Dewey can successfully hold conversations, demonstrating the functionality of the Conversation Bus. Dewey can request data from Rogers, and Rogers can respond.
*   **Conversation-based Logging:** All components successfully log to dedicated conversations on the bus.
*   **Secure Diagnostics:** The SSH diagnostic backdoor provides secure, logged, read-only access to the internal state of the MADs without exposing a full shell.
*   **Archivist Pattern:** The core loop of Dewey monitoring Rogers, archiving data, and notifying Rogers for cleanup is fully functional.
*   **Configuration Security:** The pattern of redacting secrets from configuration files and diagnostic outputs is implemented and verified.
*   **Conversation Immutability:** The database schema and application logic in Rogers enforce the append-only nature of conversations.

This stable and proven baseline provides a strong foundation for the development and integration of the remaining 11 MADs to a V1 standard.

---
---