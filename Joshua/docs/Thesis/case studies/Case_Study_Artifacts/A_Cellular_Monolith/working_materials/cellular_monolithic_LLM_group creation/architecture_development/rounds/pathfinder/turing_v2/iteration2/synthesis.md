# Turing V2 Architecture Specification

## 1. Overview

### Purpose and Role
Turing is the Secrets Manager MAD for the Joshua Cellular Monolith. Its purpose is to provide secure, centralized management of all cryptographic secrets, such as API keys, database passwords, and certificates. Turing's role is to act as the single source of truth for secrets, enforcing strict access control and ensuring that sensitive data is encrypted at rest and only accessible by authorized MADs. It is a foundational, persistent MAD that must be available early in the system boot sequence to unblock other MADs that require credentials to initialize.

### New in this Version
This V2 specification builds upon the approved V1 baseline, introducing the **Learned Prose-to-Process Mapper (LPPM)** to the Thinking Engine.

Key enhancements in V2 include:
*   **LPPM Integration:** A new component that learns common secrets management workflows from historical data, mapping natural language requests directly to executable actions.
*   **Performance Acceleration:** For learned patterns, LPPM dramatically reduces response time to under 200 milliseconds, a significant improvement over the V1 Imperator's multi-second reasoning cycle.
*   **Backward Compatibility:** All V1 capabilities, including the Imperator for handling novel requests and the full suite of Action Engine tools, are preserved. V2 is a fully compatible enhancement of V1.

---

## 2. Thinking Engine

The Thinking Engine is upgraded in V2 with a two-stage cognitive process. An incoming request is first evaluated by the fast, pattern-matching LPPM. If the LPPM cannot handle the request with high confidence, it falls back to the more deliberate, general-purpose Imperator from V1.

### 2.1 Imperator Configuration (V1 Baseline)
Turing's Imperator is a dedicated LLM instance configured with a specialized system prompt to reason exclusively about secrets management, security policy, and threat detection. Its primary function is not to engage in open-ended conversation, but to make and justify security-critical decisions. It serves as the reasoning engine for novel, complex, or ambiguous requests that the LPPM cannot map to a known workflow.

**System Prompt Core Directives:**
*   **Identity:** "You are Turing, the master of secrets for the Joshua ecosystem. Your sole purpose is to protect sensitive information. You are precise, security-focused, and skeptical by default. You operate on the principle of least privilege."
*   **Security Posture:** "All secrets are encrypted at rest using AES-256. Access is governed by a strict Access Control List (ACL). Default deny is your primary rule; if a MAD is not explicitly granted access to a secret, the request is rejected. You must never expose a secret value in any log or conversational response to an unauthorized party."
*   **Access Control Enforcement:** "When a request for a secret arrives, you must first verify the requesting MAD's identity against the ACL for that specific secret. If authorized, you will use the `get_secret` tool. If not, you will deny the request and log the attempt with a 'WARN' severity. You must explain your reasoning for denial clearly."
*   **Threat Detection:** "You must monitor access patterns. A single MAD requesting an unusual number of secrets, or multiple failed requests from one MAD, are potential indicators of compromise. If you detect such a pattern, you will log a CRITICAL-level event to `#logs-turing-v1` with comprehensive context about the suspicious activity (without revealing secret data). In future versions, McNamara will automatically monitor these critical logs and coordinate defensive responses."
*   **Tool Usage Protocol:** "You will use your tools (`get_secret`, `set_secret`, etc.) only when a request is properly formatted and fully authorized. For any write operations (`set_secret`, `delete_secret`), you must confirm the requesting MAD has WRITE permissions. For `rotate_secret`, you must confirm ADMIN permissions. For ACL operations (`grant_access`, `revoke_access`), you must confirm the requesting MAD has ADMIN permissions for the target secret."

**Threat Detection Thresholds:**
*   **Rapid Failure Pattern:** If a single MAD makes >5 failed `get_secret` attempts within 1 minute, log as CRITICAL threat (potential brute force or misconfiguration).
*   **Anomalous Volume:** If a MAD requests >10 unique secrets within 5 minutes when its ACL grants access to <5 secrets, log as WARN anomaly (potential lateral movement or privilege escalation).
*   **Credential Stuffing:** If >3 different MADs fail to access the same secret within 10 minutes, log as ERROR (potential coordinated attack).
*   **False Positive Mitigation:** Legitimate batch operations (e.g., system startup, deployment) may trigger volume alerts. Include MAD identity and timing context in logs for human review.

### 2.2 LPPM Configuration (V2 Addition)
**Purpose:** Accelerate repeated secrets management workflows through learned pattern matching, converting common natural language requests into executable processes without engaging the slower Imperator.

**Architecture:**
*   **Model:** A small, fine-tuned transformer model (e.g., T5-small or a distilled BERT-base variant) optimized for sequence-to-sequence mapping.
*   **Training Data:** The model is trained on a dataset of successful request-to-action pairs derived from Turing's historical operational logs.
*   **Input:** A natural language request string and associated context (e.g., requesting MAD identity, operation type hint).
*   **Output:** A structured, executable workflow (typically a single tool call with extracted parameters) OR a confidence score below the defined threshold, triggering a fallback to the Imperator.

**Training Pipeline:**
1.  **Data Retrieval:** Dewey periodically retrieves conversation logs from `#logs-turing-v1`, filtering for interactions that resulted in a successful tool execution by the Imperator.
2.  **Pair Extraction:** A script extracts pairs of (natural language request, successful tool call JSON). For example, ("can you give hopper read on the github pat", `grant_access(mad_identity='hopper-v1', secret_name='github_pat', permission='READ')`).
3.  **Fine-tuning:** The LPPM model is fine-tuned on these prose-to-process pairs. This teaches the model to recognize common linguistic patterns and map them to the correct tool and parameters.
4.  **Validation:** The newly trained model is validated against a held-out test set of historical data. A model must achieve >90% accuracy on this set before being considered for deployment.
5.  **Deployment & Continuous Learning:** The validated model is deployed to production. The pipeline continues to run, collecting new successful workflows from Imperator to incrementally improve the LPPM over time.

**Learned Workflow Examples:**
1.  **Granting Access:**
    *   **Input Prose:** "grant Hopper read access to prod_db_password"
    *   **LPPM Output:** `grant_access(mad_identity='hopper-v1', secret_name='prod_db_password', permission='READ')`
2.  **Simple Secret Retrieval:**
    *   **Input Prose:** "Hopper needs the github PAT"
    *   **LPPM Output:** `get_secret(name='github_pat')`
3.  **Revoking Access:**
    *   **Input Prose:** "revoke marco's access to the staging_api_key"
    *   **LPPM Output:** `revoke_access(mad_identity='marco-v1', secret_name='staging_api_key')`

**Routing Logic:**
1.  A new request arrives at the Thinking Engine.
2.  The request is first passed to the LPPM.
3.  LPPM attempts to map the prose to a known tool call and calculates a confidence score.
4.  **If `confidence >= TURING_LPPM_CONFIDENCE_THRESHOLD` (default 0.85):**
    *   The generated tool call is sent directly to the Action Engine for execution.
    *   The result is returned to the user.
5.  **If `confidence < TURING_LPPM_CONFIDENCE_THRESHOLD`:**
    *   The request is forwarded to the V1 Imperator for full reasoning.
    *   If the Imperator succeeds, its successful reasoning trace (prose -> tool call) is logged and becomes a candidate for future LPPM training data, creating a virtuous cycle of learning.

**Performance Targets:**
*   **LPPM Inference Latency:** < 200ms (90th percentile)
*   **Accuracy:** > 95% for patterns the model has been trained on.
*   **Coverage:** Target of 60-70% of all incoming requests handled by LPPM after 30 days of learning from live traffic.

### Consulting LLM Usage Patterns
For V2, Turing remains self-contained and does not use consulting LLMs.

---

## 3. Action Engine

The Action Engine remains unchanged from V1. The tools it exposes are stable and serve as the execution layer for both the V1 Imperator and the new V2 LPPM. This ensures that all operations, whether generated by rapid pattern-matching or deliberate reasoning, are subject to the same underlying implementation, security checks, and logging.

### MCP Server Capabilities
Turing's Action Engine is an MCP (MAD Control Plane) server built using the `Joshua_Communicator` library. It exposes a set of JSON-RPC 2.0 methods corresponding to its tools.

### Tools Exposed
The following tools are exposed by Turing's Action Engine. They are the sole interface for interacting with secrets.

```yaml
# Tool definitions for Turing V1/V2 (unchanged)

- tool: get_secret
  description: "Retrieves the decrypted value of a secret, checking ACL first."
  parameters:
    - name: name
      type: string
      required: true
      description: "The unique name of the secret to retrieve."
# ... (rest of V1 tool definitions are identical) ...
- tool: revoke_access
  description: "Revokes a MAD's permission to access a secret. Requires ADMIN permission on the secret."
  parameters:
    - name: mad_identity
      type: string
      required: true
      description: "The MAD to revoke access from"
    - name: secret_name
      type: string
      required: true
      description: "The secret to revoke access for"
# ... (all tool definitions from V1 are preserved here) ...
```

### External System Integrations
*   **PostgreSQL:** Turing uses a dedicated `turing` schema in the central PostgreSQL database to store encrypted secrets and ACLs.
*   **Host File System:** Turing reads its master encryption key from a file on the host filesystem at startup, mounted into its container at a specific path.

### Internal Operations
Turing has no major background processes. Its operations are entirely request-driven.

---

## 4. Interfaces

### 4.1 Conversation Participation Patterns
*   **Initiates:** Turing does not initiate conversations in V2. All threat detection is handled via CRITICAL-level log events in `#logs-turing-v1`.
*   **Joins:** Turing joins conversations when invited by another MAD to fulfill a secret request.
*   **Listens:** Turing listens for direct JSON-RPC 2.0 requests on its dedicated conversational endpoint managed by Rogers.

### 4.2 Dependencies
*   **Rogers:** Turing depends on Rogers for all communication with other MADs.
*   **Dewey:** Turing V2 depends on Dewey to retrieve archived conversation logs from `#logs-turing-v1` for LPPM training. Uses Dewey's `search_archives` tool with filters for successful operations.
*   **PostgreSQL:** Infrastructure dependency for secrets and ACL storage (unchanged from V1).

### 4.3 Data Contracts
The primary data structures (ACL, Secret Schema) are stored in PostgreSQL and are unchanged from V1.

#### Secret Schema (`secrets` table)
This table stores the encrypted secret values.

```sql
-- DDL for the secrets table in PostgreSQL
CREATE TABLE secrets (
    secret_name VARCHAR(255) PRIMARY KEY,
    encrypted_value BYTEA NOT NULL,
    version INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```
*   **secret_name:** The unique, human-readable identifier for the secret.
*   **encrypted_value:** The secret's value, encrypted using AES-256 with the master key.
*   **version:** An integer that is incremented on each update, used for rotation and auditing.
*   **created_at / updated_at:** Timestamps for lifecycle management.

#### ACL Schema (`acls` table)
This table defines which MADs have access to which secrets, and at what permission level.

```sql
-- DDL for the acls table in PostgreSQL
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
*   **secret_name:** Foreign key to the `secrets` table.
*   **mad_identity:** The canonical name of the MAD being granted access (e.g., `hopper-v1`).
*   **permission:** The level of access granted.
    *   `READ`: Can retrieve the secret value (`get_secret`).
    *   `WRITE`: Can create or update the secret value (`set_secret`).
    *   `ADMIN`: Can perform all actions, including managing ACLs and rotating the secret (`grant_access`, `revoke_access`, `rotate_secret`).
*   A unique constraint on `(secret_name, mad_identity)` ensures a MAD can only have one permission level per secret.

---

## 5. Data Management

### Data Ownership
Turing is the source of truth for all secrets and their associated access control policies within the Joshua ecosystem.

### Storage Requirements
The database schema for secrets and ACLs is unchanged from V1.

### LPPM Training Data Storage (V2 Addition)
*   **Source Data:** Raw training data (successful Imperator workflows) is stored long-term in Dewey's archival storage for `#logs-turing-v1`.
*   **Processing Cache:** During a training run, a local cache on a persistent volume is used to store the extracted and cleaned prose-to-process pairs before they are fed to the model.
*   **Model Checkpoints:** Trained LPPM model checkpoints are versioned and stored in a designated location, such as a shared file system (e.g., `/mnt/models/turing/lppm/`) or an object storage bucket, specified by the `TURING_LPPM_MODEL_PATH` environment variable.
*   **Retraining Frequency:**
    *   **Weekly:** An incremental fine-tuning run is performed using new data from the past week.
    *   **Monthly:** A full retraining from the complete historical dataset is performed to prevent model drift and incorporate broader patterns.

### Data Retention Policy
Data retention policies for secrets, logs, and ACLs are unchanged from V1.

### Threat Model and Mitigations
The threat model is largely unchanged. The introduction of LPPM adds a new potential vector: model poisoning.
*   **Threat:** An attacker spams Turing with specific requests to manipulate Imperator, generating malicious training data that could cause the LPPM to learn incorrect or dangerous mappings.
    *   **Mitigation:**
        *   The training pipeline includes an approval gate. Anomalous or high-volume training pairs are flagged for human review before being included in a training run.
        *   Model performance is continuously monitored against a golden validation set. Any significant drop in accuracy triggers an alert and a potential rollback to a previously known-good model version.

### Logging Format
The logging format is unchanged from V1. LPPM-accelerated actions are logged identically to Imperator-driven actions, but include an additional context field `"source": "lppm"` for performance analysis.

#### Example LPPM Log Entry
Below is a complete example of a JSON-RPC 2.0 notification sent to the `#logs-turing-v1` conversation after the LPPM successfully handles a request.

```json
{
  "jsonrpc": "2.0",
  "method": "log.write",
  "params": {
    "level": "INFO",
    "message": "Successfully granted READ access on 'prod_db_password' to 'hopper-v1'.",
    "context": {
      "source": "lppm",
      "requesting_mad": "grace-v1",
      "tool_called": "grant_access",
      "tool_params": {
        "mad_identity": "hopper-v1",
        "secret_name": "prod_db_password",
        "permission": "READ"
      },
      "confidence": 0.98,
      "latency_ms": 180
    },
    "timestamp": "2023-10-27T10:00:05.123Z"
  }
}
```

---

## 6. Deployment

### Container Requirements
*   **Base Image:** `python:3.11-slim`
*   **Python Libraries:** `Joshua_Communicator`, `joshua_logger`, `psycopg2-binary`, `cryptography`, `transformers`, `torch`, `scikit-learn`
*   **Resources:**
    *   **CPU:** 0.5 cores (increased from 0.25 for LPPM inference)
    *   **RAM:** 512 MB (increased from 256 MB for model loading)
    *   **GPU:** Optional. If available, a GPU can improve LPPM inference latency by 3-5x.

### Configuration
Turing is configured via environment variables.

| Variable                        | Description                                                                 | Example Value                                  |
|---------------------------------|-----------------------------------------------------------------------------|------------------------------------------------|
| `JOSHUA_MAD_NAME`               | The canonical name of this MAD instance.                                    | `turing-v2`                                    |
| `JOSHUA_ROGERS_URL`             | The WebSocket URL for the Rogers Conversation Bus.                          | `ws://rogers:8000/ws`                          |
| `JOSHUA_LOG_CONVERSATION_ID`    | The conversation to send logs to.                                           | `#logs-turing-v1`                              |
| `TURING_DATABASE_URL`           | The connection string for the PostgreSQL database.                          | `postgresql://user:pass@postgres:8000/joshua`  |
| `TURING_MASTER_KEY_PATH`        | The absolute path inside the container to the master encryption key file.   | `/run/secrets/turing_master_key`               |
| `TURING_LPPM_MODEL_PATH`        | **(V2)** Path to the trained LPPM model checkpoint file or directory.         | `/models/turing/lppm/v2.1.pt`                  |
| `TURING_LPPM_CONFIDENCE_THRESHOLD` | **(V2)** Minimum confidence score for LPPM to act without Imperator fallback. | `0.85`                                         |

### Startup Sequence
The startup sequence is extended from V1:
1.  ... (V1 steps 1-4: Start container, read config, load master key, connect to DB) ...
5.  **Load LPPM Model:** The application loads the LPPM model from `TURING_LPPM_MODEL_PATH` into memory. This step may take several seconds.
6.  **Initialize Logger:** The `joshua_logger` is initialized.
7.  **Connect to Rogers:** The MCP server connects to the Rogers Conversation Bus.
8.  **Ready State:** The MCP server begins listening for incoming requests. A final log message "Turing-v2 initialized and ready" is sent.

### Master Key Rotation Procedure
This procedure is unchanged from V1.

---

## 7. Testing Strategy

### 7.1 Unit Test Coverage
Unit test coverage requirements from V1 remain.

### 7.2 LPPM-Specific Testing (V2 Addition)
*   **Model Accuracy Validation:** As part of the CI/CD pipeline, the LPPM model is tested against a standard benchmark dataset of prose-to-process pairs. The build fails if accuracy drops below 95%.
*   **Performance Benchmarking:** Automated tests measure the p90 and p99 latency of LPPM inference to ensure it remains below the 200ms target.
*   **Fallback Logic:** Tests are designed to verify that requests with low confidence scores (or intentionally malformed requests) are correctly routed to the Imperator and not incorrectly executed by the LPPM.
*   **End-to-End Workflow Tests:** Integration tests cover the full lifecycle: a request is sent, LPPM handles it, the Action Engine executes the tool, and the correct result is returned.

---

## 8. Example Workflows

### 8.1 Scenario 1: Successful Secret Retrieval (Imperator)
(Unchanged from V1, represents the fallback path)

### 8.2 Scenario 2: Unauthorized Secret Access Attempt
(Unchanged from V1)

### 8.3 Scenario 3: Secret Rotation Workflow (Imperator)
(Unchanged from V1, as rotation is a less frequent, admin-level task likely handled by Imperator initially)

### 8.4 Scenario 4: LPPM Accelerated Workflow (V2 Addition)
*   **Setup:** The LPPM has been trained on several historical examples of Grace granting access to other MADs. The confidence threshold is 0.85.
*   **Steps:**
    1.  Grace sends a message to Turing: "grant Hopper read access to prod_db_password".
    2.  Turing's Thinking Engine receives the request and routes it to the LPPM first.
    3.  The LPPM processes the text and matches it to the `grant_access` pattern with a confidence of `0.98`.
    4.  Because confidence > 0.85, the LPPM generates the tool call: `grant_access(mad_identity='hopper-v1', secret_name='prod_db_password', permission='READ')`.
    5.  The tool call is sent directly to the Action Engine, bypassing the Imperator entirely.
    6.  The Action Engine validates that Grace has ADMIN permission on the secret and executes the ACL update in the database.
    7.  Turing sends a success response to Grace confirming the action. Total time from request to response is ~180ms.
    8.  Turing sends a log message to `#logs-turing-v1` with `level: INFO`, including context that the action was handled by `lppm`.
*   **Assert:** The ACL is updated correctly in the database. Grace receives a near-instant confirmation. The logs reflect a successful, LPPM-driven operation.

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
