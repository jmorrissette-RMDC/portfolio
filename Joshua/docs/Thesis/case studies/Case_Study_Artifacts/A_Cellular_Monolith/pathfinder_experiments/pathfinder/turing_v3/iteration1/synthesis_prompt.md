# Turing V3 Architecture Synthesis Prompt

## Your Role
You are the lead developer creating the **Turing V3** architecture specification, building upon the approved V2 baseline.

## Context

**V2 Baseline (Approved):**
- Thinking Engine: LPPM → Imperator
- LPPM handles learned patterns (<200ms), Imperator handles novel requests (<5s)
- All 7 V1 tools preserved
- Dependencies: Rogers, Dewey (for training), PostgreSQL

**V3 Addition:** Decision Tree Router (DTR)
- New first-stage component before LPPM
- Deterministic rule-based routing for ultra-fast common patterns
- Target: <50ms for DTR-routable requests
- Architecture becomes: **DTR → LPPM → Imperator**

## Task

Create complete Turing V3 specification using the template from ARCHITECTURE_GUIDELINES.md. Build on the approved V2 specification (iteration 3), adding DTR while preserving all V2 capabilities.

## V3-Specific Requirements

### 1. DTR Component (Section 2.3)

**Purpose:** Ultra-fast routing for deterministic, high-frequency patterns

**Implementation:**
- Rule-based decision tree (not ML)
- Compiled from Turing-specific routing rules
- Examples of DTR-routable patterns:
  - "get secret X" → `get_secret(name='X')`
  - "list secrets" → `list_secrets()`
  - "grant [MAD] [permission] access to [secret]" → `grant_access(...)`

**Performance:**
- Target: <50ms (90th percentile)
- Expected coverage: 30-40% of requests after tuning
- Zero training required (rule-based)

**Rule Structure:** Define the decision tree rule format (e.g., regex patterns, keyword matching, parameter extraction)

### 2. Three-Stage Routing Logic (Section 2)

Update the routing flow:
1. Request → DTR first
2. If DTR matches rule with confidence: Execute action
3. If no DTR match: Forward to LPPM
4. If LPPM confidence < threshold: Forward to Imperator

**Routing Decision Criteria:**
- DTR: Exact pattern match required
- LPPM: Confidence ≥ 0.85
- Imperator: Fallback for all others

### 3. DTR Rule Management

**Where rules come from:**
- Initial ruleset: Hand-authored for common operations
- Future expansion: Analysis of high-frequency LPPM patterns (manual curation, not automatic)

**Rule versioning:** How rules are updated/deployed

**Monitoring:** Track DTR hit rate, false positives

### 4. Performance Targets (Update from V2)

- DTR-routed: <50ms (90th percentile)
- LPPM-routed: <200ms (unchanged from V2)
- Imperator fallback: <5s (unchanged from V1)

**Expected distribution after 30 days:**
- DTR: 30-40%
- LPPM: 30-40%
- Imperator: 20-30%

### 5. Dependencies (Unchanged from V2)

DTR doesn't require new dependencies:
- Rogers (communication)
- Dewey (LPPM training only)
- PostgreSQL (storage)

### 6. Deployment Updates

**Container requirements:**
- CPU: 0.5 cores (unchanged - DTR is lightweight)
- RAM: 512 MB (unchanged)
- Libraries: Add `pyyaml` or similar for rule configuration

**Configuration variables:**
Add `TURING_DTR_RULES_PATH` environment variable for rule file location

### 7. Example Workflows

Include at least one scenario showing:
- Request matches DTR rule
- Executed in <50ms
- Logged with `source: "dtr"`

## Critical Requirements

✅ **All V2 capabilities preserved:** LPPM and Imperator still function identically
✅ **V3 = DTR + LPPM + Imperator:** Explicitly state this in Overview
✅ **No V4 components:** No CET (Context Engineering Transformer) mentioned
✅ **Backward compatible:** All V1/V2 tools unchanged
✅ **Complete schemas:** Include full data contracts even if "unchanged"
✅ **Logging examples:** Show DTR log format with JSON-RPC 2.0
✅ **Performance justification:** Explain why 50ms is realistic for decision tree lookup
✅ **Clear routing diagram:** Consider adding a simple flowchart in text/mermaid

## Template Sections (All Required)

1. Overview (Purpose, Role, New in V3)
2. Thinking Engine (2.1 Imperator, 2.2 LPPM, 2.3 DTR, 2.4 Routing Logic)
3. Action Engine (unchanged from V2)
4. Interfaces (4.1 Conversation Patterns, 4.2 Dependencies, 4.3 Data Contracts)
5. Data Management (Add DTR rule storage)
6. Deployment (Update for DTR config)
7. Testing Strategy (Add DTR-specific tests)
8. Example Workflows (Add DTR example)
9. Appendix (Glossary, Error Codes)

## Constraints

- Use ARCHITECTURE_GUIDELINES.md template structure
- Reference ANCHOR_OVERVIEW.md for V3 definition
- Align with MAD_ROSTER.md for Turing's role
- Follow NON_FUNCTIONAL_REQUIREMENTS.md for performance/logging
- Build directly on approved V2 (iteration 3) specification

## Deliverable

Complete `synthesis.md` file for Turing V3, ready for 7-LLM review panel evaluation.

**Focus:** Make DTR addition clear, concrete, and implementable while preserving all V2/V1 functionality.
