# Knuth Requirements

- **Role**: Documentation Management
- **Version**: V7.0
- **Home**: `mads/knuth/`

---

## 1. Overview

-   **Purpose**: `Knuth` is the specialized MAD responsible for the creation, management, and compilation of complex, structured technical documentation within the Joshua ecosystem. It acts as the system's "Master Technical Writer" and "Documentation System."
-   **V7.0 Scope Definition**: As a V7.0 MAD, Knuth is a fully cognitive agent capable of autonomously generating everything from simple READMEs to comprehensive, multi-chapter, cross-referenced books, orchestrating other MADs to gather information and produce high-quality, polished documentation.

---

## 2. Tool Exposure Model

This MAD follows the Direct Tool Exposure architecture (ADR-023). Its public tools are exposed directly on its MCP server and are discoverable via the Rogers registry. Any incoming communication that is not a valid MCP call for an exposed tool is routed to the Thought Engine for conversational processing (e.g., "Document the entire `Sutherland` MAD, including its API and architecture.").

> **Note on Tool List:** The tools listed in this document are a *provisional set* based on the MAD's high-level requirements. The final, authoritative list of tools, their specific parameters, and their return schemas will be defined in a dedicated Design Document prior to implementation.

---

## 3. Public Action Engine Tools

### `knuth_create_document_project`
- **Description:** Initiates a new documentation project with a given title and a hierarchical structure of chapters and sections.
- **Input Schema:**
    - `title` (string, required): The main title of the document.
    - `structure` (array[dict], required): A hierarchical list defining chapters and sections (e.g., `[{"title": "Introduction", "sections": [...]}]`).
- **Output Schema:** `{"status": "success", "document_id": "uuid-1234", "message": "Documentation project created."}`

### `knuth_add_section_content`
- **Description:** Adds or replaces the content for a specific section within a document project.
- **Input Schema:**
    - `document_id` (string, required): The ID of the document project.
    - `section_path` (array[string], required): The hierarchical path to the section (e.g., `["Introduction", "Overview"]`).
    - `content` (string, required): The content to add (e.g., Markdown text).
    - `content_type` (string, optional, default: "markdown"): The format of the content.
- **Output Schema:** `{"status": "success", "document_id": "...", "section_path": "..."}`

### `knuth_add_diagram_to_section`
- **Description:** Orchestrates `Playfair` to generate a diagram based on a prompt and embeds it into a specific document section.
- **Input Schema:**
    - `document_id` (string, required): The ID of the document project.
    - `section_path` (array[string], required): The hierarchical path to the section.
    - `diagram_prompt` (string, required): A natural language prompt for `Playfair` to generate the diagram.
- **Output Schema:** `{"status": "success", "output_image_path": "/path/to/diagram.png"}`

### `knuth_embed_code_snippet`
- **Description:** Fetches a code snippet from a file (via `Horace` or `Starret`) and embeds it with syntax highlighting into a document section.
- **Input Schema:**
    - `document_id` (string, required): The ID of the document project.
    - `section_path` (array[string], required): The hierarchical path to the section.
    - `file_path` (string, required): The path to the source code file.
    - `line_range` (string, optional): A range of lines (e.g., "10-25"). If omitted, the entire file is embedded.
- **Output Schema:** `{"status": "success", "code_embedded": true}`

### `knuth_compile_document`
- **Description:** Compiles the entire document project into a final output file (e.g., PDF, HTML book), handling table of contents, numbering, and cross-references.
- **Input Schema:**
    - `document_id` (string, required): The ID of the document project.
    - `format` (string, required): The target output format (e.g., "pdf", "html").
    - `output_path` (string, required): The absolute path to save the compiled file.
- **Output Schema:** `{"status": "success", "output_path": "/path/to/document.pdf"}`

---

## 4. Future Evolution (Post-V0)

Knuth is introduced in Phase 6 (Expansion) at V7.0 as the master technical writer and documentation system for the mature Joshua ecosystem.

*   **Phase 6 (Expansion / V7.0):** Knuth enters the ecosystem as a fully-capable V7.0 MAD with complete PCP (DTR, LPPM, CET, CRS), pure Kafka conversation bus integration, and eMAD awareness. As the documentation specialist, Knuth orchestrates multiple MADs (Hopper for code analysis, Playfair for diagrams, Fiedler for prose generation) to autonomously create comprehensive technical documentation. Knuth embodies Donald Knuth's literate programming philosophy, weaving code and explanation into coherent narratives. It manages the entire Joshua Papers suite, maintaining cross-references and version consistency across all system documentation.
*   **Post-V7.0 Enhancements:** Future evolution includes real-time collaborative documentation (multiple MADs contributing simultaneously to living documents), automated documentation maintenance (detecting code-documentation drift and triggering updates), multi-format adaptive output (tailoring documentation complexity to audience expertise), and integration with Lovelace for automated research paper generation from experimental results. Knuth's CRS learns optimal documentation structures for different technical domains, continuously improving clarity and effectiveness based on reader engagement patterns.

---
