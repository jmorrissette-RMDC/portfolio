# MAD Testing Guide

**Purpose:** This guide defines the standard procedures for designing and executing comprehensive tests for pMADs in the Joshua26 ecosystem during the deployment phase. It outlines a two-tiered approach to ensure that every tool is fully functional and integrates correctly within the system.

---

## 1. Introduction: Two Tiers of Testing

Ensuring a MAD works correctly involves more than just checking if its public interface responds. It requires verifying that the internal state of the system is updated as expected. This guide distinguishes between two levels of testing:

1.  **Interface & Contract Testing (Black-Box):** Validates the MAD's public-facing MCP tools and their immediate responses.
2.  **Integration & State Verification Testing (Gray-Box):** Confirms that internal system state changes (e.g., database writes, file creations) occur correctly after a tool invocation.

Both tiers are essential for a complete verification of MAD functionality.

---

## 2. General Testing Principles

-   **Reproducibility:** Tests should produce the same results every time they are run with the same inputs.
-   **Automation First:** Prioritize automated testing where feasible, using scripts for repetitive checks.
-   **Thoroughness:** Cover not just the "happy path" but also edge cases, invalid inputs, and error conditions.
-   **Clarity:** Test results and procedures should be easy to understand and interpret.
-   **Logging:** Ensure detailed logs are available during testing for debugging purposes (`ADR-047`).

---

## 3. Tier 1: Interface & Contract Testing

This tier focuses on verifying the public interface of a MAD's MCP tools, typically performed from an external client (e.g., your local machine running `curl` or a Python `mcp_client`).

**Goal:** To confirm that each MCP tool responds correctly to valid inputs, handles invalid inputs gracefully, and adheres to its documented input/output schema.

### Methods

-   **Direct `curl` (for HTTP/SSE endpoints):** Useful for quick checks of `/health` and basic `POST /mcp` tool invocations.
    ```bash
    # Check health endpoint
    curl -s http://[mad-name]:[port]/health | python3 -m json.tool

    # Example: Invoke a tool via POST /mcp (sessionless mode, JSON-RPC 2.0)
    curl -s -X POST -H "Content-Type: application/json" 
         -d '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"[tool-name]","arguments":{"param1":"value1"}},"id":"1"}' 
         http://[mad-name]:[port]/mcp | python3 -m json.tool
    ```

-   **Direct MCP POST (sessionless):** The standard way to invoke MCP tools. pMADs on `joshua-net` accept sessionless `POST /mcp` calls directly — no relay required. SAM relay is deprecated (2026-02-26); do not use it for new testing.
    ```bash
    # Sessionless MCP tool call — direct to pMAD gateway
    curl -s -X POST -H "Content-Type: application/json" \
      -d '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"[tool-name]","arguments":{"param1":"value1"}},"id":"1"}' \
      http://[mad-name]:[port]/mcp | python3 -m json.tool
    ```

### Test Case Design

For each MCP tool, consider the following:

1.  **Happy Path:**
    *   **Input:** All required parameters with valid data.
    *   **Expected Output:** Successful JSON response, matching `outputSchema`, with correct data.
    *   **Example:** `conv_store_message` with a valid `conversation_id`, `role`, `sender_id`, and `content`. Expected: `{"message_id": "...", "conversation_id": "...", "sequence_number": 1}`.

2.  **Edge Cases:**
    *   **Input:** Empty strings, zero values, maximum length strings (if applicable), boundary conditions.
    *   **Expected Output:** Tool handles gracefully (e.g., returns empty list, default value, or specific error).
    *   **Example:** `mem_search` with an empty `query` string. Expected: `{"results": []}`.

3.  **Error Conditions (Invalid Inputs):**
    *   **Input:** Missing required parameters, incorrect data types (e.g., string where number expected), malformed JSON.
    *   **Expected Output:** Appropriate error message and status code (e.g., JSON-RPC 2.0 error response, HTTP 4xx).
    *   **Example:** `conv_store_message` with a missing `conversation_id`. Expected: `{"jsonrpc":"2.0","error":{"code":-32602,"message":"Invalid params"},"id":"1"}`.

4.  **Performance & Timeouts:**
    *   **Input:** Long-running operations, or simulating network delays.
    *   **Expected Output:** Tool completes within acceptable time, or times out gracefully with an error.
    *   **Example:** Call a computationally intensive `embed_text` tool with a very long text. Expected: Completion within X seconds, or a timeout error.

--- 

## 4. Tier 2: Integration & State Verification Testing

This tier goes beyond the public interface to verify that the internal components and data stores of the MAD (and its backing services) are correctly updated after a tool call.

**Goal:** To confirm that the side-effects of a tool invocation match the expected system behavior and data models defined in the MAD's `REQ` document and relevant `HLD`s.

### Methods

These tests often require direct access to the deployment host and containers.

1.  **SSH into the Target Host:**
    ```bash
    ssh aristotle9@[host-ip]
    ```

2.  **Inspect Container Logs:** Check `stdout`/`stderr` for expected log entries, warnings, or errors (`ADR-047`).
    ```bash
    docker logs [mad-name] --tail 50
    docker logs [mad-name]-langgraph --tail 50
    ```

3.  **Execute Commands inside Containers (`docker exec`):** Run commands directly within the MAD or its backing service containers to inspect their state.

4.  **Database Inspection:**
    *   **PostgreSQL (`[mad]-postgres`):** Connect to `psql` to query tables and verify data.
        ```bash
        docker exec -it [mad-name]-postgres psql -U postgres -d [database-name]
        # Inside psql:
        SELECT * FROM conversation_messages WHERE conversation_id = 'test_conversation_123';
        ```
    *   **Neo4j (`[mad]-neo4j`):** Use `cypher-shell` to query the graph database.
        ```bash
        docker exec -it [mad-name]-neo4j cypher-shell -u neo4j -p [password]
        # Inside cypher-shell:
        MATCH (n:ConversationTurn {session_id: 'test_session_123'}) RETURN n;
        ```
    *   **Redis (`[mad]-redis`):** Use `redis-cli` to inspect keys, lists, or hash sets.
        ```bash
        docker exec -it [mad-name]-redis redis-cli
        # Inside redis-cli:
        LRANGE [queue-name] 0 -1
        GET [key-name]
        ```

5.  **Filesystem Checks:** Verify files are created, modified, or deleted in expected locations.
    ```bash
    docker exec [mad-name] ls -la /workspace/[mad-name]/data/
    docker exec [mad-name] cat /storage/config/[mad-name]/logging.json
    ```

6.  **Network Inspection:** Verify network isolation and connectivity (`ADR-046`, `ADR-053`).
    ```bash
    docker network inspect joshua-net
    docker network inspect [mad-name]-net
    ```

### Test Case Design

Each state verification test should follow a pattern:

1.  **Pre-Condition:** Describe the expected state of the system *before* the tool is called.
2.  **Action:** Invoke the MCP tool (e.g., using `mcp_client.py`).
3.  **Post-Condition:** Describe the expected state of the system *after* the tool call, including changes in databases, files, queues, etc.
    *   **Example (Rogers `conv_store_message`):**
        *   **Action:** Call `rogers_conv_store_message` with a new message.
        *   **Post-Condition:**
            1.  `rogers-postgres` database: A new row exists in `conversation_messages` with the correct content and `conversation_id`.
            2.  `rogers-neo4j` database: If memory extraction occurs, new nodes and relationships reflecting entities from the turn are present.
            3.  `rogers-redis` queue: If asynchronous processing is used, a message for embedding/summarization is present in the appropriate Redis queue (and eventually processed).

--- 

## 5. Test Plan Template (Example)

This template can be adapted for each MAD and should be part of its `docs/` folder (e.g., `mads/[mad-name]/docs/TEST-PLAN-[mad-name].md`).

```markdown
# TEST PLAN: [MAD Name]

**MAD Group:** [mad-name] **Version:** [X.Y.Z] **Date:** [YYYY-MM-DD]

---

## 1. Environment Setup

- [ ] Ensure [mad-name] pMAD group is deployed on [host-name] (`[host-ip]`)
- [ ] Verify all containers in the pMAD group are `(healthy)`: `docker ps --filter "label=mad.logical_actor=[mad-name]"`
- [ ] Confirm SAM relay is running and connected to [mad-name].

## 2. Tier 1: Interface & Contract Tests

### Tool: `[domain]_[action_1]`

-   **Test Case 1.1: Happy Path - Basic functionality**
    -   **Input:** `{"param1": "value", "param2": 123}`
    -   **Expected Output:** `{"success": true, "result": "..."}`
    -   **Command:** (e.g., `mcp_client.py call [mad-name]_[action_1] ...` or `curl ...`)

-   **Test Case 1.2: Edge Case - Empty input (if applicable)**
    -   **Input:** `{"param1": ""}`
    -   **Expected Output:** (e.g., empty array, default value, or specific error if invalid)

-   **Test Case 1.3: Error Condition - Missing required parameter**
    -   **Input:** `{"param2": 123}` (missing `param1`)
    -   **Expected Output:** JSON-RPC error `(-32602, Invalid params)`

### Tool: `[domain]_[action_2]` (and so on for all tools)

-   ...

## 3. Tier 2: Integration & State Verification Tests

### Tool: `[domain]_[action_X]` (e.g., `rogers_conv_store_message`)

-   **Test Case 2.1: Data Persistence - New record creation**
    -   **Action:** Call `[domain]_[action_X]` with a new data entry.
    -   **Verification (on host via SSH):**
        ```bash
        # Example for PostgreSQL
        docker exec -it [mad-name]-postgres psql -U [user] -d [db-name] -c 
            "SELECT column1, column2 FROM table_name WHERE id='[expected-id]';"
        # Expected: Row exists with correct data
        ```

-   **Test Case 2.2: Data Update - Existing record modification**
    -   **Action:** Call `[domain]_[action_X]` to update an existing entry.
    -   **Verification (on host via SSH):**
        ```bash
        # Example for Neo4j
        docker exec -it [mad-name]-neo4j cypher-shell -u neo4j -p [password] -c 
            "MATCH (n:Node {id: '[expected-id]'}) RETURN n.property;"
        # Expected: Property updated to new value
        ```

-   **Test Case 2.3: File System Side-Effect (if applicable)**
    -   **Action:** Call a tool that creates or modifies a file.
    -   **Verification (on host via SSH):**
        ```bash
        docker exec [mad-name] ls -la /workspace/[mad-name]/files/output.json
        docker exec [mad-name] cat /workspace/[mad-name]/files/output.json
        # Expected: File exists with correct content and permissions
        ```

## 4. Overall Verification

- [ ] All required documentation is up-to-date (README.md, REQ-*.md).
- [ ] Logs show no unexpected errors or warnings (`docker logs [mad-name]`).
- [ ] Health endpoints for all containers report `(healthy)`.

---

---

## 6. Test-Fix Log

Every MAD's `tests/` directory must contain a `TEST-RESULTS.md` file. This is a
**running log** of every test run, every failure found, and every fix applied. It is
the authoritative record of the MAD's test history and must be updated after every
test run.

### Purpose

- Prevents losing institutional knowledge when plan files or context windows are reset
- Provides a traceable history of what broke, when, and how it was fixed
- Makes regressions visible: if a test that was passing is now failing, the log shows when it last passed

### Format

Each entry is appended to the top of the file (newest first):

```markdown
## YYYY-MM-DD — <brief description of what was run or changed>

**Command:** `<exact command used to run tests>`
**Results:** X passed, Y failed (Z skipped)

### Failures
- `<test-name>`: <what failed and why>

### Fixes Applied
- `<file>`: <what was changed and why>

### Notes
<any other relevant observations>
```

### Location

`mads/[mad-name]/tests/TEST-RESULTS.md`

### Master Index

| MAD | Test Results Log |
|---|---|
| Apgar | `mads/apgar/tests/TEST-RESULTS.md` |
| Henson | `mads/henson/tests/TEST-RESULTS.md` |
| Rogers | `mads/rogers/tests/TEST-RESULTS.md` |
| Sutherland | `mads/sutherland/tests/TEST-RESULTS.md` |

### Rules

- **Always update after a test run** — even if all tests pass (record the pass)
- **Record fixes inline** — when a test fails and you fix it, record both the failure and the fix in the same entry
- **Never delete old entries** — the log is append-only; history is valuable
- **Link to commits** — include the git commit hash when a fix is committed

---

**Related:** [Deployment Guide](./mad-deployment-guide.md) · [Gate Reviewer Guide](./mad-gate-reviewer-guide.md) · [MAD Coding Guide](./mad-coding-guide.md) · [REQ-000 System Requirements](../requirements/REQ-000-Joshua26-System-Requirements-Specification.md)
