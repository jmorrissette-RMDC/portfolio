# `Joshua_Flow_Runner` Library Requirements

- **Role**: Headless Langflow Execution Engine
- **Version**: 0.1
- **Home**: `lib/joshua_flow_runner/`

---

## 1. Overview

-   **Purpose**: This document specifies the requirements for the `joshua_flow_runner` shared library. This library provides a standardized, lightweight, and headless runtime engine for executing the logic defined in Langflow `flow.json` files. It is the core execution component of the Langflow-based Thought Engine architecture (ADR-030).
-   **Scope Definition**: To create a purely programmatic interface that can load a `flow.json` artifact and its associated custom Python components, execute the defined logic, and return a result, without exposing any UI or web server.

---

## 2. Architectural Principles

-   **Headless Execution**: The library **must not** instantiate or expose any web server or user interface. Its operation must be entirely programmatic.
-   **Wrapper, Not a Rewrite**: This library is an abstraction layer, or "wrapper," over the internal, programmatic APIs of the `langflow` Python package. It is not a re-implementation of the Langflow engine.
-   **Strict Version Pinning**: The library's dependencies, particularly `langflow` and `langchain`, **must** be strictly pinned to specific versions to ensure a stable and reproducible runtime. This is critical due to the reliance on non-public, internal APIs.
-   **Standardized Interface**: The library must expose a simple and consistent API to its primary consumer, the `joshua_thought_engine` harness library.

---

## 3. Functional Requirements

-   **Flow Loading**: The `FlowRunner` class must be able to load a `flow.json` file from a specified file path. It must validate that the file is well-formed JSON.
-   **Custom Component Loading**: The library must be able to discover, dynamically import, and register custom Python components from a specified directory path. This allows MADs to have unique, flow-specific logic.
-   **Flow Execution**:
    -   The library must provide a primary `async execute` method.
    -   This method must accept a dictionary as input, which will be passed to the input node of the Langflow graph.
    -   It must return a dictionary containing the final output from the graph's designated output node.
-   **Error Handling**: The library must gracefully handle and report errors, including:
    -   `FlowLoadError`: If the `flow.json` file is missing, invalid, or cannot be parsed.
    -   `ComponentLoadError`: If a custom component cannot be imported or is malformed.
    -   `FlowExecutionError`: If an error occurs during the execution of the Langflow graph.
    -   Error responses must be structured and informative.
-   **Logging Integration**: The library must accept an instance of the `joshua_communicator`'s `IntegratedLogger` and use it for all diagnostic output.
