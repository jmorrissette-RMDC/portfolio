# ADR-026: Henson's Unified Embedding Model for RAG

**Status:** Accepted
**Date:** 2025-12-18
**Updated:** 2025-12-22 (Implementation details in ADR-039)
**Deciders:** System Architect

---

## 📝 Implementation Note (2025-12-22)

This ADR defines Henson's role as Context Engineer and the choice of M2-BERT 32K as the unified embedding model. For detailed implementation (CET-driven semantic chunking, hardware allocation, Qdrant configuration), see **ADR-039: RAG Embedding Strategy with CET-Driven Semantic Chunking**.

---

## Context and Problem Statement

The Joshua architecture designates the `Henson` MAD as the "Context Engineer" responsible for providing Retrieval-Augmented Generation (RAG) capabilities to the ecosystem. This functionality is critical for searching across multiple data sources to provide relevant context to other MADs.

However, the specific embedding model—the core technology `Henson` will use to convert text into searchable vectors—has not been formally specified. A decision is required to select a model that is powerful, efficient, and well-suited to the project's diverse data types and local-hosting requirements.

The primary challenge is addressing the varied nature of Henson's **Qdrant collections** (vector database indexes):
1.  **`persona_rules`:** Short, dense MAD behavior instructions
2.  **`conversations`:** Multi-turn dialogue from current and past Claude sessions
3.  **`logs`:** System error logs and debug sessions
4.  **`documents`:** ADRs, requirements, design docs, and documentation
5.  **`projects`:** Code repositories from `/mnt/projects` (Joshua codebase, libraries, configs)

## Decision Drivers

*   **Local Hosting:** The model must be open-source and capable of being run locally on project hardware.
*   **Performance:** The model must rank highly on retrieval benchmarks (like MTEB) to ensure relevant search results.
*   **Long-Context Capability:** The model must be able to effectively process long technical documents without losing critical semantic context, a known limitation of models with small (e.g., 512-token) context windows.
*   **Resource Efficiency:** The model should be computationally inexpensive for inference to ensure low-latency RAG performance without requiring dedicated high-end GPUs for the retrieval step.
*   **Architectural Simplicity:** The implementation within `Henson` should be as simple and maintainable as possible, aligning with the Cellular Monolith philosophy.

## Considered Options

### Option 1: A Specialized, Multi-Model Architecture

Use different, best-in-class embedding models for each of the five distinct collections.

*   **Example:**
    *   `BAAI/bge-large-en-v1.5` for `persona_rules` (high precision on short text)
    *   `sentence-transformers/all-mpnet-base-v2` for `conversations`
    *   `togethercomputer/m2-bert-80M-32k-retrieval` for `documents` and `projects`
    *   Separate model for `logs` (optimized for technical error text)
*   **Pros:**
    *   Theoretically offers the highest possible retrieval accuracy for each specific collection
*   **Cons:**
    *   Massively increases the complexity of the `Henson` MAD, which would need to host, manage, and route requests to multiple separate models
    *   Increases VRAM/RAM and maintenance overhead
    *   The marginal performance benefits may not justify the significant increase in complexity

### Option 2: A Unified, Single-Model Architecture

Select one single, powerful, and versatile embedding model to handle all five collections, while maintaining logically separate Qdrant collections.

*   **Model Candidates:**
    *   **`togethercomputer/m2-bert-80M-32k-retrieval`:** An 80M parameter model with an exceptional 32k token context window.
    *   **`nomic-ai/nomic-embed-text-v1.5`:** A strong performer with a large 8k token context window.
    *   **`BAAI/bge-large-en-v1.5`:** A top performer on MTEB, but with a restrictive 512-token context window.
*   **Pros:**
    *   Drastically simplifies the `Henson` MAD's architecture and operational footprint.
    *   A long-context model can handle all document types effectively, whereas a short-context model struggles with long documents.
    *   Reduces resource consumption and maintenance overhead.
*   **Cons:**
    *   May not be the absolute number one performer for *every single* use case, but a top-tier model should be highly effective across all of them.

## Decision Outcome

**Chosen Option:** Option 2, A Unified, Single-Model Architecture.

The selected model is **`togethercomputer/m2-bert-80M-32k-retrieval`**.

**Rationale:**

1.  **Dominant Long-Context Capability:** The 32,768-token sequence length is the single most important feature for this project. It is purpose-built to handle long architectural documents, code files, and conversation sessions without context loss or chunking complexity.
2.  **Versatility:** While optimized for long context, the model's performance remains high for shorter texts (persona rules, log entries), making it more than capable of handling all five collections effectively. The benefits of its long-context strength outweigh the marginal gains that might be achieved by using specialized short-text models.
3.  **Exceptional Efficiency:** With only 80 million parameters, the model is extremely lightweight. It requires minimal VRAM (~500MB model + batching) and can achieve ~800-1200 docs/sec on K80 GPU (see ADR-039 for hardware allocation). This allows the project's powerful V100 GPUs to be reserved for CET and other demanding workloads.
4.  **Architectural Simplicity:** This choice results in a much cleaner and more maintainable `Henson` MAD. It aligns with the project's philosophy of creating streamlined, specialized components. `Henson` will use this single model but will maintain five distinct Qdrant collections (`persona_rules`, `conversations`, `logs`, `documents`, `projects`) to provide logical data separation and collection-specific metadata schemas.

### Implementation Plan

1.  The `Henson` MAD's design document will be updated to specify `togethercomputer/m2-bert-80M-32k-retrieval` as its primary embedding model.
2.  `Henson`'s Action Engine will be implemented with tools for embedding generation and retrieval across all collections.
3.  `Henson` will manage five separate Qdrant collections:
    - **`persona_rules`:** MAD behavior instructions (metadata: mad_id, rule_type, priority)
    - **`conversations`:** Claude sessions (metadata: conversation_id, timestamp, message_range, user_id)
    - **`logs`:** System logs (metadata: level, service, error_code, timestamp)
    - **`documents`:** ADRs, requirements, design docs (metadata: doc_type, file_path, last_modified)
    - **`projects`:** Code repositories (metadata: repo_name, file_path, language, last_commit)
4.  Each collection uses the same M2-BERT 32K embedding model but different metadata schemas optimized for their search patterns.

**See ADR-039** for detailed implementation: CET-driven semantic chunking, K80 hardware allocation, Qdrant configuration, and retrieval pipeline.

## Consequences

*   **Positive:** The path to implementing a powerful, efficient, and architecturally simple RAG system is now clear. `Henson`'s resource requirements will be low. Single model simplifies maintenance and operations.
*   **Negative:** We are foregoing the potential for minor, specialized performance gains in the short-text collections (persona_rules, logs), a trade-off deemed acceptable in exchange for significantly reduced complexity.
*   **Neutral:** The performance of this model across all five collections should be monitored. If it proves to be a bottleneck or insufficiently accurate in the future, this decision can be revisited, but the initial implementation will be greatly simplified by this unified approach.

## Related Decisions

- **ADR-039:** RAG Embedding Strategy with CET-Driven Semantic Chunking - Detailed implementation of this decision
- **ADR-038:** CET Model Selection and Hardware Configuration - CET provides semantic chunking for conversations collection
- **ADR-015:** Joshua GPU Compute Cluster - K80 hardware allocation for embedding workload
