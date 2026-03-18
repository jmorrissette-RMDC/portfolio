# === GRACE V3 DELTA ===
# Grace V3 Architecture Specification

**This document assumes the approved V2 architecture as a baseline. It describes ONLY the deltas required to add V3 capabilities.**

## 1. Overview
- **New in this Version:** V3 adds the Decision Tree Router (DTR) as an ultra-fast classification layer in the Thinking Engine. The DTR sits before the LPPM and provides <10ms routing for the most common request patterns. The DTR→LPPM→Imperator cascade provides three tiers of speed optimization. All V2 functionality is preserved unchanged.

## 2. Thinking Engine
### 2.3 DTR Integration (V3+)
- **DTR Integration (V3+):** Grace's DTR is a gradient-boosted decision tree classifier trained on the same data sources as the LPPM. It performs ultra-fast classification-based routing for the most common request patterns.
  - **Training Data Sources:**
    - V1/V2 production logs (same as LPPM)
    - Synthetic data from Fiedler
    - Hand-crafted golden examples
  - **Model Architecture:**
    - Gradient-boosted decision tree (XGBoost)
    - TF-IDF feature extraction (top 500 features)
    - Classification into 8 common request types + "OTHER"
    - Model size: 64-128 MB on disk
  - **Routing Logic:**
    - DTR invoked first for every request
    - IF confidence > 98% AND recognized pattern → Direct tool call (< 10ms)
    - ELSE IF confidence 90-98% → Pass to LPPM for refinement
    - ELSE (confidence < 90% OR "OTHER") → Fall back to Imperator
  - **Example Ultra-Fast Paths:**
    - "Serve the homepage" (GET /)
    - "Fetch the main stylesheet" (GET /css/main.css)
    - "Process user login" (POST /api/login)
    - "Get user profile for user_id 123" (GET /api/users/123)
  - **Training Loop:**
    - Initial training: 4 hours on 100K V1/V2 logs
    - Continuous learning: Weekly retraining with new production data
    - Validation: 98% accuracy on top-10 request types before deployment

## 6. Deployment (Changes from V2)
- **Container Requirements - Resources (UPDATED):**
  - **RAM:** 384 MB (increased from 256 MB)
    - V2 baseline: 256 MB
    - DTR model: +128 MB
    - Total V3: 384 MB

- **Configuration (NEW variable):**

| Variable | Description | Example Value |
|---|---|---|
| `GRACE_DTR_MODEL_PATH` | Path to the trained DTR model file. | `/models/dtr/grace_dtr_v3.onnx` |

## 7. Testing Strategy (V3 Additions)
- **DTR Accuracy Tests:**
  - Test DTR on 1000-sample validation set
  - Verify >98% accuracy for top-10 request types
  - Verify correct handoff to LPPM/Imperator for low-confidence requests

- **Latency Comparison:**
  - Measure P50, P95, P99 latency for DTR ultra-fast path vs. LPPM fast path vs. Imperator reasoning
  - Target: DTR path <10ms, LPPM path <50ms, Imperator path 500-2000ms

## 8. Example Workflows (V3 Enhancements)
- **Workflow: Serving static asset**
  1. Request: "GET /images/logo.png"
  2. Grace's DTR receives the request.
  3. DTR classifies the request as `serve_static_asset` with 100% confidence.
  4. DTR bypasses LPPM/Imperator and directly serves the file from the web root.
  5. The image is returned in <10ms.
