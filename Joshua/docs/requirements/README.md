# Joshua Project Requirements

This directory contains the master requirements documentation for the Joshua project, organized by architectural layer to mirror the **thin composition layer** design philosophy.

## Overview

The Joshua ecosystem is built on composition, not monoliths. MADs are lightweight containers that compose functionality from:
- **Libraries** - Foundational engines (Action Engine, Thought Engine)
- **Nodes** - Fine-grained building blocks used within flows
- **Flows** - Reusable logic patterns

This directory structure reflects that architectural reality.

## Directory Structure

```
requirements/
├── README.md (this file)
├── MADs/                    # MAD composition manifests
│   ├── README.md
│   ├── MAD_Template_V0.7_Requirements.md
│   ├── 01_Hopper_Requirements.md
│   ├── 02_Turing_Requirements.md
│   └── ... (31+ MADs)
├── Libraries/               # Infrastructure and engine specifications
│   ├── README.md
│   ├── 20_Joshua_Communicator_Library_Specification.md
│   ├── Joshua_Flow_Runner_Library_Requirements.md
│   └── pcp/                # Progressive Cognitive Pipeline components
│       ├── README.md
│       ├── joshua_thought_engine_library_requirements.md
│       └── joshua_imperator_library_requirements.md
├── Nodes/                   # Fine-grained building block specifications
│   ├── README.md
│   ├── core/               # Universal nodes (joshua_core)
│   ├── providers/          # Provider-specific nodes (joshua_gemini, joshua_claude, etc.)
│   └── domain/             # Domain-specific nodes (joshua_ffmpeg, etc.)
└── Flows/                   # General-purpose reusable flows
    └── README.md
```

## Quick Navigation

### I Want To...

**Understand what a MAD does** → `MADs/README.md`
- MAD requirements are composition manifests specifying which libraries, nodes, and flows a MAD uses

**Understand a foundational library** → `Libraries/README.md`
- Library requirements specify public APIs, performance, and reliability for infrastructure components

**Understand PCP cognitive tiers** → `Libraries/pcp/README.md`
- PCP component libraries provide custom reasoning nodes for Thought Engines

**Find reusable building blocks** → `Nodes/README.md`
- Node library requirements catalog fine-grained components used within flows

**Discover common flow patterns** → `Flows/README.md`
- Flow requirements document general-purpose logic patterns (currently empty, will grow over time)

**Create a new MAD** → `MADs/MAD_Template_V0.7_Requirements.md`
- Template for writing MAD composition manifests

## Architectural Context

This structure is based on:
- **ADR-032**: Fully Flow-Based Architecture - Logic in flows, not code
- **ADR-036**: Node Library Architecture - Three-tiered node model
- **ADR-031**: Modular PCP Component Libraries - Cognitive tier organization

The key insight: **MADs are thin composition layers**. They contain ~100 lines of glue code (`server_joshua.py`) and `.json` flows. All functionality is imported from libraries and nodes.

## Reference Documents

### Vision Statements
- **`MAD_Vision_Statements.csv`** - Master reference for immutable MAD vision statements (kept in root for backward compatibility)

### Obsolete Documents (Deleted 2025-12-22)
The following documents have been deleted as they were superseded by newer ADRs and architecture decisions:
- **`Fiedler_CLI_Integration_Requirements.md`** - Superseded by ADR-035 (Direct Access AI Model Nodes)
- **`joshua_ai_access_library_requirements.md`** - Superseded by ADR-034/036/037 (CLI-first strategy with fine-grained node libraries)
- **`Imperator_V1.0_Requirements.md`** - Superseded by `Libraries/pcp/joshua_imperator_library_requirements.md`

## Version Progression

Requirements documents evolve with the system:
- **V0.7** - Flow-based architecture foundation
- **V0.10** - Phase 1 foundation MADs complete
- **V1.0** - Conversation bus, Imperator-only Thought Engines
- **V5.0** - Full PCP stack (all cognitive tiers)
- **V6.0+** - eMAD team collaboration, production features

## How to Create New Requirements

### For a New MAD
1. Copy `MADs/MAD_Template_V0.7_Requirements.md`
2. Fill in composition details (libraries, nodes, flows)
3. Number sequentially (next available MAD number)
4. Add to `MADs/README.md`

### For a New Library
1. Determine category (Action Engine, PCP component, etc.)
2. Create in `Libraries/` or `Libraries/pcp/`
3. Follow existing library requirement patterns
4. Add to `Libraries/README.md` or `Libraries/pcp/README.md`

### For a New Node Library
1. Determine tier (universal/provider-specific/domain-specific per ADR-036)
2. Create in appropriate `Nodes/` subdirectory
3. Document each node's inputs, outputs, behavior
4. Add to `Nodes/README.md`

### For a New General-Purpose Flow
1. Extract reusable pattern from MAD-specific flow
2. Document inputs, outputs, node composition
3. Create in `Flows/`
4. Add to `Flows/README.md`

## Related Documentation

- **Architecture Documents**: `/docs/architecture/` - System-wide architectural patterns
- **ADRs**: `/docs/architecture/adr/` - Architectural Decision Records
- **PCP Design Docs**: `/docs/architecture/pcp/` - Progressive Cognitive Pipeline specifications
- **Design Documents**: `/docs/design/` - Detailed implementation designs

---

**Last Updated:** 2025-12-22
