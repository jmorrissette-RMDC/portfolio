# `joshua_thought_engine` Library Requirements

- **Role**: Master Library and Dependency Aggregator for Thought Engine Components
- **Version**: 0.7
- **Home**: `lib/joshua_thought_engine/`
- **ADR References**: ADR-031 (Modular PCP), ADR-032 (Flow-Based Architecture)

---

## 1. Overview

-   **Purpose**: This document specifies the requirements for the `joshua_thought_engine` master library. Following the adoption of a fully flow-based architecture (ADR-032) and modular PCP components (ADR-031), this library's role is fundamentally different from previous versions. It is **not an implementation library** but rather a **dependency aggregator** that provides a convenient way to install all Thought Engine component libraries as a single unit.
-   **Scope Definition**: To create a minimal package that declares dependencies on all PCP component libraries, provides documentation of the Thought Engine architecture, and enables easy installation of the complete Thought Engine stack.

---

## 2. Architectural Principles

-   **No Root Implementation Code**: The library contains **ZERO** implementation code. No classes, no functions, no reasoning logic. It is purely a packaging and dependency declaration artifact.
-   **Dependency Aggregator**: The library's sole purpose is to declare dependencies on PCP component libraries (joshua_dtr, joshua_lppm, joshua_cet, joshua_imperator, joshua_crs).
-   **Convenience Package**: Installing `joshua_thought_engine` should automatically install all required PCP component libraries, ensuring version compatibility.
-   **Documentation Hub**: The library provides comprehensive documentation explaining the Thought Engine architecture and how PCP components work together.
-   **Versioning Coordination**: The library version number reflects the compatibility set of PCP component versions it depends on.

---

## 3. Package Structure

The library structure is minimal:

```
joshua_thought_engine/
├── pyproject.toml              # Declares dependencies on PCP components
├── README.md                   # Comprehensive architecture documentation
├── CHANGELOG.md                # Version history and compatibility notes
└── LICENSE                     # License file
```

**Notably absent:**
- ❌ No `src/` directory with implementation code
- ❌ No `joshua_thought_engine/` module directory
- ❌ No `__init__.py` with classes or functions
- ❌ No reasoning logic, flow execution, or orchestration code

---

## 4. Functional Requirements

### 4.1 Dependency Declaration

The `pyproject.toml` must declare dependencies on all PCP component libraries with appropriate version constraints:

```toml
[project]
name = "joshua_thought_engine"
version = "0.7.0"
description = "Master library for Joshua Thought Engine - aggregates PCP component libraries"
requires-python = ">=3.11"

dependencies = [
    "joshua_dtr>=0.7.0,<0.8.0",          # Dynamic Triage Router
    "joshua_lppm>=0.7.0,<0.8.0",         # Learning Prompt Pattern Manager
    "joshua_cet>=0.7.0,<0.8.0",          # Cognitive Execution Tracker
    "joshua_imperator>=0.7.0,<0.8.0",    # Core Deliberative Reasoning
    "joshua_crs>=0.7.0,<0.8.0",          # Cognitive Reflection System
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-asyncio>=0.21.0",
]
```

**Version Constraints:**
- Each component version must be compatible with the master library version
- Use semantic versioning to indicate breaking changes
- Lock minor versions to ensure tested compatibility

### 4.2 Documentation Requirements

The `README.md` must provide:

1. **Architecture Overview**: Explain that the TE is composed of modular PCP components
2. **Component Descriptions**: Brief description of each PCP component's role
3. **Flow-Based Architecture**: Explain that logic lives in flows, not in these libraries
4. **Installation Instructions**: How to install the complete TE stack
5. **Component Usage**: How PCP components provide nodes for flows
6. **Related Documentation**: Links to individual component library docs

Example structure:

```markdown
# Joshua Thought Engine

The Joshua Thought Engine is a **master library** that aggregates the Progressive Cognitive Pipeline (PCP) component libraries. It contains no implementation code itself.

## Architecture

The Thought Engine consists of five modular component libraries:

- **joshua_dtr**: Dynamic Triage Router - decides which flow to call
- **joshua_lppm**: Learning Prompt Pattern Manager - manages learned patterns
- **joshua_cet**: Cognitive Execution Tracker - tracks reasoning progress
- **joshua_imperator**: Core Deliberative Reasoning - provides reasoning nodes
- **joshua_crs**: Cognitive Reflection System - learns from outcomes

## Installation

```bash
pip install joshua_thought_engine
```

This will install all PCP component libraries.

## Usage

The Thought Engine components provide custom Langflow nodes that are composed in flows. See ADR-032 for the fully flow-based architecture.

[... additional documentation ...]
```

### 4.3 Version Compatibility

The library must maintain a compatibility matrix documenting which versions of component libraries work together:

```markdown
## Compatibility Matrix

| joshua_thought_engine | joshua_dtr | joshua_lppm | joshua_cet | joshua_imperator | joshua_crs |
|-----------------------|------------|-------------|------------|------------------|------------|
| 0.7.0                 | 0.7.0      | 0.7.0       | 0.7.0      | 0.7.0            | 0.7.0      |
| 0.8.0                 | 0.8.x      | 0.8.x       | 0.8.x      | 0.8.x            | 0.8.x      |
```

### 4.4 No Implementation Requirements

**Critical Requirement**: The library must NOT contain:
- Classes or functions for reasoning
- Flow execution logic (that's in `joshua_flow_executor`, part of Action Engine)
- Orchestration code (decision-making is distributed in flows)
- LLM access code (that's in `joshua_llm_client`, part of Action Engine)
- Any imperative logic

If implementation code is needed, it belongs in one of the PCP component libraries, not here.

---

## 5. Relationship to Other Components

### 5.1 Action Engine Components (NOT part of this library)

The following components are **NOT** dependencies of joshua_thought_engine:
- `joshua_flow_executor` - Flow execution (part of Action Engine)
- `Joshua_Communicator` - Network I/O (part of Action Engine)

These are Action Engine components and should not be listed as dependencies.

**Note**: There is no centralized `joshua_llm_client` library. Flows make direct MCP calls to Fiedler and implement their own failover strategies (per ADR-029).

### 5.2 PCP Component Libraries (ARE dependencies)

The following ARE dependencies:
- `joshua_dtr` - Provides DTR nodes for triage/routing
- `joshua_lppm` - Provides pattern matching nodes
- `joshua_cet` - Provides execution tracking nodes
- `joshua_imperator` - Provides deliberative reasoning nodes
- `joshua_crs` - Provides reflection nodes

### 5.3 Usage in MADs

MADs that want the complete Thought Engine stack simply:

```toml
# In MAD's pyproject.toml
dependencies = [
    "joshua_thought_engine>=0.7.0,<0.8.0",  # Gets all PCP components
    "joshua_flow_executor>=0.7.0",          # Separately, from AE
    "Joshua_Communicator>=0.7.0",           # Separately, from AE
    "ollama-python>=0.1.0",                 # For Ollama failover (optional)
]
```

---

## 6. Non-Functional Requirements

### 6.1 Minimal Footprint

- Package size should be minimal (< 100KB excluding dependencies)
- No heavy dependencies beyond the PCP component libraries
- Quick installation time

### 6.2 Documentation Quality

- README must be comprehensive and up-to-date
- All links to component library docs must work
- Architecture diagrams (optional but recommended)

### 6.3 Versioning Discipline

- Follow semantic versioning strictly
- Increment version when component dependencies change
- Document breaking changes in CHANGELOG.md

---

## 7. Deliverables

1. **`pyproject.toml`**: Dependency declarations
2. **`README.md`**: Comprehensive documentation
3. **`CHANGELOG.md`**: Version history
4. **`LICENSE`**: License file

**Not Required:**
- ❌ Source code directory
- ❌ Test suite (components have their own tests)
- ❌ Implementation examples (those are in MAD templates)

---

## 8. Success Criteria

The `joshua_thought_engine` library will be considered successful when:

1. **Installation Works**: `pip install joshua_thought_engine` installs all PCP components
2. **Version Compatibility**: All declared component versions work together without conflicts
3. **Zero Implementation**: Contains no `.py` files with classes or functions
4. **Documentation Complete**: README fully explains architecture and component roles
5. **Maintainable**: Clear process for updating component version dependencies

---

## 9. Related Decisions

- **ADR-029**: Local Ollama Failover Architecture - Defines LLM access (not part of TE)
- **ADR-030**: Langflow Internal Architecture - Establishes flow-based paradigm
- **ADR-031**: Modular PCP Component Libraries - Defines this master library pattern
- **ADR-032**: Fully Flow-Based Architecture - Explains distributed decision-making

---

## 10. Migration from Previous Architecture

**V0.6 and earlier**: joshua_thought_engine had a `ThoughtEngine` class with reasoning loops

**V0.7+**: joshua_thought_engine is a dependency aggregator with no implementation code

**Migration Path for MADs:**
1. Remove direct instantiation of `ThoughtEngine` class (doesn't exist anymore)
2. Install PCP component libraries via this master library
3. Use `joshua_flow_executor` (AE) for flow execution
4. Use component nodes in flows instead of imperative reasoning code

**Code that should be removed:**
```python
# OLD (V0.6) - DON'T DO THIS ANYMORE
from joshua_thought_engine import ThoughtEngine
te = ThoughtEngine(mad_name, communicator, config)
result = await te.process_conversational_prompt(prompt)
```

**New pattern (V0.7):**
```python
# NEW (V0.7) - Use flow executor
from joshua_flow_executor import FlowExecutor
executor = FlowExecutor(flows_dir, components_dir, llm_client)
result = await executor.execute("reasoning_flow", {"prompt": prompt})
```
