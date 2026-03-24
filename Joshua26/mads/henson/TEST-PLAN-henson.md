# TEST PLAN: Henson — The Human Interaction Hub

**MAD Group:** henson
**Version:** 1.0.0 (Phase 1 Baseline)
**Date:** 2026-02-28
**Related REQ:** REQ-henson (REQ-033)
**Host:** m5 (192.168.1.120)

---

## 1. Environment Setup

Before executing any tests, verify the following conditions are met on m5.

### 1.1 Container Health

```bash
# Verify all henson containers are (healthy)
docker ps --filter "label=mad.logical_actor=henson" --format "table {{.Names}}\t{{.Status}}"
```

Expected: All five containers report `(healthy)`:

| Container | Role |
|---|---|
| `henson` | MCP gateway (port 9224) |
| `henson-langgraph` | Logic engine (Quart/LangGraph) |
| `henson-postgres` | State storage |
| `henson-nginx` | UI router (internal, henson-net) |
| `henson-openwebui` | Phase 1 chat UI |

- [ ] `henson` — healthy
- [ ] `henson-langgraph` — healthy
- [ ] `henson-postgres` — healthy
- [ ] `henson-nginx` — healthy
- [ ] `henson-openwebui` — healthy

### 1.2 Dependency Services

- [ ] **Sutherland** is deployed and running on m5 (port 11435) — required for Gunner persona inference
- [ ] **Malory** is running on m5 (port 9222) — required for all UI browser automation tests
- [ ] **Rogers** is running (required for `ensure_rogers_session` and `write_memory_to_rogers` graph nodes)
- [ ] OpenAI API key readable at `/storage/credentials/api-keys/openai.env` — required for Henson persona
- [ ] Gemini API key readable at `/storage/credentials/api-keys/gemini.env` — required for Grace persona

### 1.3 Network Topology

```bash
# Verify henson gateway is on both networks
docker inspect henson --format '{{range $k,$v := .NetworkSettings.Networks}}{{$k}} {{end}}'
# Expected output includes: joshua-net henson-net

# Verify backing services are henson-net only
docker inspect henson-langgraph --format '{{range $k,$v := .NetworkSettings.Networks}}{{$k}} {{end}}'
# Expected: henson-net only (NOT joshua-net)
```

- [ ] `henson` is on both `joshua-net` and `henson-net`
- [ ] `henson-langgraph`, `henson-postgres`, `henson-nginx`, `henson-openwebui` are on `henson-net` only

### 1.4 Health Endpoint

```bash
curl -s http://localhost:9224/health | python3 -m json.tool
# Expected: {"status": "ok"} or equivalent healthy response
```

- [ ] `/health` returns OK

### 1.5 Credentials and Access

- **Admin credentials:** `admin@henson.local` / `HensonAdmin26!`
- **User credentials:** `j@4morr.com` / `Edgar01760`
- **Gateway URL (from m5):** `http://localhost:9224`
- **Malory URL (from m5):** `http://localhost:9222`
- **Open WebUI (browser):** `http://henson:9224` (via gateway UI proxy)

---

## 2. Tier 1: Interface & Contract Tests

### 2.1 Automated Test Execution

```bash
# Run from m5 host — covers MCP-1 through MCP-3 and basic UI (T01-T04)
python3 mads/henson/tests/test_henson.py

# Run extended regression suite (UI T01-T43, Tier 2 state verification)
python3 mads/henson/tests/test_henson_regression.py

# Cleanup sessions and test data created during runs
python3 mads/henson/tests/cleanup.py
```

### 2.2 MCP Tool Tests

All MCP tool tests invoke the gateway directly at `http://localhost:9224/mcp` using JSON-RPC 2.0. No SAM relay is required for direct gateway testing.

---

#### Tool: `henson_list_personas`

**Description:** Queries `henson-postgres` and returns all available personas. No required parameters.

**Test Case MCP-1.1: Happy Path — All three personas returned**

- **Input:** `{}`
- **Command:**
  ```bash
  curl -s -X POST -H "Content-Type: application/json" \
    -d '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"henson_list_personas","arguments":{}},"id":"t1"}' \
    http://localhost:9224/mcp | python3 -m json.tool
  ```
- **Expected Output:** Response contains a `personas` array with exactly three entries; IDs `henson`, `gunner`, and `grace` are all present.
  ```json
  {
    "personas": [
      {"id": "henson", "display_name": "Henson", ...},
      {"id": "gunner", "display_name": "Gunner", ...},
      {"id": "grace",  "display_name": "Grace",  ...}
    ]
  }
  ```
- **Pass Criteria:** `personas` array length >= 3; set `{"henson","gunner","grace"}` is a subset of returned IDs.
- **Status:** [ ] PASS / [ ] FAIL

**Test Case MCP-1.2: Edge Case — Persona object schema validation**

- **Input:** `{}`
- **Expected Output:** Each persona object contains at minimum the fields `id`, `display_name`, and `routing_type`. No missing keys on any of the three records.
- **Pass Criteria:** All three persona objects pass schema check: `id` (non-empty string), `display_name` (non-empty string), `routing_type` (one of `local`, `peer_mad`, `openai`, `gemini`).
- **Note:** No required parameters exist for this tool; there are no error-condition test cases.
- **Status:** [ ] PASS / [ ] FAIL

---

#### Tool: `henson_switch_session_persona`

**Description:** Updates `active_sessions` in `henson-postgres` to associate a session with a named persona. Required parameters: `session_id` (string), `persona_id` (string).

**Test Case MCP-2.1: Happy Path — Switch to a different persona**

- **Input:** `{"session_id": "test-switch-<timestamp>", "persona_id": "gunner"}`
- **Command:**
  ```bash
  SESSION="test-switch-$(date +%s)"
  curl -s -X POST -H "Content-Type: application/json" \
    -d "{\"jsonrpc\":\"2.0\",\"method\":\"tools/call\",\"params\":{\"name\":\"henson_switch_session_persona\",\"arguments\":{\"session_id\":\"$SESSION\",\"persona_id\":\"gunner\"}},\"id\":\"t2\"}" \
    http://localhost:9224/mcp | python3 -m json.tool
  ```
- **Expected Output:**
  ```json
  {"status": "success", "session_id": "<session_id>", "active_persona_id": "gunner"}
  ```
- **Pass Criteria:** `active_persona_id` equals `"gunner"` in the response.
- **Status:** [ ] PASS / [ ] FAIL

**Test Case MCP-2.2: Edge Case — Switch to the same persona that is already active**

- **Pre-condition:** Session already has `active_persona_id = "gunner"` (e.g., from MCP-2.1).
- **Input:** Same `session_id`, `"persona_id": "gunner"` (no change).
- **Expected Output:** Tool returns success; `active_persona_id` still equals `"gunner"`. No error or exception thrown. Idempotent behavior.
- **Pass Criteria:** `status == "success"`, `active_persona_id == "gunner"`.
- **Status:** [ ] PASS / [ ] FAIL

**Test Case MCP-2.3: Edge Case — Switch back to original persona**

- **Pre-condition:** Session active persona is `"gunner"`.
- **Input:** Same `session_id`, `"persona_id": "henson"`.
- **Expected Output:** `{"status": "success", ..., "active_persona_id": "henson"}`
- **Pass Criteria:** `active_persona_id` equals `"henson"`.
- **Status:** [ ] PASS / [ ] FAIL

**Test Case MCP-2.4: Error Condition — Unknown persona_id**

- **Input:** `{"session_id": "test-switch-err-<timestamp>", "persona_id": "nonexistent_persona_xyz"}`
- **Expected Output:** JSON-RPC error response. Either a `-32602 Invalid params` error code or an application-level error field indicating the persona ID was not found. Must NOT return `"status": "success"` with a bogus persona.
- **Pass Criteria:** Response contains `"error"` key or `"status": "error"`; no row written to `active_sessions` with invalid persona.
- **Status:** [ ] PASS / [ ] FAIL

**Test Case MCP-2.5: Error Condition — Missing session_id**

- **Input:** `{"persona_id": "gunner"}` (omit `session_id`)
- **Expected Output:** JSON-RPC error response: `{"jsonrpc":"2.0","error":{"code":-32602,"message":"Invalid params"},"id":"..."}`
- **Pass Criteria:** HTTP response contains `"error"` at JSON-RPC level; no crash or 500 from gateway.
- **Status:** [ ] PASS / [ ] FAIL

**Test Case MCP-2.6: Error Condition — Missing persona_id**

- **Input:** `{"session_id": "test-switch-err2-<timestamp>"}` (omit `persona_id`)
- **Expected Output:** JSON-RPC error response indicating missing required parameter.
- **Pass Criteria:** Response contains `"error"` key; tool does not silently insert a null/default persona.
- **Status:** [ ] PASS / [ ] FAIL

---

#### Tool: `henson_chat_turn`

**Description:** The primary execution entrypoint. Triggers the full Shared Imperator LangGraph: `parse_and_load_persona` → `ensure_rogers_session` → `fetch_rogers_context` → `build_inference_payload` → `execute_inference` → `write_memory_to_rogers`. Required parameters: `session_id` (string), `message` (string). Optional: `persona_override` (string).

**Test Case MCP-3.1: Happy Path — Non-empty response, no system error**

- **Input:** `{"session_id": "test-chat-<timestamp>", "message": "Hello. In one sentence, who are you?"}`
- **Command:**
  ```bash
  SESSION="test-chat-$(date +%s)"
  curl -s -X POST -H "Content-Type: application/json" \
    -d "{\"jsonrpc\":\"2.0\",\"method\":\"tools/call\",\"params\":{\"name\":\"henson_chat_turn\",\"arguments\":{\"session_id\":\"$SESSION\",\"message\":\"Hello. In one sentence, who are you?\"}},\"id\":\"t3\"}" \
    http://localhost:9224/mcp | python3 -m json.tool
  ```
- **Expected Output:** `{"response": "<non-empty string>"}` where the string does not contain `[SYSTEM ERROR`.
- **Pass Criteria:**
  - `response` field is present and non-empty (length > 0).
  - Response does not contain `[SYSTEM ERROR`.
  - Response may contain `[SYSTEM WARNING: Memory unreachable]` if Rogers is unavailable — this is acceptable and does NOT constitute a test failure (Rogers is a soft dependency per REQ-henson §9).
- **Status:** [ ] PASS / [ ] FAIL

**Test Case MCP-3.2: Happy Path — Default persona is henson for a new session**

- **Input:** Fresh `session_id` (no prior `henson_switch_session_persona` call), `"message": "What is your name?"`
- **Expected Output:** Response is generated by the `henson` persona (GPT-4o, `routing_type=openai`). The content should identify as Henson.
- **Pass Criteria:** Non-empty response without `[SYSTEM ERROR`. Persona used defaults to `henson` per §6.3 Node 1 fallback logic.
- **Status:** [ ] PASS / [ ] FAIL

**Test Case MCP-3.3: Edge Case — Very long input message**

- **Input:** `{"session_id": "test-chat-long-<timestamp>", "message": "<2000-character message>"}` (e.g., 2000 repetitions of a word or a lengthy technical question).
- **Expected Output:** Non-empty response without error; completes within 120 seconds.
- **Pass Criteria:** `response` field present and non-empty; no JSON-RPC error; no gateway timeout at the test client side (90s timeout in `test_henson.py`).
- **Status:** [ ] PASS / [ ] FAIL

**Test Case MCP-3.4: Edge Case — Multi-turn same session (context continuity)**

- **Turn 1 Input:** `{"session_id": "test-chat-multi-<timestamp>", "message": "My name is Jason."}`
- **Turn 2 Input:** Same `session_id`, `"message": "What did I just tell you my name was?"`
- **Expected Output (Turn 2):** Response references the name "Jason" (demonstrating that Rogers context was successfully retrieved for the second turn).
- **Pass Criteria:** Turn 2 response is non-empty, no `[SYSTEM ERROR`; response ideally references "Jason". If Rogers is unavailable, `[SYSTEM WARNING: Memory unreachable]` is acceptable and the test records a conditional pass.
- **Status:** [ ] PASS / [ ] FAIL (Conditional if Rogers unavailable)

**Test Case MCP-3.5: Edge Case — persona_override field routes to correct persona**

- **Input:** `{"session_id": "test-chat-override-<timestamp>", "message": "Who are you?", "persona_override": "grace"}`
- **Expected Output:** Response is generated by the Grace persona (Gemini). Content should identify as Grace.
- **Pass Criteria:** Non-empty response; no `[SYSTEM ERROR`; `active_sessions` row for this session_id should show `active_persona_id = 'grace'` after the turn (verifiable in Tier 2).
- **Status:** [ ] PASS / [ ] FAIL

**Test Case MCP-3.6: Error Condition — Missing session_id**

- **Input:** `{"message": "Hello"}` (omit `session_id`)
- **Expected Output:** JSON-RPC error: `{"error": {"code": -32602, ...}}`
- **Pass Criteria:** Response contains `"error"` at JSON-RPC level; no 500 / crash.
- **Status:** [ ] PASS / [ ] FAIL

**Test Case MCP-3.7: Error Condition — Missing message**

- **Input:** `{"session_id": "test-chat-err-<timestamp>"}` (omit `message`)
- **Expected Output:** JSON-RPC error indicating missing required parameter.
- **Pass Criteria:** Response contains `"error"`; gateway does not forward a malformed payload to `henson-langgraph`.
- **Status:** [ ] PASS / [ ] FAIL

---

### 2.3 UI Tests (Open WebUI via Malory browser automation)

All UI tests navigate to `http://henson:9224` via Malory. The gateway UI proxy forwards browser traffic through `henson-nginx:8080` to `henson-openwebui:8080` (Open WebUI). Malory is addressed at `http://localhost:9222` from the m5 host.

**Credentials used:**
- Admin: `admin@henson.local` / `HensonAdmin26!`
- Standard user: `j@4morr.com` / `Edgar01760`

**Status key:**
- `PASS` — verified on 2026-02-26
- `UNTESTED` — not yet tested (Phase 2 feature now configured)
- `NOT TESTED` — trimmed from last test session; needs re-test
- `N/A` — permanently not applicable (feature absent/third-party internal)
- `SKIPPED` — not regression-relevant for Henson MAD testing

---

#### T01–T10: Authentication & Account Management

| ID | Test Description | Notes | Status |
|---|---|---|---|
| T01 | Navigate to `http://henson:9224`; page loads without error | Gateway UI proxy → nginx → Open WebUI | PASS |
| T02 | Admin sign-in: `admin@henson.local` / `HensonAdmin26!`; redirected to main chat UI | | PASS |
| T03 | Sign out from admin account; redirected to sign-in page | | PASS |
| T04 | Standard user sign-in: `j@4morr.com` / `Edgar01760`; chat UI loads | | PASS |
| T05 | Attempt sign-in with incorrect password; error message displayed | | PASS |
| T06 | Attempt sign-in with unknown email; error message displayed | | PASS |
| T07 | Admin creates a new user account via Admin Panel > Users | | PASS |
| T08 | Copy invite link for new user (clipboard API) | Browser clipboard API; environment-dependent | SKIPPED |
| T09 | Like/dislike a message using thumbs up/down | Open WebUI internal feedback; not Henson-relevant | SKIPPED |
| T10 | Admin deletes the test user created in T07 | | PASS |

#### T11–T21: Persona Selection and Basic Chat

| ID | Test Description | Notes | Status |
|---|---|---|---|
| T11 | Model selector dropdown opens; lists `henson`, `gunner`, `grace` | Populated from `GET /v1/models` → `henson-langgraph` → personas table | PASS |
| T12 | Select `henson` persona from model picker | | PASS |
| T13 | Send "Hello. In one sentence, who are you?" to henson persona; non-error response received | | PASS |
| T14 | Select `gunner` persona from model picker | Routes via `peer_mad` → Sutherland | PASS |
| T15 | Send test message to gunner persona; non-error response received | | PASS |
| T16 | Select `grace` persona from model picker | Routes via `gemini` → Gemini 2.5 Pro | PASS |
| T17 | Send test message to grace persona; non-error response received | | PASS |
| T18 | Start a new chat thread; model selector resets to default | | PASS |
| T19 | Send a multi-turn message (3 turns) to henson; responses are contextually coherent | Validates Rogers multi-turn context retrieval | PASS |
| T20 | Send message to henson; `[SYSTEM WARNING: Memory unreachable]` does NOT appear in normal operation | Validates Rogers is reachable | PASS |
| T21 | Send message to henson; `[SYSTEM ERROR` does NOT appear in the response | Validates inference backend is reachable | PASS |

#### T22–T30: UI Feature Coverage

| ID | Test Description | Notes | Status |
|---|---|---|---|
| T22 | Speech-to-text (STT) input button is present; activation attempt | STT backend now configured via Phase 2 env vars | UNTESTED |
| T23 | Chat message history persists after page reload | Tests `henson-openwebui` data persistence at `/workspace/henson/ui_data` | PASS |
| T24 | Chat search: search for a previous message text; result found | | PASS |
| T25 | Archive a chat thread; thread moves to archive | Open WebUI internal | PASS |
| T26 | Delete a chat thread; thread removed from sidebar | | PASS |
| T27 | Text-to-speech (TTS) output button visible on assistant message | TTS backend now configured via Phase 2 env vars | UNTESTED |
| T28 | Markdown rendering: send a message containing `**bold**` and `# Header`; renders correctly in UI | | PASS |
| T29 | Code block rendering: send a Python code snippet; renders with syntax highlighting | | PASS |
| T30 | Copy button on code block: copies code to clipboard | | PASS |

#### T31–T43: Admin, Settings, and Advanced Features

| ID | Test Description | Notes | Status |
|---|---|---|---|
| T31 | Admin Panel accessible at `/admin`; loads without error | | PASS |
| T32 | Admin Panel > Models: `henson`, `gunner`, `grace` appear in model list | Sourced from `/v1/models` endpoint | PASS |
| T33 | Custom model configuration (system prompt override) via model settings | Open WebUI internal override; not Henson persona management | SKIPPED |
| T34 | User settings: change display name; saved and reflected in UI | Open WebUI profile feature | PASS |
| T35 | Multimodal: attach an image to a chat message and send to grace persona | Requires image upload support | NOT TESTED |
| T36 | Multimodal: attach an image to a chat message and send to henson persona | Requires image upload support | NOT TESTED |
| T37 | Multimodal: verify LangGraph `build_inference_payload` passes content parts array correctly to backend | Requires log inspection in addition to UI test | NOT TESTED |
| T38 | Web search toggle: enable in chat; verify search results appear in response | Web search backend now configured via Phase 2 env vars | UNTESTED |
| T39 | Image generation: request an image via chat; image appears in response | Image generation backend now configured via Phase 2 env vars | UNTESTED |
| T40 | Channels feature: create a channel, post a message | Open WebUI internal; not Henson-relevant | SKIPPED |
| T41 | Notes feature: create a note via sidebar | Open WebUI internal; not Henson-relevant | SKIPPED |
| T42 | Workspace > Prompts: create and use a saved prompt | | PASS |
| T43 | Workspace > Tools: verify tool list renders (even if empty in Phase 1) | | PASS |

---

## 3. Tier 2: Integration & State Verification Tests

These tests require SSH access to m5 and direct `docker exec` into containers. They verify that the side-effects of tool invocations correctly propagate to the internal data stores.

### 3.1 Prerequisites

```bash
ssh aristotle9@192.168.1.120
```

All commands below are run from the m5 host unless otherwise noted.

---

### 3.2 Persona Table Verification

**Test Case ST-1: Seed data integrity — personas table is populated**

- **Pre-condition:** `henson-postgres` container is running and healthy.
- **Action:** (No tool call required — verify initial state.)
- **Verification:**
  ```bash
  docker exec henson-postgres psql -U henson hensondb -c \
    "SELECT id, display_name, routing_type FROM personas ORDER BY id;"
  ```
- **Expected Output:** Three rows returned:
  ```
   id     | display_name | routing_type
  --------+--------------+-------------
   grace  | Grace        | gemini
   gunner | Gunner       | peer_mad
   henson | Henson       | openai
  ```
- **Pass Criteria:** Exactly three rows present; all three IDs (`grace`, `gunner`, `henson`) exist; `routing_type` values match the seed data in REQ-henson §4.3.
- **Status:** [ ] PASS / [ ] FAIL

---

### 3.3 Session Persona Switch — State Verification

**Test Case ST-2: henson_switch_session_persona — active_persona_id written to active_sessions**

- **Pre-condition:** No row exists in `active_sessions` for `<test-session-id>`.
- **Action:** Call `henson_switch_session_persona` with a fresh session ID and `persona_id = "gunner"`:
  ```bash
  TEST_SESSION="st-test-$(date +%s)"
  curl -s -X POST -H "Content-Type: application/json" \
    -d "{\"jsonrpc\":\"2.0\",\"method\":\"tools/call\",\"params\":{\"name\":\"henson_switch_session_persona\",\"arguments\":{\"session_id\":\"$TEST_SESSION\",\"persona_id\":\"gunner\"}},\"id\":\"st2\"}" \
    http://localhost:9224/mcp
  echo "Session: $TEST_SESSION"
  ```
- **Verification:**
  ```bash
  docker exec henson-postgres psql -U henson hensondb -c \
    "SELECT active_persona_id FROM active_sessions WHERE session_id='<test-session-id>';"
  ```
  Replace `<test-session-id>` with the value printed by `echo "Session: $TEST_SESSION"`.
- **Expected Output:**
  ```
   active_persona_id
  -------------------
   gunner
  ```
- **Pass Criteria:** Exactly one row returned; `active_persona_id = 'gunner'`.
- **Status:** [ ] PASS / [ ] FAIL

**Test Case ST-3: henson_switch_session_persona — persona switch updates existing row**

- **Pre-condition:** `active_sessions` row from ST-2 exists with `active_persona_id = 'gunner'`.
- **Action:** Call `henson_switch_session_persona` with the same session ID and `persona_id = "grace"`.
- **Verification:**
  ```bash
  docker exec henson-postgres psql -U henson hensondb -c \
    "SELECT active_persona_id FROM active_sessions WHERE session_id='<test-session-id>';"
  ```
- **Expected Output:**
  ```
   active_persona_id
  -------------------
   grace
  ```
- **Pass Criteria:** Same row now reflects `active_persona_id = 'grace'`; no duplicate rows created.
- **Status:** [ ] PASS / [ ] FAIL

---

### 3.4 Chat Turn — Rogers Session Hydration Verification

**Test Case ST-4: henson_chat_turn — rogers_conversation_id populated on first turn**

- **Pre-condition:** A fresh session ID with no prior turns; no row in `active_sessions` for this ID.
- **Action:** Call `henson_chat_turn` with a new session ID:
  ```bash
  CHAT_SESSION="st-chat-$(date +%s)"
  curl -s -X POST -H "Content-Type: application/json" \
    -d "{\"jsonrpc\":\"2.0\",\"method\":\"tools/call\",\"params\":{\"name\":\"henson_chat_turn\",\"arguments\":{\"session_id\":\"$CHAT_SESSION\",\"message\":\"Hello.\"}},\"id\":\"st4\"}" \
    http://localhost:9224/mcp
  echo "Chat session: $CHAT_SESSION"
  ```
- **Verification:**
  ```bash
  docker exec henson-postgres psql -U henson hensondb -c \
    "SELECT session_id, rogers_conversation_id, rogers_context_window_id FROM active_sessions WHERE session_id='<test-session-id>';"
  ```
  Replace `<test-session-id>` with the value of `$CHAT_SESSION`.
- **Expected Output:**
  ```
   session_id           | rogers_conversation_id | rogers_context_window_id
  ----------------------+------------------------+--------------------------
   st-chat-<timestamp>  | <uuid>                 | <uuid>
  ```
- **Pass Criteria:**
  - Row exists in `active_sessions`.
  - `rogers_conversation_id` IS NOT NULL.
  - `rogers_context_window_id` IS NOT NULL.
  - If Rogers was unavailable during the turn, both fields may be NULL — this is acceptable graceful degradation per REQ-henson §9, and the test records a conditional pass.
- **Status:** [ ] PASS / [ ] FAIL (Conditional if Rogers unavailable)

**Test Case ST-5: henson_chat_turn — rogers IDs are reused on subsequent turns (not re-created)**

- **Pre-condition:** ST-4 has run; `active_sessions` row exists with non-null `rogers_conversation_id` and `rogers_context_window_id`.
- **Action:** Call `henson_chat_turn` again with the same session ID:
  ```bash
  curl -s -X POST -H "Content-Type: application/json" \
    -d "{\"jsonrpc\":\"2.0\",\"method\":\"tools/call\",\"params\":{\"name\":\"henson_chat_turn\",\"arguments\":{\"session_id\":\"$CHAT_SESSION\",\"message\":\"And who am I talking to?\"}},\"id\":\"st5\"}" \
    http://localhost:9224/mcp
  ```
- **Verification:** Query the same row again — both Rogers ID fields must be identical to the values set in ST-4.
  ```bash
  docker exec henson-postgres psql -U henson hensondb -c \
    "SELECT rogers_conversation_id, rogers_context_window_id FROM active_sessions WHERE session_id='<test-session-id>';"
  ```
- **Pass Criteria:** UUID values are unchanged from ST-4. A new conversation/context_window is NOT created for the second turn.
- **Status:** [ ] PASS / [ ] FAIL

---

### 3.5 Error State — Database Constraint Verification

**Test Case ST-6: FK constraint — unknown persona_id rejected by active_sessions**

- **Pre-condition:** No persona with ID `bad_persona_xyz` exists in `personas` table.
- **Action:** Attempt a direct insert into `active_sessions` with an invalid foreign key:
  ```bash
  docker exec henson-postgres psql -U henson hensondb -c \
    "INSERT INTO active_sessions (session_id, active_persona_id) VALUES ('fk-test', 'bad_persona_xyz');"
  ```
- **Expected Output:** PostgreSQL ERROR: foreign key violation:
  ```
  ERROR:  insert or update on table "active_sessions" violates foreign key constraint
  DETAIL:  Key (active_persona_id)=(bad_persona_xyz) is not present in table "personas".
  ```
- **Pass Criteria:** Error is raised; no row inserted.
- **Status:** [ ] PASS / [ ] FAIL

---

### 3.6 Container Log Verification

After running the MCP and UI test suites, inspect logs for unexpected errors.

```bash
# Gateway — should show clean MCP routing, no error-level stack traces
docker logs henson --tail 100

# Logic engine — should show graph execution per turn; WARN for Rogers degradation is acceptable
docker logs henson-langgraph --tail 100

# Postgres — should show only normal startup/connection messages
docker logs henson-postgres --tail 50

# Nginx — should show 200/101 (WebSocket upgrades) for UI proxy traffic
docker logs henson-nginx --tail 50

# Open WebUI — should show normal startup; no backend connection errors
docker logs henson-openwebui --tail 50
```

- [ ] `henson` logs: no unexpected ERROR entries
- [ ] `henson-langgraph` logs: graph executions visible; WARN for Rogers degradation acceptable; no unhandled exceptions
- [ ] `henson-postgres` logs: no ERROR entries
- [ ] `henson-nginx` logs: no upstream connection failures to `henson-openwebui` or `henson-langgraph`
- [ ] `henson-openwebui` logs: no backend API connection failures to `henson-langgraph`

---

### 3.7 Network Isolation Verification

```bash
# Verify henson-langgraph CANNOT reach joshua-net directly
docker exec henson-langgraph ping -c 1 rogers 2>&1
# Expected: Name resolution failure or no route — langgraph is on henson-net only

# Verify henson gateway CAN reach rogers on joshua-net (peer proxy works)
docker exec henson curl -s http://rogers:9220/health
# Expected: {"status": "ok"} or similar healthy response from Rogers gateway
```

- [ ] `henson-langgraph` cannot resolve `rogers` directly (ADR-053 isolation confirmed)
- [ ] `henson` gateway can reach Rogers via `joshua-net` (peer proxy path functional)

---

## 4. Overall Verification Checklist

- [ ] All five Henson containers report `(healthy)` in `docker ps`
- [ ] MCP-1 (`henson_list_personas`): returns all 3 personas with correct schema
- [ ] MCP-2 (`henson_switch_session_persona`): happy path, edge cases, and error cases pass
- [ ] MCP-3 (`henson_chat_turn`): happy path, edge cases, and error cases pass
- [ ] UI T01–T21: core authentication and persona chat tests all pass
- [ ] UI T22–T43: see individual statuses; UNTESTED items tracked for Phase 2 follow-up
- [ ] ST-1: personas table seeded with 3 records matching REQ-henson §4.3
- [ ] ST-2/ST-3: `active_persona_id` written and updated correctly in `active_sessions`
- [ ] ST-4/ST-5: Rogers IDs created on first turn and reused (not re-created) on subsequent turns
- [ ] ST-6: FK constraint on `active_sessions.active_persona_id` enforced by database
- [ ] Container logs: no unexpected ERROR-level output in any container
- [ ] Network isolation: `henson-langgraph` cannot reach `joshua-net` directly; gateway peer proxy path functional
- [ ] REQ-henson.md is up-to-date and accurately reflects deployed state
- [ ] EX-HENSON-002 (Open WebUI anonymous volume suppression) documented and working
- [ ] EX-HENSON-003 (`henson-postgres` UID 70 exception) documented and working

---

**Related:**
[REQ-henson](./REQ-henson.md) · [HLD: Human Interaction Layer](./HLD-henson-chat-hub.md) · [MAD Testing Guide](../../docs/guides/mad-testing-guide.md) · [MAD Deployment Guide](../../docs/guides/mad-deployment-guide.md)
