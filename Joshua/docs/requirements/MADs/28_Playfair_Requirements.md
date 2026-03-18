# Playfair Requirements

- **Role**: Data Visualization
- **Version**: V7.0
- **Home**: `mads/playfair/`

---

## 1. Overview

-   **Purpose**: Playfair is the specialist MAD for generating charts, diagrams, and other visualizations from data or descriptive prompts.
-   **V7.0 Scope Definition**: As a V7.0 MAD, Playfair provides a comprehensive and cognitive suite of tools for data visualization, capable of autonomously generating complex charts, diagrams, and interactive dashboards, with an Imperator that translates natural language requests into optimal visual encodings.

---

## 2. Tool Exposure Model

This MAD follows the Direct Tool Exposure architecture (ADR-023). Its public tools are exposed directly on its MCP server and are discoverable via the Rogers registry. Any incoming communication that is not a valid MCP call for an exposed tool is routed to the Thought Engine for conversational processing (e.g., "Create a bar chart showing user growth per quarter from this data.").

> **Note on Tool List:** The tools listed in this document are a *provisional set* based on the MAD's high-level requirements. The final, authoritative list of tools, their specific parameters, and their return schemas will be defined in a dedicated Design Document prior to implementation.

---

## 3. Public Action Engine Tools

### `playfair_create_chart`
- **Description:** Generates a static image of a chart (e.g., bar, line, scatter) from structured data.
- **Input Schema:**
    - `chart_type` (string, required): The type of chart (e.g., "bar", "line", "scatter", "pie").
    - `data` (dict, required): The structured data for the chart (e.g., `{"x_axis": [1,2,3], "y_axis": [10,20,30]}`).
    - `output_path` (string, required): The path to save the generated image file (e.g., `/mnt/irina_storage/charts/user_growth.png`).
    - `options` (dict, optional): Chart-specific options (e.g., `{"title": "User Growth", "x_label": "Quarter"}`).
- **Output Schema:** `{"status": "success", "output_path": "/path/to/chart.png"}`

### `playfair_create_diagram`
- **Description:** Generates a static image of a diagram (e.g., flowchart, sequence diagram, network graph) from a textual specification (e.g., Mermaid syntax, Graphviz DOT).
- **Input Schema:**
    - `diagram_type` (string, required): The type of diagram (e.g., "flowchart", "sequence", "network").
    - `spec_format` (string, required): The format of the diagram specification (e.g., "mermaid", "dot").
    - `spec_content` (string, required): The textual specification of the diagram.
    - `output_path` (string, required): The path to save the generated image file.
- **Output Schema:** `{"status": "success", "output_path": "/path/to/diagram.svg"}`

### `playfair_create_dashboard`
- **Description:** Generates a multi-panel dashboard image by combining multiple charts and diagrams.
- **Input Schema:**
    - `panels` (array[dict], required): A list of panels, each referencing a chart/diagram tool call and its output.
    - `layout` (dict, required): Specifies the layout of the panels (e.g., `{"rows": 2, "cols": 2}`).
    - `output_path` (string, required): The path to save the generated dashboard image.
- **Output Schema:** `{"status": "success", "output_path": "/path/to/dashboard.png"}`

---

## 4. Future Evolution (Post-V0)

Playfair begins in Phase 1 (V0.1) as a basic visualization tool and evolves to V7.0 as the intelligent visualization platform for the mature Joshua ecosystem.

*   **Phase 6 (Expansion / V7.0):** Playfair is upgraded to V7.0 as a fully-capable MAD with complete PCP (DTR, LPPM, CET, CRS), pure Kafka conversation bus integration, and eMAD awareness. As the visualization specialist, Playfair's CET enables complex multi-panel dashboards and animated visualizations, while CRS learns optimal chart types and visual encodings from usage patterns. Playfair coordinates with Bass (image generation), Lovelace (data science visualizations), Knuth (documentation diagrams), Muybridge (video visualization), and domain-specific MADs.
*   **Post-V7.0 Enhancements:** Future evolution includes interactive real-time dashboards, accessibility optimization (color blindness, screen readers), 3D visualization capabilities, augmented reality (AR) visualization output, automatic data story generation, and compelling visual narratives aligned with Joshua's strategic communication needs.

---