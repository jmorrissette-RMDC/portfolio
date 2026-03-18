# ADR-051: MCP Gateway Library Pattern (State 1 Evolution)

**Status:** Accepted
**Date:** 2026-01-31
**Deciders:** System Architect
**Related:** ADR-042 (Shared MAD Core Library), ADR-046 (MAD Groups)

## Context

ADR-042 introduced mad-core-js and mad-core-py for State 0 (monolithic) MADs. As the architecture evolved to State 1 (functional decomposition), a pattern emerged where MCP gateway containers share nearly identical infrastructure code.

State 1 MADs decompose into specialized containers:
- **`[mad]` (MCP Gateway)**: Public-facing MCP API layer, thin routing layer
- **`[mad]-langgraph`**: Internal processing engine (LangGraph flows)
- **`[mad]-[technology]`**: Backing services (postgres, redis, neo4j, etc.)

Each `[mad]` gateway container does the same work:
- Expose MCP tools via HTTP/SSE
- Route tool calls to langgraph/backing containers
- Aggregate health status from dependencies
- Log MCP requests/responses

Current approach: Each MAD implements similar gateway code, leading to duplication and inconsistency.

## Decision

For State 1 MCP gateway containers, we adopt a **configuration-driven template pattern** with standard libraries. MCP gateways become thin configuration layers that compose standard functionality.

### Standard Libraries

Located in `lib/` at project root:

**mcp-protocol-lib** (`lib/mcp-protocol-lib/`)
- HTTP/SSE server implementation
- MCP protocol handling
- Tool registration and discovery
- Request/response formatting
- Automatic request logging

**health-aggregator-lib** (`lib/health-aggregator-lib/`)
- Dependency health checking
- Status aggregation (healthy/degraded/unhealthy)
- HTTP `/health` endpoint implementation
- Configurable health check strategies per dependency type

**logging-lib** (`lib/logging-lib/`)
- Structured JSON logging
- stdout/stderr output
- Log level management (runtime configurable)
- Context injection (request_id, tool_name, etc.)

**routing-lib** (`lib/routing-lib/`)
- HTTP client for langgraph/backing containers
- Tool call forwarding
- Response handling
- Error mapping

### Template Server Code

Generic server.js (< 20 lines), same across all MADs:

```javascript
// mads/[mad]/js/server.js
const { MCPGateway } = require('mcp-protocol-lib');
const config = require('./config.json');

const gateway = new MCPGateway(config);
gateway.start();
```

Template uses local library references in package.json:

```json
{
  "dependencies": {
    "mcp-protocol-lib": "file:../../lib/mcp-protocol-lib",
    "health-aggregator-lib": "file:../../lib/health-aggregator-lib",
    "logging-lib": "file:../../lib/logging-lib",
    "routing-lib": "file:../../lib/routing-lib"
  }
}
```

### Configuration File

MAD-specific behavior defined in `mads/[mad-name]/config.json`:

```json
{
  "port": 6340,
  "tools": {
    "conv_add_turn": {
      "target": "[mad]-langgraph:8000",
      "endpoint": "/invoke/add_turn",
      "schema": {
        "input": { "conversation_id": "string", "turn": "object" },
        "output": { "success": "boolean" }
      }
    },
    "mem_search": {
      "target": "[mad]-langgraph:8000",
      "endpoint": "/invoke/search_memory",
      "schema": {
        "input": { "query": "string" },
        "output": { "results": "array" }
      }
    }
  },
  "dependencies": {
    "postgres": "[mad]-postgres:5432",
    "redis": "[mad]-redis:6379",
    "neo4j": "[mad]-neo4j:7687"
  },
  "logging": {
    "level": "INFO",
    "configPath": "/storage/config/[mad-name]/logging.json"
  },
  "routing": {
    "timeout": 30000,
    "retries": 3
  }
}
```

Configuration must validate against `templates/mcp-gateway/config.schema.json`.

### Directory Structure

```
Joshua26/
├── lib/
│   ├── mcp-protocol-lib/
│   ├── health-aggregator-lib/
│   ├── logging-lib/
│   └── routing-lib/
├── templates/
│   └── mcp-gateway/
│       ├── server.js (template)
│       ├── config.schema.json
│       ├── config.example.json
│       ├── package.json (template)
│       ├── Dockerfile.template
│       └── README.md
└── mads/
    ├── [mad-name]/
    │   ├── config.json (MAD-specific)
    │   ├── package.json (uses template libs)
    │   ├── js/
    │   │   └── server.js (copied from template)
    │   └── Dockerfile
    └── [mad-name]-langgraph/
        └── flows/
```

## Usage Guidelines

### State 0 (Monolithic MADs)

Use mad-core-js or mad-core-py as documented in ADR-042. These libraries remain available for State 0 MADs that have not been converted to State 1.

### State 1 (Decomposed MADs)

**MCP Gateway (`[mad]`):**
- Use configuration-driven template pattern with standard libraries
- Copy entire template container from `mads/_template/template/` (includes pre-built server.js, Dockerfile, package.json)
- Customize tools and dependencies in config.json (primary customization point)
- Reference standard libraries in package.json via `file:` protocol (already configured in template)

**LangGraph (`[mad]-langgraph`):**
- Does NOT use mad-core or MCP libraries (no MCP exposure)
- Pure processing engine, internal to MAD group
- Receives requests from MCP gateway via HTTP

**Backing Services (`[mad]-[technology]`):**
- Does NOT use mad-core or MCP libraries (official images)
- Standard infrastructure services (postgres, redis, neo4j, playwright, etc.)

## Benefits

**Eliminates Code Duplication:**
- No repeated gateway implementation across MADs
- Single source of truth for MCP infrastructure
- Centralized bug fixes and improvements

**Configuration-Driven:**
- Configuration changes don't require code changes
- Easier testing and validation (JSON schema)
- Clear separation: behavior (libs) vs specification (config)

**Faster MAD Development:**
- Copy working template containers (`mads/_template/`), not individual files
- Customize config.json and business logic, no infrastructure code needed
- Template includes production patterns (health checks, logging, backups)
- Reduces onboarding time for new MADs

**Consistent Behavior:**
- Standard libraries ensure uniform behavior
- Same logging format, health check pattern, error handling
- Easier debugging and monitoring

**Easier Updates:**
- Library updates apply to all gateways
- No need to update gateway code in each MAD
- Backward compatibility maintained via library versioning

## Consequences

### Positive
- Drastic reduction in gateway code duplication
- Configuration-driven MAD development
- Standard libraries ensure consistency
- Faster development and deployment
- Easier maintenance and updates
- Clear separation of concerns

### Negative
- Additional libraries to maintain (4 standard libraries)
- Library versioning coordination
- Initial template development overhead
- MADs must follow library conventions

### Neutral
- mad-core remains for State 0 MADs (parallel approach)
- New pattern applies to State 1 only
- Migration from State 0 to State 1 is optional

## Implementation

Template implementation deliverables documented in:
- `mads/_template/docs/REQ-mcp-protocol-lib.md`
- `mads/_template/docs/REQ-health-aggregator-lib.md`
- `mads/_template/docs/REQ-logging-lib.md`
- `mads/_template/docs/REQ-routing-lib.md`
- `mads/_template/docs/REQ-mcp-gateway-template.md`

Template usage (copy-paste workflow): `mads/_template/README.md`

LangGraph template documented in:
- `docs/templates/langgraph/REQ-langgraph-template.md`

## References

- ADR-039: Radical Simplification (State 1 architecture)
- ADR-042: Shared MAD Core Library (State 0 pattern)
- ADR-045: MAD Template Standard (security principles, healthcheck)
- ADR-046: MAD Groups and Database Storage (State 1 pattern)
- ADR-047: MCP Request Logging (logging requirements)
- REQ-000: Joshua26 System Requirements Specification
