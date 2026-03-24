# TEST PLAN: Rogers

**MAD Group:** rogers  **Version:** 3.1  **Date:** 2026-02-28

---

## 1. Environment Setup

- [ ] Ensure rogers MAD group is deployed on m5 (`192.168.1.120`)
- [ ] Verify all containers in the MAD group are `(healthy)`:
  ```bash
  docker ps --filter "label=mad.logical_actor=rogers"
  ```
- [ ] Confirm rogers gateway is reachable from m5:
  ```bash
  curl -s http://localhost:6380/health | python3 -m json.tool
  ```
- [ ] Confirm rogers-langgraph is reachable internally (from inside container):
  ```bash
  docker exec rogers-langgraph curl -s http://localhost:8000/health
  ```
- [ ] Note: `mem_*` tests require Sutherland (port 11435 on m5). If Sutherland is not running, `mem_*` tests will skip gracefully with a SKIP message — this is expected and not a failure.

**Test identifiers used throughout this plan:**
- Test user ID: `joshua26-test-regression`
- Test session prefix: `test-regression-`
- Primary seed session: `test-regression-seed`

---

## 2. Tier 1: Interface and Contract Tests

Tests are executed inside the rogers-langgraph container against `localhost:8000`. All tool calls use the pattern:

```bash
docker exec rogers-langgraph python3 /app/tests/test_tools.py
```

The automated test suite covers all cases below. The per-tool cases here document intent and expected behaviour for manual verification or debugging.

---

### Tool: `health`

**Test Case 1.1: Happy Path — Server healthy**
- Input: `GET /health`
- Expected output: `{"status": "healthy"}`, HTTP 200
- Verifies: postgres pool responds to `SELECT 1`, redis responds to `PING`
- Command:
  ```bash
  docker exec rogers-langgraph curl -s http://localhost:8000/health
  ```

**Test Case 1.2: Degraded — Dependency unavailable**
- Condition: Simulate by stopping rogers-postgres or rogers-redis
- Expected output: `{"status": "unhealthy", "error": "..."}`, HTTP 503
- Note: This is a manual-only test; do not run during normal regression

---

### Tool: `conv_create_session`

**Test Case 1.3: Happy Path — Create new session**
- Input:
  ```json
  {
    "session_id": "test-regression-001",
    "flow_id": "test-regression",
    "user_id": "joshua26-test-regression",
    "flow_name": "Test Regression Suite",
    "interface_name": "test",
    "max_token_limit": 50000
  }
  ```
- Expected output: `{"session_id": "test-regression-001", "config": {"max_token_limit": 50000, ...}}`
- Checks: `session_id` matches input, `config` key present, `config.max_token_limit == 50000`

**Test Case 1.4: Edge Case — Duplicate session_id (idempotent)**
- Input: Same `session_id` as Test Case 1.3
- Expected output: HTTP 200 with same `session_id` returned (upsert behaviour)
- Note: Duplicate create should not error; idempotency is required for retry safety

**Test Case 1.5: Error Condition — Missing session_id**
- Input: `{"flow_id": "test-regression", "user_id": "joshua26-test-regression"}`
- Expected output: HTTP 400, `{"success": false, "error": {"code": "VALIDATION_ERROR", "message": "..."}}`

---

### Tool: `conv_get_session_config`

**Test Case 1.6: Happy Path — Retrieve existing session**
- Pre-condition: Session from Test Case 1.3 exists
- Input: `{"session_id": "test-regression-001"}`
- Expected output: `{"session_id": "test-regression-001", "max_token_limit": 50000, "total_turns": N, ...}`
- Checks: correct `session_id`, `max_token_limit` present, `total_turns` present

**Test Case 1.7: Edge Case — create_if_missing=true with new session**
- Input: `{"session_id": "test-regression-automake-<uuid>", "create_if_missing": true}`
- Expected output: HTTP 200, `{"session_id": "test-regression-automake-<uuid>", ...}` (session created on demand)
- Checks: returns a session even though it did not previously exist

**Test Case 1.8: Error Condition — Missing session_id**
- Input: `{}`
- Expected output: HTTP 400, `{"success": false, "error": {"code": "VALIDATION_ERROR", ...}}`

---

### Tool: `conv_store_turn`

**Test Case 1.9: Happy Path — Store a single turn**
- Pre-condition: Session `test-regression-001` exists
- Input:
  ```json
  {
    "session_id": "test-regression-001",
    "user_message": "Hello, I need help with Python.",
    "ai_message": "Sure! What do you need help with?",
    "user_sender_name": "Joshua",
    "ai_sender_name": "Claude",
    "model_name": "test-model",
    "token_count": 25
  }
  ```
- Expected output: `{"turn_id": "<uuid>", "session_id": "test-regression-001"}`
- Checks: `turn_id` present (UUID), `session_id` matches input

**Test Case 1.10: Edge Case — Large message content**
- Input: Same as above but `user_message` is a 10,000-character string
- Expected output: HTTP 200, `turn_id` returned — no truncation errors
- Checks: Confirms there is no hard content-length rejection at the endpoint level

**Test Case 1.11: Error Condition — Missing required fields**
- Input: `{"session_id": "test-regression-001"}` (missing `user_message`, `ai_message`)
- Expected output: HTTP 400, `{"success": false, "error": {"code": "VALIDATION_ERROR", ...}}`

---

### Tool: `conv_get_history`

**Test Case 1.12: Happy Path — Retrieve turns in order**
- Pre-condition: Three turns stored in `test-regression-001` (Python help turns from test_tools.py TURNS list)
- Input: `{"session_id": "test-regression-001"}`
- Expected output:
  ```json
  {
    "turns": [
      {"user_message": "Hello, I need help with Python.", "ai_message": "...", "created_at": "..."},
      ...
    ],
    "session": {...}
  }
  ```
- Checks: `turns` is a list of length 3, ordered ascending by `created_at`, first turn `user_message` matches first stored message, no `user_embedding` or `ai_embedding` fields present

**Test Case 1.13: Edge Case — Empty session (no turns stored)**
- Pre-condition: Session exists but has zero turns
- Input: `{"session_id": "test-regression-empty"}`
- Expected output: `{"turns": [], "session": {...}}`, HTTP 200
- Checks: `turns` is an empty list, no error raised

**Test Case 1.14: Error Condition — Missing session_id**
- Input: `{}`
- Expected output: HTTP 400, `{"success": false, "error": {"code": "VALIDATION_ERROR", ...}}`

---

### Tool: `conv_list_sessions`

**Test Case 1.15: Happy Path — Session appears in listing**
- Pre-condition: `test-regression-001` session created with `flow_id="test-regression"`
- Input: `{"flow_id": "test-regression"}`
- Expected output: `{"sessions": [{...}, ...]}`
- Checks: `sessions` is a list, `test-regression-001` appears in list, listed session has `total_turns` matching the number of stored turns, `first_user_message` matches the first stored user message

**Test Case 1.16: Edge Case — Filter by flow_id returns only matching sessions**
- Input: `{"flow_id": "test-regression"}`
- Checks: No sessions from other `flow_id` values appear in the result

**Test Case 1.17: Error Condition — No sessions for unknown flow_id**
- Input: `{"flow_id": "nonexistent-flow-99999"}`
- Expected output: `{"sessions": []}`, HTTP 200 (empty list, not an error)

---

### Tool: `conv_retrieve_context`

**Test Case 1.18: Happy Path — All turns returned within generous budget**
- Pre-condition: `test-regression-001` has 3 turns with total token count ~100
- Input: `{"session_id": "test-regression-001", "max_tokens": 100000}`
- Expected output: `{"turns": [...], "total_tokens": N}`
- Checks: `turns` length equals number of stored turns, `total_tokens` present

**Test Case 1.19: Edge Case — Tight max_tokens returns fewer turns**
- Input: `{"session_id": "test-regression-001", "max_tokens": 50}`
- Expected output: `{"turns": [...], "total_tokens": N}`
- Checks: `len(turns) < 3` — the budget is smaller than the total stored token count, so the oldest turns are dropped

**Test Case 1.20: Error Condition — Missing session_id**
- Input: `{"max_tokens": 10000}`
- Expected output: HTTP 400, `{"success": false, "error": {"code": "VALIDATION_ERROR", ...}}`

---

### Tool: `mem_add` *(skip if Sutherland unavailable)*

**Test Case 1.21: Happy Path — Memory stored and ID returned**
- Input:
  ```json
  {
    "content": "The test user prefers dark mode and writes Python.",
    "user_id": "joshua26-test-regression"
  }
  ```
- Expected output: `{"memory_id": "<uuid>", "status": "added"}`
- Checks: `memory_id` present (UUID), `status == "added"`

**Test Case 1.22: Edge Case — Duplicate content**
- Input: Same content as Test Case 1.21
- Expected output: HTTP 200; Mem0 may return `status == "noop"` or update the existing entry — no error
- Checks: No exception raised; response is a valid JSON object

**Test Case 1.23: Error Condition — Missing user_id**
- Input: `{"content": "some content"}`
- Expected output: HTTP 400, `{"success": false, "error": {"code": "VALIDATION_ERROR", ...}}`

---

### Tool: `mem_search` *(skip if Sutherland unavailable)*

**Test Case 1.24: Happy Path — Results returned for matching query**
- Pre-condition: At least one memory stored for `joshua26-test-regression`
- Input: `{"query": "dark mode", "user_id": "joshua26-test-regression"}`
- Expected output: `{"memories": {"results": [...]}}`
- Checks: `memories` key present, `memories.results` is a list with at least one entry

**Test Case 1.25: Edge Case — Empty query returns empty results**
- Input: `{"query": "", "user_id": "joshua26-test-regression"}`
- Expected output: `{"memories": {"results": []}}` or HTTP 400
- Checks: No exception; result is gracefully empty or a validation error (either is acceptable)

**Test Case 1.26: Error Condition — Missing user_id**
- Input: `{"query": "something"}`
- Expected output: HTTP 400, `{"success": false, "error": {"code": "VALIDATION_ERROR", ...}}`

---

### Tool: `mem_get_context` *(skip if Sutherland unavailable)*

**Test Case 1.27: Happy Path — Context string returned**
- Pre-condition: At least one memory stored for `joshua26-test-regression`
- Input: `{"query": "What does the user prefer?", "user_id": "joshua26-test-regression"}`
- Expected output: `{"context": "...", "memories": [...]}`
- Checks: `context` is a non-empty string, `memories` is a list

**Test Case 1.28: Edge Case — User with no memories returns empty context**
- Input: `{"query": "any query", "user_id": "joshua26-test-no-memories-ever"}`
- Expected output: `{"context": "", "memories": []}` or `{"context": "No relevant memories found.", "memories": []}`
- Checks: Returns HTTP 200 with a `context` key, no exception

---

### Tool: `mem_list` *(skip if Sutherland unavailable)*

**Test Case 1.29: Happy Path — Memories listed for user**
- Pre-condition: At least one memory stored for `joshua26-test-regression`
- Input: `{"user_id": "joshua26-test-regression"}`
- Expected output: `{"memories": [...]}`
- Checks: `memories` key present, is a list

**Test Case 1.30: Edge Case — User with no memories returns empty list**
- Input: `{"user_id": "joshua26-test-no-memories-ever"}`
- Expected output: `{"memories": []}`, HTTP 200
- Checks: Empty list, no error

---

### Tool: `mem_delete` *(skip if Sutherland unavailable)*

**Test Case 1.31: Happy Path — Memory deleted**
- Pre-condition: At least one memory exists for `joshua26-test-regression`; obtain `memory_id` from `mem_list`
- Input: `{"memory_id": "<uuid>", "user_id": "joshua26-test-regression"}`
- Expected output: `{"status": "deleted"}` or similar, HTTP 200
- Checks: `status` key present, no error

**Test Case 1.32: Error Condition — Invalid memory_id**
- Input: `{"memory_id": "00000000-0000-0000-0000-000000000000", "user_id": "joshua26-test-regression"}`
- Expected output: HTTP 400 or 404, or `{"status": "not_found"}` — must not raise an unhandled 500

---

### Tool: `mem_extract` *(skip if Sutherland unavailable)*

**Test Case 1.33: Happy Path — Memories extracted from session**
- Pre-condition: Session `test-regression-seed` has turns with factual content (seeded by `seed.py`)
- Input: `{"session_id": "test-regression-seed", "user_id": "joshua26-test-regression"}`
- Expected output: `{"extracted": 1, "status": "extracted", "result": {...}}`
- Checks: `result` or `memories` or `extracted` key present, `extracted >= 0`

**Test Case 1.34: Edge Case — Session with no extractable facts**
- Pre-condition: Session exists but turns contain only filler content
- Input: `{"session_id": "test-regression-seed", "user_id": "joshua26-test-regression"}`
- Expected output: HTTP 200; `extracted` may be 0 or status may be `"no messages"` — no exception

---

## 3. Tier 2: Integration and State Verification Tests

These tests are run from the m5 host (`ssh aristotle9@192.168.1.120`) after the Tier 1 suite has run (or after `seed.py` has been executed). They verify that tool invocations correctly persisted state to the backing stores.

---

### State Verification: `conv_store_turn`

**Test Case 2.1: Row exists in conversation_messages after turn storage**

Action: Call `conv_store_turn` for session `test-regression-seed` (or run `seed.py`)

Verification:
```bash
docker exec rogers-postgres psql -U rogers rogers -c \
  "SELECT id, user_message, ai_message, token_count, created_at \
   FROM conversation_messages \
   WHERE session_id = 'test-regression-seed' \
   ORDER BY created_at;"
```

Expected: Three rows visible with correct `user_message` content matching the three Python help turns from `seed.py`.

**Test Case 2.2: conversations row created on conv_create_session**

Action: Call `conv_create_session` for `test-regression-seed`

Verification:
```bash
docker exec rogers-postgres psql -U rogers rogers -c \
  "SELECT id, flow_id, user_id, max_token_limit, created_at \
   FROM conversations \
   WHERE id = 'test-regression-seed';"
```

Expected: One row with `id = 'test-regression-seed'`, `flow_id = 'test-regression'`, `user_id = 'joshua26-test-regression'`, `max_token_limit = 50000`.

**Test Case 2.3: context_windows row exists (if applicable)**

Verification:
```bash
docker exec rogers-postgres psql -U rogers rogers -c \
  "SELECT id, conversation_id, max_token_limit \
   FROM context_windows \
   WHERE conversation_id = 'test-regression-seed';"
```

Expected: At least one row if the session creates a context window on setup.

---

### State Verification: `mem_add`

**Test Case 2.4: Row exists in mem0_memories after mem_add**

Action: Call `mem_add` with `user_id = "joshua26-test-regression"` (or run `seed.py`)

Verification:
```bash
docker exec rogers-postgres psql -U rogers rogers -c \
  "SELECT id, payload->>'user_id' AS user_id, payload->>'data' AS data \
   FROM mem0_memories \
   WHERE payload->>'user_id' = 'joshua26-test-regression';"
```

Expected: At least one row with `user_id = 'joshua26-test-regression'` and `data` containing the seeded memory content.

**Test Case 2.5: Neo4j node exists after mem_add**

Action: Same as Test Case 2.4

Verification:
```bash
docker exec rogers-neo4j cypher-shell -u neo4j -p <password> \
  "MATCH (n {user_id: 'joshua26-test-regression'}) RETURN n LIMIT 5;"
```

Expected: At least one node with `user_id = 'joshua26-test-regression'` present in the graph.

Note: Retrieve the Neo4j password from `/storage/credentials/rogers/neo4j.txt` on m5. The file uses `NEO4J_AUTH=neo4j/<password>` format.

---

### Schema Note: Correct Table Names

The existing `cleanup()` in `test_tools.py` uses incorrect legacy table names (`conversation_turns`, `conversation_summaries`, `conversation_sessions`). The correct current schema names are:

| Legacy name (wrong) | Correct name |
|---|---|
| `conversation_sessions` | `conversations` |
| `conversation_turns` | `conversation_messages` |
| `conversation_summaries` | `conversation_summaries` (unchanged) |
| *(no equivalent)* | `context_windows` |

The `cleanup.py` and `seed.py` scripts in this test suite use the correct names.

---

## 4. Automated Test Commands

All commands are run from the m5 host after SSHing in (`ssh aristotle9@192.168.1.120`).

```bash
# Full functional test (Tier 1 — runs inside container, exits 0 on all pass)
docker exec rogers-langgraph python3 /app/tests/test_tools.py

# Seed known test data before quality/timing tests
docker exec rogers-langgraph python3 /app/tests/seed.py

# LLM extraction quality (requires Sutherland + seed data)
docker exec rogers-langgraph python3 /app/tests/test_quality.py

# Pipeline timing (requires seed data)
docker exec rogers-langgraph python3 /app/tests/test_timing.py

# Cleanup all test data (postgres + neo4j)
docker exec rogers-langgraph python3 /app/tests/cleanup.py
```

Recommended sequence for a full regression run:
```bash
docker exec rogers-langgraph python3 /app/tests/cleanup.py
docker exec rogers-langgraph python3 /app/tests/seed.py
docker exec rogers-langgraph python3 /app/tests/test_tools.py
docker exec rogers-langgraph python3 /app/tests/test_quality.py
docker exec rogers-langgraph python3 /app/tests/cleanup.py
```

---

## 5. Overall Verification Checklist

- [ ] `test_tools.py` exits 0 with 0 failures
- [ ] `seed.py` exits 0 and prints created resources
- [ ] `cleanup.py` exits 0 and prints deleted counts
- [ ] `docker logs rogers-langgraph --tail 50` shows no unexpected ERROR-level entries
- [ ] `docker logs rogers --tail 20` shows no unexpected ERROR-level entries
- [ ] All containers report `(healthy)` in `docker ps`
- [ ] PostgreSQL state verification queries (Section 3) return expected rows
- [ ] Neo4j state verification query (Section 3, Test Case 2.5) returns expected node (if Sutherland available)

---

**Related:** [Deployment Guide](../../docs/guides/mad-deployment-guide.md) · [Testing Guide](../../docs/guides/mad-testing-guide.md) · [REQ-rogers](./REQ-rogers.md)
