# === HOPPER V2 DELTA ===
# Hopper V2 Architecture Specification

**This document assumes the approved V1 architecture as a baseline. It describes ONLY the deltas required to add V2 capabilities.**

## 1. Overview
- **New in this Version:** V2 adds the Learned Prose-to-Process Mapper (LPPM) as a performance optimization layer in the Thinking Engine. The LPPM recognizes common request patterns and maps them directly to tool calls, bypassing full Imperator reasoning for significant speed gains. All V1 functionality is preserved unchanged.

## 2. Thinking Engine
### 2.2 LPPM Integration (V2+)
- **LPPM Integration (V2+):** Hopper's LPPM is a distilled transformer model trained on historical conversation logs from V1 deployments. It learns to recognize common request patterns and map them directly to tool call sequences.
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
    - "What is the status of Horace?" → `get_mad_status(name='horace-v2')`
    - "List all running MADs" → `list_mads()`
    - "Restart fiedler-v2" → `restart_mad(name='fiedler-v2')`
    - "Stop gates-v2" → `stop_mad(name='gates-v2')`
    - "Rollback the last deployment of Marco" → `rollback_deployment(name='marco-v2')`
  - **Training Loop:**
    - Initial training: 24 hours on 100K V1 logs
    - Continuous learning: Weekly retraining with new V1/V2 production data
    - Validation: 95% accuracy on held-out test set before deployment

## 6. Deployment (Changes from V1)
- **Container Requirements - Resources (UPDATED):**
  - **RAM:** 2048 MB (increased from 1536 MB)
    - V1 baseline: 1536 MB
    - LPPM model: +512 MB
    - Total V2: 2048 MB

- **Configuration (NEW variable):**

| Variable | Description | Example Value |
|---|---|---|
| `HOPPER_LPPM_MODEL_PATH` | Path to the trained LPPM model file. | `/models/lppm/hopper_lppm_v2.onnx` |

## 7. Testing Strategy (V2 Additions)
- **LPPM Accuracy Tests:**
  - Test LPPM on 1000-sample validation set
  - Verify >95% accuracy for common patterns
  - Verify correct fallback to Imperator for low-confidence requests

- **Latency Comparison:**
  - Measure P50, P95, P99 latency for LPPM fast path vs. Imperator reasoning
  - Target: LPPM fast path <50ms, Imperator path 500-2000ms

## 8. Example Workflows (V2 Enhancements)
No workflow changes from V1.
