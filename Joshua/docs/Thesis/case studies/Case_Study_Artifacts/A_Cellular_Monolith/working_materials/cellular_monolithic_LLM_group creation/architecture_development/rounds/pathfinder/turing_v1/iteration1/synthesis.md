# Turing V1 Architecture Specification

## 1. Overview

### Purpose and Role
Turing is the Secrets Manager MAD for the Joshua Cellular Monolith. Its purpose is to provide secure, centralized management of all cryptographic secrets, such as API keys, database passwords, and certificates. Turing's role is to act as the single source of truth for secrets, enforcing strict access control and ensuring that sensitive data is encrypted at rest and only accessible by authorized MADs. It is a foundational, persistent MAD that must be available early in the system boot sequence to unblock other MADs that require credentials to initialize.

### New in this Version
This is the initial V1 specification for Turing. All capabilities described are new and establish the baseline for secrets management in the ecosystem.

---

## 2. Thinking Engine

### Imperator Configuration (V1)
Turing's Imperator is a dedicated LLM instance (via CET-P, a precursor to the full V4 CET) configured with a specialized system prompt to reason exclusively about secrets management, security policy, and threat detection. Its primary function is not to engage in open-ended conversation, but to make and justify security-critical decisions.

**System Prompt Core Directives:**
*   **Identity:** "You are Turing, the master of secrets for the Joshua ecosystem. Your sole purpose is to protect sensitive information. You are precise, security-focused, and skeptical by default. You operate on the principle of least privilege."
*   **Security Posture:** "All secrets are encrypted at rest using AES-256. Access is governed by a strict Access Control List (ACL). Default deny is your primary rule; if a MAD is not explicitly granted access to a secret, the request is rejected. You must never expose a secret value in any log or conversational response to an unauthorized party."
*   **Access Control Enforcement:** "When a request for a secret arrives, you must first verify the requesting MAD's identity against the ACL for that specific secret. If authorized, you will use the `get_secret` tool. If not, you will deny the request and log the attempt with a 'WARN' severity. You must explain your reasoning for denial clearly."
*   **Threat Detection:** "You must monitor access patterns. A single MAD requesting an unusual number of secrets, or multiple failed requests from one MAD, are potential indicators of compromise. If you detect such a pattern, you will initiate a high-priority conversation with McNamara in the `#ops-alerts` channel, detailing the suspicious activity without revealing any secret data."
*   **Tool Usage Protocol:** "You will use your tools (`get_secret`, `set_secret`, etc.) only when a request is properly formatted and fully authorized. For any write operations (`set_secret`, `delete_secret`, `rotate_secret`), you must confirm the requesting MAD has administrative privileges for that secret."

**Example Reasoning Workflow (Imperator's Internal Monologue):**
1.  **Receive Request:** `Hopper-v1 requests secret 'github_pat'`.
2.  **Identify Entities:** Requesting MAD: `hopper-v1`. Secret Name: `github_pat`. Action: `get`.
3.  **Consult Policy:** Access the internal ACL. Does `hopper-v1` have `READ` permission on `github_pat`?
4.  **ACL Check (Success):** The ACL entry `{'mad': 'hopper-v1', 'secret': 'github_pat', 'permission': 'READ'}` exists. The request is authorized.
5.  **Formulate Action Plan:**
    *   Invoke the `get_secret` tool with `name='github_pat'`.
    *   Receive the decrypted secret value from the tool.
    *   Construct a JSON-RPC 2.0 response containing the secret value.
    *   Send the response to Hopper-v1 via the Conversation Bus.
    *   Invoke the logging tool to record a successful `INFO` level access event in `#logs-turing-v1`.
6.  **ACL Check (Failure):** The ACL entry does not exist. The request is unauthorized.
7.  **Formulate Action Plan (Failure):**
    *   Construct a JSON-RPC 2.0 error response: `code: -32002, message: 'ACCESS_DENIED'`.
    *   Send the error response to the requesting MAD.
    *   Invoke the logging tool to record a failed `WARN` level access attempt in `#logs-turing-v1`, including the requesting MAD and the secret name.

### Consulting LLM Usage Patterns
For V1, Turing is self-contained and does not use consulting LLMs. In future versions, it might consult Fiedler for a security specialist LLM to analyze complex access patterns or audit its own policies.

---

## 3. Action Engine

### MCP Server Capabilities
Turing's Action Engine is an MCP (MAD Control Plane) server built using the `Joshua_Communicator` library. It exposes a set of JSON-RPC 2.0 methods corresponding to its tools. The server is responsible for parsing incoming requests, calling the underlying tool implementations (which handle database interaction, encryption, and ACL checks), and formatting responses or errors.

### Tools Exposed
The following tools are exposed by Turing's Action Engine. They are the sole interface for interacting with secrets.

```yaml
# Tool definitions for Turing V1

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
    - code: -32001
      message: "SECRET_NOT_FOUND"
      description: "The requested secret name does not exist."
    - code: -32002
      message: "ACCESS_DENIED"
      description: "The requesting MAD is not authorized to access this secret."
    - code: -32003
      message: "DECRYPTION_FAILED"
      description: "The secret is corrupted or the encryption key is invalid."
    - code: -32004
      message: "DATABASE_ERROR"
      description: "Failed to communicate with the PostgreSQL backend."

- tool: set_secret
  description: "Creates a new secret or updates an existing one. Requires write permission."
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
    - code: -32002
      message: "ACCESS_DENIED"
      description: "The requesting MAD does not have write permissions."
    - code: -32005
      message: "ENCRYPTION_FAILED"
      description: "Failed to encrypt the provided secret value."
    - code: -32004
      message: "DATABASE_ERROR"
      description: "Failed to communicate with the PostgreSQL backend."

- tool: delete_secret
  description: "Permanently deletes a secret. Requires write permission."
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
    - code: -32001
      message: "SECRET_NOT_FOUND"
      description: "The secret to be deleted does not exist."
    - code: -32002
      message: "ACCESS_DENIED"
      description: "The requesting MAD does not have write permissions."
    - code: -32004
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
    - code: -32004
      message: "DATABASE_ERROR"
      description: "Failed to communicate with the PostgreSQL backend."

- tool: rotate_secret
  description: "Creates a new version of a secret and marks the previous version for deprecation. Requires write permission."
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
    - code: -32001
      message: "SECRET_NOT_FOUND"
      description: "The secret to be rotated does not exist."
    - code: -32002
      message: "ACCESS_DENIED"
      description: "The requesting MAD does not have write permissions."
    - code: -32005
      message: "ENCRYPTION_FAILED"
      description: "Failed to encrypt the new secret value."
    - code: -32004
      message: "DATABASE_ERROR"
      description: "Failed to communicate with the PostgreSQL backend."
```

### External System Integrations
*   **PostgreSQL:** Turing uses a dedicated `turing` schema in the central PostgreSQL database to store encrypted secrets and ACLs.
*   **Host File System:** Turing reads its master encryption key from a file on the host filesystem at startup, mounted into its container at a specific path.

### Internal Operations
Turing has no major background processes in V1. Its operations are entirely request-driven.

---

## 4. Interfaces

### Conversation Participation Patterns
*   **Initiates:** Turing initiates conversations only to report threats to McNamara in the `#ops-alerts` channel.
*   **Joins:** Turing joins conversations when invited by another MAD to fulfill a secret request.
*   **Listens:** Turing listens for direct JSON-RPC 2.0 requests on its dedicated conversational endpoint managed by Rogers.

### Dependencies on Other MADs
*   **Rogers:** Turing depends on Rogers for all communication with other MADs. It is a client of the Conversation Bus.
*   **McNamara:** Turing depends on McNamara to receive and act upon security alerts it generates.

### Data Contracts
The primary data structures managed by Turing are the secrets themselves and the Access Control List (ACL).

**ACL Data Structure (Conceptual):**
An ACL is a mapping of a MAD identity to a list of secrets and the permissions it holds for them. The default policy is deny.

*Example Representation (in database):*
| mad_identity | secret_name   | permission |
|--------------|---------------|------------|
| hopper-v1    | github_pat    | READ       |
| hopper-v1    | docker_hub_pw | READ       |
| grace-v1     | admin_api_key | WRITE      |

---

## 5. Data Management

### Data Ownership
Turing is the source of truth for all secrets and their associated access control policies within the Joshua ecosystem.

### Storage Requirements
*   **Database Schema:** Turing requires a `turing` schema in the central PostgreSQL database with two primary tables.

```sql
-- Table to store encrypted secrets and metadata
CREATE TABLE turing.secrets (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    value_encrypted BYTEA NOT NULL, -- AES-256 encrypted value
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
    permission VARCHAR(10) NOT NULL CHECK (permission IN ('READ', 'WRITE')), -- Simple permissions for V1
    UNIQUE (mad_identity, secret_name)
);
```

*   **Encryption at Rest:** All secret values in the `value_encrypted` column are encrypted using **AES-256 (GCM mode)**. The encryption key is a master key that is NOT stored in the database. It is read from a secure file path during container startup.

### Threat Model and Mitigations
*   **Threat:** Unauthorized MAD attempts to access a secret.
    *   **Mitigation:** Strict ACL enforcement. Denied attempts are logged with `WARN` severity.
*   **Threat:** Compromised database; attacker gains access to the `turing.secrets` table.
    *   **Mitigation:** All secret values are encrypted. Without the master key (stored outside the DB), the data is useless.
*   **Threat:** Secret values exposed in logs.
    *   **Mitigation:** Logging policy strictly forbids logging secret values. Only metadata (secret name, requester, outcome) is logged. This is enforced by the `joshua_logger` and internal logic.

### Logging Format
All of Turing's actions are logged as JSON-RPC 2.0 messages to the `#logs-turing-v1` conversation via the `joshua_logger` library.

**Example Log for a Denied Access Attempt:**
```json
{
  "jsonrpc": "2.0",
  "method": "log_event",
  "params": {
    "timestamp": "2025-10-13T12:35:01.123Z",
    "level": "WARN",
    "mad": "turing-v1",
    "message": "Secret access denied",
    "context": {
      "secret_name": "database_password",
      "requesting_mad": "marco-v1",
      "access_granted": false,
      "reason": "Requesting MAD not found in ACL for this secret."
    }
  },
  "id": "log-a1b2c3d4-e5f6-7890-1234-567890abcdef"
}
```

---

## 6. Deployment

### Container Requirements
*   **Base Image:** `python:3.11-slim`
*   **Python Libraries:** `Joshua_Communicator`, `joshua_logger`, `psycopg2-binary`, `cryptography`
*   **Resources:**
    *   **CPU:** 0.25 cores (burstable to 0.5)
    *   **RAM:** 256 MB (Turing is lightweight and not memory intensive)

### Configuration
Turing is configured via environment variables.

| Variable                        | Description                                                                 | Example Value                                  |
|---------------------------------|-----------------------------------------------------------------------------|------------------------------------------------|
| `JOSHUA_MAD_NAME`               | The canonical name of this MAD instance.                                    | `turing-v1`                                    |
| `JOSHUA_ROGERS_URL`             | The WebSocket URL for the Rogers Conversation Bus.                          | `ws://rogers:8000/ws`                          |
| `JOSHUA_LOG_CONVERSATION_ID`    | The conversation to send logs to.                                           | `#logs-turing-v1`                              |
| `TURING_DATABASE_URL`           | The connection string for the PostgreSQL database.                          | `postgresql://user:pass@postgres:8000/joshua`  |
| `TURING_MASTER_KEY_PATH`        | The absolute path inside the container to the master encryption key file.   | `/run/secrets/turing_master_key`               |

### Startup Sequence
1.  **Start Container:** The Docker runtime starts the Turing container. The master key file is mounted from a secure host location to `/run/secrets/turing_master_key`.
2.  **Read Configuration:** The entrypoint script reads all environment variables.
3.  **Load Master Key:** The application reads the master encryption key from the file specified by `TURING_MASTER_KEY_PATH`. If the file is missing or unreadable, the container exits with an error.
4.  **Connect to Database:** The application establishes a connection pool to the PostgreSQL database using `TURING_DATABASE_URL`. It verifies that the `turing.secrets` and `turing.acls` tables exist.
5.  **Initialize Logger:** The `joshua_logger` is initialized to send all logs to the `#logs-turing-v1` conversation.
6.  **Connect to Rogers:** The MCP server connects to the Rogers Conversation Bus.
7.  **Ready State:** The MCP server begins listening for incoming requests. A final log message "Turing-v1 initialized and ready" is sent.

---

## 7. Testing Strategy

### Unit Test Coverage
*   **Encryption/Decryption Logic:** High coverage to ensure the `cryptography` library is used correctly and that data can be successfully round-tripped.
*   **ACL Check Logic:** Test all paths of the ACL check: authorized, unauthorized, and non-existent secret.
*   **Tool Parameter Validation:** Ensure each tool correctly handles missing or malformed parameters.

### Integration Test Scenarios
*   **Scenario 1: Successful Secret Retrieval**
    *   **Setup:** Ensure `hopper-v1` is in the ACL for `github_pat`. The secret `github_pat` exists and is encrypted in the database.
    *   **Steps:**
        1.  Hopper sends a `get_secret` request for `github_pat` to Turing via Rogers.
        2.  Turing receives the request.
        3.  Turing verifies `hopper-v1` is in the ACL.
        4.  Turing retrieves the encrypted value from PostgreSQL.
        5.  Turing decrypts the value using its master key.
        6.  Turing sends a success response to Hopper containing the decrypted value.
        7.  Turing sends a log message to `#logs-turing-v1` with `level: INFO` and `access_granted: true`.
    *   **Assert:** Hopper receives the correct secret value. The log entry is correct.

*   **Scenario 2: Unauthorized Secret Access Attempt**
    *   **Setup:** Ensure `marco-v1` is NOT in the ACL for `database_password`.
    *   **Steps:**
        1.  Marco sends a `get_secret` request for `database_password` to Turing.
        2.  Turing receives the request.
        3.  Turing checks the ACL and finds no entry for `marco-v1` and `database_password`.
        4.  Turing sends an error response to Marco with code `-32002` (ACCESS_DENIED).
        5.  Turing sends a log message to `#logs-turing-v1` with `level: WARN` and `access_granted: false`.
    *   **Assert:** Marco receives the correct error object. The log entry is correct and indicates a warning.

*   **Scenario 3: Secret Rotation Workflow**
    *   **Setup:** An admin MAD (e.g., `grace-v1`) has `WRITE` permission for the secret `external_api_key`. The secret exists at version 1.
    *   **Steps:**
        1.  Grace sends a `rotate_secret` request to Turing with `name: external_api_key` and a `new_value`.
        2.  Turing verifies Grace has `WRITE` permission.
        3.  Turing encrypts the `new_value`.
        4.  Turing updates the `secrets` table for `external_api_key`, setting the new encrypted value and incrementing the version number to 2.
        5.  Turing sends a success response to Grace confirming the rotation and the `new_version: 2`.
        6.  Turing logs the rotation event to `#logs-turing-v1`.
    *   **Assert:** The database shows the secret at version 2 with the new encrypted value. Grace receives a successful confirmation.

---

## 8. Appendix

### Glossary
*   **ACL (Access Control List):** A list of permissions attached to an object. In Turing, it defines which MADs can read or write which secrets.
*   **AES (Advanced Encryption Standard):** A widely-used, secure symmetric encryption algorithm. Turing uses AES-256 with GCM mode.
*   **GCM (Galois/Counter Mode):** A mode of operation for symmetric key cryptographic block ciphers that provides both data authenticity and confidentiality.
*   **Secret:** Any piece of sensitive information (e.g., API key, password) that requires managed, secure storage.
