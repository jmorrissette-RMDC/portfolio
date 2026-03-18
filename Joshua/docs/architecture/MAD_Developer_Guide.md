# MAD Developer's Guide

**Version:** 1.0
**Status:** Adopted
**Date:** 2025-11-30
**Owner:** Architecture Team

---

## 1. Core Development Standards

All MADs must be developed in alignment with the following core standards. These are the active, binding rules for all new development and refactoring.

### Architectural Principles (from ADRs 025, 027)

*   **I. Codebase:** A single codebase for each MAD is tracked in version control.
*   **II. Dependencies:** All dependencies **must** be explicitly declared (e.g., in `requirements.txt`) and isolated. Do not rely on system-level packages.
*   **III. Config:** All configuration (credentials, hostnames, etc.) **must** be stored in environment variables. No configuration should be hardcoded.
*   **IV. Backing Services:** All backing services (databases, file storage) are treated as attached resources, accessible via a URL or other locator stored in config. This is primarily achieved through the use of specialist data-manager MADs.
*   **VI. Processes:** All MAD processes **must** be stateless and share-nothing. Any necessary state must be externalized to a backing service.
*   **VII. Port Binding:** Services **must** be self-contained and export their service via a port (`8000` internally). This is handled by the `Joshua_Communicator` library and must not be bypassed.
*   **VIII. Concurrency:** The application's internal logic must be written to support concurrency. In our `async` architecture, this means **never using blocking I/O calls** that would stall the event loop.
*   **IX. Disposability:** MADs must be disposable, favoring fast startup and graceful shutdown. Avoid long, blocking operations during application startup.
*   **XI. Logs:** All logs **must** be treated as event streams. Your application should write its logs, unbuffered, to `stdout`. All logging **must** be performed through the `Joshua_Communicator`'s integrated logger.

### Code Promotion & Environment Parity (from ADR 025)

*   **Development:** May use a read-only "hot-mount" of the source code to enable rapid iteration. Data is read from and written to `/mnt/irina_storage/dev/`.
*   **Testing & Production:** **Must** use immutable Docker images where the code is **COPIED** into the image at build time. These environments will **not** mount the host source code. They will mount `/mnt/irina_storage/test/` and `/mnt/irina_storage/prod/` respectively.
*   **Storage Paths:** All file I/O within a MAD's code **must** use the `STORAGE_ROOT` environment variable to construct paths, with a default of `/mnt/irina_storage/files`. Hardcoded paths are forbidden.

### Coding & Quality Standards (from ADR 028)

*   **Formatting & Linting:** All Python code **must** be formatted with `black` and linted with `ruff`.
*   **Type Hinting:** All function signatures and variable declarations **must** include modern Python type hints.
*   **Testing:** All public functions and methods **must** have corresponding unit tests using the `pytest` framework.
*   **Security:** No secrets are to be hardcoded in the codebase. All secrets **must** be managed via environment variables until the `Turing` MAD is operational.

### V0.7+ Development Standards

*   All MADs developed at V0.7+ must follow the **flow-based architecture** (ADR-032), implementing logic in declarative LangFlow flows rather than imperative Python code.
*   Use **LangFlow native nodes** where available (ADR-037), only building custom nodes for provider-specific optimizations or domain-specific functionality.
*   Follow the **thin composition layer** pattern - MADs should be ~100 lines of glue code, with all functionality in flows and library imports.

## 2. The Three Stages of Development

This document defines the formal, three-stage development lifecycle for all MADs within the Joshua ecosystem. This process ensures that development proceeds from a high-level vision to a concrete, vetted design before implementation begins, ensuring architectural consistency and quality.

This process is a direct outcome of the architectural decisions outlined in ADR-021, ADR-022, and ADR-023.

Every MAD, whether new or undergoing a major revision, must proceed through the following three distinct stages. The output of each stage is a formal document that serves as the input for the next.

### **Stage 1: Requirements Document (`.md`)**

*   **Purpose:** To capture the high-level vision, role, and strategic purpose of the MAD.
*   **Content:**
    *   **Role:** The MAD's primary responsibility within the ecosystem (e.g., "File System Management").
    *   **Scope:** The boundaries of its domain and key capabilities.
    *   **Future Evolution:** A high-level summary of its expected evolution path, aligned with the 6-Phase System Roadmap.
    *   **Provisional Tool List:** A preliminary, *unvetted* list of the tools the MAD is expected to provide. This list is for conceptual planning only.
*   **Key Characteristic:** This document is about the **"what"** and the **"why."** It is intentionally not overly technical.
*   **Ownership:** Typically authored by the System Architect or a project lead. The existing 31 requirements documents in `Joshua/docs/requirements/` represent this stage.

### **Stage 2: Design Document (`.md`)**

*   **Purpose:** To translate the high-level requirements into a concrete, technical blueprint for implementation. This is the most critical technical design phase.
*   **Content:**
    *   **Finalized Tool API:** This is the core of the Design Document. It provides the **authoritative, vetted, and complete specification** for every tool the Action Engine will expose. For each tool, it must include:
        *   The exact `tool_name`.
        *   A clear `description`.
        *   A precise `inputSchema` detailing all parameters, their types, and whether they are required.
        *   A precise `outputSchema` detailing the structure of the successful return value.
    *   **Internal Architecture:** Details on the MAD's internal components (e.g., specific Python libraries to be used, database schemas if any).
    *   **Dependencies:** An explicit list of other MADs this MAD will interact with.
    *   **Test Plan:** A high-level plan for the unit and integration tests that will be written.
*   **Key Characteristic:** This document is about the **"how."** It is the definitive guide for the developer (whether human or AI like `Hopper`). The Action Engine's code should be a direct implementation of the tool APIs defined here.
*   **Ownership:** Authored by the lead developer or `Hopper`, with review and approval from the Architecture Team.

### **Stage 3: Implementation (`.py`, `.toml`, etc.)**

*   **Purpose:** To write the code that brings the Design Document to life.
*   **Process:**
    1.  The developer (or `Hopper`) uses the Design Document as the single source of truth for implementation.
    2.  The Action Engine's MCP server is built to expose the exact tools specified in the Design Document.
    3.  The Thought Engine is implemented to use those internal tools.
    4.  Unit and integration tests are written according to the test plan.
*   **Key Characteristic:** This stage is purely about execution. All major design decisions should have already been made and resolved in Stage 2.

## 3. Workflow Diagram

```mermaid
graph TD
    A[Stage 1: Requirements Document<br><i>(What & Why)</i>] --> B{Review &<br>Approval};
    B --> C[Stage 2: Design Document<br><i>(How - Finalizes Tool API)</i>];
    C --> D{Review &<br>Approval};
    D --> E[Stage 3: Implementation<br><i>(Code & Tests)</i>];
    E --> F{Code Review &<br>CI/CD};
    F --> G[Deployment];
```

## 4. Rationale

Adopting this formal lifecycle provides several key benefits:

*   **Rigor:** It forces a deliberate design phase, preventing requirements from flowing directly into half-considered code.
*   **Clarity:** The Design Document becomes the single source of truth for a MAD's API, which is essential for both internal development and external discovery.
*   **Vetting:** It provides a formal checkpoint (the Design Document review) to ensure a MAD's proposed tools align with the broader ecosystem architecture before implementation effort is spent.
*   **Enables Automation:** This structured process is ideal for autonomous development. `Hopper` can be tasked to take a Requirements Document, generate a Design Document for review, and then, upon approval, execute the implementation.
