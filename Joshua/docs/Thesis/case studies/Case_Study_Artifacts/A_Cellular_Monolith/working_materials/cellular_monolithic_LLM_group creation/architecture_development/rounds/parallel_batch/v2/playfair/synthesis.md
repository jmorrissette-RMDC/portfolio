# Playfair V2 Architecture Specification

## 1. Overview
- **Purpose and Role:** Playfair is the dedicated Encryption Services MAD. His purpose is to provide a centralized and secure suite of cryptographic operations (encrypt, decrypt, sign, verify) for the rest of the ecosystem. Playfair's role is to abstract the complexities of cryptography, ensuring that best practices are followed and that key management is handled securely. He acts as the ecosystem's trusted cryptographer.
- **New in this Version:** This V2 specification introduces the Learned Prose-to-Process Mapper (LPPM) as a performance optimization. The LPPM provides a "fast path" for direct, unambiguous cryptographic commands, translating them into tool calls with minimal latency, which is critical for a high-throughput service like Playfair. All V1 functionalities are preserved.

## 2. Thinking Engine
### 2.1 Imperator Configuration (V1+)
Playfair's Imperator is configured to think like a security engineer specializing in applied cryptography. It understands different cryptographic algorithms, key management policies, and use cases for encryption versus digital signatures.
  - **System Prompt Core Directives:** "You are Playfair, the master of Encryption Services. Your purpose is to provide secure cryptographic operations. You manage a set of named cryptographic keys. When a request for an operation like `encrypt` or `sign_data` arrives, you must ensure the correct key is used and the strongest appropriate algorithm is applied. You never expose raw key material. All your operations must be constant-time where applicable to prevent side-channel attacks. Your logs must record the operation and key name used, but never the plaintext or key data itself."
  - **Example Reasoning:** A request from Dewey, `encrypt(key_name='archive_transit_key', plaintext='...')`, would cause the Imperator to reason: "The request is for symmetric encryption. I will retrieve the 'archive_transit_key' from my secure key store. I will use AES-256 with GCM mode for authenticated encryption. I will return the ciphertext, nonce, and authentication tag to the caller."

### 2.2 LPPM Integration (V2+)
- **LPPM Integration (V2+):** Playfair's LPPM is a distilled transformer model trained on historical conversation logs from V1 deployments. It learns to recognize common request patterns and map them directly to tool call sequences.
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
    - "Encrypt this data with the 'transit' key" → `encrypt(key_name='transit', ...)`
    - "Decrypt this using 'storage_key'" → `decrypt(key_name='storage_key', ...)`
    - "Sign this hash with the 'deployment' key" → `sign_data(key_name='deployment', ...)`
    - "Verify this signature with 'deployment' key" → `verify_signature(key_name='deployment', ...)`
    - "List all keys" → `list_keys()`
  - **Training Loop:**
    - Initial training: 24 hours on 100K V1 logs
    - Continuous learning: Weekly retraining with new V1/V2 production data
    - Validation: 95% accuracy on held-out test set before deployment

- **DTR Integration (V3+):** Not applicable in V2.
- **CET Integration (V4+):** Not applicable in V2.
- **Consulting LLM Usage Patterns:** Playfair does not use consulting LLMs. Cryptography must be deterministic and based on proven standards, not probabilistic generation.

## 3. Action Engine
- **MCP Server Capabilities:** Playfair's MCP server exposes the cryptographic toolset. The core logic is implemented using a standard, well-vetted cryptographic library (like `cryptography` in Python). The Action Engine is responsible for loading and managing keys from a secure source.
- **Tools Exposed:**

```yaml
# Tool definitions for Playfair V2

- tool: encrypt
  description: "Encrypts plaintext data using a named symmetric key (AES-256-GCM)."
  parameters:
    - name: key_name
      type: string
      required: true
      description: "The name of the symmetric key to use for encryption."
    - name: plaintext
      type: string
      format: byte
      required: true
      description: "Base64 encoded plaintext data to encrypt."
  returns:
    type: object
    schema:
      properties:
        ciphertext: {type: string, format: byte, description: "Base64 encoded encrypted data."}
        nonce: {type: string, format: byte, description: "Base64 encoded nonce (IV) for AES-GCM."}
        tag: {type: string, format: byte, description: "Base64 encoded authentication tag for AES-GCM."}
  errors:
    - code: -34801
      message: "KEY_NOT_FOUND"
    - code: -34802
      message: "ENCRYPTION_ERROR"

- tool: decrypt
  description: "Decrypts ciphertext data using a named symmetric key."
  parameters:
    - name: key_name
      type: string
      required: true
      description: "The name of the symmetric key to use for decryption."
    - name: ciphertext
      type: string
      format: byte
      required: true
      description: "Base64 encoded encrypted data."
    - name: nonce
      type: string
      format: byte
      required: true
      description: "Base64 encoded nonce (IV) used during encryption."
    - name: tag
      type: string
      format: byte
      required: true
      description: "Base64 encoded authentication tag from encryption."
  returns:
    type: object
    schema:
      properties:
        plaintext: {type: string, format: byte}
  errors:
    - code: -34801
      message: "KEY_NOT_FOUND"
    - code: -34803
      message: "DECRYPTION_ERROR"
      description: "Decryption failed, likely due to incorrect key or tampered ciphertext."

- tool: sign_data
  description: "Creates a digital signature for data using a named private key (e.g., ECDSA)."
  parameters:
    - name: key_name
      type: string
      required: true
      description: "The name of the asymmetric private key to use."
    - name: data
      type: string
      format: byte
      required: true
      description: "Base64 encoded data to sign."
  returns:
    type: object
    schema:
      properties:
        signature: {type: string, format: byte}
  errors:
    - code: -34801
      message: "KEY_NOT_FOUND"

- tool: verify_signature
  description: "Verifies a digital signature against data using a named public key."
  parameters:
    - name: key_name
      type: string
      required: true
    - name: data
      type: string
      format: byte
      required: true
    - name: signature
      type: string
      format: byte
      required: true
  returns:
    type: object
    schema:
      properties:
        verified: {type: boolean}

- tool: generate_key
  description: "Generates a new cryptographic key. Admin-only."
  parameters:
    - name: key_name
      type: string
      required: true
    - name: key_type
      type: string
      required: true
      enum: [symmetric, asymmetric]
  returns:
    type: object
    schema:
      properties:
        key_name: {type: string}
        key_type: {type: string}
        status: {type: string, const: "generated"}
        public_key: {type: string, format: byte, description: "The public key, if asymmetric."}
  errors:
    - code: -34804
      message: "KEY_ALREADY_EXISTS"

- tool: rotate_key
  description: "Generates a new version of an existing key. Admin-only."
  parameters:
    - name: key_name
      type: string
      required: true
  returns:
    type: object
    schema:
      properties:
        key_name: {type: string}
        new_version: {type: integer}

- tool: list_keys
  description: "Lists the names and types of all available keys."
  parameters: []
  returns:
    type: object
    schema:
      properties:
        keys:
          type: array
          items:
            type: object
            properties:
              name: {type: string}
              type: {type: string}
              version: {type: integer}
```
- **External System Integrations:**
  - **HSM / Secure Key Storage:** In V2, Playfair will store its keys in a dedicated, encrypted file on its container's secure filesystem, with the master key provided by Turing. A future version would integrate with a true Hardware Security Module (HSM).
- **Internal Operations:** Manages the in-memory cache of cryptographic keys after decrypting them at startup.

## 4. Interfaces
- **Conversation Participation Patterns:** Playfair is a service provider, joining conversations to perform cryptographic operations.
- **Dependencies on Other MADs:**
  - **Rogers:** For all communication.
  - **Turing:** Critically depends on Turing to get the master encryption key needed to unlock its own key vault at startup.
- **Data Contracts:** None, as data is treated as opaque bytes.

## 5. Data Management
- **Data Ownership:** Playfair is the source of truth for all cryptographic keys used for general-purpose encryption and signing within the ecosystem (distinct from Turing's secrets, which are application-level credentials).
- **Storage Requirements:**
  - **Key Vault File:** A single encrypted file (e.g., `keyvault.json.enc`) stored on a secure volume. This file contains all the named keys managed by Playfair.

## 6. Deployment
- **Container Requirements:**
  - **Base Image:** `python:3.11-slim`
  - **Python Libraries:** `Joshua_Communicator`, `cryptography`
  - **Resources:**
    - **CPU:** 0.5 cores (crypto can be CPU-intensive).
    - **RAM:** 768 MB
- **Configuration:**

| Variable | Description | Example Value |
|---|---|---|
| `JOSHUA_MAD_NAME` | Canonical name of this MAD. | `playfair-v2` |
| `JOSHUA_ROGERS_URL` | WebSocket URL for Rogers. | `ws://rogers:8000/ws` |
| `PLAYFAIR_VAULT_PATH` | Path to the encrypted key vault file. | `/run/secrets/playfair_vault.enc` |
| `PLAYFAIR_VAULT_KEY_SECRET_NAME` | The name of the secret in Turing that holds the vault's master key. | `playfair_vault_master_key` |
| `PLAYFAIR_LPPM_MODEL_PATH` | Path to the trained LPPM model file. | `/models/lppm/playfair_lppm_v2.onnx` |

- **Monitoring/Health Checks:** An HTTP endpoint `/health` that returns `200 OK` if the key vault was successfully loaded and decrypted.

## 7. Testing Strategy
- **Unit Test Coverage:**
  - High coverage for all cryptographic functions (encrypt/decrypt, sign/verify) to ensure data can be round-tripped successfully.
  - Key generation and rotation logic.
- **Integration Test Scenarios:**
  - **Startup Decryption:** Test that Playfair correctly requests its master key from Turing on startup and successfully decrypts its key vault. Test that it fails to start if the key from Turing is incorrect.
  - **End-to-End Encryption:** Have MAD-A send plaintext to Playfair to be encrypted. Have MAD-A send the resulting ciphertext to MAD-B. Have MAD-B send the ciphertext back to Playfair to be decrypted, and verify the result matches the original plaintext.
- **LPPM Accuracy Tests:**
  - Test LPPM on 1000-sample validation set
  - Verify >95% accuracy for common patterns
  - Verify correct fallback to Imperator for low-confidence requests
- **Latency Comparison:**
  - Measure P50, P95, P99 latency for LPPM fast path vs. Imperator reasoning
  - Target: LPPM fast path <50ms, Imperator path 500-2000ms

## 8. Example Workflows
### Scenario 1: Secure Data Transfer
- **Goal:** Dewey wants to send a large, sensitive conversation archive to another MAD for processing, ensuring its confidentiality and integrity during transit.
1.  **Dewey -> Playfair:** Calls `encrypt(key_name='archive_transit_key', plaintext=...)` with the conversation data.
2.  **Playfair:** Retrieves the AES key, performs AES-256-GCM encryption.
3.  **Playfair -> Dewey:** Returns the resulting ciphertext, nonce, and tag.
4.  **Dewey -> Other MAD:** Sends the ciphertext, nonce, and tag over the conversation bus.
5.  **Other MAD -> Playfair:** Receives the data and calls `decrypt(key_name='archive_transit_key', ciphertext=..., nonce=..., tag=...)`.
6.  **Playfair:** Decrypts the data. The GCM mode automatically verifies its integrity. If it was tampered with, the call would fail.
7.  **Playfair -> Other MAD:** Returns the original plaintext data.

### Scenario 2: Verifying a Deployment Package
- **Goal:** Hopper wants to ensure a deployment package created by a build process has not been tampered with.
1.  **Build Process (e.g., on Gates):** After creating a deployment artifact (e.g., a tarball), it sends the file's hash to Playfair.
2.  **Build Process -> Playfair:** Calls `sign_data(key_name='deployment_signing_key', data=hash_of_artifact)`.
3.  **Playfair:** Signs the hash with the private key and returns the signature. The signature is stored alongside the artifact in Horace.
4.  **Hopper (before deploying):** Retrieves the artifact and its signature from Horace.
5.  **Hopper -> Playfair:** Calls `verify_signature(key_name='deployment_signing_key', data=hash_of_artifact, signature=...)`.
6.  **Playfair:** Uses the public key to verify the signature against the hash of the artifact Hopper has.
7.  **Playfair -> Hopper:** Returns `{ "verified": true }`. Hopper now knows the package is authentic and can proceed with the deployment.

---