# HLD — Conversational Core

**Version:** 3.0
**Date:** 2026-03-13
**Status:** Active
**Scope:** Henson · Rogers · Sutherland

---

## 1. Purpose and Scope

This document is the authoritative High-Level Design for the Joshua26 Conversational Core.
It defines the architecture, network boundaries, and exact interaction flows between the
three pMADs that power conversation in the ecosystem. Every Thought Engine (TE) in the
ecosystem — whether in a pMAD or an eMAD — depends on this infrastructure: Rogers for
context, Sutherland for inference, and Henson for human-facing interaction. The patterns
defined here are ecosystem-wide requirements, not implementation details of three services.

This document supersedes the Version 1.0 HLD, which described the State 1 four-MAD
architecture (including Hamilton as a standalone embedding MAD). In the Ray iteration,
Hamilton is retired and its embedding function is absorbed into Sutherland's unified
compute cluster.

The three pMADs and their single-sentence roles:

| pMAD | Canonical Role |
|---|---|
| **Henson** | The Human Switchboard — hosts UIs, manages sessions and personas, and coordinates context and compute |
| **Rogers** | The Context Broker — stores conversation history, assembles context windows, and manages the async memory pipeline |
| **Sutherland** | The Inference Broker — owns the GPU hardware pool and executes all ML inference (LLM chat, embeddings, reranking) |

---

## 2. The "One pMAD, One Domain" Principle

The conversational core is built on strict separation of concerns. Each pMAD owns exactly
one domain. The constraints below are architectural invariants, not implementation
preferences.

### 2.1 Henson — The Human Switchboard

**Role:** Henson hosts the user interfaces (Open WebUI, etc.), manages the human's
session, and resolves the active Persona. It orchestrates the interaction between the
user, the context layer (Rogers), and the inference layer (Sutherland).

**Constraints:**
- **Zero memory.** Henson does not store conversation history. It holds only the
  session-to-persona and session-to-Rogers-conversation-ID mappings needed to route
  requests to the correct Rogers and Sutherland resources.
- **Zero inference.** Henson does not execute model inference of any kind. It
  packages prompts and forwards them to Sutherland.

### 2.2 Rogers — The Context Broker

**Role:** Rogers is the universal context broker and memory engine. It manages
conversation history, engineers optimized context windows (Tier 1 summary + Tier 2
facts + recent turns), and stores vector embeddings. It manages multiple distinct
knowledge collections within its Mem0/Neo4j + pgvector hybrid store — a general
conversation store and purpose-specific collections (e.g., a coding-focused collection)
— each independently queryable. It is designed to handle complex memory pipelines
(context compression, RAG, Mem0 knowledge graphs) in the background without blocking
the chat turn.

Rogers serves the entire ecosystem, not only Henson. Any agent or process that needs
a curated context window calls Rogers. See Section 3 for the broader ecosystem role.

**Constraints:**
- **No inference.** Rogers does not execute model inference.
- **No embedding generation.** Rogers does not generate embeddings itself. All ML
  mathematical operations — including embedding vector computation — are delegated
  entirely to Sutherland.
- **No anchor package assembly.** Rogers supplies components — retrieved history,
  extracted facts, prior decisions — that orchestrators may draw on. It does not
  assemble anchor packages or task-specific context packages. That responsibility
  belongs to the agent or process that owns the task.
  See `docs/concepts/d6-the-anchor-package.md`.

### 2.3 Sutherland — The Inference Broker

**Role:** Sutherland owns and manages the ecosystem's GPU hardware pool across all
hosts: m5's V100s and P40s, Irina's Tesla P4, and J-Desktop's RTX 3050. It
executes LLM inference, text embeddings, and reranking via an OTS compute cluster
(Ray Serve + llama.cpp). A LangGraph StateGraph acts as the intelligent routing layer
in front of the OTS cluster.

A Sutherland alias is not a simple name-to-endpoint mapping. Each alias is an entry
point into a StateGraph that applies routing logic at inference time: selecting among
physical backends based on request content or load, swapping LoRA adapters, routing to
specific GPU hardware based on capability requirements, or any other dynamic adjustment.
A single stable alias represents evolving routing behaviour without requiring changes
to callers.

**Constraints:**
- **No concept of a user.** Sutherland has no awareness of UI sessions, conversation
  history, or personas. It receives an input (prompt, text, or document list), performs
  the math, and returns the output.
- **No context management.** Sutherland does not assemble, truncate, or manage
  context windows. That is Rogers' responsibility.

---

## 3. Strategic Architecture: Rogers as Ecosystem Context Broker

The conversational core serves more than human chat sessions. Rogers is the central
context broker for every Thought Engine in the Joshua26 ecosystem — any Imperator,
whether in a pMAD or an eMAD, that needs memory of past work or a curated context
window for a task, calls Rogers. Sutherland is the inference broker for every TE —
no agent calls an LLM endpoint directly.

### 3.1 Multi-Collection Knowledge Management

Rogers manages multiple distinct knowledge collections within its Mem0/Neo4j + pgvector
hybrid store. A general collection serves broad ecosystem memory. Purpose-specific
collections can be created for targeted domains (e.g., a collection with a coding-specific
knowledge orientation). Collections are independently queryable.

Rogers uses Mem0's user ID and conversation ID keying to scope retrieval: an agent can
retrieve memories focused narrowly on its own prior work (by its user ID and active
conversation), or query more broadly across the ecosystem. This gives any Rogers consumer
both focused and general memory access from the same infrastructure.

### 3.2 Dual-Mode Knowledge Access

The same knowledge stores that Rogers uses to assemble pre-run context windows can also
be exposed as searchable runtime tools via MCP. An agent does not have to choose between
receiving curated context at startup and querying memory during execution — it can have
both:

- **Pre-assembled context** — Rogers assembles an optimised context window before the
  agent begins work, delivered via `conv_retrieve_context`. This is the standard agent
  startup pattern.
- **Runtime search tools** — the same vector and graph stores are accessible as MCP
  tools the agent can call at any point during execution to retrieve specific memories,
  search prior decisions, or look up facts.

### 3.3 The Agent Context Hydration Pattern

Any agent in the Joshua26 ecosystem that maintains a Rogers conversation follows the
same startup pattern:

```
Agent starts
        │
        ▼
Ensure Rogers session
    └─ conv_create_conversation (new task) or resolve existing conversation ID
        │
        ▼
Fetch Rogers context
    └─ conv_retrieve_context → curated context window assembled by Rogers
        │
        ▼
Begin work with full memory of prior relevant history
```

This pattern applies equally to pMAD Imperators (persistent, system domain) and eMAD
Imperators (ephemeral, subject domain). Rogers' context window is what makes any
Imperator — whether newly started or long-running — immediately aware of the history
relevant to its work, without requiring that history to be retransmitted by the caller.

### 3.4 Horace — Future Filesystem Knowledge Layer

Horace is a planned pMAD that will do for the filesystem what Rogers does for
conversations. It will index files, build structured knowledge about their contents
and relationships, and provide tools to both agents and Rogers. Once deployed, Rogers
will be able to incorporate filesystem-derived knowledge into context windows —
enabling agents to receive context that includes awareness of the current state of
the codebase or storage without having to read files themselves.

Horace is not yet deployed. This section documents the intended integration point.

---

## 4. Network Topology and Trust Boundaries

Every pMAD follows the same isolation pattern. The MCP Gateway is the only container
exposed to `joshua-net`. LangGraph and all backing services are isolated on the pMAD's
private `[mad]-net`. No LangGraph container speaks directly to another pMAD's LangGraph
— all cross-pMAD calls traverse the Peer Proxy path.

### 4.1 The Public Square (`joshua-net`)

`joshua-net` is the Docker Swarm overlay network. All cross-pMAD communication happens
exclusively here. Only the MCP Gateway containers reside on this network. No backing
service (Postgres, Redis, llama.cpp workers) is ever exposed to `joshua-net`.

Two protocols traverse `joshua-net`:

- **MCP JSON-RPC over HTTP** — for discrete tool calls: context broker operations
  (Rogers), GitHub operations (Starret), eMAD management (Kaiser install/list/create),
  metrics, and all other structured request/response operations.
- **OpenAI-compatible `/v1/chat/completions`** — for conversational message exchange:
  inference (Sutherland), eMAD chat (Kaiser). This is the industry-standard protocol
  for LLM conversation. Supports streaming (SSE), multimodal content, and structured
  tool calling natively.

The choice of protocol is determined by the nature of the interaction: MCP for tool
calls, OpenAI chat completions for conversation. Both traverse the same gateway peer
proxy path (see §4.4).

### 4.2 The Private Backplanes (`[mad]-net`)

Each pMAD has its own private overlay network (`henson-net`, `rogers-net`,
`sutherland-net`). Services within a pMAD communicate freely on this private network.
No service on `[mad]-net` is reachable from another pMAD's network.

### 4.3 The Brain/Brawn Split

Inside each private network, all custom programmatic logic is executed exclusively by a
**LangGraph container**. The actual heavy lifting is done by unmodified Off-The-Shelf
(OTS) containers — Postgres, Redis, Ray Serve nodes, llama.cpp servers — sitting securely
behind LangGraph. LangGraph is the brain; OTS containers are the brawn.

### 4.4 Peer Proxying

LangGraph containers never communicate directly across pMAD boundaries. If Henson-LangGraph
needs to call Rogers, it sends the request to its own gateway's peer proxy endpoint
(`http://henson:9224/peer/rogers/...`). The Henson Gateway forwards it across `joshua-net`
to the Rogers Gateway, which routes it internally to Rogers-LangGraph. The path is always:

```
Source-LangGraph → Source-Gateway (peer proxy) → joshua-net → Target-Gateway → Target-LangGraph
```

### 4.5 Topology Diagram

```
User / Open WebUI
      │
      ▼
┌─────────────────┐
│  henson         │  (gateway, joshua-net + henson-net)
│  :9224          │
└────────┬────────┘
         │ henson-net
         ▼
┌─────────────────────┐
│  henson-langgraph   │  (LangGraph orchestrator)
└────────┬────────────┘
         │
         │ peer calls via henson gateway → joshua-net → peer gateway
         │
         ├────────────────────────────────────────────┐
         ▼                                            ▼
┌─────────────────┐                      ┌───────────────────────┐
│  rogers         │                      │  sutherland           │
│  :6380          │                      │  :11435               │
└────────┬────────┘                      └──────────┬────────────┘
         │ rogers-net                               │ sutherland-net
         ▼                                          ▼
┌─────────────────────┐           ┌────────────────────────────────┐
│ rogers-langgraph    │           │ sutherland-langgraph           │
│ rogers-postgres     │           │ OTS compute cluster:           │
│ rogers-redis        │           │   Ray Serve + llama.cpp nodes  │
└─────────────────────┘           │   m5: V100 SXM2 pair + P40s    │
                                  │   Irina: Tesla P4 (embeddings) │
                                  │   J-Desktop: RTX 3050          │
                                  └────────────────────────────────┘
```

---

## 5. The Synchronous Chat Turn (The Happy Path)

The synchronous path is everything that must complete before the user sees a response.
Henson orchestrates this as a linear LangGraph StateGraph. This phase is optimized for
minimum Time To First Token (TTFT).

Henson resolves the persona and then routes to one of two paths depending on the backend
type. Both paths speak the OpenAI chat completions protocol to their backend.

### 5.1 Sutherland Path — Direct Inference Personas

For personas backed by a Sutherland model alias. Henson orchestrates the full
conversational core: Rogers session, context retrieval, prompt assembly, and inference.

```
User message arrives at Henson gateway
        │
        ▼
[1] Intercept & Resolve
    └─ Henson-LangGraph intercepts the message from Open WebUI
    └─ Looks up the active session in henson-postgres
    └─ Resolves the active Persona and its llm_model_name
    └─ Resolves the Rogers Conversation ID and Context Window ID for this session

[2] Context Retrieval
    └─ Henson calls Rogers: conv_retrieve_context(context_window_id) via MCP
    └─ Rogers-LangGraph assembles an optimized context block:
       Tier 1 (summary) + Tier 2 (extracted facts) + recent turns
    └─ Rogers enforces the token budget; Henson blindly trusts the output
    └─ Rogers returns the formatted XML context block + token count
    └─ If Rogers unreachable: inject "[SYSTEM WARNING: Memory unreachable]"

[3] Prompt Assembly
    └─ Henson invisibly prepends the Rogers context block to the user's message:
       "{context_block}\n\n--- New Message ---\n{user_input}"
    └─ Resolve any image UUIDs: read from workspace uploads volume → base64 encode
    └─ Package with persona system prompt and generation parameters

[4] Inference Execution
    └─ Henson calls Sutherland: /v1/chat/completions (model=alias, messages=[...])
    └─ Sutherland-LangGraph resolves the model alias to a physical OTS backend
    └─ Sutherland routes the request to the Ray Serve / llama.cpp cluster
    └─ Sutherland streams tokens back through the chain to the user (SSE)
    └─ Henson forwards the stream directly to the Open WebUI client
```

### 5.2 Kaiser Path — eMAD-Hosted Personas

For personas backed by an eMAD hosted on Kaiser (e.g., Hopper). The eMAD is a fully
autonomous agent — it owns its own Rogers relationship, context retrieval, and inference.
Henson's role is limited to persona resolution, message forwarding, and conversation_id
persistence.

```
User message arrives at Henson gateway
        │
        ▼
[1] Intercept & Resolve
    └─ Henson-LangGraph intercepts the message from Open WebUI
    └─ Looks up the active session in henson-postgres
    └─ Resolves the active Persona and its peer_mad_name (e.g., "kaiser")
    └─ Looks up the conversation_id for this chat session from active_sessions
       (empty on first turn)

[2] Forward to Kaiser
    └─ Henson extracts the last user message (including multimodal content parts)
    └─ Henson calls Kaiser: /v1/chat/completions
       (model=emad_name, messages=[last_user], conversation_id, stream=true)
    └─ conversation_id is an ecosystem extension to the OpenAI protocol for
       Rogers session continuity (see §5.5)

[3] eMAD Execution (inside Kaiser)
    └─ Kaiser resolves the eMAD by name, invokes its StateGraph
    └─ The eMAD manages its own Rogers lifecycle:
       - Creates Rogers conversation + context window on first turn
         (with its own build type and token budget)
       - Fetches Rogers context on subsequent turns (full conversation history)
    └─ The eMAD calls Sutherland for inference via /v1/chat/completions
    └─ The eMAD may call tools, loop back to Sutherland, etc.

[4] Response
    └─ Kaiser streams the response back to Henson (OpenAI SSE format)
    └─ Henson forwards the stream directly to the Open WebUI client
    └─ Henson stores the conversation_id from the response in active_sessions
       for the next turn
    └─ The eMAD writes user + assistant messages to Rogers in the background
       (non-blocking — simultaneous with streaming the response)
```

### 5.3 Context injection rationale (Sutherland path)

Henson uses **Deterministic Context Prepending**: the Rogers context block is blindly
prepended to the user message before sending to Sutherland. This is a deliberate
architectural choice:

- **Local model compatibility** — works regardless of whether the model supports
  system prompts or tool-calling
- **Recency bias** — the user's question immediately follows the context, leveraging
  LLM attention to the most recent tokens
- **Low TTFT** — single inference call with no tool-calling round-trips
- **Deterministic** — Henson performs no context reasoning; Rogers performs all
  token-aware assembly upstream

### 5.4 Persona → backend resolution

Henson stores persona configurations in `henson-postgres`. Each persona has a
`routing_type` that determines which path is taken:

- **`routing_type: "sutherland"`** (default) — `llm_model_name` is a Sutherland alias.
  Sutherland resolves that alias via its LangGraph routing StateGraph. The two-level
  indirection means changing which model serves a persona requires only a database
  update — no code deployment.
- **`routing_type: "peer_mad"`** — `peer_mad_name` identifies the backend pMAD (e.g.,
  "kaiser"), and `llm_model_name` identifies the eMAD within it.
  Henson forwards to the peer pMAD's `/v1/chat/completions` endpoint.

```
Sutherland path:
  Henson persona:    [persona-name]    →  llm_model_name: "[sutherland-alias]"
  Sutherland alias:  "[sutherland-alias]"  →  StateGraph routing → physical OTS backend

Kaiser path:
  Henson persona:    [persona-name]    →  peer_mad_name: "kaiser", llm_model_name: "[emad-name]"
  Kaiser endpoint:   /v1/chat/completions (model="[emad-name]")  →  eMAD StateGraph
```

### 5.5 conversation_id — Rogers session continuity extension

The OpenAI chat completions protocol is stateless — the client sends the full message
history each time. For the Joshua26 ecosystem, Rogers provides persistent conversation
memory that survives across sessions and enables context engineering (tiered summaries,
knowledge extraction, semantic search).

To bridge the stateless protocol with Rogers' stateful context, the ecosystem adds a
`conversation_id` field to the OpenAI chat completions request and response body. This
is the ecosystem's standard extension to the protocol:

- **Request:** An optional `conversation_id` field in the request body. If present, the
  backend uses it to look up an existing Rogers session. If empty or absent, the backend
  creates a new Rogers conversation.
- **Response:** The `conversation_id` field in the response body. The caller persists
  this and passes it back on subsequent turns for session continuity.

For Sutherland-path personas, Henson manages the Rogers session directly (§5.1 steps
1–2). For Kaiser-path personas, the eMAD manages its own Rogers session and Henson
simply persists the conversation_id between turns (§5.2 steps 1, 4).

---

## 6. The Asynchronous Memory Pipeline

Memory processing is fully decoupled from the chat turn. It must not block the UI.
The pipeline is triggered after the user has received their complete response.

### 6.1 Step-by-step sequence

```
User receives completed response
        │
        ▼
[1] Storage Trigger
    └─ Henson sends the final turn to Rogers:
         conv_store_message(role=user, content=user_input)
         conv_store_message(role=assistant, content=generated_response)
    └─ Rogers writes both messages to rogers-postgres and returns immediately
    └─ Rogers enqueues background jobs to rogers-redis

[2] Embedding Generation (async background)
    └─ Rogers background worker dequeues the embedding job
    └─ Rogers calls Sutherland: llm_embeddings(text=content) via MCP
    └─ Sutherland routes the request to the embedding model (Tesla P4 on Irina)
    └─ Sutherland returns the 768-dim float vector

[3] Vector Storage
    └─ Rogers saves the embedding vector to rogers-postgres (pgvector extension)
    └─ Vector is available for future semantic search during context retrieval
```

### 6.2 Additional background jobs

Rogers' queue worker processes two additional job types beyond embeddings:

| Job type | What it does |
|---|---|
| `context_assembly_jobs` | Recomputes context window token counts; truncates oldest turns if over budget |
| `memory_extraction_jobs` | Calls Sutherland `llm_chat_completions` with an extraction prompt; LLM extracts facts and entities; Rogers updates the Mem0 knowledge graph |

### 6.3 Memory pipeline latency targets

The async pipeline does not block the UI. However, it must complete before the next user
message to ensure memory is current.

| Pipeline stage | Expected latency |
|---|---|
| Rogers message write (sync) | < 50ms |
| Sutherland embedding (Tesla P4) | < 200ms per chunk |
| Mem0 LLM extraction (via Sutherland) | 5–15s |
| Context assembly / truncation | < 100ms |
| **Full pipeline completion target** | **< 30s from turn completion** |

---

## 7. Sutherland (Ray Iteration) Capabilities

Sutherland's Ray iteration is designed to guarantee inference performance under production load.
Three invariants are baked into every backend deployment.

### 7.1 No Eviction — Sovereign Model Pinning

Sovereign models (e.g., the 72B anchor model spanning the NVLink-connected V100 pair on
m5) are pinned permanently in VRAM by the OTS orchestrator. `OLLAMA_KEEP_ALIVE` is set
to `-1` on all applicable instances. No eviction policy is active for production models.

**Rationale:** Cold model load from disk takes 15–45 seconds — an unacceptable latency
spike that would degrade TTFT from `< 3s` to `> 15s` for all personas sharing that model
instance. Sovereign models must be available instantly, at all times.

### 7.2 Hard-Fail on CPU Spill

Sutherland explicitly prohibits silent CPU offloading. If a model's VRAM requirement
exceeds what is physically available on the assigned GPU, the orchestrator kills the
process rather than silently spilling layers to system RAM.

**Rationale:** CPU inference is 10–100x slower than GPU inference. Silent CPU spill
produces a system that appears healthy but is delivering catastrophically poor
performance with no external signal. Hard-failing ensures the system degrades loudly
and visibly rather than silently and acceptably.

### 7.3 Heterogeneous Slicing

The cluster allocates smaller hardware (P40s) among utility models (e.g., the 7B agent
model, the reranker) using fractional GPU slicing. The V100s are reserved for
sovereign (large) models; the P40s serve multiple utility models concurrently via
GPU slices; the P4 on Irina serves the embedding model; the RTX 3050 on J-Desktop
provides auxiliary burst capacity.

| Node | Hardware | Assigned role |
|---|---|---|
| m5 | 2x V100 SXM2 NVLink (32GB each) | Sovereign LLMs (e.g., 72B models via NVLink span) |
| m5 | 1x V100 PCIe (16GB) | Mid-size LLMs |
| m5 | 3x P40 (24GB each) | Utility models (7B agents, reranker) via slicing |
| Irina | Tesla P4 (8GB) | Embedding model (text → 768-dim vectors) |
| J-Desktop | RTX 3050 (8GB) | Auxiliary burst / smaller utility models |

---

## 8. Failure Modes and Graceful Degradation

| Failure | Henson behaviour | User impact |
|---|---|---|
| Rogers unreachable | Injects `[SYSTEM WARNING: Memory unreachable]`; continues with inference | No memory context; model still responds |
| Rogers slow (timeout) | Same as unreachable | Same |
| Sutherland unreachable | Returns `[SYSTEM ERROR: Compute backend unreachable]` | No response; clear error displayed |
| Sutherland embedding fails | Rogers embedding queue backs up; chat unaffected | Memory embeddings lag; chat continues normally |
| Mem0 extraction fails | Logged; extraction skipped for this turn | Knowledge graph not updated; chat unaffected |

**Design principle:** Henson must always produce an LLM response if Sutherland is
reachable, regardless of the state of Rogers. Memory subsystem failures are degraded,
not catastrophic.

---

## 9. Latency Budgets — Synchronous Path

Only Phase 1 is visible to the user. Phase 2 runs in the background.

### Phase 1 — Synchronous (user waits for first token)

| Step | Budget |
|---|---|
| Henson routing and persona load | < 50ms |
| Rogers context retrieval | < 150ms |
| Payload assembly (incl. image base64) | < 100ms |
| **Sutherland TTFT — cloud models (GPT-4o, Gemini)** | **500ms – 1.2s** |
| **Sutherland TTFT — local models, warm (V100/P40)** | **< 3s** |
| Sutherland TTFT — local models, cold (loading from disk) | 15–45s (unacceptable; see §7.1) |
| **Total TTFT target (warm local model)** | **< 4s** |
| **Total TTFT target (cloud model)** | **< 2s** |

### Phase 2 — Async (invisible to user)

| Stage | Budget |
|---|---|
| Rogers message write | < 50ms |
| Full memory pipeline completion | < 30s |

---

## 10. Data Ownership

| Data | Owner | Storage |
|---|---|---|
| Session → persona mapping | Henson | henson-postgres: active_sessions |
| Persona definitions | Henson | henson-postgres: personas |
| Rogers session IDs (conversation + context window) | Henson | henson-postgres: active_sessions |
| Conversation message history | Rogers | rogers-postgres: conversation_messages |
| Context window state + token counts | Rogers | rogers-postgres: context_windows |
| Message embeddings (pgvector) | Rogers | rogers-postgres |
| Mem0 knowledge graph | Rogers | rogers-postgres (mem0 tables) |
| Background job queues | Rogers | rogers-redis |
| Model alias registry | Sutherland | sutherland-postgres: model_aliases |
| UI file uploads | Shared volume | /workspace/henson/ui_data/uploads/ |

---

## 11. Related Documents

- `docs/designs/HLD-Joshua26-system-overview.md` — system-wide architecture and core concepts
- `docs/designs/HLD-joshua26-agent-architecture.md` — agent classes, TE anatomy, Rogers/Sutherland dependency pattern
- `docs/designs/HLD-state3-mad.md` — AE/TE separation, dynamic StateGraph loading
- `docs/designs/HLD-MAD-container-composition.md` — pMAD container architecture pattern
- `docs/concepts/a2-conversation-as-state.md` — conversation as the substrate of state
- `docs/concepts/c1-the-context-broker.md` — The Context Broker concept (Rogers' conceptual basis)
- `docs/concepts/d6-the-anchor-package.md` — Anchor Package concept
- `docs/concepts/c2-the-inference-broker.md` — Inference Broker concept (Sutherland's conceptual basis)
- `mads/henson/docs/REQ-henson.md` — Henson requirements
- `mads/rogers/docs/REQ-rogers.md` — Rogers requirements
- `mads/sutherland/docs/REQ-sutherland.md` — Sutherland (Ray iteration) requirements
