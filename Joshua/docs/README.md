# Joshua Project Documentation - Master Index

This document serves as the single, authoritative entry point and master index for all Joshua project documentation. Its purpose is to provide a clear, logical structure and reading guide for new and existing team members, ensuring that critical information is easily discoverable and understood.

---

## 1. Documentation Structure

The `docs/` directory is organized into the following subdirectories, each with a distinct purpose:

*   **`docs/planning/`**:
    *   **Purpose:** Contains actionable, forward-looking plans that guide project execution. These documents describe *what we are going to do*.
    *   **Key Contents:** Detailed build plans, integration strategies, and specific execution roadmaps.

*   **`docs/architecture/`**:
    *   **Purpose:** Houses documents describing the high-level, cross-cutting architectural principles and the definitive strategic vision of the Joshua ecosystem. These are the "laws of physics" for our system.
    *   **Key Contents:**
        *   **`00_Joshua_System_Roadmap.md`**: The authoritative, unified strategic roadmap (to be created by Claude).
        *   **`adr/`**: Architecture Decision Records (ADRs) that document significant architectural decisions.
        *   **`00_MAD_Ingress_Architecture.md`**: Details the standard ingress routing for all MADs.
        *   **`MAD_Development_Lifecycle.md`**: Defines the formal stages for MAD development.

*   **`docs/requirements/`**:
    *   **Purpose:** Contains "Stage 1: Requirements Documents" for each individual MAD and key shared components. These define the high-level "what" and "why" for each part of the system.
    *   **Key Contents:** Numbered MAD requirements documents (e.g., `01_Hopper_V0.10_Requirements.md`), and requirements for shared libraries/templates (e.g., `Imperator_V1.0_Requirements.md`, `MAD_Template_V0.7_Requirements.md`).

*   **`docs/design/`**:
    *   **Purpose:** Contains "Stage 2: Design Documents." These are the detailed technical blueprints that translate requirements into implementation specifics for individual MADs or subsystems. They define the precise "how."
    *   **Key Contents:** Detailed API specifications for Action Engine tools, internal architectural choices, and module designs.

*   **`docs/thesis/`**:
    *   **Purpose:** A distinct body of academic work related to the Joshua project, separate from the core engineering documentation.
    *   **Key Contents:** Research papers (J-series, M-series, C-series).

---

## 2. Reading Guide: Getting Started

For new team members or those seeking a comprehensive understanding of the Joshua project, we recommend the following reading order:

1.  **Start Here:** Read this `README.md` to understand the overall documentation structure.
2.  **Strategic Vision:** Read `docs/architecture/00_Joshua_System_Roadmap.md` (once created by Claude) to grasp the project's high-level goals and evolutionary path.
3.  **Core Architecture:** Read `docs/architecture/00_MAD_Ingress_Architecture.md` to understand how MADs communicate internally and externally.
4.  **Architectural Decisions:** Browse `docs/architecture/adr/` to understand the rationale behind key architectural choices.
5.  **MAD Development Process:** Read `docs/architecture/MAD_Development_Lifecycle.md` to understand how MADs are brought from concept to code.
6.  **Specific MADs:** Once you have the foundational understanding, dive into `docs/requirements/` for high-level MAD descriptions, and then `docs/design/` for their detailed technical blueprints.

---

## 3. Related Directories (Outside `docs/`)

*   **`/mnt/projects/Joshua/processes/`**: Contains runtime process definitions for the deployed Joshua ecosystem (e.g., how specific operational workflows are executed by MADs). This is distinct from development processes.
*   **`/mnt/projects/Joshua/lib/`**: Contains shared Python libraries (e.g., `Joshua_Communicator`, `joshua_thought_engine`) used across MADs.

---
