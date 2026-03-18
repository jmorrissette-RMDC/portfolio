# REQ-sutherland — Sutherland (Ray Iteration)

**Version:** 2.0
**Date:** 2026-02-28
**Status:** Draft
**Supersedes:** REQ-sutherland v1.0 (llamacpp/vllm iteration)

This is a delta REQ. The baseline MAD pattern (gateway, LangGraph, health checks,
logging, MCP protocol, container structure, networking) is defined in
`mads/_template/docs/REQ-langgraph-template.md`. This document specifies only what
differs from or extends that baseline.

---

## §1. Purpose and Scope

Sutherland is the AI compute platform for the Joshua26 ecosystem. Every MAD that
requires AI computation — LLM inference, text embedding, or reranking — calls
Sutherland. Sutherland owns the hardware, manages the workloads, and exposes three
clean, targeted MCP tools.

**Ray iteration changes from previous (llamacpp/vllm):**

| Change | Previous (llamacpp/vllm) | Current (Ray) |
|---|---|---|
| Inference layer | Static `docker-compose` containers per model (ollama, vllm) | Ray Serve cluster with `llama-cpp-python` deployments |
| Hardware orchestration | Individual docker containers per GPU | Ray Head + Ray Workers spanning m5, Irina, J-Desktop |
| Embedding tools | Not present (delegated to Hamilton MAD) | `llm_embeddings` tool (Hamilton retired, absorbed) |
| Backend URLs in alias registry | Docker container hostnames | Internal Ray Serve HTTP endpoints (`http://sutherland-ray-head:8000/...`) |

---

## §2. Registry Allocation

| Field | Value |
|---|---|
| Name | sutherland |
| UID | 2007 |
| GID | 2001 (administrators) |
| Port | 11435 |
| Host | m5 (192.168.1.120) |
| GPU | 2x V100 SXM2 NVLink (32GB ea), 1x V100 PCIe (16GB), 3x P40 (24GB ea) |

**Hamilton retirement:** Hamilton (UID 2015, port 6335, host irina) is retired in
the Ray iteration. Its embedding function and the Tesla P4 GPU worker on Irina move under
Sutherland's management as a Ray Worker node.

---

## §3. MCP Tools

Sutherland exposes four MCP tools: three for inference/embedding/rerank and one for observability.

### §3.1 `llm_chat_completions`

Unified LLM inference across local GPU models and cloud APIs via model alias.
Supports both streaming (SSE) and non-streaming response modes, and supports vision
(multimodal) payloads in the messages array.

**Input schema:**
```json
{
  "model":       { "type": "string",  "required": true,  "description": "Model alias (e.g. imperator-gunner, imperator-grace)" },
  "messages":    { "type": "array",   "required": true,  "description": "OpenAI-compatible messages array, including vision content blocks" },
  "stream":      { "type": "boolean", "required": false, "default": false },
  "max_tokens":  { "type": "integer", "required": false },
  "temperature": { "type": "number",  "required": false }
}
```

**Output:** OpenAI-compatible chat completion response (non-streaming), or SSE stream
of OpenAI-compatible chunks terminated with `data: [DONE]` (streaming).

**Flow:** `alias_resolution_flow` (AE) — alias lookup → backend dispatch → response.

---

### §3.2 `llm_embeddings`

Converts text to dense 768-dimensional embedding vectors via the m2-bert embedding
model on the Tesla P4 (Irina). Absorbed from the retired Hamilton MAD. Accepts either
a single string or a batch of strings in a single call.

**Input schema:**
```json
{
  "input": {
    "type": "string | array[string]",
    "required": true,
    "description": "Single text string, or array of strings (max 32 items per batch)"
  }
}
```

**Output (single string input):**
```json
{
  "embedding":  [768 floats],
  "dimension":  768,
  "tokens":     123
}
```

**Output (array input):**
```json
{
  "embeddings":   [[768 floats], ...],
  "dimension":    768,
  "count":        2,
  "tokens":       [50, 73],
  "total_tokens": 123
}
```

**Flow:** AE (deterministic) — routes to Ray Serve embedding deployment on Irina P4.
Synchronous (no streaming).

---

### §3.3 `llm_rerank`

Scores a list of documents against a query and returns them ranked by relevance.
Powered by bge-reranker-v2-m3 on the P40 pool.

**Input schema:**
```json
{
  "query":     { "type": "string",  "required": true,  "description": "The search query or reference sentence" },
  "documents": { "type": "array",   "required": true,  "description": "Array of strings to score against the query" },
  "top_n":     { "type": "integer", "required": false, "description": "Return only the top N documents by score" }
}
```

**Output:**
```json
{
  "results": [
    { "index": 2, "document": "...", "score": 0.97 },
    { "index": 0, "document": "...", "score": 0.43 }
  ]
}
```

**Flow:** AE (deterministic) — routes to Ray Serve reranker deployment on P40 pool.
Synchronous (no streaming).

---

### §3.4 `metrics_get`

Returns Prometheus exposition-format metrics for this MAD. Used by Apgar's metrics scraper via the Apgar gateway peer proxy (`/peer/sutherland/metrics_get`). Enables ecosystem observability (see `docs/guides/mad-prometheus-metrics-guide.md`).

**Input schema:** `{}` (no arguments).

**Output:** JSON `{ "metrics": "# HELP ...\n# TYPE ...\n..." }` — the `metrics` value is Prometheus text format. The gateway forwards this tool to `sutherland-langgraph:8000/metrics_get`, which returns the same content as `GET /metrics` on the langgraph container.

**Flow:** Gateway forwards to langgraph. The langgraph **MUST** implement metrics via a StateGraph (per REQ-000 §4.7, §4.11): the `/metrics_get` (and `GET /metrics`) route(s) only build state and invoke a compiled metrics graph (e.g. `_metrics_graph.ainvoke(state)`); a **node** inside that graph calls `prometheus_client.generate_latest(REGISTRY)` and returns the metrics text. Do not implement as direct Quart route handlers that call `generate_latest` in the route — that bypasses LangGraph and is an architectural violation.

---

## §4. Architecture

### §4.1 Container Group (MAD containers — docker-compose, m5)

These four containers form the core Sutherland MAD and run on m5 under docker-compose,
on `sutherland-net`.

| Container | Image | Host | Network | Purpose |
|---|---|---|---|---|
| `sutherland` | Custom (Node.js gateway) | m5 | joshua-net + sutherland-net | MCP gateway; sole cross-MAD network boundary |
| `sutherland-langgraph` | Custom (Python/Quart) | m5 | sutherland-net | Alias resolution, request routing, LangGraph flows |
| `sutherland-postgres` | postgres:16-alpine | m5 | sutherland-net | Model alias registry |
| `sutherland-ray-head` | rayproject/ray:latest-gpu | m5 | sutherland-net | Ray cluster head; hosts Ray Serve HTTP server |

### §4.2 Ray Cluster (inference layer — Ray managed)

The Ray cluster replaces State 1's static inference containers. It consists of:

- **Ray Head (`sutherland-ray-head`):** Runs on m5, connected to `sutherland-net`.
  Hosts the Ray Serve HTTP API (`http://sutherland-ray-head:8000`). All
  `sutherland-langgraph` inference calls target this endpoint.
- **Ray Workers:** Processes on m5, Irina, and J-Desktop that join the cluster via
  the Ray Head's LAN IP (`192.168.1.120`). Ray manages their lifecycle; hardware
  is partitioned by `accelerator_type` resource labels at registration.

Ray Serve deployments are declared as `@serve.deployment` classes backed by
`llama-cpp-python` (`Llama` class) for GGUF models, and the HuggingFace
`text-embeddings-inference` HTTP server for the embedding model.

**Ray Worker hardware topology:**

| Worker Node | Host | GPU | VRAM | Ray resource label |
|---|---|---|---|---|
| m5 (V100 pool) | m5 (192.168.1.120) | 2x V100 SXM2 NVLink + 1x V100 PCIe | 80GB (64GB NVLink + 16GB PCIe) | `accelerator_type:V100` |
| m5 (P40 pool) | m5 (192.168.1.120) | 3x P40 | 72GB | `accelerator_type:P40` |
| irina | irina (192.168.1.110) | Tesla P4 | 8GB | `accelerator_type:P4` |
| j-desktop | j-desktop (192.168.1.250) | RTX 3050 | 8GB | `accelerator_type:RTX3050` |

**Ray Serve deployment assignments:**

| Deployment | Accelerator | Ray num_gpus | Model / Service |
|---|---|---|---|
| `ImperatorDeployment` | V100 (NVLink pair) | 2.0 | Qwen2.5-VL-72B (GGUF Q3_K_S) — spans NVLink pair |
| `AgentSmallDeployment` | P40 (fractional) | 0.33 | Qwen2.5-7B (GGUF Q8_0) |
| `RerankerDeployment` | P40 (fractional) | 0.05 | bge-reranker-v2-m3 |
| `EmbeddingDeployment` | P4 (Irina) | 1.0 | m2-bert-80M-32k-retrieval via TEI |
| Ephemeral Ray Jobs | RTX 3050 (J-Desktop) | 1.0 | Ad-hoc compute tasks (FFMPEG, etc.) |

### §4.3 Performance Invariants

These are non-negotiable architectural invariants baked into every Ray deployment.

#### Invariant 1: No Eviction — Sovereign Model Pinning

All production Ray Serve deployments are configured with `min_replicas=1`. The Ray
Serve autoscaler is disabled or set to a minimum floor of 1 for all inference
deployments. Replicas are never scaled to zero.

```python
@serve.deployment(
    name="ImperatorDeployment",
    num_replicas=1,
    ray_actor_options={"num_gpus": 2.0, "resources": {"accelerator_type:V100": 0.01}},
    autoscaling_config={"min_replicas": 1, "max_replicas": 1}  # pinned, no scaling
)
class ImperatorDeployment:
    ...
```

**Rationale:** Cold model load from disk takes 60–120 seconds for a 72B model.
This is not an acceptable operating condition. Sovereign models must be available
instantly at all times.

#### Invariant 2: Hard-Fail on CPU Spill

Silent CPU offloading is strictly prohibited. `llama-cpp-python` must be initialized
with `n_gpu_layers=-1` (all layers on GPU). Ray worker containers must run with
Docker memory limits sized to the host's GPU VRAM. If a model exceeds VRAM and
attempts to spill layers to system RAM, the Linux OOM killer will terminate the
Ray worker process, producing a loud, visible error rather than silent performance
degradation.

```python
# REQUIRED initialization in every llama-cpp-python deployment
self.llm = Llama(
    model_path=model_path,
    n_gpu_layers=-1,      # ALL layers on GPU — no CPU fallback
    n_ctx=context_size,
    ...
)
```

**Rationale:** CPU inference is 10–100x slower than GPU inference. A system that
silently spills to CPU appears healthy while delivering catastrophically poor TTFT
with no external signal. Hard-failing makes degradation loud and immediately
actionable.

#### Invariant 3: Heterogeneous Slicing

Smaller GPUs (P40s) serve multiple utility models concurrently via Ray's fractional
GPU resource allocation. Each Ray Serve deployment requests a fraction of a GPU
(`num_gpus=0.33`, `num_gpus=0.05`), allowing multiple deployments to share the P40
pool without physical partitioning.

---

## §5. Alias Registry

### §5.1 Schema

`sutherland-postgres` table `model_aliases`:

```sql
CREATE TABLE model_aliases (
    alias          VARCHAR(100) PRIMARY KEY,
    backend_type   VARCHAR(20)  NOT NULL CHECK (
                     backend_type IN (
                       'local_ray',    -- Ray Serve deployment on sutherland-ray-head
                       'openai',
                       'gemini'
                     )
                   ),
    backend_url    VARCHAR(500),          -- Ray Serve endpoint for local; null for cloud
    model_name     VARCHAR(200),          -- Ray deployment name or cloud model ID
    api_key_file   VARCHAR(500),          -- Path to credentials file (cloud only)
    active         BOOLEAN DEFAULT true,
    created_at     TIMESTAMPTZ DEFAULT NOW()
);
```

**LoRA routing (future capability):** The schema supports an optional `lora_adapter`
column (VARCHAR) to enable dynamic LoRA routing — routing different aliases to the
same base model deployment with different adapter weights loaded at inference time.
This is noted as a planned capability; implementation follows when LoRA adapters
are introduced to the model inventory.

### §5.2 Ray Iteration Seed Data

| Alias | Backend Type | URL | Model / Deployment |
|---|---|---|---|
| `imperator-gunner` | local_ray | `http://sutherland-ray-head:8000/imperator` | ImperatorDeployment |
| `agent-small` | local_ray | `http://sutherland-ray-head:8000/agent-small` | AgentSmallDeployment |
| `bge-reranker-v2-m3` | local_ray | `http://sutherland-ray-head:8000/reranker` | RerankerDeployment |
| `embed-default` | local_ray | `http://sutherland-ray-head:8000/embedding` | EmbeddingDeployment |
| `imperator-grace` | gemini | null | gemini-2.5-pro |
| `imperator-henson` | openai | null | gpt-4o |

---

## §6. LangGraph Flows and Routes

### §6.1 `alias_resolution_flow` — chat completions

**AE (deterministic) StateGraph:** `resolve_alias → execute_inference → END`

**State schema:**
```python
class InferenceState(TypedDict):
    messages:           list
    model:              str
    temperature:        float
    max_tokens:         int
    generation_params:  dict
    alias_row:          Optional[dict]
    generated_response: str
    error_state:        Optional[str]
```

**`_node_resolve_alias`:**
```sql
SELECT alias, backend_type, backend_url, model_name, api_key_file
FROM model_aliases WHERE alias = $1 AND active = true
```
On miss: set `error_state = f"Unknown model alias: {model}"`.

**`_node_execute_inference`:**
- `local_ray`: `httpx.AsyncClient(timeout=120.0)` POST to `backend_url` (Ray Serve
  HTTP). OpenAI-compatible `/v1/chat/completions` endpoint on the Ray deployment.
- `openai`: LangChain `ChatOpenAI(model=model_name, api_key=read_credential(api_key_file))`
- `gemini`: LangChain `ChatGoogleGenerativeAI(model=model_name, api_key=...)`

**Streaming:** Quart SSE response; LangGraph `astream_events`; filter
`on_chat_model_stream`; yield OpenAI SSE chunks; terminate with `[DONE]`.

### §6.2 Embedding and Rerank Routes

Embedding and rerank requests are deterministic pass-throughs with no branching logic.
They do not require a StateGraph. Implemented as direct Quart route handlers.

**`POST /llm_embeddings`:**
```
1. Unwrap routing-lib payload: params = body.get("params", body)
2. Look up "embed-default" alias → get backend_url from model_aliases
3. Determine if params["input"] is a string or list
4. httpx.AsyncClient(timeout=60.0) POST to f"{backend_url}"
   with {"input": params["input"]}  (Ray Serve embedding deployment handles both)
5. Map response to single {embedding, dimension, tokens} or
   batch {embeddings, dimension, count, tokens, total_tokens}
```

**`POST /llm_rerank`:**
```
1. Unwrap routing-lib payload: params = body.get("params", body)
2. Look up "bge-reranker-v2-m3" alias → get backend_url
3. httpx.AsyncClient(timeout=30.0) POST to f"{backend_url}"
   with {"query": params["query"], "documents": params["documents"]}
4. Apply top_n filter if present; return ranked results
```

### §6.3 Health Route

`GET /health` checks:
- `sutherland-postgres`: critical — 503 if unreachable
- `http://sutherland-ray-head:8000/-/healthz`: soft — logs degraded if unreachable
- Individual Ray deployment readiness (via Ray Serve status API): soft per deployment

Individual deployment failures degrade specific aliases but do not fail the overall
health check.

---

## §7. config.json

```json
{
  "name": "sutherland",
  "port": 11435,
  "tools": {
    "llm_chat_completions": {
      "description": "Unified LLM inference across local GPU models and cloud APIs via model alias",
      "target": "sutherland-langgraph:8000",
      "endpoint": "/v1/chat/completions",
      "schema": {
        "input": {
          "model":       { "type": "string",  "required": true },
          "messages":    { "type": "array",   "required": true },
          "stream":      { "type": "boolean", "required": false },
          "max_tokens":  { "type": "integer", "required": false },
          "temperature": { "type": "number",  "required": false }
        }
      }
    },
    "llm_embeddings": {
      "description": "Convert text to 768-dim embedding vectors (single or batch)",
      "target": "sutherland-langgraph:8000",
      "endpoint": "/llm_embeddings",
      "schema": {
        "input": {
          "input": { "type": "string | array[string]", "required": true }
        }
      }
    },
    "llm_rerank": {
      "description": "Rerank documents against a query using bge-reranker-v2-m3",
      "target": "sutherland-langgraph:8000",
      "endpoint": "/llm_rerank",
      "schema": {
        "input": {
          "query":     { "type": "string",  "required": true },
          "documents": { "type": "array",   "required": true },
          "top_n":     { "type": "integer", "required": false }
        }
      }
    }
  },
  "dependencies": [
    {
      "name": "langgraph",
      "host": "sutherland-langgraph",
      "port": 8000,
      "type": "http",
      "critical": true,
      "endpoint": "/health"
    },
    {
      "name": "postgres",
      "host": "sutherland-postgres",
      "port": 5432,
      "type": "postgres",
      "critical": true,
      "database": "sutherland",
      "user": "sutherland",
      "credentials_file": "/storage/credentials/sutherland/postgres.txt"
    },
    {
      "name": "ray-head",
      "host": "sutherland-ray-head",
      "port": 8000,
      "type": "http",
      "critical": false,
      "endpoint": "/-/healthz"
    }
  ],
  "logging": {
    "level": "INFO"
  },
  "routing": {
    "timeout": 240000
  }
}
```

**Routing timeout:** 240,000 ms. GPT-4o (`imperator-henson`) through the full
Henson pipeline can exceed 120s on long responses. 240s provides adequate headroom.

---

### §7.5 Prometheus Metrics

Sutherland exposes `/metrics` per [mad-prometheus-metrics-guide.md](../../guides/mad-prometheus-metrics-guide.md).

**Gateway (`sutherland`):** Standard metrics only. The Node.js gateway uses `prom-client` (or equivalent) to expose `mcp_requests_total`, `mcp_request_duration_seconds`, `mcp_requests_errors_total` with labels `mad=sutherland`, `tool`, `status`, `error_type`. Endpoint: `GET http://sutherland:11435/metrics`.

**MCP tool `metrics_get`:** Required for cross-network collection (joshua-net is MCP-only). Apgar calls `POST /peer/sutherland/metrics_get` via its gateway; that proxies to `tools/call` on this gateway. **Schema:** Input: `{}` (no args). Output: `{ "content": [ { "type": "text", "text": "<Prometheus exposition format>" } ] }` — the `text` value is identical to `GET /metrics` response. **Implementation:** Register `metrics_get` in config.json; handler invokes `registry.metrics()` (or equivalent) and returns the string. Same data source as the `/metrics` route — prom-client accumulates counters/histograms from request instrumentation.

**LangGraph (`sutherland-langgraph`):** Metrics **MUST** be produced inside a StateGraph (REQ-000 §4.7, §4.11). The `GET /metrics` and `POST /metrics_get` endpoints must be thin transport: build state, call a compiled metrics graph (e.g. `_metrics_graph.ainvoke(state)`), return the graph output. A node in that graph performs metrics generation (e.g. `prometheus_client.generate_latest(REGISTRY)`). Do not implement as direct route handlers that call `generate_latest` in the route. Standard metrics plus Sutherland-specific:
- `llm_inference_requests_total` — Counter, labels: `mad=sutherland`, `tool` (llm_chat_completions, llm_embeddings, llm_rerank), `model_alias`, `status`
- `llm_inference_duration_seconds` — Histogram, labels: `mad=sutherland`, `model_alias`; buckets: 0.1, 0.5, 1, 2, 5, 30, 120
- `llm_inference_tokens_total` — Counter, labels: `mad=sutherland`, `model_alias`, `direction` (input|output)

**Ray Serve (`sutherland-ray-head`):** Ray exposes `/metrics` by default. Ensure deployment names (imperator, agent-small, reranker, embedding) appear in metric labels for deployment-level visibility. No Sutherland-specific changes required if Ray's default metrics suffice; otherwise add a custom metrics endpoint.

---

## §8. Performance Requirements

### §8.1 GPU Utilisation (mandatory — no exceptions)

- All model layers must load 100% on GPU. CPU offload is strictly prohibited.
- `llama-cpp-python` must be initialized with `n_gpu_layers=-1` on all deployments.
- Ray Serve deployments must be configured with `min_replicas=1`. No scale-to-zero.
- Docker resource limits on Ray worker containers must be sized to prevent system RAM
  from absorbing GPU overflow. OOMKill is the intended failure mode.

### §8.2 Context Windows

- `ImperatorDeployment` (Qwen2.5-VL-72B): `n_ctx=69632` — verified maximum for
  100% GPU loading across the NVLink V100 pair.
- `AgentSmallDeployment` (Qwen2.5-7B): `n_ctx=131072` — maximum for P40 pool.
- Context window values must be verified post-deployment by confirming no CPU layer
  offload in `llama-cpp-python` verbose output.

### §8.3 Latency Budgets (warm model)

| Operation | Target |
|---|---|
| Time to first token — local model (warm, V100) | < 3 seconds |
| Time to first token — cloud model (OpenAI/Gemini) | < 2 seconds |
| Embedding — single text or small batch | < 200ms |
| Rerank — 10 documents | < 2 seconds |
| Alias registry lookup (Postgres) | < 10ms |

---

## §9. Verification

### §9.1 `llm_chat_completions`

| Test | Input | Expected |
|---|---|---|
| Happy path — local | `model: imperator-gunner, messages: [{role: user, content: "Say hello"}]` | Non-empty response, quality check |
| Happy path — cloud | `model: imperator-grace, messages: [...]` | Non-empty response |
| Streaming | `model: imperator-gunner, stream: true` | SSE chunks with `data:` prefix; terminates with `data: [DONE]` |
| Invalid alias | `model: nonexistent` | Structured error response, not HTTP 500 |
| Vision — local | `messages` array with base64 image content block; `model: imperator-gunner` | Response describing image content |
| `max_tokens` respected | `max_tokens: 30` | Response ≤ 30 tokens |
| Temperature=0 determinism | Two calls: `temperature: 0, messages: [{content: "What is 2+2?"}]` | Both return "4" |

### §9.2 `llm_embeddings`

| Test | Input | Expected |
|---|---|---|
| Single string | `input: "Hello world"` | `embedding` array of 768 floats; `dimension: 768` |
| Batch | `input: ["a", "b", "c"]` | `embeddings` array with 3 subarrays; `count: 3` |
| Long text | Single 32000-char string | Successful embedding; no truncation error |
| Empty string | `input: ""` | Structured error |
| Max batch | 32 strings | All 32 embeddings returned |
| Over-limit batch | 33 strings | Structured error |

### §9.3 `llm_rerank`

| Test | Input | Expected |
|---|---|---|
| Happy path | `query: "machine learning", documents: ["ML is...", "Cats are...", "Neural nets..."]` | Ranked list with scores; ML documents rank higher |
| `top_n` respected | `top_n: 1` | Exactly 1 document in results |
| Score ordering | Mixed relevant/irrelevant docs | Relevant docs score > 0.5; irrelevant < 0.3 |

### §9.4 GPU and Model Verification (post-deployment)

```bash
# Verify ImperatorDeployment loads all layers on V100 — run once after deploy
# Check llama-cpp-python verbose output in Ray worker logs for:
# "llm_load_tensors: offloaded N/N layers to GPU"  (N/N, not partial)

# Verify VRAM footprint on m5
nvidia-smi
# V100 SXM2 pair should show ~34GB combined; PCIe V100 idle; P40s show agent-small usage

# Verify model persistence (no eviction after idle)
# Wait 10 minutes, then confirm Ray Serve deployments are still RUNNING:
ray status  # on m5 Ray head node — all deployments should show RUNNING
```

### §9.5 Health Check

```
GET http://192.168.1.120:11435/health  →  200
```

Response must include dependency status for postgres and ray-head. Individual Ray
deployment failures produce degraded status (not 503).

---

## §10. Consumer Impact

### §10.1 Henson

No change. Henson calls `llm_chat_completions` via peer proxy — interface unchanged.

### §10.2 Rogers

Rogers currently calls Hamilton for embeddings. The Ray iteration requires the following
Rogers-side configuration updates:

- `mads/rogers/rogers/config.json` peers: remove `hamilton`; ensure `sutherland`
  is listed.
- Rogers LangGraph embed tool calls: update from `hamilton/embed_text` to
  `sutherland/llm_embeddings`.
- Peer routing timeout for embedding calls: must accommodate TEI latency (< 500ms).

---

## §11. Ray Deployment Specifications

### §11.1 ImperatorDeployment (m5, V100 NVLink pair)

```python
@serve.deployment(
    name="ImperatorDeployment",
    num_replicas=1,
    ray_actor_options={
        "num_gpus": 2.0,
        "resources": {"accelerator_type:V100": 0.01}
    },
    autoscaling_config={"min_replicas": 1, "max_replicas": 1}
)
class ImperatorDeployment:
    def __init__(self):
        self.llm = Llama(
            model_path="/workspace/sutherland/models/qwen2.5-vl-72b.Q3_K_S.gguf",
            n_gpu_layers=-1,      # all layers on GPU, no CPU fallback
            n_ctx=69632,
            tensor_split=[0.5, 0.5],  # split across NVLink pair
        )
```

Model path: `/workspace/sutherland/models/qwen2.5-vl-72b.Q3_K_S.gguf` (m5 local)

### §11.2 AgentSmallDeployment (m5, P40 pool — fractional)

```python
@serve.deployment(
    name="AgentSmallDeployment",
    num_replicas=1,
    ray_actor_options={
        "num_gpus": 0.33,
        "resources": {"accelerator_type:P40": 0.01}
    },
    autoscaling_config={"min_replicas": 1, "max_replicas": 1}
)
class AgentSmallDeployment:
    def __init__(self):
        self.llm = Llama(
            model_path="/workspace/sutherland/models/qwen2.5-7b.Q8_0.gguf",
            n_gpu_layers=-1,
            n_ctx=131072,
        )
```

### §11.3 RerankerDeployment (m5, P40 pool — fractional)

```python
@serve.deployment(
    name="RerankerDeployment",
    num_replicas=1,
    ray_actor_options={
        "num_gpus": 0.05,
        "resources": {"accelerator_type:P40": 0.01}
    },
    autoscaling_config={"min_replicas": 1, "max_replicas": 1}
)
class RerankerDeployment:
    # Wraps bge-reranker-v2-m3 via cross-encoder inference
    ...
```

### §11.4 EmbeddingDeployment (Irina, Tesla P4)

The embedding deployment runs on Irina as a Ray Worker node. It wraps the
HuggingFace Text Embeddings Inference (TEI) HTTP server running locally on Irina,
or directly invokes the model via `sentence-transformers`.

```python
@serve.deployment(
    name="EmbeddingDeployment",
    num_replicas=1,
    ray_actor_options={
        "num_gpus": 1.0,
        "resources": {"accelerator_type:P4": 0.01}
    },
    autoscaling_config={"min_replicas": 1, "max_replicas": 1}
)
class EmbeddingDeployment:
    # Model: m2-bert-80M-32k-retrieval (768-dim output)
    # Must load from pre-staged weights at /mnt/storage/models/hamilton
    # (offline-first — no HuggingFace Hub download at runtime)
    ...
```

**Pascal architecture note:** The Tesla P4 (Compute 6.1, Pascal) requires specific
image / library compatibility. Verify CUDA and PyTorch version support for Pascal
before deploying. `sentence-transformers` with a compatible CUDA build is preferred
over TEI for Pascal if TEI's Pascal support proves limited.

### §11.5 J-Desktop — Ephemeral Ray Jobs (RTX 3050)

J-Desktop (Hyper-V DDA Linux VM, RTX 3050, 8GB) is registered as a Ray Worker with
`accelerator_type:RTX3050`. It is not assigned a persistent Ray Serve deployment.
It accepts **Ray Jobs** submitted for ephemeral compute workloads (e.g., FFMPEG
video processing, ad-hoc model inference). Model assignment (7B class at Q4/Q8) is
TBD; register alias in Postgres once a model is selected.

---

## §12. Credentials

All credentials loaded at runtime from files. Never injected as environment variables
or hardcoded.

| Secret | Path |
|---|---|
| OpenAI API key | `/storage/credentials/api-keys/openai.env` |
| Gemini API key | `/storage/credentials/api-keys/gemini.env` |
| Postgres password | `/storage/credentials/sutherland/postgres.txt` |

---

## §13. Documentation Updates Required (post-approval)

| Document | Change |
|---|---|
| `registry.yml` | Mark Hamilton as retired; update Sutherland description to include embedding tool |
| `docs/designs/HLD-conversational-core.md` | ✅ Already updated (v2.0) — Hamilton removed; Rogers calls Sutherland for embeddings |
| `mads/rogers/rogers/config.json` | Update peers: embed calls route to `sutherland/llm_embeddings`, not `hamilton/embed_text` |
| `mads/rogers/docs/REQ-rogers.md` | Update §Consumer Dependencies: Hamilton → Sutherland for embedding tool |
