# ADR-038: Hybrid Runtime Package Caching For MCP Servers

Status: Accepted (Supersedes ADR-037 for MCP-specific containers)
Date: 2026-01-01
Deciders: System Architect

## Context and Problem Statement

While implementing MCP (Model Context Protocol) server support in Langflow, we encountered critical issues with Python-based MCP filesystem servers:

1. Malicious PyPI Packages: The mcp-server-filesystem package on PyPI (version 0.1.0) is not official and contains malicious code that launches calculator applications
2. No Official Python Implementation: Anthropic's official MCP servers are Node.js packages under the @modelcontextprotocol namespace
3. Runtime Timeout Issues: Using uvx to run MCP servers results in 3+ second dependency resolution times, exceeding Langflow's initialization timeout
4. Dual Runtime Requirements: Python is needed for AI/ML workloads, but Node.js is required for official MCP infrastructure

The original ADR-037 addressed Python package caching but did not account for Node.js/npm requirements or MCP-specific tooling needs.

## Decision

We will adopt a hybrid runtime approach that supports both Python and Node.js package caching for containers requiring MCP server integration. This pattern:

1. Adds Node.js LTS to Python-based containers that need MCP servers
2. Pre-installs official MCP packages during build to avoid runtime downloads
3. Implements npm package caching parallel to the existing pip caching pattern
4. Uses official Anthropic packages from the @modelcontextprotocol namespace

### Core Principle

MCP servers are infrastructure, not application code. They should be baked into the image at build time, not resolved at runtime.

## Implementation Pattern

### 1. Directory Structure

```
project/
├── packages/              # Python packages (from ADR-037)
├── node_modules/          # npm packages cache
├── requirements.txt       # Python dependencies
├── package.json           # Node.js dependencies
├── package-lock.json      # npm lockfile
├── Dockerfile             # Hybrid runtime setup
└── docker-compose.yml
```

### 2. Package Configuration

package.json (Node.js dependencies):
```json
{
  "dependencies": {
    "@modelcontextprotocol/server-filesystem": "^2025.12.18",
    "@modelcontextprotocol/server-everything": "^2025.12.18",
    "@wonderwhy-er/desktop-commander": "^0.2.28"
  }
}
```

### 3. Dockerfile Pattern

- Install Node.js LTS alongside Python
- Copy and install Node.js dependencies from cache
- Copy and install Python dependencies from cache (ADR-037 pattern)
- Pre-install MCP packages globally

### 4. MCP Server Configuration in Langflow

Filesystem Access (Official Anthropic):
- Command: npx
- Arguments: -y @modelcontextprotocol/server-filesystem /

Desktop Commander (Terminal + Advanced File Operations):
- Command: npx
- Arguments: -y @wonderwhy-er/desktop-commander

Note: Because packages are pre-installed globally, npx executes instantly without downloads.

## Consequences

### Positive
- Security: Uses official @modelcontextprotocol namespaced packages, avoiding malicious PyPI typosquats
- Performance: Pre-installed packages eliminate 3+ second timeout issues
- Reliability: No runtime dependency resolution means deterministic, reproducible environments
- Offline Capability: Both Python and Node.js packages work without internet
- Ecosystem Access: Unlocks 60%+ of MCP servers that are Node.js-only

### Negative
- Image Size: Node.js adds ~180-200MB to base image
- Complexity: Must maintain both pip and npm dependency trees
- Dual Package Managers: Security advisories must track both PyPI and npm

## MCP Packages Used

### @modelcontextprotocol/server-filesystem (Official Anthropic)
- Purpose: Secure filesystem access for AI agents
- Capabilities: read, write, search, list, delete files within specified directories
- Security: Respects .gitignore patterns, sandboxed to specified paths

### @wonderwhy-er/desktop-commander (Community - Eduard Ruzga)
- Purpose: Terminal operations and advanced file editing for AI agents
- Capabilities: Terminal Access, Advanced Search (ripgrep), File Operations, Block Editing

### @modelcontextprotocol/server-everything (Official Anthropic)
- Purpose: Reference implementation exercising all MCP protocol features

## Migration from ADR-037

For Pure Python Projects: Continue using ADR-037 pattern (pip-only caching)

For MCP-Enabled Projects: Adopt ADR-038 pattern:
1. Add package.json with MCP dependencies
2. Create node_modules/.gitignore
3. Update Dockerfile to install Node.js
4. Pre-install MCP packages globally
5. Configure Langflow to use npx commands

## Related Decisions
- ADR-037: Local Package Caching For Docker Builds
- ADR-027: 12-Factor App Methodology
- ADR-028: Core Coding Practice Standards

## Appendix A: Investigation - Discovery of Malicious PyPI Package

Investigation revealed that the mcp-server-filesystem package on PyPI was fake/malicious:
- No author, no homepage, gibberish summary ("poneglyph")
- Code launches GUI calculator apps on import
- Official MCP servers from Anthropic are Node.js packages ONLY

## Appendix B: Technical Details

Why uvx Failed:
- Dependency resolution took 3+ seconds
- Langflow expects MCP server initialization in <3 seconds
- The package uvx was trying to run was fake/malicious

NPM Package Pre-installation Benefits:
- Packages installed once during image build
- npx finds package in global location, executes in milliseconds
- Langflow initialization succeeds

## Testing Results (2026-01-01)

Desktop Commander (@wonderwhy-er/desktop-commander): VERIFIED WORKING
- Successfully initializes and connects to Langflow
- Capabilities Confirmed: Terminal access, file operations, process management

Recommendation: Use Desktop Commander as primary MCP server for joshua ecosystem orchestration.
