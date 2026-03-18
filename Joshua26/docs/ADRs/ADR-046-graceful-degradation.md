# ADR-046: Graceful Degradation

Status: Accepted
Date: 2026-01-10

## Context

Joshua26 consists of multiple MADs that provide different services. Some provide shared infrastructure (databases, caches) while others provide application functionality.

A naive architecture creates hard dependencies where failure of one service cascades to dependents.

## Decision

MADs must not have hard dependencies on peer MADs, **except within MAD groups** (bounded contexts).

### MAD Groups (Bounded Contexts)

A **MAD group** is a collection of tightly-coupled containers that share a private network and operate as a unified service with internal hard dependencies.

**Rules:**

1. **Within MAD group (private network):**
   - Hard dependencies acceptable
   - Containers can require each other to function
   - Graceful **recovery** required (retry with exponential backoff)
   - Containers must start successfully even if dependencies not ready
   - System must recover automatically when dependencies return
   - Example: rogers-langgraph requires rogers-postgres, rogers-neo4j

2. **External to MAD group (public network / joshua-net):**
   - Graceful **degradation** required
   - MAD group must not fail to start when external MADs unavailable
   - MAD group may operate in degraded mode
   - Example: Sutherland unavailable → Rogers-MCP queries still work, Mem0 processing queued

**Example MAD Group:** Rogers Conversation Service
- **Private network:** rogers-private-net
- **Public network:** joshua-net
- **Components:** rogers-mcp, rogers-langgraph, rogers-postgres, rogers-neo4j, rogers-redis
- **Internal dependencies:** rogers-langgraph requires rogers-postgres (hard dependency, graceful recovery)
- **External dependencies:** rogers-langgraph calls Hamilton, Sutherland (graceful degradation)
- **Boundary:** rogers-mcp bridges both networks (exposes MCP tools to joshua-net, accesses private network internally)

**Registry Entries:** All containers in MAD group receive registry entries with shared UID. See ADR-043 (Centralized Identity) for State 1 registry pattern and field requirements.

### Principles

1. **Independent Operation (MAD groups)**: Each MAD or MAD group must be capable of basic operation when peer MADs are unavailable. A MAD may operate in degraded mode but must not fail to start.

2. **Shared Services are Optimizations**: Shared databases (Codd/PostgreSQL, Babbage/MongoDB), caches (Rogers/Redis), and vector stores (Henson/Qdrant) improve performance but are not requirements for basic operation. Exception: MAD groups may have internal shared services with hard dependencies.

3. **Local State Storage**: Each MAD group stores database data in `/workspace/[mad-name]/databases/` for co-located performance. Backups are stored in `/storage/backups/databases/[mad-name]/`.

4. **Host Affinity**: MAD groups co-locate on a single host for optimal performance (fast local workspace I/O).

5. **Graceful Recovery vs Degradation**:
   - **Recovery:** Within MAD group, retry connections with backoff, don't crash loop
   - **Degradation:** External dependencies, queue work and continue when dependencies return

### Examples

**Joshua (Langflow):**
- Stores state in /storage/databases/langflow/
- Uses SQLite (Langflow default), not Codd
- Operates independently of all other MADs

**Brin (GSuite):**
- Could use Rogers (Redis) for caching
- Must operate without cache if Rogers unavailable

**CLI Wrappers:**
- Stateless, fully independent

### MAD Group Database Storage Policy

**Date Added:** 2026-01-31

**Database Data Files:** Stored in `/workspace/[mad-name]/databases/[technology]/data` (local to host)

**Database Backups:** Stored in `/storage/backups/databases/[mad-name]/[technology]/` (shared, backed up)

**Rationale:**
- MAD groups are deployment units that co-locate on a single host for performance
- workspace provides fast local I/O for co-located database containers
- storage provides shared, backed-up location for database backups
- Backup strategy copies from workspace to storage regularly

**Examples:**

PostgreSQL:
- Data: `/workspace/[mad-name]/databases/postgres/data`
- Backups: `/storage/backups/databases/[mad-name]/postgres/`

Redis:
- Data: `/workspace/[mad-name]/databases/redis/`
- Backups: `/storage/backups/databases/[mad-name]/redis/`

Neo4j:
- Data: `/workspace/[mad-name]/databases/neo4j/data`
- Backups: `/storage/backups/databases/[mad-name]/neo4j/`

**MAD-specific subdirectory pattern** (`/workspace/[mad-name]/`) prevents conflicts when multiple MAD groups share the same host.

**Host directory permissions:** Database directories require stricter permissions (750/640) applied on the host after container creates directories. This is applied post-deployment on the host filesystem.

**Backup Strategy:** Regular backup jobs copy database data from workspace to storage for long-term persistence and disaster recovery.

## Consequences

### Benefits
- Higher system availability
- Easier development and testing
- Clearer failure boundaries
- No startup ordering required

### Trade-offs
- Some data duplication
- Cross-MAD queries require explicit integration
