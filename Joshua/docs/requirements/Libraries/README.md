# Library Requirements

This directory contains requirements documents for shared libraries used across all MADs in the Joshua ecosystem.

## What is a Library Requirements Document?

Libraries are the foundational engines and infrastructure components that MADs import and compose. A library requirements document specifies:

1. **Purpose & Scope** - The library's core responsibility
2. **Public API** - Exposed classes, functions, and interfaces
3. **Dependencies** - Other libraries or external packages required
4. **Performance Requirements** - Latency, throughput, resource constraints
5. **Reliability Requirements** - Error handling, failover strategies, resilience
6. **Configuration** - How MADs customize the library's behavior
7. **Testing Strategy** - Unit test coverage, integration test patterns

Library requirements documents focus on **what the library must do**, not how MADs use it.

## Library Categories

### Action Engine Libraries

Core infrastructure for MAD execution:

- **Joshua_Communicator** (`20_Joshua_Communicator_Library_Specification.md`) - Network I/O, MCP communication, logging, ingress routing
- **Joshua_Flow_Runner** (`Joshua_Flow_Runner_Library_Requirements.md`) - Langflow `.json` flow execution engine
- **joshua_flow_scheduler** (MISSING) - Scheduled/periodic flow triggers

### Thought Engine Libraries

The `pcp/` subdirectory contains Progressive Cognitive Pipeline (PCP) component libraries that provide custom Langflow nodes for MAD reasoning:

- **joshua_thought_engine** (`pcp/joshua_thought_engine_library_requirements.md`) - Master dependency aggregator (no implementation code)
- **joshua_imperator** (`pcp/joshua_imperator_library_requirements.md`) - Tier 4: Full LLM reasoning nodes
- **joshua_dtr** (MISSING) - Tier 1: Dynamic Triage Router nodes
- **joshua_lppm** (MISSING) - Tier 2: Learning Prompt Pattern Manager nodes
- **joshua_cet** (MISSING) - Tier 3: Cognitive Execution Tracker nodes
- **joshua_crs** (MISSING) - Tier 5: Cognitive Reflection System nodes

See `pcp/README.md` for detailed PCP architecture overview.

## Installation & Dependency Management

All libraries are installed via pip from MAD `requirements.txt` files:

```txt
# Action Engine Libraries
joshua_communicator>=0.7.0
joshua_flow_runner>=0.7.0
joshua_flow_scheduler>=0.7.0

# Thought Engine Libraries
joshua_thought_engine>=0.7.0  # Pulls in all PCP component libraries
```

## Versioning Strategy

Libraries follow semantic versioning:
- **Major version** (1.x.x) - Breaking API changes
- **Minor version** (x.1.x) - New features, backward compatible
- **Patch version** (x.x.1) - Bug fixes

MADs specify minimum compatible versions in `requirements.txt`.

## Related Documentation

- **Architecture Documents**: `/docs/architecture/` - System-wide patterns
- **ADRs**: `/docs/architecture/adr/` - Architectural decisions
- **PCP Documentation**: `/docs/architecture/pcp/` - Progressive Cognitive Pipeline specifications
- **MADs**: `../MADs/` - How MADs compose libraries
- **Nodes**: `../Nodes/` - Fine-grained node building blocks (used within flows)

---

**Last Updated:** 2025-12-21
