# Rogers Conversation Service — Architecture

**Version:** 1.0 **Date:** 2026-01-29 **Status:** Draft

**Related Documents:**

-   HLD-token-aware-memory-system.md (docs/designs/)
-   HLD-grace-langflow-integration.md (docs/designs/)
-   Conversation-Ecosystem-Rework-Project-Plan.md (project plan and migration execution)

***

## Executive Summary

Rogers is a unified conversation management service that consolidates fragmented conversation storage, embedding, and memory functionality into a cohesive bounded context. It replaces the current setup (Henson workers, Codd, conversation-watcher) with a clean architecture following the State 1 composition model.

**Why Rogers?**

1.  Postgres database corruption (TOAST index) requires fresh database
2.  Token-aware memory system requires new schema (per HLD-token-aware-memory-system.md)
3.  Mem0 knowledge graph memory functionality needed
4.  Current architecture is fragmented and difficult to maintain

***

## MAD Group: Bounded Context Model

Rogers is a **MAD group** (per ADR-046) — a collection of tightly-coupled containers sharing a private network with hard dependencies acceptable within the group.

**Within rogers-private-net (internal MAD group):**

-   Hard dependencies acceptable
-   Graceful recovery required (retry with exponential backoff)
-   Example: rogers-langgraph requires rogers-postgres, rogers-neo4j

**External to MAD group (via joshua-net):**

-   Graceful degradation required
-   Example: Sutherland unavailable → Rogers queries still work, Mem0 processing queued

***

## Network Architecture

Rogers operates across two network boundaries:

```
joshua-net (overlay, all MADs)
    ↓
Rogers (public MCP interface - bridges both networks)
    ↓
rogers-private-net (internal Rogers ecosystem)
    ↓
rogers-langgraph, rogers-postgres, rogers-neo4j, rogers-redis
    ↓ (via joshua-net MCP)
Hamilton, Sutherland (external MADs)
```

**joshua-net:** Overlay network connecting all MADs across hosts (irina, m5) **rogers-private-net:** Internal network for Rogers components only

**Boundary:** Rogers is attached to both networks:

-   joshua-net: Exposes MCP tools to Sam and other MADs
-   rogers-private-net: Accesses internal Rogers infrastructure.

***

## Component Overview

### GPU-Bound Services (Hardware-Specific)

These are standalone MADs tied to specific GPU hardware, accessed via MCP by any service:

| Service        | Host  | Hardware      | Role                                |
|----------------|-------|---------------|-------------------------------------|
| **Sutherland** | m5    | V100 + 3x P40 | LLM inference (OpenAI-compatible)   |
| **Hamilton**   | irina | Tesla P4      | Embedding service (replaces Henson) |

**Hamilton** is a new/renamed service that provides embedding-as-a-service:

-   Runs `m2-bert-80M-32k-retrieval` on Tesla P4
-   Exposes MCP tools: `embed_text`, `embed_texts`, `embed_and_store`
-   Any MAD can call it for embeddings
-   Strips out Qdrant, conversation logic (that moves to Rogers)

### Rogers Ecosystem (Distributed)

```
┌─────────────────────────────────────────────────────────────────┐
│                    Rogers Service (Bounded Context)              │
│                                                                  │
│  ┌──────────────┐   ┌────────────────┐   ┌─────────────────┐   │
│  │ Rogers   │──▶│ Rogers-LangGraph│──▶│ Rogers-Postgres │   │
│  │ (API Gateway)│   │ (Processing)    │   │ (conversations) │   │
│  └──────────────┘   └────────────────┘   └─────────────────┘   │
│         │                   │                   │               │
│  ┌──────┴───────┐          │           ┌───────▼───────┐       │
│  │ Rogers-Redis │          │           │ Rogers-Neo4j  │       │
│  │ (Cache+Queue)│          │           │ (Mem0 graphs) │       │
│  └──────────────┘          │           └───────────────┘       │
│                            │                                    │
└────────────────────────────┼────────────────────────────────────┘
                             │
              ┌──────────────┴──────────────┐
              │                             │
       ┌──────▼──────┐              ┌───────▼──────┐
       │ Sutherland  │              │  Hamilton    │
       │ (m5 - LLMs) │              │ (irina - Emb)│
       └─────────────┘              └──────────────┘
```

### Components

| Container            | Role                                    | Host | Reason                                                                            |
|----------------------|-----------------------------------------|------|-----------------------------------------------------------------------------------|
| **rogers**           | MCP gateway (public API)                | M5   | Exposes conv_\* and mem_\* tools to clients                                       |
| **rogers-langgraph** | Processing engine & orchestration       | M5   | Handles async workflows, Mem0 integration, orchestrates Hamilton/Sutherland calls |
| **rogers-postgres**  | Conversation storage (turns, summaries) | M5   | ZFS storage, co-located with embedding GPU                                        |
| **rogers-neo4j**     | Knowledge graph for Mem0                | M5   | Graph memory storage                                                              |
| **rogers-redis**     | Hot cache + ingestion queue             | m5   | Large RAM (\~256GB) for cache                                                     |

**Note on orchestration:** There is no separate "composition root" container. The `rogers` container is a thin MCP gateway that exposes tools and delegates to `rogers-langgraph` for processing. `rogers-langgraph` handles all workflow orchestration using LangGraph (ingest → embed → store → summarize → extract memories).

Note: Mem0's vector store uses rogers-postgres (pgvector) — no separate Qdrant needed.

### External Dependencies (via overlay network)

-   **Hamilton** (irina:6335) — Embeddings via MCP
-   **Sutherland** (m5:11435) — LLM for summarization + memory extraction

***

## Mem0 Integration

Mem0 is a knowledge graph memory system that learns user preferences, facts, and context from conversations.

**Architecture:**

-   `rogers-neo4j` — Neo4j graph database for Mem0's knowledge graph storage
-   `rogers-postgres` — pgvector for both conversation embeddings AND Mem0's vector store (same instance, Mem0 creates its own tables)
-   Mem0 Python library integrated into `rogers-langgraph` for memory operations
-   Uses Hamilton for embeddings, Sutherland for LLM extraction

**Why Neo4j (not just pgvector for everything):**

Mem0 uses a hybrid approach:

-   **pgvector** — Semantic similarity search ("find memories related to this query")
-   **Neo4j** — Entity relationships as triplets: `(entity1, relationship, entity2)`

The graph captures structured relationships that vector similarity misses:

-   `(alice, prefers, coffee)` + `(alice, intolerant_of, dairy)` → related facts about alice
-   `(starret, requested, schema_change)` + `(schema_change, affects, users_table)` → trace of actions

Graph traversal finds connected entities even when the text isn't semantically similar.

**Future Enhancement (Not in Mem0):** Edge scoring with positive/negative weights (e.g., "this document is relevant but harmful for uid X") is a potential RL-based extension, not part of Mem0's current capabilities. This would require custom work on top of Mem0.

**Memory Scoping (Critical for Multi-Agent System):**

Mem0 scopes memories using three identifiers:

-   `user_id` — The actor initiating the conversation (human OR agent — anyone with a UID)
-   `agent_id` — The agent receiving/handling the conversation
-   `run_id` — The specific session/conversation

In Joshua26's architecture, both humans and MADs have OS user accounts with UIDs:

-   `user_id` = whoever is talking (could be a human, could be Starret calling Codd)
-   `agent_id` = the MAD being talked to
-   `run_id` = session_id

**Examples:**

```python
# Human "alice" (uid 1000) talking to food assistant
m.add("I'm lactose intolerant", user_id="alice", agent_id="food-assistant", run_id="session-123")

# Starret (uid 2006) talking to Codd (uid 2003)
m.add("Need schema for users table", user_id="starret", agent_id="codd", run_id="git-op-456")

# Cross-agent memories (shared facts about alice, accessible to all agents)
m.search("dietary restrictions", user_id="alice")  # finds lactose intolerance regardless of agent
```

***

## Database Schema

Rogers-Postgres stores all conversation data with pgvector embeddings for semantic search.

### Tables

#### conversation_sessions

```sql
CREATE TABLE conversation_sessions (
    id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255),
    context_id VARCHAR(255),
    flow_id VARCHAR(255),                      -- Links conversation to Langflow flow (for Grace UI)
    flow_name VARCHAR(255),                    -- Display name for UI
    interface_name VARCHAR(100) DEFAULT 'grace', -- Which UI was used
    max_token_limit INTEGER DEFAULT 100000,
    trigger_threshold_percent FLOAT DEFAULT 0.75,
    recent_window_percent FLOAT DEFAULT 0.20,
    summary_target_percent FLOAT DEFAULT 0.05,
    total_turns INTEGER DEFAULT 0,
    estimated_token_count INTEGER DEFAULT 0,
    last_summarized_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

#### conversation_turns

```sql
CREATE TABLE conversation_turns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id VARCHAR(255) NOT NULL REFERENCES conversation_sessions(id),
    user_message TEXT NOT NULL,
    user_sender_name VARCHAR(100) DEFAULT 'User',
    ai_message TEXT NOT NULL,
    ai_sender_name VARCHAR(100) DEFAULT 'AI',
    token_count INTEGER,
    model_name VARCHAR(100),
    user_embedding vector(768),
    ai_embedding vector(768),
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### conversation_summaries

```sql
CREATE TABLE conversation_summaries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id VARCHAR(255) NOT NULL REFERENCES conversation_sessions(id),
    summary_text TEXT NOT NULL,
    summary_embedding vector(768),
    summarizes_from_turn_id UUID REFERENCES conversation_turns(id),
    summarizes_to_turn_id UUID REFERENCES conversation_turns(id),
    message_count INTEGER,
    original_token_count INTEGER,
    summary_token_count INTEGER,
    summarized_by_model VARCHAR(100),
    summarized_at TIMESTAMP DEFAULT NOW(),
    superseded_by UUID REFERENCES conversation_summaries(id),
    is_active BOOLEAN DEFAULT true
);
```

### Indexes

```sql
CREATE INDEX idx_turns_session ON conversation_turns(session_id);
CREATE INDEX idx_turns_created ON conversation_turns(created_at);
CREATE INDEX idx_turns_user_emb ON conversation_turns USING ivfflat (user_embedding vector_cosine_ops);
CREATE INDEX idx_turns_ai_emb ON conversation_turns USING ivfflat (ai_embedding vector_cosine_ops);
CREATE INDEX idx_summaries_session ON conversation_summaries(session_id, is_active);
CREATE INDEX idx_summaries_emb ON conversation_summaries USING ivfflat (summary_embedding vector_cosine_ops);

-- Grace UI indexes
CREATE INDEX idx_sessions_flow ON conversation_sessions(flow_id);
CREATE INDEX idx_sessions_flow_user ON conversation_sessions(user_id, flow_id, updated_at DESC);
```

**Note:** Memories are stored in Neo4j via Mem0, not Postgres. Neo4j provides the knowledge graph for entity relationships.

***

## MCP Tools (Rogers)

Rogers exposes conversation and memory tools using the `conv_` and `mem_` prefixes.

### Conversation Management

-   `conv_store_turn` - Store user+AI turn, trigger summarization if needed
-   `conv_retrieve_context` - Get summary + recent turns (fast, no LLM)
-   `conv_get_session_config` - Get/create session with token budgets
-   `conv_store_summary` - Store summary, mark previous inactive
-   `conv_get_turns_to_summarize` - Get old turns that need summarization

### Grace UI Support

-   `conv_list_sessions` - List sessions for a flow (populates sidebar)
    -   Input: flow_id, user_id (optional), limit, offset
    -   Output: session metadata array (id, flow_id, created_at, updated_at, total_turns, first_user_message)
-   `conv_get_history` - Get full conversation for display
    -   Input: session_id, include_summary (bool)
    -   Output: session metadata + summary + all turns in chronological order
-   `conv_create_session` - Initialize new session from UI
    -   Input: session_id, flow_id, user_id, flow_name, interface_name, max_token_limit
    -   Output: session_id, created_at, config

### Memory (Mem0 via Neo4j)

-   `mem_add` - Add a memory to the knowledge graph
-   `mem_search` - Search memories (semantic + graph traversal)
-   `mem_list` - List memories for a user
-   `mem_delete` - Remove a memory from the graph
-   `mem_get_context` - Get relevant memories for prompt injection (graph-aware)
-   `mem_extract` - Extract memories from conversation via LLM, store in graph

These tools wrap the Mem0 Python library, which uses Neo4j for graph storage.

***

## Processing Pipeline (Rogers-LangGraph)

LangGraph flow for async processing:

```
Ingest Turn
    ↓
Generate Embeddings (call Hamilton)
    ↓
Store in Postgres
    ↓
Check Token Threshold
    ↓ (if over threshold)
Generate Summary (call Sutherland)
    ↓
Store Summary
    ↓
Extract Memories (call Sutherland LLM)
    ↓
Store in Mem0 Graph (Neo4j)
    ↓
Done
```

***

## Tool Naming Convention

Rogers uses the `conv_` **prefix** for all conversation domain tools (per ADR-045).

**Rationale:**

-   Service-level tools: `pg_*` (Codd), `redis_*` (Rogers-Redis) — generic operations
-   Domain-level tools: `conv_*` (Rogers) — conversation-specific operations
-   Rogers exposes high-level `conv_*` tools that abstract backend implementation (Postgres, Neo4j)

**Examples:**

-   `conv_store_turn` — Store user+AI conversation turn
-   `conv_retrieve_context` — Get summary + recent turns
-   `conv_get_session_config` — Get/create session with token budgets
-   `mem_add`, `mem_search`, `mem_list` — Mem0 knowledge graph operations (keep `mem_` prefix)

***

## mad-core Library Usage

**Rogers (MCP Gateway)** uses **mad-core-js** (Node.js runtime) per ADR-042. Only the containers with the MCP gateway use the core library. No sub container under the MCP container uses it.

**Rationale:**

-   MCP is natively Node.js (Anthropic SDK)
-   mad-core-js provides:
    -   Standardized health checks (`/health` endpoint)
    -   Automatic request logging (per ADR-047)
    -   MCP server infrastructure (`/mcp` endpoint)

**Rogers-LangGraph (Processing Engine)** does NOT use mad-core.

**Rationale:**

-   Not an MCP server (internal processing engine)
-   No MCP tools to expose (rogers exposes all MCP tools)
-   Orchestrates workflows using LangGraph
-   Handles Mem0 integration and asynchronous processing

***

## High-Level Data Flow

```
Conversation Turn Ingestion:
    conversation-watcher detects new turn
        ↓
    Calls Rogers conv_store_turn
        ↓
    Rogers-LangGraph processes asynchronously:
        ↓
    1. Generate embeddings (call Hamilton)
    2. Store turn in rogers-postgres
    3. Check token threshold
    4. If over threshold:
        a. Generate summary (call Sutherland)
        b. Store summary
        c. Extract memories (call Sutherland LLM)
        d. Store in Mem0 graph (Neo4j)
        ↓
    Done
```

**Context Retrieval:**

```
UI/Client requests conversation context
    ↓
Calls Rogers conv_retrieve_context(session_id)
    ↓
Rogers queries rogers-postgres:
    - Active summary (if exists)
    - Recent turns (last N% of token budget)
    ↓
Returns formatted context (no LLM call - fast)
```

**Memory Context Injection:**

```
UI/Client requests relevant memories
    ↓
Calls Rogers mem_get_context(user_id, query)
    ↓
Rogers-LangGraph:
    - Semantic search via pgvector
    - Graph traversal via Neo4j
    - Combine results
    ↓
Returns relevant memories for prompt injection
```

***

## Graceful Degradation Strategy

Per ADR-046 (MAD Groups / Bounded Context):

**Within rogers-private-net (MAD group):**

-   Hard dependencies acceptable
-   Graceful **recovery** required:
    -   Retry connections with exponential backoff
    -   Containers start successfully even if dependencies not ready
    -   System recovers automatically when dependencies return
    -   Health status reporting (waiting/connected/error)

**External dependencies (via joshua-net):**

-   Graceful **degradation** required:
    -   Example: Sutherland unavailable → Rogers queries still work
    -   Mem0 processing stalls, queue accumulates, resumes when Sutherland returns
    -   Hamilton unavailable → New embeddings fail, but conversation storage continues

***

## Downstream Consumers

### Grace UI

Grace is the web chat interface that consumes Rogers for conversation storage. See `docs/designs/HLD-grace-langflow-integration.md`.

**Grace requires from Rogers:**

-   `conv_list_sessions(flow_id)` — Populate sidebar
-   `conv_get_history(session_id)` — Load full conversation
-   `conv_create_session(session_id, flow_id, user_id)` — New conversation button
-   `mem_get_context(user_id, query)` — Get relevant Mem0 memories for prompt injection

**Schema requirement:** `flow_id` field in conversation_sessions (included in schema).

**Deployment order:** Rogers must be deployed and verified before Grace can connect.

There are many consumers possible within the network. Grace is just one of them. Joshua (LangFlow) is a critical user. Any MAD that requires access to conversational history or engages in conversation (which should always be recorded) uses Rogers.

***

## Decisions Made

1.  **Henson → Hamilton** — Henson is deprecated entirely. Hamilton is a new pure embedding service on irina.
2.  **Codd** — Deprecated after data recovery. Rogers-Postgres takes over.
3.  **Data** — Attempt recovery from corrupted DB before fresh start. Replay through pipeline (not direct DB import) to regenerate embeddings and extract memories.
4.  **Host** — Rogers on M5
5.  **Mem0** — Use real Mem0 library with Neo4j for knowledge graphs (not pgvector alone). Graph relationships capture entity connections that vector similarity misses.
6.  **Grace integration** — Rogers provides all conversation tools Grace needs. Grace HLD updated to reference Rogers.
7.  **Tool naming** — Use `conv_` prefix for conversation domain tools (per ADR-045).
8.  **mad-core runtime** — rogers uses mad-core-js (MCP is natively Node.js); rogers-langgraph uses mad-core-py.
9.  **Network architecture** — Two-network boundary: joshua-net (public) and rogers-private-net (internal MAD group).
10. **Graceful degradation** — Bounded context model: hard dependencies within MAD group acceptable, external dependencies require degradation.

***

## ADR Compliance

This architecture document aligns with the following ADRs:

| ADR     | Title                          | Compliance Status                                          |
|---------|--------------------------------|------------------------------------------------------------|
| ADR-037 | Local Package Caching          | Compliant (see REQ docs)                                   |
| ADR-039 | Radical Simplification         | Compliant (two-volume mounting, storage organization)      |
| ADR-040 | MCP Relay Architecture         | Compliant (HTTP/SSE transport via mad-core)                |
| ADR-042 | Shared MAD Core Library        | Compliant (mad-core-js for MCP, mad-core-py for LangGraph) |
| ADR-043 | Centralized Identity           | Compliant (UID 2002, GID 2000, lsyncd)                     |
| ADR-044 | Unified Credentials Management | Compliant (see REQ docs)                                   |
| ADR-045 | MAD Template Standard          | Compliant (tool naming, HEALTHCHECK, non-root user)        |
| ADR-046 | Graceful Degradation           | Compliant (MAD group bounded context model)                |
| ADR-047 | MCP Request Logging            | Compliant (mad-core auto-logging)                          |
| ADR-049 | Conversation Ingestion         | Updated (Rogers-based pattern)                             |

***

## Registry Entries

### Rogers

```yaml
rogers:
  uid: 2002
  gid: 2000
  ports:
    mcp: 6380
    postgres: 5432
    neo4j_bolt: 7687
    neo4j_http: 7474
  host: M5
  description: Unified conversation + memory service (with Mem0)
  mcp_endpoints:
    health: /health
    stream: /mcp
```

### Hamilton

```yaml
hamilton:
  uid: 2005        # Inherited from henson
  gid: 2000
  ports:
    mcp: 6335      # New port (henson was 6334)
  host: irina
  hardware: Tesla P4
  description: Pure embedding service (m2-bert-80M-32k-retrieval)
  mcp_endpoints:
    health: /health
    stream: /mcp
  tools:
    - embed_text
    - embed_texts
```

***

**Document Status:** v1.0 - Finalized **Next Steps:** See Conversation-Ecosystem-Rework-Project-Plan.md for project phases and migration execution
