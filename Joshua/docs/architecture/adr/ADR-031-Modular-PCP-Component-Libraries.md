# ADR-031: Modular PCP Component Libraries

**Status:** Superseded (by ADR-045: PCP as Unified Flow Pipeline)

> **⚠️ SUPERSEDED**: This ADR proposed separate libraries for each PCP tier (joshua_dtr, joshua_lppm, joshua_imperator, joshua_cet, joshua_crs) based on code-first architecture assumptions. **ADR-045** supersedes this with a unified `joshua_thought_engine` library containing the complete PCP pipeline, reflecting the flow-based architecture established by ADR-032.
**Date:** 2025-12-20
**Updated:** 2025-12-21 (Implementation approach updated per ADR-034)
**Deciders:** System Architect

---

## Implementation Update (2025-12-21)

**This ADR defines the modular structure of PCP component libraries. However, the implementation approach has changed per ADR-034: CLI-First LLM Integration Strategy.**

**Key Changes:**
- PCP component libraries (joshua_imperator, joshua_dtr, etc.) now serve as **specification documents**, not immediate implementations
- Initial implementation uses **LLM provider CLIs** wrapped by Fiedler MCP tools
- Custom nodes may be built later if CLI capabilities insufficient (rare)

**This ADR remains valid** for defining the modular architecture and intellectual capital preservation patterns. The CLI-first approach simply changes *how* these capabilities are delivered to MADs (via CLI wrappers instead of custom nodes).

**See ADR-034 for implementation details.**

---

## Context and Problem Statement

The Progressive Cognitive Pipeline (PCP) is a complex, multi-stage reasoning framework composed of distinct tiers: DTR (Dynamic Triage Router), LPPM (Learning Prompt Pattern Manager), CET (Cognitive Execution Tracker), Imperator (Core Deliberative Reasoning), and CRS (Cognitive Reflection System).

In earlier architectures, these components were tightly coupled within a monolithic `joshua_thought_engine` codebase. As the system evolves toward a fully flow-based architecture (ADR-032), we need a clear decision on how to structure these cognitive components: Should they remain as modules in a monolith, or become independent libraries?

This decision is critical for:
- **Maintainability** - Can we develop and test each component independently?
- **Versioning** - Can different MADs use different versions of components?
- **Reusability** - Can components be composed in new ways for different reasoning patterns?
- **Intellectual Capital** - How do we preserve sophisticated reasoning patterns while migrating to flows?

## Decision

We will decompose the PCP into **modular, independently versioned component libraries**. Each tier of the PCP will be implemented as its own distinct Python library that can be developed, tested, versioned, and released independently.

### Component Library Structure

The following libraries will be created:

1. **`joshua_dtr`** - Dynamic Triage Router
   - Provides custom nodes for initial request classification
   - Determines routing strategy for different request types

2. **`joshua_lppm`** - Learning Prompt Pattern Manager
   - Provides nodes for prompt pattern matching and selection
   - Manages learned patterns and adaptations

3. **`joshua_cet`** - Cognitive Execution Tracker
   - Provides nodes for tracking reasoning progress
   - Manages working memory and intermediate states

4. **`joshua_imperator`** - Core Deliberative Reasoning
   - Provides nodes for deep, step-by-step reasoning
   - Implements self-critique, planning, and refinement patterns

5. **`joshua_crs`** - Cognitive Reflection System
   - Provides nodes for post-execution analysis
   - Implements learning from outcomes

### Master Library Composition

The **`joshua_thought_engine`** remains as a master library that:
- Declares dependencies on the PCP component libraries
- Provides the top-level interface for the Thought Engine
- Contains decision logic for selecting which flows to invoke
- Does NOT contain orchestration logic (flows handle that per ADR-032)

**Dependency structure:**
```
joshua_thought_engine (master library)
  ├─ depends on: joshua_dtr
  ├─ depends on: joshua_lppm
  ├─ depends on: joshua_cet
  ├─ depends on: joshua_imperator
  └─ depends on: joshua_crs
```

### Integration with Flow-Based Architecture

As established in ADR-032, these component libraries:

1. **Provide custom nodes for flows** - Each library exports Python classes/functions that can be used as nodes within Langflow graphs
2. **Do not orchestrate** - The libraries do not control the sequence of operations; flows define the logic
3. **Are stateless where possible** - Nodes should be idempotent and avoid hidden state
4. **Can be composed in any pattern** - Flows can use nodes from different libraries in any order, not just the traditional PCP sequence

**Example flow usage:**
```
communications_routing_flow.json:
  - joshua_dtr.TriageNode (classify request)
  - joshua_lppm.PatternMatchNode (find similar patterns)
  - joshua_imperator.DeliverativeReasoningNode (deep thinking)
  - joshua_crs.ReflectionNode (learn from outcome)
```

### Preserving Intellectual Capital

**Critical principle:** Established reasoning patterns (like the Imperator's self-critique loop) represent significant intellectual capital. As we migrate to a flow-based architecture, these patterns must be:

1. **Explicitly preserved** - Documented as canonical flow patterns in the component library repositories
2. **Transformed, not lost** - Converted from imperative code to declarative flow graphs
3. **Made more transparent** - Visual flow representation makes the patterns easier to understand and modify
4. **Maintained as reference implementations** - Each library includes example flows demonstrating its proper use

**Example:** The Imperator's "Plan → Critique → Refine" loop will be implemented as:
- **Nodes** in `joshua_imperator` library (PlanNode, CritiqueNode, RefineNode)
- **Reference flow** `imperator_self_critique_pattern.json` showing the canonical usage
- **Documentation** explaining the pattern and its rationale

## Consequences

### Positive

**Independent Development:**
- Each component can be developed by different teams/processes
- Changes to one component don't require rebuilding others
- Faster iteration cycles for individual components

**Independent Versioning:**
- MADs can upgrade components individually
- Breaking changes in one library don't force upgrades across all components
- Different MADs can use different component versions if needed

**Better Testing:**
- Each library has its own test suite
- Component testing isolated from integration testing
- Easier to achieve high test coverage per component

**Reusability:**
- Components can be mixed in novel flow patterns
- Not locked into a single PCP sequence
- Easier to experiment with new reasoning architectures

**Clearer Ownership:**
- Each library has clear scope and responsibility
- Documentation and requirements naturally partitioned
- Easier to assign maintenance responsibility

### Negative

**Dependency Management Complexity:**
- More libraries to track and version
- Potential for version conflicts between components
- Need robust dependency resolution in master library

**Integration Testing Overhead:**
- Must test not just individual libraries but their combinations
- Flows using multiple components require cross-library integration tests
- More complex CI/CD pipeline

**Initial Development Effort:**
- Requires creating separate repositories/packages for each component
- Each library needs its own requirements, design, and test documentation
- Migration of existing code to new structure takes time

## Implementation Plan

### Phase 1: Foundation (V0.7)
1. Create `joshua_imperator` library (highest priority, most complex reasoning)
2. Update `joshua_thought_engine` to depend on `joshua_imperator`
3. Establish patterns for component library structure

### Phase 2: Expansion (V0.8+)
4. Create remaining PCP component libraries (`joshua_dtr`, `joshua_lppm`, `joshua_cet`, `joshua_crs`)
5. Migrate existing PCP logic to new modular structure
6. Create reference flow patterns for each component

### Phase 3: Optimization (V0.9+)
7. Independent versioning and release cycles for mature components
8. Cross-MAD component sharing (if applicable)
9. Advanced flow composition patterns

## Related Decisions

- **ADR-029**: Local Ollama Failover Architecture - Defines LLM access for PCP components
- **ADR-030**: Langflow Internal Architecture - Introduced flow-based paradigm and Joshua_Flow_Runner
- **ADR-032**: Fully Flow-Based Architecture - Establishes that flows orchestrate component nodes, not Python code
- **ADR-033**: Metaprogramming via Hopper-Orchestrated Optimization - Depends on modular structure for targeted optimization
- **ADR-034**: CLI-First LLM Integration Strategy - **Changes implementation approach** - PCP capabilities provided by CLI wrappers, not custom nodes

## Action Items

### Completed (Specification Documents)
1. ~~Create requirements document for `joshua_imperator` library~~ ✅ **COMPLETED** - See `/docs/requirements/joshua_imperator_library_requirements.md` (now serves as Fiedler CLI wrapper specification per ADR-034)
2. ~~Create design document for `joshua_imperator` library~~ ✅ **COMPLETED** - See `/docs/design/joshua_imperator_library_design.md` (now serves as capability map and design reference per ADR-034)
3. ~~Update `joshua_thought_engine` requirements to reflect master library role~~ ✅ **COMPLETED** - See `/docs/requirements/joshua_thought_engine_library_requirements.md` (dependency aggregator with no root code)

### Cancelled (Removed from Architecture)
4. ~~Create requirements document for `joshua_llm_client` library~~ ❌ **CANCELLED** - Removed from architecture (flows handle LLM failover directly, per ADR-029)
5. ~~Create requirements document for `joshua_flow_executor` library~~ ❌ **CANCELLED** - MAD servers use Joshua_Flow_Runner directly (no wrapper needed)

### Superseded by ADR-034 (CLI-First Approach)
6. ~~Build joshua_imperator library implementation~~ → **SUPERSEDED** - Use Fiedler CLI wrappers instead (see ADR-034)
7. ~~Build other PCP component library implementations~~ → **SUPERSEDED** - Use Fiedler CLI wrappers instead (see ADR-034)

### New Action Items (CLI Integration)
8. **Implement Fiedler CLI MCP tool wrappers** - See ADR-034 and `/docs/requirements/Fiedler_CLI_Integration_Requirements.md`
9. **Update MAD Template to use CLI sessions** - Replace custom node examples with Fiedler CLI tool usage
10. **Create reference flows using CLI tools** - Demonstrate chatbot, code generation, multi-turn reasoning patterns

### Still Valid (Future Work)
11. Establish component library development guidelines (if custom nodes needed later)
12. Create template repository for PCP component libraries (if custom nodes needed later)
