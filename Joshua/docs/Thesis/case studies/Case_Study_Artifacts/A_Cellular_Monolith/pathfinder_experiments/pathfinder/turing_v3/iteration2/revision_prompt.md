# Turing V3 Iteration 2 - Critical Architectural Corrections

## Issues from Iteration 1 (5/7 ACCEPT, 71% - FAILED QUORUM)

### Critical Issue #1: DTR Performance Target Wrong (Both reviewers)

**Objection:** NON_FUNCTIONAL_REQUIREMENTS.md explicitly states "< 10 microseconds" for DTR-routed content, but iteration 1 synthesis states "<50ms".

**Fact check:**
```
NON_FUNCTIONAL_REQUIREMENTS.md line ~47:
"Target (Routed Content): Median processing time of **< 10 microseconds** for deterministic content routed by the DTR directly to the Action Engine."
```

**Fix:** Update ALL performance targets for DTR from "<50ms" to "<10 microseconds (µs)". This applies to:
- Section 2.3 DTR Configuration performance targets
- Section 2.4 Routing Logic timing diagram
- Section 6 Deployment (if mentioned)
- Any example workflows showing DTR timing

### Critical Issue #2: DTR Nature Mismatch (Grok-4)

**Objection:** ANCHOR_OVERVIEW.md describes DTR as "a lightweight, fast machine learning classifier that inspects incoming messages. It learns to immediately route..." but iteration 1 implements it as hand-authored regex rules with NO learning mechanism.

**Fact check:**
```
ANCHOR_OVERVIEW.md:
"The DTR is a lightweight, fast machine learning classifier that inspects incoming messages. It learns to immediately route deterministic content..."
```

**Fix:** Completely revise Section 2.3 DTR Configuration to be ML-based:

**NEW DTR Implementation Approach:**

**Purpose:** Ultra-fast ML-based routing classifier for deterministic patterns

**Architecture:**
- **Model:** Lightweight classifier (e.g., XGBoost, small neural network, or decision tree ensemble)
- **Input features:** Message length, keyword presence, MAD identity, conversation type, structural markers
- **Output:** Route decision (DTR_DIRECT, FORWARD_TO_LPPM) + confidence score
- **Inference time:** <10 microseconds (achievable with tree-based models on CPU)

**Training Pipeline:**
1. **Data source:** LPPM and Imperator success logs from Dewey (same source as LPPM training)
2. **Feature extraction:** Convert messages to numeric features (bag-of-words, length, patterns)
3. **Label generation:** Messages that LPPM handled with confidence >0.95 are labeled "DTR_DIRECT candidates"
4. **Training:** Incremental training weekly using new success data
5. **Validation:** Model must achieve >98% accuracy on held-out test set before deployment
6. **Deployment:** Model checkpoints stored similar to LPPM

**Learned Pattern Examples:**
- After 30 days, DTR learns that messages starting with "get secret" + single word = direct `get_secret` call
- Messages matching "list" + no parameters = direct `list_secrets` call
- Grant/revoke patterns with standard syntax = direct ACL calls

**Key difference from LPPM:**
- DTR: Binary classifier (can I route directly or not?) - very fast, simple model
- LPPM: Sequence-to-sequence (prose → tool call JSON) - slower, complex model

**Routing Logic:**
1. DTR checks if message matches learned "direct route" patterns (confidence >0.90)
2. If yes: Extract parameters using learned extraction rules and execute
3. If no: Forward to LPPM

**DTR vs. LPPM Coverage:**
- DTR handles: Simple, structured, high-frequency commands (30-40% after training)
- LPPM handles: More complex prose-to-process mappings (30-40%)
- Imperator handles: Novel, ambiguous, or complex reasoning (20-30%)

### Important Issue: Imperator Fallback Handling (GPT-4o)

**Objection:** "Section 2.4 does not clearly explain how the system responds when a request fails to match both DTR and LPPM."

**Fix:** In Section 2.4 Routing Logic, explicitly state:

```markdown
**Stage 3: Imperator Fallback (Final Stage)**
If LPPM confidence < 0.85, the request is forwarded to the Imperator for full reasoning. The Imperator ALWAYS provides a response - it either:
1. Successfully maps the request to a tool call and executes it
2. Asks clarifying questions to the requesting MAD
3. Returns an error response if the request is malformed or unauthorized

There is no scenario where a request "fails" through all three stages - the Imperator is the universal fallback that handles ALL requests, including novel, ambiguous, or complex ones.
```

---

## Task

Revise iteration 1 synthesis to:
1. **Change DTR from hand-authored rules to ML classifier that learns** (Section 2.3)
   - Add training pipeline (similar to LPPM but simpler)
   - Specify model type (tree-based for microsecond inference)
   - Explain how it learns from LPPM/Imperator successes
   - Keep examples but frame as "learned patterns" not "hand-authored rules"

2. **Change ALL DTR performance targets from "<50ms" to "<10 microseconds"**
   - Section 2.3 performance targets
   - Section 2.4 routing timing
   - Any deployment or example sections

3. **Clarify Imperator as universal fallback** (Section 2.4)
   - Explicitly state Imperator handles all requests that reach it
   - No requests "fail" through the three stages

4. **Update deployment section for ML model**
   - DTR model checkpoints storage location
   - Training infrastructure requirements
   - Libraries: Add ML libraries (xgboost, sklearn, or similar)

5. **Keep all V2/V1 content unchanged**
   - LPPM training pipeline preserved
   - Imperator configuration preserved
   - All 7 tools preserved

## Critical Requirements

✅ DTR must be ML-based classifier that LEARNS (not hand-authored rules)
✅ DTR performance target must be <10 microseconds (not milliseconds)
✅ DTR training pipeline must be specified
✅ Imperator fallback must be explicitly described as universal handler
✅ All V2 capabilities preserved

This addresses 2 critical objections from Grok-4 and GPT-4o.
