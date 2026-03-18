# Henson Requirements

- **Role**: Context Engineering
- **Version**: V0.8
- **Home**: `mads/henson/`

---

## 1. Overview

-   **Purpose**: Henson provides context engineering services to the Joshua ecosystem.
-   **V0.8 Scope Definition**: In its initial V0.8 incarnation, Henson's primary role is to host the **Fast RAG** services. It provides an ultra-fast, in-memory vector store for MAD personas/rules and recent conversation history, serving as a precursor to the full Context Engineering Transformer (CET) of V4.0+.

---

## 2. Tool Exposure Model

Henson is a specialized service MAD. It follows the Direct Tool Exposure architecture (ADR-023), but its tools are highly specific to its context-providing role and are not typically called directly by users. They are designed to be used by the Thought Engines of other MADs.

> **Note on Tool List:** The tools listed in this document are a *provisional set* based on the MAD's high-level requirements. The final, authoritative list of tools, their specific parameters, and their return schemas will be defined in a dedicated Design Document prior to implementation.

---

## 3. Public Action Engine Tools

### `henson_query_fast_rag`
- **Description:** Performs a vector similarity search against one of the in-memory Fast RAG stores.
- **Input Schema:**
    - `rag_source` (string, required): The source to query. Must be one of `["persona", "recent_conversation"]`.
    - `query_embedding` (array[float], required): The vector embedding of the query text.
    - `limit` (integer, optional, default: 5): The maximum number of results to return.
- **Output Schema:** `{"status": "success", "results": [{"content": "...", "similarity": 0.94}, ...]}`

### `henson_update_persona_store`
- **Description:** Updates the in-memory vector store for a specific MAD's persona and rules. This is typically called by `Joshua` or `Hopper` when a MAD's configuration changes.
- **Input Schema:**
    - `mad_name` (string, required): The name of the MAD whose persona is being updated.
    - `persona_content` (string, required): The full text of the persona and rules document.
- **Output Schema:** `{"status": "success", "message": "Persona store for 'hopper' updated."}`

---

## 4. Future Evolution (Post-V0)

Henson's role expands significantly in later phases to become the host of the full Context Engineering Transformer (CET).

*   **Phase 1 (Foundation / V0.8):** Henson is introduced to the V0.10 Core Fleet to provide "Fast RAG" services. It hosts in-memory vector stores for MAD personas/rules (Fast RAG #1) and recent conversation history (Fast RAG #2), providing a foundational context optimization layer.
*   **Phase 3 (Cognition / V4.0 -> V5.0):** As the ecosystem migrates to V5.0, Henson is upgraded to host the full **Context Engineering Transformer (CET)**. It orchestrates context assembly from multiple distributed RAG sources (`Babbage`, `Horace`, `Codd`) and uses a shared transformer model with domain-specific LoRA adapters to engineer optimal context for every Imperator request.
*   **Phase 5 (Autonomy / V7.0):** Henson's CET integrates with Joshua MAD's strategic directives, allowing for constitutional principles and high-level goals to be dynamically injected into the context of all MADs, ensuring system-wide alignment.

---