# Babbage Requirements

- **Role**: Semi-Structured Data Management
- **Version**: V1.0
- **Home**: `mads/babbage/`

---

## 1. Overview

-   **Purpose**: Babbage is the specialist MAD for managing semi-structured data using document databases (MongoDB).
-   **V1.0 Scope Definition**: In the V1.0 pure-Kafka architecture, Babbage's primary role is to act as the **primary durable consumer of the Kafka log** and the builder of **CQRS Read Models**. It provides the queryable, long-term memory for the entire ecosystem.

---

## 2. Tool Exposure Model

This MAD follows the Direct Tool Exposure architecture (ADR-023). Its public tools are exposed directly on its MCP server and are discoverable via the Rogers registry. Any incoming communication that is not a valid MCP call for an exposed tool is routed to the Thought Engine for conversational processing (e.g., "Find all conversations from last week involving an error in the Hopper MAD.").

> **Note on Tool List:** The tools listed in this document are a *provisional set* based on the MAD's high-level requirements. The final, authoritative list of tools, their specific parameters, and their return schemas will be defined in a dedicated Design Document prior to implementation.

---

## 3. Public Action Engine Tools

### `babbage_find_documents`
- **Description:** Finds and retrieves documents from a specified collection based on a MongoDB query filter. This is the primary query interface for the CQRS Read Models.
- **Input Schema:**
    - `collection` (string, required): The name of the collection to query (e.g., "conversations", "logs").
    - `filter` (dict, required): A MongoDB-style query filter.
    - `projection` (dict, optional): A MongoDB-style projection to shape the output.
- **Output Schema:** `{"status": "success", "documents": [{"_id": "...", ...}, ...]}`

### `babbage_store_document`
- **Description:** Stores a single document in a specified collection. (Note: In V1.0, this is less common, as most data arrives via the Kafka consumer. This tool is for direct storage requests).
- **Input Schema:**
    - `collection` (string, required): The name of the collection.
    - `document` (dict, required): The document to store.
- **Output Schema:** `{"status": "success", "document_id": "..."}`

---

## 4. Future Evolution (Post-V0)

Babbage's role evolves from a general semi-structured data manager to the critical memory and archival system for the entire Joshua ecosystem.

*   **Phase 2 (Conversation / V1.0):** Babbage is re-platformed as the primary **Kafka log consumer** and **CQRS Read Model builder** (ADR-007 v2). It continuously consumes the immutable conversation log from Rogers/Kafka and transforms it into efficiently queryable Read Models in MongoDB. This fulfills the Query side of the CQRS pattern, separating the durable write log (Kafka) from optimized read structures (MongoDB). Babbage becomes the system's memory, making all historical conversation data accessible for analysis and learning.
*   **Phase 3 (Cognition / V5.0):** Babbage receives the full PCP stack (DTR, LPPM, CET, CRS), enabling intelligent query optimization, learned indexing strategies, and advanced data transformation pipelines. The Read Models built by Babbage become the foundational training datasets for the ecosystem's PCP tiers, with Babbage serving as the data pipeline that transforms raw conversation logs into structured learning inputs.
*   **Phase 4 (eMADs / V6.0):** Babbage becomes eMAD-aware, capable of managing ephemeral conversation archives and providing specialized Read Models for short-lived eMAD team interactions.
*   **Phase 5 (Autonomy / V7.0):** Babbage integrates with Joshua MAD's strategic orchestration, implementing top-down data retention policies and constitutional data governance rules.

---