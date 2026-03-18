# === TURING V2 DELTA ===
# Turing V2 Architecture Specification

**This document assumes the approved V1 architecture as a baseline. It describes ONLY the deltas required to add V2 capabilities.**

## 1. Overview
- **New in this Version:** V2 adds the Learned Prose-to-Process Mapper (LPPM) as a performance optimization layer in the Thinking Engine. The LPPM recognizes common request patterns and maps them directly to tool calls, bypassing full Imperator reasoning for significant speed gains. All V1 functionality is preserved unchanged.

## 2. Thinking Engine
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

## 6. Deployment (Changes from V1)
- **Container Requirements - Resources (UPDATED):**
  - **RAM:** 1280 MB (increased from 768 MB)
    - V1 baseline: 768 MB
    - LPPM model: +512 MB
    - Total V2: 1280 MB

- **Configuration (NEW variable):**

| Variable | Description | Example Value |
|---|---|---|
| `TURING_LPPM_MODEL_PATH` | Path to the trained LPPM model file. | `/models/lppm/turing_lppm_v2.onnx` |

## 7. Testing Strategy (V2 Additions)
- **LPPM Accuracy Tests:**
  - Test LPPM on 1000-sample validation set
  - Verify >95% accuracy for common patterns
  - Verify correct fallback to Imperator for low-confidence requests

- **Latency Comparison:**
  - Measure P50, P95, P99 latency for LPPM fast path vs. Imperator reasoning
  - Target: LPPM fast path <50ms, Imperator path 500-2000ms

## 8. Example Workflows (V2 Enhancements)
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
