# Clarke Requirements

- **Role**: Cryptographic Services
- **Version**: V7.0
- **Home**: `mads/clarke/`

---

## 1. Overview

-   **Purpose**: Clarke provides centralized cryptographic services to the Joshua ecosystem, abstracting the complexities of encryption, decryption, signing, and verification.
-   **V7.0 Scope Definition**: As a V7.0 MAD, Clarke offers a comprehensive and cognitive suite of cryptographic tools, with an Imperator capable of providing guidance on best practices and algorithm selection.

---

## 2. Tool Exposure Model

This MAD follows the Direct Tool Exposure architecture (ADR-023). Its public tools are exposed directly on its MCP server and are discoverable via the Rogers registry. Any incoming communication that is not a valid MCP call for an exposed tool is routed to the Thought Engine for conversational processing (e.g., "What's the strongest encryption algorithm for sensitive data?").

> **Note on Tool List:** The tools listed in this document are a *provisional set* based on the MAD's high-level requirements. The final, authoritative list of tools, their specific parameters, and their return schemas will be defined in a dedicated Design Document prior to implementation.

---

## 3. Public Action Engine Tools

### `clarke_encrypt`
- **Description:** Encrypts plaintext data using AES-256-GCM. Requires a key to be managed by `Turing`.
- **Input Schema:**
    - `plaintext_data` (string, required): The data to encrypt (base64 encoded).
    - `key_name` (string, required): The name of the encryption key to retrieve from `Turing`.
- **Output Schema:** `{"status": "success", "ciphertext_data": "...", "tag": "...", "nonce": "...", "encoding": "base64"}`

### `clarke_decrypt`
- **Description:** Decrypts ciphertext data previously encrypted by `clarke_encrypt`.
- **Input Schema:**
    - `ciphertext_data` (string, required): The encrypted data (base64 encoded).
    - `tag` (string, required): The authentication tag (base64 encoded).
    - `nonce` (string, required): The nonce (base64 encoded).
    - `key_name` (string, required): The name of the decryption key to retrieve from `Turing`.
- **Output Schema:** `{"status": "success", "plaintext_data": "...", "encoding": "base64"}`

### `clarke_sign`
- **Description:** Creates a digital signature for data using a private key managed by `Turing`.
- **Input Schema:**
    - `data` (string, required): The data to sign (base64 encoded).
    - `key_name` (string, required): The name of the signing key to retrieve from `Turing`.
- **Output Schema:** `{"status": "success", "signature": "...", "encoding": "base64"}`

### `clarke_verify`
- **Description:** Verifies a digital signature using a public key associated with a key managed by `Turing`.
- **Input Schema:**
    - `data` (string, required): The original data (base64 encoded).
    - `signature` (string, required): The digital signature (base64 encoded).
    - `key_name` (string, required): The name of the key to retrieve from `Turing` for verification.
- **Output Schema:** `{"status": "success", "is_valid": true}`

---

## 4. Future Evolution (Post-V0)

Clarke is introduced in Phase 6 (Expansion) at V7.0 as the centralized cryptographic services platform for the mature Joshua ecosystem.

*   **Phase 6 (Expansion / V7.0):** Clarke enters the ecosystem as a fully-capable V7.0 MAD with complete PCP (DTR, LPPM, CET, CRS), pure Kafka conversation bus integration, and eMAD awareness. As the cryptographic specialist, Clarke provides core encryption, decryption, signing, and verification capabilities while coordinating with Turing for key management, Bace for authentication, and McNamara for security operations. Clarke's CET enables complex cryptographic workflows (key rotation, certificate management, secure multi-party protocols), while CRS detects potential security weaknesses and recommends proactive algorithm upgrades based on emerging threats.

*   **Post-V7.0 Enhancements:** Future evolution includes advanced cryptographic primitives (homomorphic encryption, zero-knowledge proofs, post-quantum algorithms), comprehensive PKI infrastructure management, hardware security module (HSM) integration, automated compliance monitoring (FIPS, SOC2), and cryptographic agility frameworks enabling rapid algorithm transitions in response to security research developments.

---