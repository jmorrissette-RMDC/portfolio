# ADR-032: Fully Flow-Based Architecture

**Status:** Accepted
**Date:** 2025-12-21
**Deciders:** System Architect
**Supersedes:** ADR-031

## Context and Problem Statement

ADR-030 introduced Langflow for visual flow design, and ADR-031 attempted to scope it to the Imperator component only. However, both ADRs maintained the assumption that a "programmatic orchestrator" in Python code would coordinate the overall MAD logic.

Through extensive architectural discussion, a more elegant and powerful model emerged: **eliminate programmatic orchestration entirely** and adopt a **fully flow-based architecture** where nearly all MAD logic is defined in Langflow `.json` flows, not imperative Python code.

This represents a fundamental shift from "code with some flows" to "flows with minimal interface code."

## Decision

We will adopt a **fully flow-based architecture** where:

1. **All logic is defined in Langflow flows** - reactive flows (triggered by messages/events) and proactive flows (scheduled/periodic tasks)
2. **MCP tools are flow triggers** - each exposed MCP tool simply kicks off a corresponding flow
3. **No programmatic orchestrators** - there is no Python code orchestrating "first do A, then B, then C"
4. **Minimal interface code** - Python libraries exist only as thin interfaces to external systems or as custom nodes for flows

### Architectural Structure

```
MAD (container)
├── Action Engine (AE) - "The Hands"
│   ├── Joshua_Flow_Runner - Executes .json flows (headless Langflow engine)
│   ├── joshua_flow_scheduler - Triggers scheduled/periodic flows
│   └── Joshua_Communicator - Network I/O, triggers routing flows
│
└── Thought Engine (TE) - "The Brain"
    ├── joshua_thought_engine - Master library (dependency aggregator, NO root code)
    └── PCP Component Libraries (provide nodes for flows):
        ├── joshua_dtr - Dynamic Triage Router nodes (decides which flow to call)
        ├── joshua_lppm - Learning Prompt Pattern Manager nodes
        ├── joshua_imperator - Core Deliberative Reasoning nodes
        ├── joshua_cet - Cognitive Execution Tracker nodes
        └── joshua_crs - Cognitive Reflection System nodes
```

### Key Principles

**1. Flows Are Distributed**

Flows are not centrally orchestrated. They are triggered by various components:
- **Incoming message** → `Joshua_Communicator` triggers `communications_routing_flow.json`
- **Scheduled task** → `joshua_flow_scheduler` triggers `periodic_review_flow.json`
- **Tool call** → MCP tool handler triggers corresponding flow

**2. Action Engine Contains Flow Execution**

`Joshua_Flow_Runner` (part of the Action Engine) is responsible for loading and executing `.json` flows. This is an "action" the MAD performs, hence it belongs in the AE. It is the headless Langflow execution engine that MAD servers use directly.

**3. Thought Engine Decides Flow Selection**

The Thought Engine's component libraries (particularly `joshua_dtr` for triage/routing) decide which flow is most appropriate to handle inputs. This decision-making is distributed throughout the flow graph, not centralized in any single component. Both reactive (message-triggered) and proactive (scheduled) thinking are supported.

**Important:** The `joshua_thought_engine` master library contains NO implementation code. It is purely a dependency aggregator that declares dependencies on PCP component libraries. Decision logic lives in those components (DTR, LPPM, etc.), not in the master library.

**4. PCP Components Provide Flow Nodes**

The PCP component libraries (joshua_imperator, joshua_dtr, etc.) are **not** orchestrators. They provide custom Python nodes that can be used **within** flows. A flow might call an Imperator node, then a CET node, then back to an Imperator node - the flow defines the logic, not the libraries.

**5. Progressive Cognitive Pipeline Is A Flow Pattern**

The PCP (DTR → LPPM → CET → Imperator → CRS) is **one possible flow pattern**, not a hardcoded orchestration. Different flows can use different patterns. Some flows might skip tiers, repeat tiers, or use a completely different pattern.

**6. LLM Access and Failover Strategy**

Flows make direct MCP calls to Fiedler for LLM access. Each flow implements its own failover strategy when Fiedler is unavailable:
- Primary path: MCP calls to Fiedler MAD (`mcp__fiedler__fiedler_send`)
- Fallback path: Direct calls to local Ollama instance (`http://localhost:11434`)
- **Flow-controlled degradation**: Each flow decides whether to fail, degrade, queue, or use alternative strategies
- Shared resource: Single Ollama instance per MAD container serves all flows

**No centralized LLM client**: Removed from architecture to give flows agency over degradation decisions.

See **ADR-029: Local Ollama Failover Architecture** for detailed rationale and implementation patterns.

### Types of Flows

**Reactive Flows** (triggered by external events):
- `communications_routing_flow.json` - Routes incoming messages to appropriate handlers
- `tool_execution_flow.json` - Handles MCP tool calls
- `user_prompt_flow.json` - Processes natural language requests

**Proactive Flows** (scheduled/periodic):
- `periodic_review_flow.json` - Regular self-assessment
- `metric_collection_flow.json` - Gather performance data
- `learning_update_flow.json` - LPPM pattern refinement

**Internal Process Flows**:
- `pcp_full_deliberation_flow.json` - Full DTR→LPPM→CET→Imperator→CRS pipeline
- `quick_triage_flow.json` - Simplified fast-path reasoning
- `cross_mad_coordination_flow.json` - Orchestrating multi-MAD operations

### Flow Execution Mechanism

When a flow needs to run:

1. **Trigger source** (Communicator, Scheduler, or Thought Engine) determines a flow is needed
2. **Trigger source** calls `flow_runner.execute(flow_name, input_data)`
3. **Joshua_Flow_Runner** loads the corresponding `flow_name.json` from the MAD's flows directory
4. **Joshua_Flow_Runner** executes the flow graph
5. **Flow** calls custom component nodes (from PCP libraries, external APIs, etc.) as needed
6. **Joshua_Flow_Runner** returns result to the trigger source

## Consequences

### Positive

**Reduced Code Complexity:**
- Eliminates complex imperative orchestration logic
- Flow graphs are easier to understand visually than nested Python code
- Reduces surface area for bugs in core logic

**Enhanced Metaprogramming:**
- MADs can safely modify their own flows (low risk)
- Hopper can optimize flows without deep code analysis
- Flows are declarative artifacts easily versioned in Git

**Flexible Reasoning Patterns:**
- Not locked into a single PCP sequence
- Different contexts can use different flow patterns
- Easy to experiment with new reasoning approaches

**Better Observability:**
- Flow execution paths are self-documenting
- Hamilton can trace exact flow graphs executed
- Debugging is visual, not buried in stack traces

**Parallelization Opportunities:**
- Flows can define parallel execution paths
- Independent flow branches can run concurrently
- Natural fit for async execution model

### Negative

**Debugging Complexity:**
- Visual flow debugging is harder than traditional Python debuggers
- Stack traces less meaningful when logic is in graph nodes
- Requires Langflow UI access for effective debugging

**Learning Curve:**
- Developers must learn Langflow paradigm
- Not all developers comfortable with flow-based programming
- Different mental model from traditional code

**Flow Explosion Risk:**
- Complex logic can create sprawling flow graphs
- Need discipline to use composite nodes (flows-within-flows)
- Potential for "spaghetti diagrams" if not well-organized

**External Dependency:**
- Relies on Joshua_Flow_Runner (wrapper around Langflow internals)
- Langflow updates could break flows
- Need strict version pinning for stability

## Implementation Notes

**Code-to-Flow Migration:**
- Existing MADs will gradually migrate logic from Python to flows
- High-value, stable logic migrates first
- Critical performance paths may remain in optimized Python nodes

**Flow Organization:**
- Each MAD has a `flows/` directory containing its `.json` flows
- Composite nodes (reusable sub-flows) encouraged for common patterns
- Flow naming convention: `{purpose}_{type}_flow.json` (e.g., `user_prompt_reactive_flow.json`)

**Custom Node Development:**
- PCP component libraries provide custom nodes via `components/` directories
- Custom nodes are thin wrappers around core logic
- Custom nodes must be stateless and idempotent where possible

### MAD Physical Structure and Composition Pattern

**Critical Architectural Principle:** The MAD is a **thin composition layer**. The Action Engine and Thought Engine shown in the logical architecture diagram are **not directories** - they are **imported libraries**.

#### What the MAD Contains

The MAD repository contains only:
1. **Minimal wiring code** (`server_joshua.py`)
2. **MAD-specific flows** (`.json` files in `flows/`)
3. **Test flows** (`.json` files in `test_flows/`)
4. **Configuration** (persona, flow parameters)

#### What the MAD Does NOT Contain

- ❌ Node implementations (those live in libraries: joshua_core, joshua_imperator, etc.)
- ❌ Flow execution engine (imported from Joshua_Flow_Runner)
- ❌ Communication infrastructure (imported from Joshua_Communicator)
- ❌ PCP cognitive components (imported from joshua_thought_engine, joshua_dtr, etc.)

#### Standard MAD Directory Structure

```
mad_name/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt          # Declares library dependencies
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

#### Composition Pattern: requirements.txt

The MAD's `requirements.txt` declares all imported functionality:

```txt
# Action Engine Libraries (imported, not implemented in MAD)
joshua_flow_runner>=0.7.0
joshua_communicator>=0.7.0
joshua_flow_scheduler>=0.7.0

# Thought Engine Libraries (imported, not implemented in MAD)
joshua_thought_engine>=0.7.0  # Master library (dependency aggregator)

# Node Libraries (imported, available to flows)
joshua_core>=1.0.0            # Universal nodes (LLMCLINode, flow control, utilities)
joshua_gemini>=1.0.0          # Provider-specific nodes (if needed)
joshua_ffmpeg>=1.0.0          # Domain-specific nodes (if needed)
```

#### Testing Model

- **Unit tests for nodes** → Live in node libraries (joshua_core, joshua_imperator, etc.)
- **Integration tests for flows** → Live in MAD's `test_flows/` directory
- **Flow test execution** → Performed by flow executor (typically orchestrated by Deming MAD)

**Result:** The MAD is extremely lightweight - typically < 100 lines of Python code in `server_joshua.py`, with all logic defined declaratively in `.json` flows.

## Implementation Strategy: CLI-First Approach (2025-12-21)

While this ADR establishes the flow-based architecture as the foundation, **ADR-034: CLI-First LLM Integration Strategy** defines the initial implementation approach.

**Key Implementation Decisions:**

- **Custom nodes not built initially**: PCP component libraries (joshua_imperator, etc.) provide specifications, not implementations
- **CLI wrappers in Fiedler**: Fiedler exposes LLM provider CLIs (Claude Code, Gemini CLI, Aider, Grok, Codex) via MCP tools
- **Flows orchestrate CLI calls**: Flows compose `claude_session`, `gemini_session`, `aider_session` etc. instead of custom nodes
- **Provider innovation leverage**: MADs benefit from continuous CLI improvements without maintenance burden

**Rationale:**
LLM providers continuously improve their CLIs through competitive innovation. Building custom nodes would duplicate capabilities providers do better, diverting resources from Joshua's unique value proposition (multi-MAD orchestration).

**Example Flow (CLI-based):**
```json
{
  "nodes": [
    {
      "id": "chat_1",
      "type": "MCPToolNode",
      "tool": "mcp__fiedler__claude_session",
      "inputs": {
        "message": "{{input.user_message}}",
        "session_id": "{{input.session_id}}",
        "auto_compress": true
      }
    }
  ]
}
```

This provides all ChatSessionNode capabilities (session management, context compression, tool calling) without custom implementation.

**See ADR-034 for complete implementation details.**

---

## Related Decisions

- **ADR-029**: Local Ollama Failover Architecture - Defines LLM failover strategy (still valid for CLI degradation)
- **ADR-030**: Langflow Internal Architecture - Introduced Langflow, established Joshua_Flow_Runner
- **ADR-031**: Modular PCP Component Libraries - Defines PCP component structure (implementation via CLIs per ADR-034)
- **ADR-031 (superseded)**: Modular PCP and Langflow Imperator - **SUPERSEDED** by this ADR (incorrectly scoped Langflow to Imperator only)
- **ADR-033**: Metaprogramming via Hopper-Orchestrated Optimization - Depends on this flow-based model for safe self-modification
- **ADR-034**: CLI-First LLM Integration Strategy - Defines implementation approach for this architecture

## References

- Langflow Documentation: https://docs.langflow.org/
- Architectural Discussion Transcript: See `ADR-032_Appendix_A_Verbatim_Transcript.md`
