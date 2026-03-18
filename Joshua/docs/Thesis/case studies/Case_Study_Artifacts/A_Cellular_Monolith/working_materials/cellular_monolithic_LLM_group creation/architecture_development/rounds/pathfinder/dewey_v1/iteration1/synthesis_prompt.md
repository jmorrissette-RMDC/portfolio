# Dewey V1 Architecture Synthesis Prompt

## Your Role
You are the lead developer creating the **Dewey V1** architecture specification (Conversational baseline).

## Context

**MAD Role:** Dewey - Data Lake Manager / The Librarian
- Long-term memory and archival system for the Joshua ecosystem
- Monitors Conversation Bus for inactive/completed conversations
- Archives conversations from Rogers' hot storage to data lake (Winnipesaukee)
- Provides search and retrieval interface for archived data
- Acts as DBA for its own schemas

**V1 Definition (from ANCHOR_OVERVIEW):**
- Conversational baseline with Imperator (LLM) integration
- Uses reasoning to handle complex archival decisions
- Establishes foundational tool set and conversation patterns

## Task

Create complete Dewey V1 specification using the template from ARCHITECTURE_GUIDELINES.md.

## Dewey-Specific Requirements

### 1. Thinking Engine (Imperator Only - V1)

**Purpose:** Intelligent archival and retrieval decisions

**Imperator Configuration:**
- LLM: Claude 3.5 Sonnet (via Fiedler)
- System Prompt: "You are Dewey, the data lake manager and librarian for the Joshua ecosystem. Your purpose is to make intelligent decisions about archiving conversations, indexing data, and retrieving relevant information from the data lake."
- Context Window: Sufficient for conversation analysis (up to 200k tokens)
- Temperature: 0.0 (deterministic for archival decisions)

**Imperator Responsibilities:**
- Decide when conversations are ready for archival (inactive for >N hours, completed status)
- Determine optimal indexing strategy for archived data
- Handle complex search queries requiring semantic understanding
- Resolve conflicts (e.g., archival errors, corrupted data)
- Make database administration decisions

### 2. Action Engine (MCP Server + Tools)

**Core Tools:**
1. `archive_conversation` - Archive conversation from Rogers to data lake
   - Inputs: conversation_id, metadata
   - Outputs: archive_location, archive_timestamp
   - Effects: Conversation moved to data lake, Rogers notified for cleanup

2. `search_archives` - Search archived conversations
   - Inputs: query (text), filters (date_range, participants, channel), limit
   - Outputs: List of matching conversations with relevance scores
   - Effects: None (read-only)

3. `retrieve_conversation` - Retrieve specific archived conversation
   - Inputs: conversation_id or archive_location
   - Outputs: Full conversation with messages and metadata
   - Effects: None (read-only)

4. `index_data` - Create or update search indices
   - Inputs: index_name, data_source, index_type (full_text, semantic, metadata)
   - Outputs: index_status
   - Effects: New/updated index for faster search

5. `get_archive_stats` - Get statistics about archived data
   - Inputs: stat_type (storage_used, conversation_count, date_range_stats)
   - Outputs: Statistics object
   - Effects: None (read-only)

6. `verify_archive_integrity` - Check integrity of archived data
   - Inputs: conversation_id or date_range
   - Outputs: integrity_report (status, errors_found, corrupted_entries)
   - Effects: Logs integrity issues

7. `optimize_storage` - Optimize data lake storage
   - Inputs: optimization_strategy (compress, deduplicate, reorganize)
   - Outputs: optimization_report
   - Effects: Data lake reorganization for efficiency

### 3. Conversation Patterns

**Archivist Pattern (Core V1 Pattern):**
1. Dewey monitors Rogers for conversation metadata (listens to `#conversation-metadata` channel)
2. When conversation becomes inactive (>24 hours) or marked completed:
   - Dewey requests full conversation from Rogers (`get_conversation_history`)
   - Imperator analyzes conversation for archival readiness
   - If ready: `archive_conversation` tool → data lake
   - Dewey notifies Rogers: "Conversation {id} archived, safe to purge"
3. Rogers removes conversation from hot storage

**Search Pattern:**
1. MAD sends search request to Dewey conversation
2. Dewey Imperator interprets query and context
3. `search_archives` tool with optimal parameters
4. Results returned to requesting MAD

**Retrieval Pattern:**
1. MAD requests specific conversation from Dewey
2. `retrieve_conversation` tool
3. Full conversation returned

### 4. Dependencies

**Required:**
- **Rogers:** Source of conversations to archive, communication bus
  - Uses: `get_conversation_history`, `send_message`
- **PostgreSQL:** Metadata storage (indices, archive locations, statistics)
- **NAS (Winnipesaukee Data Lake):** Long-term storage for archived conversations
  - File structure: `/mnt/winnipesaukee/archives/{year}/{month}/{conversation_id}.json`
- **Fiedler:** LLM access for Imperator reasoning

**Optional:** None for V1

### 5. Data Contracts

**Archive Entry Schema:**
```json
{
  "conversation_id": "uuid",
  "archived_at": "ISO-8601 timestamp",
  "archive_location": "/path/to/file",
  "participants": ["mad_name1", "mad_name2"],
  "channel": "#channel-name",
  "message_count": "integer",
  "start_time": "ISO-8601",
  "end_time": "ISO-8601",
  "status": "completed|archived",
  "size_bytes": "integer",
  "checksum": "sha256 hash"
}
```

**Search Result Schema:**
```json
{
  "conversation_id": "uuid",
  "relevance_score": "float 0-1",
  "snippet": "preview text",
  "metadata": {Archive Entry Schema}
}
```

### 6. Performance Targets

- **Archive throughput:** 100 conversations/hour (sustained)
- **Search latency:** <2s for full-text search, <5s for semantic search (V1 baseline)
- **Retrieval latency:** <500ms for single conversation
- **Storage efficiency:** <10% overhead for indices and metadata
- **Availability:** 99.5% (infrastructure MAD)

### 7. Deployment

**Container Requirements:**
- **CPU:** 0.5 cores (0.25 for Imperator, 0.25 for archival operations)
- **RAM:** 512 MB - 1 GB (Imperator client + index caches)
- **Disk:** 100 GB local (indices and metadata), unlimited NAS (data lake)
- **Network:** Access to Rogers, PostgreSQL, NAS, Fiedler

**Configuration:**
- `DEWEY_ARCHIVE_THRESHOLD_HOURS` - Hours of inactivity before archival (default: 24)
- `DEWEY_DATA_LAKE_PATH` - Path to NAS data lake (default: /mnt/winnipesaukee/archives)
- `DEWEY_INDEX_REFRESH_INTERVAL` - Seconds between index refreshes (default: 3600)
- `DEWEY_IMPERATOR_LLM` - LLM model for Imperator (default: claude-3-5-sonnet-20241022)

### 8. Example Workflows

**Example 1: Automatic Archival**
- User completes task with Turing
- Rogers marks conversation as completed
- Dewey Imperator analyzes: "Conversation completed 2 hours ago, 45 messages, participants: Grace, Turing. Ready for archival."
- Dewey executes `archive_conversation`
- Rogers receives notification, purges from hot storage

**Example 2: Historical Search**
- Grace asks: "Show me conversations about the user authentication system from last month"
- Dewey Imperator interprets query: date_range filter (last month), keyword filter (authentication)
- Executes `search_archives` with optimized parameters
- Returns top 10 relevant conversations to Grace

## Critical Requirements

✅ **V1 = Imperator only:** Single-stage reasoning, no LPPM/DTR/CET
✅ **Complete tool set:** All 7 archival/retrieval tools defined with full schemas
✅ **Archivist pattern:** Core workflow documented
✅ **Data contracts:** Explicit schemas for all data structures
✅ **Logging:** JSON-RPC 2.0 format with all required fields
✅ **Performance targets:** Documented as V1 baseline
✅ **Dependencies:** Rogers, PostgreSQL, NAS, Fiedler
✅ **Deployable:** Engineer can implement from this specification

## Template Sections (All Required)

1. Overview (Purpose, Role, Responsibilities)
2. Thinking Engine (Imperator configuration and responsibilities)
3. Action Engine (MCP Server + 7 tools with full specifications)
4. Interfaces (Conversation Patterns, Dependencies, Data Contracts)
5. Data Management (PostgreSQL schemas, NAS structure, index management)
6. Deployment (Container requirements, configuration, startup sequence)
7. Testing Strategy (Unit, integration, performance tests)
8. Example Workflows (2-3 scenarios demonstrating V1 capabilities)
9. Appendix (Glossary, Error Codes)

## Constraints

- Use ARCHITECTURE_GUIDELINES.md template structure
- Reference ANCHOR_OVERVIEW.md for MAD vision
- Align with MAD_ROSTER.md for Dewey's role
- Follow NON_FUNCTIONAL_REQUIREMENTS.md for logging/performance
- Integrate with V1_PHASE1_BASELINE.md (Rogers + Dewey already deployed)

## Deliverable

Complete `synthesis.md` file for Dewey V1, ready for 7-LLM review panel evaluation.

**Focus:** Establish intelligent archival system using Imperator reasoning for complex decisions. This is the foundation for V2/V3/V4 optimizations.
