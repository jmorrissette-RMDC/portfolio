# Rogers Requirements

- **Role**: Conversation Bus Controller & Service Registry
- **Version**: V1.0
- **Home**: `mads/rogers/`

---

## 1. Overview

-   **Purpose**: Rogers is the central nervous system of the Joshua V1.0+ ecosystem, providing two distinct but related services:
    1.  **Conversation Bus Controller (Transport):** Manages the lifecycle of conversations on the Kafka bus.
    2.  **Service Registry (Discovery):** Acts as the authoritative source for discovering the capabilities and tools of all online MADs.
-   **V1.0 Scope Definition**: Implement the pure-Kafka control plane and the service registry, enabling a fully decoupled, observable, and discoverable V1.0 ecosystem.

---

## 2. Tool Exposure Model

Rogers is a core infrastructure MAD. It follows the Direct Tool Exposure architecture (ADR-023), exposing a specific set of tools for bus management and service discovery. Any other communication is routed to its Thought Engine for conversational status queries (e.g., "How many active conversations are there?").

> **Note on Tool List:** The tools listed in this document are a *provisional set* based on the MAD's high-level requirements. The final, authoritative list of tools, their specific parameters, and their return schemas will be defined in a dedicated Design Document prior to implementation.

---

## 3. Public Action Engine Tools

### 3.1 Service Registry Tools (per ADR-022)

#### `rogers_register_tools`
- **Description:** Called by a MAD upon startup to register its public tools and capabilities with Rogers.
- **Input Schema:**
    - `mad_name` (string, required): The name of the registering MAD.
    - `tool_manifest` (dict, required): A manifest detailing the MAD's offerings.
        - `tools` (array[string]): A list of public tool names (e.g., `["horace_file_read"]`).
        - `capabilities` (array[string]): A list of abstract capabilities (e.g., `["file_system_management"]`).
- **Output Schema:** `{"status": "success", "registered_tools": 2, "registered_capabilities": 1}`

#### `rogers_find_capability`
- **Description:** Queries the registry to find which MAD(s) provide a general capability.
- **Input Schema:**
    - `capability` (string, required): The abstract capability to search for (e.g., "git_management").
- **Output Schema:** `{"status": "success", "capability": "git_management", "providers": ["starret"]}`

#### `rogers_find_tool`
- **Description:** Queries the registry to find which MAD provides a specific, named tool.
- **Input Schema:**
    - `tool_name` (string, required): The exact name of the tool (e.g., "starret_commit").
- **Output Schema:** `{"status": "success", "tool_name": "starret_commit", "provider": "starret"}`

### 3.2 Conversation Bus Control Plane Tools

#### `rogers_create_conversation`
- **Description:** Creates a new conversation (i.e., a new Kafka topic) and registers the initial participants.
- **Input Schema:**
    - `topic_name` (string, required): A human-readable name for the conversation.
    - `participants` (array[string], required): A list of initial MADs to include.
- **Output Schema:** `{"status": "success", "conversation_id": "topic-uuid-1234", "topic_name": "..."}`

#### `rogers_get_conversation_info`
- **Description:** Retrieves the metadata for an existing conversation.
- **Input Schema:**
    - `conversation_id` (string, required): The ID of the conversation.
- **Output Schema:** `{"status": "success", "info": {"participants": ["hopper", "starret"], "created_at": "..."}}`

---

## 4. Future Evolution (Post-V0)

As the Joshua ecosystem evolves, Rogers' role as the conversation bus becomes the central communication and learning substrate.

*   **Phase 2 (Conversation / V1.0):** Rogers is re-platformed to a pure Apache Kafka architecture (ADR-007 v2) to serve as the durable, learnable communication fabric for all Core Fleet MADs. This eliminates the WebSocket-based implementation in favor of Kafka's high-performance, distributed log.

    **V1.0 Architectural Changes:**
    - **Rogers as Bus Controller:** Rogers transitions from being an active message router to a **control plane manager**. MADs publish and consume messages directly from Kafka topics; Rogers only manages topic lifecycle, service registry, and administrative operations. This separation allows Kafka to handle data plane scalability independently.
    - **Babbage as CQRS Consumer:** The Babbage MAD becomes the **primary consumer** of the Kafka log, continuously reading the complete event stream and building **CQRS Read Models** in MongoDB. Kafka provides the write-optimized log; Babbage transforms it into read-optimized document structures for complex queries and long-term archival.
    - **Durable Fast Lane:** Kafka's architecture provides low-millisecond latency (via OS page cache) and guaranteed persistence (via durable log) simultaneously, eliminating the need for separate in-memory systems.

*   **Phase 3 (Cognition / V5.0):** Rogers receives the full PCP stack (DTR, LPPM, CET, CRS), enabling it to intelligently manage conversation routing, optimize topic creation, and learn from communication patterns. Babbage's Read Models become the primary source of training data for the ecosystem's learning tiers—LPPM learns from conversation patterns, CET optimizes context assembly from historical interactions, and CRS refines routing strategies based on observed outcomes.

*   **Phase 4 (eMADs / V6.0):** Rogers becomes eMAD-aware, capable of managing ephemeral conversation participants and dynamically created topics for short-lived eMAD teams.

*   **Phase 5 (Autonomy / V7.0):** Rogers integrates with Joshua MAD's strategic orchestration, receiving top-down directives for system-wide communication policies and constitutional guidance enforcement.

---