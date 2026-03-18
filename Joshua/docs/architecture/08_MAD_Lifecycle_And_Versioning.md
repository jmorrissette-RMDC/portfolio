# MAD Lifecycle, Versioning, and Code Structure

**Version**: 1.0 (Unified)
**Status:** Authoritative

---

## 1. The MAD Development Lifecycle

All MADs, whether new or undergoing a major revision, follow a formal, three-stage development lifecycle. This process ensures that development proceeds from a high-level vision to a concrete, vetted design before implementation begins, ensuring architectural consistency and quality.

### 1.1. Stage 1: Requirements Document

*   **Purpose:** To capture the high-level vision, role, and strategic purpose of the MAD.
*   **Content:** Role, scope, future evolution, and a *provisional* list of tools.
*   **Key Characteristic:** This document is about the **"what"** and the **"why."** It is intentionally not overly technical.
*   **Ownership:** Typically authored by the System Architect or a project lead. The existing 31 requirements documents in `Joshua/docs/requirements/` represent this stage.

### 1.2. Stage 2: Design Document

*   **Purpose:** To translate the high-level requirements into a concrete, technical blueprint for implementation. This is the most critical technical design phase.
*   **Content:** **Finalized and vetted tool API** (names, schemas), internal architecture, dependencies, and a test plan.
*   **Key Characteristic:** This document is about the **"how."** It is the definitive guide for the developer (whether human or AI like `Hopper`). The Action Engine's code should be a direct implementation of the tool APIs defined here.
*   **Ownership:** Authored by the lead developer or `Hopper`, with review and approval from the Architecture Team.

### 1.3. Stage 3: Implementation

*   **Purpose:** To write the code that brings the Design Document to life.
*   **Process:**
    1.  The developer (or `Hopper`) uses the Design Document as the single source of truth for implementation.
    2.  The Action Engine's MCP server is built to expose the exact tools specified in the Design Document.
    3.  The Thought Engine is implemented to use those internal tools.
    4.  Unit and integration tests are written according to the test plan.
*   **Key Characteristic:** This stage is purely about execution. All major design decisions should have already been made and resolved in Stage 2.

### 1.4. Workflow Diagram

```mermaid
graph TD
    A[Stage 1: Requirements Document<br><i>(What & Why)</i>] --> B{Review &<br>Approval};
    B --> C[Stage 2: Design Document<br><i>(How - Finalizes Tool API)</i>];
    C --> D{Review &<br>Approval};
    D --> E[Stage 3: Implementation<br><i>(Code & Tests)</i>];
    E --> F{Code Review &<br>CI/CD};
    F --> G[Deployment];
```

## 2. MAD Versioning Progression

This section defines the version progression for Joshua MADs, from early foundational stages through full autonomy and integration with the conversation bus. This progression applies to the internal sophistication and capabilities of each MAD.

### 2.1. Key Concept: V0 = Infrastructure, V1+ = Intelligence

**V0 versions build the STRUCTURE and INFRASTRUCTURE that V1+ brings to life with learning and autonomy.** This foundational development is guided by **ADR-032 (Fully Flow-Based Architecture)** and adheres to **ADR-028 (Core Coding Practice Standards)**.

-   **V0 (0.1 → 0.10)**: Building the house - architecture, frameworks, modern tooling, standardized structure. V0 MADs are increasingly sophisticated but remain fundamentally **deterministic**.
-   **V1.0+**: Living in the house - autonomous learning, emergent behaviors, true command-control. V1+ MADs stop being sophisticated programs and start becoming domain experts.

### 2.2. Version Progression Overview

| Version | Name | Focus | Key Characteristic | Autonomous? |
| :--- | :--- | :--- | :--- | :--- |
| **V0.1** | Foundation | Action Engine only | Pure tool provider. | No |
| **V0.5** | Reasoning | Add Thought Engine | Custom Python Imperator with basic LLM reasoning. | No |
| **V0.7** | Flow-Based | LangFlow Architecture | Logic in declarative flows, Imperator without RAG. | No |
| **V0.8** | Context-Aware | RAG Integration | Henson built, Imperator gains context retrieval. | No |
| **V0.10**| Federation | Quality Gate | Production-ready, fully tested, reliable in the V0 mesh. | No |
| **V1.0** | Conversation| Bus Migration | Migrated to the V1+ Conversation Bus (transport change only). | Yes (Initial) |
| **V5.0** | Cognition | Full PCP | Implements the full Progressive Cognitive Pipeline (DTR, LPPM, etc.). | Yes |
| **V7.0** | Autonomy | Joshua-Aware | Fully autonomous and integrated with system-wide strategic leadership. | Yes |

*Note: Not all MADs need every version step. A simple utility MAD might go from V0.1 -> V0.7 -> V0.10 if it requires no reasoning. However, all MADs must hit V0.7 (flow-based architecture) and V0.10 (quality gate) before V1.0.*

### 2.3. Migration Paths (V0 to V1+)

Migrating a MAD from V0 to V1 involves updating its `Joshua_Communicator` library to a `v1.x` version and changing its configuration to use Kafka brokers instead of direct WebSocket URLs. The core application logic (tool handlers, Thought Engine handler) remains largely unchanged because the `Joshua_Communicator`'s API is stable across versions and acts as a facade, as defined in **ADR-021 (Unified I/O and Logging Hub)**. This architectural approach, which simplifies changes to the underlying transport layer, is a direct application of the **12-Factor App methodology (ADR-027)**, specifically Factor IV (Backing Services) and Factor IX (Disposability).

## 3. Standard MAD Code Structure

All Joshua MADs **must** adhere to a standard code structure. This consistency is a core principle of the Cellular Monolith architecture, enabling faster development, easier maintenance, and shared tooling.

### 3.1. Directory Structure (V0.7+ Flow-Based Architecture)

**Per ADR-032**, the MAD is a **thin composition layer**. The Action Engine and Thought Engine are **imported libraries**, not directories within the MAD. The MAD contains only its specific flows, minimal wiring code, and configuration.

```
mad_name/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt          # Declares library dependencies (see Section 3.4)
├── README.md
├── mad_name/                 # Python package root
│   ├── __init__.py
│   ├── server_joshua.py      # Minimal glue: imports libraries, defines MCP tool → flow mappings
│   ├── flows/                # MAD-specific production flows (.json)
│   │   ├── main_flow.json
│   │   └── planning_flow.json
│   ├── test_flows/           # Test flows (executed by flow executor for validation)
│   │   ├── test_main_flow.json
│   │   └── test_planning_flow.json
│   └── config/               # MAD-specific configuration
│       ├── persona.md        # MAD identity/personality
│       └── flow_config.yaml  # Flow parameters, model preferences, etc.
```

**Key Principle:** The MAD is extremely lightweight - typically < 100 lines of Python code in `server_joshua.py`, with all logic defined declaratively in `.json` flows. See **ADR-032: MAD Physical Structure and Composition Pattern** for complete details.

### 3.2. `server_joshua.py` - Minimal Wiring Code

This file is the main entry point for the MAD. Its sole responsibility is to:
1.  Import shared libraries (`Joshua_Communicator`, `Joshua_Flow_Runner`)
2.  Define MCP tool → flow mappings
3.  Wire the libraries together
4.  Start the server

**The MAD contains NO business logic** - all logic is in flows.

```python
# server_joshua.py (Flow-Based Architecture - ADR-032)
import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv

from joshua_communicator import Communicator
from joshua_flow_runner import FlowRunner

load_dotenv()
mad_name = os.getenv("MAD_NAME", "my_mad")

# Define MCP tools as flow triggers
# Each tool name maps to the flow file that handles it
TOOL_FLOW_MAPPINGS = {
    "tool_one": "tool_one_flow.json",
    "tool_two": "tool_two_flow.json",
}

async def main():
    # Paths to MAD-specific flows and config
    flows_dir = Path(__file__).parent / "flows"
    config_dir = Path(__file__).parent / "config"

    # Configuration for the Communicator (V0 WebSocket transport)
    config_v0 = {"version": "v0", "port": 8000}

    # Instantiate the Flow Runner (Action Engine)
    flow_runner = FlowRunner(
        mad_name=mad_name,
        flows_directory=flows_dir,
        config_directory=config_dir
    )
    await flow_runner.initialize()

    # Instantiate the Communicator (Action Engine)
    communicator = Communicator(
        mad_name=mad_name,
        tool_flow_mappings=TOOL_FLOW_MAPPINGS,
        flow_runner=flow_runner,
        config=config_v0
    )

    try:
        # Start the communicator (starts MCP server, routes tools to flows)
        await communicator.start()
        await communicator.log.info(f"{mad_name} is online on port {config_v0['port']}.")
        await asyncio.Event().wait()
    except Exception as e:
        await communicator.log.error(f"{mad_name} failed to start: {e}")
    finally:
        await communicator.stop()

if __name__ == "__main__":
    asyncio.run(main())
```

**Key Points:**
- **< 50 lines of code** - The MAD is extremely minimal
- **No tool implementations** - Tools just map to flows
- **No business logic** - All logic in `.json` flow files
- **Pure composition** - Imports libraries, wires them together

### 3.3. Shared Libraries and Composition Pattern

**Per ADR-032**, MADs are thin composition layers. All functionality comes from imported libraries declared in `requirements.txt`.

#### Action Engine Libraries (Imported)

*   **`joshua_flow_runner`**: Headless Langflow execution engine. Loads and executes `.json` flow files.
*   **`joshua_communicator`**: MCP communication (client/server), ingress routing, integrated logging. Routes MCP tool calls to flows.
*   **`joshua_flow_scheduler`**: Triggers scheduled/periodic flows for proactive tasks.

#### Thought Engine Libraries (Imported)

*   **`joshua_thought_engine`**: Master library (dependency aggregator, **NO implementation code**). Declares dependencies on PCP component libraries.
*   **PCP Component Libraries** (provide custom nodes for flows):
    *   `joshua_dtr` - Dynamic Triage Router nodes
    *   `joshua_lppm` - Learning Prompt Pattern Manager nodes
    *   `joshua_imperator` - Core Deliberative Reasoning nodes
    *   `joshua_cet` - Cognitive Execution Tracker nodes
    *   `joshua_crs` - Cognitive Reflection System nodes

#### Node Libraries (Imported)

*   **`joshua_core`**: Universal nodes available to all MADs:
    *   `LLMCLINode` - Provider-agnostic LLM access (CLI-based per ADR-034)
    *   Flow control nodes (if/else, loop, switch)
    *   Utilities (string format, JSON parse, data transform)

*   **Provider-specific libraries** (opt-in):
    *   `joshua_gemini`, `joshua_claude`, `joshua_openai` - Vendor-specific features

*   **Domain-specific libraries** (opt-in):
    *   `joshua_ffmpeg`, `joshua_stable_diffusion`, `joshua_whisper` - Specialized compute

#### Example requirements.txt

```txt
# Action Engine Libraries
joshua_flow_runner>=0.7.0
joshua_communicator>=0.7.0
joshua_flow_scheduler>=0.7.0

# Thought Engine Libraries
joshua_thought_engine>=0.7.0  # Master library (dependency aggregator)

# Node Libraries
joshua_core>=1.0.0            # Universal nodes (LLMCLINode, flow control, utilities)
joshua_gemini>=1.0.0          # Provider-specific (if needed)
joshua_ffmpeg>=1.0.0          # Domain-specific (if needed)
```

**Result:** The MAD contains almost no code. It declares dependencies, maps tools to flows, and wires libraries together. All logic is in flows, all capabilities are in libraries.