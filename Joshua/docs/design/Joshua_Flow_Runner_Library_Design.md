# `Joshua_Flow_Runner` Library Design

- **Role**: Headless Langflow Execution Engine
- **Version**: 0.1
- **Home**: `lib/joshua_flow_runner/`

---

## 1. Overview

This document provides the technical design for the `Joshua_Flow_Runner` library, a headless execution engine for `flow.json` files. It implements the requirements specified in `Joshua_Flow_Runner_Library_Requirements.md`. The core of this design is a `JoshuaFlowRunner` class that wraps the internal programmatic APIs of the `langflow` library to provide a simple and stable interface for the Joshua ecosystem.

---

## 2. Core Components & Class Design

The library will provide a single primary class, `JoshuaFlowRunner`.

### 2.1 `JoshuaFlowRunner` Class

```python
# Conceptual implementation in lib/joshua_flow_runner/runner.py

import os
import importlib.util
from typing import Dict, Any

from joshua_communicator.logger import IntegratedLogger
# NOTE: These are hypothetical imports from Langflow's internal API.
# The actual paths will be determined during implementation.
from langflow.processing.process import load_flow_from_json
from langflow.graph import Graph

from .errors import FlowRunnerError, FlowLoadError, ComponentLoadError

class JoshuaFlowRunner:
    """
    A headless runner for executing Langflow JSON definitions.
    """
    def __init__(self, flow_json_path: str, components_path: str, logger: IntegratedLogger):
        self.logger = logger
        self.flow_json_path = flow_json_path
        self.components_path = components_path
        self.executable_graph: Graph = None

        self._load_and_build_graph()

    def _load_custom_components(self) -> None:
        """
        Discovers and dynamically loads custom Python components.
        This function will iterate through .py files in the components_path,
        import them as modules, and rely on Langflow's internal component
        registry to make them available to the graph builder.
        """
        self.logger.info(f"Loading custom components from: {self.components_path}")
        if not os.path.isdir(self.components_path):
            self.logger.warning("Custom components path not found. No components loaded.")
            return

        for filename in os.listdir(self.components_path):
            if filename.endswith(".py") and not filename.startswith("__"):
                module_name = filename[:-3]
                file_path = os.path.join(self.components_path, filename)
                try:
                    spec = importlib.util.spec_from_file_location(module_name, file_path)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    self.logger.debug(f"Successfully loaded component module: {module_name}")
                except Exception as e:
                    raise ComponentLoadError(f"Failed to load component {file_path}: {e}")

    def _load_and_build_graph(self) -> None:
        """
        Loads the flow JSON and builds the executable Langflow graph object.
        This is the primary point of integration with Langflow's internal APIs.
        """
        try:
            # 1. Load any custom components first so they are available to the graph
            self._load_custom_components()

            # 2. Load the flow from the JSON file
            self.logger.info(f"Loading flow definition from: {self.flow_json_path}")
            with open(self.flow_json_path, 'r') as f:
                flow_data = json.load(f)

            # 3. Use Langflow's internal API to build the graph object.
            # This is the most critical and tightly-coupled part of the library.
            # The actual function call may differ based on Langflow's implementation.
            self.executable_graph = load_flow_from_json(flow_data)
            self.logger.info("Successfully built executable flow graph.")

        except FileNotFoundError:
            raise FlowLoadError(f"Flow JSON file not found at: {self.flow_json_path}")
        except json.JSONDecodeError:
            raise FlowLoadError("Failed to parse invalid JSON in flow file.")
        except Exception as e:
            # Catch-all for errors from Langflow's internal APIs
            raise FlowRunnerError(f"An unexpected error occurred building the graph: {e}")

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes the loaded flow with the given input data.
        """
        if not self.executable_graph:
            raise FlowRunnerError("Cannot execute, graph is not built.")

        self.logger.info("Executing flow...")
        try:
            # The actual execution call will depend on the Langflow Graph API
            result = await self.executable_graph.arun(input_data)
            self.logger.info("Flow execution completed successfully.")
            return {"status": "success", "result": result}
        except Exception as e:
            self.logger.error(f"Error during flow execution: {e}", exc_info=True)
            # Re-raise as a standard error for the harness to catch
            raise FlowExecutionError(f"An exception occurred in the flow: {e}")
```

## 3. Error Handling Strategy

The library will define custom exceptions (`FlowLoadError`, `ComponentLoadError`, `FlowExecutionError`) to provide clear diagnostics. The `JoshuaFlowRunner`'s public `execute` method will be wrapped in a `try...except` block within the consuming `joshua_thought_engine` harness to catch these exceptions and translate them into standard JSON-RPC error responses.

## 4. Example Usage (in `joshua_thought_engine` harness)

This shows how the refactored `ThoughtEngine` would use the new `JoshuaFlowRunner`.

```python
# In lib/joshua_thought_engine/engine.py (Refactored)

from joshua_flow_runner import JoshuaFlowRunner, FlowRunnerError

class ThoughtEngine:
    def __init__(self, communicator, config: dict):
        self.communicator = communicator
        self.log = communicator.log
        self.config = config
        self.flow_runner: JoshuaFlowRunner = None

    async def initialize(self):
        """Initializes the ThoughtEngine by setting up the FlowRunner."""
        self.log.info("Initializing ThoughtEngine harness...")
        try:
            self.flow_runner = JoshuaFlowRunner(
                flow_json_path=self.config["flow_json_path"],
                components_path=self.config["components_path"],
                logger=self.log
            )
        except FlowRunnerError as e:
            self.log.error(f"Failed to initialize JoshuaFlowRunner: {e}", exc_info=True)
            self.flow_runner = None # Ensure it's None on failure

    async def process_conversational_prompt(self, prompt: str) -> Dict[str, Any]:
        if not self.flow_runner:
            return {"error": "ThoughtEngine is not initialized or failed to load flow."}

        input_data = {"input": prompt} # Or whatever the flow's input schema is
        try:
            return await self.flow_runner.execute(input_data)
        except FlowExecutionError as e:
            return {"error": "An error occurred during agentic reasoning.", "details": str(e)}
```

## 5. Key Dependencies & Versioning

-   **`langflow`**: The core dependency. The `pyproject.toml` for `joshua_flow_runner` **must** pin this to an exact version (e.g., `langflow == "1.1.0"`).
-   **`langchain`**: A transitive dependency of `langflow`, but it should also be pinned to ensure compatibility.
-   **`joshua_communicator`**: For logging.
