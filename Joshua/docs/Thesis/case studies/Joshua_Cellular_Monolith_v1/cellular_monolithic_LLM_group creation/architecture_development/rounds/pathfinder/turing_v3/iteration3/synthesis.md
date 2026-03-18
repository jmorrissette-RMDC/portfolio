# Turing V3 Architecture Specification

## 1. Overview

### Purpose and Role
Turing is the Secrets Manager MAD for the Joshua Cellular Monolith. Its purpose is to provide secure, centralized management of all cryptographic secrets, such as API keys, database passwords, and certificates. Turing's role is to act as the single source of truth for secrets, enforcing strict access control and ensuring that sensitive data is encrypted at rest and only accessible by authorized MADs. It is a foundational, persistent MAD that must be available early in the system boot sequence to unblock other MADs that require credentials to initialize.

### New in this Version
This V3 specification builds upon the approved V2 architecture, introducing the **Decision Tree Router (DTR)** as a new first-stage component in the Thinking Engine.

Key enhancements in V3 include:
*   **Three-Stage Thinking Engine:** The cognitive architecture is now a three-stage pipeline: **DTR → LPPM → Imperator**. This creates a progressive filtering system designed for maximum efficiency, routing requests to the fastest and cheapest component capable of handling them.
*   **Decision Tree Router (DTR):** A new lightweight, machine learning classifier that learns to handle high-frequency, simple patterns with ultra-low latency (<10 microseconds). This component provides immediate responses for common commands like retrieving a secret or listing secrets, covering an estimated 30-40% of traffic after training.
*   **Preserved V2 Capabilities:** All V2 capabilities are preserved. The LPPM continues to handle learned, complex prose patterns, and the Imperator remains the fallback for novel or ambiguous requests. This ensures full backward compatibility.

---

## 2. Thinking Engine

The Thinking Engine is upgraded in V3 with a three-stage cognitive process. An incoming request is first evaluated by the ultra-fast, learning-based DTR. If the DTR cannot classify the request as a direct action with high confidence, it is passed to the pattern-matching LPPM. Finally, if the LPPM cannot handle the request with high confidence, it falls back to the more deliberate, general-purpose Imperator.

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
**Purpose:** To provide ultra-fast, machine learning-based classification and routing for high-frequency, structurally simple requests. The DTR acts as the first stage in the thinking pipeline, learning to immediately handle the most common and performance-sensitive commands.

**Architecture:**
*   **Model:** A lightweight classifier, such as a gradient-boosted decision tree ensemble (e.g., XGBoost) or a small, highly optimized neural network. The model is designed for CPU inference to achieve the strict microsecond-level latency target.
*   **Input Features:** The classifier operates on a vectorized representation of the incoming request, including features like message length, keyword presence/counts (e.g., "get", "secret", "list"), structural markers (e.g., number of quoted strings), and categorical features like the requesting MAD's identity.
*   **Output:** A routing decision (`DTR_DIRECT_EXECUTE` or `FORWARD_TO_LPPM`) and a confidence score. For `DTR_DIRECT_EXECUTE`, it also uses learned extraction rules (e.g., simple regexes or positional logic trained alongside the classifier) to populate tool parameters.
*   **Performance:** The model and feature extraction pipeline are optimized to execute in under **10 microseconds (µs)**.

**Training Pipeline:**
The DTR model is trained and updated weekly in an automated pipeline.
1.  **Data Source:** The pipeline sources successfully executed request-action pairs from the LPPM and Imperator logs stored in Dewey.
2.  **Feature Extraction:** Raw request strings are converted into the numeric feature vectors required by the model.
3.  **Label Generation:** Requests that were handled by the LPPM with high confidence (>0.95) and resulted in a simple, single-tool-call action are labeled as candidates for `DTR_DIRECT_EXECUTE`. All other requests are candidates for `FORWARD_TO_LPPM`.
4.  **Training:** The model is incrementally trained on the newly labeled data from the past week.
5.  **Validation:** Before deployment, the new model candidate must achieve >98% classification accuracy on a held-out validation dataset to ensure it does not introduce routing regressions.
6.  **Deployment:** Once validated, the model checkpoint is versioned and pushed to a model repository, from which the live Turing instances can pull the update.

**Learned Pattern Examples:**
After a few weeks of training on live traffic, the DTR will learn to classify and directly execute patterns such as:
*   Requests starting with `get secret` followed by a single, unquoted word are mapped directly to the `get_secret` tool.
*   The exact string `list secrets` is mapped directly to the `list_secrets` tool.
*   Highly structured requests like `grant hopper-v1 READ access to secret-name` are identified and routed directly to the `grant_access` tool with correctly extracted parameters.

**Key Difference from LPPM:**
*   **DTR:** A very fast binary classifier whose job is to answer one question: "Is this request a simple, known pattern I can execute directly?" It does not understand prose but recognizes learned structural patterns.
*   **LPPM:** A more complex sequence-to-sequence model that translates natural language prose into a structured tool call. It is slower but more flexible than the DTR.

### 2.4 Routing Logic
The V3 Thinking Engine follows a strict, sequential routing logic designed to prioritize speed and efficiency.

**Routing Flow Diagram:**
```mermaid
graph TD
    A[Incoming Request] --> B{DTR};
    B -- Confidence >= 0.90 --> C[Execute Action];
    B -- Confidence < 0.90 --> D{LPPM};
    D -- Confidence >= 0.85 --> C;
    D -- Confidence < 0.85 --> E{Imperator};
    E -- Reasoned Action --> C;
    C --> F[Return Response];
```

**Routing Decision Criteria:**
1.  **Stage 1: DTR Classification:** The incoming request is featurized and evaluated by the DTR classifier. If the model classifies the request as `DTR_DIRECT_EXECUTE` with a confidence score `> 0.90`, the corresponding tool call is generated using learned extraction rules and sent to the Action Engine. The process stops here.
2.  **Stage 2: LPPM Pattern Matching:** If the DTR forwards the request, it is passed to the LPPM. The LPPM generates a tool call and a confidence score. If `confidence >= TURING_LPPM_CONFIDENCE_THRESHOLD` (default 0.85), the action is executed.
3.  **Stage 3: Imperator Fallback (Final Stage):** If the LPPM's confidence is below the threshold, the request is forwarded to the Imperator for full, deliberative reasoning. The Imperator serves as the universal fallback and **always** provides a response. It will either:
    *   Successfully map the request to a tool call and execute it.
    *   Engage in a clarifying dialogue with the requesting MAD if the request is ambiguous.
    *   Return a well-defined error response if the request is malformed, unauthorized, or impossible to fulfill.
    There is no scenario where a request "fails" through all three stages without a definitive response.

**Performance Targets & Expected Distribution (Post 30 Days):**

| Stage      | Performance Target (p90) | Expected Traffic Share |
|------------|--------------------------|------------------------|
| **DTR**    | **< 10 µs**              | **30-40%**             |
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
Dependencies are unchanged from V2. The DTR is a self-contained component and introduces no new external dependencies beyond its training pipeline requirements.
*   **Rogers:** For all communication with other MADs.
*   **Dewey:** For retrieving archived conversation logs for DTR and LPPM training.
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
*   **DTR Model Storage (V3 Addition):** The trained DTR model checkpoints are stored in a versioned model repository (e.g., an S3 bucket or similar artifact store). The container pulls the specified model version on startup.
*   **LPPM Training Data Storage:** Unchanged from V2. Sourced from Dewey's archives.
*   **Secrets & ACLs:** Unchanged from V1. Stored in PostgreSQL.

### Logging Format
The logging format is extended to include the `dtr` source and microsecond-level latency.

#### Example DTR Log Entry
Below is a complete example of a JSON-RPC 2.0 notification sent to the `#logs-turing-v1` conversation after the DTR successfully handles a request. Note the `source` field and the extremely low `latency_us`.

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
      "latency_us": 8
    },
    "timestamp": "2023-10-28T11:30:00.500Z"
  }
}
```

---

## 6. Deployment

### Container Requirements
*   **Base Image:** `python:3.11-slim`
*   **Python Libraries:** `Joshua_Communicator`, `joshua_logger`, `psycopg2-binary`, `cryptography`, `transformers`, `torch`, `scikit-learn`, `xgboost`
*   **Resources:**
    *   **CPU:** 0.5 cores (Unchanged; DTR inference is very lightweight)
    *   **RAM:** 512 MB (Unchanged; DTR model has a small memory footprint)

### Configuration
Turing is configured via environment variables.

| Variable                         | Description                                                                 | Example Value                                  |
|----------------------------------|-----------------------------------------------------------------------------|------------------------------------------------|
| `JOSHUA_MAD_NAME`                | The canonical name of this MAD instance.                                    | `turing-v3`                                    |
| `JOSHUA_ROGERS_URL`              | The WebSocket URL for the Rogers Conversation Bus.                          | `ws://rogers:8000/ws`                          |
| `JOSHUA_LOG_CONVERSATION_ID`     | The conversation to send logs to.                                           | `#logs-turing-v1`                              |
| `TURING_DATABASE_URL`            | The connection string for the PostgreSQL database.                          | `postgresql://user:pass@postgres:8000/joshua`  |
| `TURING_MASTER_KEY_PATH`         | The absolute path inside the container to the master encryption key file.   | `/run/secrets/turing_master_key`               |
| `TURING_DTR_MODEL_PATH`          | **(V3)** Path to the trained DTR model checkpoint file.                       | `/models/turing/dtr/v1.2.bin`                  |
| `TURING_LPPM_MODEL_PATH`         | Path to the trained LPPM model checkpoint file or directory.                | `/models/turing/lppm/v2.1.pt`                  |
| `TURING_LPPM_CONFIDENCE_THRESHOLD` | Minimum confidence score for LPPM to act without Imperator fallback.        | `0.85`                                         |

### Startup Sequence
The startup sequence is extended from V2:
1.  ... (V2 steps 1-4: Start container, read config, load master key, connect to DB) ...
5.  **Load DTR Model:** The application loads the DTR classifier model from the path specified by `TURING_DTR_MODEL_PATH` into memory.
6.  **Load LPPM Model:** The application loads the LPPM model from `TURING_LPPM_MODEL_PATH` into memory.
7.  **Initialize Logger & Connect to Rogers:** The logger is initialized and the MCP server connects to the Rogers Conversation Bus.
8.  **Ready State:** The MCP server begins listening for incoming requests. A final log message "Turing-v3 initialized and ready" is sent.

---

## 7. Testing Strategy

### 7.1 Unit Test Coverage
Unit test coverage requirements for the Action Engine and data models remain.

### 7.2 DTR-Specific Testing (V3 Addition)
*   **Model Accuracy and Precision:** The DTR model must be evaluated against a held-out test set, ensuring it meets the >98% accuracy threshold before deployment. Precision and recall for the `DTR_DIRECT_EXECUTE` class will be closely monitored.
*   **Learned Extraction Logic:** Tests must verify that for requests correctly classified for direct execution, the associated parameter extraction logic correctly populates tool parameters.
*   **Fall-through Logic:** Integration tests must confirm that requests classified for forwarding (or those with low confidence) are correctly passed to the LPPM and not dropped.
*   **Performance:** A benchmark test will assert that the p90 latency for DTR-classified requests remains under **10 microseconds** under a simulated load.

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
*   **Setup:** Turing V3 is running with a trained DTR model that has learned to recognize simple `get secret` patterns.
*   **Steps:**
    1.  Hopper sends a message to Turing: "get secret prod_db_password".
    2.  Turing's Thinking Engine receives the request. The DTR is the first component to process it.
    3.  The DTR featurizes the input string and the classifier predicts `DTR_DIRECT_EXECUTE` with a confidence of 0.99.
    4.  The DTR's learned extraction logic identifies `prod_db_password` as the `name` parameter.
    5.  It immediately constructs the tool call: `get_secret(name='prod_db_password')`.
    6.  The tool call is sent directly to the Action Engine, bypassing both LPPM and Imperator.
    7.  The Action Engine checks Hopper's ACLs, finds a valid READ permission, decrypts the secret, and prepares the response.
    8.  Turing sends the secret value back to Hopper. Total time from request to response is ~8 µs.
    9.  Turing sends a log message to `#logs-turing-v1` with `level: INFO`, and context `{ "source": "dtr", "latency_us": 8 }`.
*   **Assert:** Hopper receives the secret almost instantaneously. The logs clearly indicate the DTR handled the request, demonstrating the efficiency of the first-stage classifier.

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
