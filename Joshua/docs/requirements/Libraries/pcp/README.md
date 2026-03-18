# Progressive Cognitive Pipeline (PCP) Component Libraries

This directory contains requirements documents for the PCP component libraries that form the Thought Engine of all MADs.

## PCP Architecture Overview

The Progressive Cognitive Pipeline (PCP) is a five-tier cognitive cascade inspired by biological progressive cognition:

1. **DTR** (Dynamic Triage Router) - Reflexive routing (10-100μs)
2. **LPPM** (Learned Prose-to-Process Mapper) - Process learning (50-500ms)
3. **CET** (Cognitive Execution Tracker) - Context optimization (100-500ms)
4. **Imperator** (LLM Reasoning) - Full semantic reasoning (1-10s)
5. **CRS** (Cognitive Reflection System) - Metacognitive validation (parallel)

## Version Progression

**Per 00_Joshua_System_Roadmap.md:**

### Phase 2: V1.0 - Imperator Only
- All operations require full LLM reasoning
- Latency: 1-10 seconds per operation
- Purpose: Establish conversation bus, accumulate operational data

### Phase 3: V5.0 - Full PCP Stack
**All PCP tiers rolled out together:**
- DTR + LPPM + CET + Imperator + CRS implemented simultaneously
- Latency: 10-100μs to 10s depending on complexity
- Cost: ~80-90% reduction from V1.0

### Phase 4+: V6.0+ - eMAD-Aware and Beyond
- Mature PCP + eMAD orchestration
- Production operations with self-healing

## Component Libraries

### Master Library

- **joshua_thought_engine** (`joshua_thought_engine_library_requirements.md`)
  - Pure dependency aggregator
  - Contains **NO implementation code**
  - Declares dependencies on all PCP component libraries below

### PCP Tier Libraries

- **joshua_imperator** (`joshua_imperator_library_requirements.md`)
  - Tier 4: Full LLM reasoning
  - Provides deliberative reasoning nodes for Langflow flows
  - **Current**: Fully specified (V1.0)

- **joshua_dtr** (MISSING - Required for V5.0)
  - Tier 1: Dynamic Triage Router
  - Provides reflexive routing nodes (10-100μs)
  - Decides which flow/tier to invoke

- **joshua_lppm** (MISSING - Required for V5.0)
  - Tier 2: Learning Prompt Pattern Manager
  - Provides learned process nodes (50-500ms)
  - Knowledge distillation from Imperator

- **joshua_cet** (MISSING - Required for V5.0)
  - Tier 3: Cognitive Execution Tracker
  - Provides context optimization nodes (100-500ms)
  - Purpose-specific context assembly

- **joshua_crs** (MISSING - Required for V5.0)
  - Tier 5: Cognitive Reflection System
  - Provides metacognitive validation nodes
  - Self-reflective decision quality checks

## How PCP Libraries Are Used

PCP component libraries provide **custom Langflow nodes** that can be used within flows:

```json
{
  "nodes": [
    {
      "id": "triage_1",
      "type": "DTRNode",
      "inputs": {"message": "{{input.user_message}}"}
    },
    {
      "id": "reason_1",
      "type": "ImperatorNode",
      "inputs": {"context": "{{triage_1.output}}"}
    },
    {
      "id": "reflect_1",
      "type": "CRSNode",
      "inputs": {"decision": "{{reason_1.output}}"}
    }
  ]
}
```

Flows define the orchestration logic, not the libraries. Different flows can use different tier patterns.

## Related Documentation

- **PCP Design Documents**: `/docs/architecture/pcp/` - Detailed tier specifications
- **ADR-031**: Modular PCP Component Libraries - Architecture decision
- **ADR-032**: Fully Flow-Based Architecture - How PCP integrates with flows
- **00_Joshua_System_Roadmap.md**: Version progression and rollout strategy

---

**Last Updated:** 2025-12-21
