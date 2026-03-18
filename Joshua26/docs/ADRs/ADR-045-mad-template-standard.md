# ADR-045: MAD Template Standard

**Status:** Accepted
**Date:** 2026-01-10
**Updated:** 2026-01-15
**Deciders:** System Architect

## Context

ADR-039 established MCP as the communication protocol for all services. ADR-042 introduced the mad-core shared library. However, no single document defines the standard template that every MAD must follow.

## Decision

Every MAD in the Joshua ecosystem follows this template.

### Required Components

| Component | Implementation |
|-----------|----------------|
| MCP Server | mad-core-js or mad-core-py (State 0) OR config-driven template (State 1) |
| Endpoints | /health, /mcp (auto-provided by mad-core or mcp-protocol-lib) |
| health_check tool | First tool, auto-provided by mad-core |
| Service account | UID from registry.yml, GID 2001 (administrators) |
| Volumes | storage:/storage, workspace:/workspace |
| HEALTHCHECK | In Dockerfile (timing varies: 10s-120s start_period) |
| Version Pinning | All dependencies and base images pinned |
| Package Caching | packages/ directory (ADR-037) |
| umask | umask 000 for world-writable file creation |

**Note:** Both volumes are read-write. Workspace is for container-local persistent data (caches, temp files, runtime config) per ADR-039.

### Required Documentation

Every MAD must have these documentation artifacts:

| Document | Location | Purpose |
|----------|----------|---------|
| Requirements Doc | Google Docs (REQ-XXX) | Detailed requirements, tool specifications, integration points |
| README.md | mads/<name>/README.md | What it is, how to use it, configuration options |
| Registry Entry | registry.yml | UID, port, host, MCP endpoints |

**Requirements Doc (REQ-XXX):**
- Purpose and scope
- Tool specifications with parameters
- External dependencies and credentials
- Configuration options

**README.md:**
- Brief description
- Architecture (if multi-container)
- MCP tools table
- Configuration variables
- Usage examples
- Recovery procedures (if applicable)

**Registry Entry:**

For State 0 (monolithic) MADs:
```yaml
service-name:
  uid: XXXX
  gid: 2001  # administrators (all services)
  port: XXXX
  host: hostname
  description: Brief description
  mcp_endpoints:
    health: /health
    stream: /mcp
```

For State 1 (multi-container) MADs: All containers in the MAD group receive registry entries with shared UID. See ADR-043 (Centralized Identity) for complete State 1 registry pattern and field requirements.

### Tool Naming Convention

Tools MUST use a domain prefix to avoid ambiguity when aggregated via Sam. All MAD tools appear in a single namespace, so prefixes prevent collisions.

**Examples:**

| MAD | Prefix | Tool Names |
|-----|--------|------------|
| Malory | `browser_` | browser_navigate, browser_click, browser_screenshot |
| Brin | `drive_`, `docs_`, `sheets_`, `calendar_` | drive_list, docs_read, sheets_write |
| Henson | `qdrant_`, `embed_`, `vector_` | qdrant_create_collection, embed_text, vector_upsert |
| CLIs | `<provider>_` | gemini_exec, grok_exec, gpt_exec, claude_exec |

**Pattern:** `<domain>_<action>` or `<service>_<action>`

### Sam Dynamic Tool Discovery

Sam (the MCP relay) supports dynamic tool discovery without requiring client session restarts:

- **Adding a MAD:** Use `relay_add_server` - tools are immediately available
- **Removing a MAD:** Use `relay_remove_server` - tools are immediately removed
- **Updating tools:** Use `relay_reconnect_server` - updated tool list is immediately available

This enables rapid deployment and testing cycles without disrupting active sessions.

### Directory Structure

```
mads/<name>/
├── Dockerfile
├── docker-compose.yml
├── package.json
├── README.md
└── js/
    └── server.js
```

For Python MADs, replace package.json with requirements.txt and js/ with python/.

### Minimal server.js

```javascript
import MadServer, { z } from '../lib/mad-core-js/index.js';

const SERVICE_NAME = 'service-name';
const PORT = XXXX;  // from registry.yml

const server = new MadServer(SERVICE_NAME, {
  description: 'What this MAD does',
  port: PORT
});

// Add domain-specific tools here (with prefix!)
server.addTool({
  name: 'domain_action',  // e.g., browser_navigate, drive_list
  description: 'What the tool does',
  parameters: z.object({
    param: z.string().describe('Parameter description')
  }),
  execute: async ({ param }) => {
    // Implementation
    return JSON.stringify({ success: true, result: '...' });
  }
});

server.start();
```

### Security Principles

**Root Usage:** Containers start as root by default. Root should ONLY be used for:
1. Installing system packages (apt-get, yum, apk, etc.) - OS-level packages that modify system directories
2. Creating users and groups

**Everything else runs as the service user:**
- Copying application files (use `COPY --chown`)
- Installing application dependencies (npm install, pip install, etc.)
- Running the application
- Installing user-cached dependencies (Playwright browsers, etc.)

**Never switch back to root after initial system setup.**

**umask Configuration:** All containers must set `umask 000` for world-writable file creation (777/666 default permissions).

Implementation varies by runtime:
- **Node.js**: `process.umask(0o000);` in server.js (after imports)
- **Python**: `os.umask(0o000)` in server.py/entrypoint.py (after imports)
- **Supervisord**: Must wrap with start.sh script setting `umask 000` (supervisord's umask directive doesn't work reliably)

Start scripts must be executable: `RUN chmod +x /app/start.sh`

Verification: `docker exec [container] cat /proc/1/status | grep Umask` should show `0000`

**Note:** Some directories (databases) may need stricter permissions (750/640) applied on the host after deployment. Most application files use the world-writable default.

### HEALTHCHECK Configuration

**Purpose:** Docker HEALTHCHECK monitors container process health, separate from application dependency health.

**Timing Guidelines:**
- `--interval=30s`: Check every 30 seconds (standard)
- `--timeout=3s`: Health check must respond within 3 seconds
- `--start-period`: Varies by service complexity
  - Simple services (API gateways): 10-30s
  - Standard services: 60s (recommended default)
  - Complex services (databases, embeddings): 90-120s
- `--retries=3`: Mark unhealthy after 3 consecutive failures

**Two-Layer Health Architecture:**
- **Docker HEALTHCHECK**: Lightweight process check, does NOT check dependencies
- **HTTP `/health` endpoint**: Application-level check, actively tests dependencies (MCP gateway only)

**Pattern:**
```dockerfile
HEALTHCHECK --interval=30s --timeout=3s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:PORT/health || exit 1
```

Adjust `start-period` based on initialization time. Services with slow startup (loading models, initializing databases) need longer start periods.

### Version Pinning Principle

**All versions must be pinned.** Containers must not break due to unexpected updates. Updates must be purposefully decided on, not automatic.

This applies to:

**Docker Base Images:**
```dockerfile
# WRONG - will break when node:20 updates
FROM node:20-slim

# CORRECT - explicit version
FROM node:20.11.0-slim
```

**Python Dependencies:**
```txt
# requirements.txt - WRONG (unpinned)
fastmcp
qdrant-client

# requirements.txt - CORRECT (pinned)
fastmcp==0.1.0
qdrant-client==1.7.0
```

**Node.js Dependencies:**
```json
// package.json - pin exact versions
{
  "dependencies": {
    "express": "4.18.2"  // Not "^4.18.2" or "~4.18.2"
  }
}
```

**Always commit lock files:**
- Python: `requirements.txt` with pinned versions
- Node.js: `package-lock.json` or `yarn.lock`

**Updating versions:**
- Test updates in development first
- Update version explicitly in dependency file
- Regenerate lock file
- Rebuild and test container
- Commit both dependency file and lock file

### Minimal Dockerfile

```dockerfile
FROM node:20.11.0-slim

ARG USER_NAME=servicename
ARG USER_UID=XXXX
ARG USER_GID=2001

# ROOT: Only for system packages and user creation
RUN apt-get update && \
    apt-get install -y curl && \
    rm -rf /var/lib/apt/lists/* && \
    groupadd --gid $USER_GID administrators 2>/dev/null || true && \
    useradd --uid $USER_UID --gid $USER_GID -m -s /bin/bash $USER_NAME

# Switch to service user immediately
USER $USER_NAME

WORKDIR /app

# Copy with ownership (avoids chown -R)
COPY --chown=$USER_NAME:$USER_GID lib/mad-core-js/ /app/lib/mad-core-js/
COPY --chown=$USER_NAME:$USER_GID mads/<name>/ /app/

# Application dependencies (as service user)
RUN npm install

# User-cached dependencies (as service user)
# e.g., RUN npx playwright install chromium

EXPOSE XXXX

HEALTHCHECK --interval=30s --timeout=3s --start-period=60s --retries=3 \
    CMD node -e "fetch('http://localhost:XXXX/health').then(r => r.ok ? process.exit(0) : process.exit(1)).catch(() => process.exit(1))"

CMD ["node", "js/server.js"]
```

**Python variant:**

```dockerfile
FROM python:3.11.7-slim

ARG USER_NAME=servicename
ARG USER_UID=XXXX
ARG USER_GID=2001

# ROOT: Only for system packages and user creation
RUN apt-get update && \
    apt-get install -y curl && \
    rm -rf /var/lib/apt/lists/* && \
    groupadd --gid $USER_GID administrators 2>/dev/null || true && \
    useradd --uid $USER_UID --gid $USER_GID -m -s /bin/bash $USER_NAME

# Switch to service user immediately
USER $USER_NAME

WORKDIR /app

# Copy with ownership
COPY --chown=$USER_NAME:$USER_GID lib/mad-core-py/ /app/lib/mad-core-py/
COPY --chown=$USER_NAME:$USER_GID mads/<name>/ /app/

# Application dependencies (as service user)
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE XXXX

HEALTHCHECK --interval=30s --timeout=3s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:XXXX/health || exit 1

CMD ["python", "server.py"]
```

### Docker Compose Configuration

**Master File Pattern:** All service definitions exist in the master `docker-compose.yml` at the project root. Never create MAD-specific docker-compose.yml files.

**Build Context:** Must be `.` (project root), not `mads/[mad-name]`. This allows Dockerfile to access shared libraries and other MADs.

**Dockerfile COPY paths:** Must be relative to project root, e.g., `COPY mads/[mad-name]/...`

**Example service definition:**

```yaml
services:
  service-name:
    build:
      context: .  # Project root, not mads/<name>
      dockerfile: mads/<name>/Dockerfile
    image: joshua26/service-name
    container_name: service-name
    restart: unless-stopped
    networks:
      - joshua-net
    ports:
      - "XXXX:XXXX"
    volumes:
      - storage:/storage
      - workspace:/workspace
    env_file:
      - /mnt/storage/credentials/api-keys/xxx.env  # if needed

networks:
  joshua-net:
    external: true

volumes:
  storage:
    external: true
  workspace:
    external: true
```

## Consequences

- All MADs have consistent structure and documentation
- New MADs can be created by copying template and adding domain tools
- mad-core provides baseline functionality (health check, MCP transport)
- Questions like "should X have MCP?" are answered: yes, everything does
- Tool names are unambiguous when aggregated via Sam
- Containers run with least privilege (non-root service accounts)
- User-specific caches work correctly at runtime
- Deployment and testing is streamlined via Sam's dynamic discovery

## References

- ADR-039: Radical Simplification (MCP transport, workspace usage)
- ADR-040: MCP Relay Architecture (Sam)
- ADR-042: Shared MAD Core Library
- ADR-043: Identity Management (UIDs)
- ADR-044: Credentials Management
