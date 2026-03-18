# Codd Requirements

- **Role**: Structured Data Management
- **Version**: V7.0
- **Home**: `mads/codd/`

---

## 1. Overview

-   **Purpose**: Codd is the specialist MAD for managing structured data in relational databases (PostgreSQL).
-   **V7.0 Scope Definition**: As a V7.0 MAD, Codd provides a comprehensive and cognitive suite of tools for database administration and executing SQL queries, with an Imperator capable of translating natural language questions into SQL and interpreting results conversationally.

---

## 2. Tool Exposure Model

This MAD follows the Direct Tool Exposure architecture (ADR-023). Its public tools are exposed directly on its MCP server and are discoverable via the Rogers registry. Any incoming communication that is not a valid MCP call for an exposed tool is routed to the Thought Engine for conversational processing (e.g., "Which tables contain user authentication data?").

> **Note on Tool List:** The tools listed in this document are a *provisional set* based on the MAD's high-level requirements. The final, authoritative list of tools, their specific parameters, and their return schemas will be defined in a dedicated Design Document prior to implementation.

---

## 3. Public Action Engine Tools

### `codd_execute_query`
- **Description:** Executes a SQL query against the managed PostgreSQL database. Supports DML and DDL operations.
- **Input Schema:**
    - `query` (string, required): The SQL query string to execute.
    - `database_name` (string, optional): The target database. Defaults to primary.
- **Output Schema (DML):** `{"status": "success", "rows": [{"column1": "value1", ...}, ...], "row_count": 10}`
- **Output Schema (DDL):** `{"status": "success", "message": "Command executed successfully."}`

### `codd_get_schema`
- **Description:** Retrieves the schema definition for a specified table or the entire database.
- **Input Schema:**
    - `table_name` (string, optional): The name of the table to describe. If omitted, returns the entire database schema.
- **Output Schema:** `{"status": "success", "schema_definition": {"table_name": "users", "columns": [...], "indexes": [...]}}`

### `codd_update_schema_metadata` (V4.0+ CET RAG Support)
- **Description:** Updates schema descriptions and rebuilds vector embeddings for improved semantic search, primarily for `Henson`'s CET.
- **Input Schema:**
    - `database_name` (string, required): The database name.
    - `table_name` (string, required): The table name.
    - `description` (string, optional): A natural language description of the table.
    - `column_descriptions` (dict, optional): Descriptions for individual columns.
- **Output Schema:** `{"status": "success", "metadata_updated": true, "embeddings_regenerated": 5}`

---

## 4. Future Evolution (Post-V0)

Codd is introduced in Phase 6 (Expansion) at V7.0 as the specialized structured data management platform for the mature Joshua ecosystem.

*   **Phase 6 (Expansion / V7.0):** Codd enters the ecosystem as a fully-capable V7.0 MAD with complete PCP (DTR, LPPM, CET, CRS), pure Kafka conversation bus integration, and eMAD awareness. As the structured data specialist, Codd provides conversational access to PostgreSQL databases with natural language to SQL translation and semantic understanding of schema relationships. Codd's CET enables complex database workflows (schema migrations, data transformations, cross-database synchronization), while CRS learns from query performance patterns to automatically create indexes, optimize query plans, and detect schema anti-patterns. Codd coordinates with Babbage (semi-structured data), Lovelace (analytical queries), Horace (file-based data), and Brin/Gates (cloud database services).

*   **Post-V7.0 Enhancements:** Future evolution includes multi-database federation, automated disaster recovery orchestration, intelligent data lifecycle management, real-time replication coordination, advanced query optimization using machine learning, autonomous database tuning, and predictive capacity planning aligned with Joshua's strategic data architecture needs.

---