# Flow Requirements

This directory contains requirements documents for general-purpose, reusable Langflow flows that can be composed and referenced across multiple MADs.

## What is a Flow Requirements Document?

Per **ADR-032: Fully Flow-Based Architecture**, flows are the primary logic artifacts in the Joshua ecosystem. A flow requirements document specifies:

1. **Purpose** - What problem the flow solves
2. **Inputs** - Required and optional parameters
3. **Outputs** - Return value structure and format
4. **Node Composition** - Which nodes from which libraries are used
5. **Control Flow** - Branching, loops, error handling patterns
6. **Performance Characteristics** - Expected latency, resource usage
7. **Reusability** - How other flows or MADs can compose this flow

## General-Purpose Flows vs. MAD-Specific Flows

**General-Purpose Flows** (this directory):
- Reusable across multiple MADs
- Solve common, domain-agnostic problems
- Examples:
  - Standard self-critique flow (Plan → Critique → Refine pattern)
  - Error handling flow with retry logic
  - Context compression flow for large inputs

**MAD-Specific Flows** (described in `../MADs/` requirements):
- Tailored to a specific MAD's domain
- May reference general-purpose flows as sub-flows
- Examples:
  - Hopper's "bootstrap new MAD" flow
  - Starret's "commit with conventional message" flow
  - Fiedler's "recommend optimal model for task" flow

## Common Flow Patterns

### Reactive Flows
Triggered by external events (messages, tool calls):
- **User prompt flow** - Natural language request handling
- **Tool execution flow** - MCP tool invocation processing
- **Error recovery flow** - Graceful degradation on failures

### Proactive Flows
Triggered by schedules or internal state:
- **Periodic review flow** - Regular self-assessment
- **Metric collection flow** - Performance data gathering
- **Learning update flow** - Knowledge base refinement

### Cognitive Flows
Implementing reasoning patterns:
- **Full PCP deliberation** - DTR → LPPM → CET → Imperator → CRS
- **Quick triage** - Simplified fast-path decision making
- **Self-critique** - Plan → Critique → Refine cycle

## Flow Composition

Flows can compose other flows as sub-flows (composite nodes):

```json
{
  "nodes": [
    {
      "id": "preprocess",
      "type": "SubFlowNode",
      "flow": "standard_input_validation_flow.json"
    },
    {
      "id": "reason",
      "type": "SubFlowNode",
      "flow": "standard_self_critique_flow.json",
      "inputs": {"validated_input": "{{preprocess.output}}"}
    },
    {
      "id": "postprocess",
      "type": "SubFlowNode",
      "flow": "standard_output_formatting_flow.json"
    }
  ]
}
```

## How to Use General-Purpose Flows

MADs reference general-purpose flows in their requirements documents:

```markdown
## Core Flows

This MAD uses the following general-purpose flows from `/Flows/`:
- `standard_self_critique_flow.json` - For all code generation tasks
- `standard_error_recovery_flow.json` - For graceful degradation

And implements these MAD-specific flows:
- `bootstrap_new_mad_flow.json` - Orchestrates MAD creation process
```

## Flow Development Workflow

1. **Design** - Use Hopper's Langflow UI for visual flow design
2. **Export** - Export as `.json` artifact
3. **Document** - Create requirements document in this directory
4. **Version Control** - Commit flow and requirements to git
5. **Test** - Validate with flow executor (typically via Deming)
6. **Publish** - Make available for MAD composition

## Current Status

**This directory is currently empty.** As the ecosystem matures, general-purpose flows will be extracted from MAD-specific implementations and documented here for reuse.

**Candidates for Future General-Purpose Flows:**
- Standard self-critique flow (Plan → Critique → Refine)
- Standard context compression flow
- Standard error handling with retry flow
- Standard MCP tool orchestration flow
- Standard multi-model consensus flow

## Related Documentation

- **ADR-032**: Fully Flow-Based Architecture - Flow design principles
- **ADR-030**: Langflow Internal Architecture - Flow execution engine
- **MADs**: `../MADs/` - MAD-specific flows
- **Nodes**: `../Nodes/` - Building blocks used within flows
- **Libraries**: `../Libraries/` - Infrastructure for flow execution

---

**Last Updated:** 2025-12-21
