# MAD Requirements

This directory contains requirements documents for all Multipurpose Agentic Duos (MADs) in the Joshua ecosystem.

## What is a MAD Requirements Document?

Per the **thin composition layer architecture** (ADR-032), MADs are lightweight containers that compose functionality from shared libraries, nodes, and flows. A MAD requirements document is a **composition manifest** that specifies:

1. **Role & Purpose** - The MAD's strategic function in the ecosystem
2. **Core Libraries** - Which Action Engine and Thought Engine libraries it imports
3. **Required Nodes** - Which node libraries it depends on (universal, provider-specific, domain-specific)
4. **Core Flows** - References to reusable flows from `../Flows/` and descriptions of MAD-specific flows
5. **Exposed MCP Tools** - Minimal list of tools that trigger flows
6. **Configuration** - Persona, behavioral guidelines, flow parameters

MAD requirements documents do **not** specify implementation details (those live in the Libraries and Nodes directories).

## MAD Categories (6-Phase Roadmap)

### Phase 1: Foundation MADs (V0.10)
- **01_Hopper** - Metaprogramming Engine - Orchestrates system evolution and MAD development
- **02_Turing** - Testing & Validation - Ensures code quality and correctness
- **03_Starret** - Git Operations - Version control management
- **04_Fiedler** - AI Model Ecosystem Orchestrator - Model recommendations, GPU coordination
- **05_Deming** - Quality Assurance - Continuous improvement processes
- **06_Malory** - Web Gateway - External internet access
- **07_Grace** - Build & Dependency - Compilation and dependency management
- **08_Sutherland** - Local Inference - Shared host-level AI model execution
- **09_Henson** - Creativity & Innovation - Novel problem-solving approaches
- **10_Hamilton** - Observability & Monitoring - System health and performance tracking
- **11_Rogers** - Conversation Bus - Kafka-based message routing (V1.0+)
- **12_Sam** - Security & Compliance - Constitutional enforcement and security policies
- **13_Babbage** - Read Model Generator - Kafka log consumer, MongoDB read models (V1.0+)
- **14_Horace** - File Management - Distributed file storage and retrieval (V1.0+)
- **15_McNamara** - Project Management - Strategic planning and resource coordination

### Phase 2: V1.0 - Conversation Bus Foundation
All Phase 1 MADs migrate to Conversation Bus architecture with Imperator-only Thought Engines.

### Phase 3: V5.0 - Full PCP Stack
All Phase 1 MADs upgraded to V5.0 with complete PCP (DTR + LPPM + CET + Imperator + CRS).

### Phase 4: V6.0 - eMAD Revolution
- **15_Kaiser** - eMAD Lifecycle Management - Team Assembler for ephemeral agent teams (see ADR-017)
- **16_Moses** - Federated Container Orchestration - Master Orchestrator for container placement (see ADR-018)

### Phase 5-6: Specialized Domain MADs
- **17_Joshua** - Constitutional Authority - System-wide governance
- **18_Bace** - Security Auditing
- **19_Bass** - Performance Optimization
- **20_Bush** - Documentation Generation
- **21_Cerf** - Network Management
- **22_Clarke** - Space Systems (future)
- **23_Codd** - Database Operations
- **24_Lovelace** - Algorithm Design
- **25_McNamara** (duplicate number - needs correction)
- **26_Moog** - Audio Processing
- **27_Muybridge** - Video Processing
- **28_Playfair** - Data Visualization
- **29_Knuth** - Documentation & Publishing
- **30_Brin** - Search & Discovery
- **31_Gates** - UI/UX Design

## Template

**MAD_Template_V0.7_Requirements.md** - Blueprint for creating new MAD requirements documents as composition manifests

## Related Documentation

- **Architecture Documents**: `/docs/architecture/` - System-wide architectural patterns
- **ADRs**: `/docs/architecture/adr/` - Architectural Decision Records
- **Libraries**: `../Libraries/` - Shared library specifications
- **Nodes**: `../Nodes/` - Reusable node building blocks
- **Flows**: `../Flows/` - General-purpose flow patterns

---

**Last Updated:** 2025-12-22
