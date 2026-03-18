# Turing V2 Architecture Specification

## 1. Overview

### Purpose and Role
Turing is the Secrets Manager MAD for the Joshua Cellular Monolith. Its purpose is to provide secure, centralized management of all cryptographic secrets, such as API keys, database passwords, and certificates. Turing's role is to act as the single source of truth for secrets, enforcing strict access control and ensuring that sensitive data is encrypted at rest and only accessible by authorized MADs. It is a foundational, persistent MAD that must be available early in the system boot sequence to unblock other MADs that require credentials to initialize.

### New in this Version
This V2 specification introduces the Learned Prose-to-Process Mapper (LPPM) as a performance optimization. The LPPM provides a "fast path" for common, high-frequency requests like "get secret" or "list my secrets," translating them directly into tool calls to reduce latency and cognitive load. All V1 functionalities are preserved.

---

## 2. Thinking Engine

### 2.1 Imperator Configuration (V1+)
Turing's Imperator is a dedicated LLM instance configured with a specialized system prompt to reason exclusively about secrets management, security policy, and threat detection. Its primary function is not to engage in open-ended conversation, but to make and justify security-critical decisions.

**System Prompt Core Directives:**
*   **Identity:** "You are Turing, the master of secrets for the Joshua ecosystem. Your sole purpose is to protect sensitive information. You are precise, security-focused, and skeptical by default. You operate on the principle of least privilege."
*   **Security Posture:** "All secrets are encrypted at rest using AES-256. Access is governed by a strict Access Control List (ACL). Default deny is your primary rule; if a MAD is not explicitly granted access to a secret, the request is rejected. You must never expose a secret value in any log or conversational response to an unauthorized party."
*   **Access Control Enforcement:** "When a request for a secret arrives, you must first verify the requesting MAD's identity against the ACL for that specific secret. If authorized, you will use the `get_secret` tool. If not, you will deny the request and log the attempt with a 'WARN' severity. You must explain your reasoning for denial clearly."
*   **Threat Detection:** "You must monitor access patterns. A single MAD requesting an unusual number of secrets, or multiple failed requests from one MAD, are potential indicators of compromise. If you detect such a pattern, you will log a CRITICAL-level event to `#logs-turing-v2` with comprehensive context about the suspicious activity (without revealing secret data). In future versions, McNamara will automatically monitor these critical logs and coordinate defensive responses."
*   **Tool Usage Protocol:** "You will use your tools (`get_secret`, `set_secret`, etc.) only when a request is properly formatted and fully authorized. For any write operations (`set_secret`, `delete_secret`), you must confirm the requesting MAD has WRITE permissions. For `rotate_secret`, you must confirm ADMIN permissions. For ACL operations (`grant_access`, `revoke_access`), you must confirm the requesting MAD has ADMIN permissions for the target secret."

**Threat Detection Thresholds:**
*   **Rapid Failure Pattern:** If a single MAD makes >5 failed `get_secret` attempts within 1 minute, log as CRITICAL threat (potential brute force or misconfiguration).
*   **Anomalous Volume:** If a MAD requests >10 unique secrets within 5 minutes when its ACL grants access to <5 secrets, log as WARN anomaly (potential lateral movement or privilege escalation).
*   **Credential Stuffing:** If >3 different MADs fail to access the same secret within 10 minutes, log as ERROR (potential coordinated attack).
*   **False Positive Mitigation:** Legitimate batch operations (e.g., system startup, deployment) may trigger volume alerts. Include MAD identity and timing context in logs for human review.

### 2.2 LPPM Integration (V2+)
- **LPPM Integration (V2+):** Turing's LPPM is a distilled transformer model trained on historical conversation logs from V1 deployments. It learns to recognize common request patterns and map them directly to tool call sequences.
  - **Training Data Sources:**
    - V1 production logs (Imperator reasoning + tool calls)
    - Synthetic data from Fiedler consulting LLMs
    - Hand-crafted golden examples for edge cases
  - **Model Architecture:**
    - Distilled BERT-style encoder (6 layers, 384 hidden dims)
    - Classification head for tool selection
    - Sequence output head for parameter extraction
    - Model size: 384-512 MB on disk
  - **Fast Path Conditions:** The LPPM is invoked for every request. If confidence > 95%, the tool call sequence is executed directly without Imperator reasoning. If confidence ≤ 95%, request falls back to Imperator.
  - **Example Fast Paths:**
    - "Get the secret for github_pat" → `get_secret(name='github_pat')`
    - "List the secrets I can access" → `list_secrets()`
    - "Delete the secret 'old_api_key'" → `delete_secret(name='old_api_key')`
  - **Training Loop:**
    - Initial training: 24 hours on 100K V1 logs
    - Continuous learning: Weekly retraining with new V1/V2 production data
    - Validation: 95% accuracy on held-out test set before deployment

### Consulting LLM Usage Patterns
For V2, Turing is self-contained and does not use consulting LLMs. In future versions, it might consult Fiedler for a security specialist LLM to analyze complex access patterns or audit its own policies.

---

## 3. Action Engine

### MCP Server Capabilities
Turing's Action Engine is an MCP (MAD Control Plane) server built using the `Joshua_Communicator` library. It exposes a set of JSON-RPC 2.0 methods corresponding to its tools. The server is responsible for parsing incoming requests, calling the underlying tool implementations (which handle database interaction, encryption, and ACL checks), and formatting responses or errors.

All logging is performed via the `joshua_logger` library, which automatically wraps log events in JSON-RPC 2.0 format. The MCP server never constructs log messages manually; it invokes `joshua_logger.log(level, message, context)`, and the library handles JSON-RPC structuring, conversation routing, and error handling.

### Tools Exposed
The following tools are exposed by Turing's Action Engine. They are the sole interface for interacting with secrets.

```yaml
# Tool definitions for Turing V2

- tool: get_secret
  description: "Retrieves the decrypted value of a secret, checking ACL first."
  parameters:
    - name: name
      type: string
      required: true
      description: "The unique name of the secret to retrieve."
  returns:
    type: object
    description: "An object containing the secret's details."
    schema:
      type: object
      properties:
        name: {type: string}
        value: {type: string, description: "The decrypted secret value."}
        created_at: {type: string, format: date-time}
        version: {type: integer}
      required: [name, value, created_at, version]
  errors:
    - code: -35001
      message: "SECRET_NOT_FOUND"
      description: "The requested secret name does not exist."
    - code: -35002
      message: "ACCESS_DENIED"
      description: "The requesting MAD is not authorized to access this secret."
    - code: -35003
      message: "DECRYPTION_FAILED"
      description: "The secret is corrupted or the encryption key is invalid."
    - code: -35004
      message: "DATABASE_ERROR"
      description: "Failed to communicate with the PostgreSQL backend."

- tool: set_secret
  description: "Creates a new secret or updates an existing one. Requires WRITE permission."
  parameters:
    - name: name
      type: string
      required: true
      description: "The unique name of the secret to create or update."
    - name: value
      type: string
      required: true
      description: "The secret value to be stored. Will be encrypted."
  returns:
    type: object
    description: "A confirmation object."
    schema:
      type: object
      properties:
        name: {type: string}
        status: {type: string, enum: [created, updated]}
        version: {type: integer}
      required: [name, status, version]
  errors:
    - code: -35002
      message: "ACCESS_DENIED"
      description: "The requesting MAD does not have WRITE permissions."
    - code: -35005
      message: "ENCRYPTION_FAILED"
      description: "Failed to encrypt the provided secret value."
    - code: -35004
      message: "DATABASE_ERROR"
      description: "Failed to communicate with the PostgreSQL backend."

- tool: delete_secret
  description: "Permanently deletes a secret. Requires WRITE permission."
  parameters:
    - name: name
      type: string
      required: true
      description: "The unique name of the secret to delete."
  returns:
    type: object
    description: "A confirmation object."
    schema:
      type: object
      properties:
        name: {type: string}
        status: {type: string, const: "deleted"}
      required: [name, status]
  errors:
    - code: -35001
      message: "SECRET_NOT_FOUND"
      description: "The secret to be deleted does not exist."
    - code: -35002
      message: "ACCESS_DENIED"
      description: "The requesting MAD does not have WRITE permissions."
    - code: -35004
      message: "DATABASE_ERROR"
      description: "Failed to communicate with the PostgreSQL backend."

- tool: list_secrets
  description: "Lists the names of all secrets the requesting MAD is authorized to read."
  parameters: []
  returns:
    type: object
    description: "An object containing a list of accessible secret names."
    schema:
      type: object
      properties:
        secrets:
          type: array
          items:
            type: string
      required: [secrets]
  errors:
    - code: -35004
      message: "DATABASE_ERROR"
      description: "Failed to communicate with the PostgreSQL backend."

- tool: rotate_secret
  description: "Creates a new version of a secret and marks the previous version for deprecation. Requires ADMIN permission (not just WRITE)."
  parameters:
    - name: name
      type: string
      required: true
      description: "The unique name of the secret to rotate."
    - name: new_value
      type: string
      required: true
      description: "The new secret value."
  returns:
    type: object
    description: "A confirmation object with the new version number."
    schema:
      type: object
      properties:
        name: {type: string}
        status: {type: string, const: "rotated"}
        new_version: {type: integer}
      required: [name, status, new_version]
  errors:
    - code: -35001
      message: "SECRET_NOT_FOUND"
      description: "The secret to be rotated does not exist."
    - code: -35002
      message: "ACCESS_DENIED"
      description: "The requesting MAD does not have ADMIN permission for this secret. WRITE permission is insufficient for rotation."
    - code: -35005
      message: "ENCRYPTION_FAILED"
      description: "Failed to encrypt the new secret value."
    - code: -35004
      message: "DATABASE_ERROR"
      description: "Failed to communicate with the PostgreSQL backend."

- tool: grant_access
  description: "Grants a MAD permission to access a secret. Requires ADMIN permission on the secret."
  parameters:
    - name: mad_identity
      type: string
      required: true
      description: "The MAD to grant access to (e.g., 'hopper-v2')"
    - name: secret_name
      type: string
      required: true
      description: "The secret to grant access for"
    - name: permission
      type: string
      required: true
      description: "Permission level to grant"
      enum: [READ, WRITE, ADMIN]
  returns:
    type: object
    description: "Confirmation of ACL update"
    schema:
      type: object
      properties:
        mad_identity: {type: string}
        secret_name: {type: string}
        permission: {type: string}
        status: {type: string, const: "granted"}
      required: [mad_identity, secret_name, permission, status]
  errors:
    - code: -35001
      message: "SECRET_NOT_FOUND"
      description: "The specified secret does not exist"
    - code: -35002
      message: "ACCESS_DENIED"
      description: "Requesting MAD does not have ADMIN permission for this secret"
    - code: -35006
      message: "INVALID_PERMISSION"
      description: "Permission value must be READ, WRITE, or ADMIN"
    - code: -35004
      message: "DATABASE_ERROR"
      description: "Failed to update ACL in PostgreSQL"

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
  returns:
    type: object
    description: "Confirmation of ACL removal"
    schema:
      type: object
      properties:
        mad_identity: {type: string}
        secret_name: {type: string}
        status: {type: string, const: "revoked"}
      required: [mad_identity, secret_name, status]
  errors:
    - code: -35001
      message: "SECRET_NOT_FOUND"
      description: "The specified secret does not exist"
    - code: -35002
      message: "ACCESS_DENIED"
      description: "Requesting MAD does not have ADMIN permission for this secret"
    - code: -35007
      message: "ACL_ENTRY_NOT_FOUND"
      description: "The specified MAD does not have access to this secret"
    - code: -35004
      message: "DATABASE_ERROR"
      description: "Failed to update ACL in PostgreSQL"
```

### External System Integrations
*   **PostgreSQL:** Turing uses a dedicated `turing` schema in the central PostgreSQL database to store encrypted secrets and ACLs.
*   **Host File System:** Turing reads its master encryption key from a file on the host filesystem at startup, mounted into its container at a specific path.

### Internal Operations
Turing has no major background processes in V2. Its operations are entirely request-driven.

---

## 4. Interfaces

### Conversation Participation Patterns
*   **Initiates:** Turing does not initiate conversations in V2. All threat detection is handled via CRITICAL-level log events in `#logs-turing-v2`.
*   **Joins:** Turing joins conversations when invited by another MAD to fulfill a secret request.
*   **Listens:** Turing listens for direct JSON-RPC 2.0 requests on its dedicated conversational endpoint managed by Rogers.

### Dependencies
*   **Rogers:** Turing depends on Rogers for all communication with other MADs. It is a client of the Conversation Bus. All logs are published to Rogers-managed conversations.

### Data Contracts
The primary data structures managed by Turing are the secrets themselves and the Access Control List (ACL).

**ACL Data Structure (Conceptual):**
An ACL is a mapping of a MAD identity to a list of secrets and the permissions it holds for them. The default policy is deny.

*Example Representation (in database):*
| mad_identity | secret_name   | permission |
|--------------|---------------|------------|
| hopper-v2    | github_pat    | READ       |
| hopper-v2    | docker_hub_pw | READ       |
| grace-v2     | admin_api_key | ADMIN      |

---

## 5. Data Management

### Data Ownership
Turing is the source of truth for all secrets and their associated access control policies within the Joshua ecosystem.

### Storage Requirements
*   **Database Schema:** Turing requires a `turing` schema in the central PostgreSQL database.

```sql
-- Table to store encrypted secrets and metadata
CREATE TABLE turing.secrets (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    value_encrypted BYTEA NOT NULL, -- AES-256 encrypted value
    key_version INT NOT NULL DEFAULT 1,
    version INT NOT NULL DEFAULT 1,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_accessed_by VARCHAR(255),
    last_accessed_at TIMESTAMPTZ
);

-- Table to manage Access Control Lists (ACLs)
CREATE TABLE turing.acls (
    id SERIAL PRIMARY KEY,
    mad_identity VARCHAR(255) NOT NULL,
    secret_name VARCHAR(255) NOT NULL,
    permission VARCHAR(10) NOT NULL CHECK (permission IN ('READ', 'WRITE', 'ADMIN')),
    UNIQUE (mad_identity, secret_name)
);
```

---

## 6. Deployment

### Container Requirements
*   **Base Image:** `python:3.11-slim`
*   **Python Libraries:** `Joshua_Communicator`, `joshua_logger`, `psycopg2-binary`, `cryptography`
*   **Resources:**
    *   **CPU:** 0.25 cores (burstable to 0.5)
    *   **RAM:** 768 MB
### Configuration
Turing is configured via environment variables.

| Variable                        | Description                                                                 | Example Value                                  |
|---------------------------------|-----------------------------------------------------------------------------|------------------------------------------------|
| `JOSHUA_MAD_NAME`               | The canonical name of this MAD instance.                                    | `turing-v2`                                    |
| `JOSHUA_ROGERS_URL`             | The WebSocket URL for the Rogers Conversation Bus.                          | `ws://rogers:8000/ws`                          |
| `JOSHUA_LOG_CONVERSATION_ID`    | The conversation to send logs to.                                           | `#logs-turing-v2`                              |
| `TURING_DATABASE_URL`           | The connection string for the PostgreSQL database.                          | `postgresql://user:pass@postgres:8000/joshua`  |
| `TURING_MASTER_KEY_PATH`        | The absolute path inside the container to the master encryption key file.   | `/run/secrets/turing_master_key`               |
| `TURING_LPPM_MODEL_PATH` | Path to the trained LPPM model file. | `/models/lppm/turing_lppm_v2.onnx` |

---

## 7. Testing Strategy

### 7.1 Unit Test Coverage
*   **Encryption/Decryption Logic:** High coverage to ensure the `cryptography` library is used correctly and that data can be successfully round-tripped.
*   **ACL Check Logic:** Test all paths of the ACL check: authorized (READ/WRITE/ADMIN), unauthorized, and non-existent secret.
*   **Tool Parameter Validation:** Ensure each tool correctly handles missing or malformed parameters.

- **LPPM Accuracy Tests:**
  - Test LPPM on 1000-sample validation set
  - Verify >95% accuracy for common patterns
  - Verify correct fallback to Imperator for low-confidence requests
- **Latency Comparison:**
  - Measure P50, P95, P99 latency for LPPM fast path vs. Imperator reasoning
  - Target: LPPM fast path <50ms, Imperator path 500-2000ms

---

## 8. Example Workflows

### 8.1 Scenario 1: Successful Secret Retrieval
*   **Setup:** Ensure `hopper-v2` is in the ACL for `github_pat` with `READ` permission. The secret `github_pat` exists and is encrypted in the database.
*   **Steps:**
    1.  Hopper sends a `get_secret` request for `github_pat` to Turing via Rogers.
    2.  Turing's LPPM recognizes the request and directly calls the `get_secret` tool.
    3.  Turing verifies `hopper-v2` is in the ACL.
    4.  Turing retrieves the encrypted value from PostgreSQL.
    5.  Turing decrypts the value using its master key.
    6.  Turing sends a success response to Hopper containing the decrypted value.
    7.  Turing sends a log message to `#logs-turing-v2` with `level: INFO` and `access_granted: true`.
*   **Assert:** Hopper receives the correct secret value. The log entry is correct.

---