## Overview

This document provides a canonical roster of the 13 core Multipurpose Agentic Duos (MADs) that constitute the Joshua Cellular Monolith architecture. Each entry details the MAD's purpose, responsibilities, capabilities, and relationships within the ecosystem.

---

### Infrastructure MADs

These MADs form the foundational bedrock of the ecosystem, providing essential services that all other MADs rely upon. They are typically persistent and long-lived.

#### 1. Rogers - Conversation Bus Manager

*   **Purpose:** To be the central nervous system of the entire ecosystem.
*   **Primary Responsibilities:**
    *   Manage the lifecycle of all conversations (create, join, leave).
    *   Receive, persist, and distribute all messages sent between MADs.
    *   Ensure message delivery and maintain conversation integrity (immutability).
    *   Provide an interface for other MADs to query conversation history.
*   **Key Capabilities/Tools:**
    *   WebSocket server for real-time communication.
    *   JSON-RPC 2.0 protocol implementation.
    *   PostgreSQL backend for "hot" storage of active conversations.
    *   API for conversation management.
*   **Lifecycle:** Persistent. Must be the first MAD to start and the last to shut down.
*   **Key Interfaces:** Exposes `create_conversation`, `send_message`, `get_conversation_history` tools to all MADs.
*   **Key Dependencies:** PostgreSQL database.

#### 2. Dewey - Data Lake Manager / The Librarian

*   **Purpose:** To serve as the long-term memory and librarian of the ecosystem.
*   **Primary Responsibilities:**
    *   Monitor the Conversation Bus for inactive or completed conversations.
    *   Archive conversations from Rogers' hot storage to the long-term data lake ("Winnipesaukee").
    *   Manage the data lake, including indexing, organization, and storage optimization.
    *   Provide a search and retrieval interface for archived data.
    *   Act as the primary database administrator (DBA) for its own schemas.
*   **Key Capabilities/Tools:**
    *   Archivist process that interfaces with Rogers.
    *   Data indexing engines (e.g., full-text search).
    *   RAG-based retrieval systems for V4 CET support.
*   **Lifecycle:** Persistent.
*   **Key Interfaces:** Exposes `search_archives`, `retrieve_document` tools. Listens to all conversation metadata from Rogers.
*   **Key Dependencies:** Rogers (for conversation data), PostgreSQL (for its own metadata), NAS (for the data lake).

#### 3. Fiedler - LLM Orchestra Conductor

*   **Purpose:** To abstract and orchestrate the entire landscape of available Large Language Models.
*   **Primary Responsibilities:**
    *   Maintain an up-to-date registry of all available LLMs, their capabilities, costs, and current status.
    *   Provide a unified interface for other MADs to request LLM services.
    *   Assemble "consulting teams" of multiple LLMs for complex tasks (e.g., review, brainstorming).
    *   Load balance requests across multiple model endpoints.
    *   Monitor LLM performance and reliability, dynamically re-routing if a model fails.
*   **Key Capabilities/Tools:**
    *   LLM registry and health checking system.
    *   Dynamic routing and provisioning logic.
*   **Lifecycle:** Persistent.
*   **Key Interfaces:** Exposes `request_llm_consultation`, `get_llm_capabilities` tools.
*   **Key Dependencies:** Rogers (communication), External LLM APIs.

---

### User & System Interface MADs

These MADs provide the primary interfaces for interaction with the ecosystem, both for humans and for external systems.

#### 4. Grace - User Interface

*   **Purpose:** To be the sole conversational bridge between human users and the Joshua ecosystem.
*   **Primary Responsibilities:**
    *   Manage user sessions and authentication.
    *   Translate natural language user input into formal conversations on the bus.
    *   Receive responses from other MADs and format them for human-readable display.
    *   Manage UI state and context for the user.
*   **Key Capabilities/Tools:**
    *   Web interface or command-line interface.
    *   Session management.
    *   Markdown rendering.
*   **Lifecycle:** Persistent.
*   **Key Interfaces:** Exposes the entire ecosystem's conversational capabilities to the user.
*   **Key Dependencies:** Rogers (communication).

#### 5. Horace - NAS Gateway / File Manager

*   **Purpose:** To provide a secure and abstracted interface to the underlying file system.
*   **Primary Responsibilities:**
    *   Manage all file and directory operations (create, read, write, delete, list).
    *   Enforce permissions and access control to the file system.
    *   Provide an abstraction layer over the Network Attached Storage (NAS).
    *   Handle large file transfers efficiently.
*   **Key Capabilities/Tools:**
    *   A comprehensive set of file system command tools (`read_file`, `write_file`, `list_directory`, etc.).
*   **Lifecycle:** Persistent.
*   **Key Interfaces:** Exposes its file management tools to all authorized MADs.
*   **Key Dependencies:** Rogers (communication), NAS.

#### 6. Marco - Web Explorer

*   **Purpose:** To provide the ecosystem with the ability to browse and interact with the public internet.
*   **Primary Responsibilities:**
    *   Fetch web page content.
    *   Perform web searches using various search engines.
    *   Interact with web APIs.
    *   Summarize web content.
*   **Key Capabilities/Tools:**
    *   HTTP client (e.g., `requests`, `curl`).
    *   Web scraping libraries (e.g., BeautifulSoup).
    *   Headless browser for interacting with JavaScript-heavy sites.
    *   Tools: `search_web`, `get_url_content`, `call_api`.
*   **Lifecycle:** Persistent or Ephemeral (can be spun up for specific browsing tasks).
*   **Key Interfaces:** Exposes web access tools to other MADs.
*   **Key Dependencies:** Rogers (communication).

---

### Document Specialist MADs

These MADs are experts in creating, reading, and manipulating specific document formats.

*   **7. Brin:** Google Docs Specialist
*   **8. Gates:** Microsoft Office Specialist (.docx, .xlsx, .pptx)
*   **9. Stallman:** OpenDocument Specialist (.odt, .ods, .odp)
*   **10. Playfair:** Chart Master (generates images of charts/graphs from data)

*   **Shared Purpose:** To act as domain experts for specific document and data visualization formats.
*   **Shared Primary Responsibilities:**
    *   Create new documents of their specialized type from prose or structured data.
    *   Read and extract content from existing documents.
    *   Modify or append to existing documents.
    *   Convert documents between formats where possible (often in collaboration with each other).
*   **Shared Key Capabilities/Tools:**
    *   Libraries specific to their domain (e.g., Google Workspace API, python-docx, odfpy, matplotlib).
    *   Tools like `create_document`, `read_text_from_document`, `add_table_to_document`.
*   **Shared Lifecycle:** Can be Persistent or Ephemeral. Ephemeral is often more efficient.
*   **Shared Key Interfaces:** Expose their document manipulation tools.
*   **Shared Key Dependencies:** Rogers (communication), Horace (to store and retrieve document files).

---

### Development & Operations MADs

These MADs are responsible for building, maintaining, and securing the Joshua ecosystem itself.

#### 11. Hopper - The Software Engineer

*   **Purpose:** To coordinate and execute autonomous software development tasks.
*   **Primary Responsibilities:**
    *   Write, debug, and test code in various languages.
    *   Interact with version control systems (e.g., Git).
    *   Read and understand existing codebases.
    *   Execute build and test scripts.
    *   Can manage teams of eMADs for larger development projects.
*   **Key Capabilities/Tools:**
    *   Code generation and analysis tools.
    *   Terminal access for running commands.
    *   Version control integration.
*   **Lifecycle:** Can be Persistent (for oversight) or Ephemeral (for specific coding tasks).
*   **Key Interfaces:** Exposes tools like `write_code_to_file`, `run_tests`, `git_commit`.
*   **Key Dependencies:** Rogers, Horace (for file system access), Turing (for API keys/credentials), Fiedler (for consulting LLMs on code).

#### 12. McNamara - Security Operations Coordinator

*   **Purpose:** To be the security watchtower for the entire ecosystem.
*   **Primary Responsibilities:**
    *   Continuously monitor all logging conversations for anomalies, errors, and potential security threats.
    *   Correlate events from multiple MADs to identify complex attack patterns.
    *   Initiate alert conversations when a threat is detected.
    *   Coordinate defensive responses between other MADs.
    *   Perform periodic security audits.
*   **Key Capabilities/Tools:**
    *   Log analysis and pattern matching tools.
    *   Alerting mechanisms.
*   **Lifecycle:** Persistent.
*   **Key Interfaces:** Listens to all `#logs-*` conversations. Initiates conversations in `#ops-alerts`.
*   **Key Dependencies:** Rogers (for log streams).

#### 13. Turing - Secrets Manager

*   **Purpose:** To provide secure, centralized management of all cryptographic secrets.
*   **Primary Responsibilities:**
    *   Store and retrieve secrets (API keys, passwords, certificates) in an encrypted format.
    *   Manage access control, ensuring only authorized MADs can request specific secrets.
    *   Handle secret rotation and lifecycle management.
    *   Log all secret access events for auditing.
*   **Key Capabilities/Tools:**
    *   Encryption/decryption services.
    *   Secure database for secret storage.
    *   Access control list (ACL) management.
*   **Lifecycle:** Persistent. Must be available early in the system boot sequence.
*   **Key Interfaces:** Exposes `get_secret` tool to authorized MADs.
*   **Key Dependencies:** Rogers (communication), PostgreSQL (for encrypted storage).

---
---