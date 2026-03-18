# Bush Requirements

- **Role**: Jupyter Notebook Automation
- **Version**: V7.0
- **Home**: `mads/bush/`

---

## 1. Overview

-   **Purpose**: Bush is the authoritative **Notebook Automation Engine** for the Joshua ecosystem. Its purpose is to programmatically replicate the iterative workflow of a data scientist using a Jupyter/Colab notebook.
-   **V7.0 Scope Definition**: As a V7.0 MAD, Bush provides a comprehensive and cognitive suite of tools to create, modify, execute, and convert notebooks, enabling fully autonomous data science and experimentation workflows.

---

## 2. Tool Exposure Model

This MAD follows the Direct Tool Exposure architecture (ADR-023). Its public tools are exposed directly on its MCP server and are discoverable via the Rogers registry. Any incoming communication that is not a valid MCP call for an exposed tool is routed to the Thought Engine for conversational processing (e.g., "Design an experiment to analyze this dataset and create a notebook for it.").

> **Note on Tool List:** The tools listed in this document are a *provisional set* based on the MAD's high-level requirements. The final, authoritative list of tools, their specific parameters, and their return schemas will be defined in a dedicated Design Document prior to implementation.

---

## 3. Public Action Engine Tools

### `bush_create_notebook`
- **Description:** Creates a new, empty Jupyter notebook file (`.ipynb`).
- **Input Schema:**
    - `path` (string, required): The absolute path where the new notebook file should be created.
- **Output Schema:** `{"status": "success", "path": "/path/to/notebook.ipynb"}`

### `bush_add_code_cell`
- **Description:** Adds a new code cell to an existing notebook.
- **Input Schema:**
    - `path` (string, required): The path to the target `.ipynb` file.
    - `source` (string, required): A string containing the Python code for the new cell.
- **Output Schema:** `{"status": "success"}`

### `bush_add_markdown_cell`
- **Description:** Adds a new markdown cell to an existing notebook.
- **Input Schema:**
    - `path` (string, required): The path to the target `.ipynb` file.
    - `source` (string, required): A string containing the markdown text for the new cell.
- **Output Schema:** `{"status": "success"}`

### `bush_execute_notebook`
- **Description:** Executes all code cells in a notebook from top to bottom, updating the file in-place with all outputs.
- **Input Schema:**
    - `path` (string, required): The path to the `.ipynb` file to execute.
    - `dependencies` (array[string], optional): A list of pip packages to install on-the-fly before execution.
- **Output Schema:** `{"status": "complete" | "failed", "execution_time_seconds": 123.45, "errors": ["..."]}`

### `bush_convert_notebook`
- **Description:** Converts an executed notebook into a distributable format.
- **Input Schema:**
    - `path` (string, required): The path to the source `.ipynb` file.
    - `format` (string, required): The target format. Supported: `"html"`, `"pdf"`, `"slides_html"`.
    - `output_path` (string, required): The absolute path to save the converted file.
- **Output Schema:** `{"status": "success", "path": "/path/to/converted_file.html"}`

### `bush_fetch_data`
- **Description:** A utility tool to download a file from a URL into the local workspace.
- **Input Schema:**
    - `url` (string, required): The URL of the file to download.
    - `local_path` (string, required): The absolute local path to save the file.
- **Output Schema:** `{"status": "success", "path": "/path/to/local_file.csv", "size_bytes": 123456}`

---

## 4. Future Evolution (Post-V0)

Bush begins in Phase 1 (V0.1) as a basic notebook automation tool and evolves to V7.0 as the intelligent experimentation platform for the mature Joshua ecosystem.

*   **Phase 1 (Foundation / V0.1):** Bush exists as a notebook automation engine with a deterministic Action Engine only (no Thought Engine). It provides six core tools for creating, modifying, executing, and converting Jupyter notebooks programmatically. Bush operates via the `Joshua_Communicator` protocol, enabling basic notebook workflows for early data science activities.
*   **Phase 6 (Expansion / V7.0):** Bush is upgraded to V7.0 as a fully-capable MAD with complete PCP (DTR, LPPM, CET, CRS), pure Kafka conversation bus integration, and eMAD awareness. Bush's CET enables complex multi-notebook workflows with intelligent orchestration, while CRS learns from experiment patterns to suggest optimal analysis approaches. Bush coordinates with Lovelace (data science), Horace (dataset management), Bass/Muybridge (visualization), and Brin/Gates (cloud notebook platforms). Bush becomes the central notebook intelligence hub, capable of autonomous experiment design, execution, and analysis interpretation aligned with Joshua's research objectives.
*   **Post-V7.0 Enhancements:** Future evolution includes collaborative notebook environments, real-time kernel management across distributed resources, automated experiment tracking and versioning, reproducibility verification, and integration with academic publication workflows.
