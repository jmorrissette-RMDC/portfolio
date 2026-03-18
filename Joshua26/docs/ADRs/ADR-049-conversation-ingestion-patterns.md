# ADR-049: Conversation Ingestion and Storage Architecture

Status: Updated - Rogers Migration
Date: 2026-01-11 (Original), 2026-01-29 (Updated)
Deciders: System Architect
Related: ADR-026 (Unified Embedding Model), ADR-039 (Radical Simplification), ADR-046 (Graceful Degradation)

## Context

Conversations from multiple sources (CLIs, agents, frameworks) need unified storage and retrieval. Requirements:
- Semantic search across all conversations
- Complex queries (SQL filters + vector search)
- Analytics and reporting
- Reliable ingestion pipeline
- Scale to handle concurrent agents
- Knowledge graph memory (Mem0)

---

## Historical Pattern (Deprecated - Pending Rogers Completion)

**Note:** This pattern is being replaced by the Rogers-based pattern below. The old system will be deprecated once Rogers Step 9 (Cutover) completes.

**Storage Architecture (Old):**
- Conversations → Codd (Postgres+pgvector)
- Files/Documents → Qdrant (high-volume semantic search)
- Separation by data characteristics

**Ingestion Pipeline (Old):**
- All sources → Redis queue (henson:embed)
- Henson GPU workers consume queue
- Workers embed with m2-bert and route to Codd
- FIFO processing with automatic load balancing

**Worker Architecture (Old):**
- GPU pooling: 2 workers (one per Tesla P4)
- Pull from shared Redis queue (BRPOP)
- Independent processes with dedicated GPUs
- Automatic load balancing via queue

**Legacy File Watchers:**
- Kept for backward compatibility with bare metal CLIs
- Gradually migrating to Redis queue
- Eventually deprecate in favor of unified queue

**Issues with old pattern:**
- Codd database corruption (TOAST index)
- Fragmented architecture (Henson, Codd, conversation-watcher)
- No knowledge graph memory (Mem0)
- Token-aware memory system not supported

---

## Current Pattern (Rogers-based)

**Storage Architecture (New):**
- Conversations → Rogers-Postgres (pgvector for messages, context windows, summaries, embeddings)
- Knowledge Graph → Rogers-Neo4j (Mem0 entity relationships)
- Files/Documents → Qdrant (unchanged - high-volume semantic search)

**Ingestion Approaches:**

**Preferred - Direct Rogers Integration:**
- Components conducting conversations write directly to Rogers via MCP tools
- Pattern: Call Rogers MCP tool `conv_store_message` directly from the component
- Eliminates file-based intermediary overhead
- Immediate feedback and error handling
- Example: CLI containers, agent frameworks call Rogers MCP directly

**Legacy - File-based Watcher:**
- Components write JSON files to watched directory
- conversation-watcher detects files and calls Rogers-MCP API (`conv_store_message`)
- Available for systems that cannot integrate directly
- Pattern: Write to `/storage/conversations/incoming/` for watcher pickup

**Ingestion Pipeline (New):**
- **Direct:** Component → Rogers-MCP API (`conv_store_message`)
- **Legacy:** Component → File → conversation-watcher → Rogers-MCP API (`conv_store_message`)
- Rogers-MCP → Rogers-LangGraph (async processing)
- Rogers-LangGraph → Hamilton (embeddings), Sutherland (LLM), Rogers-Postgres (storage), Rogers-Neo4j (Mem0)

**Processing Flow (New):**
```
conversation-watcher detects new message
    ↓
Calls Rogers-MCP conv_store_message (direct API call, not Redis queue)
    ↓
Rogers-LangGraph processes asynchronously:
    1. Dedup check (skip duplicate consecutive messages from same sender)
    2. Store message in Rogers-Postgres
    3. Generate embedding (call Hamilton via peer proxy)
    4. After embedding, queue in parallel:
        a. Context assembly — check all context windows, summarize if threshold crossed
        b. Memory extraction — Mem0 m.add() → Neo4j entity graph
    ↓
Done
```

**MAD Group (Bounded Context):**
Rogers is a MAD group (per ADR-046) with internal hard dependencies:
- **Private network:** rogers-private-net
- **Public network:** joshua-net
- **Components:** rogers-mcp, rogers-langgraph, rogers-postgres, rogers-neo4j, rogers-redis
- **Internal dependencies:** Hard dependencies acceptable (graceful recovery with retry/backoff)
- **External dependencies:** Graceful degradation (Hamilton, Sutherland via joshua-net)

**Key Differences from Historical Pattern:**
1. **Direct API calls** instead of Redis queue for ingestion
2. **Bounded context** (MAD group) instead of loosely-coupled services
3. **Mem0 knowledge graph** via Neo4j for entity relationships
4. **Token-aware memory system** with summarization and context retrieval
5. **LangGraph processing** instead of worker pool pattern
6. **Hamilton** (pure embedding service) instead of Henson (multi-function)

## Rationale

### Historical Pattern Rationale

**Postgres+pgvector for conversations:**
- Conversations are relational (users, projects, sessions)
- Need SQL queries and analytics
- Hybrid search (SQL filters + vector similarity)
- ACID transactions
- One system simpler than two

**Redis queue:**
- Decouples producers from consumers
- Handles bursts naturally
- Reliable delivery (AOF persistence)
- Auto-balancing across workers
- Industry standard pattern

**GPU pooling:**
- 2x throughput with dual GPUs
- Workers self-balance via queue
- Fault tolerance (one worker can handle load)
- Scales linearly with GPU count

**Qdrant for files:**
- Pure semantic search use case
- High volume (millions of chunks)
- Specialized vector operations
- Keep what works well

### Rogers Pattern Rationale

**Direct API calls (not Redis queue):**
- Simpler architecture (fewer moving parts)
- Immediate feedback (synchronous MCP tool calls)
- LangGraph handles async processing internally
- No queue management overhead
- Clearer error handling

**Bounded Context (MAD Group):**
- Conversations are a cohesive domain
- Internal components tightly coupled by design
- Simplifies development and testing
- Clear boundary via rogers-mcp API
- Graceful degradation for external dependencies only

**Mem0 + Neo4j:**
- Knowledge graph captures entity relationships
- Complements vector similarity search
- Structured memory (triplets) + semantic search (pgvector)
- Multi-agent memory scoping (user_id, agent_id, run_id)

**Hamilton (pure embedding service):**
- Single responsibility (embeddings only)
- Can be called by any MAD via MCP
- No conversation-specific logic
- Cleaner separation of concerns

**Token-aware memory system:**
- Automatic summarization at threshold
- Context retrieval without full conversation replay
- Efficient token budget management
- Better LLM prompt construction

## Consequences

### Historical Pattern Consequences

**Positive:**
- Simplified architecture (one backend per data type)
- Hybrid queries native in Postgres
- Reliable async ingestion
- Better GPU utilization
- Natural backpressure handling
- Analytics queries performant

**Negative:**
- More complex than single backend
- Requires Redis infrastructure
- Multi-process worker management
- Need to maintain both storage backends

**Risks:**
- pgvector performance at scale (mitigated: benchmarking, 86K conversations well within limits)
- Queue backlog if workers slow (mitigated: monitoring, alerts, scaling)
- Worker crashes (mitigated: auto-restart, redundancy)

### Rogers Pattern Consequences

**Positive:**
- Unified bounded context (all conversation logic in one place)
- Knowledge graph memory (Mem0) with entity relationships
- Token-aware memory system (automatic summarization)
- Simpler ingestion (direct API calls, no queue management)
- Clearer architecture (MAD group with defined boundary)
- Fresh database (no corruption from old Codd)
- LangGraph processing (declarative flows, easier to understand)

**Negative:**
- More services to manage (rogers-mcp, rogers-langgraph, rogers-postgres, rogers-neo4j)
- Requires Neo4j infrastructure (additional database)
- MAD group has internal hard dependencies (graceful recovery required)

**Risks:**
- Neo4j performance at scale (mitigated: Mem0 proven architecture)
- LangGraph complexity (mitigated: clear flow definitions)
- MAD group startup ordering (mitigated: graceful recovery with retry/backoff per ADR-046)

## Migration

**Cutover:** When Rogers Step 9 (Cutover) completes:
1. conversation-watcher switches from Redis queue to Rogers-MCP API
2. Old pattern (Henson workers, Codd) deprecated
3. Historical data replayed through Rogers pipeline (embeddings regenerated, memories extracted)

**Timeline:** See `mads/rogers/docs/PLAN.md` for migration steps.

## Implementation

### Historical Pattern (Deprecated)
See:
- REQ-011 (Henson) - Worker implementation, routing logic
- REQ-008 (Rogers-Redis) - Queue contract and message schema
- REQ-010 (Codd) - Database schema and vector indexes

### Current Pattern (Rogers-based)
See:
- `mads/rogers/docs/REQ-rogers.md` - Delta requirements and full design
- `mads/rogers/docs/architecture.md` - Design rationale and history
- `mads/rogers/README.md` - Quick reference (containers, tools, architecture)
