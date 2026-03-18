# Turing V2 Architecture Synthesis Prompt

## Context

You are creating the **V2 (Imperator + LPPM)** architecture specification for **Turing**, building upon the approved V1 baseline.

## Your Task

Evolve the Turing V1 specification to V2 by adding the **Learned Prose-to-Process Mapper (LPPM)** component to the Thinking Engine. Follow the Standardized MAD Architecture Template and maintain all V1 capabilities while adding V2 enhancements.

## Input Documents

You will receive:
1. **Turing V1 approved specification** - The baseline to build upon
2. **ANCHOR_OVERVIEW.md** - V2 definition and LPPM requirements
3. All other anchor package documents for consistency checking

## V2 Requirements (from ANCHOR_OVERVIEW.md)

**V2 = Imperator + LPPM (Learned Prose-to-Process Mapper)**

### LPPM Purpose
Convert natural language task descriptions into executable process workflows that can be cached and reused, dramatically speeding up repeated operations.

### V2 Capabilities for Turing
1. **Pattern Recognition:** LPPM learns common secrets management workflows (e.g., "rotate API key", "grant Hopper access to GitHub PAT", "audit secret access for prod environment")
2. **Workflow Caching:** Frequently executed workflows cached as process templates
3. **Performance Target:** < 200 milliseconds for learned patterns (vs. < 5 seconds for Imperator)
4. **Imperator Fallback:** Novel requests still routed to Imperator, then learned by LPPM for future use

### LPPM Training Data Sources
- Historical conversation logs from `#logs-turing-v1` (via Dewey)
- Successful Imperator reasoning workflows from V1
- Common ACL management patterns (grant/revoke access)
- Secret rotation workflows
- Multi-secret batch operations

## Key Changes for V2

### 1. Section 1 (Overview)
Update "New in this Version" to describe V2 additions:
- LPPM integration for learned workflow acceleration
- Performance improvements for common patterns
- Maintain backward compatibility with V1

### 2. Section 2 (Thinking Engine) - PRIMARY FOCUS
**Add new subsection 2.2: LPPM Configuration**

Structure:
```
## 2. Thinking Engine

### 2.1 Imperator Configuration (V1 Baseline)
[Keep existing V1 content unchanged]

### 2.2 LPPM Configuration (V2 Addition)
**Purpose:** Accelerate repeated secrets management workflows through learned pattern matching.

**Architecture:**
- Small transformer model (e.g., T5-small, BERT-base)
- Trained on Turing's historical successful workflows
- Input: Natural language request + context (requesting MAD, operation type)
- Output: Executable workflow steps OR confidence < threshold → route to Imperator

**Training Pipeline:**
1. Dewey retrieves `#logs-turing-v1` conversations with successful outcomes
2. Extract request-response pairs where Imperator succeeded
3. Fine-tune LPPM on these pairs to map prose → workflow
4. Validate on held-out test set (>90% accuracy required)
5. Deploy to production, continue learning from new Imperator successes

**Learned Workflow Examples:**
[Provide 3 concrete examples of what LPPM learns]

**Routing Logic:**
[Explain how requests are routed between LPPM and Imperator]

**Performance Targets:**
- LPPM inference: < 200ms (90th percentile)
- Accuracy: > 95% for learned patterns
- Coverage: 60-70% of requests after 30 days of learning
```

### 3. Section 3 (Action Engine)
Add note that tools remain unchanged - LPPM uses same MCP tools as Imperator.

### 4. Section 5 (Data Management)
Add new subsection: **LPPM Training Data Storage**
- Where training data stored (Dewey archives + local cache)
- Model checkpoint storage location
- Retraining frequency (weekly incremental, monthly full retrain)

### 5. Section 6 (Deployment)
Update resource requirements:
- CPU: 0.5 cores (increased from 0.25 for LPPM inference)
- RAM: 512 MB (increased from 256 MB for model loading)
- GPU: Optional (improves LPPM inference 3-5x)
- Add Python libraries: `transformers`, `torch`, `scikit-learn`

Add environment variables:
- `TURING_LPPM_MODEL_PATH`: Path to LPPM checkpoint
- `TURING_LPPM_CONFIDENCE_THRESHOLD`: Minimum confidence to use LPPM (default: 0.85)

### 6. Section 7 (Testing Strategy)
Add LPPM-specific tests:
- Model accuracy validation
- Performance benchmarks (inference time)
- Fallback to Imperator when confidence low

### 7. Section 8 (Example Workflows)
Add one new workflow: **Scenario 4: LPPM Accelerated Workflow**
- Show Grace requesting "grant Hopper read access to prod_db_password"
- LPPM recognizes pattern, generates workflow in <200ms
- Executes grant_access tool directly
- Logs success to #logs-turing-v1 for future training

---

## Quality Standards

- **Maintain V1 strengths:** All V1 content preserved, tools unchanged, same dependencies
- **Clear V2 additions:** Obvious what's new vs. baseline
- **Realistic LPPM:** Don't over-promise - acknowledge learning curve, accuracy limits
- **Performance concrete:** Specific targets (200ms, 95% accuracy, 60-70% coverage)
- **Training pipeline detailed:** How LPPM learns from Imperator
- **No breaking changes:** V2 must be backward compatible with V1

---

## Validation Checklist

Before submitting:
- [ ] V1 specification fully incorporated (tools, ACLs, all sections)
- [ ] LPPM subsection added to section 2
- [ ] LPPM training pipeline explained
- [ ] 3+ learned workflow examples provided
- [ ] Routing logic (LPPM vs. Imperator) clear
- [ ] Performance targets specific (200ms, 95%, 60-70%)
- [ ] Resource requirements updated (0.5 cores, 512 MB)
- [ ] LPPM-specific test scenario added
- [ ] Training data storage documented
- [ ] No V3/V4 features (no DTR or CET)

---

## Begin Synthesis

Create the complete Turing V2 architecture document now, building upon V1 and adding LPPM capabilities per ANCHOR_OVERVIEW.md V2 definition.
