# Turing V4 Architecture Synthesis Prompt

## Your Role
You are the lead developer creating the **Turing V4** architecture specification, building upon the approved V3 baseline.

## Context

**V3 Baseline (Approved):**
- Thinking Engine: DTR → LPPM → Imperator
- DTR handles learned deterministic patterns (ML classifier, <10µs target)
- LPPM handles learned prose-to-process mappings (<200ms)
- Imperator handles novel/complex reasoning (<5s)
- All 7 V1 tools preserved
- Dependencies: Rogers, Dewey (for DTR and LPPM training), PostgreSQL

**V4 Addition:** Context Engineering Transformer (CET)
- New component that sits **before** the Imperator
- Dynamically assembles optimal context for reasoning tasks
- Pulls from: recent conversation history, Dewey archives, external docs, real-time MAD data
- Overcomes fixed context window limitations
- Embodies "Intelligent Conversation and Context Management (ICCM)"
- Architecture becomes: **DTR → LPPM → CET → Imperator**

## Task

Create complete Turing V4 specification using the template from ARCHITECTURE_GUIDELINES.md. Build on the approved V3 specification (iteration 3), adding CET while preserving all V3/V2/V1 capabilities.

## V4-Specific Requirements

### 1. CET Component (Section 2.4)

**IMMUTABLE PRINCIPLE:** Per ANCHOR_OVERVIEW Core Principle #1, the core vision in version definitions is immutable. V4 CET must be implemented as specified in the anchor.

**Purpose:** Actively engineer optimal context for Imperator reasoning

**Implementation (per ANCHOR_OVERVIEW.md):**
- **"Sophisticated neural network"** that dynamically assembles context
- **NOT** a simple retrieval system - it's an ML component that learns what context is relevant
- Sits as a layer before Imperator in the pipeline

**Context Sources:**
1. Recent conversation history (last N messages)
2. Long-term archival memory (via Dewey search)
3. External documentation (if applicable for secrets management)
4. Real-time data from other MADs (e.g., current system state)

**CET Processing:**
- Input: Imperator-bound request + available context universe
- Process: ML-based relevance scoring and assembly
- Output: Optimized context package + original request → Imperator

**Training:**
- Learns from feedback: Which contexts led to successful Imperator outcomes?
- Data source: Dewey archives of Imperator successes/failures with context metadata
- Continuous improvement: Better context selection over time

### 2. Four-Stage Routing Logic (Section 2)

Update the routing flow:
1. Request → DTR first (learned deterministic patterns)
2. If no DTR match: Forward to LPPM (learned prose-to-process)
3. If LPPM confidence < 0.85: Forward to CET
4. CET assembles optimal context → forwards to Imperator
5. Imperator reasons with engineered context → executes

**Key point:** CET is **only** invoked for Imperator-bound requests (complex/novel tasks requiring deep reasoning)

### 3. CET Training Pipeline

**Data Collection:**
- Log all Imperator requests with: original request, context provided, outcome (success/failure), reasoning quality
- Store in Dewey with metadata about context sources used

**Training Approach:**
- Model type: Transformer-based relevance ranker or context selector
- Input features: Request embedding, candidate context chunks, historical relevance signals
- Output: Relevance scores for context candidates
- Training: Supervised learning from historical success/failure patterns

**Validation:**
- Measure Imperator success rate with CET-engineered context vs. baseline
- Target: 20-40% improvement in task completion (per NON_FUNCTIONAL_REQUIREMENTS)

### 4. Performance Targets (Update from V3)

- DTR-routed: <10µs (research target, unchanged from V3)
- LPPM-routed: <200ms (unchanged from V3)
- CET processing: **Small overhead** (per ANCHOR: "adds a small amount of processing time")
  - Target: <500ms for context assembly
- Imperator w/ CET: Still <5s total (includes CET overhead)

**Net benefit:** While CET adds time, it improves reasoning quality → fewer errors, less back-and-forth → faster problem resolution overall

**Expected distribution after 30 days:**
- DTR: 30-40%
- LPPM: 30-40%
- CET+Imperator: 20-30%

### 5. Dependencies (Update from V3)

**New dependency:**
- **Dewey** usage expands: Now required for DTR training, LPPM training, AND CET context retrieval
- CET will use Dewey's `search_archives` and potentially `retrieve_document` for long-term memory

**Full V4 dependencies:**
- Rogers (communication)
- Dewey (training data + context retrieval)
- PostgreSQL (storage)

### 6. Deployment Updates

**Container requirements:**
- CPU: May increase to 0.75-1.0 cores (CET context assembly)
- RAM: May increase to 768 MB - 1 GB (CET model loading)
- Libraries: Add transformer libraries (`transformers`, `sentence-transformers`, or similar)

**Configuration variables:**
Add:
- `TURING_CET_MODEL_PATH` - Path to CET model checkpoint
- `TURING_CET_CONTEXT_LIMIT` - Max tokens for assembled context
- `TURING_CET_SEARCH_DEPTH` - How far back in Dewey archives to search

### 7. Example Workflows

Include at least one scenario showing:
- Complex request requiring deep reasoning
- CET retrieves relevant historical context from Dewey
- Assembles optimized context package
- Imperator successfully reasons with improved context
- Demonstrates ICCM (Intelligent Conversation and Context Management)

**Example scenario ideas:**
- Secret rotation with historical failure context
- Complex ACL decision requiring past policy decisions
- Threat detection leveraging historical attack patterns

## Critical Requirements

✅ **All V3 capabilities preserved:** DTR, LPPM, Imperator all function identically
✅ **V4 = DTR + LPPM + CET + Imperator:** Explicitly state this in Overview
✅ **CET is ML-based neural network** (per ANCHOR immutable vision)
✅ **CET only processes Imperator-bound requests** (not invoked for DTR/LPPM paths)
✅ **Backward compatible:** All V1/V2/V3 tools unchanged
✅ **Complete schemas:** Include full data contracts
✅ **Logging examples:** Show CET log format with context metadata
✅ **ICCM principle:** Explain how CET embodies "context as engineered resource"
✅ **Performance justification:** Explain net benefit despite added overhead

## Template Sections (All Required)

1. Overview (Purpose, Role, New in V4)
2. Thinking Engine (2.1 Imperator, 2.2 LPPM, 2.3 DTR, 2.4 CET, 2.5 Routing Logic)
3. Action Engine (unchanged from V3)
4. Interfaces (4.1 Conversation Patterns, 4.2 Dependencies, 4.3 Data Contracts)
5. Data Management (Add CET training data + model storage)
6. Deployment (Update for CET requirements)
7. Testing Strategy (Add CET-specific tests)
8. Example Workflows (Add CET-enabled example)
9. Appendix (Glossary, Error Codes)

## Constraints

- Use ARCHITECTURE_GUIDELINES.md template structure
- Reference ANCHOR_OVERVIEW.md for V4 definition (IMMUTABLE)
- Align with MAD_ROSTER.md for Turing's role
- Follow NON_FUNCTIONAL_REQUIREMENTS.md for performance/logging
- Build directly on approved V3 (iteration 3) specification

## Deliverable

Complete `synthesis.md` file for Turing V4, ready for 7-LLM review panel evaluation.

**Focus:** Make CET addition clear, demonstrate ICCM principle, preserve all V3/V2/V1 functionality. This is the final, complete thinking engine architecture.
