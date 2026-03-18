# ADR-039: RAG Embedding Strategy with CET-Driven Semantic Chunking

**Status:** Accepted
**Date:** 2025-12-22

---

## 📝 Henson MAD Implementation

This ADR provides the detailed technical implementation for **Henson's** RAG system as defined in **ADR-026: Henson's Unified Embedding Model for RAG**. Henson is the Context Engineer MAD responsible for providing retrieval-augmented generation capabilities across the Joshua ecosystem.

---

## Context

The Henson MAD requires a Retrieval-Augmented Generation (RAG) implementation for searching across multiple data sources. Key requirements:

1. **Long Conversation Storage:** Claude sessions and other conversations can exceed 2M tokens across hundreds or thousands of messages
2. **Semantic Retrieval:** Find relevant conversation segments based on meaning, not just keywords
3. **Hybrid Search:** Support both semantic similarity and exact keyword matching (error codes, IDs, technical terms)
4. **Context Preservation:** Retrieve coherent conversation sections, not fragmented sentence snippets
5. **Intelligent Chunking:** Split conversations at logical boundaries (topic shifts, task completion) rather than arbitrary token counts
6. **Streaming Ingestion:** Handle continuous conversation growth with incremental embedding updates

The challenge: Arbitrary token-based chunking fragments conversations and loses context. We need semantic awareness to identify natural breakpoints.

## Decision

### Embedding Model: M2-BERT 80M 2K (32K variant)

We will use **M2-BERT 32K** (80M parameters, 32,768 token context) as the primary embedding model:

1. **Long Context:** 32K token window captures entire conversation sections without chunking
   - Most conversations: 500-1500 tokens per logical section
   - Long troubleshooting sessions: Up to 25K tokens preserved intact
   - Eliminates information loss from mid-conversation splits

2. **Retrieval-Optimized:** Specifically trained for dense retrieval and passage ranking (not general sentence similarity)
   - Better RAG performance than sentence-transformers models
   - Multi-scale architecture captures both token-level and document-level semantics

3. **Output Dimensions:** 768-dimensional embeddings (standard for modern retrieval)

4. **Performance:** ~800-1200 docs/sec on K80 with batching (sufficient for streaming ingestion)

**Alternative considered:** M2-BERT 2K (faster at ~1500 docs/sec) - rejected because 2K context requires chunking most conversations, losing coherence

### Vector Database: Qdrant (Local Deployment)

Henson will use **Qdrant** running locally on filesystem storage:

1. **Hybrid Search:** Native support for combining dense vector search with sparse BM25 keyword search
   - Semantic: "What were the GPU performance issues?"
   - Keyword: "Error code CUDA_OUT_OF_MEMORY"
   - Combined: Best of both worlds

2. **Local Storage:** Data persists to configurable directory (e.g., `/mnt/irina_storage/qdrant_data/`)
   - No cloud dependencies
   - Data privacy
   - Low latency (local disk access)

3. **Rich Metadata Filtering:** Supports complex queries with filters (metadata varies by collection)

4. **Concurrent Writes:** Handles multiple embedding instances writing simultaneously

5. **Collection Structure:**

   Henson manages five distinct Qdrant collections (see ADR-026):

   - **`persona_rules`:** MAD behavior instructions
     - Metadata: mad_id, rule_type, priority
     - Search pattern: "What are Fiedler's orchestration rules?"

   - **`conversations`:** Claude sessions (past and current)
     - Metadata: conversation_id, timestamp, message_range, user_id, chunk_number, breakpoint_reason
     - Search pattern: "What did we decide about GPU allocation last week?"

   - **`logs`:** System error logs and debug sessions
     - Metadata: level (ERROR/WARN/INFO), service, error_code, timestamp
     - Search pattern: "Show me all CUDA errors from yesterday"

   - **`documents`:** ADRs, requirements, design docs
     - Metadata: doc_type (adr/requirement/design), file_path, last_modified
     - Search pattern: "What ADRs mention Fiedler?"

   - **`projects`:** Code repositories from `/mnt/projects`
     - Metadata: repo_name, file_path, language, last_commit, git_branch
     - Search pattern: "Find all Python files that use joshua_network"

   All collections use 768-dimensional M2-BERT 32K embeddings with collection-specific metadata schemas.

### Hardware Allocation

**K80 (24GB dual GPU):** Primary embedding workload
- Advantages:
  - 24GB VRAM supports large batch sizes (8-16 conversations at 32K tokens)
  - Dual GPU architecture allows parallel processing or model+LLM separation
  - Sufficient memory for M2-BERT 32K + working batches
- Configuration:
  - GPU 0: M2-BERT 32K instance (~500MB model + ~18GB batching headroom)
  - GPU 1: Available for second embedding instance or small RAG LLM

**P4 (8GB):** Backup/parallel embedding (excluded from primary allocation per user direction)

**P1000 (4GB):** Video output only (insufficient VRAM for 32K context batching)

### CET-Driven Semantic Chunking

**Problem:** Arbitrary 32K token chunking splits conversations mid-topic, losing context and reducing retrieval quality.

**Solution:** Use the Context Engineering Transformer (CET - Mistral Small 24B, see ADR-038) to identify logical breakpoints:

#### Chunking Workflow

1. **CET Analysis Phase:**
   - Input: Full conversation (up to 80K tokens, expanding to 128K)
   - CET identifies natural breakpoints:
     - Topic shifts (user changes subject)
     - Task completion ("Problem solved", "That works")
     - Time gaps (>30 minutes between messages)
     - Explicit transitions ("Let's move on to...", "New question:")
   - Output: List of message IDs for chunk boundaries

2. **Chunk Assembly:**
   - Split conversation at CET-identified breakpoints
   - Target 20K-25K tokens per chunk (soft limit)
   - Hard limit: 32K tokens (never exceed M2-BERT capacity)
   - Overlap: 10-20% between chunks to preserve context continuity

3. **Embedding Phase:**
   - M2-BERT embeds each semantic chunk
   - Store in Qdrant with metadata:
     ```
     {
       conversation_id: "conv_12345",
       chunk_number: 2,
       message_range: "151-300",
       breakpoint_reason: "topic_shift",
       token_count: 24500,
       vector: [0.234, -0.567, ...],
       text: "full 24.5K token chunk"
     }
     ```

4. **Active Chunk Management:**
   - Track last embedded message ID per conversation
   - Debounce: Re-embed active chunk only when:
     - New content exceeds 5K tokens, OR
     - User performs search (lazy update), OR
     - Conversation closes/pauses
   - Completed chunks: Never re-embed (immutable)

#### CET Semantic Chunking Advantages

1. **Coherent Retrieval:** Each chunk is a complete discussion thread, not a fragment
2. **Better Precision:** "What was the GPU discussion outcome?" retrieves the full resolution, not mid-conversation snippets
3. **Context Preservation:** Related multi-turn exchanges stay together
4. **Efficient Storage:** Fewer, larger semantic chunks vs many small fragments
5. **Improved RAG Quality:** LLM receives coherent context sections, not disjointed sentences

### Retrieval Pipeline

**Indexing:**
```
New conversation message → Accumulate in active chunk →
CET detects breakpoint OR 5K new tokens →
M2-BERT 32K embeds chunk (K80) →
Qdrant stores vector + full text + metadata
```

**Querying:**
```
User question → M2-BERT 32K embeds query (same model!) →
Qdrant hybrid search (semantic + keyword) →
Returns top 5 chunks (up to 160K tokens) →
Send to downstream LLM with original question
```

### Storage Schema

**Qdrant Collections Detail:**

All collections managed by Henson share common vector properties but have collection-specific metadata:

**Common to all collections:**
- Vectors: 768 dimensions (M2-BERT 32K output)
- Sparse vectors: BM25 keyword index (hybrid search)
- Payload field: `text` (full embedded content, up to 32K tokens)

**Collection-specific metadata:**

**`conversations`:**
- `conversation_id`, `chunk_number`, `message_range`
- `breakpoint_reason`: "topic_shift" | "task_complete" | "time_gap" | "hard_limit"
- `token_count`, `timestamp_start`, `timestamp_end`
- `user_id`, `tags[]`, `last_embedded_message_id`

**`logs`:**
- `level` (ERROR/WARN/INFO), `service`, `error_code`
- `timestamp`, `host`, `container_id`

**`documents`:**
- `doc_type` (adr/requirement/design), `file_path`, `last_modified`
- `version`, `status` (proposed/accepted/superseded)

**`projects`:**
- `repo_name`, `file_path`, `language`, `last_commit`
- `git_branch`, `file_size`, `line_count`

**`persona_rules`:**
- `mad_id`, `rule_type`, `priority`
- `version`, `last_updated`

## Consequences

### Positive

1. **Full Context Retrieval:** 32K embeddings preserve entire conversation sections, eliminating information loss from chunking
2. **Semantic Chunking:** CET-driven breakpoints maintain topic coherence, dramatically improving retrieval relevance
3. **Hybrid Search:** Qdrant combines semantic understanding with exact keyword matching for technical terms
4. **Scalable Ingestion:** K80's 24GB VRAM supports batch processing of long conversations (8-16 at once)
5. **Local Deployment:** No cloud costs, data privacy, low latency
6. **Multi-Model Synergy:** CET and M2-BERT work together - CET chunks intelligently, M2-BERT embeds efficiently
7. **Flexible Expansion:** Can run multiple M2-BERT instances across K80 dual GPU for parallel bulk indexing

### Negative

1. **Two-Model Dependency:** CET chunking requires 3x V100 cluster to be available; cannot operate independently
2. **Chunking Latency:** CET analysis adds ~5-10 seconds per 80K conversation before embedding can begin
3. **Complexity:** More moving parts than simple fixed-size chunking; requires coordination between CET and embedding pipeline
4. **K80 Speed:** Older architecture; embedding throughput (~800-1200/sec) slower than modern GPUs but adequate for streaming use case
5. **Storage Overhead:** Storing full 32K text chunks + vectors requires more disk space than compressed/summarized approaches

### Trade-offs

**Chosen:** Semantic chunking + 32K embeddings
**Alternative:** Fixed 2K chunks + faster embedding
**Justification:** Retrieval quality (coherent context) more valuable than ingestion speed for conversation/log search

### Implementation Notes

**Debouncing Active Chunks:**
- Track `last_embedded_token_count` in metadata
- Only re-embed when `current_count - last_embedded > 5000`
- Prevents excessive recomputation on every new message

**CET Chunking Heuristics:**
- Primary: Semantic analysis (topic shift detection)
- Secondary: Time gaps (>30 min between messages)
- Tertiary: Explicit phrases ("moving on", "new topic", "resolved")
- Hard limit: 32K tokens (never exceed M2-BERT capacity)
- Soft target: 20-25K tokens (allows CET to find nearby breakpoint)

**Overlap Strategy:**
- Last 10-20% of chunk N overlaps with first 10-20% of chunk N+1
- Prevents information loss at boundaries
- Slightly increases storage but dramatically improves retrieval

### Performance Characteristics

**Indexing Throughput:**
- CET chunking: ~80K conversation analyzed in 5-10 seconds
- M2-BERT embedding: ~800-1200 docs/sec (batched on K80)
- Qdrant ingestion: ~2000-5000 points/sec
- Bottleneck: M2-BERT embedding (acceptable for streaming use)

**Query Latency:**
- Embed query: ~50-100ms (single doc)
- Qdrant search: ~5-20ms (hybrid search)
- Total: <200ms for retrieval
- Downstream LLM processing: 2-5 seconds (separate concern)

### Related Decisions

- **ADR-026:** Henson's Unified Embedding Model for RAG - The decision this ADR implements
- **ADR-038:** CET Model Selection and Hardware Configuration - Provides chunking intelligence for conversations collection
- **ADR-015:** Joshua GPU Compute Cluster - K80 hardware allocation for M2-BERT embedding workload
- **ADR-035:** Direct Access AI Model Nodes - Inference integration pattern

## References

- M2-BERT: https://huggingface.co/microsoft/m2-bert-80m-32k
- Qdrant: https://qdrant.tech/
- Context Engineering: Emerging discipline for optimizing LLM information environments
- Semantic Chunking: Superior to fixed-size chunking for RAG quality (2025 best practice)
