# Architecture Decision Records (ADRs) Index

**Status:** Active
**Last Updated:** 2025-12-23

## Overview
This document serves as the official index for all Architecture Decision Records (ADRs) in the Joshua project. ADRs capture significant architectural decisions, their context, and consequences, providing a historical record and guiding future development.

## ADR Status Definitions:
- **Accepted:** An active decision, currently guiding implementation.
- **Proposed:** Under consideration; not yet binding.
- **Amended:** The core decision is still valid, but has been clarified or updated by a newer ADR.
- **Partially Superseded:** Core principles remain valid, but specific implementation details have been updated by newer ADRs.
- **Superseded:** This decision has been entirely replaced by a newer ADR. Do not use for new designs.
- **Deprecated:** A decision that is no longer recommended or has been phased out, but is kept for historical context.

## ADR Index

### Core System Architecture

*   [ADR-002: V0 MAD DNA (Hybrid Framework Integration)](./ADR-002-V0-MAD-DNA-Hybrid-Framework-Integration.md) - **Status:** Superseded (by ADR-032)
*   [ADR-007: Kafka-Based Conversation Bus](./ADR-007-Kafka-Based-Conversation-Bus.md) - **Status:** Amended (by ADR-022)
*   [ADR-020: System Evolution Roadmap](./ADR-020-System-Evolution-Roadmap.md) - **Status:** Accepted
*   [ADR-021: Unified Joshua_Communicator](./ADR-021-Unified-Joshua-Communicator.md) - **Status:** Accepted
*   [ADR-022: Rogers as Bus Controller and Service Registry](./ADR-022-Rogers-As-Bus-Controller-And-Service-Registry.md) - **Status:** Accepted
*   [ADR-023: Direct Tool Exposure](./ADR-023-Direct-Tool-Exposure.md) - **Status:** Accepted
*   [ADR-024: Non-Python Subsystem Pattern](./ADR-024-Non-Python-Subsystem-Pattern.md) - **Status:** Accepted
*   [ADR-025: Environment-Specific Storage and Promotion Model](./ADR-025-Environment-Specific-Storage-And-Promotion-Model.md) - **Status:** Accepted
*   [ADR-027: Adoption of the 12-Factor App Methodology](./ADR-027-Adoption-Of-The-12-Factor-App-Methodology.md) - **Status:** Proposed

### Progressive Cognitive Pipeline (PCP)

*   [ADR-001: CRS ML Approach](./ADR-001-CRS-ML-Approach.md) - **Status:** Accepted
*   [ADR-003: Hybrid Transformer LoRA for V4 CET](./ADR-003-Hybrid-Transformer-LoRA-For-V4-CET.md) - **Status:** Accepted
*   [ADR-004: Hybrid LPPM Architecture](./ADR-004-Hybrid-LPPM-Architecture.md) - **Status:** Accepted
*   [ADR-005: V3 PCP Flow with DTR Routing](./ADR-005-V3-PCP-Flow-With-DTR-Routing.md) - **Status:** Accepted
*   [ADR-031: Modular PCP Component Libraries](./ADR-031-Modular-PCP-Component-Libraries.md) - **Status:** Superseded (by ADR-045)
*   [ADR-038: CET Model Selection and Hardware Configuration](./ADR-038-CET-Model-Selection-And-Hardware-Configuration.md) - **Status:** Accepted

### Flow-Based Architecture & Node Libraries

*   [ADR-030: Langflow Internal Architecture](./ADR-030-Langflow-Internal-Architecture.md) - **Status:** Accepted
*   [ADR-032: Fully Flow-Based Architecture](./ADR-032-Fully-Flow-Based-Architecture.md) - **Status:** Accepted
*   [ADR-033: Metaprogramming via Hopper-Orchestrated Optimization](./ADR-033-Metaprogramming-Via-Hopper-Orchestrated-Optimization.md) - **Status:** Accepted
*   [ADR-034: CLI-First LLM Integration Strategy](./ADR-034-CLI-First-LLM-Integration-Strategy.md) - **Status:** Partially Superseded (by ADR-037)
*   [ADR-036: Node Library Architecture](./ADR-036-Node-Library-Architecture.md) - **Status:** Partially Superseded (by ADR-037)
*   [ADR-037: LangFlow Node Sourcing Strategy](./ADR-037-LangFlow-Node-Sourcing-Strategy.md) - **Status:** Accepted
*   [ADR-042: MAD Embedded LangFlow Backend Architecture](./ADR-042-MAD-Embedded-LangFlow-Backend-Architecture.md) - **Status:** Proposed
*   [ADR-045: PCP as Unified Flow Pipeline](./ADR-045-PCP-As-Unified-Flow-Pipeline.md) - **Status:** Accepted
*   [ADR-046: LangFlow to LangGraph Compiler](./ADR-046-LangFlow-To-LangGraph-Compiler.md) - **Status:** Accepted

### LLM Integration & AI Model Access

*   [ADR-008: Fiedler Integration Strategy](./ADR-008-Fiedler-Integration-Strategy.md) - **Status:** Accepted (amended by ADR-035)
*   [ADR-011: Relocate LLM Orchestration Logic](./ADR-011-Relocate-LLM-Orchestration-Logic.md) - **Status:** Superseded (by ADR-021, ADR-023)
*   [ADR-013: Henson-Fiedler Separation](./ADR-013-Henson-Fiedler-Separation.md) - **Status:** Superseded (by ADR-021, ADR-023)
*   [ADR-014: Dynamic LLM Selection](./ADR-014-Dynamic-LLM-Selection.md) - **Status:** Accepted (amended by ADR-035)
*   [ADR-029: Local Ollama Failover Architecture](./ADR-029-Local-Ollama-Failover-Architecture.md) - **Status:** Accepted
*   [ADR-035: Direct Access AI Model Nodes](./ADR-035-Direct-Access-AI-Model-Nodes.md) - **Status:** Accepted
*   [ADR-040: Baseline LLM for Local Agent Resilience](./ADR-040-Baseline-LLM-For-Local-Agent-Resilience.md) - **Status:** Accepted

### MAD-Specific Decisions

*   [ADR-026: Henson's Unified Embedding Model for RAG](./ADR-026-Hensons-Unified-Embedding-Model-For-RAG.md) - **Status:** Accepted
*   [ADR-039: RAG Embedding Strategy with CET-Driven Chunking](./ADR-039-RAG-Embedding-Strategy-With-CET-Driven-Chunking.md) - **Status:** Accepted

### Ephemeral MADs (eMADs) Architecture

*   [ADR-009: eMAD Team Evolution](./ADR-009-eMAD-Team-Evolution.md) - **Status:** Accepted
*   [ADR-010: eMAD Mandate for V6](./ADR-010-eMAD-Mandate-For-V6.md) - **Status:** Accepted
*   [ADR-017: Kaiser eMAD Lifecycle Management](./ADR-017-Kaiser-eMAD-Lifecycle-Management.md) - **Status:** Accepted
*   [ADR-018: Moses Container Orchestrator](./ADR-018-Moses-Container-Orchestrator.md) - **Status:** Accepted
*   [ADR-019: Kaiser eMAD Placement Orchestration](./ADR-019-Kaiser-eMAD-Placement-Orchestration.md) - **Status:** Accepted

### Infrastructure and Compute

*   [ADR-015: Joshua GPU Compute Cluster](./ADR-015-Joshua-GPU-Compute-Cluster.md) - **Status:** Accepted
*   [ADR-016: Joshua MAD Orchestrator](./ADR-016-Joshua-MAD-Orchestrator.md) - **Status:** Accepted
*   [ADR-043: Hamilton Flow Observability Integration](./ADR-043-Hamilton-Flow-Observability-Integration.md) - **Status:** Proposed

### Hardware & Storage

*   [ADR-041: Storage Consolidation to RAID Array](./ADR-041-Storage-Consolidation-To-RAID-Array.md) - **Status:** Accepted

### General Standards

*   [ADR-028: Core Coding Practice Standards](./ADR-028-Core-Coding-Practice-Standards.md) - **Status:** Proposed
*   [ADR-044: Monorepo Library Distribution Pattern](./ADR-044-Monorepo-Library-Distribution-Pattern.md) - **Status:** Accepted

---

## ADR Naming Convention:
`ADR-NNN-Title-Case-Description.md`

Where:
- `ADR` = All caps prefix
- `NNN` = Zero-padded sequential number (001, 002, ...)
- `Title-Case-Description` = Title Case with hyphens (capitalize all major words, acronyms in ALL CAPS)

---

## Contributing

When adding new ADRs:
1. Follow the ADR template (see `docs/templates/adr-template.md` if exists)
2. Assign the next sequential number (currently: **047**)
3. Update this README index
4. Reference related ADRs in the new document
5. Tag with appropriate phase/version
6. Use Title Case naming convention (see above)

---

**Maintained by:** Joshua Project Architecture Team
**Questions?** See `docs/architecture/README.md` for broader architecture documentation
