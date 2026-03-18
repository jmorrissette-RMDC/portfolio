# Joshua Project Architecture

This directory contains the authoritative architectural documentation for the Joshua project.

## Documentation Structure

### Core Architecture Documents

The following documents describe the unified Joshua architecture (V0 through V1+):

1. **`00_Joshua_System_Roadmap.md`** - High-level strategic roadmap from V0 through V7.0, MAD build order, and version progression
2. **`01_System_Overview.md`** - System-wide architectural overview, evolution from V0 mesh to V1+ conversation bus
3. **`02_Communication_Architecture.md`** - MAD-to-MAD communication patterns and protocols
4. **`03_Data_Architecture.md`** - Data management, storage, and persistence patterns
5. **`04_Integration_Architecture.md`** - External integration, gateways, and egress patterns
6. **`05_Operational_Architecture.md`** - Logging, monitoring, CI/CD, and operational patterns
7. **`06_Workflow_Orchestration.md`** - Task coordination and multi-MAD workflow patterns
8. **`07_Deployment_And_Containerization.md`** - Docker deployment, container orchestration
9. **`08_MAD_Lifecycle_And_Versioning.md`** - MAD development lifecycle, version progression standards
10. **`09_MAD_Internal_Architecture.md`** - **Flow-based MAD architecture** (V0.7+), composition pattern, directory structure
11. **`10_Docker_Network_Configuration.md`** - Network topology and container networking

### Developer Documentation

- **`MAD_Developer_Guide.md`** - Practical guide for developing MADs

### Architectural Decision Records (ADRs)

The `adr/` subdirectory contains formal Architectural Decision Records documenting key architectural choices:

**Key ADRs for Understanding Joshua:**
- **ADR-002**: V0 MAD DNA - Cellular Monolith pattern
- **ADR-021**: Unified I/O and Logging Hub - Joshua_Communicator architecture
- **ADR-024**: Polyglot Subprocess Pattern - Non-Python component integration
- **ADR-030**: Langflow Internal Architecture - Flow execution foundation
- **ADR-032**: Fully Flow-Based Architecture - **CRITICAL** - Defines MAD composition pattern
- **ADR-034**: CLI-First LLM Integration Strategy - How LLM access works
- **ADR-035**: Direct Access AI Model Nodes - MADs access LLMs directly, not via Fiedler proxy
- **ADR-036**: Node Library Architecture - Node organization and acquisition strategies

See `adr/` directory for complete list of ADRs.

## Architectural Eras

### V0.1 - V0.6: Code-First Architecture (Legacy)
Early MAD versions contained imperative Python code in `action_engine/` and `thought_engine/` directories within each MAD.

**Status:** Superseded by flow-based architecture.

### V0.7+: Flow-Based Architecture (Current)
**Per ADR-032**, MADs are thin composition layers:
- Action Engine and Thought Engine are **imported libraries**
- MAD logic defined in `.json` flow files (Langflow)
- MAD contains < 100 lines of wiring code
- All capabilities from imported libraries

**See:** `09_MAD_Internal_Architecture.md` for complete details.

### V1.0+: Conversation Bus Architecture (Future)
Migration from direct communication (V0) to conversation bus (V1+) managed by Rogers MAD.

**See:** `01_System_Overview.md` Section 3.2 for V1+ architecture.

## Quick Start for Developers

1. **Understand the System:** Start with `01_System_Overview.md`
2. **Understand MAD Structure:** Read `09_MAD_Internal_Architecture.md` (flow-based architecture)
3. **Understand Composition Pattern:** Read ADR-032 "MAD Physical Structure and Composition Pattern"
4. **Understand Node Libraries:** Read ADR-036 "Node Library Architecture"
5. **Build a MAD:** Follow `08_MAD_Lifecycle_And_Versioning.md` for the development lifecycle

## Key Architectural Principles

1. **Cellular Monolith** - All MADs share common DNA (libraries, patterns, communication protocols)
2. **Thin Composition** - MADs are nearly empty; functionality comes from imported libraries
3. **Flow-Based Logic** - Logic defined declaratively in `.json` flows, not imperative code
4. **Direct Access AI Models** - MADs use library nodes to access LLMs directly (not via Fiedler execution)
5. **12-Factor App** - All components follow 12-factor methodology for cloud-native design

## Directory Organization

```
architecture/
├── README.md                               # This file
├── 00_Joshua_System_Roadmap.md            # Strategic roadmap
├── 01_System_Overview.md                  # System architecture overview
├── 02_Communication_Architecture.md        # Communication patterns
├── 03_Data_Architecture.md                # Data management
├── 04_Integration_Architecture.md         # External integration
├── 05_Operational_Architecture.md         # Operations and monitoring
├── 06_Workflow_Orchestration.md           # Multi-MAD workflows
├── 07_Deployment_And_Containerization.md  # Docker deployment
├── 08_MAD_Lifecycle_And_Versioning.md     # Development lifecycle
├── 09_MAD_Internal_Architecture.md        # MAD structure (CRITICAL)
├── 10_Docker_Network_Configuration.md     # Network topology
├── MAD_Developer_Guide.md                 # Developer guide
└── adr/                                   # Architectural Decision Records
    ├── ADR-002_V0_MAD_DNA.md
    ├── ADR-032_Fully_Flow-Based_Architecture.md  # CRITICAL
    ├── ADR-035_Direct_Access_AI_Model_Nodes.md
    ├── ADR-036_Node_Library_Architecture.md
    └── ... (see directory for complete list)
```

---

**Last Updated:** 2025-12-21
**Status:** Authoritative
