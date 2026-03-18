# === HORACE V4 DELTA ===
# Horace V4 Architecture Specification

**This document assumes the approved V3 architecture as a baseline. It describes ONLY the deltas required to add V4 capabilities.**

## 1. Overview
- **New in this Version:** V4 adds the Context Engineering Transformer (CET) as the final optimization layer in the Thinking Engine. The CET sits before the Imperator in the fallback path and performs context engineering—compressing and structuring requests and conversation history into optimal prompts. This results in 25-40% faster Imperator reasoning and improved accuracy. The complete cascade is now: DTR → LPPM → CET + Imperator. All V3 functionality is preserved unchanged.

## 2. Thinking Engine
### 2.4 CET Integration (V4+)
- **CET Integration (V4+):** Horace's CET is a small transformer model trained on successful Imperator reasoning chains from V1/V2/V3 production. It performs context engineering to create optimal prompts for the Imperator.
  - **Training Data Sources:**
    - V1/V2/V3 production logs with successful Imperator reasoning
    - Synthetic examples from Fiedler demonstrating effective prompt structures
    - Hand-crafted golden examples for complex scenarios
  - **Model Architecture:**
    - Small transformer (distilled GPT-style decoder, 6 layers, 512 hidden dims)
    - Encoder-decoder structure for context compression
    - Model size: 256-384 MB on disk
  - **Context Engineering Process:**
    - Input: Raw request + conversation history (up to 8K tokens)
    - Processing: Compress, summarize, highlight relevant context, filter noise
    - Output: Engineered context (2K-4K tokens) optimized for Imperator
    - Latency: 50-150ms for context engineering
  - **Integration Point:** CET is invoked when both DTR and LPPM defer to Imperator (confidence thresholds not met)
  - **Benefits:**
    - Imperator latency reduced by 25-40% (300-1500ms vs 500-2000ms baseline)
    - Improved Imperator accuracy through better-structured prompts
    - Lower API costs due to smaller prompts
  - **Training Loop:**
    - Initial training: 12 hours on 50K V1/V2/V3 Imperator logs
    - Continuous learning: Bi-weekly retraining with production feedback
    - Validation: Imperator accuracy >99%, latency reduced by 30%

## 6. Deployment (Changes from V3)
- **Container Requirements - Resources (UPDATED):**
  - **RAM:** 1152 MB (increased from 768 MB)
    - V3 baseline: 768 MB
    - CET model: +384 MB
    - Total V4: 1152 MB

- **Configuration (NEW variable):**

| Variable | Description | Example Value |
|---|---|---|
| `HORACE_CET_MODEL_PATH` | Path to the trained CET model file. | `/models/cet/horace_cet_v4.onnx` |

## 7. Testing Strategy (V4 Additions)
- **CET Context Engineering Tests:**
  - Test CET on 500-sample validation set
  - Verify context compression (8K → 2-4K tokens) maintains key information
  - Verify Imperator accuracy with CET-engineered prompts matches baseline (>99%)

- **Latency Comparison:**
  - Measure P50, P95, P99 latency for full cascade: DTR → LPPM → CET+Imperator
  - Target: CET context engineering 50-150ms, CET+Imperator total 350-1650ms (vs 500-2000ms V3 baseline)

## 8. Example Workflows (V4 Enhancements)
No workflow changes from V3.
