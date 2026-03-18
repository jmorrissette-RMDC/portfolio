# Turing V4 Iteration 2 Revision Prompt

## Context

Iteration 1 received 4/7 ACCEPT (57%), failing to achieve 6/7 (86%) quorum. Three REJECT votes contained mix of valid and invalid objections.

## Valid Objections to Address

### 1. CET Training Pipeline Insufficient Detail
**Reviewers:** GPT-4o (critical), GPT-4-turbo (important), DeepSeek-R1 (critical)
**Issue:** Training pipeline described at high level without specific operational details
**Required additions:**
- Retraining schedule (frequency, triggers)
- Specific performance metrics for validation
- Data batch sizes and selection criteria
- Model deployment and rollback procedures

### 2. Dewey Dependency for CET Training Not Explicit
**Reviewers:** GPT-4-turbo (critical), DeepSeek-R1 (critical)
**Issue:** Dependencies list Dewey for context retrieval but don't explicitly state Dewey's role in CET training data provisioning
**Required fix:**
- Update Section 4.2 Dependencies to explicitly state: "Dewey: Required for DTR training, LPPM training, AND CET training data pipeline"
- Clarify how Dewey provides training data (logged Imperator outcomes)

### 3. CET Model Storage and Versioning Undefined
**Reviewers:** GPT-4o (important), DeepSeek-R1 (minor)
**Issue:** Deployment mentions `TURING_CET_MODEL_PATH` but lacks versioning strategy, rollback mechanisms, validation procedures
**Required additions:**
- Semantic versioning scheme for CET models
- A/B testing deployment approach
- Model validation criteria before production deployment
- Rollback procedures and archive retention policy

### 4. CET Environment Variables Unclear
**Reviewers:** GPT-4o (important)
**Issue:** Environment variables listed without explaining their operational effects and interdependencies
**Required additions:**
- Detailed explanation of each CET environment variable
- How they interact with existing LPPM/DTR configuration
- Example values and their impact

### 5. Fallback Mechanisms for CET Failures
**Reviewers:** GPT-4o (important)
**Issue:** No description of what happens if CET fails to assemble adequate context
**Required addition:**
- Explicit fallback logic: CET failure → Imperator receives request with baseline context (recent conversation history only)
- Logging of CET failures for improvement

### 6. RAM Allocation Potentially Insufficient
**Reviewers:** DeepSeek-R1 (important)
**Issue:** Allocated 768MB-1GB might be too low for transformer models (base BERT requires 1.5-3GB)
**Required action:**
- Review RAM allocation
- If justified (using smaller models), explain the choice
- If insufficient, increase to 2-3GB with justification

## Invalid/Questionable Objections (Do Not Address)

### GPT-4-turbo: "Transformer architecture not explicit"
**Status:** FACTUAL ERROR
**Evidence:** synthesis.md Section 2.4 line 80 explicitly states "sophisticated neural network, specifically a transformer-based model"
**Action:** IGNORE - objection based on misreading

### DeepSeek-R1: "CET doesn't learn from Imperator outcomes"
**Status:** CONTRADICTORY
**Evidence:** DeepSeek's own thinking (lines 27-30) acknowledges "Training Pipeline: Described with a feedback loop: logs to Dewey, retrains periodically using success/failure outcomes"
**Action:** IGNORE - objection contradicts reviewer's own analysis

### DeepSeek-R1: "Ambiguous Imperator-bound criteria"
**Status:** CONTRADICTORY
**Evidence:** DeepSeek's thinking (line 34) acknowledges "CET is only invoked for Imperator-bound requests (i.e., when LPPM confidence is too low)"
**Action:** IGNORE - routing is clear (LPPM confidence < 0.85 → CET → Imperator)

### DeepSeek-R1: "DTR learning mechanism missing"
**Status:** QUESTIONABLE
**Reason:** V4 is delta document building on approved V3 baseline which contains DTR training pipeline. "Reference, Don't Repeat" strategy applies.
**Action:** IGNORE - V3 baseline already approved with DTR learning

## Revision Instructions

Update iteration 1 synthesis.md to address the 6 valid objections above. Maintain all existing content, add clarifications and details where needed.

### Section 2.4 Context Engineering Transformer (CET) - Expand Training Pipeline
Add subsection "CET Training Pipeline Details":
```markdown
#### CET Training Pipeline Details

**Data Collection:**
- All Imperator requests logged to Dewey with: original request, CET-assembled context, reasoning outcome, success/failure indicator
- Success criteria: Task completed without errors within 3 conversation turns
- Logged to Dewey channel: `#turing-cet-training`

**Training Schedule:**
- Initial training: Manual, using historical Imperator data from Dewey archives (6 months lookback)
- Retraining: Automated weekly (every Sunday 02:00 UTC)
- Triggered retraining: When success rate drops below 70% threshold (checked daily)

**Training Procedure:**
- Batch size: 1000 request-context-outcome triplets
- Validation split: 80% train, 20% validation
- Model type: Transformer-based relevance ranker (e.g., sentence-transformers)
- Training objective: Maximize relevance scores for contexts that led to successful Imperator outcomes
- Validation metrics:
  - Context relevance accuracy >85%
  - Imperator success rate improvement: 20-40% vs. baseline (no CET)

**Model Deployment:**
- Semantic versioning: `vMAJOR.MINOR.PATCH` (e.g., v1.0.0)
- A/B testing: New model deployed to 10% traffic for 24 hours
- Promotion criteria: Success rate ≥ current model, no critical errors
- Rollback: Automatic if success rate drops >5% or critical error rate >1%
- Archive retention: Previous 3 model versions retained for 30 days
```

### Section 4.2 Dependencies - Clarify Dewey Role
Update Dewey dependency entry:
```markdown
*   **Dewey:** Turing's conversation archive and training data provider. Required for:
    - **DTR Training:** Provides archived deterministic request patterns for ML classifier training
    - **LPPM Training:** Provides successful conversation workflows for prose-to-process mapping training
    - **CET Context Retrieval:** Real-time search of conversation archives for relevant historical context
    - **CET Training Data:** Provides logged Imperator requests with outcomes for CET model training
    Uses Dewey's `search_archives`, `retrieve_conversation`, and `query_logs` tools.
```

### Section 5. Data Management - Add CET Model Versioning
Add subsection "CET Model Storage":
```markdown
#### CET Model Storage

**Model Repository:**
- Location: `/models/turing/cet/` (mounted volume)
- Structure:
  - `/models/turing/cet/production/model.pt` - Current production model
  - `/models/turing/cet/production/metadata.json` - Version, training date, metrics
  - `/models/turing/cet/candidate/model.pt` - A/B test candidate
  - `/models/turing/cet/archive/v{version}/` - Historical models (30-day retention)

**Versioning Scheme:**
- Semantic versioning: `vMAJOR.MINOR.PATCH`
  - MAJOR: Architecture changes (e.g., switch from BERT to GPT)
  - MINOR: Training data expansion or hyperparameter tuning
  - PATCH: Bug fixes or small retraining

**Validation Before Deployment:**
1. Offline evaluation: Replay last 1000 Imperator requests with new model
2. Success rate threshold: Must meet or exceed current production model
3. A/B testing: 10% traffic for 24 hours, monitor success rate and latency
4. Promotion: If validation passes, candidate → production
```

### Section 2.5 Routing Logic - Add CET Fallback
Add to Stage 3 (CET) description:
```markdown
**CET Failure Handling:**
- If CET fails to assemble context (Dewey unavailable, timeout, error): Forward to Imperator with baseline context (last 10 messages from conversation history)
- Log failure to Dewey for CET improvement
- Success rate with fallback context tracked separately for CET quality monitoring
```

### Section 6. Deployment - Expand Environment Variables
Update CET configuration variables with detailed explanations:
```markdown
**CET Configuration:**
- `TURING_CET_MODEL_PATH` (required): Absolute path to CET model checkpoint file (e.g., `/models/turing/cet/production/model.pt`). Loaded at startup. Model changes require Turing restart.
- `TURING_CET_CONTEXT_LIMIT` (default: 8000): Maximum tokens for CET-assembled context. Must be less than Imperator's context window (32,000 tokens for Claude 3.5 Sonnet). Higher values improve context quality but increase Imperator latency.
- `TURING_CET_SEARCH_DEPTH` (default: 90): How many days back in Dewey archives to search for relevant context. Higher values improve context breadth but increase CET processing time. Range: 7-365 days.
- `TURING_CET_RELEVANCE_THRESHOLD` (default: 0.70): Minimum relevance score (0.0-1.0) for context chunks to be included. Higher values produce more focused context, lower values cast wider net. Tuned during CET training validation.

**Interactions with existing configuration:**
- CET model path independent of LPPM/DTR models
- `TURING_CET_CONTEXT_LIMIT` must leave room for request + response within Imperator's total context window
- `TURING_CET_SEARCH_DEPTH` interacts with `DEWEY_SEARCH_MAX_RESULTS` - CET may retrieve up to Dewey's limit
```

### Section 6. Deployment - Review RAM Allocation
Update container requirements with justification:
```markdown
**Container Requirements:**
- **CPU:** 0.75 - 1.0 cores (0.5 for Imperator, 0.25 for CET context assembly, 0.25 for DTR/LPPM)
- **RAM:** 1.5 - 2 GB total
  - Imperator LLM client: 256 MB
  - LPPM model: 256 MB (scikit-learn random forest)
  - DTR model: 128 MB (lightweight classifier)
  - **CET model: 768 MB - 1.2 GB** (sentence-transformers base model)
    - Justification: Using `all-MiniLM-L6-v2` (22M parameters, ~90MB model file, ~700MB runtime with embeddings cache) or `all-mpnet-base-v2` (110M parameters, ~420MB model file, ~1GB runtime)
    - Research context allows testing smaller models first, scaling to BERT-large (335M parameters, ~1.3GB) if needed
  - Context buffers: 256 MB
- **Disk:** 2 GB (1.5 GB for CET models + archives)
```

## Validation

After revision, verify:
- ✅ All 6 valid objections addressed with specific details
- ✅ No changes to V3/V2/V1 preserved capabilities
- ✅ No violations of immutable ANCHOR_OVERVIEW principles
- ✅ Document remains "Deployable" (engineer can implement from specification)
- ✅ All template sections complete

## Deliverable

Complete `synthesis.md` for iteration 2, ready for second 7-LLM review cycle.
