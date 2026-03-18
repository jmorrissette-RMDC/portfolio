# Horace Requirements

- **Role**: File System Management
- **Version**: V1.0
- **Home**: `mads/horace/`

---

## 1. Overview

-   **Purpose**: Horace is the specialist MAD for managing unstructured data, acting as the ecosystem's intelligent file system gateway.
-   **V1.0 Scope Definition**: Provide a robust, programmatic, and conversational interface to file system operations on a designated storage mount. **Horace is explicitly a V1.0+ MAD and is not part of the V0.10 bootstrap ecosystem.** V0 MADs must use direct file I/O.

---

## 2. Tool Exposure Model

This MAD follows the Direct Tool Exposure architecture (ADR-023). Its public tools are exposed directly on its MCP server (in V1.0, this server is for external gateways like `Sam`; inter-MAD communication is via the bus) and are discoverable via the Rogers registry. Any incoming communication that is not a valid MCP call for an exposed tool is routed to the Thought Engine for conversational processing (e.g., "Find all my text files from last week").

> **Note on Tool List:** The tools listed in this document are a *provisional set* based on the MAD's high-level requirements. The final, authoritative list of tools, their specific parameters, and their return schemas will be defined in a dedicated Design Document prior to implementation.

---

## 3. Public Action Engine Tools

### `horace_read_file`
- **Description:** Reads the content of a specified file.
- **Input Schema:**
    - `path` (string, required): The absolute path to the file within the managed storage (e.g., `/mnt/irina_storage/files/report.txt`).
- **Output Schema:** `{"status": "success", "content": "...", "encoding": "utf-8"}`

### `horace_write_file`
- **Description:** Writes content to a specified file, creating directories as needed.
- **Input Schema:**
    - `path` (string, required): The absolute path to the file.
    - `content` (string, required): The content to be written.
- **Output Schema:** `{"status": "success", "path": "/path/to/file.txt", "bytes_written": 1234}`

### `horace_list_directory`
- **Description:** Lists the contents of a specified directory.
- **Input Schema:**
    - `path` (string, required): The absolute path to the directory.
- **Output Schema:** `{"status": "success", "contents": [{"name": "file.txt", "type": "file"}, {"name": "subdir", "type": "directory"}]}`

### `horace_delete`
- **Description:** Deletes a file or an empty directory.
- **Input Schema:**
    - `path` (string, required): The absolute path to the file or directory to delete.
- **Output Schema:** `{"status": "success"}`

---

## 4. Future Evolution (Post-V0)

Horace's role as the file system gateway evolves to become an intelligent, learning-enabled interface with comprehensive vector search and content understanding.

*   **Phase 2 (Conversation / V1.0):** Horace is introduced to the ecosystem and communicates exclusively via the Rogers Conversation Bus (pure Kafka), using `Joshua_Communicator` for all inter-MAD communication. File operations become asynchronous and event-driven, with all requests/responses flowing through the conversation log.
*   **Phase 3 (Cognition / V5.0):** Horace receives the full PCP stack (DTR, LPPM, CET, CRS), enabling intelligent file access patterns, learned caching strategies, and predictive pre-fetching. The vector search capabilities are enhanced with CET-powered semantic understanding, making file discovery dramatically more powerful.
*   **Phase 4 (eMADs / V6.0):** Horace becomes eMAD-aware, capable of providing isolated file system views for ephemeral MAD teams, managing temporary workspaces, and cleaning up resources when eMAD teams terminate.
*   **Phase 5 (Autonomy / V7.0):** Horace integrates with Joshua MAD's strategic directives, implementing top-down file access policies, constitutional constraints on sensitive file operations, and system-wide file governance rules.

---
