# === GATES V2 DELTA ===
# Gates V2 Architecture Specification

**This document assumes the approved V1 architecture as a baseline. It describes ONLY the deltas required to add V2 capabilities.**

## 1. Overview
- **New in this Version:** V2 adds the Learned Prose-to-Process Mapper (LPPM) as a performance optimization layer in the Thinking Engine. The LPPM recognizes common request patterns and maps them directly to tool calls, bypassing full Imperator reasoning for significant speed gains. All V1 functionality is preserved unchanged.

## 2. Thinking Engine
### 2.2 LPPM Integration (V2+)
- **LPPM Integration (V2+):** Gates's LPPM is a distilled transformer model trained on historical conversation logs from V1 deployments. It learns to recognize common request patterns and map them directly to tool call sequences.
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
    - "Run this python code: print('hi')" → `execute_code(language='python', code="print('hi')")`
    - "Execute `ls -l` in bash" → `execute_code(language='bash', code='ls -l')`
    - "What is the status of exec-123?" → `get_execution_status(execution_id='exec-123')`
    - "Cancel execution exec-456" → `cancel_execution(execution_id='exec-456')`
    - "List available environments" → `list_environments()`
  - **Training Loop:**
    - Initial training: 24 hours on 100K V1 logs
    - Continuous learning: Weekly retraining with new V1/V2 production data
    - Validation: 95% accuracy on held-out test set before deployment

## 6. Deployment (Changes from V1)
- **Container Requirements - Resources (UPDATED):**
  - **RAM:** 1536 MB (increased from 1024 MB)
    - V1 baseline: 1024 MB
    - LPPM model: +512 MB
    - Total V2: 1536 MB

- **Configuration (NEW variable):**

| Variable | Description | Example Value |
|---|---|---|
| `GATES_LPPM_MODEL_PATH` | Path to the trained LPPM model file. | `/models/lppm/gates_lppm_v2.onnx` |

## 7. Testing Strategy (V2 Additions)
- **LPPM Accuracy Tests:**
  - Test LPPM on 1000-sample validation set
  - Verify >95% accuracy for common patterns
  - Verify correct fallback to Imperator for low-confidence requests

- **Latency Comparison:**
  - Measure P50, P95, P99 latency for LPPM fast path vs. Imperator reasoning
  - Target: LPPM fast path <50ms, Imperator path 500-2000ms

## 8. Example Workflows (V2 Enhancements)
### Scenario 1: Simple Code Execution from Grace
1.  **User (via Grace):** "Gates, run this python code: `for i in range(3): print(f'Line {i}')`"
2.  **Grace -> Gates:** Sends `execute_code(language='python', code='...')`.
3.  **Gates' LPPM:** Recognizes this as a simple execution request and bypasses the Imperator.
4.  **Gates -> Grace:** Immediately responds with `{ "execution_id": "exec-123", "status": "started" }`.
5.  **Gates' Action Engine:** Starts a `python:3.11-slim` container and runs the code.
6.  **Gates -> Grace (stream 1):** Sends a log message: `{ "method": "execution_log", "params": { "execution_id": "exec-123", "stream": "stdout", "line": "Line 0" } }`.
7.  **Gates -> Grace (stream 2):** Sends `{ ... "line": "Line 1" }`.
8.  **Gates -> Grace (stream 3):** Sends `{ ... "line": "Line 2" }`.
9.  **Gates:** The container exits. Gates destroys it.
10. **Gates -> Grace (final result):** Sends `{ "method": "execution_result", "params": { "execution_id": "exec-123", "status": "completed", "exit_code": 0, ... } }`.
11. **Grace:** Formats the streamed logs and the final result for the user.
