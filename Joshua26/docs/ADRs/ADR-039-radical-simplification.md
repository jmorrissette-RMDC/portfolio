# ADR-039: Radical Simplification

Status: Accepted
Date: 2026-01-04
Deciders: System Architect

## Context and Problem Statement

The Joshua architecture, as defined in ADRs 001-038, has grown to a level of complexity that hinders development velocity, especially when relying on LLM-driven implementation. Key issues identified include:

1. Excessive Complexity: The multi-environment storage model, granular MAD-specific deliverables, and premature enforcement of "best practices" create significant overhead.
2. Data Loss and Instability: LLM agents have proven unreliable in complex environments, often leading to data loss or corruption.
3. Lack of Foundational Capability: The focus on a distributed MAD ecosystem has come at the cost of developing a single, highly capable agent.

A radical simplification is required to establish a stable, resilient foundation from which a more complex architecture can be grown organically and safely.

## Decision

We will adopt a Radical Simplification of the V0 architecture, prioritizing stability, a single capable agent, and robust data protection.

### 1. Unified Storage and Data Protection

- Deprecate the multi-environment storage model and consolidate all storage onto the Irina server's 44TB RAID array
- ZFS Filesystem with automatic snapshots (hourly/daily/weekly)
- Safety Net: Containerized gitwatch service (Starret) for continuous, real-time commits

Storage Layout:
```
/mnt/storage/
├── projects/           # Git repositories
├── files/              # General shared storage
├── archive/            # Cold storage
├── databases/          # Stateful service data
└── models/             # AI models
```

Two-Volume Mounting Policy: All containers mount exactly two volumes - no more, no less:
- **storage** → /storage (Shared network storage via NFS, accessible across all hosts)
- **workspace** → /workspace (Local storage on each host, fast local disk)

**Volume Mounting Pattern:**
- **CORRECT:** `storage:/storage` and `workspace:/workspace` (mount root volumes)
- **WRONG:** `storage:/storage/databases/postgres` (subdirectory mounts)
- Subdirectory mounts cause entire host `/mnt/storage` to be mounted at incorrect container path
- Always mount the volume root, then create subdirectories inside container

**Storage vs Workspace Semantics:**
- **storage (shared)**: Shared network storage (NFS), accessible across all hosts
  - Use for: credentials, backups, shared configuration, cross-host data
  - Implementation: NFS mount from Irina to all compute nodes
  - Persistence: Long-term, backed up, shared

- **workspace (local)**: Local storage on each host (fast local disk)
  - Use for: MAD group databases, cache, temporary files, processing artifacts
  - Implementation: Local disk on each host (NOT shared via NFS)
  - Persistence: Long-term but local to host, not shared

**Workspace Clarification:** The workspace volume is for container-local persistent data that should survive container restarts but doesn't need to be shared across nodes. Examples:
- MAD group database data files (co-located for performance)
- CLI conversation history (~/.gemini, ~/.claude, etc.)
- Local caches and indexes
- Container-specific state that is backed up to /storage periodically

**Decision Rule:** "Does this need to be shared across hosts?" → Yes=storage, No=workspace

**Important:** Logs go to stdout/stderr (Docker captures), NOT to files in workspace. See ADR-047 for logging requirements.

Containers must NOT create additional Docker volumes. All persistent data goes through /storage or /workspace. If a container needs local persistent data (e.g., CLI history), it should store it under /workspace/[container-name]/ and optionally rsync to /storage for backup.

Bare Metal Mounting Policy: All servers (Irina, M5, and any future nodes) must mount Irina's storage at the same path used by containers:
- /mnt/storage/ on bare metal maps to the same location as /storage in containers
- This ensures consistent paths whether working inside or outside containers
- Implemented via NFS mount from Irina to all other servers
- Irina itself has direct access (local filesystem)

### 2. Two-Server Topology

| Server | Role | Key Resources | Container Types |
|--------|------|---------------|-----------------|
| Irina (192.168.1.110) | Storage | 44TB ZFS RAID | Databases, file services |
| M5 (192.168.1.120) | Compute | 5 GPUs, NVMe | Model serving, agents, inference |

Two-Network Model:
- joshua-net (10.0.1.0/24): Container-to-container communication (overlay)
- LAN (192.168.1.0/24): External access via host-bound ports

### 3. "Hub and Spoke" Architectural Model

- The Hub (Agent): The Joshua container (running Langflow) serves as the single, centralized agent for all reasoning, planning, and orchestration
- The Spokes (Tools): All other capabilities provided by simple, single-purpose service containers exposing functionality via lightweight MCP servers

### 4. De-prioritization of Premature Best Practices

Formal CI/CD, complex secrets management, and granular separation of concerns are de-prioritized in favor of simpler, "good enough" solutions that maximize development velocity.

### 5. Redefined V0 Service Architecture

The V0 ecosystem consists of 15 containers:

The Hub (1):
1. Joshua: The central agent (running Langflow)

Core Services (9):
2. Starret: gitwatch for automated safety net
3. Rogers: Redis for messaging, memory, and caching
4. Babbage: MongoDB
5. Codd: PostgreSQL
6. Henson-Qdrant: Qdrant for vector storage
7. Henson-Embed: BERT embedding model
8. Sutherland: Ollama for local LLM inference
9. Malory: Playwright for web browsing
10. Brin: MCP server for external documentation (Google Docs, Confluence)

External LLM Access (5):
11. Gemini-CLI
12. Claude-CLI
13. GPT-CLI
14. Grok-CLI
15. Aider-CLI

### 6. Standardized Hybrid Runtime Environment

Custom-built service containers use a hybrid runtime environment with both Python and Node.js, leveraging local package caching (per ADR-37 and ADR-38).

### 7. Permission Model: Security Groups and Service Accounts

Group-based permission model:
- joshua-admin: Human administrators (Full RW everywhere)
- joshua-agents: Agent containers (RW to agent code, RW shared files)
- joshua-services: Service containers (RO projects, RW shared files)
- joshua-readonly: Monitoring, logging (RO everywhere)

Each container runs as a dedicated Linux user assigned to the appropriate security group.

### 8. Minimal Repository Structure

Repository Layout:
```
Joshua26/
├── README.md
├── lib/
├── mads/               # All containers (hub and spokes)
├── docs/ 
├── docker-compose.yml
├── docker-compose.irina.yml
└── docker-compose.m5.yml
```


### 9. MCP Transport Protocol

All MCP servers use HTTP/SSE transport (not WebSocket or stdio).
- Health check: http://service:port/health
- MCP endpoint: http://service:port/mcp

The joshua_network WebSocket library from previous architecture is deprecated.

## Consequences

### Positive
- Drastic Reduction in Complexity
- Enhanced Data Safety via gitwatch
- Focused Development on single capable agent
- Stability and Reproducibility
- Clear Path Forward for V0 roadmap

### Negative
- Temporary Deferment of distributed multi-agent MAD ecosystem
- Slight Increase in Image Size for hybrid runtime

## Supersedes

- ADR-025: Multi-environment storage model replaced by unified ZFS-backed model
- ADR-020 (partially): V0 goal redefined from fleet of MADs to single capable agent
- Any ADRs enforcing premature "best practices" that conflict with simplification

---

## Workspace Volume Organization

Each container MUST have its own named subdirectory in the workspace volume to maintain clear separation and avoid conflicts.

**Required Folder Structure:**
```
/workspace/
├── <container-name>/          # One folder per container
│   ├── config/                 # Runtime configuration files
│   ├── tmp/                    # Temporary working files
│   ├── cache/                  # Application caches
│   └── logs/                   # Optional: short-term logs
└── README.md
```

**Naming Rules:**

1. **Container folder name must match container name exactly**
   - Example: `sam-irina` container → `/workspace/sam-irina/`
   - Example: `babbage` container → `/workspace/babbage/`

2. **Standard subfolders** (recommended but not required):
   - `config/` - Configuration files that containers modify at runtime
   - `tmp/` - Temporary files (can be cleared)
   - `cache/` - Performance caches (can be cleared)
   - `logs/` - Short-term logs (archive to `/storage/logs/` for long-term)

3. **Isolation**: Containers must NOT write to other containers' workspace folders

**Storage vs Workspace Decision Matrix:**

| Data Type | Location | Why |
|-----------|----------|-----|
| **Credentials** | `/storage/credentials/` | Shared across hosts, persistent, sensitive |
| **Backups** | `/storage/backups/` | Shared, backed up, long-term |
| **Shared config** | `/storage/config/` | Shared across hosts |
| **Source code** | `/storage/projects/` | Shared, version-controlled |
| **Models** | `/storage/models/` | Large, expensive to recreate, shared |
| **User files** | `/storage/files/` | Shared user data |
| **MAD group databases** | `/workspace/[mad-name]/databases/` | Local for co-located performance |
| **Runtime config** | `/workspace/[container]/config/` | Modified at runtime, local |
| **Temp files** | `/workspace/[container]/tmp/` | Ephemeral, local |
| **App caches** | `/workspace/[container]/cache/` | Performance, can rebuild, local |
| **Logs** | stdout/stderr (NOT files) | Docker captures, see ADR-047 |

**Database Storage Pattern (ADR-046):**
- **Database data files:** `/workspace/[mad-name]/databases/[technology]/data`
- **Database backups:** `/storage/backups/databases/[mad-name]/[technology]/`
- Rationale: MAD groups co-locate on single host for fast local I/O
- Backup strategy copies from workspace to storage regularly
