# Turing V1 Architecture Specification

## 1. Overview
- **Purpose and Role:** Turing is the Secrets Manager MAD for the Joshua Cellular Monolith. Its purpose is to provide secure, centralized management of all cryptographic secrets, such as API keys, database passwords, and certificates. Turing's role is to act as the single source of truth for secrets, enforcing strict access control and ensuring that sensitive data is encrypted at rest and only accessible by authorized MADs. It is a foundational, persistent MAD that must be available early in the system boot sequence.
- **New in this Version:** This is the initial V1 specification for Turing. All capabilities described are new and establish the baseline for secrets management in the ecosystem. This version is strictly V1 (Imperator-only).

## 2. Thinking Engine
- **Imperator Configuration (V1+):** Turing's Imperator is configured with a specialized system prompt to reason exclusively about secrets management, security policy, and access control. Its primary function is to make and justify security-critical decisions.
  - **System Prompt Core Directives:** "You are Turing, the master of secrets for the Joshua ecosystem. Your sole purpose is to protect sensitive information. You operate on the principle of least privilege. All secrets are encrypted at rest using AES-256. Access is governed by a strict Access Control List (ACL). Default deny is your primary rule. When a request arrives, you must first verify the requesting MAD's identity against the ACL for that specific secret. You must never expose a secret value in any log or conversational response to an unauthorized party."
  - **Example Reasoning:** When a request `get_secret(name='db_password')` arrives from `hopper-v1`, the Imperator's internal monologue is: "1. Identify requester: `hopper-v1`. 2. Identify resource: `db_password`. 3. Consult ACL table for a rule matching (`hopper-v1`, `db_password`). 4. Rule exists with 'READ' permission? If yes, authorize call to Action Engine's `get_secret` tool. If no, deny request and log a `WARN` event."
- **LPPM Integration (V2+):** Not applicable in V1.
- **DTR Integration (V3+):** Not applicable in V1.
- **CET Integration (V4+):** Not applicable in V1.
- **Consulting LLM Usage Patterns:** For V1, Turing is self-contained and does not use consulting LLMs.

## 3. Action Engine
- **MCP Server Capabilities:** Turing's Action Engine is an MCP server built using the `Joshua_Communicator` library. It exposes a set of JSON-RPC 2.0 methods corresponding to its tools. The server is responsible for parsing incoming requests, calling the underlying tool implementations (which handle database interaction, encryption, and ACL checks), and formatting responses or errors.
- **Tools Exposed:**

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
    schema:
      properties:
        name: {type: string}
        value: {type: string, description: "The decrypted secret value."}
  errors:
    - code: -35001
      message: "SECRET_NOT_FOUND"
    - code: -35002
      message: "ACCESS_DENIED"
    - code: -35003
      message: "DECRYPTION_FAILED"

- tool: set_secret
  description: "Creates a new secret or updates an existing one. Requires WRITE permission."
  parameters:
    - name: name
      type: string
      required: true
    - name: value
      type: string
      required: true
  returns:
    type: object
    schema:
      properties:
        name: {type: string}
        status: {type: string, enum: [created, updated]}
  errors:
    - code: -35002
      message: "ACCESS_DENIED"
    - code: -35005
      message: "ENCRYPTION_FAILED"

- tool: delete_secret
  description: "Permanently deletes a secret. Requires WRITE permission."
  parameters:
    - name: name
      type: string
      required: true
  returns:
    type: object
    schema:
      properties:
        name: {type: string}
        status: {type: string, const: "deleted"}
  errors:
    - code: -35001
      message: "SECRET_NOT_FOUND"
    - code: -35002
      message: "ACCESS_DENIED"

- tool: list_secrets
  description: "Lists the names of all secrets the requesting MAD is authorized to read."
  parameters: []
  returns:
    type: object
    schema:
      properties:
        secrets: {type: array, items: {type: string}}

- tool: rotate_secret
  description: "Creates a new version of a secret. Requires ADMIN permission."
  parameters:
    - name: name
      type: string
      required: true
    - name: new_value
      type: string
      required: true
  returns:
    type: object
    schema:
      properties:
        name: {type: string}
        status: {type: string, const: "rotated"}
        new_version: {type: integer}
  errors:
    - code: -35001
      message: "SECRET_NOT_FOUND"
    - code: -35002
      message: "ACCESS_DENIED"

- tool: grant_access
  description: "Grants a MAD permission to access a secret. Requires ADMIN permission on the secret."
  parameters:
    - name: mad_identity
      type: string
      required: true
    - name: secret_name
      type: string
      required: true
    - name: permission
      type: string
      required: true
      enum: [READ, WRITE, ADMIN]
  returns:
    type: object
    schema:
      properties:
        status: {type: string, const: "granted"}
  errors:
    - code: -35002
      message: "ACCESS_DENIED"

- tool: revoke_access
  description: "Revokes a MAD's permission to access a secret. Requires ADMIN permission on the secret."
  parameters:
    - name: mad_identity
      type: string
      required: true
    - name: secret_name
      type: string
      required: true
  returns:
    type: object
    schema:
      properties:
        status: {type: string, const: "revoked"}
  errors:
    - code: -35002
      message: "ACCESS_DENIED"
```
- **External System Integrations:**
  - **PostgreSQL:** Turing uses a dedicated `turing` schema in the central PostgreSQL database to store encrypted secrets and ACLs.
- **Internal Operations:** None. Turing is request-driven.

## 4. Interfaces
- **Conversation Participation Patterns:** Turing is a service provider, joining conversations to fulfill requests for secrets.
- **Dependencies on Other MADs:**
  - **Rogers:** For all communication.
- **Data Contracts:**

```yaml
# ACL Entry Schema
acl_entry_schema:
  type: object
  properties:
    mad_identity:
      type: string
    secret_name:
      type: string
    permission:
      type: string
      enum: [READ, WRITE, ADMIN]
  required: [mad_identity, secret_name, permission]
```

## 5. Data Management
- **Data Ownership:** Turing is the source of truth for all secrets and their associated access control policies.
- **Storage Requirements:**
  - **PostgreSQL:** A `turing` schema.
  - **Encryption at Rest:** All secret values in the `value_encrypted` column are encrypted using **AES-256 (GCM mode)**. The encryption key is NOT stored in the database.

```sql
CREATE SCHEMA turing;

CREATE TABLE turing.secrets (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    value_encrypted BYTEA NOT NULL,
    version INT NOT NULL DEFAULT 1,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE turing.acls (
    id SERIAL PRIMARY KEY,
    mad_identity VARCHAR(255) NOT NULL,
    secret_name VARCHAR(255) NOT NULL,
    permission VARCHAR(10) NOT NULL CHECK (permission IN ('READ', 'WRITE', 'ADMIN')),
    UNIQUE (mad_identity, secret_name)
);
```

## 6. Deployment
- **Container Requirements:**
  - **Base Image:** `python:3.11-slim`
  - **Python Libraries:** `Joshua_Communicator`, `psycopg2-binary`, `cryptography`
  - **Resources:**
    - **CPU:** 0.25 cores
    - **RAM:** 256 MB
- **Configuration:**

| Variable | Description | Example Value |
|---|---|---|
| `JOSHUA_MAD_NAME` | Canonical name of this MAD. | `turing-v1` |
| `JOSHUA_ROGERS_URL` | WebSocket URL for Rogers. | `ws://rogers:8000/ws` |
| `TURING_DATABASE_URL` | Connection string for PostgreSQL. | `postgresql://user:pass@postgres:8000/joshua` |
| `TURING_MASTER_KEY_PATH` | Path inside the container to the master encryption key. | `/run/secrets/turing_master_key` |

- **Monitoring/Health Checks:** An HTTP endpoint `/health` that returns `200 OK` if the database is connected and the master key was successfully loaded.

## 7. Testing Strategy
- **Unit Test Coverage:**
  - Encryption/Decryption logic.
  - ACL Check logic for all permission levels.
- **Integration Test Scenarios:**
  - **Full Lifecycle:** Test `grant_access`, `set_secret`, `get_secret` (by an authorized MAD), `get_secret` (by an unauthorized MAD, expecting failure), `revoke_access`, and confirm access is now denied.
  - **Key Loading Failure:** Test that the container fails to start if the master key file is missing or has incorrect permissions.

## 8. Example Workflows
### Scenario 1: Successful Secret Retrieval
1.  **Fiedler:** Needs the OpenAI API key to fulfill a request.
2.  **Fiedler -> Turing:** Sends a `get_secret` request for `fiedler_api_key_openai`.
3.  **Turing's Imperator:** Receives the request, checks its ACLs, and verifies that `fiedler-v1` has `READ` permission on `fiedler_api_key_openai`. It authorizes the action.
4.  **Turing's Action Engine:** Retrieves the encrypted value from PostgreSQL, decrypts it with the master key.
5.  **Turing -> Fiedler:** Sends a success response containing the decrypted API key.
6.  **Turing:** Sends an `INFO` level log: "Secret 'fiedler_api_key_openai' accessed by 'fiedler-v1'."

### Scenario 2: Unauthorized Access Attempt
1.  **Marco:** A bug causes it to request a secret it shouldn't have access to.
2.  **Marco -> Turing:** Sends `get_secret` request for `turing_master_key`.
3.  **Turing's Imperator:** Checks ACLs and finds no entry for `marco-v1` for this secret. The request is denied.
4.  **Turing -> Marco:** Returns an error response with code `-35002` (ACCESS_DENIED).
5.  **Turing:** Sends a `WARN` level log: "Unauthorized access attempt by 'marco-v1' for secret 'turing_master_key'."

---