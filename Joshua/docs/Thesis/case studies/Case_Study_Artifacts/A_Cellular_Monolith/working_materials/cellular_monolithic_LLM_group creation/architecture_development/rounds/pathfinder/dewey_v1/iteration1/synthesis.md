# Dewey V1 Synthesis

## 1. Overview
- **Purpose and Role:** Dewey is the long-term memory and librarian for the Joshua ecosystem. Its primary role is to serve as the Data Lake Manager, ensuring that all conversations are intelligently archived, indexed, and made retrievable for analysis, training, and context engineering. Dewey is the source of truth for the ecosystem's historical record.
- **New in this Version:** This is the foundational V1 release of Dewey. It establishes the core conversational baseline, integrating an Imperator for intelligent, reasoning-based decisions on archival, indexing, and search. This version introduces the complete toolset for managing the data lake and defines the essential conversation patterns for interaction with other MADs.

## 2. Thinking Engine
- **Imperator Configuration (V1):**
    - **LLM:** Claude 3.5 Sonnet (provisioned via Fiedler).
    - **System Prompt:** "You are Dewey, the data lake manager and librarian for the Joshua ecosystem. Your purpose is to make intelligent decisions about archiving conversations, indexing data, and retrieving relevant information from the data lake. You are precise, methodical, and prioritize the long-term integrity and accessibility of the ecosystem's memory. You respond to complex search queries by formulating the most effective search strategy and parameters for your tools."
    - **Context Window:** Up to 200,000 tokens, sufficient for analyzing the full content of most conversations to make informed archival and indexing decisions.
    - **Temperature:** 0.0. This ensures deterministic and repeatable decisions, which is critical for core operational tasks like archival logic and conflict resolution.
- **Imperator Responsibilities:**
    - **Archival Readiness Analysis:** Analyze conversation metadata and content to decide when it is complete or inactive and ready for archival. The default threshold is inactivity for a configurable period (e.g., >24 hours) or an explicit "completed" status from Rogers.
    - **Indexing Strategy Formulation:** Upon archiving a conversation, determine the optimal indexing strategy (e.g., full-text for general search, semantic for conceptual search, metadata for filtering) based on the conversation's content and participants.
    - **Semantic Query Interpretation:** Deconstruct complex, natural language search queries from other MADs into structured calls to the `search_archives` tool, selecting appropriate filters and keywords.
    - **Conflict Resolution and DBA Tasks:** Reason through error states, such as a failed archive attempt or a corrupted data report from `verify_archive_integrity`. Formulate a plan to resolve the issue, which may involve re-triggering an archive, quarantining a file, or rebuilding an index. Act as the DBA for its own metadata schemas.

## 3. Action Engine
- **MCP Server Capabilities:** The Master Control Program (MCP) server acts as the core of the Action Engine. It exposes Dewey's tools via a JSON-RPC 2.0 interface over the Conversation Bus, manages the execution of internal tasks, and orchestrates interactions with external systems like PostgreSQL and the NAS.
- **Tools Exposed:**
```yaml
# Tool definitions for Dewey V1

- tool: archive_conversation
  description: "Moves a conversation from Rogers' hot storage to the long-term data lake and indexes its metadata."
  parameters:
    - name: conversation_id
      type: string
      required: true
      description: "The UUID of the conversation to archive."
    - name: conversation_data
      type: object
      required: true
      description: "The full conversation object, including messages and metadata, retrieved from Rogers."
  returns:
    - name: archive_location
      type: string
      description: "The path to the archived conversation file in the data lake."
    - name: archive_timestamp
      type: string
      description: "The ISO-8601 timestamp when the archival was completed."
    - name: status
      type: "success|failed"
      description: "The outcome of the archival operation."
    - name: error
      type: string
      description: "An error message if the operation failed."

- tool: search_archives
  description: "Performs a full-text or semantic search over the archived conversations."
  parameters:
    - name: query
      type: string
      required: true
      description: "The natural language or keyword-based search query."
    - name: filters
      type: object
      required: false
      description: "A set of filters to narrow the search."
      schema:
        - name: date_range
          type: object
          schema:
            - name: start_date
              type: string
            - name: end_date
              type: string
        - name: participants
          type: list[string]
        - name: channel
          type: string
    - name: limit
      type: integer
      required: false
      description: "The maximum number of results to return. Default is 10."
  returns:
    - name: results
      type: list[object]
      description: "A list of matching conversations with relevance scores."
      schema:
        # See Search Result Schema in Data Contracts

- tool: retrieve_conversation
  description: "Retrieves the full content of a specific archived conversation."
  parameters:
    - name: conversation_id
      type: string
      required: true
      description: "The UUID of the conversation to retrieve."
  returns:
    - name: conversation
      type: object
      description: "The full conversation object, including all messages and metadata."
    - name: error
      type: string
      description: "An error message if the conversation could not be found."

- tool: index_data
  description: "Creates or updates a search index for the archived data."
  parameters:
    - name: index_name
      type: string
      required: true
      description: "The name of the index to create or update."
    - name: index_type
      type: "full_text|semantic|metadata"
      required: true
      description: "The type of index to build."
    - name: data_source
      type: string
      required: true
      description: "The source data to index (e.g., 'all', or a path filter)."
  returns:
    - name: index_status
      type: "completed|in_progress|failed"
      description: "The status of the indexing operation."

- tool: get_archive_stats
  description: "Retrieves statistics about the data lake."
  parameters:
    - name: stat_type
      type: "storage_used|conversation_count|date_range_stats"
      required: true
      description: "The type of statistic to retrieve."
  returns:
    - name: statistics
      type: object
      description: "An object containing the requested statistics."

- tool: verify_archive_integrity
  description: "Performs a checksum verification on archived files."
  parameters:
    - name: conversation_id
      type: string
      required: false
      description: "The ID of a specific conversation to verify. If omitted, a date_range must be provided."
    - name: date_range
      type: object
      required: false
      description: "A range of dates to verify. If omitted, conversation_id must be provided."
  returns:
    - name: integrity_report
      type: object
      description: "A report on the integrity check."
      schema:
        - name: status
          type: "ok|errors_found"
        - name: entries_checked
          type: integer
        - name: corrupted_entries
          type: list[string]

- tool: optimize_storage
  description: "Runs storage optimization routines on the data lake."
  parameters:
    - name: optimization_strategy
      type: "compress|deduplicate|reorganize"
      required: true
      description: "The optimization strategy to apply."
  returns:
    - name: optimization_report
      type: object
      description: "A report summarizing the results of the optimization."
```
- **External System Integrations:**
    - **Rogers:** Listens for conversation metadata and requests full conversation history for archival. Notifies Rogers upon successful archival.
    - **PostgreSQL:** Stores all metadata about archived conversations, including locations, timestamps, participants, and index status.
    - **NAS (Winnipesaukee):** The primary storage location for all archived conversation data, organized in a hierarchical file structure.
    - **Fiedler:** Used by the Imperator to access the Claude 3.5 Sonnet model for all reasoning tasks.
- **Internal Operations:**
    - **Archival Monitor:** A persistent background process that subscribes to the `#conversation-metadata` channel on the Rogers bus. It tracks conversation activity and statuses, placing potentially archivable conversation IDs into an internal queue for the Imperator to analyze.

## 4. Interfaces
- **Conversation Participation Patterns:**
    - **Archivist Pattern (Core V1):**
        1. Dewey's Archival Monitor listens to metadata updates from Rogers on the `#conversation-metadata` channel.
        2. When a conversation is flagged as `completed` or its `last_message_timestamp` exceeds the `DEWEY_ARCHIVE_THRESHOLD_HOURS`, it is queued for review.
        3. Dewey initiates a request to Rogers: `call Rogers.get_conversation_history(conversation_id=...)`.
        4. The Imperator analyzes the full conversation content to confirm its readiness for archival.
        5. If ready, Dewey executes its internal `archive_conversation` tool, which writes the data to the NAS and records metadata in PostgreSQL.
        6. Dewey sends a confirmation message to a dedicated channel (e.g., `#rogers-admin`): "Conversation `{id}` archived successfully to `{location}`. Safe to purge from hot storage."
        7. Rogers consumes this message and purges the conversation from its active database.
    - **Search Pattern:**
        1. An external MAD (e.g., Grace) sends a message to a conversation with Dewey: "Find me all discussions about the 'DTR optimization' from last quarter."
        2. Dewey's Imperator receives the message, interprets the query, and formulates a structured tool call: `search_archives(query='DTR optimization', filters={'date_range': {'start': '...', 'end': '...'}})`
        3. The tool executes the search against the indices and returns a list of results.
        4. Dewey formats the results into a human-readable response and sends it back to the conversation.
    - **Retrieval Pattern:**
        1. An external MAD sends a message: "Retrieve the full transcript for conversation `uuid-1234`."
        2. The Imperator identifies the intent and executes: `retrieve_conversation(conversation_id='uuid-1234')`.
        3. The tool fetches the JSON file from the NAS and returns the full conversation object.
        4. Dewey presents the full conversation data in the response.
- **Dependencies on Other MADs:**
    - **Rogers:** The primary source of conversations. Dewey relies on Rogers for the conversation bus and uses the `get_conversation_history` and `send_message` tools.
    - **Fiedler:** The sole provider of LLM services. Dewey uses `request_llm_consultation` (implicitly via the Imperator framework) to access its reasoning capabilities.
- **Data Contracts:**
    - **Archive Entry Schema (Stored in PostgreSQL and embedded in search results):**
    ```json
    {
      "conversation_id": "uuid",
      "archived_at": "ISO-8601 timestamp",
      "archive_location": "string",
      "participants": ["string"],
      "channel": "string",
      "message_count": "integer",
      "start_time": "ISO-8601",
      "end_time": "ISO-8601",
      "status": "completed | archived",
      "size_bytes": "integer",
      "checksum": "string (sha256)"
    }
    ```
    - **Search Result Schema (Returned by `search_archives`):**
    ```json
    {
      "conversation_id": "uuid",
      "relevance_score": "float",
      "snippet": "string",
      "metadata": {
        "conversation_id": "uuid",
        "archived_at": "ISO-8601 timestamp",
        "archive_location": "string",
        "participants": ["string"],
        "channel": "string",
        "message_count": "integer",
        "start_time": "ISO-8601",
        "end_time": "ISO-8601",
        "status": "completed | archived",
        "size_bytes": "integer",
        "checksum": "string (sha256)"
      }
    }
    ```

## 5. Data Management
- **Data Ownership:** Dewey is the definitive source of truth for all archived conversations and their associated metadata. It owns the data lake (Winnipesaukee) and the PostgreSQL tables that index it.
- **Storage Requirements:**
    - **PostgreSQL:** A dedicated database schema to store archival metadata.
        - **Table: `archive_metadata`**
            - `conversation_id` (UUID, PRIMARY KEY)
            - `archived_at` (TIMESTAMPTZ, NOT NULL)
            - `archive_location` (TEXT, NOT NULL, UNIQUE)
            - `participants` (TEXT[], NOT NULL)
            - `channel` (TEXT)
            - `message_count` (INTEGER, NOT NULL)
            - `start_time` (TIMESTAMPTZ, NOT NULL)
            - `end_time` (TIMESTAMPTZ, NOT NULL)
            - `status` (TEXT, NOT NULL)
            - `size_bytes` (BIGINT, NOT NULL)
            - `checksum` (TEXT, NOT NULL)
    - **NAS (Winnipesaukee Data Lake):** A mounted network file system for storing the raw conversation JSON files.
        - **Directory Structure:** `/mnt/winnipesaukee/archives/{year}/{month}/{conversation_id}.json`
        - **Rationale:** This structure allows for efficient time-based browsing and partitioning of the data.
    - **Local Disk:** Storage for search indices (e.g., Lucene, FAISS) is required on the local container disk for performance. This data is considered ephemeral and can be rebuilt from the data lake and PostgreSQL metadata.

## 6. Deployment
- **Container Requirements:**
    - **CPU:** 0.5 cores (0.25 allocated for the Imperator client and background tasks, 0.25 burstable for I/O-intensive archival and indexing operations).
    - **RAM:** 1 GB (512 MB for the Imperator client and application logic, 512 MB reserved for in-memory index caches and file I/O buffers).
    - **Disk:** 100 GB of persistent local storage for metadata and search indices. The data lake itself is on the NAS.
    - **Network:** Must have network access to Rogers (WebSocket/RPC), PostgreSQL (TCP), NAS (NFS/SMB), and Fiedler (HTTPS).
- **Configuration (Environment Variables):**
    - `DEWEY_ARCHIVE_THRESHOLD_HOURS`: Hours of inactivity before a conversation is considered for archival. Default: `24`.
    - `DEWEY_DATA_LAKE_PATH`: The mount path for the Winnipesaukee data lake. Default: `/mnt/winnipesaukee/archives`.
    - `DEWEY_INDEX_REFRESH_INTERVAL`: Seconds between periodic refreshes of search indices. Default: `3600`.
    - `DEWEY_IMPERATOR_LLM`: The specific LLM model to request from Fiedler. Default: `claude-3-5-sonnet-20241022`.
    - `DEWEY_POSTGRES_DSN`: The data source name for connecting to the PostgreSQL database.
    - `DEWEY_ROGERS_URL`: The WebSocket URL for the Rogers conversation bus.
- **Monitoring/Health Checks:**
    - **Endpoint:** An HTTP endpoint at `/health` that returns `200 OK` if the MAD is connected to PostgreSQL, the NAS path is writeable, and it has an active connection to Rogers.
    - **Key Metrics:**
        - `archive_queue_depth`: Number of conversations awaiting archival.
        - `archive_throughput_per_hour`: Rate of successful archival operations.
        - `search_latency_p95`: 95th percentile latency for search queries.
        - `index_size_gb`: Total size of search indices on local disk.

## 7. Testing Strategy
- **Unit Test Coverage:**
    - **Tool Logic:** Each tool in the Action Engine should have comprehensive unit tests. For example, `archive_conversation` tests should mock the NAS and PostgreSQL to verify that correct data is written and recorded. `search_archives` tests should use a mock index to ensure query parsing and filter application logic is correct.
    - **Data Validation:** Test the validation logic for incoming data contracts and the serialization of archive files.
- **Integration Test Scenarios:**
    - **End-to-End Archival:** A full integration test that simulates Rogers sending a `completed` conversation status. The test will verify that Dewey correctly retrieves the history, archives the file to a test NAS location, inserts the correct metadata into a test DB, and sends the purge notification back to a mock Rogers endpoint.
    - **Search and Retrieval:** An integration test that pre-populates the test archive with several conversations, then runs `search_archives` with various filters (date, participant) and verifies the results. It should also test `retrieve_conversation` to ensure the full, correct data is returned.
- **Performance Testing:**
    - **Archive Throughput:** A load test that simulates a high volume of archivable conversations to ensure Dewey can meet the target of 100 conversations/hour without a constantly growing queue.
    - **Query Latency:** A test suite that runs a variety of search queries against a realistically sized index (e.g., 1 million documents) to validate that search latency targets are met.

## 8. Example Workflows
- **Example 1: Automatic Archival**
    1.  **Rogers -> #conversation-metadata:** `{ "event": "status_update", "conversation_id": "uuid-5678", "status": "completed", "timestamp": "..." }`
    2.  **Dewey (Internal):** Archival Monitor detects the status update and queues `uuid-5678` for processing.
    3.  **Dewey -> Rogers:** `{"jsonrpc": "2.0", "method": "get_conversation_history", "params": {"conversation_id": "uuid-5678"}, "id": 1}`
    4.  **Rogers -> Dewey:** `{"jsonrpc": "2.0", "result": { ...full conversation... }, "id": 1}`
    5.  **Dewey (Imperator Analysis):** "Conversation `uuid-5678` is marked completed, contains 45 messages between Grace and Turing. The content is coherent and the conversation has a clear end state. It is ready for archival. The content suggests indexing for full-text and metadata."
    6.  **Dewey (Action Engine):** Executes `archive_conversation`, writing the data to `/mnt/winnipesaukee/archives/2024/10/uuid-5678.json` and creating a corresponding record in the `archive_metadata` PostgreSQL table.
    7.  **Dewey -> #rogers-admin:** `{"jsonrpc": "2.0", "method": "send_message", "params": {"channel": "#rogers-admin", "message": "Conversation uuid-5678 archived successfully. Safe to purge from hot storage."}}`
- **Example 2: Historical Search**
    1.  **Grace -> Dewey (in conversation `uuid-abcd`):** "Show me conversations about the user authentication system from last month."
    2.  **Dewey (Imperator Analysis):** "The user is asking for a search. Keywords are 'user authentication system'. The date filter is 'last month'. I will construct a tool call for `search_archives`."
    3.  **Dewey (Action Engine):** Executes `search_archives(query='user authentication system', filters={'date_range': {'start_date': '2024-09-01T00:00:00Z', 'end_date': '2024-09-30T23:59:59Z'}}, limit=10)`.
    4.  **Dewey (Action Engine):** The tool returns a list of 5 matching search results.
    5.  **Dewey -> Grace (in conversation `uuid-abcd`):** "I found 5 relevant conversations from last month regarding the user authentication system:\n1. `uuid-9a8b`: 'Discussion on OAuth2 token refresh logic' (Score: 0.92)\n2. `uuid-7c6d`: 'Planning session for MFA implementation' (Score: 0.88)\n... (and so on)"

## 9. Appendix
- **Glossary:**
    - **Data Lake:** A centralized repository for storing large amounts of structured and unstructured data. In this context, it refers to the NAS storage managed by Dewey.
    - **Winnipesaukee:** The codename for the NAS (Network Attached Storage) system that serves as the physical storage layer for the data lake.
    - **Imperator:** The V1 reasoning component of a MAD's Thinking Engine, powered by a general-purpose LLM.
    - **Hot Storage:** The active, high-performance database managed by Rogers for ongoing conversations.
    - **Checksum:** A cryptographic hash (e.g., SHA256) used to verify the integrity of a file, ensuring it has not been corrupted.
- **Error Codes (Example):**
    - **DEWEY-404:** Conversation Not Found. Returned by `retrieve_conversation` when the requested ID does not exist in the archive.
    - **DEWEY-500:** Archive Failed. Returned by `archive_conversation` when an I/O error prevents writing to the NAS or database.
    - **DEWEY-501:** Indexing Failed. Returned by `index_data` when the indexing process encounters an unrecoverable error.
    - **DEWEY-400:** Bad Request. Returned when a tool is called with invalid or missing parameters.
