# TEST PLAN: Sutherland (Ray Iteration)

**MAD Group:** sutherland
**Version:** 2.0 (Ray cluster architecture)
**Date:** 2026-02-28

---

## 1. Environment Setup

- [ ] Ensure the `sutherland` MAD group is deployed on `m5` (`192.168.1.120`).
- [ ] Verify the four MAD containers (`sutherland`, `sutherland-langgraph`, `sutherland-postgres`, `sutherland-ray-head`) are `(healthy)` via `docker ps`.
- [ ] Ensure Ray worker nodes (on m5, Irina, and J-Desktop) have joined the cluster and are visible via `ray status` on the head node.
- [ ] Verify the Ray Serve deployments (`ImperatorDeployment`, `AgentSmallDeployment`, `RerankerDeployment`, `EmbeddingDeployment`) are `RUNNING`.

---

## 2. Tier 1: Interface & Contract Tests

These tests verify the MCP Gateway API using `curl` against the sessionless `POST /mcp` endpoint (JSON-RPC 2.0).
All tests target: `http://192.168.1.120:11435/mcp`

### Tool: `llm_chat_completions`

- **Test Case 1.1: Happy Path — Local Model (Non-Streaming)**
  - **Input:** `{"jsonrpc":"2.0","method":"tools/call","params":{"name":"llm_chat_completions","arguments":{"model":"imperator-gunner","messages":[{"role":"user","content":"Say 'System is nominal'."}]}},"id":"1"}`
  - **Expected Output:** OpenAI-compatible response body containing "System is nominal".
  - **Latency Target:** `< 4.0s` (includes prompt processing + TTFT).

- **Test Case 1.2: Happy Path — Cloud Model (Non-Streaming)**
  - **Input:** Same as above, but `model` is `imperator-grace`.
  - **Expected Output:** OpenAI-compatible response.
  - **Latency Target:** `< 2.0s`.

- **Test Case 1.3: Streaming (SSE)**
  - **Input:** Add `"stream": true` to the arguments.
  - **Expected Output:** Stream of `data: {...}` chunks in OpenAI format, terminating with `data: [DONE]`.

- **Test Case 1.4: Vision / Multimodal (Local)**
  - **Input:** `messages` array containing an image content block (base64 encoded image), targeting `imperator-gunner` (Qwen2.5-VL).
  - **Expected Output:** Text response accurately describing the image content.

- **Test Case 1.5: Determinism (`temperature: 0`)**
  - **Input:** Send the exact same prompt twice (e.g., "Write a random number") with `"temperature": 0`.
  - **Expected Output:** Both responses are identical.

- **Test Case 1.6: Parameter Validation — Max Tokens**
  - **Input:** Send a prompt asking for a long story, with `"max_tokens": 10`.
  - **Expected Output:** Response is truncated at exactly 10 tokens.

- **Test Case 1.7: Error Condition — Invalid Alias**
  - **Input:** `model` is `invalid-alias-123`.
  - **Expected Output:** JSON response containing `[ERROR: Unknown model alias: invalid-alias-123]`.

### Tool: `llm_embeddings`

- **Test Case 1.8: Happy Path — Single String**
  - **Input:** `{"jsonrpc":"2.0","method":"tools/call","params":{"name":"llm_embeddings","arguments":{"input":"Hello world", "model": "primary-embedder"}},"id":"2"}`
  - **Expected Output:** Response containing `embedding` (array of 768 floats) and `dimension: 768`.
  - **Latency Target:** `< 200ms`.

- **Test Case 1.9: Happy Path — Batch Processing**
  - **Input:** `input` is `["Hello", "World"]`.
  - **Expected Output:** Response containing `embeddings` (array of 2 sub-arrays), `dimension: 768`, and `count: 2`.

- **Test Case 1.10: Long Context Limits**
  - **Input:** `input` is a single string containing 30,000 characters.
  - **Expected Output:** Successful embedding array returned with no truncation or HTTP 500 errors.

- **Test Case 1.11: Max Batch Boundary**
  - **Input:** `input` is an array of exactly 32 strings.
  - **Expected Output:** Successful response with 32 embeddings.

- **Test Case 1.12: Over-limit Batch**
  - **Input:** `input` is an array of 33 strings.
  - **Expected Output:** HTTP 400 Bad Request or JSON-RPC schema error.

- **Test Case 1.13: Error Condition — Empty Input**
  - **Input:** `input` is `""` or `[]`.
  - **Expected Output:** HTTP 400 Bad Request or JSON-RPC error.

### Tool: `llm_rerank`

- **Test Case 1.14: Happy Path — Relevance Ordering**
  - **Input:** `{"jsonrpc":"2.0","method":"tools/call","params":{"name":"llm_rerank","arguments":{"model":"primary-reranker", "query":"machine learning","documents":["ML is great","Cats are fuzzy","Neural networks"]}},"id":"4"}`
  - **Expected Output:** Array of results where "ML is great" and "Neural networks" score significantly higher than "Cats are fuzzy".
  - **Score Targets:** Relevant docs score `> 0.5`; irrelevant doc scores `< 0.3`.

- **Test Case 1.15: `top_n` Filtering**
  - **Input:** Same as above, but with `"top_n": 1`.
  - **Expected Output:** Array containing exactly 1 result (the highest scoring document).

---

## 3. Tier 2: Integration & State Verification Tests

These tests verify the architectural invariants (No Eviction, No CPU Spill, Heterogeneous Slicing) defined in REQ-000 and the HLD.

### Check 3.1: GPU VRAM Pinning (No CPU Spill)
- **Action:** Wait for the Ray cluster to fully initialize models.
- **Verification (m5 via SSH):**
  ```bash
  nvidia-smi
  ```
- **Expected:** The 3x V100 pool shows combined memory usage matching the Qwen2.5-VL-72B model size (~34GB+). The P40s show memory usage for the 7B and reranker models.
- **Verification (Ray Head logs):**
  ```bash
  docker logs sutherland-ray-head | grep "llm_load_tensors: offloaded"
  ```
- **Expected:** Log must show `offloaded N/N layers to GPU`. Partial offload (e.g., `offloaded 60/80 layers`) is a **critical failure** of the hard-fail invariant.

### Check 3.2: Persistent Actors (No Eviction)
- **Action:** Leave the system idle for 15 minutes. Make a `llm_chat_completions` request to `imperator-gunner`.
- **Verification:** Measure the Time To First Token (TTFT).
- **Expected:** TTFT is `< 4.0s`. If the response takes > 15s, the Ray Serve autoscaler has improperly evicted the model to disk.

### Check 3.3: Database Schema Integrity
- **Action:** Inspect the `model_aliases` registry.
- **Verification (m5 via SSH):**
  ```bash
  docker exec -it sutherland-postgres psql -U sutherland -d sutherlanddb -c "SELECT alias, backend_type, backend_url FROM model_aliases WHERE alias='imperator-gunner';"
  ```
- **Expected:** Row exists with `backend_type='local_ray'` and `backend_url='http://sutherland-ray-head:8000'`.

### Check 3.4: Cross-Node Network Connectivity
- **Action:** Verify the embedding model on Irina (P4) is accessible from the LangGraph container on m5.
- **Verification (m5 via SSH):**
  ```bash
  # Execute the embedding tool through the gateway
  curl -s -X POST -H "Content-Type: application/json" -d '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"llm_embeddings","arguments":{"input":"Ping", "model":"primary-embedder"}},"id":"5"}' http://192.168.1.120:11435/mcp
  ```
- **Expected:** Successful 768-dim vector response, proving `sutherland-langgraph` successfully POSTed to the Ray API, which successfully routed to the Ray Worker on Irina.

---

## 4. Overall Verification

- [ ] `mads/sutherland/docs/REQ-sutherland.md` is current.
- [ ] `docs/designs/HLD-conversational-core.md` is current.
- [ ] `GET http://192.168.1.120:11435/health` returns `{"status": "healthy"}` showing `postgres: ok` and `ray_cluster: ok`.
- [ ] `mads/sutherland/tests/TEST-RESULTS.md` updated with the results of this plan.
