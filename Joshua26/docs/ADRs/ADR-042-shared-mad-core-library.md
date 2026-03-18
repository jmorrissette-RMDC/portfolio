# ADR-042: Shared MAD Core Library

## Status
Accepted

## Date
2026-01-08

## Updated
2026-01-11

## Context

The Joshua26 ecosystem consists of multiple Modular Agent Daemons (MADs), each providing specific capabilities via MCP (Model Context Protocol). As defined in ADR-039, we have 15+ containers that need to:

1. Expose MCP tools over HTTP/SSE transport
2. Connect to the Sam relay (ADR-040)
3. Handle authentication, logging, health checks consistently

Currently, Brin (ADR-041) implements MCP directly using FastMCP. If every MAD reimplements this infrastructure independently, we face:
- Code duplication across containers
- Inconsistent error handling and logging
- Divergent configuration patterns
- Maintenance burden multiplied by container count

## Decision

We will create shared core libraries in `Joshua26/lib/` that wrap FastMCP and provide standardized infrastructure for all MADs:

### Directory Structure

```
Joshua26/
├── lib/
│   ├── mad-core-js/          # Node.js implementation
│   │   ├── package.json
│   │   ├── index.js
│   │   └── README.md
│   └── mad-core-py/          # Python implementation
│       ├── pyproject.toml
│       ├── mad_core/
│       │   ├── __init__.py
│       │   └── server.py
│       └── README.md
└── mads/
    ├── brin/                  # Uses mad-core-js
    ├── sam/                   # Uses mad-core-py
    └── ...
```

### Core Library Features

1. **MCP Server Wrapper**
   - Wraps FastMCP with standard configuration
   - Consistent tool registration API
   - Automatic HTTP/SSE transport setup on port 8002 (configurable)

2. **Health Check Endpoint**
   - `/health` endpoint for container orchestration
   - Reports server status, uptime, connected tools

3. **Structured Logging**
   - JSON logging format for aggregation
   - Log levels via environment variable
   - Request/response logging for debugging

4. **Configuration Management**
   - Environment variable patterns
   - Credential file loading from `/app/credentials/`
   - Service name identification

5. **Error Handling**
   - Consistent error response format
   - Automatic error logging
   - Graceful degradation patterns

### Usage Pattern

Node.js MAD:
```javascript
const { MadServer } = require('mad-core');

const server = new MadServer('brin', {
    description: 'GSuite MCP Server'
});

server.addTool({
    name: 'drive_list',
    description: 'List files in Google Drive',
    parameters: { ... },
    execute: async (params) => { ... }
});

server.start();
```

Python MAD:
```python
from mad_core import MadServer

server = MadServer('sam', description='MCP Relay')

@server.tool()
def relay_status() -> str:
    '''Get relay status'''
    return json.dumps({'status': 'ok'})

server.start()
```

### Dependency Management

MADs reference the local library:

```json
// package.json
{
  "dependencies": {
    "mad-core": "file:../../lib/mad-core-js"
  }
}
```

```toml
# pyproject.toml
[project]
dependencies = ["mad-core @ file:../../lib/mad-core-py"]
```

### Docker Integration

**Security Principle:** Root is only used for system packages and user creation. All application operations run as the service user.

Node.js example:
```dockerfile
FROM node:20-slim

ARG USER_NAME=brin
ARG USER_UID=2020
ARG USER_GID=2000

# ROOT: Only for system packages and user creation
RUN apt-get update && \
    apt-get install -y curl && \
    rm -rf /var/lib/apt/lists/* && \
    groupadd --gid $USER_GID joshua-services 2>/dev/null || true && \
    useradd --uid $USER_UID --gid $USER_GID -m -s /bin/bash $USER_NAME

# Switch to service user immediately
USER $USER_NAME

WORKDIR /app

# Copy with ownership (avoids chown -R)
COPY --chown=$USER_NAME:$USER_GID lib/mad-core-js/ /app/lib/mad-core-js/
COPY --chown=$USER_NAME:$USER_GID mads/brin/ /app/

# Install dependencies (will use local lib) - as service user
RUN npm install

CMD ["node", "server.js"]
```

Python example:
```dockerfile
FROM python:3.11-slim

ARG USER_NAME=sam
ARG USER_UID=2015
ARG USER_GID=2000

# ROOT: Only for system packages and user creation
RUN apt-get update && \
    apt-get install -y curl && \
    rm -rf /var/lib/apt/lists/* && \
    groupadd --gid $USER_GID joshua-services 2>/dev/null || true && \
    useradd --uid $USER_UID --gid $USER_GID -m -s /bin/bash $USER_NAME

# Switch to service user immediately
USER $USER_NAME

WORKDIR /app

# Copy with ownership
COPY --chown=$USER_NAME:$USER_GID lib/mad-core-py/ /app/lib/mad-core-py/
COPY --chown=$USER_NAME:$USER_GID mads/sam/ /app/

# Install dependencies - as service user
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "server.py"]
```

## Consequences

### Positive
- Single source of truth for MCP infrastructure
- Consistent behavior across all MADs
- Reduced boilerplate in each container
- Easier onboarding for new MADs
- Centralized bug fixes and improvements
- Containers run with least privilege (non-root)

### Negative
- Additional dependency to maintain
- Version coordination across MADs
- Local file dependencies require careful Docker COPY ordering

### Neutral
- Both JS and Python implementations needed (ecosystem uses both)
- MADs must follow library conventions

## State 1 Evolution: Configuration-Driven MCP Gateway Pattern

**Date Added:** 2026-01-31

As the architecture evolved to State 1 (functional decomposition into specialized containers), a new pattern emerged for MCP gateway containers that supersedes mad-core for new State 1 MADs.

### State 1 Architecture Pattern

State 1 MADs decompose into specialized containers:
- **`[mad]` (MCP Gateway)**: Public-facing MCP API layer, thin routing layer
- **`[mad]-langgraph`**: Internal processing engine (LangGraph flows)
- **`[mad]-[technology]`**: Backing services (postgres, redis, neo4j, etc.)

### Configuration-Driven Template Pattern

**For State 1 MCP Gateway containers ONLY:**

MCP gateways use a configuration-driven template pattern with standard libraries:

**Standard Libraries (in `lib/` directory):**
- **mcp-protocol-lib**: HTTP/SSE server, MCP protocol handling, tool registration
- **health-aggregator-lib**: Dependency health checking, status aggregation
- **logging-lib**: Structured JSON logging, stdout/stderr output
- **routing-lib**: HTTP client for langgraph/backing containers

**Template server.js (generic, < 20 lines):**
```javascript
const { MCPGateway } = require('mcp-protocol-lib');
const config = require('./config.json');

const gateway = new MCPGateway(config);
gateway.start();
```

**config.json (MAD-specific):**
```json
{
  "port": 6340,
  "tools": {
    "tool_name": {
      "target": "[mad]-langgraph:8000",
      "endpoint": "/invoke/tool_handler",
      "schema": { "input": {...}, "output": {...} }
    }
  },
  "dependencies": {
    "postgres": "[mad]-postgres:5432",
    "redis": "[mad]-redis:6379"
  }
}
```

**Benefits:**
- Eliminates duplicated gateway code across MADs
- Configuration changes don't require code changes
- Standard libraries ensure consistent behavior
- Easier testing and updates
- Faster MAD development (write config, not code)

### Usage Guidelines

**State 0 (Monolithic MADs):** Use mad-core-js or mad-core-py as documented above

**State 1 (Decomposed MADs):**
- **MCP Gateway (`[mad]`)**: Use configuration-driven template pattern with standard libraries
- **LangGraph (`[mad]-langgraph`)**: Does NOT use mad-core (no MCP exposure)
- **Backing Services (`[mad]-[technology]`)**: Does NOT use mad-core (official images)

**mad-core remains available** for State 0 monolithic MADs that have not been converted to State 1.

## References

- ADR-039: Radical Simplification (container list)
- ADR-040: MCP Relay Architecture (Sam)
- ADR-041: GSuite MCP Server (Brin)
- ADR-045: MAD Template Standard (security principles)
- ADR-046: MAD Groups and Database Storage (State 1 pattern)
- FastMCP: https://github.com/jlowin/fastmcp
- See `mads/_template/README.md` for State 1 template usage and `mads/_template/docs/` for library REQ specifications
