# ADR-040: MCP Relay Architecture

## Status
Accepted

## Date
2026-01-08

## Context

Claude Code communicates with MCP (Model Context Protocol) servers via stdio (standard input/output). However, we want to run MCP servers in Docker containers for isolation, portability, and easier deployment. Docker containers naturally expose HTTP endpoints, not stdio streams.

This creates an impedance mismatch: Claude Code expects stdio, containerized servers provide HTTP.

Additionally, we want the flexibility to:
- Connect to multiple MCP servers simultaneously
- Hot-reload server connections without restarting Claude Code
- Monitor and manage server connections dynamically

## Decision

We will build **Sam**, a Python-based MCP relay that:

1. **Exposes stdio to Claude Code** - Sam runs as a local process that Claude Code connects to via stdio
2. **Connects to HTTP/SSE backends** - Sam maintains SSE (Server-Sent Events) connections to containerized MCP servers
3. **Multiplexes tools** - Sam aggregates tools from multiple backend servers, prefixing them to avoid collisions
4. **Provides management tools** - Sam exposes relay_* tools for adding, removing, and monitoring backend connections

### Architecture

```
┌─────────────┐     stdio      ┌─────────┐     HTTP/SSE     ┌─────────────┐
│ Claude Code │ ◄────────────► │   Sam   │ ◄──────────────► │    Brin     │
└─────────────┘                │ (relay) │                  │  (GSuite)   │
                               │         │     HTTP/SSE     ├─────────────┤
                               │         │ ◄──────────────► │   Future    │
                               └─────────┘                  │   Servers   │
                                                            └─────────────┘
```

### Key Implementation Details

- **Transport**: SSE for server-to-client streaming, HTTP POST for client-to-server requests
- **Tool namespacing**: Backend tools are optionally prefixed (e.g., `brin_drive_list`)
- **Connection management**: Automatic reconnection with exponential backoff
- **Configuration**: YAML file for initial backends, plus runtime management via relay_* tools

## Consequences

### Positive
- Decouples Claude Code from server implementation details
- Enables containerized, isolated MCP servers
- Supports multiple simultaneous backend connections
- Allows runtime server management without restarting Claude Code
- Single configuration point for all MCP connections

### Negative
- Adds a layer of indirection (potential latency)
- Another component to maintain and monitor
- SSE connection management adds complexity

### Neutral
- Requires backends to implement HTTP/SSE transport (FastMCP supports this)
- Tool prefixing changes tool names from backend perspective

## Cross-Host Networking Requirements

**Date Added:** 2026-01-31

All inter-container communication (including Sam relay to backend servers) must use **container names via overlay network DNS**, never IP addresses.

### Networking Pattern

**CORRECT:**
```python
backend_url = "http://[container-name]:PORT"
# Examples:
# "http://brin:6350"
# "http://rogers-postgres:5432"
# "http://[mad]-langgraph:8000"
```

**WRONG:**
```python
backend_url = "http://172.18.0.5:6350"  # Hardcoded IP - DO NOT USE
```

### Rationale

**Overlay Network:** Joshua ecosystem uses `joshua-net` overlay network for cross-host container communication.

**Problem with IP addresses:**
- VXLAN FDB (Forwarding Database) entries can become stale when containers move between hosts
- IP addresses change during container restart or redeployment
- Breaks cross-host communication unpredictably

**DNS-based solution:**
- Overlay network provides DNS resolution for container names
- Works for both same-host and cross-host communication
- Automatically updates when containers move or restart
- Pattern: `http://[container-name]:PORT`

### Verification

All configuration files and code must use container names, not IP addresses:

```bash
# Search for hardcoded IPs (should find none)
grep -r "[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}" mads/[mad-name]/ --include="*.js" --include="*.py" --include="*.json"
```

### Implementation

**Sam relay configuration:**
```yaml
# config.yml - use container names
backends:
  brin:
    url: http://brin:6350  # Container name, not IP
    prefix: brin_
```

**MCP gateway config.json:**
```json
{
  "tools": {
    "tool_name": {
      "target": "[mad]-langgraph:8000"  // Container name
    }
  },
  "dependencies": {
    "postgres": "[mad]-postgres:5432"  // Container name
  }
}
```

## References

- MCP Specification: https://modelcontextprotocol.io
- Sam implementation: /home/aristotle9/Joshua26/mads/sam/
- FastMCP library: Used by backend servers for MCP implementation
- ADR-039: Radical Simplification (overlay network architecture)
