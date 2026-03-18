# Turing Requirements

- **Role**: Secrets & Credentials Management
- **Version**: V0.10
- **Home**: `mads/turing/`

---

## 1. Overview

- **Purpose**: Turing is the dedicated secrets management MAD for the Joshua ecosystem.
- **V0.10 Scope Definition**: Provide secure storage, retrieval, and lifecycle management of secrets like API keys and tokens for the foundational MADs.

---

## 2. Tool Exposure Model

This MAD follows the Direct Tool Exposure architecture (ADR-023). Its public tools are exposed directly on its MCP server and are discoverable via the Rogers registry. Any incoming communication that is not a valid MCP call for an exposed tool is routed to the Thought Engine for conversational processing or policy guidance.

> **Note on Tool List:** The tools listed in this document are a *provisional set* based on the MAD's high-level requirements. The final, authoritative list of tools, their specific parameters, and their return schemas will be defined in a dedicated Design Document prior to implementation.

---

## 3. Public Action Engine Tools

### `turing_store_secret`
- **Description:** Securely stores a secret value under a given name. This operation requires administrative privileges.
- **Input Schema:**
    - `secret_name` (string, required): The unique name for the secret (e.g., "openai_api_key").
    - `secret_value` (string, required): The raw secret value to be stored.
- **Output Schema:** `{"status": "success", "message": "Secret 'openai_api_key' stored successfully."}`

### `turing_retrieve_secret`
- **Description:** Retrieves a decrypted secret value. The Action Engine must perform strict authorization checks based on the requesting `participant_id` before returning the secret.
- **Input Schema:**
    - `secret_name` (string, required): The name of the secret to retrieve.
- **Output Schema:** `{"status": "success", "secret_name": "openai_api_key", "secret_value": "sk-..."}`

---

## 4. Future Evolution (Post-V0)

Turing's role as the secrets management platform remains focused on secure credential storage and access control throughout the ecosystem's evolution.

*   **Phase 1 (Foundation / V0.10):** Turing is hardened and quality-gated for flawless Direct Communication, becoming the reliable secrets management platform for the V0.10 Core Fleet. All MADs depend on Turing for secure credential access, making it a critical infrastructure component.
*   **Phase 2 (Conversation / V1.0):** Turing is re-platformed to communicate exclusively via the Rogers Conversation Bus (pure Kafka), using `Joshua_Communicator` for all inter-MAD communication. Secrets retrieval requests and audit events flow through the durable conversation log (with secrets themselves never logged).
*   **Phase 5 (Autonomy / V7.0):** Turing integrates with Joshua MAD's strategic orchestration, receiving top-down directives for system-wide secrets policies, constitutional constraints on credential access patterns, and strategic enforcement of security best practices across the entire ecosystem.

---