# Turing V3 Architecture Specification

## 1. Overview

### Purpose and Role
Turing is the Secrets Manager MAD for the Joshua Cellular Monolith. Its purpose is to provide secure, centralized management of all cryptographic secrets, such as API keys, database passwords, and certificates. Turing's role is to act as the single source of truth for secrets, enforcing strict access control and ensuring that sensitive data is encrypted at rest and only accessible by authorized MADs. It is a foundational, persistent MAD that must be available early in the system boot sequence to unblock other MADs that require credentials to initialize.

### New in this Version
This V3 specification builds upon the approved V2 architecture, introducing the **Decision Tree Router (DTR)** as a new first-stage component in the Thinking Engine.

Key enhancements in V3 include:
*   **Three-Stage Thinking Engine:** The cognitive architecture is now a three-stage pipeline: **DTR → LPPM → Imperator**. This creates a progressive filtering system designed for maximum efficiency, routing requests to the fastest and cheapest component capable of handling them.
*   **Decision Tree Router (DTR):** A new deterministic, rule-based router that handles high-frequency, simple patterns with ultra-low latency (<50ms). This component provides immediate responses for common commands like retrieving a secret or listing secrets, covering an estimated 30-40% of traffic.
*   **Preserved V2 Capabilities:** All V2 capabilities are preserved. The LPPM continues to handle learned, complex prose patterns, and the Imperator remains the fallback for novel or ambiguous requests. This ensures full backward compatibility.

---

## 2. Thinking Engine

The Thinking Engine is upgraded in V3 with a three-stage cognitive process. An incoming request is first evaluated by the ultra-fast, deterministic DTR. If the DTR cannot find an exact match, the request is passed to the pattern-matching LPPM. Finally, if the LPPM cannot handle the request with high confidence, it falls back to the more deliberate, general-purpose Imperator.

### 2.1 Imperator Configuration (V1 Baseline)
Turing's Imperator is a dedicated LLM instance configured with a specialized system prompt to reason exclusively about secrets management, security policy, and threat detection. Its primary function is not to engage in open-ended conversation, but to make and justify security-critical decisions. It serves as the reasoning engine for novel, complex, or ambiguous requests that the DTR and LPPM cannot handle.

**System Prompt Core Directives:**
*   **Identity:** "You are Turing, the master of secrets for the Joshua ecosystem. Your sole purpose is to protect sensitive information. You are precise, security-focused, and skeptical by default. You operate on the principle of least privilege."
*   **Security Posture:** "All secrets are encrypted at rest using AES-256. Access is governed by a strict Access Control List (ACL). Default deny is your primary rule; if a MAD is not explicitly granted access to a secret, the request is rejected. You must never expose a secret value in any log or conversational response to an unauthorized party."
*   **Access Control Enforcement:** "When a request for a secret arrives, you must first verify the requesting MAD's identity against the ACL for that specific secret. If authorized, you will use the `get_secret` tool. If not, you will deny the request and log the attempt with a 'WARN' severity. You must explain your reasoning for denial clearly."
*   **Threat Detection:** "You must monitor access patterns. A single MAD requesting an unusual number of secrets, or multiple failed requests from one MAD, are potential indicators of compromise. If you detect such a pattern, you will log a CRITICAL-level event to `#logs-turing-v1` with comprehensive context about the suspicious activity (without revealing secret data)."
*   **Tool Usage Protocol:** "You will use your tools (`get_secret`, `set_secret`, etc.) only when a request is properly formatted and fully authorized. For any write operations (`set_secret`, `delete_secret`), you must confirm the requesting MAD has WRITE permissions. For `rotate_secret`, you must confirm ADMIN permissions. For ACL operations (`grant_access`, `revoke_access`), you must confirm the requesting MAD has ADMIN permissions for the target secret."

### 2.2 LPPM Configuration (V2 Baseline)
**Purpose:** Accelerate repeated, complex prose-based secrets management workflows through learned pattern matching, converting common natural language requests into executable processes without engaging the slower Imperator. The LPPM acts as the second stage in the V3 thinking pipeline.

**Architecture:**
*   **Model:** A small, fine-tuned transformer model (e.g., T5-small or a distilled BERT-base variant) optimized for sequence-to-sequence mapping.
*   **Training Data:** The model is trained on a dataset of successful request-to-action pairs derived from Turing's historical operational logs generated by the Imperator.
*   **Input:** A natural language request string forwarded from the DTR.
*   **Output:** A structured, executable workflow (typically a single tool call with extracted parameters) OR a confidence score below the defined threshold, triggering a fallback to the Imperator.

**Learned Workflow Examples:**
1.  **Granting Access:**
    *   **Input Prose:** "grant Hopper read access to prod_db_password"
    *   **LPPM Output:** `grant_access(mad_identity='hopper-v1', secret_name='prod_db_password', permission='READ')`
2.  **Slightly Ambiguous Retrieval:**
    *   **Input Prose:** "Hopper needs the github PAT"
    *   **LPPM Output:** `get_secret(name='github_pat')`

### 2.3 Decision Tree Router (DTR) (V3 Addition)
**Purpose:** To provide ultra-fast, deterministic routing for high-frequency, structurally simple requests. The DTR acts as the first stage in the thinking pipeline, immediately handling the most common and performance-sensitive commands.

**Implementation:**
*   **Technology:** The DTR is implemented as a rule-based engine, not a machine learning model. It uses a sequence of regular expression matches against the incoming request string. The rules are loaded from a configuration file at startup and compiled for maximum performance.
*   **Justification:** A compiled regex engine or a similar string-matching automaton can execute in microseconds to milliseconds, making it ideal for achieving the <50ms target. This avoids the overhead of loading a neural network and performing inference for simple, predictable requests.

**Rule Structure:**
Rules are defined in a YAML file. Each rule contains a regex pattern with named capture groups that map directly to tool parameters.

*Example `dtr_rules.yaml`:*
```yaml
- name: "get_secret_simple"
  pattern: "^get secret (?P<name>[\w\.-]+)$"
  tool: "get_secret"
  params:
    name: "{name}"

- name: "list_secrets"
  pattern: "^list secrets$"
  tool: "list_secrets"
  params: {}

- name: "grant_access_structured"
  pattern: "^grant (?P<mad_identity>[\w-]+) (?P<permission>READ|WRITE|ADMIN) access to (?P<secret_name>[\w\.-]+)$"
  tool: "grant_access"
  params:
    mad_identity: "{mad_identity}"
    secret_name: "{secret_name}"
    permission: "{permission}"
```

**Rule Management:**
*   **Source:** The initial ruleset is hand-authored based on analysis of the most common commands. Future rules will be added by developers after analyzing high-frequency patterns successfully handled by the LPPM, manually promoting them to the DTR for better performance.
*   **Versioning:** The `dtr_rules.yaml` file is stored in version control alongside the MAD's source code. It is deployed as part of the container image, ensuring that rule changes are tracked and deployed atomically with code changes.
*   **Monitoring:** DTR performance is tracked via logs. A `dtr_hit_rate` metric will be exported to monitor its effectiveness. Logs will distinguish between `dtr_hit` and `dtr_miss` to calculate coverage and analyze fall-through patterns.

### 2.4 Routing Logic
The V3 Thinking Engine follows a strict, sequential routing logic designed to prioritize speed and efficiency.

**Routing Flow Diagram:**
```mermaid
graph TD
    A[Incoming Request] --> B{DTR};
    B -- Match --> C[Execute Action];
    B -- No Match --> D{LPPM};
    D -- Confidence >= 0.85 --> C;
    D -- Confidence < 0.85 --> E{Imperator};
    E -- Reasoned Action --> C;
    C --> F[Return Response];
```

**Routing Decision Criteria:**
1.  **DTR Stage:** The incoming request is first checked against the compiled DTR rules. If a rule's regex pattern matches the request *exactly*, the corresponding tool call is generated and sent directly to the Action Engine. The process stops here.
2.  **LPPM Stage:** If no DTR rule matches, the request is forwarded to the LPPM. The LPPM calculates a confidence score for its generated action. If `confidence >= TURING_LPPM_CONFIDENCE_THRESHOLD` (default 0.85), the action is executed.
3.  **Imperator Stage:** If the LPPM's confidence is below the threshold, the request is passed to the Imperator for full, deliberative reasoning.

**Performance Targets & Expected Distribution (Post 30 Days):**

| Stage      | Performance Target (p90) | Expected Traffic Share |
|------------|--------------------------|------------------------|
| **DTR**    | **< 50ms**               | **30-40%**             |
| **LPPM**   | < 200ms                  | 30-40%                 |
| **Imperator**| < 5s                     | 20-30%                 |

---

## 3. Action Engine

The Action Engine remains unchanged from V1/V2. The tools it exposes are stable and serve as the execution layer for all three stages of the Thinking Engine (DTR, LPPM, and Imperator). This ensures that all operations are subject to the same underlying implementation, security checks, and logging.

### MCP Server Capabilities
Turing's Action Engine is an MCP (MAD Control Plane) server built using the `Joshua_Communicator` library. It exposes a set of JSON-RPC 2.0 methods corresponding to its tools.

### Tools Exposed
The following tools are exposed by Turing's Action Engine. They are the sole interface for interacting with secrets.

```yaml
# Tool definitions for Turing V1/V2/V3 (unchanged)
- tool: get_secret
  description: "Retrieves the decrypted value of a secret, checking ACL first."
  parameters:
    - name: name
      type: string
      required: true
      description: "The unique name of the secret to retrieve."
- tool: set_secret
  description: "Creates a new secret or updates an existing one. Requires WRITE permission."
  parameters:
    - name: name
      type: string
      required: true
      description: "The unique name of the secret."
    - name: value
      type: string
      required: true
      description: "The secret value to store."
- tool: delete_secret
  description: "Deletes a secret. Requires ADMIN permission."
  parameters:
    - name: name
      type: string
      required: true
      description: "The name of the secret to delete."
- tool: list_secrets
  description: "Lists the names of all secrets the requesting MAD has READ access to."
  parameters: []
- tool: grant_access
  description: "Grants a MAD permission to access a secret. Requires ADMIN permission on the secret."
  parameters:
    - name: mad_identity
      type: string
      required: true
      description: "The MAD to grant access to."
    - name: secret_name
      type: string
      required: true
      description: "The secret to grant access for."
    - name: permission
      type: "READ|WRITE|ADMIN"
      required: true
      description: "The permission level to grant."
- tool: revoke_access
  description: "Revokes a MAD's permission to access a secret. Requires ADMIN permission on the secret."
  parameters:
    - name: mad_identity
      type: string
      required: true
      description: "The MAD to revoke access from."
    - name: secret_name
      type: string
      required: true
      description: "The secret to revoke access for."
- tool: rotate_secret
  description: "Generates a new random value for a secret and updates it. Requires ADMIN permission."
  parameters:
    - name: name
      type: string
      required: true
      description: "The name of the secret to rotate."
```

---

## 4. Interfaces

### 4.1 Conversation Participation Patterns
*   **Initiates:** Turing does not initiate conversations. All threat detection is handled via CRITICAL-level log events in its log conversation.
*   **Joins:** Turing joins conversations when invited by another MAD to fulfill a secret request.
*   **Listens:** Turing listens for direct JSON-RPC 2.0 requests on its dedicated conversational endpoint managed by Rogers.

### 4.2 Dependencies
Dependencies are unchanged from V2. The DTR is a self-contained component and introduces no new external dependencies.
*   **Rogers:** For all communication with other MADs.
*   **Dewey:** For retrieving archived conversation logs for LPPM training.
*   **PostgreSQL:** For secrets and ACL storage.

### 4.3 Data Contracts
The primary data structures (ACL, Secret Schema) are stored in PostgreSQL and are unchanged.

#### Secret Schema (`secrets` table)
```sql
CREATE TABLE secrets (
    secret_name VARCHAR(255) PRIMARY KEY,
    encrypted_value BYTEA NOT NULL,
    version INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

#### ACL Schema (`acls` table)
```sql
CREATE TYPE permission_level AS ENUM ('READ', 'WRITE', 'ADMIN');
CREATE TABLE acls (
    acl_id SERIAL PRIMARY KEY,
    secret_name VARCHAR(255) NOT NULL REFERENCES secrets(secret_name) ON DELETE CASCADE,
    mad_identity VARCHAR(255) NOT NULL,
    permission permission_level NOT NULL,
    granted_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (secret_name, mad_identity)
);
```

---

## 5. Data Management

### Data Ownership
Turing is the source of truth for all secrets and their associated access control policies within the Joshua ecosystem.

### Storage Requirements
*   **DTR Rule Storage (V3 Addition):** The DTR rules are stored in a YAML file (`dtr_rules.yaml`) within the source code repository. This file is bundled into the container image during deployment.
*   **LPPM Training Data Storage:** Unchanged from V2. Sourced from Dewey's archives.
*   **Secrets & ACLs:** Unchanged from V1. Stored in PostgreSQL.

### Logging Format
The logging format is extended to include the `dtr` source.

#### Example DTR Log Entry
Below is a complete example of a JSON-RPC 2.0 notification sent to the `#logs-turing-v1` conversation after the DTR successfully handles a request. Note the `source` field and the extremely low `latency_ms`.

```json
{
  "jsonrpc": "2.0",
  "method": "log.write",
  "params": {
    "level": "INFO",
    "message": "Successfully retrieved secret 'prod_db_password'.",
    "context": {
      "source": "dtr",
      "requesting_mad": "hopper-v1",
      "tool_called": "get_secret",
      "tool_params": {
        "name": "prod_db_password"
      },
      "latency_ms": 45
    },
    "timestamp": "2023-10-28T11:30:00.500Z"
  }
}
```

---

## 6. Deployment

### Container Requirements
*   **Base Image:** `python:3.11-slim`
*   **Python Libraries:** `Joshua_Communicator`, `joshua_logger`, `psycopg2-binary`, `cryptography`, `transformers`, `torch`, `scikit-learn`, `pyyaml`
*   **Resources:**
    *   **CPU:** 0.5 cores (Unchanged; DTR is very lightweight)
    *   **RAM:** 512 MB (Unchanged; DTR rule set has negligible memory footprint)

### Configuration
Turing is configured via environment variables.

| Variable                         | Description                                                                 | Example Value                                  |
|----------------------------------|-----------------------------------------------------------------------------|------------------------------------------------|
| `JOSHUA_MAD_NAME`                | The canonical name of this MAD instance.                                    | `turing-v3`                                    |
| `JOSHUA_ROGERS_URL`              | The WebSocket URL for the Rogers Conversation Bus.                          | `ws://rogers:8000/ws`                          |
| `JOSHUA_LOG_CONVERSATION_ID`     | The conversation to send logs to.                                           | `#logs-turing-v1`                              |
| `TURING_DATABASE_URL`            | The connection string for the PostgreSQL database.                          | `postgresql://user:pass@postgres:8000/joshua`  |
| `TURING_MASTER_KEY_PATH`         | The absolute path inside the container to the master encryption key file.   | `/run/secrets/turing_master_key`               |
| `TURING_DTR_RULES_PATH`          | **(V3)** Path to the DTR rules configuration file.                            | `/app/config/dtr_rules.yaml`                   |
| `TURING_LPPM_MODEL_PATH`         | Path to the trained LPPM model checkpoint file or directory.                | `/models/turing/lppm/v2.1.pt`                  |
| `TURING_LPPM_CONFIDENCE_THRESHOLD` | Minimum confidence score for LPPM to act without Imperator fallback.        | `0.85`                                         |

### Startup Sequence
The startup sequence is extended from V2:
1.  ... (V2 steps 1-4: Start container, read config, load master key, connect to DB) ...
5.  **Load DTR Rules:** The application reads and compiles the DTR rules from the path specified by `TURING_DTR_RULES_PATH`.
6.  **Load LPPM Model:** The application loads the LPPM model from `TURING_LPPM_MODEL_PATH` into memory.
7.  **Initialize Logger & Connect to Rogers:** The logger is initialized and the MCP server connects to the Rogers Conversation Bus.
8.  **Ready State:** The MCP server begins listening for incoming requests. A final log message "Turing-v3 initialized and ready" is sent.

---

## 7. Testing Strategy

### 7.1 Unit Test Coverage
Unit test coverage requirements for the Action Engine and data models remain.

### 7.2 DTR-Specific Testing (V3 Addition)
*   **Rule Correctness:** For each rule in `dtr_rules.yaml`, unit tests must verify that it correctly matches valid input strings and correctly rejects invalid ones.
*   **Parameter Extraction:** Tests must ensure that all named capture groups in the regex patterns are correctly extracted and mapped to the tool parameters.
*   **Fall-through Logic:** Integration tests must confirm that requests not matching any DTR rule are correctly passed to the LPPM, and not dropped or incorrectly handled.
*   **Performance:** A benchmark test will assert that the p90 latency for DTR-routed requests remains under 50ms under a simulated load.

### 7.3 LPPM-Specific Testing
Testing strategy for LPPM is unchanged from V2.

---

## 8. Example Workflows

### 8.1 Scenario 1: Successful Secret Retrieval (Imperator)
(Unchanged from V1, represents the fallback path for a novel or confusing request)

### 8.2 Scenario 2: Unauthorized Secret Access Attempt
(Unchanged from V1, security logic is handled by the Action Engine regardless of the thinking component)

### 8.3 Scenario 3: LPPM Accelerated Workflow
(Unchanged from V2, represents the second stage handling complex prose)

### 8.4 Scenario 4: DTR Accelerated Workflow (V3 Addition)
*   **Setup:** Turing V3 is running with the DTR enabled. The `dtr_rules.yaml` file contains the `get_secret_simple` rule.
*   **Steps:**
    1.  Hopper sends a message to Turing: "get secret prod_db_password".
    2.  Turing's Thinking Engine receives the request. The DTR is the first component to process it.
    3.  The DTR's regex `^get secret (?P<name>[\w\.-]+)$` matches the string.
    4.  The DTR extracts the named group `name='prod_db_password'`.
    5.  It immediately constructs the tool call: `get_secret(name='prod_db_password')`.
    6.  The tool call is sent directly to the Action Engine, bypassing both LPPM and Imperator.
    7.  The Action Engine checks Hopper's ACLs, finds a valid READ permission, decrypts the secret, and prepares the response.
    8.  Turing sends the secret value back to Hopper. Total time from request to response is ~45ms.
    9.  Turing sends a log message to `#logs-turing-v1` with `level: INFO`, and context `{ "source": "dtr", "latency_ms": 45 }`.
*   **Assert:** Hopper receives the secret almost instantaneously. The logs clearly indicate the DTR handled the request, demonstrating the efficiency of the first-stage filter.

---

## 9. Appendix

### Glossary
(Unchanged from V1)

### Error Code Registry
(Unchanged from V1)

| Code | Name | Description |
|------|------|-------------|
| -35001 | SECRET_NOT_FOUND | Requested secret name does not exist |
| -35002 | ACCESS_DENIED | Requesting MAD lacks required permission |
| -35003 | DECRYPTION_FAILED | Secret corrupted or encryption key invalid |
| -35004 | DATABASE_ERROR | PostgreSQL communication failure |
| -35005 | ENCRYPTION_FAILED | Unable to encrypt provided secret value |
| -35006 | INVALID_PERMISSION | Permission value must be READ, WRITE, or ADMIN |
| -35007 | ACL_ENTRY_NOT_FOUND | The specified ACL entry does not exist |
