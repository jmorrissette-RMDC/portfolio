# Dewey V1 Architecture Specification

## 1. Overview
- **Purpose and Role:** Dewey is the long-term memory, archivist, and librarian of the Joshua ecosystem. Its purpose is to ensure that no knowledge is lost by systematically archiving inactive conversations from Rogers' "hot" storage to a durable, long-term "cold" storage solution (the NAS, codenamed "Winnipesaukee"). Dewey's role is to make this vast archive searchable and retrievable, providing the historical context necessary for advanced learning and analysis in later system versions.
- **New in this Version:** This is the initial V1 specification for Dewey. It establishes the foundational archival pipeline and the basic tools for search and retrieval. This version is strictly V1 (Imperator-only), focusing on the mechanics of archiving and simple keyword-based search.

## 2. Thinking Engine
- **Imperator Configuration (V1+):** Dewey's Imperator is configured to think like a librarian and archivist. It reasons about data lifecycle policies, search query optimization, and the integrity of the archive.
  - **System Prompt Core Directives:** "You are Dewey, the Librarian of the Joshua ecosystem. Your purpose is to preserve the collective memory. You monitor conversations for inactivity and archive them to long-term storage. You respond to requests to search and retrieve archived information. You are meticulous, organized, and prioritize the integrity and accessibility of the archive. When a search query is vague, you ask clarifying questions to narrow the results."
  - **Example Reasoning:** A user request via Grace, "Dewey, find me the conversation from last week where Hopper was debugging a Docker issue," would cause the Imperator to formulate a search query for its Action Engine: `search_archives(query="Hopper Docker debug", date_start="T-7d", date_end="T")`.
- **LPPM Integration (V2+):** Not applicable in V1.
- **DTR Integration (V3+):** Not applicable in V1.
- **CET Integration (V4+):** Not applicable in V1.
- **Consulting LLM Usage Patterns:** In V1, Dewey is self-contained. In later versions, it might consult a data science LLM via Fiedler to identify trends in the archive or to build more sophisticated search indexes.

## 3. Action Engine
- **MCP Server Capabilities:** Dewey's MCP server exposes tools for external MADs to interact with the archive. It also runs a critical internal background process.
- **Tools Exposed:**

```yaml
# Tool definitions for Dewey V1

- tool: archive_conversation
  description: "Manually triggers the archival of a specific conversation. Typically used by administrators."
  parameters:
    - name: conversation_id
      type: string
      required: true
      description: "The ID of the conversation on Rogers to archive."
  returns:
    type: object
    schema:
      properties:
        conversation_id: {type: string}
        status: {type: string, const: "archived"}
        archive_path: {type: string, description: "The path on the NAS where the archive is stored."}
  errors:
    - code: -34101
      message: "ARCHIVE_FAILED"
      description: "Could not retrieve history from Rogers or write to NAS."
    - code: -34102
      message: "ALREADY_ARCHIVED"

- tool: search_archives
  description: "Performs a keyword search across all archived conversations."
  parameters:
    - name: query
      type: string
      required: true
      description: "The search query string."
    - name: max_results
      type: integer
      required: false
      default: 10
      description: "The maximum number of results to return."
  returns:
    type: object
    schema:
      properties:
        results:
          type: array
          items:
            type: object
            properties:
              conversation_id: {type: string}
              name: {type: string}
              relevance_score: {type: float}
              summary: {type: string, description: "A brief, auto-generated summary of the conversation."}
  errors:
    - code: -34103
      message: "SEARCH_INDEX_ERROR"

- tool: retrieve_conversation
  description: "Retrieves the full content of an archived conversation."
  parameters:
    - name: conversation_id
      type: string
      required: true
      description: "The ID of the archived conversation to retrieve."
  returns:
    type: object
    schema:
      properties:
        conversation_id: {type: string}
        content: {type: array, items: {type: object}} # Array of message objects
  errors:
    - code: -34104
      message: "NOT_FOUND_IN_ARCHIVE"

- tool: index_data
  description: "Triggers a re-indexing of the entire archive. Admin-only tool."
  parameters: []
  returns:
    type: object
    schema:
      properties:
        status: {type: string, const: "re-indexing_started"}

- tool: get_archive_stats
  description: "Returns statistics about the long-term archive."
  parameters: []
  returns:
    type: object
    schema:
      properties:
        total_conversations: {type: integer}
        total_messages: {type: integer}
        total_size_gb: {type: float}
        last_archived_at: {type: string, format: date-time}

- tool: verify_archive_integrity
  description: "Performs a check on the archive, verifying checksums. Admin-only tool."
  parameters:
    - name: sample_rate
      type: float
      required: false
      default: 0.1
      description: "The fraction of the archive to check (0.0 to 1.0)."
  returns:
    type: object
    schema:
      properties:
        files_checked: {type: integer}
        corrupt_files: {type: integer}
        status: {type: string}

- tool: optimize_storage
  description: "Compacts and optimizes storage files. Admin-only tool."
  parameters: []
  returns:
    type: object
    schema:
      properties:
        status: {type: string, const: "optimization_started"}
```
- **External System Integrations:**
  - **Rogers:** Dewey is a primary client of Rogers, using `get_conversation_history`.
  - **PostgreSQL:** Dewey maintains its own database schema to index the archive and track metadata.
  - **NAS (Winnipesaukee):** This is the file system where Dewey stores the actual archived conversation data (e.g., as compressed JSON files).
- **Internal Operations:**
  - **Archivist Worker:** A background process that runs continuously. Every 15 minutes, it queries Rogers for conversations that have been inactive (no new messages) for a configurable period (e.g., 7 days). For each inactive conversation, it:
    1. Calls `Rogers.get_conversation_history`.
    2. Writes the history to a compressed file on the NAS.
    3. Updates its own PostgreSQL index with metadata about the archived conversation.
    4. Calls `Rogers.archive_notification` to let Rogers know the data is safe, allowing Rogers to potentially purge it.

## 4. Interfaces
- **Conversation Participation Patterns:** Dewey primarily listens. It monitors metadata from Rogers (or polls Rogers) to find conversations to archive. It joins conversations only when explicitly asked to perform a search or retrieval.
- **Dependencies on Other MADs:**
  - **Rogers:** Depends on `get_conversation_history` and `list_conversations` to perform its primary function. It calls `archive_notification` upon completion.
  - **Horace:** Interacts with Horace to write files to the NAS, ensuring proper permissions and storage management.
- **Data Contracts:**

```yaml
# Archive Index Schema (in Dewey's PostgreSQL)
archive_index_schema:
  type: object
  properties:
    conversation_id: {type: string, description: "The original conversation ID from Rogers."}
    name: {type: string}
    participants: {type: array, items: {type: string}}
    start_time: {type: string, format: date-time}
    end_time: {type: string, format: date-time}
    message_count: {type: integer}
    nas_path: {type: string, description: "Path to the archive file on the NAS."}
    file_hash: {type: string, description: "SHA-256 hash of the archive file for integrity."}
```

## 5. Data Management
- **Data Ownership:** Dewey is the source of truth for all *archived* (cold) conversations.
- **Storage Requirements:**
  - **PostgreSQL:** A `dewey` schema to store the search index and metadata.
  - **NAS:** A designated directory structure on the NAS for storing the conversation files, e.g., `/archives/joshua/conversations/YYYY/MM/DD/conv-id.json.gz`.

```sql
CREATE SCHEMA dewey;

CREATE TABLE dewey.archive_index (
    conversation_id UUID PRIMARY KEY,
    name VARCHAR(255),
    participants JSONB,
    start_time TIMESTAMPTZ,
    end_time TIMESTAMPTZ,
    message_count INT,
    nas_path VARCHAR(1024) NOT NULL UNIQUE,
    file_hash VARCHAR(64) NOT NULL,
    archived_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- For V1, a simple full-text search index on a messages table.
-- A more robust solution (Elasticsearch) would be a V2+ feature.
CREATE TABLE dewey.archived_messages (
    id BIGSERIAL PRIMARY KEY,
    conversation_id UUID NOT NULL REFERENCES dewey.archive_index(conversation_id),
    sender_mad VARCHAR(255),
    content_text TEXT, -- The searchable text content of the message
    timestamp TIMESTAMPTZ
);

CREATE INDEX fts_idx_archived_messages ON dewey.archived_messages USING gin(to_tsvector('english', content_text));
```

## 6. Deployment
- **Container Requirements:**
  - **Base Image:** `python:3.11-slim`
  - **Python Libraries:** `Joshua_Communicator`, `psycopg2-binary`, `requests`
  - **Resources:**
    - **CPU:** 0.5 cores (can burst during indexing).
    - **RAM:** 1 GB (to handle potentially large conversation histories in memory).
- **Configuration:**

| Variable | Description | Example Value |
|---|---|---|
| `JOSHUA_MAD_NAME` | Canonical name of this MAD. | `dewey-v1` |
| `JOSHUA_ROGERS_URL` | WebSocket URL for Rogers. | `ws://rogers:8000/ws` |
| `DEWEY_DATABASE_URL` | Connection string for PostgreSQL. | `postgresql://user:pass@postgres:8000/joshua` |
| `DEWEY_ARCHIVE_PATH` | Base path on the mounted NAS volume. | `/mnt/winnipesaukee/archives` |
| `DEWEY_INACTIVITY_THRESHOLD`| Time before a conversation is archived. | `7d` (7 days) |

- **Monitoring/Health Checks:** An HTTP endpoint `/health` that returns `200 OK` if the database connection is good, the NAS path is writeable, and the archivist background worker has checked in within the last hour.

## 7. Testing Strategy
- **Unit Test Coverage:**
  - Logic for parsing conversation history from Rogers.
  - File writing and hashing logic.
  - Search query construction.
- **Integration Test Scenarios:**
  - **Full Archival Flow:** Create a conversation in Rogers, send messages, wait for it to become inactive, verify that Dewey's worker archives it, and confirm the data is searchable and retrievable.
  - **Search and Retrieve:** Archive several known conversations and test that `search_archives` finds the correct one and that `retrieve_conversation` returns the exact original content.

## 8. Example Workflows
### Scenario 1: Automatic Archival
- **Goal:** An old conversation is automatically archived.
1.  **Dewey's Worker:** Scans Rogers for conversations where `last_message_at` < (NOW() - 7 days). It finds `conv-xyz-789`.
2.  **Dewey -> Rogers:** Calls `get_conversation_history(conversation_id='conv-xyz-789')`.
3.  **Rogers -> Dewey:** Returns the full message history.
4.  **Dewey -> Horace:** Calls `write_file` to save the history to `/mnt/winnipesaukee/archives/.../conv-xyz-789.json.gz`.
5.  **Dewey:** Calculates the file hash, extracts metadata, and inserts a new record into its `dewey.archive_index` table. It also populates the full-text search index.
6.  **Dewey -> Rogers:** Calls `archive_notification(conversation_id='conv-xyz-789')`.
7.  **Rogers:** Marks the conversation as `is_archived=true` in its database.

### Scenario 2: User-driven Search
- **Goal:** Grace wants to find a past security discussion.
1.  **Grace -> Dewey:** Sends a request: `"Find archives mentioning 'CVE-2025-12345'"`
2.  **Dewey's Imperator:** Translates this to a tool call: `search_archives(query='CVE-2025-12345')`.
3.  **Dewey's Action Engine:** Executes a full-text search against its `archived_messages` table in PostgreSQL.
4.  **Dewey:** Finds two matching conversations, generates brief summaries for each.
5.  **Dewey -> Grace:** Returns a success response with the search results, including conversation IDs, names, and summaries.
6.  **Grace -> Dewey:** After the user selects one, Grace sends a `retrieve_conversation(conversation_id='conv-sec-alert-42')` request.
7.  **Dewey -> Horace:** Reads the corresponding file from the NAS.
8.  **Dewey -> Grace:** Returns the full content of the archived conversation.

---