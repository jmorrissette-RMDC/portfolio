# Review Instructions for Turing V4 Architecture

## Your Role

You are a member of a 7-LLM review panel evaluating the **V4 (Imperator + LPPM + DTR + CET)** architecture specification for **Turing**, building upon the approved V3 baseline.

## Review Package Contents

1. **synthesis.md** - The Turing V4 architecture specification to be reviewed
2. **ANCHOR_OVERVIEW.md** - System vision including V4 definition
3. **SYSTEM_DIAGRAM.md** - Visual architecture of all 13 MADs
4. **NON_FUNCTIONAL_REQUIREMENTS.md** - Performance, security, logging requirements
5. **MAD_ROSTER.md** - Canonical descriptions of all MADs
6. **V1_PHASE1_BASELINE.md** - Current baseline (Rogers + Dewey V1 complete)
7. **ARCHITECTURE_GUIDELINES.md** - Template structure and "Deployable" definition
8. **REVIEW_CRITERIA.md** - Complete evaluation criteria

## Your Task

Evaluate `synthesis.md` against the criteria in `REVIEW_CRITERIA.md`. Return a structured JSON review with your verdict and any objections.

## Review Criteria Summary (V4-Specific)

### 1. Version Compatibility
- **V4 = Imperator + LPPM + DTR + CET** (Context Engineering Transformer)
- CET should be present and properly integrated before Imperator
- DTR should be preserved from V3 (ML classifier that learns)
- LPPM should be preserved from V2 (learned patterns)
- Imperator should be preserved from V1 (fallback reasoning)
- All V3/V2/V1 capabilities must be preserved

### 2. CET Completeness
- CET component defined with clear purpose (dynamic context assembly)
- ML architecture specified (**per ANCHOR: "sophisticated neural network"**)
- Training pipeline defined (learns from Imperator success/failure patterns)
- Context sources specified (conversation history, Dewey archives, external docs, MAD data)
- Performance impact acknowledged (small overhead per ANCHOR)
- Demonstrates ICCM (Intelligent Conversation and Context Management) principle

### 3. Four-Stage Routing Logic
- Clear flow: DTR → LPPM → CET → Imperator
- DTR handles learned deterministic patterns (unchanged from V3)
- LPPM handles learned prose-to-process (unchanged from V3)
- **CET only invoked for Imperator-bound requests** (not for DTR/LPPM paths)
- CET assembles optimal context before Imperator reasoning
- No gaps or ambiguities in routing decisions

### 4. Dependencies (V4-Specific)
- **Expected dependencies:**
  - Rogers (communication)
  - Dewey (DTR training, LPPM training, AND CET context retrieval)
  - PostgreSQL (storage)
- CET requires Dewey for context retrieval from archives
- Verify dependency declarations match actual requirements

### 5. Performance Targets (V4-Specific)
- DTR target: <10 microseconds (research goal, unchanged from V3)
- LPPM target: <200ms (unchanged from V3)
- CET overhead: Small (per ANCHOR: "adds a small amount of processing time")
  - Reasonable target: <500ms for context assembly
- Imperator+CET: <5s total (unchanged overall target)
- **Net benefit:** 20-40% improvement in task completion (per NON_FUNCTIONAL_REQUIREMENTS)
- Performance justification: CET improves reasoning quality despite overhead

### 6. Backward Compatibility
- All V3 tools must remain unchanged
- DTR training pipeline preserved
- LPPM training pipeline preserved
- Imperator configuration preserved
- All V1 workflows must still function
- No breaking changes to ACL, secrets, or external interfaces

### 7. All Standard Criteria
- Completeness (template sections)
- Feasibility (implementable with ML libraries)
- Consistency (aligns with anchor documents)
- Clarity (deployable by engineer)
- JSON-RPC 2.0 logging compliance
- Data contracts explicit
- Error handling specific

## V4-Specific Critical Review Focus

### 1. CET Component Definition
Verify the document describes:
- **Purpose:** Dynamic context assembly for optimal Imperator reasoning
- **Implementation:** ML-based neural network (per ANCHOR: "sophisticated neural network")
- **Model architecture:** Transformer-based or similar for context relevance
- **Training pipeline:** How CET learns from Imperator outcomes
- **Context sources:** Conversation history, Dewey archives, external data, MAD state
- **Performance:** Small overhead with net benefit to reasoning quality
- **ICCM principle:** How CET embodies "context as engineered resource"

### 2. Four-Stage Routing Flow
Verify clear logic for:
- Stage 1: DTR evaluates with ML classifier (learned deterministic patterns)
- Stage 2: If DTR confidence insufficient, forward to LPPM (learned prose-to-process)
- Stage 3: If LPPM confidence < 0.85, forward to CET for context assembly
- Stage 4: CET assembles optimal context, forwards to Imperator with engineered context
- **Key:** CET is only invoked for Imperator-bound requests, not DTR/LPPM paths
- No circular routing or dead ends
- Each stage has clear success/failure criteria

### 3. CET Training and Learning
Verify approach for:
- How CET learns which contexts are relevant (feedback from Imperator outcomes)
- Training data pipeline (Imperator requests + contexts + outcomes → training data)
- Model versioning and deployment
- Continuous improvement mechanism
- Validation: Measured improvement in Imperator success rate (20-40% target)

### 4. Performance Claims and Research Context
Check that:
- All V3 performance targets preserved (DTR <10µs, LPPM <200ms)
- CET overhead is "small" and justified (per ANCHOR requirement)
- Net benefit documented: Better reasoning quality → faster problem resolution
- 20-40% task completion improvement target (per NON_FUNCTIONAL_REQUIREMENTS)
- Research context: Performance targets are goals to test, not hard blockers

### 5. V3 Components Preserved
**CRITICAL:** Verify that:
- DTR training pipeline still described (ML classifier that learns)
- LPPM training pipeline still described (Dewey retrieval, training, validation)
- Imperator system prompt unchanged
- All 7 tools preserved
- Three-stage filtering (DTR → LPPM → Imperator) preserved with CET added before Imperator

### 6. Resource Requirements Updated
Verify deployment section reflects CET additions:
- CPU: May increase (0.75-1.0 cores for CET context assembly)
- RAM: May increase (768 MB - 1 GB for CET model loading)
- Libraries: Transformer libraries (`transformers`, `sentence-transformers`, or similar)
- New environment variables: `TURING_CET_MODEL_PATH`, `TURING_CET_CONTEXT_LIMIT`, etc.
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

- This is **Turing V4** (Imperator + LPPM + DTR + CET), building on approved V3
- **IMMUTABLE PRINCIPLE:** Core vision from ANCHOR_OVERVIEW defines requirements (per Core Principle #1)
- **CET must be sophisticated neural network** (per ANCHOR_OVERVIEW V4 definition)
- CET presence is **required** for V4, not a violation
- DTR, LPPM, and Imperator must be **preserved** from V3/V2/V1
- Dependencies include Dewey for training AND context retrieval
- Performance targets are **research goals** - specification should attempt or document achievable performance
- **Research context:** This is exploratory work testing the immutable vision
- Your review contributes to a 6/7 (86%) quorum requirement for approval

---

**Begin your review now. Return only the JSON object.**
