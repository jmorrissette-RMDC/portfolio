# Review Instructions for Dewey V1 Architecture

## Your Role

You are a member of a 7-LLM review panel evaluating the **V1 (Conversational)** architecture specification for **Dewey**, the Data Lake Manager and Librarian MAD.

## Review Package Contents

1. **synthesis.md** - The Dewey V1 architecture specification to be reviewed
2. **ANCHOR_OVERVIEW.md** - System vision including V1 definition
3. **SYSTEM_DIAGRAM.md** - Visual architecture of all 13 MADs
4. **NON_FUNCTIONAL_REQUIREMENTS.md** - Performance, security, logging requirements
5. **MAD_ROSTER.md** - Canonical description of Dewey's role
6. **V1_PHASE1_BASELINE.md** - Existing baseline (Rogers + Dewey already deployed in basic form)
7. **ARCHITECTURE_GUIDELINES.md** - Template structure and "Deployable" definition
8. **REVIEW_CRITERIA.md** - Complete evaluation criteria

## Your Task

Evaluate `synthesis.md` against the criteria in `REVIEW_CRITERIA.md`. Return a structured JSON review with your verdict and any objections.

## Review Criteria Summary (V1-Specific)

### 1. Version Compatibility
- **V1 = Conversational = Imperator only** (single-stage reasoning, no LPPM/DTR/CET)
- Imperator handles all intelligent decisions (archival readiness, search interpretation, conflict resolution)
- No training components should be present in V1
- This establishes the baseline for future V2/V3/V4 optimizations

### 2. Thinking Engine Completeness
- Imperator configured with appropriate LLM (Claude 3.5 Sonnet via Fiedler)
- System prompt defines Dewey's role and responsibilities
- Clear decision-making responsibilities (when to archive, how to search, conflict resolution)
- Temperature setting appropriate (0.0 for deterministic archival decisions)
- Context window sufficient for conversation analysis

### 3. Action Engine (Tool Set)
Must define complete set of archival/retrieval tools:
- `archive_conversation` - Archive conversation from Rogers to data lake
- `search_archives` - Search archived conversations
- `retrieve_conversation` - Retrieve specific archived conversation
- `index_data` - Create/update search indices
- `get_archive_stats` - Get statistics about archived data
- `verify_archive_integrity` - Check integrity of archived data
- `optimize_storage` - Optimize data lake storage

Each tool must have:
- Input parameters with types
- Output schema
- Side effects clearly stated
- Error conditions defined

### 4. Conversation Patterns
**Critical - Archivist Pattern:**
- Dewey monitors Rogers for conversation metadata
- Triggers archival when conversation is inactive (>24 hours) or completed
- Imperator analyzes conversation for archival readiness
- Archives to data lake via `archive_conversation` tool
- Notifies Rogers that conversation can be purged
- Rogers removes from hot storage

**Search Pattern:**
- MAD requests search from Dewey
- Imperator interprets query and context
- Executes `search_archives` with optimal parameters
- Returns results to requesting MAD

**Retrieval Pattern:**
- MAD requests specific conversation
- `retrieve_conversation` tool execution
- Full conversation returned

### 5. Dependencies
**Expected dependencies:**
- **Rogers:** Source of conversations, communication bus (uses `get_conversation_history`, `send_message`)
- **PostgreSQL:** Metadata storage (indices, archive locations, statistics)
- **NAS (Winnipesaukee):** Long-term data lake storage
- **Fiedler:** LLM access for Imperator reasoning

No dependencies on other MADs for V1.

### 6. Data Contracts
Must explicitly define schemas for:
- Archive Entry (conversation_id, archived_at, archive_location, participants, channel, size, checksum, etc.)
- Search Result (conversation_id, relevance_score, snippet, metadata)
- Tool inputs and outputs for all 7 tools

### 7. Performance Targets (V1 Baseline)
- Archive throughput: Target specified (e.g., 100 conversations/hour)
- Search latency: Targets for full-text and semantic search
- Retrieval latency: Single conversation fetch time
- Storage efficiency: Overhead for indices/metadata
- Availability: As infrastructure MAD (e.g., 99.5%)

These are V1 baselines - future versions will optimize.

### 8. Data Management
- PostgreSQL schema defined (metadata tables, indices)
- NAS file structure specified (e.g., `/mnt/winnipesaukee/archives/{year}/{month}/{conversation_id}.json`)
- Index management approach described
- Integrity verification mechanism defined

### 9. Deployment
- Container requirements (CPU, RAM, disk, network)
- Configuration variables (archive threshold, data lake path, index refresh interval, LLM model)
- Startup sequence
- Dependencies on external services (Rogers, PostgreSQL, NAS, Fiedler)

### 10. Standard Criteria
- **Completeness:** All template sections filled
- **Feasibility:** Implementable with current technology
- **Consistency:** Aligns with anchor documents (ANCHOR_OVERVIEW, MAD_ROSTER, V1_PHASE1_BASELINE)
- **Clarity:** "Deployable" - engineer can implement from this spec
- **Logging:** JSON-RPC 2.0 format with all required fields
- **Error Handling:** Specific error codes and handling strategies
- **Testing Strategy:** Unit, integration, performance tests defined

## V1-Specific Critical Review Focus

### 1. Imperator-Only Architecture
Verify:
- NO LPPM, DTR, or CET components (these are V2/V3/V4 additions)
- Imperator is the sole thinking component
- All complex decisions routed through Imperator reasoning
- Performance targets reflect single-stage reasoning (no routing logic needed)

### 2. Archivist Pattern Implementation
Verify:
- Clear monitoring mechanism (how Dewey watches Rogers)
- Archival trigger conditions specified (inactivity threshold, completion status)
- Imperator's role in archival decisions documented
- Tool execution flow clear (retrieve → analyze → archive → notify)
- Rogers cleanup notification mechanism defined

### 3. Data Lake Architecture
Verify:
- NAS as primary storage clearly stated
- File structure logical and scalable (date-based partitioning recommended)
- PostgreSQL for metadata only (not full conversation storage)
- Separation of concerns: data in NAS, metadata in PostgreSQL

### 4. Search Capabilities
Verify:
- Search tool supports multiple query types (keyword, semantic, metadata filters)
- Indexing strategy defined (what indices exist, how maintained)
- Performance targets realistic for V1 (no ML-based retrieval yet)
- Results include relevance scores for ranking

### 5. Integration with Existing Baseline
Note: Per V1_PHASE1_BASELINE.md, Rogers and Dewey are already deployed in basic form. The V1 specification should:
- Build on existing deployment
- Preserve existing functionality
- Define complete Imperator integration
- Specify tool set fully

## Output Format

Return a JSON object with this exact structure:

```json
{
  "reviewer": "<your-model-name>",
  "verdict": "ACCEPT or REJECT",
  "objections": [
    {
      "mad_name": "Dewey",
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

- This is **Dewey V1** (Conversational baseline), not V2/V3/V4
- **V1 = Imperator only** - no LPPM/DTR/CET should be present
- **IMMUTABLE PRINCIPLE:** Core vision from ANCHOR_OVERVIEW defines requirements (per Core Principle #1)
- Dewey's role as "Data Lake Manager and Librarian" must be fulfilled
- Archivist pattern is critical for ecosystem functionality
- Performance targets are V1 baselines for measuring future improvements
- Dependencies must be correct (Rogers, PostgreSQL, NAS, Fiedler)
- Your review contributes to a 6/7 (86%) quorum requirement for approval

---

**Begin your review now. Return only the JSON object.**
