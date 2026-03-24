# REQ: Rogers Conversation and Context Management Service

**Document ID:** REQ-rogers
**Version:** 3.1
**Date:** 2026-02-25
**Status:** Draft
**Author:** Design Session (polished-baking-wigderson)

> **Delta REQ** — describes only what differs from the template baseline (`mads/_template/`). The template handles build system, runtime security, health checks, MCP wiring, logging, and container structure.

---

## 1. Purpose

Rogers is the unified conversation and context management service for the Joshua26 ecosystem. It provides:

- **Conversation storage** — Store and retrieve individual messages from any number of participants (human users, MADs, external tools via watchers)
- **Context engineering** — Per-participant context windows with configurable assembly strategies (build types). Each LLM participant in a conversation has its own context window with its own token budget. Rogers performs proactive context assembly — building optimized context in the background so it's ready when the LLM needs it
- **Three-tier context assembly** — Assemble context within a token budget using archival summaries (Tier 1), rolling chunk summaries (Tier 2), and recent messages verbatim (Tier 3). Build types define the strategy; the actual token limit is per-instance
- **Knowledge graph memory** — Extract and query memories via Mem0 (Neo4j + pgvector hybrid)

Rogers replaces the legacy fragmented stack: `conversation-watcher → rogers-redis → Henson → Codd`.

**Downstream consumers:**
- **Grace UI** — conversation sidebar (`conv_search`), conversation display (`conv_get_history`), conversation creation (`conv_create_conversation`), memory context injection (`mem_get_context`)
- **Claude Watchers** (`claude-watcher-irina`, `claude-watcher-m5`, `claude-watcher-hymie`) — store messages (`conv_store_message`), create conversations and context windows. Each watcher has a system UID and uses it as `sender_id` for the external LLM's messages it ingests
- **Langflow (Joshua MAD)** — context retrieval and memory access for active conversations
- **Any MAD** engaging in or needing access to conversation history

---

## 2. Registry Allocation

| Container | UID | GID | Port | Host | Network |
|---|---|---|---|---|---|
| rogers | 2002 | 2001 | 6380 | m5 | joshua-net + rogers-net |
| rogers-langgraph | 2002 | 2001 | 8000 (internal) | m5 | rogers-net |
| rogers-postgres | 2002 | 2001 | 5432 (internal) | m5 | rogers-net |
| rogers-neo4j | 2002 | 2001 | 7687, 7474 (internal) | m5 | rogers-net |
| rogers-redis | 2002 | 2001 | 6379 (internal) | m5 | rogers-net |

registry.yml carries the `rogers` gateway entry (uid 2002, gid 2001, port 6380, host m5). Sub-containers are defined in docker-compose, not the registry.

---

## 3. Containers

Rogers is a MAD group (per ADR-046) — 5 tightly-coupled containers on a private network.

| Container | Type | Base Image |
|---|---|---|
| rogers | MCP gateway (Node.js) | From `mads/_template/template/` |
| rogers-langgraph | LangGraph engine (Python) | From `mads/_template/template-langgraph/` |
| rogers-postgres | PostgreSQL + pgvector | `pgvector/pgvector:pg16` (Debian-based community image with pgvector pre-installed, digest-pinned). pgvector cannot be installed at runtime — this is the only supported distribution method. |
| rogers-neo4j | Neo4j | `neo4j:5@sha256:f95a1eac8a2e311b9aff78aae9b9793f265b464eb1b097cd2b1fb82c96de4ba3` (digest-pinned) |
| rogers-redis | Redis | `redis:7-alpine@sha256:02f2cc4882f8bf87c79a220ac958f58c700bdec0dfb9b9ea61b62fb0e8f1bfcf` (digest-pinned) |

**Network:** `rogers-net` (bridge, private). Gateway additionally on `joshua-net`.

**Docker labels** (required on all containers per HLD-MAD-container-composition.md §Design Principles):

| Container | `mad.logical_actor` | `mad.component` |
|---|---|---|
| rogers | rogers | mcp |
| rogers-langgraph | rogers | langgraph |
| rogers-postgres | rogers | postgres |
| rogers-neo4j | rogers | neo4j |
| rogers-redis | rogers | redis |

---

## 4. MCP Tools

All tools exposed by the `rogers` gateway. Routing target: `rogers-langgraph:8000`.

### 4.1 Conversation Tools (`conv_`) — Client-Facing

| Tool | Description | Flow Type |
|---|---|---|
| `conv_create_conversation` | Create a new conversation, returns `conversation_id` | AE |
| `conv_create_context_window` | Create a context window instance for a build type + token limit | AE |
| `conv_store_message` | Store a single message; triggers full pipeline (dedup → embed → context assembly + memory extraction) | AE |
| `conv_retrieve_context` | Get assembled three-tier context for a context window. Blocks if assembly in progress | AE |
| `conv_search` | General-purpose conversation search — semantic (query against message embeddings, grouped by conversation) + structured filters (flow_id, user_id, sender_id, external_session_id, date range). Serves browsing, topic search, and find-matching use cases | AE |
| `conv_search_messages` | Search within messages — semantic (embeddings) + structured filters | AE |
| `conv_get_history` | Get full message sequence for a conversation (display) | AE |
| `conv_search_context_windows` | Search/list/get context windows by ID, conversation, or build type | AE |

### 4.2 Memory Tools (`mem_`) — Client-Facing

| Tool | Description | Flow Type |
|---|---|---|
| `mem_search` | Semantic + graph search across extracted knowledge (mem0) | AE |
| `mem_get_context` | Get relevant memories formatted for prompt injection | AE |

### 4.3 Internal Tools (NOT exposed via MCP)

These exist as endpoints in `server.py` for the queue worker and internal flows. They are not advertised to external consumers.

| Tool | Purpose |
|---|---|
| `mem_add` | Triggered internally by the pipeline after embedding |
| `mem_extract` | Triggered internally — extracts memories from conversation |
| `mem_list` | Administrative/debugging |
| `mem_delete` | Administrative/debugging |

### 4.4 Tool Schemas

#### `conv_create_conversation`
```json
{
  "input": {
    "flow_id": { "type": "string", "required": true },
    "flow_name": { "type": "string" },
    "user_id": { "type": "string" },
    "title": { "type": "string" }
  },
  "output": {
    "conversation_id": { "type": "string" },
    "created_at": { "type": "string" }
  }
}
```

#### `conv_create_context_window`
```json
{
  "input": {
    "conversation_id": { "type": "string", "required": true },
    "build_type_id": { "type": "string", "required": true, "description": "e.g. 'small-basic', 'standard-tiered'" },
    "max_token_limit": { "type": "integer", "required": true, "description": "Token budget for this window" }
  },
  "output": {
    "context_window_id": { "type": "string" },
    "conversation_id": { "type": "string" },
    "build_type_id": { "type": "string" },
    "max_token_limit": { "type": "integer" },
    "created_at": { "type": "string" }
  }
}
```

#### `conv_store_message`
```json
{
  "input": {
    "context_window_id": { "type": "string", "description": "Runtime path — Rogers resolves conversation_id from it" },
    "conversation_id": { "type": "string", "description": "Direct path — for migration, background processes" },
    "role": { "type": "string", "required": true, "enum": ["user", "assistant", "system", "tool"] },
    "sender_id": { "type": "integer", "required": true, "description": "System UID of participant" },
    "content": { "type": ["string", "array"], "required": true, "description": "Message content — string for text-only, or array of OpenAI content parts for multimodal (see note below)" },
    "model_name": { "type": "string", "description": "Populated when sender is an LLM" },
    "external_session_id": { "type": "string", "description": "External tool session provenance (nullable)" },
    "token_count": { "type": "integer" }
  },
  "constraints": "Exactly one of context_window_id or conversation_id must be provided",
  "output": {
    "message_id": { "type": "string" },
    "conversation_id": { "type": "string" },
    "sequence_number": { "type": "integer" },
    "deduplicated": { "type": "boolean", "description": "True if message was a consecutive duplicate (not inserted)" }
  }
}
```

> **Multimodal Content Support (GAP — not yet implemented)**
>
> Conversation turns are multimodal — users send images, documents, and other non-text
> content. Currently `content` is stored as a plain string, which loses all non-text
> content. To preserve multimodal content across conversation history:
>
> - `content` must accept both formats: a plain string (text-only, backward compatible)
>   or an array of OpenAI content parts (`[{"type": "text", "text": "..."}, {"type":
>   "image_url", "image_url": {"url": "data:image/png;base64,..."}}]`).
> - Storage: JSONB column. Plain strings stored as-is; content parts arrays stored as
>   JSON arrays.
> - `conv_retrieve_context` returns content in the same format it was stored — callers
>   receive multimodal content parts when the original message contained them.
> - Embedding pipeline: extract text parts for embedding; non-text parts stored but not
>   embedded.
> - Context assembly: include multimodal content in Tier 3 (recent turns verbatim);
>   Tier 1/2 summaries are text-only.
```

**Deduplication:** First step before any downstream processing. Checks if the incoming message has identical content to the most recent message from the same `sender_id` in the same conversation. If so, the insert is skipped (return success with `deduplicated: true`), no embedding job is queued, no token count update, no context assembly trigger. The existing message's content is updated in-place with a repeat count suffix (e.g., `\n\n---\n[repeated 47 times]`). Two complementary signals: the content suffix informs the conversation itself (summarizer/context assembly recognizes loops); log events (info on first dup, warning at 5+) serve ops observability. Embedding is left as-is on repeat count updates.

#### `conv_retrieve_context`
```json
{
  "input": {
    "context_window_id": { "type": "string", "required": true }
  },
  "output": {
    "context": { "type": "string", "description": "Assembled three-tier context with XML markers" },
    "tiers": {
      "archival_summary": { "type": "string", "nullable": true },
      "chunk_summaries": { "type": "array", "nullable": true },
      "recent_messages": { "type": "array" }
    },
    "total_tokens": { "type": "integer" },
    "assembly_status": { "type": "string", "enum": ["ready", "blocked_waiting", "error"] }
  }
}
```

**Blocking behavior:** If context assembly is in progress, the call blocks and waits (assembly was triggered because the conversation exceeds the context window — there is no valid context without the summary). Timeout after ~60-90 seconds; returns error if assembly hasn't completed. The caller's flow handles the error.

#### `conv_search`
```json
{
  "input": {
    "query": { "type": "string", "description": "Semantic search query (optional). Embeds via Sutherland, cosine similarity against message embeddings, results grouped by conversation" },
    "flow_id": { "type": "string" },
    "user_id": { "type": "string" },
    "sender_id": { "type": "integer" },
    "external_session_id": { "type": "string", "description": "Filter by external tool session (e.g. Claude Code session ID)" },
    "date_from": { "type": "string", "format": "iso8601" },
    "date_to": { "type": "string", "format": "iso8601" },
    "limit": { "type": "integer", "default": 50 },
    "offset": { "type": "integer", "default": 0 }
  },
  "output": {
    "conversations": {
      "type": "array",
      "items": { "id": "string", "flow_id": "string", "flow_name": "string", "title": "string", "total_messages": "integer", "created_at": "string", "updated_at": "string", "best_match_score": "number (present only for semantic searches)" }
    }
  }
}
```

#### `conv_search_messages`
```json
{
  "input": {
    "query": { "type": "string", "description": "Search query (optional). Two-stage retrieval: Stage 1 = hybrid RRF combining vector ANN + BM25 full-text (top 50 candidates); Stage 2 = cross-encoder reranker (bge-reranker-v2-m3 via Sutherland) returns top 10 by relevance score. Falls back to Stage 1 results if reranker unavailable." },
    "conversation_id": { "type": "string" },
    "sender_id": { "type": "integer" },
    "role": { "type": "string" },
    "external_session_id": { "type": "string" },
    "date_from": { "type": "string", "format": "iso8601" },
    "date_to": { "type": "string", "format": "iso8601" },
    "limit": { "type": "integer", "default": 50 },
    "offset": { "type": "integer", "default": 0 }
  },
  "output": {
    "messages": {
      "type": "array",
      "items": { "id": "string", "conversation_id": "string", "role": "string", "sender_id": "integer", "content": "string", "created_at": "string", "score": "number" }
    }
  }
}
```

#### `conv_get_history`
```json
{
  "input": {
    "conversation_id": { "type": "string", "required": true }
  },
  "output": {
    "conversation": { "type": "object" },
    "messages": { "type": "array", "description": "Full message sequence in chronological order" }
  }
}
```

#### `conv_search_context_windows`
```json
{
  "input": {
    "context_window_id": { "type": "string", "description": "Get a specific window" },
    "conversation_id": { "type": "string", "description": "List windows for a conversation" },
    "build_type_id": { "type": "string", "description": "Filter by build type" }
  },
  "output": {
    "context_windows": {
      "type": "array",
      "items": { "id": "string", "conversation_id": "string", "build_type_id": "string", "max_token_limit": "integer", "last_assembled_at": "string", "created_at": "string" }
    }
  }
}
```

#### `mem_search`
```json
{
  "input": {
    "query": { "type": "string", "required": true },
    "user_id": { "type": "string", "required": true },
    "conversation_id": { "type": "string", "description": "Narrow results to memories from a specific conversation" },
    "agent_id": { "type": "string" },
    "limit": { "type": "integer", "default": 10 }
  },
  "output": {
    "memories": { "type": "array" },
    "degraded": { "type": "boolean", "description": "True if embedding service unavailable (no semantic search)" }
  }
}
```

#### `mem_get_context`
```json
{
  "input": {
    "user_id": { "type": "string", "required": true },
    "query": { "type": "string", "required": true },
    "conversation_id": { "type": "string", "description": "Narrow results to memories from a specific conversation" },
    "agent_id": { "type": "string" },
    "limit": { "type": "integer", "default": 5 }
  },
  "output": {
    "context": { "type": "string", "description": "Formatted memories for prompt injection" },
    "memories": { "type": "array" }
  }
}
```

---

## 5. Backing Services

### 5.1 rogers-postgres (PostgreSQL 16 + pgvector)

**Why:** Durable ACID storage for conversations, messages, context windows, summaries, and build type configuration. pgvector extension provides 768-dimensional embedding storage for semantic search without a separate vector DB.

**Custom image justification:** pgvector cannot be installed at runtime — it requires compilation at image build time. The `pgvector/pgvector:pg16` community image provides this. The official `postgres:16-alpine` base cannot be used.

**Schema:** `init.sql` is `COPY`'d into the image at build time (`/docker-entrypoint-initdb.d/01-init.sql`). Runs automatically on first postgres start.
**Credentials:** `/storage/credentials/rogers/postgres.txt` (plain-text password, mounted via `POSTGRES_PASSWORD_FILE`)
**Data path:** Bind-mounted at `/var/lib/postgresql/data` (host path: `/mnt/ssd1/workspace/rogers/databases/postgres/data`)

### 5.2 rogers-neo4j (Neo4j 5)

**Why:** Mem0 uses a hybrid vector + graph approach. pgvector handles semantic similarity; Neo4j stores entity relationship triplets (`entity1, relationship, entity2`). Graph traversal finds connected facts that vector similarity misses (e.g., `alice prefers coffee` + `alice intolerant of dairy`).

**Plugins:** APOC (required by Mem0). **Offline-first exception:** Currently installed via `NEO4J_PLUGINS=["apoc"]` environment variable, which triggers a runtime download on first start. This violates REQ-000 §1.5. Mitigation: once downloaded, the plugin persists in the data volume and is not re-downloaded on subsequent starts. Future improvement: pre-cache the APOC jar in `/storage/neo4j-plugins/` and mount into `/var/lib/neo4j/plugins/`.
**Configuration:** Via environment variables in docker-compose (heap size, etc.). No external config file.
**Credentials:** `/storage/credentials/rogers/neo4j.txt` (`NEO4J_AUTH=neo4j/<password>` format, mounted via `env_file`)
**Data path:** Bind-mounted at `/data` (host path: `/mnt/ssd1/workspace/rogers/databases/neo4j/data`)

### 5.3 rogers-redis (Redis 7)

**Why:** Durable job queue for async pipeline tasks (embedding, context assembly, memory extraction). Redis persistence (AOF) ensures no job loss if container restarts.

**Configuration:** Via command args in docker-compose (`redis-server --appendonly yes --dir /data`). No external config file.
**Data path:** Bind-mounted at `/data` (host path: `/mnt/ssd1/workspace/rogers/databases/redis/data`)

---

## 6. External Dependencies

| Service | Host | Port | Purpose | Degradation |
|---|---|---|---|---|
| Sutherland | m5 | 11435 | 768-dim text embeddings (`llm_embeddings`). LLM for `small-basic` summarization + Mem0 memory extraction. Cross-encoder reranking via `llm_rerank` (bge-reranker-v2-m3) for Stage 2 message search. | Queue embedding/assembly jobs in Redis; retrieval continues without summaries. `conv_search_messages` falls back to Stage 1 hybrid RRF results if reranker unavailable. |
| Gemini API | external | — | LLM for `standard-tiered` summarization (Gemini Flash-Lite) | Queue jobs in Redis; retrieval continues without summaries |

**Sutherland tools used for embeddings:** `llm_embeddings` (single or batch, max 32) → 768-dim vectors via `embed-default` alias (e.g. BAAI/bge-base-en-v1.5 or nomic-embed-text-v1.5).

**Summarization LLM routing** (internal to Rogers, not caller-configurable):
- `small-basic` build type (≤30k): Local LLM via Sutherland peer proxy. Free (local GPU)
- `standard-tiered` build type (30k+): Gemini Flash-Lite API. ~$0.10-0.15/1M input tokens, ~250-393 t/s

**Call pattern (ADR-053 peer proxy):** `rogers-langgraph` is on `rogers-net` only and cannot reach `joshua-net` directly. All calls to external peers go through the rogers gateway peer proxy on the private network:

```
rogers-langgraph  →  POST http://rogers:6380/peer/sutherland/llm_embeddings  (rogers-net)
rogers gateway    →  POST http://sutherland:11435/tool/llm_embeddings       (joshua-net)

rogers-langgraph  →  POST http://rogers:6380/peer/sutherland/[tool_name]    (rogers-net)
rogers gateway    →  POST http://sutherland:11435/tool/[tool_name]          (joshua-net)
                     (tool_name examples: llm_chat_completions, llm_rerank)
```

Gemini API calls go directly from `rogers-langgraph` (M5 has internet access).

---

## 7. LangGraph Flows (rogers-langgraph)

Rogers implements **five StateGraph flows** and **two simple-function modules**. Each StateGraph is a distinct pipeline with its own TypedDict state, nodes, edges, and compilation. Each is compiled once at module load time and invoked either by HTTP request (synchronous) or by the queue worker (asynchronous).

| StateGraph | File | Trigger | Type |
|---|---|---|---|
| Message Pipeline | `flows/message_pipeline.py` | HTTP: `conv_store_message` | Synchronous (request-driven) |
| Embed Pipeline | `flows/embed_pipeline.py` | Queue: `embedding_jobs` | Asynchronous (queue-driven) |
| Context Assembly | `flows/context_assembly.py` | Queue: `context_assembly_jobs` | Asynchronous (queue-driven) |
| Memory Extraction | `flows/memory_extraction.py` | Queue: `memory_extraction_jobs` | Asynchronous (queue-driven) |
| Retrieval | `flows/retrieval.py` | HTTP: `conv_retrieve_context` | Synchronous (request-driven) |

| Simple Functions | File | Purpose |
|---|---|---|
| Conversation Ops | `flows/conversation_ops.py` | Single-step CRUD (create conversation, create window, search, get history) |
| Memory Ops | `flows/memory_ops.py` | Single-step Mem0 wrappers (search, get_context, add, list, delete) |

Simple-function modules handle operations that are single-step with no branching or orchestration. They do not require StateGraph overhead.

**End-to-end flow:** When a message arrives via `conv_store_message`, the Message Pipeline stores it and enqueues an embed job. The queue worker picks up the job and invokes the Embed Pipeline, which embeds the message and fans out to both Context Assembly and Memory Extraction queues. Each downstream pipeline runs independently via its own queue consumer.

---

### 7.1 Message Pipeline StateGraph

**File:** `flows/message_pipeline.py`
**Trigger:** HTTP request to `/conv_store_message`
**Purpose:** Synchronous message ingestion — dedup, store, queue for async processing.

**State:**
```python
class MessagePipelineState(TypedDict):
    # Inputs
    conversation_id: str
    context_window_id: Optional[str]
    role: str
    sender_id: int
    content: str
    token_count: Optional[int]
    model_name: Optional[str]
    external_session_id: Optional[str]
    content_type: Optional[str]
    priority: int                   # 0=live user (highest) .. 3=migration (lowest)

    # Outputs (set by nodes)
    message_id: Optional[str]
    sequence_number: Optional[int]
    deduplicated: bool
    queued_jobs: list
    error: Optional[str]
```

**Nodes:**

| Node | Purpose | Service calls |
|---|---|---|
| `resolve_conversation` | Resolve conversation_id from context_window_id if needed | `db.get_context_window()` |
| `dedup_check` | Compare content to last message from same sender_id. If duplicate, update repeat count suffix on existing message. | `db.get_last_message_from_sender()`, `db.update_message_content()` |
| `store_message` | Insert message into `conversation_messages`, update conversation counters | `db.get_next_sequence_number()`, `db.insert_message()` |
| `queue_embed` | Push embedding job to Redis `embedding_jobs` list | `db.get_redis()`, Redis `lpush` |

**Edges:**
```
    [resolve_conversation]
         |            \
       (ok)        (error → END)
         |
    [dedup_check]
       /        \
 (duplicate     (new message)
  → END)            |
              [store_message]
                    |
              [queue_embed]
                    |
                   END
```

**Routing functions:**
- `should_continue_after_resolve`: END if error, else `dedup_check`
- `should_continue_after_dedup`: END if deduplicated or error, else `store_message`

---

### 7.2 Embed Pipeline StateGraph

**File:** `flows/embed_pipeline.py`
**Trigger:** Queue worker pulling from `embedding_jobs` Redis list
**Purpose:** Embed a message via Sutherland, store the vector, then fan out to context assembly and memory extraction queues.

**State:**
```python
class EmbedPipelineState(TypedDict):
    # Inputs (from job payload)
    message_id: str
    conversation_id: str

    # Intermediate (set by nodes)
    message: Optional[dict]             # Full message row from postgres
    embedding: Optional[list]           # 768-dim vector from Sutherland

    # Output
    assembly_jobs_queued: list          # context_window_ids queued for assembly
    extraction_queued: bool             # Whether memory extraction was queued
    error: Optional[str]
```

**Nodes:**

| Node | Purpose | Service calls |
|---|---|---|
| `fetch_message` | Fetch message row by UUID. If not found, set error. | `db.get_message_by_id()` |
| `embed_message` | Call Sutherland peer proxy for 768-dim embedding. If `embedding.context_window_size > 0` (from config), fetches N prior messages and prepends `[Context]\n...\n[Current]\n...` prefix before embedding. Disambiguates short messages that otherwise cluster near the origin of embedding space. | `db.get_prior_messages()`, `peer_client.embed_text()` |
| `store_embedding` | Write embedding vector to message row | `db.store_embedding()` |
| `check_context_assembly` | For each context window on this conversation, check if token threshold is crossed. If so, push job to `context_assembly_jobs`. | `db.get_conversation()`, `db.get_context_windows_for_conversation()`, `db.get_build_type()`, Redis `lpush` |
| `queue_memory_extraction` | Queue extraction if message is `content_type='conversation'` AND `memory_extracted` is false. Uses priority-based ZSET scoring. | Redis `zadd` on `memory_extraction_jobs` |

**Priority scoring** (for memory_extraction_jobs ZSET):
```python
_PRIORITY_OFFSET = {
    0: 3_000_000_000_000,  # P0: live user interactions
    1: 2_000_000_000_000,  # P1: interactive agent comms
    2: 1_000_000_000_000,  # P2: background agent prose
    3: 0,                  # P3: migration / bulk backlog
}
score = _PRIORITY_OFFSET[priority] + message_created_at_timestamp
```

Each bucket is 10^12 apart (larger than any unix timestamp ~1.8x10^9), guaranteeing priority-level ordering regardless of timestamp.

**Edges:**
```
             [fetch_message]
               |         \
          (has message)   (error → END)
               |
         [embed_message]
               |
        [store_embedding]
               |
    [check_context_assembly]
               |
   [queue_memory_extraction]
               |
              END
```

**Routing functions:**
- `check_error_after_fetch`: END if error, else `embed_message`

**Module-level configuration:** The embed pipeline reads `embedding.context_window_size` from config at runtime. Set via `configure(config)` called from `server.py` at startup (same pattern as memory_extraction.py).

**Design note:** `check_context_assembly` and `queue_memory_extraction` both enqueue to Redis (fast, non-blocking). The actual assembly and extraction work happens asynchronously via their own independent queue consumers.

---

### 7.3 Context Assembly StateGraph

**File:** `flows/context_assembly.py`
**Trigger:** Queue worker pulling from `context_assembly_jobs` Redis list
**Purpose:** Build three-tier context for a specific context window using LLM summarization.

#### 7.3.1 Three-Tier Strategy

Context assembly is proactive — triggered after message storage, runs in background during dead time between prompts. When `conv_retrieve_context` is called, the work is already done.

**Three tiers:**

| Tier | Content | Characteristics |
|---|---|---|
| Tier 1: Archival summary | Structured document covering the full conversation history | Stable, rarely changes, cacheable. Updated via consolidation (oldest Tier 2 chunks fold in) |
| Tier 2: Chunk summaries | Rolling summaries of message chunks as they age out of Tier 3 | Accumulate over time. Oldest chunks consolidate into Tier 1 |
| Tier 3: Recent messages | Verbatim recent messages | Full detail, no compression |

**Proportions scale with window size:**

| Window | Tier 1 | Tier 2 | Tier 3 |
|---|---|---|---|
| 30k | ~10% (3k) | ~20% (6k) | ~70% (21k) |
| 200k | ~3% (6k) | ~22% (44k) | ~75% (150k) |
| 1M | ~1% (10k) | ~15% (150k) | ~84% (840k) |

**Assembled context format:**
```xml
<archival_summary>[Tier 1 content]</archival_summary>
<chunk_summaries>[Tier 2 content]</chunk_summaries>
<recent_messages>[Tier 3 content]</recent_messages>
```

#### 7.3.2 Custom Assembly Flows (Henson Integration)

In addition to the generic three-tier strategy, Rogers supports custom assembly flows requested via the `build_type_id` parameter (e.g., invoked by Henson's Imperator).
- **`grace-cag-full-docs`**: Bypasses standard summarization. Injects a predefined bundle of raw architectural documents (REQ-000, HLDs, etc.) followed by the most recent conversation turns verbatim.
- **`gunner-rag-mem0-heavy`**: Alters the proportion to prioritize deep Mem0 graph traversal (personal facts, emotional anchors) and semantic RAG over recent history to assemble a specialized "Continuation Block".

#### 7.3.3 StateGraph Specification

**State:**
```python
class ContextAssemblyState(TypedDict):
    # Inputs (from job payload)
    conversation_id: str
    context_window_id: str              # UUID string
    build_type_id: str                  # e.g. "small-basic", "standard-tiered"

    # Intermediate (set by nodes)
    window: Optional[dict]              # Context window row from postgres
    build_type: Optional[dict]          # Build type config row
    messages: list                      # All messages for the conversation
    max_token_limit: int                # From window config
    tier3_budget: int                   # Calculated token budget for Tier 3
    tier3_start_seq: int                # Sequence number boundary for Tier 3
    older_messages: list                # Messages that need summarization
    chunks: list                        # Chunked older messages (20 msgs per chunk)
    llm: Optional[object]              # LLM adapter instance (not serializable)
    model_name: str                     # Name of the model used for summarization
    tier2_summaries_written: int        # Count of Tier 2 summaries written
    tier1_consolidated: bool            # Whether Tier 1 consolidation happened

    # Control
    assembly_key: str                   # Redis key for assembly_in_progress flag
    error: Optional[str]
```

**Note on `llm` field:** The LLM adapter object is not JSON-serializable and would not survive checkpointing. These background queue flows do not use checkpointing — they are fire-and-forget. If they fail, the queue worker retries from scratch.

**Nodes:**

| Node | Purpose | Service calls |
|---|---|---|
| `set_assembly_flag` | Set Redis `assembly_in_progress:{window_id}` with 120s TTL. Retrieval flow checks this flag to block/wait. | Redis `set` |
| `load_window_config` | Fetch window row and build type config. Set error if not found. | `db.get_context_window()`, `db.get_build_type()` |
| `load_messages` | Fetch all messages for the conversation. | `db.get_conversation_messages()` |
| `calculate_tiers` | Calculate tier 3 budget (70-84% based on window size), determine tier 3 boundary by walking backwards from most recent message, chunk older messages into groups of 20. | (pure computation) |
| `select_llm` | Select LLM adapter based on `build_type_id`: `small-basic` → Sutherland/Qwen (local), `standard-tiered` → Gemini Flash-Lite (cloud). | `mem0_setup._build_llm_adapter()` |
| `summarize_chunks` | Deactivate old Tier 2 summaries. For each chunk, LLM summarize (in thread pool — LLM adapters are synchronous), insert summary. | `db.deactivate_summaries_for_window()`, `llm.generate_response()` (in executor), `db.insert_summary()` |
| `consolidate_tier1` | If >3 active Tier 2 summaries, consolidate oldest into single Tier 1 archival summary. Keep 2 most recent Tier 2 chunks active. | `db.get_active_summaries_for_window()`, `llm.generate_response()` (in executor), `db.deactivate_summaries_for_window()`, `db.insert_summary()` |
| `finalize_assembly` | Update window `last_assembled_at` timestamp. | `db.update_window_last_assembled()` |
| `clear_assembly_flag` | Delete Redis assembly_in_progress flag. **ALWAYS reached** — normal and error paths both route here. | Redis `delete` |

**Edges:**
```
        [set_assembly_flag]
                |
       [load_window_config]
          /          \
    (error)        (ok)
        |              |
        |       [load_messages]
        |        /    |     \
        |  (no msgs) (ok)  (error)
        |     |       |      |
        |     |  [calculate_tiers]
        |     |     /       \
        |     | (no older)  (has older)
        |     |    |           |
        |     |    |      [select_llm]
        |     |    |           |
        |     |    |    [summarize_chunks]
        |     |    |           |
        |     |    |    [consolidate_tier1]
        |     |    |           |
        |     +----+----[finalize_assembly]
        |                      |
        +---[clear_assembly_flag]
                   |
                  END
```

**Routing functions:**
- `after_load_config`: error → `clear_assembly_flag`, ok → `load_messages`
- `after_load_messages`: no messages → `finalize_assembly` (skip, not error), error → `clear_assembly_flag`, ok → `calculate_tiers`
- `after_calculate_tiers`: no older messages → `finalize_assembly` (all fits in tier 3), has older → `select_llm`

**Critical design point:** `clear_assembly_flag` is reachable from ALL terminal paths. This replaces the `try/finally` pattern — the Redis flag is always cleaned up regardless of whether the flow succeeds or errors.

---

### 7.4 Memory Extraction StateGraph

**File:** `flows/memory_extraction.py`
**Trigger:** Queue worker pulling from `memory_extraction_jobs` Redis ZSET (priority-scored)
**Purpose:** Extract knowledge from unprocessed conversational messages via Mem0.

**State:**
```python
class MemoryExtractionState(TypedDict):
    # Input (from job payload)
    conversation_id: str

    # Intermediate (set by nodes)
    messages: list                      # Unextracted conversational messages
    user_id: str                        # From conversation row
    conversation_text: str              # Built text for Mem0 input
    selected_message_ids: list          # Message IDs included in the text
    extraction_tier: str                # "small" or "large" — determines Mem0 instance

    # Output
    extracted_count: int                # Number of messages marked as extracted
    error: Optional[str]
```

**Nodes:**

| Node | Purpose | Service calls |
|---|---|---|
| `fetch_unextracted` | Get messages where `content_type='conversation'` AND `memory_extracted=FALSE`. Also fetch conversation row for `user_id`. | `db.get_unextracted_messages()`, `db.get_conversation()` |
| `build_extraction_text` | Build conversation text from messages newest-first with character budget. Route to `small` or `large` tier based on text length vs config thresholds (`small_llm_max_chars`, `large_llm_max_chars`). | (pure computation using config) |
| `run_mem0_extraction` | Call `mem0.add()` via the appropriate Mem0 instance (small → Sutherland/Qwen, large → Gemini Flash-Lite). Runs in thread pool executor because Mem0 operations are synchronous. | `mem0_setup.get_mem0_small()` or `get_mem0_large()`, `mem0.add()` (in executor) |
| `mark_extracted` | Mark all selected message IDs as `memory_extracted=TRUE` in postgres. Only called after successful `mem0.add()`. | `db.mark_messages_extracted()` |

**Hybrid LLM routing:** Text ≤ `small_llm_max_chars` (default 90k) → small/local LLM (Sutherland/Qwen). Text > `small_llm_max_chars` → large/cloud LLM (Gemini Flash-Lite). Thresholds configured in `config.json` under `memory_extraction`.

**Edges:**
```
    [fetch_unextracted]
       /           \
 (no messages       (has messages)
  → END)                |
               [build_extraction_text]
                        |
               [run_mem0_extraction]
                        |
                 [mark_extracted]
                        |
                       END
```

**Routing functions:**
- `after_fetch`: no messages or error → END, has messages → `build_extraction_text`

**Module-level configuration:** This flow requires access to config, postgres password, neo4j password, and gateway URL for Mem0 initialization. Set via `configure()` function called from `server.py` at startup.

---

### 7.5 Retrieval StateGraph

**File:** `flows/retrieval.py`
**Trigger:** HTTP request to `/conv_retrieve_context`
**Purpose:** Retrieve assembled three-tier context for a context window. Blocks if assembly is in progress.

**State:**
```python
class RetrievalState(TypedDict):
    # Input
    context_window_id: str

    # Intermediate
    conversation_id: Optional[str]
    build_type: Optional[dict]
    window: Optional[dict]
    max_token_limit: int
    tier1_summary: Optional[str]
    tier2_summaries: list
    recent_messages: list

    # Output
    context: Optional[str]
    tiers: Optional[dict]
    total_tokens: int
    assembly_status: str            # 'ready', 'blocked_waiting', 'error'
    error: Optional[str]
```

**Nodes:**

| Node | Purpose | Service calls |
|---|---|---|
| `get_window` | Fetch context window and build type config. Set error if not found. | `db.get_context_window()`, `db.get_build_type()` |
| `check_assembly` | If `assembly_in_progress:{window_id}` flag exists in Redis, poll every 2s until cleared or timeout (50s). | Redis `get`, `asyncio.sleep` |
| `get_summaries` | Fetch active Tier 1 and Tier 2 summaries for this window. | `db.get_active_summaries_for_window()` |
| `get_recent` | Fetch Tier 3 recent messages within remaining token budget (total budget minus summary tokens). | `db.get_conversation_messages()` |
| `assemble` | Format three-tier context with XML markers. Build `tiers` dict with structured breakdown. | (pure formatting) |

**Edges:**
```
    [get_window]
       |        \
     (ok)    (error → END)
       |
  [check_assembly]
       |
  [get_summaries]
       |
   [get_recent]
       |
    [assemble]
       |
      END
```

**Routing functions:**
- `check_error`: error → END, ok → `check_assembly`

---

### 7.6 Queue Worker (concurrent background consumers)

**File:** `services/queue_worker.py`
**Purpose:** Background infrastructure that polls Redis queues and invokes compiled StateGraphs. Not itself a StateGraph — it is the scheduling layer.

**Architecture:** Three independent async consumer loops plus a dead-letter sweep loop, launched via `asyncio.gather()`:

```python
asyncio.gather(
    _consume_embedding_queue(embed_graph),
    _consume_context_assembly_queue(assembly_graph),
    _consume_memory_extraction_queue(extraction_graph),
    _sweep_dead_letters_loop(),
)
```

Each consumer independently polls its own queue and invokes its compiled StateGraph via `graph.ainvoke(initial_state)`. This ensures embedding does not block extraction, and context assembly does not block either.

**Consumer pattern (each queue follows this):**
1. Poll queue (Redis `rpop` for lists, `zpopmax` for ZSET)
2. If empty, `asyncio.sleep(QUEUE_POLL_INTERVAL)` and retry
3. Parse job JSON, construct initial state for the graph
4. Invoke compiled StateGraph: `result = await graph.ainvoke(initial_state)`
5. Check result for error
6. On failure: `_handle_failure()` (shared helper)

**Error handling (shared `_handle_failure`):**
- Increment `attempt` counter
- If `attempt ≤ 3`: re-enqueue with exponential backoff (5s, 25s, 125s)
- If `attempt > 3`: move to `dead_letter_jobs` queue, log at ERROR level

**Dead-letter sweep:** Independent loop, runs every 60s. Moves dead-letter jobs back to their original queues with `attempt` reset to 1. Up to 10 jobs per sweep.

**Job payload schema:**
```json
{
  "message_id": "uuid",
  "conversation_id": "string",
  "context_window_id": "uuid (context_assembly_jobs only)",
  "build_type_id": "string (context_assembly_jobs only)",
  "job_type": "embed | context_assembly | extract_memory",
  "enqueued_at": "iso8601",
  "attempt": 1
}
```

**Configuration:** `configure()` receives config dict, credentials, gateway URL, and the three compiled StateGraph objects from `server.py` at startup.

**Polling interval:** 5 seconds (configurable via `QUEUE_POLL_INTERVAL` environment variable).

---

### 7.7 Simple Function Modules

#### 7.7.1 Conversation Operations (`flows/conversation_ops.py`)

Single-step CRUD handlers called directly from HTTP route handlers. No StateGraph needed.

| Function | Purpose |
|---|---|
| `create_conversation()` | INSERT into conversations (ON CONFLICT DO NOTHING) |
| `create_context_window()` | INSERT into context_windows with validation |
| `get_history()` | SELECT conversation + messages in chronological order |
| `search_conversations()` | Semantic (embedding similarity) + structured filter search |
| `search_messages()` | Two-stage hybrid search: Stage 1 = hybrid RRF (vector ANN + BM25 full-text, top 50 candidates); Stage 2 = cross-encoder reranker via Sutherland `llm_rerank` (bge-reranker-v2-m3, top 10). Falls back to Stage 1 results if reranker unavailable. |
| `search_context_windows_handler()` | Filter context windows by ID, conversation, or build type |

#### 7.7.2 Memory Operations (`flows/memory_ops.py`)

Single-step Mem0 wrappers called directly from HTTP route handlers. All Mem0 operations are synchronous and run in thread pool executors.

| Function | Purpose |
|---|---|
| `mem_search()` | `m.search()` — hybrid pgvector + Neo4j traversal |
| `mem_get_context()` | `m.search()` formatted for prompt injection |
| `mem_add()` | `m.add()` — store a memory |
| `mem_list()` | `m.get_all()` — list memories for a user |
| `mem_delete()` | `m.delete()` — remove a memory by ID |

**Mem0 scoping:**
```python
# Storage — always includes conversation_id as run_id
m.add(content, user_id=user_id, agent_id=agent_id, run_id=conversation_id)

# Retrieval — two paths:
m.search(query, user_id=user_id)                          # all memories for this user
m.search(query, user_id=user_id, run_id=conversation_id)  # memories from this conversation only

m.get_all(user_id=user_id)
m.delete(memory_id)
```

---

### 7.8 Mem0 Configuration

Mem0 requires an LLM and an embedder. Sutherland is on `joshua-net` and unreachable directly from `rogers-langgraph`. All external calls go through the rogers gateway peer proxy. Because Mem0 uses its own internal OpenAI client, standard OpenAI-compatible `base_url` configuration is not sufficient — custom adapter classes are required.

**Two Mem0 instances** (lazy-initialized singletons, thread-safe):
- `get_mem0_small()` — uses small/local LLM (Sutherland/Qwen via peer proxy). For extraction text ≤ `small_llm_max_chars`.
- `get_mem0_large()` — uses large/cloud LLM (Gemini Flash-Lite via OpenAI-compatible API). For extraction text > `small_llm_max_chars`.

Both share the same pgvector + Neo4j graph store but use different LLM adapters.

**Custom LLM adapters** (`mem0_adapters.py`):
- `SutherlandLlmAdapter` — implements Mem0's `BaseLlm`. Routes via peer proxy: `POST http://rogers:6380/peer/sutherland/chat_completions`
- `OpenAICompatibleLlmAdapter` — implements Mem0's `BaseLlm`. Calls any OpenAI-compatible API directly (Gemini, etc.)

**Custom embedder adapter** (`mem0_adapters.py`):
- `SutherlandEmbedderAdapter` — implements Mem0's `BaseEmbedder`. Routes via peer proxy: `POST http://rogers:6380/peer/sutherland/llm_embeddings`. Returns 768-dim vector; declares `dims=768`.

**Mem0 initialisation** (`mem0_setup.py`): Mem0's Pydantic validators require a valid provider at construction time. The code creates a `Memory()` instance with placeholder `"openai"` provider config, then **post-injection replaces** the LLM and embedder slots with the custom adapters:

```python
# Step 1: Build Memory with placeholder config (satisfies Pydantic)
mem_config = MemoryConfig(
    version="v1.1",
    llm=LlmConfig(provider="openai", config={"api_key": "placeholder"}),
    embedder=EmbedderConfig(provider="openai", config={"api_key": "placeholder"}),
    vector_store=VectorStoreConfig(
        provider="pgvector",
        config={
            "host": "rogers-postgres",
            "port": 5432,
            "dbname": "rogers",
            "user": "rogers",
            "password": postgres_password,
            "collection_name": "mem0_memories",
            "embedding_model_dims": 768,
        }
    ),
    graph_store=GraphStoreConfig(
        provider="neo4j",
        config={
            "url": "bolt://rogers-neo4j:7687",
            "username": "neo4j",
            "password": neo4j_password,
        }
    ),
)
mem = Memory(config=mem_config)

# Step 2: Replace placeholders with real adapters
mem.llm = llm_adapter                  # SutherlandLlmAdapter or OpenAICompatibleLlmAdapter
mem.embedding_model = embed_adapter    # SutherlandEmbedderAdapter
mem.graph.llm = llm_adapter            # Graph store also needs the LLM
mem.graph.embedding_model = embed_adapter
```

**Credentials:** postgres and neo4j passwords read from files at `/storage/credentials/rogers/` (paths configured in `config.json` under `credentials`).

---

## 8. Data Models

### 8.1 conversations
```sql
CREATE TABLE conversations (
    id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255),
    flow_id VARCHAR(255),
    flow_name VARCHAR(255),
    title VARCHAR(500),
    total_messages INTEGER DEFAULT 0,
    estimated_token_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_conversations_flow ON conversations(flow_id);
CREATE INDEX idx_conversations_flow_user ON conversations(user_id, flow_id, updated_at DESC);
```

### 8.2 conversation_messages
```sql
CREATE TABLE conversation_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id VARCHAR(255) NOT NULL REFERENCES conversations(id),
    role VARCHAR(50) NOT NULL,              -- 'user', 'assistant', 'system', 'tool'
    sender_id INTEGER NOT NULL,             -- system UID of participant
    content TEXT NOT NULL,
    token_count INTEGER,
    model_name VARCHAR(100),                -- populated when sender is an LLM
    external_session_id VARCHAR(255),       -- tool session this message came from (nullable)
    embedding vector(768),                  -- single embedding per message
    sequence_number INTEGER NOT NULL,       -- ordering within conversation
    content_type VARCHAR(50) DEFAULT 'conversation',  -- conversation|tool_output|info|error
    priority SMALLINT DEFAULT 3,                      -- Queue priority: 0=live user (highest), 1=interactive, 2=agent-comms, 3=migration (lowest)
    memory_extracted BOOLEAN DEFAULT FALSE,            -- set TRUE after Mem0 extraction
    created_at TIMESTAMP DEFAULT NOW(),
    content_tsv tsvector GENERATED ALWAYS AS (to_tsvector('english', coalesce(content, ''))) STORED  -- BM25 full-text search
);
CREATE INDEX idx_messages_conversation ON conversation_messages(conversation_id);
CREATE INDEX idx_messages_conversation_seq ON conversation_messages(conversation_id, sequence_number);
CREATE INDEX idx_messages_conversation_sender ON conversation_messages(conversation_id, sender_id, sequence_number DESC);
CREATE INDEX idx_messages_created ON conversation_messages(created_at);
CREATE INDEX idx_messages_emb ON conversation_messages USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX idx_messages_tsv ON conversation_messages USING GIN(content_tsv);
```

### 8.3 context_window_build_types
```sql
CREATE TABLE context_window_build_types (
    id VARCHAR(100) PRIMARY KEY,            -- e.g. 'small-basic', 'standard-tiered'
    trigger_threshold_percent FLOAT DEFAULT 0.75,
    recent_window_percent FLOAT DEFAULT 0.20,
    summary_target_percent FLOAT DEFAULT 0.05,
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Seed data
INSERT INTO context_window_build_types (id, description) VALUES
  ('small-basic',     'Three-tier assembly for small context windows (≤30k). Summarization via local LLM.'),
  ('standard-tiered', 'Three-tier assembly for all larger context windows (30k+). Summarization via Gemini Flash Lite API. Proportions scale with window size.'),
  ('grace-cag-full-docs', 'Custom assembly for Grace: Injects full architectural doc bundle + recent turns.'),
  ('gunner-rag-mem0-heavy', 'Custom assembly for Gunner: Prioritizes semantic RAG + Mem0 graph traversal + emotional anchors.');
```

### 8.4 context_windows
```sql
CREATE TABLE context_windows (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id VARCHAR(255) NOT NULL REFERENCES conversations(id),
    build_type_id VARCHAR(100) NOT NULL REFERENCES context_window_build_types(id),
    max_token_limit INTEGER NOT NULL,       -- actual token budget for this window
    last_assembled_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_windows_conversation ON context_windows(conversation_id);
```

### 8.5 conversation_summaries
```sql
CREATE TABLE conversation_summaries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id VARCHAR(255) NOT NULL REFERENCES conversations(id),
    context_window_id UUID NOT NULL REFERENCES context_windows(id),
    summary_text TEXT NOT NULL,
    summary_embedding vector(768),
    tier INTEGER NOT NULL,                  -- 1 = archival, 2 = chunk
    summarizes_from_seq INTEGER,            -- sequence_number range
    summarizes_to_seq INTEGER,
    message_count INTEGER,
    original_token_count INTEGER,
    summary_token_count INTEGER,
    summarized_by_model VARCHAR(100),
    summarized_at TIMESTAMP DEFAULT NOW(),
    superseded_by UUID REFERENCES conversation_summaries(id),
    is_active BOOLEAN DEFAULT true
);
CREATE INDEX idx_summaries_window ON conversation_summaries(context_window_id, is_active);
CREATE INDEX idx_summaries_emb ON conversation_summaries USING ivfflat (summary_embedding vector_cosine_ops) WITH (lists = 100);
```

*Mem0 creates its own tables in the same postgres instance via the Mem0 library.*

---

## 9. config.json (rogers gateway)

```json
{
  "name": "rogers",
  "port": 6380,
  "tools": {
    "conv_create_conversation":    { "description": "Create a new conversation, returns conversation_id", "target": "rogers-langgraph:8000", "endpoint": "/conv_create_conversation" },
    "conv_create_context_window":  { "description": "Create a context window instance for a build type and token limit", "target": "rogers-langgraph:8000", "endpoint": "/conv_create_context_window" },
    "conv_store_message":          { "description": "Store a single message; triggers full pipeline (dedup, embed, context assembly, memory extraction)", "target": "rogers-langgraph:8000", "endpoint": "/conv_store_message" },
    "conv_retrieve_context":       { "description": "Get assembled three-tier context for a context window. Blocks if assembly in progress", "target": "rogers-langgraph:8000", "endpoint": "/conv_retrieve_context" },
    "conv_search":                 { "description": "General-purpose conversation search: semantic query against message embeddings grouped by conversation, plus structured filters (flow_id, user_id, sender_id, external_session_id, date range)", "target": "rogers-langgraph:8000", "endpoint": "/conv_search" },
    "conv_search_messages":        { "description": "Search within messages: two-stage hybrid (Stage 1: vector ANN + BM25 RRF top 50; Stage 2: cross-encoder reranker top 10) plus structured filters (conversation_id, sender_id, role, date range)", "target": "rogers-langgraph:8000", "endpoint": "/conv_search_messages" },
    "conv_get_history":            { "description": "Get full message sequence for a conversation in chronological order", "target": "rogers-langgraph:8000", "endpoint": "/conv_get_history" },
    "conv_search_context_windows": { "description": "Search/list/get context windows by ID, conversation, or build type", "target": "rogers-langgraph:8000", "endpoint": "/conv_search_context_windows" },
    "mem_search":                  { "description": "Semantic and graph search across extracted knowledge (mem0). Different from message search: what is known vs what was said", "target": "rogers-langgraph:8000", "endpoint": "/mem_search" },
    "mem_get_context":             { "description": "Get relevant memories formatted for prompt injection", "target": "rogers-langgraph:8000", "endpoint": "/mem_get_context" },
    "rogers_stats":                { "description": "Internal: DB counts and queue depths for Apgar health monitoring", "target": "rogers-langgraph:8000", "endpoint": "/stats", "schema": {"input": {}} }
  },
  "peers": {
    "sutherland": { "host": "sutherland", "port": 11435 }
  },
  "dependencies": [
    {
      "name": "rogers-langgraph",
      "host": "rogers-langgraph",
      "port": 8000,
      "type": "http",
      "critical": true,
      "endpoint": "/health"
    },
    {
      "name": "rogers-postgres",
      "host": "rogers-postgres",
      "port": 5432,
      "type": "postgres",
      "critical": true,
      "database": "rogers",
      "user": "rogers",
      "credentials_file": "/storage/credentials/rogers/postgres.txt"
    },
    {
      "name": "rogers-neo4j",
      "host": "rogers-neo4j",
      "port": 7474,
      "type": "http",
      "critical": true,
      "endpoint": "/"
    },
    {
      "name": "rogers-redis",
      "host": "rogers-redis",
      "port": 6379,
      "type": "redis",
      "critical": true
    }
  ],
  "logging": { "level": "INFO" },
  "routing": { "timeout": 60000 }
}
```

---

## 9b. config.json (rogers-langgraph)

The langgraph container has its own `config.json` for LLM provider selection, memory extraction thresholds, and credential file paths.

```json
{
  "log_level": "INFO",
  "llm": {
    "provider": "sutherland",
    "model": "qwen2.5-7b-instruct",
    "temperature": 0.1
  },
  "gemini_llm": {
    "provider": "openai_compatible",
    "base_url": "https://generativelanguage.googleapis.com/v1beta/openai",
    "api_key_file": "/storage/credentials/api-keys/gemini.env",
    "model": "gemini-2.5-flash-lite",
    "temperature": 0.1
  },
  "memory_extraction": {
    "small_llm_max_chars": 90000,
    "large_llm_max_chars": 450000,
    "small_llm_config_key": "llm",
    "large_llm_config_key": "gemini_llm",
    "llm_timeout": 120
  },
  "embedding": {
    "context_window_size": 3
  },
  "search": {
    "hybrid_candidate_limit": 50,
    "reranker_model": "BAAI/bge-reranker-v2-m3",
    "reranker_top_n": 10
  },
  "memory": {
    "recency_decay_days": 90,
    "recency_decay_max_penalty": 0.2,
    "confidence_archive_threshold": 0.1,
    "confidence_boost_on_access": 0.15,
    "half_life_days": {
      "ephemeral":      3,
      "infrastructure": 45,
      "procedural":     90,
      "project":        180,
      "preference":     365,
      "relationship":   730,
      "historical":     null
    }
  },
  "credentials": {
    "postgres_password_file": "/storage/credentials/rogers/postgres.txt",
    "neo4j_password_file": "/storage/credentials/rogers/neo4j.txt"
  }
}
```

**LLM routing logic** (`mem0_setup._build_llm_adapter()`): reads the `llm.provider` field to select the adapter class:
- `"sutherland"` → `SutherlandLlmAdapter` (peer proxy to local LLM)
- `"openai_compatible"` → `OpenAICompatibleLlmAdapter` (direct API call)

The queue worker's `_build_summarization_llm()` selects which config section to use based on `build_type_id`: `small-basic` → `llm` section, `standard-tiered` → `gemini_llm` section.

---

## 9c. Prometheus Metrics

Rogers exposes `/metrics` per [mad-prometheus-metrics-guide.md](../../guides/mad-prometheus-metrics-guide.md).

**Gateway (`rogers`):** Standard metrics via `prom-client`. Labels: `mad=rogers`, `tool`, `status`, `error_type`. Endpoint: `GET http://rogers:6380/metrics`.

**MCP tool `metrics_get`:** Required for cross-network collection (joshua-net is MCP-only). Apgar calls `POST /peer/rogers/metrics_get` via its gateway; that proxies to `tools/call` on this gateway. **Schema:** Input: `{}` (no args). Output: `{ "content": [ { "type": "text", "text": "<Prometheus exposition format>" } ] }` — the `text` value is identical to `GET /metrics` response. **Implementation:** Register `metrics_get` in config.json; handler invokes `registry.metrics()` (or equivalent) and returns the string. Same data source as the `/metrics` route — prom-client accumulates counters/histograms from request instrumentation.

**LangGraph (`rogers-langgraph`):** Standard metrics plus Rogers-specific:

| Metric | Type | Labels | Description |
|--------|------|--------|-------------|
| `rogers_queue_depth` | Gauge | `queue` | Current depth: `embedding_jobs`, `context_assembly_jobs`, `memory_extraction_jobs`, `dead_letter_jobs` |
| `rogers_db_counts` | Gauge | `table` | Row counts: `conversations`, `messages`, `embedded`, `summaries_active`, `memories` |
| `rogers_pipeline_duration_seconds` | Histogram | `stage` | Latency: `embed`, `assembly`, `extract`. Buckets: 0.1, 0.5, 1, 2, 5, 15, 60 |
| `rogers_pipeline_operations_total` | Counter | `stage`, `status` | Completions per stage (success/error) |

Expose at `GET http://rogers-langgraph:8000/metrics` (internal; Prometheus scrapes via gateway proxy or direct if on rogers-net). Use `prometheus_client` (Python).

**Backing services:** To metric Postgres and Redis without modifying their stock images, add **exporter sidecar containers**: `rogers-postgres-exporter` (image: `prometheuscommunity/postgres-exporter`), `rogers-redis-exporter` (image: `oliver006/redis_exporter`). Each is a separate container on rogers-net, connecting to the backing service and exposing `/metrics`. Neo4j has built-in metrics. Defer to implementation phase; initial scope is gateway + langgraph.

---

## 10. Graceful Degradation

| Dependency | Unavailable Behaviour |
|---|---|
| Sutherland (embeddings) | `conv_store_message` succeeds (message stored); embedding job queued in Redis. Context retrieval falls back to chronological (no semantic search). `mem_search` returns degraded flag. |
| Sutherland | `conv_store_message` succeeds; `small-basic` context assembly jobs queued in Redis. Memory extraction jobs queued. `conv_search_messages` falls back to Stage 1 hybrid RRF results (cross-encoder reranking skipped). |
| Gemini API | `conv_store_message` succeeds; `standard-tiered` context assembly jobs queued in Redis. |
| rogers-postgres | All conversation and context tools return 503. Health reports critical dependency unavailable. |
| rogers-neo4j | `mem_*` tools return 503 or degraded. Conversation storage unaffected. |
| rogers-redis | Queue unavailable — pipeline jobs cannot be queued. Message storage still succeeds. Health reports degraded. |

---

## 11. Deployment Notes

- **Host:** M5 (all 5 containers)
- **Credentials required on M5 before first deploy:**
  - `/storage/credentials/rogers/postgres.txt`
  - `/storage/credentials/rogers/neo4j.txt`
- **Post-deployment permissions** (run on host after first deploy):
  ```bash
  chmod 750 /workspace/rogers/databases/postgres/data
  chmod 750 /workspace/rogers/databases/neo4j/data
  chmod 750 /workspace/rogers/databases/redis/data
  ```
- **registry.yml** needs full update — see Section 2

---

## 12. Verification

| Scenario | How to Verify |
|---|---|
| Gateway healthy | `curl http://m5:6380/health` → 200 |
| Create conversation | `conv_create_conversation` with test flow → returns conversation_id |
| Create context window | `conv_create_context_window` with conversation_id + build type → returns context_window_id |
| Store a message | `conv_store_message` with context_window_id → returns message_id, sequence_number |
| Dedup works | Store identical message twice → second returns `deduplicated: true` |
| Retrieve context | `conv_retrieve_context` with context_window_id → returns three-tier assembled context |
| Embedding queued | Check Redis `embedding_jobs` queue depth drops after Sutherland processes |
| Context assembly | After threshold crossed, `conv_retrieve_context` returns summaries |
| Memory search | `mem_search` with query → returns memories after pipeline runs |
| Search conversations | `conv_search` with query → returns matching conversations |
| Search messages | `conv_search_messages` with query → returns matching messages with scores |
| Hybrid reranked search | `conv_search_messages` with query → Stage 1 hybrid RRF top 50; Stage 2 reranked to top 10 by bge-reranker-v2-m3 |
| Reranker fallback | Stop Sutherland → `conv_search_messages` still returns Stage 1 results |
| Degraded embedding service | Stop Sutherland or embedding backend → `conv_store_message` still succeeds, `mem_search` returns degraded:true |
| Degraded Sutherland | Stop Sutherland → messages store, `small-basic` assembly jobs queue in Redis |

---

**References:**
- `mads/rogers/docs/architecture.md` — full design rationale
- `mads/rogers/docs/HLD-token-aware-memory-system.md` — Langflow integration
- `mads/sutherland/docs/REQ-sutherland.md` — Sutherland (embedding + LLM + rerank)
- `mads/_template/docs/REQ-langgraph-template.md` — template baseline
- `registry.yml` — UIDs, ports, hosts
