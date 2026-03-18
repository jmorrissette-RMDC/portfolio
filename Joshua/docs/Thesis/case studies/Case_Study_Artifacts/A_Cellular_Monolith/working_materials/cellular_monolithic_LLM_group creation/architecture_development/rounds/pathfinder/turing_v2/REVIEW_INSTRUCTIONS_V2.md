# Review Instructions for Turing V2 Architecture

## Your Role

You are a member of a 7-LLM review panel evaluating the **V2 (Imperator + LPPM)** architecture specification for **Turing**, building upon the approved V1 baseline.

## Review Package Contents

1. **synthesis.md** - The Turing V2 architecture specification to be reviewed
2. **ANCHOR_OVERVIEW.md** - System vision including V2 definition
3. **SYSTEM_DIAGRAM.md** - Visual architecture of all 13 MADs
4. **NON_FUNCTIONAL_REQUIREMENTS.md** - Performance, security, logging requirements
5. **MAD_ROSTER.md** - Canonical descriptions of all MADs
6. **V1_PHASE1_BASELINE.md** - Current baseline (Rogers + Dewey V1 complete)
7. **ARCHITECTURE_GUIDELINES.md** - Template structure and "Deployable" definition
8. **REVIEW_CRITERIA.md** - Complete evaluation criteria

## Your Task

Evaluate `synthesis.md` against the criteria in `REVIEW_CRITERIA.md`. Return a structured JSON review with your verdict and any objections.

## Review Criteria Summary (V2-Specific)

### 1. Version Compatibility
- **V2 = Imperator + LPPM** (Learned Prose-to-Process Mapper)
- LPPM should be present and properly integrated
- No V3 (DTR) or V4 (CET) components
- V1 capabilities must be preserved

### 2. LPPM Completeness
- LPPM training pipeline defined
- Learned workflow examples provided (3+)
- Routing logic between LPPM and Imperator clear
- Performance targets specified (< 200ms for learned patterns)
- Training data sources identified (Dewey archives, Imperator successes)

### 3. Dependencies (V2-Specific)
- **Dewey dependency expected:** LPPM training requires access to archived logs
- Rogers (communication)
- PostgreSQL (storage)
- Check that Dewey interface is defined (which tool/method for log retrieval)

### 4. Performance Targets
- V2 target: < 200 milliseconds median for learned patterns (per NON_FUNCTIONAL_REQUIREMENTS.md)
- Imperator fallback: Still < 5 seconds for novel requests
- LPPM accuracy: Should specify target (e.g., >95%)
- Coverage: Should specify expected coverage after learning period (e.g., 60-70% after 30 days)

### 5. Backward Compatibility
- All V1 tools must remain unchanged
- V1 workflows must still function
- Imperator must handle novel requests as in V1
- No breaking changes to ACL, secrets, or external interfaces

### 6. All Standard Criteria
- Completeness (template sections)
- Feasibility (implementable with standard ML libraries)
- Consistency (aligns with anchor documents)
- Clarity (deployable by engineer)
- JSON-RPC 2.0 logging compliance
- Data contracts explicit
- Error handling specific

## V2-Specific Critical Review Focus

### 1. LPPM Training Pipeline
Verify the document describes:
- Where training data comes from (Dewey's `#logs-turing-v1` archives)
- How Imperator successes are identified for training
- Model architecture (e.g., T5-small, BERT-base)
- Training frequency (incremental vs. full retrain)
- Validation metrics (accuracy, precision, recall)

### 2. LPPM vs. Imperator Routing
Verify clear logic for:
- When LPPM handles request (confidence > threshold)
- When Imperator handles request (novel pattern or low confidence)
- Confidence threshold value specified
- Feedback loop (Imperator successes → LPPM training)

### 3. Learned Workflow Examples
Verify at least 3 concrete examples of what LPPM learns:
- Example 1: Common ACL operation (e.g., "grant Hopper read access to X")
- Example 2: Secret rotation workflow
- Example 3: Batch operation or audit query

### 4. Performance Claims Realistic
Check that:
- 200ms target realistic for transformer inference
- Accuracy targets (>95%) achievable with training data volume
- Coverage estimates (60-70%) justified based on request patterns

### 5. Dewey Dependency Properly Declared
**CRITICAL:** Section 4.2 (Dependencies) must list Dewey with:
- Why needed (LPPM training data retrieval)
- Which Dewey tool/method used (`search_archives`, `retrieve_document`, etc.)
- Data contract for retrieved logs

### 6. Resource Requirements Updated
Verify deployment section reflects LPPM additions:
- Increased CPU (0.5+ cores for model inference)
- Increased RAM (512+ MB for model loading)
- Optional GPU mention for inference acceleration
- Python ML libraries (`transformers`, `torch`, `scikit-learn`)

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

- This is **Turing V2** (Imperator + LPPM), building on approved V1
- LPPM presence is **required** for V2, not a violation
- Dewey dependency is **expected** for LPPM training
- Performance targets are **stricter** for V2 (200ms for learned patterns)
- Your review contributes to a 6/7 (86%) quorum requirement for approval

---

**Begin your review now. Return only the JSON object.**
