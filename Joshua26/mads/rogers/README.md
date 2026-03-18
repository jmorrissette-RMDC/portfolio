# Rogers — Conversation & Memory Service

**Host:** M5 | **Port:** 6380 | **UID:** 2002 | **Network:** joshua-net + rogers-net

Rogers is the unified conversation management service for the Joshua26 ecosystem.
It provides conversation message storage, token-aware three-tier context retrieval,
and Mem0-based knowledge graph memory via a 5-container MAD group.

Replaces: `conversation-watcher → rogers-redis → Henson → Codd`

---

## Containers

| Container | Type | Port |
|---|---|---|
| `rogers` | MCP gateway (Node.js) | 6380 (external) |
| `rogers-langgraph` | Python backend (Quart + LangGraph StateGraph) | 8000 (internal) |
| `rogers-postgres` | PostgreSQL 16 + pgvector | 5432 (internal) |
| `rogers-neo4j` | Neo4j 5 + APOC | 7687 (internal) |
| `rogers-redis` | Redis 7 | 6379 (internal) |

---

## MCP Tools (10 client-facing)

### Conversation (`conv_`)

| Tool | Description |
|---|---|
| `conv_create_conversation` | Create a new conversation, returns `conversation_id` |
| `conv_create_context_window` | Create a context window instance for a build type and token limit |
| `conv_store_message` | Store a single message; triggers full pipeline (dedup, embed, context assembly, memory extraction) |
| `conv_retrieve_context` | Get assembled three-tier context for a context window. Blocks if assembly in progress |
| `conv_search` | General-purpose conversation search: semantic query + structured filters (flow_id, user_id, sender_id, date range) |
| `conv_search_messages` | Search within messages: two-stage hybrid search (vector ANN + BM25 RRF top 50 → cross-encoder reranker top 10) + structured filters (conversation_id, sender_id, role, date range) |
| `conv_get_history` | Get full message sequence for a conversation in chronological order |
| `conv_search_context_windows` | Search/list/get context windows by ID, conversation, or build type |

### Memory (`mem_`)

| Tool | Description |
|---|---|
| `mem_search` | Semantic + graph search across extracted knowledge (mem0). What is known vs what was said |
| `mem_get_context` | Get relevant memories formatted for prompt injection |

4 additional internal tools (`mem_add`, `mem_list`, `mem_delete`, `mem_extract`) are accessible as HTTP endpoints but not exposed via MCP. They are used by the background queue worker and for admin purposes.

---

## Architecture

```
Client → rogers:6380 (MCP gateway, joshua-net + rogers-net)
              ↓
         rogers-langgraph:8000 (Quart + LangGraph StateGraph, rogers-net only)
              ↓
    ┌─────────────────────────────────────┐
    │ rogers-postgres (pgvector + schema) │
    │ rogers-neo4j   (entity graph)       │
    │ rogers-redis   (queue + cache)      │
    └─────────────────────────────────────┘

External peer calls (ADR-053):
    rogers-langgraph → rogers:6380/peer/sutherland/llm_embeddings → Sutherland (m5:11435)
    rogers-langgraph → rogers:6380/peer/sutherland/llm_chat_completions → Sutherland (m5:11435)
    rogers-langgraph → rogers:6380/peer/sutherland/llm_rerank → Sutherland (m5:11435)
```

### Data Model

- **conversations** — top-level entity with flow_id, title, participants derived from messages
- **conversation_messages** — one row per message (role, sender_id, content, embedding, sequence_number)
- **context_window_build_types** — strategy templates (small-basic, standard-tiered)
- **context_windows** — per-participant instances with build type + token limit
- **conversation_summaries** — tiered summaries keyed to context windows (tier 1 = archival, tier 2 = chunk)

### Message Pipeline (conv_store_message)

`conv_store_message` always succeeds immediately. Enrichment is deferred via Redis job queues:

1. **Dedup check** — first step; skips duplicate consecutive messages from same sender
2. **Embedding** — Sutherland `llm_embeddings` → contextual embedding using N prior messages as prefix (config: `embedding.context_window_size`, default 3) → stores 768-dim vector in postgres
3. **Context assembly** — checks all context windows on the conversation; queues three-tier assembly when threshold crossed. LLM selected by build type: Sutherland (local, small-basic) or Gemini Flash-Lite (API, standard-tiered)
4. **Memory extraction** — Mem0 `m.add()` → Neo4j entity graph + pgvector

Steps 3 and 4 queue **in parallel** after embedding completes.

If Sutherland is unavailable, jobs queue in Redis with 3-retry exponential
backoff. Dead-letter queue (`dead_letter_jobs`) captures persistent failures with periodic
sweep (every 60s, re-queues up to 10 jobs).

### Context Retrieval (conv_retrieve_context)

Three-tier context assembly within a context window's token budget:

- **Tier 1** — Archival summary (oldest content, most compressed)
- **Tier 2** — Chunk summaries (intermediate age)
- **Tier 3** — Recent messages verbatim (newest, within remaining budget)

If assembly is in progress when context is requested, the call blocks and waits (up to 50s timeout, under the gateway's 60s routing timeout).

---

## Pre-Deployment Requirements

**Credentials (on M5 before first deploy):**
```bash
# PostgreSQL (bare password)
echo "<password>" > /storage/credentials/rogers/postgres.txt

# Neo4j (TWO keys required: one for the container, one for server.py)
printf "NEO4J_AUTH=neo4j/<password>\nNEO4J_PASSWORD=<password>\n" \
  > /storage/credentials/rogers/neo4j.txt

# Gemini API key (for standard-tiered context assembly)
echo "<api-key>" > /storage/credentials/rogers/gemini_api_key.txt
```

**Data directories (on M5 before first deploy):**
```bash
mkdir -p /mnt/ssd1/workspace/rogers/databases/postgres/data
mkdir -p /mnt/ssd1/workspace/rogers/databases/neo4j/{data,logs}
mkdir -p /mnt/ssd1/workspace/rogers/databases/redis/data
```

**Offline packages (before building images):**
```bash
cd mads/rogers/rogers/packages && bash download-packages.sh
cd mads/rogers/rogers-langgraph/packages && bash download-packages.sh
```

---

## Verification

```bash
# Gateway health
curl -s http://m5:6380/health | jq .

# Container status
docker ps --filter "label=mad.logical_actor=rogers"

# Logs
docker logs rogers --tail 50
docker logs rogers-langgraph --tail 50

# Test tools directly via langgraph backend
docker exec rogers-langgraph python3 -c "
import urllib.request, json
req = urllib.request.Request('http://localhost:8000/conv_create_conversation',
  data=json.dumps({'params':{'flow_id':'test-flow','title':'Test Conversation'}}).encode(),
  headers={'Content-Type':'application/json'}, method='POST')
print(json.loads(urllib.request.urlopen(req).read()))
"

docker exec rogers-langgraph python3 -c "
import urllib.request, json
req = urllib.request.Request('http://localhost:8000/conv_get_history',
  data=json.dumps({'params':{'conversation_id':'<conversation_id>'}}).encode(),
  headers={'Content-Type':'application/json'}, method='POST')
print(json.loads(urllib.request.urlopen(req).read()))
"
```

---

## Deployment Status

**Status:** v3.1 deployed and operational
**Deployed:** 2026-02-25 (Phase 1 search quality upgrade)
**Host:** M5 (192.168.1.120)

**v3.1 changes (2026-02-25):** Phase 1 search quality. Contextual embeddings: 3-message prefix window for all conversation message embeds. Hybrid RRF retrieval: vector ANN + BM25 full-text combined via Reciprocal Rank Fusion with recency bias (top 50 candidates). Cross-encoder reranker: bge-reranker-v2-m3 via Sutherland `llm_rerank` (top 10 final results). Added `content_tsv` GIN index to postgres. All 83,588 messages re-embedded through contextual pipeline.

**v3.0 changes (2026-02-22):** Complete schema redesign (paired turns → single messages), context window architecture, three-tier context assembly, 10 client-facing MCP tools (was 12), LangGraph StateGraph flows, Quart async backend. Full pipeline verified: embedding via Sutherland, memory extraction via Sutherland/Qwen, Neo4j graph relations. Gate 3: 46 passed, 0 failed.

---

## Design Documents

- `docs/REQ-rogers.md` — delta requirements and full design
- `docs/architecture.md` — design rationale and history
- `docs/rogers-plan.md` — complete build log (design → implementation → deployment)

**References:**
- ADR-046: MAD Group (Bounded Context) pattern
- ADR-053: Bidirectional Gateway Peer Proxy
- REQ-000 §7.4.1: Network isolation
