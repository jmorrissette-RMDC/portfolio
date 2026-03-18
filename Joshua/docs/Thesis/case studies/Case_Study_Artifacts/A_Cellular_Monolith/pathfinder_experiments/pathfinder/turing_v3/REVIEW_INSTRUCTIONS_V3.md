# Review Instructions for Turing V3 Architecture

## Your Role

You are a member of a 7-LLM review panel evaluating the **V3 (Imperator + LPPM + DTR)** architecture specification for **Turing**, building upon the approved V2 baseline.

## Review Package Contents

1. **synthesis.md** - The Turing V3 architecture specification to be reviewed
2. **ANCHOR_OVERVIEW.md** - System vision including V3 definition
3. **SYSTEM_DIAGRAM.md** - Visual architecture of all 13 MADs
4. **NON_FUNCTIONAL_REQUIREMENTS.md** - Performance, security, logging requirements
5. **MAD_ROSTER.md** - Canonical descriptions of all MADs
6. **V1_PHASE1_BASELINE.md** - Current baseline (Rogers + Dewey V1 complete)
7. **ARCHITECTURE_GUIDELINES.md** - Template structure and "Deployable" definition
8. **REVIEW_CRITERIA.md** - Complete evaluation criteria

## Your Task

Evaluate `synthesis.md` against the criteria in `REVIEW_CRITERIA.md`. Return a structured JSON review with your verdict and any objections.

## Review Criteria Summary (V3-Specific)

### 1. Version Compatibility
- **V3 = Imperator + LPPM + DTR** (Decision Tree Router)
- DTR should be present and properly integrated as first-stage router
- LPPM should be preserved from V2 (learned patterns)
- Imperator should be preserved from V1 (fallback reasoning)
- No V4 (CET) components
- All V2/V1 capabilities must be preserved

### 2. DTR Completeness
- DTR component defined with clear purpose (ultra-fast learned routing)
- ML classifier architecture specified (model type, training approach)
- Training pipeline defined (data source, learning mechanism)
- Example learned patterns provided (3+ concrete examples)
- Performance targets specified (< 10 microseconds target per NON_FUNCTIONAL_REQUIREMENTS)
- Learning mechanism defined (how DTR improves over time)

### 3. Three-Stage Routing Logic
- Clear flow: DTR → LPPM → Imperator
- DTR decision criteria (ML confidence threshold for learned patterns)
- LPPM decision criteria (confidence ≥ 0.85, unchanged from V2)
- Imperator fallback (handles novel/ambiguous requests)
- No gaps or ambiguities in routing decisions

### 4. Dependencies (V3-Specific)
- **Expected dependencies:**
  - Rogers (communication)
  - Dewey (both LPPM and DTR training data)
  - PostgreSQL (storage)
- DTR is ML-based and requires training data from Dewey
- Verify dependency declarations match actual requirements

### 5. Performance Targets (V3-Specific)
- DTR target: < 10 microseconds (per NON_FUNCTIONAL_REQUIREMENTS - research target to test)
- LPPM target: < 200ms (unchanged from V2)
- Imperator target: < 5s (unchanged from V1)
- Coverage estimates provided (DTR: 30-40%, LPPM: 30-40%, Imperator: 20-30%)
- Performance justification: How DTR achieves target or documents actual performance if different

### 6. Backward Compatibility
- All V2 tools must remain unchanged
- LPPM training pipeline preserved
- Imperator system prompt preserved
- All V1 workflows must still function
- No breaking changes to ACL, secrets, or external interfaces

### 7. All Standard Criteria
- Completeness (template sections)
- Feasibility (implementable with standard libraries)
- Consistency (aligns with anchor documents)
- Clarity (deployable by engineer)
- JSON-RPC 2.0 logging compliance
- Data contracts explicit
- Error handling specific

## V3-Specific Critical Review Focus

### 1. DTR Component Definition
Verify the document describes:
- **Purpose:** Ultra-fast routing for deterministic, high-frequency patterns through learned classification
- **Implementation:** ML-based classifier (per ANCHOR_OVERVIEW: "lightweight, fast machine learning classifier that learns")
- **Model architecture:** Classifier type (e.g., gradient-boosted trees, small neural network)
- **Training pipeline:** How DTR learns from operational data
- **Performance:** <10 microseconds target (per NON_FUNCTIONAL_REQUIREMENTS) with justification or documented actual performance
- **Learned pattern examples:** At least 3 concrete patterns DTR learns to route

### 2. Three-Stage Routing Flow
Verify clear logic for:
- Stage 1: DTR evaluates with ML classifier (confidence threshold for learned patterns)
- Stage 2: If DTR confidence insufficient, forward to LPPM (confidence ≥ 0.85)
- Stage 3: If LPPM confidence < 0.85, forward to Imperator
- No circular routing or dead ends
- Each stage has clear confidence thresholds and success/failure criteria

### 3. Training and Learning Mechanism
Verify approach for:
- How initial model is trained (data source from Dewey)
- How DTR learns and improves over time (incremental training)
- Training data pipeline (logs → features → training)
- Model versioning and deployment
- Monitoring of DTR accuracy, coverage, and performance
- Feedback loop (operational data → improved model)

### 4. Performance Claims and Research Context
Check that:
- <10 microseconds target acknowledged (per NON_FUNCTIONAL_REQUIREMENTS)
- Document either justifies how this is achieved OR documents actual achievable performance
- Performance approach explained (e.g., optimized ML inference, model size vs. speed trade-offs)
- Coverage estimates (30-40% DTR) justified
- Distribution across three stages makes sense
- No performance regression for V2/V1 paths
- Research context: This is a performance target to test, not a hard requirement that blocks approval

### 5. V2 Components Preserved
**CRITICAL:** Verify that:
- LPPM training pipeline still described (Dewey retrieval, training, validation)
- LPPM performance targets unchanged (<200ms)
- LPPM confidence threshold unchanged (0.85)
- Imperator system prompt unchanged
- All 7 tools preserved

### 6. Resource Requirements Updated
Verify deployment section reflects DTR additions:
- CPU: May increase slightly for ML inference (still lightweight classifier)
- RAM: May increase for model loading (but DTR model should be small)
- Libraries: ML libraries (`xgboost`, `scikit-learn`, `torch`, or similar)
- New environment variables: `TURING_DTR_MODEL_PATH` and possibly `TURING_DTR_CONFIDENCE_THRESHOLD`
- Training infrastructure requirements (if applicable)

## Output Format

Return a JSON object with this exact structure:

```json
{
  "reviewer": "<your-model-name>",
  "verdict": "ACCEPT or REJECT",
  "objections": [
    {
      "mad_name": "Turing",
      "document_section": "<section name or number>",
      "severity": "critical|important|minor",
      "summary": "<one-line summary>",
      "detail": "<detailed explanation of the issue>",
      "suggested_resolution": "<how to fix it>"
    }
  ]
}
```

### Severity Definitions
- **critical:** Blocks implementation or violates anchor requirements (causes REJECT verdict)
- **important:** Significant quality/clarity issue (may cause REJECT if multiple)
- **minor:** Improvement suggestion (does not affect verdict)

### Verdict Rules
- **ACCEPT:** No critical objections, at most 1-2 important objections, document is "Deployable"
- **REJECT:** At least 1 critical objection OR 3+ important objections

If you find **no objections**, return an empty `objections` array with `"verdict": "ACCEPT"`.

## Important Notes

- This is **Turing V3** (Imperator + LPPM + DTR), building on approved V2
- **IMMUTABLE PRINCIPLE:** DTR must be ML classifier that learns (per ANCHOR_OVERVIEW Core Principle: "core vision as stated in version definitions is immutable")
- DTR presence is **required** for V3, not a violation
- LPPM and Imperator must be **preserved** from V2/V1
- Dependencies include Dewey for both LPPM and DTR training
- Performance target <10 microseconds is a **research goal** - specification should attempt or document actual achievable performance
- **Research context:** This is exploratory work testing the vision, not production software
- Your review contributes to a 6/7 (86%) quorum requirement for approval

---

**Begin your review now. Return only the JSON object.**
