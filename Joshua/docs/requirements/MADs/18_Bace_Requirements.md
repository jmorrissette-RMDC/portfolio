# Bace Requirements

- **Role**: Authentication and Authorization
- **Version**: V7.0
- **Home**: `mads/bace/`

---

## 1. Overview
- **Purpose**: Bace is the centralized authentication and authorization MAD, managing user identities, roles, and permissions for the entire ecosystem.
- **V7.0 Scope Definition**: As a V7.0 MAD, Bace provides a comprehensive suite of security services, including MFA, RBAC, and session management, with a fully cognitive Thought Engine for context-aware and risk-based security decisions.

---

## 2. Tool Exposure Model

This MAD follows the Direct Tool Exposure architecture (ADR-023). Its public tools are exposed directly on its MCP server and are discoverable via the Rogers registry. Any incoming communication that is not a valid MCP call for an exposed tool is routed to the Thought Engine for conversational processing (e.g., security policy questions).

> **Note on Tool List:** The tools listed in this document are a *provisional set* based on the MAD's high-level requirements. The final, authoritative list of tools, their specific parameters, and their return schemas will be defined in a dedicated Design Document prior to implementation.

---

## 3. Public Action Engine Tools

### `bace_login`
- **Description:** Authenticates a user with a username, password, and MFA code, returning a JWT session token upon success.
- **Input Schema:**
    - `username` (string, required): The user's username.
    - `password` (string, required): The user's password.
    - `mfa_code` (string, optional): The multi-factor authentication code, if enabled for the user.
- **Output Schema:** `{"status": "success", "token": "jwt-token-string", "expires_in": 3600}`

### `bace_validate_token`
- **Description:** Validates a JWT session token.
- **Input Schema:**
    - `token` (string, required): The JWT to validate.
- **Output Schema:** `{"status": "success", "is_valid": true, "payload": {"user_id": "...", "roles": ["..."]}}`

### `bace_check_permission`
- **Description:** Checks if a user (identified by a valid token) has a specific permission.
- **Input Schema:**
    - `token` (string, required): The user's JWT session token.
    - `permission` (string, required): The permission to check (e.g., "files:write").
- **Output Schema:** `{"status": "success", "has_permission": true}`

### `bace_get_user_roles`
- **Description:** Retrieves the roles associated with a user.
- **Input Schema:**
    - `user_id` (string, required): The ID of the user.
- **Output Schema:** `{"status": "success", "roles": ["editor", "viewer"]}`

---

## 4. Future Evolution (Post-V0)

Bace is introduced in Phase 6 (Expansion) at V7.0 as the centralized authentication and authorization service for the mature Joshua ecosystem.

*   **Phase 6 (Expansion / V7.0):** Bace enters the ecosystem as a specialized security MAD, inheriting the full V7.0 capabilities including complete PCP (DTR, LPPM, CET, CRS), pure Kafka conversation bus integration, and eMAD awareness. Bace provides unified authentication and authorization services to all MADs, replacing ad-hoc security implementations. It integrates with Codd for structured user data storage, McNamara for security monitoring, and Cerf for API gateway authentication. Bace's Imperator enables context-aware security decisions, such as risk-based authentication and adaptive authorization policies based on conversation context.

*   **Post-V7.0 Enhancements:** Future evolution may include federated identity management (SSO, SAML, OAuth2 provider), biometric authentication support, advanced threat detection through CRS pattern recognition, and integration with external identity providers (LDAP, Active Directory). Bace may evolve to support zero-trust security models with continuous authentication and fine-grained, dynamic authorization policies informed by real-time ecosystem state.

---