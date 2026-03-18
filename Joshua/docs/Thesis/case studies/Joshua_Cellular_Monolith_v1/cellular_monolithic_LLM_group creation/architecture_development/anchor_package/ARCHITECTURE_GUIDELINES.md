## 1. Overview

This document provides the essential guidelines and standards for creating MAD architecture and requirements documents. Adherence to these guidelines is mandatory for all synthesis tasks. The goal is to produce documents that are clear, consistent, unambiguous, and directly implementable by a competent software engineer. These guidelines apply to your own synthesis process and will be used by the LLM review panel to evaluate your work.

---

## 2. Standardized MAD Architecture Template

All MAD requirement documents, from V1 to V4, must follow this standardized template. This ensures consistency and makes it easy for reviewers and developers to locate specific information.

```markdown
# [MAD_NAME] V[X] Requirements

## 1. Overview
- **Purpose and Role:** A concise statement of this MAD's purpose and its role within the Joshua ecosystem.
- **New in this Version:** (For V2+ only) A bulleted list summarizing the key new capabilities, components, or improvements being introduced in this version.

## 2. Thinking Engine
- **Imperator Configuration (V1+):** Details on the base prompt, specialized knowledge, and core reasoning tasks for the Imperator LLM.
- **LPPM Integration (V2+):** Describes the specific prose-to-process patterns the LPPM will be trained to recognize and automate.
- **DTR Integration (V3+):** Defines the classes of messages (deterministic, fixed, prose) the DTR will be trained to route, including specific patterns or keywords.
- **CET Integration (V4+):** Specifies the context sources the CET will draw from (e.g., specific archived conversation types, external documentation) and the goals of its context engineering.
- **Consulting LLM Usage Patterns:** Describes scenarios where this MAD would request consulting LLMs from Fiedler and the types of specialists it would need.

## 3. Action Engine
- **MCP Server Capabilities:** A high-level description of the MAD's internal control plane.
- **Tools Exposed:** A definitive list of the tools (functions, capabilities) this MAD exposes to other MADs via conversation. Use the specified Interface Definition Format.
- **External System Integrations:** Details of any integrations with systems outside the MAD itself (e.g., file systems, databases, web APIs).
- **Internal Operations:** Description of internal processes, such as background monitoring tasks or data processing pipelines.

## 4. Interfaces
- **Conversation Participation Patterns:** Describes the types of conversations this MAD will initiate, join, and listen to.
- **Dependencies on Other MADs:** An explicit list of other MADs this MAD depends on and the specific tools it uses from them.
- **Data Contracts:** Formal definitions for any complex data structures passed to or from this MAD's tools. Use YAML or JSON.

## 5. Data Management
- **Data Ownership:** What data is this MAD the "source of truth" for?
- **Storage Requirements:** Specific storage needs (e.g., PostgreSQL tables, file system directories, in-memory caches).
- **Conversation Patterns:** Examples of typical request/response conversations this MAD will engage in.

## 6. Deployment
- **Container Requirements:** Any specific OS packages, libraries, or resource requirements (CPU, RAM) for the Docker container.
- **Configuration:** A list of all required configuration parameters (e.g., database URLs, API keys) and how they are provided (e.g., environment variables).
- **Monitoring/Health Checks:** Specific metrics or endpoints that should be monitored to determine the health of the MAD.

## 7. Testing Strategy
- **Unit Test Coverage:** Key areas of the Action Engine that require high unit test coverage.
- **Integration Test Scenarios:** Scenarios for testing this MAD's interaction with its key dependencies (e.g., "Test that Hopper can successfully request a file from Horace and receive its contents").

## 8. Example Workflows
- Provide 2-3 concrete, step-by-step examples of the MAD in action, from receiving a request to completing a task. Show the conversational messages exchanged.
```

---

## 3. "Reference, Don't Repeat" Strategy

To maintain clarity and reduce token consumption in future syntheses, we will employ a delta-based approach for versions V2 and above.

*   **V1 Synthesis:** The V1 document for a MAD must be complete and comprehensive, using the full template.
*   **V2 Synthesis:** The V2 document should begin with the statement: *"This document assumes the approved V1 architecture as a baseline. It describes ONLY the deltas required to add V2 capabilities."* The document should then only detail the changes and additions, primarily in the "Thinking Engine" (LPPM), "Action Engine" (new automated processes), and "Example Workflows" sections.
*   **V3 Synthesis:** Begins with: *"Assume V1+V2 approved. Describe ONLY deltas for DTR addition."*
*   **V4 Synthesis:** Begins with: *"Assume V1+V2+V3 approved. Describe ONLY deltas for CET addition."*

This strategy ensures that each version's requirements are focused and builds cleanly upon the previously approved foundation.

---

## 4. Interface Definition Format

All tools exposed by a MAD's Action Engine must be defined using a structured YAML format within a code block. This is unambiguous and machine-parsable.

**Example:**

```yaml
# Tool definitions for Horace V1

- tool: read_file
  description: "Reads the entire content of a file from the NAS."
  parameters:
    - name: path
      type: string
      required: true
      description: "The absolute path to the file on the NAS."
  returns:
    - name: content
      type: string
      description: "The UTF-8 encoded content of the file."
    - name: error
      type: string
      description: "An error message if the file could not be read."

- tool: list_directory
  description: "Lists the contents of a directory."
  parameters:
    - name: path
      type: string
      required: true
      description: "The absolute path to the directory."
  returns:
    - name: items
      type: list[object]
      description: "A list of files and directories."
      schema:
        - name: name
          type: string
        - name: type
          type: "file|directory"
        - name: size_bytes
          type: integer
```

---

## 5. "Deployable" Definition

A MAD architecture document is considered **"deployable"** if it meets the following criteria. This is the quality standard for all synthesized outputs.

*   **Sufficient Detail:** A competent senior software engineer can take the document and implement the MAD from start to finish without needing to ask for clarification on core behavior, dependencies, or interfaces.
*   **Unambiguous Contracts:** All interfaces and data contracts are explicitly defined. There is no ambiguity about what data is required or what will be returned.
*   **Complete Dependencies:** All dependencies on other MADs or infrastructure services are clearly listed.
*   **Concrete Examples:** The example workflows are specific and illustrate the primary use cases of the MAD, clarifying any complex interactions.
*   **Rationale Included:** Where non-obvious design choices are made, a brief rationale is provided.

---

## 6. Clarity Standards

To meet the "deployable" standard, all documents must adhere to these clarity principles:

*   **Be Unambiguous:** Avoid vague terms. Instead of "handles files," specify "provides tools to read, write, and delete files at specified paths."
*   **Favor Concrete over Abstract:** Instead of "improves efficiency," state "adds a DTR to route deterministic commands directly to the Action Engine, bypassing the Imperator."
*   **Use Examples for Complexity:** For any multi-step or non-trivial interaction, provide a concise example of the conversational exchange.
*   **Explain Your Rationale:** Briefly explain *why* a decision was made. For example, "Horace is a persistent MAD because file system access must be highly available to all other MADs at all times."

---
---