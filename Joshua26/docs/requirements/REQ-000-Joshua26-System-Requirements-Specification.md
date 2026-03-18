# Joshua26 System Requirements Specification

**Document ID:** REQ-000
**Version:** 1.0 (Draft)
**Date:** 2026-01-31
**Status:** Draft - Requirements Definition
**Purpose:** Define comprehensive system requirements for Joshua26 ecosystem components

## Document Purpose and Scope

This document serves as the **authoritative specification** for what constitutes a compliant component in the Joshua26 ecosystem. It defines:

1. **System Requirements** - What must be true for components to function correctly
2. **Architectural Patterns** - State 0 vs State 1, container types, composition models
3. **Compliance Principles** - How requirements are verified and exceptions handled
4. **Audit Framework** - How to use these requirements to verify component compliance

**Relationship to Other Documents:**
- **ADRs (Architecture Decision Records)**: Source of architectural principles and decisions
- **Audit Checklist Template**: Verification instrument derived from these requirements
- **HLD Documents**: High-level designs that must align with these requirements
- **REQ Documents**: Component-specific requirements that must comply with this specification

**Target Audience:**
- System architects designing new components
- Developers implementing components
- Auditors verifying component compliance
- Operations teams deploying and maintaining components

---

## Guiding Philosophy: Code for Clarity

All code in the Joshua26 ecosystem, whether written by humans or LLMs, MUST be clear, readable, and maintainable. This is not a suggestion, but a core requirement. The system's long-term health and the efficiency of both human and AI developers depend on a codebase that is easy to understand. This philosophy underpins all requirements that follow. Key principles include:

-   **Write Descriptive Names:** Use clear, unambiguous names for variables, functions, and classes.
-   **Keep Functions Small and Focused:** Each function should do one thing and do it well.
-   **Comment the *Why*, Not the *What*:** Use comments to explain complex logic or design choices, not to state the obvious.

---

## Part 1: Compliance Principles

These principles govern how requirements are verified and how exceptions are handled.

**Approval Authority:** All N/A determinations and exceptions must be approved by Joshua/Aristotle9.

**Severity:** All requirements are mandatory. There are no non-blocking violations - any non-compliance is a blocker.

### 1. Complete Coverage - No Items Skipped
Every single checklist item must be explicitly addressed. There is no blanket decision-making where an entire category can be dismissed without justification.

**Examples of what NOT to do:**
- "This is just a database, so I'll skip all the logging items"
- "This doesn't use Python, so I'll mark all Python items as N/A without documenting why"

**What TO do:**
- Evaluate every item individually
- Document the reason for every N/A or exception
- Seek explicit user approval for N/A or exception determinations

### 2. N/A Requires Justification and Approval
Marking an item as "N/A" (Not Applicable) is not a casual decision. Each N/A must have:
- A clear, specific reason why it doesn't apply
- Explicit user approval (can be blanket approval for related items)
- Documentation in the audit report

**Valid N/A example:**
- Items about Python package caching when the component only uses Node.js
- Must list all Python-related items and get approval: "Items X, Y, Z are N/A because this is a Node.js-only component. Approve?"

### 3. Exceptions Require Justification and Approval
When a component cannot comply with a requirement, an exception must be:
- Documented with specific reasons
- Include risk mitigation strategies
- Receive explicit user approval
- Recorded in REQ-000-exception-registry (Approved Exceptions)

**Exception process:**
1. Identify the conflict
2. Explain why compliance is impossible or impractical
3. Describe mitigation measures
4. Request approval
5. Document in REQ-000-exception-registry

### 4. Blanket Approval is Allowed (But Must Be Explicit)
For efficiency, you can request approval for multiple related items at once:
- List all items explicitly (by number/description)
- Provide a single reason that applies to all
- Get user approval
- Document that reason for each item in the audit

**Example:**
"Items 1, 2, 3, 4, 5 (all Python package caching requirements) should be marked N/A because this component uses only Node.js and has no Python dependencies. Do you approve?"

### 5. Principle-Based, Not ADR-Based
The checklist is organized by **what matters in practice**, not by strict ADR structure.

**This means:**
- Focus on "does logging work correctly?" not "does this comply with ADR-047?"
- The ADRs are the source of the principles
- The checklist groups requirements logically by function
- ADR numbers are references, not the organizing structure

---

## Part 2: Architectural Context

Understanding the architectural patterns is essential for applying requirements correctly.

### Container Architecture Patterns

**Architecture States:**

- **State 0 (Legacy/Deprecated):** Monolithic single container. No new pMADs built this way.
- **State 1 (Transitional):** Functional decomposition — Node.js MCP gateway + langgraph container + backing services. Current template pattern. All existing deployed pMADs are State 1 or higher.
- **State 2 (Current state of platform pMADs):** OTS infrastructure only — nginx gateway + langgraph container + official backing service images. Peer calls via langchain-mcp-adapters. Imperator pattern mandatory. Current state of deployed platform pMADs (Rogers, Sutherland, Starret, Henson, Malory, etc.).
- **State 3 (Current target):** Separates AE (infrastructure) from TE (intelligence). The AE is a stable bootstrap kernel (MCP routing, peer proxy, observability, `install_stategraph()`) that almost never changes. Both AE StateGraph packages and TE (Imperator) packages are published to Alexandria as versioned Python wheels and loaded at runtime without restart. Kaiser is the first implementation. eMADs (Hopper, etc.) are TE-only library packages with no AE, hosted by a State 3 pMAD. All pMADs migrate toward State 3 as their infrastructure stabilises. See §7.13 and HLD-state3-mad.md.

**Container Types:**

1. **`[mad]` - MCP Gateway Container**
   - Public-facing MCP API layer
   - Uses configuration-driven template with standard libraries (mcp-protocol-lib, health-aggregator-lib, logging-lib, routing-lib) + config.json
   - Exposes tools via HTTP/SSE
   - Thin layer, delegates to langgraph for processing
   - All tool routing logic in config.json, minimal code in server.js (< 20 lines)
   - Example: `[mad]` exposes MCP tools
   - **Full checklist compliance required**

2. **`[mad]-langgraph` - Processing/Orchestration Container**
   - Internal processing engine, NOT public-facing
   - Does NOT use mad-core (no MCP exposure)
   - Python or Node.js depending on processing needs
   - Handles workflows, orchestration, programmatic logic
   - Example: `[mad]-langgraph` handles processing
   - **Partial checklist compliance** (no MCP, communication, or Sam integration)

3. **`[mad]-[technology]` - Backing Service Container**
   - Official images (postgres, redis, neo4j, playwright, etc.)
   - Standard infrastructure services
   - Example: `[mad]-postgres`, `[mad]-redis`
   - **Minimal checklist compliance** (mostly N/A, use official defaults)

**Auditing Approach:** Each container requires its own audit against its own audit checklist.

---

## Part 3: System Requirements by Category

Requirements are organized by **functional concerns** - what actually needs to work in practice. Each category defines requirements that components must meet.

### 1. Build System
**Purpose:** Ensure components can build offline, reproducibly, without external dependencies.

**Requirements:**

**1.1 Python Package Caching** (ADR-037)
- **What:** All Python dependencies must be cached locally in `packages/` directory
- **Detail:**
  - `requirements.txt` with pinned versions (use `==`, not `>=` or `~=`)
  - All packages downloaded and stored in `packages/`
  - `packages/.gitignore` configured to exclude packages from git
  - Dockerfile uses `COPY packages/ /tmp/packages/` and `pip install --find-links=/tmp/packages/ --prefer-binary`
- **Verification:** Build container with network disabled - must succeed
- **Example:** `flask==2.3.2` not `flask>=2.0`

**1.2 Node.js Package Caching** (ADR-037)
- **What:** All Node.js dependencies must be cached locally in `packages/` directory
- **Detail:**
  - `package.json` with exact versions (no `^` or `~`)
  - `package-lock.json` committed to repository
  - All packages downloaded and stored in `packages/`
  - Dockerfile uses `npm ci --cache /tmp/packages/ --prefer-offline`
- **Verification:** Build container with network disabled - must succeed
- **Example:** `express: "4.18.2"` not `express: "^4.18.0"`

**1.3 System Package Caching** (ADR-037)
- **What:** System packages (apt/apk) must be cached locally
- **Detail:**
  - `packages/apt/*.deb` or `packages/apk/*.apk` directory with cached packages
  - Download script exists (e.g., `download-packages.sh`)
  - Dockerfile uses `dpkg -i` with fallback to `apt-get install`
- **Verification:** Build container with network disabled - must succeed

**1.4 Docker Base Image Caching** (ADR-037)
- **What:** Base Docker images must be available locally or cached
- **Detail:**
  - Pinned base image version in Dockerfile (e.g., `FROM node:20.11.0-slim`)
  - Base image .tar file in `packages/docker/` OR available in local Docker cache
  - Build documentation includes `docker load` step if using .tar files
- **Verification:** Base image version is pinned (not `latest` or untagged)
- **Example:** `FROM python:3.11.7-slim` not `FROM python:3.11` or `FROM python`

**1.5 Runtime Binary Caching** (ADR-037)
- **What:** Runtime binaries (Playwright browsers, etc.) must be cached locally
- **Detail:**
  - Binaries cached in `packages/playwright/` or similar
  - Dockerfile copies cached binaries to correct location
  - No runtime downloads during container startup
- **Verification:** Start container with network disabled - must succeed

**1.6 Hybrid Runtime Environments** (ADR-038)
- **What:** Containers using BOTH Python AND Node.js must cache both runtimes' packages
- **Detail:**
  - All Python package caching requirements (1.1) apply
  - All Node.js package caching requirements (1.2) apply
  - Both runtimes installed and available at container startup
- **Verification:** Both `python --version` and `node --version` succeed; build works offline

**1.7 Version Pinning** (ADR-045)
- **What:** All dependencies must be locked to specific versions
- **Detail:**
  - Docker base image: pinned version tag
  - Python: `==` in requirements.txt
  - Node.js: exact versions (no `^`, `~`) in package.json
  - Lock files committed (package-lock.json, requirements.txt)
- **Verification:** No unpinned versions in any dependency file
- **Example:** `redis==5.0.1` and `express: "4.18.2"` and `FROM node:20.11.0-slim`

**1.8 Code Formatting (Python)**
- **What:** All Python code **MUST** be formatted with `black`.
- **Verification:** The code must pass a `black --check .` command without errors.

**1.9 Code Linting (Python)**
- **What:** All Python code **MUST** pass a `ruff check .` linting analysis without errors.
- **Detail:** This includes adhering to standard rules that prevent common bugs and anti-patterns.

**1.10 Unit Testing Mandate**
- **What:** All new programmatic logic **MUST** be accompanied by corresponding unit tests.
- **Detail:** Logic within `[mad-name]-langgraph` service modules (e.g., `database_service.py`, `api_client.py`) **MUST** have `pytest` tests covering, at a minimum, the primary success path ("happy path") and known common error conditions.
- **Verification:** During code review, new functions must have corresponding test files and test cases.

**Key Principle:** Don't re-download dependencies during build/runtime - rely on local caching for speed and internet efficiency. Versions pinned to prevent unexpected breakage.

### 2. Runtime Security and Permissions
**Purpose:** Ensure components run with least privilege, proper user/group configuration, and correct file permissions.

**Requirements:**

**2.1 Root Usage Pattern** (ADR-042, ADR-045)
- **What:** Root privileges used ONLY for system package installation and user creation
- **Detail:**
  - Root operations limited to: installing apt/apk packages, creating service user/group
  - USER directive must immediately follow user creation
  - No application code, file operations, or runtime tasks as root
  - COPY --chown used instead of chown -R
- **Verification:** Check Dockerfile - all application operations after USER directive
- **Example:** Root installs packages, creates user, then `USER [mad-name]` before copying app code

**2.2 Service Account Creation** (ADR-043)
- **What:** Container must run as a dedicated service account with UID from registry.yml
- **Detail:**
  - UID assigned per registry.yml (e.g., rogers=2002, hamilton=2036)
  - User created in Dockerfile: `useradd --uid $USER_UID --gid $USER_GID $USER_NAME`
  - User name matches service name
  - No running as root or generic uids (1000, etc.)
- **Verification:** `docker exec <container> id` shows correct UID/GID, user name matches service
- **Example:** Service runs as UID 2002, user "[mad-name]"

**2.3 Group Membership** (ADR-043, MAD consolidation)
- **What:** ALL services use GID 2001 (administrators group)
- **Detail:**
  - Primary GID: 2001 (administrators)
  - Group created in Dockerfile: `groupadd --gid 2001 administrators`
  - NOT GID 2000 (joshua-services) - that's obsolete
  - Supplementary groups via `group_add` in docker-compose.yml when needed to read host files
- **Verification:** `docker exec <container> id` shows gid=2001(administrators)
- **Example:** All services: `ARG USER_GID=2001` and `groupadd --gid $USER_GID administrators`

**2.4 umask Configuration** (MAD consolidation)
- **What:** umask 000 set in all containers for world-writable file creation
- **Detail:**
  - umask 000 enables 777/666 default permissions
  - Implementation varies by runtime:
    - **Node.js**: `process.umask(0o000);` in server.js (after imports)
    - **Python**: `os.umask(0o000)` in server.py/entrypoint.py (after imports)
    - **Supervisord**: Wrap with start.sh script setting `umask 000` (supervisord's umask directive doesn't work)
  - Start scripts must be executable: `RUN chmod +x /app/start.sh`
- **Verification:** `docker exec <container> cat /proc/1/status | grep Umask` shows 0000
- **Example:** Node.js adds `process.umask(0o000);` at top of server.js

**2.5 File Ownership in Dockerfile** (ADR-042, ADR-045)
- **What:** Use COPY --chown instead of chown -R for setting file ownership
- **Detail:**
  - Pattern: `COPY --chown=$USER_NAME:$USER_GID <src> <dest>`
  - Avoids separate chown layer (saves space, faster builds)
  - Sets ownership at copy time, not after
- **Verification:** Dockerfile uses `COPY --chown` for all application files
- **Example:** `COPY --chown=[mad-name]:2001 mads/[mad-name]/js/ /app/js/`

**2.6 Post-Deployment Permission Adjustment** (MAD consolidation)
- **What:** Some directories may need stricter permissions after container is running
- **Detail:**
  - Database directories: 770/660 or 750/640 (owner+group only)
  - PostgreSQL specifically requires 750/640 for data directory
  - Applied on host after container creates directories
  - Most application files: 777/666 (default from umask 000)
- **Verification:** Check database directory permissions on host: `ls -la /mnt/storage/databases/`
- **Example:** PostgreSQL: `chmod 750 /mnt/storage/databases/postgres` after deployment

**Key Principle:** Root only for system setup. Everything runs as non-root with GID 2001 (administrators). umask 000 for world-writable defaults. Supervisord needs start.sh wrapper.

### 3. Storage and Data
**Purpose:** Ensure data persistence, correct volume mounting, proper organization, and secure credential management.

**Requirements:**

**3.1 Two-Volume Mounting Policy** (ADR-039)
- **What:** Containers must mount exactly two volumes: storage and workspace
- **Detail:**
  - storage volume: shared network storage (NFS), accessible across all hosts
  - workspace volume: local storage on each host (fast local disk)
  - No additional volumes beyond these two
  - Both volumes required for all containers
  - Both volumes are persistent (not ephemeral)
- **Verification:** docker-compose.yml shows exactly two volume mounts per container
- **Example:** `volumes: [storage:/storage, workspace:/workspace]`
- **Exception — Official images with VOLUME declarations:** Some official Docker images (postgres, neo4j, redis) declare `VOLUME` paths in their Dockerfiles. If no explicit mount is provided at a declared VOLUME path, Docker creates an anonymous volume there — which is untracked, unmanageable, and violates this policy. The only way to suppress anonymous volume creation is to provide a bind mount at the exact declared path. Containers using such images **must** use bind mounts at each declared VOLUME path rather than the named `workspace` volume. This deviation requires a formal approved exception registered in REQ-000-exception-registry before deployment. See ADR-052 for the full pattern and `docker inspect <image> --format='{{.Config.Volumes}}'` to identify whether an image is affected.

**3.2 Volume Mount Correctness** (ADR-039, MAD consolidation)
- **What:** Must mount root volumes, NOT subdirectories
- **Detail:**
  - Correct: `storage:/storage` (mounts entire storage volume at /storage)
  - WRONG: `storage:/storage/databases/postgres` (mounts entire /mnt/storage root at wrong path)
  - Subdirectory mounts cause entire host `/mnt/storage` to be mounted at incorrect container path
  - Always mount the volume root, then create subdirectories inside container
  - Same applies to workspace: mount `workspace:/workspace` not subdirectories
- **Verification:** docker-compose.yml volume mounts are `storage:/storage` and `workspace:/workspace`
- **Example:** `volumes: ["storage:/storage", "workspace:/workspace"]` NOT `"storage:/storage/databases/rogers"`

**3.3 Workspace Folder Organization** (ADR-039)
- **What:** Each container creates its own workspace subdirectory
- **Detail:**
  - Pattern: `/workspace/<container-name>/` for container-specific files
  - Container creates directory at startup if needed
  - No conflicts between containers sharing workspace volume
  - Workspace is local to host - fast I/O for co-located containers
- **Verification:** Container startup creates `/workspace/<container-name>/` directory
- **Example:** Containers create `/workspace/[container-name]/`

**3.4 Storage vs Workspace Decision** (ADR-039, ADR-046)
- **What:** Data placement based on one rule: does it need to be shared across hosts?
- **Detail:**
  - **Decision rule:** "Does this need to be shared across hosts?" → Yes=`/storage`, No=`/workspace`
  - `/storage` is a network share (NFS). Only put things there that genuinely need to be accessible from multiple hosts. If it doesn't need to be shared, there is no reason to put it on a network share.
  - **storage (shared across hosts)**: Credentials, backups, package caches, model files, any data that multiple MADs or hosts must read/write
  - **workspace (local to host)**: MAD databases, configuration files, cache, temporary files, processing artifacts — anything that belongs to a single MAD on a single host
  - Configuration files belong in `/workspace/[mad-name]/` — they are local to the MAD's host and do not need to be shared
  - Credentials are the exception: always in `/storage/credentials/` because they must be available across hosts and are managed centrally
  - Database backups go to `/storage/backups/` because backups must survive host failure
  - Logs go to stdout/stderr (Docker captures), NOT to files in workspace
- **Verification:** pMAD group database paths point to /workspace/<mad>/databases/, config files in /workspace/<mad>/, credentials in /storage/credentials/
- **Example:** PostgreSQL data: `/workspace/[mad-name]/databases/postgres/data`, config: `/workspace/[mad-name]/config/`, backups: `/storage/backups/databases/[mad-name]/postgres/`

**3.5 Credentials Management** (ADR-044)
- **What:** Credentials loaded from /storage/credentials/, never hardcoded
- **Detail:**
  - Pattern: `/storage/credentials/<service>/<credential-file>`
  - JSON or text files with secrets (API keys, passwords, tokens)
  - Loaded at container startup
  - No credentials in environment variables, Dockerfiles, or code
  - Example paths: `/storage/credentials/[mad-name]/api-key.json`
- **Verification:** Grep code for hardcoded secrets - must find none; startup logs show loading from /storage/credentials/
- **Example:** `const apiKey = JSON.parse(fs.readFileSync('/storage/credentials/[mad-name]/api-key.json'))`

**3.6 No Hardcoded Secrets** (ADR-044)
- **What:** No secrets in code, Dockerfiles, environment variables, or git
- **Detail:**
  - All secrets loaded from /storage/credentials/ at runtime
  - No ENV variables with secrets in docker-compose.yml
  - No secrets in .env files (which might be committed)
  - .gitignore includes credentials/ directory
  - Placeholder/example credentials can exist in docs, but never real secrets
- **Verification:** `git grep -i "password\|api.key\|secret\|token" -- '*.js' '*.py' '*.yml' 'Dockerfile*'` finds no real secrets
- **Example:** ❌ `ENV API_KEY=abc123` ✅ Load from `/storage/credentials/service/api-key.json`

**3.7 Database/State Storage Location** (ADR-046)
- **What:** pMAD group databases stored in workspace for co-located performance
- **Detail:**
  - **Database data files**: `/workspace/<mad-name>/databases/<technology>/data`
  - **Database backups**: `/storage/backups/databases/<mad-name>/<technology>/`
  - Pattern enables ppMAD groups to co-locate on single host for fast local I/O
  - PostgreSQL: data in `/workspace/[mad-name]/databases/postgres/data`, backups in `/storage/backups/databases/[mad-name]/postgres/`
  - Redis: data in `/workspace/[mad-name]/databases/redis/`, backups in `/storage/backups/databases/[mad-name]/redis/`
  - Neo4j: data in `/workspace/[mad-name]/databases/neo4j/data`, backups in `/storage/backups/databases/[mad-name]/neo4j/`
  - MAD-specific subdirectory prevents conflicts
  - Host directory permissions applied after deployment (750/640 for databases)
  - Backup strategy must copy from workspace to storage regularly
- **Verification:** Database configuration points to /workspace/<mad>/databases/<tech>/, backup scripts copy to /storage/backups/
- **Example:** PostgreSQL PGDATA: `/workspace/[mad-name]/databases/postgres/data` NOT `/storage/databases/postgres/data`

**Key Principle:** Exactly two volumes. Mount root volumes (storage:/storage), never subdirectories. Data organized by sharing needs (storage=shared across hosts, workspace=local to host). ppMAD groups use workspace for databases (co-located performance), storage for backups. Credentials never hardcoded. Logs go to stdout/stderr, not files.

### 4. Communication and Integration
**Purpose:** Ensure services can discover and communicate with components via MCP protocol.

**Requirements:**

**4.1 MCP Transport Protocol** (ADR-039, ADR-040)
- **What:** MCP must use HTTP/SSE transport, not WebSocket or stdio
- **Detail:**
  - Protocol: HTTP with Server-Sent Events (SSE) for streaming
  - NOT WebSocket (deprecated)
  - NOT stdio (local only, not network-accessible)
  - HTTP/SSE allows network discovery and relay compatibility
  - All MCP gateway containers expose HTTP/SSE endpoint
- **Verification:** MCP server listens on HTTP port, MCP endpoint responds to connections
- **Example:** MCP server on `http://[mad]:6340/mcp`

**4.2 MCP Endpoint Availability** (ADR-039, ADR-042, ADR-045, ADR-053)
- **What:** MCP gateway must expose required HTTP endpoints
- **Detail:**
  - `/health` endpoint: Health check (GET request returns 200 OK when healthy)
  - `/mcp` endpoint: MCP protocol endpoint for tool invocation
    - `GET /mcp`: Establishes SSE session for server→client messages
    - `POST /mcp?sessionId=xxx`: Routes message to existing SSE session (standard MCP)
    - `POST /mcp` (no sessionId): Sessionless mode — processes `tools/call` synchronously and returns JSON-RPC 2.0 response in body; used by peer gateways acting as MCP clients
  - `/peer/{peer-name}/{tool-name}` endpoint: Proxy tool call to a declared peer MAD (POST); enables langgraph containers on private networks to call peers on joshua-net via MCP JSON-RPC 2.0
  - `/peer/{peer-name}/v1/chat/completions` endpoint: Proxy OpenAI-compatible chat completions to a declared peer MAD (POST); enables langgraph containers to make conversational calls to peers. See §4.2.1.
  - Endpoints documented in README and registry.yml
  - Endpoints accessible from joshua-net overlay network (`/peer` also accessible from `[mad]-net`)
  - Port assigned per registry.yml (e.g., 6340, 6350)
- **Verification:** `curl http://[mad]:PORT/health` returns 200, `/mcp` accepts MCP connections
- **Example:** Health at `http://[mad]:6340/health`, MCP at `http://[mad]:6340/mcp`

**4.2.1 OpenAI-Compatible Chat Completions** (HLD-conversational-core §5)
- **What:** MADs that host conversational agents may expose an OpenAI-compatible `/v1/chat/completions` endpoint on their gateway alongside `/mcp`
- **Detail:**
  - Two protocols traverse joshua-net: MCP JSON-RPC for discrete tool calls, and OpenAI chat completions for conversational message exchange
  - **When to use which:** MCP for structured operations (tool calls, management, context broker). OpenAI chat completions for conversational exchange (inference, eMAD chat)
  - The `/v1/chat/completions` endpoint follows the OpenAI API specification: accepts `model`, `messages`, `stream`, and standard generation parameters
  - **Ecosystem extension — `conversation_id`:** An optional `conversation_id` field in the request body provides Rogers session continuity. The response includes the `conversation_id` for the caller to persist. This is the ecosystem's standard extension to the OpenAI protocol (see HLD-conversational-core §5.5)
  - Multimodal content (images, documents) is carried natively in the OpenAI `messages` content parts format
  - Streaming responses use standard SSE format (`data: {...}\n\n`, `data: [DONE]\n\n`)
  - Not all MADs require this endpoint — only those that host conversational agents (e.g., Sutherland, Kaiser)
- **Verification:** `POST /v1/chat/completions` with standard OpenAI payload returns streaming SSE response
- **Example:** `POST http://kaiser:9226/v1/chat/completions` with `{"model": "hopper", "messages": [...], "stream": true, "conversation_id": "abc-123"}`

**4.3 Sam Relay Compatibility** (ADR-040) — **[DEPRECATED 2026-02-26]**

> SAM relay is being phased out. MCP gateways are directly addressable on `joshua-net`
> by container hostname and port. New MADs are not required to register with SAM.
> Existing SAM integrations remain functional but compliance with this requirement is
> no longer enforced. The registry.yml entry remains useful for host affinity and
> port documentation purposes independent of SAM.

~~- **What:** MAD must be discoverable and manageable by Sam relay~~
~~- **Verification:** Sam can discover MAD via registry.yml, relay tool calls succeed~~

**4.4 Tool Naming Convention** (ADR-045)
- **What:** MCP tools must use domain prefixes to avoid name collisions
- **Detail:**
  - Pattern: `[domain]_[action]` (e.g., `conv_add_turn`, `mem_search`)
  - Domain prefix identifies the MAD/capability area
  - Prevents collisions when multiple MADs expose tools via Sam
  - Consistent naming across ecosystem
  - Tool names documented in README tool table
- **Verification:** All tool names follow `[domain]_[action]` pattern, no collisions in Sam relay
- **Example:** `conv_add_turn`, `mem_search`, `git_commit` (NOT `add_turn`, `search`, `commit`)

**4.5 MCP Gateway Template Usage** (MCP Gateway Library Pattern ADR)
- **What:** New State 1 pMADs created by copying and customizing base template at `mads/_template/`
- **Detail:**
  - **Base Template Location**: `mads/_template/` contains working multi-container MAD
  - **Template Containers**: `template/` (gateway), `template-langgraph/` (backend), `template-postgres/` (database - optional)
  - **Copy-Paste Pattern**: Developers copy entire container directories, rename, and customize config.json
  - **Standard Libraries**: mcp-protocol-lib, health-aggregator-lib, logging-lib, routing-lib (in gateway only)
  - **Generic server.js**: Pre-implemented, < 20 lines, requires no changes when copied
  - **config.json**: MAD-specific configuration defining tools, routing, dependencies (primary customization point)
  - **All other containers**: Do NOT use MCP libraries (langgraph, backing services, etc.)
  - Template provides: MCP server, HTTP/SSE transport, tool registration, health endpoint, automatic logging, production patterns
- **Verification:**
  - New MAD created by copying `mads/_template/` containers (not manual file assembly)
  - Gateway has config.json defining MAD-specific tools and dependencies
  - package.json includes standard libraries (mcp-protocol-lib, health-aggregator-lib, logging-lib, routing-lib)
  - server.js unchanged from template (generic implementation)
- **Example:** `cp -r mads/_template/template mads/[mad-name]` then customize config.json
- **Reference:** `mads/_template/README.md` for template usage workflow
- **Reference:** `docs/guides/mad-implementation-guide.md` for detailed implementation patterns

**4.6 Configuration File Requirements** (MCP Gateway Library Pattern ADR, ADR-053)
- **What:** MCP gateways must have valid config.json defining all tools and dependencies
- **Detail:**
  - Location: `mads/[mad-name]/config.json`
  - Must validate against config.schema.json
  - Required fields: port, tools, dependencies
  - Tools section: Each tool has target container, endpoint path, input/output schema
  - Dependencies section: List all health check targets (databases, caches, etc.)
  - Optional: logging configuration (level, configPath), routing configuration (timeout, retries)
  - Optional: `peers` section — when langgraph containers need to call peer MADs, declare them here:
    ```json
    "peers": {
      "[peer-name]": { "host": "[peer-container-name]", "port": [peer-mcp-port] }
    }
    ```
  - `host` is the peer's container DNS name on `joshua-net`; `port` is the peer's MCP gateway port from registry.yml
  - Tool names follow `[domain]_[action]` convention
  - Target containers use DNS names (`[mad]-langgraph:8000`, `[mad]-postgres:5432`)
- **Verification:**
  - config.json exists and validates against schema
  - All tools have complete schemas (input, output)
  - All dependencies listed for health checks
  - Tool names match README documentation
  - If peers are declared, entries have valid host (string) and port (integer)
- **Example:** See MCP Gateway Template REQ documents for complete config.json examples

**4.7 LangGraph Mandate**
- **What:** All programmatic and cognitive logic within a State 1 pMAD **MUST** be implemented in the `[mad-name]-langgraph` container using LangGraph's `StateGraph`.
- **Detail:** The use of other web frameworks (e.g., Flask, FastAPI) to implement the primary application logic is a direct architectural violation. The `server.py` entry point should initialize and run the `StateGraph`.

**4.8 Thin Gateway Mandate**
- **What:** The `[mad-name]` gateway container **MUST** function only as a thin, configuration-driven router.
- **Detail:** All programmatic logic **MUST** be delegated to the langgraph container. The gateway's `server.js` file **MUST** remain minimal (< 20 lines) and unmodified from the `mads/_template`. All tool definitions, schemas, and routing logic **MUST** be defined in `config.json`.

**4.9 LangGraph State Immutability**
- **What:** Functions executed within a `StateGraph` node **MUST NOT** modify the input state in-place.
- **Detail:** Each node **MUST** return a new dictionary containing only the updated state variables. This adheres to the functional programming principles that `StateGraph` is built upon and ensures predictable state transitions.

**4.10 LLM Routing**
- **What:** All LLM calls go through Sutherland. No direct external LLM API calls from MADs.
- **Detail:**
  - MADs that need chat completion, embedding, or rerank must call Sutherland's MCP tools (`llm_chat_completions`, `llm_embeddings`, `llm_rerank`) via the gateway or peer proxy
  - No MAD (other than Sutherland) may call external LLM providers (OpenAI, Anthropic, Google, etc.) or local model APIs directly
  - Sutherland is the single AI compute platform; it may use cloud APIs or local Ray Serve deployments internally
  - Enables consistent model aliasing, cost control, and observability
- **Verification:** Grep MAD codebases (excluding Sutherland) for direct LLM client usage or external API keys; should find none
- **Example:** Apgar's diagnose flow calls Sutherland for synthesis; Rogers uses Sutherland for embeddings; no MAD calls OpenAI API directly

**4.11 Prometheus Metrics** (Observability)
- **What:** MADs expose metrics for ecosystem observability per `docs/guides/mad-prometheus-metrics-guide.md`.
- **Detail:**
  - **MCP Gateway:** Exposes MCP tool `metrics_get` (returns Prometheus exposition format). Used by Apgar's metrics scraper via peer proxy `/peer/{mad}/metrics_get`. Optionally also exposes `GET /metrics` on the gateway for direct scrape when on same network.
  - **LangGraph / backends:** Expose `GET /metrics` and (for gateway forwarding) `POST /metrics_get` returning `{ "metrics": "<text>" }`. **In langgraph containers, metrics MUST be produced inside a StateGraph** (see §4.7 LangGraph Mandate). The HTTP route must only construct initial state, invoke a compiled StateGraph (e.g. `_metrics_graph.ainvoke(state)`), and return the graph output. A node within the graph must perform the actual metrics generation (e.g. call `prometheus_client.generate_latest(REGISTRY)`). **Do not** implement `/metrics` or `/metrics_get` as imperative route handlers that directly call the metrics library and return — that bypasses LangGraph and is an architectural violation.
  - **Backing services** (Postgres, Redis, etc.): Do not require modification and must not be forked. If a **pre-built exporter image exists** for the technology (e.g. `prometheuscommunity/postgres-exporter`, `oliver006/redis_exporter`), run it as a sidecar container on the private `[mad]-net` to expose `/metrics`. If no pre-built exporter image exists for the technology, implement metrics collection in the LangGraph `metrics_get` StateGraph instead — the langgraph container queries the backing service via its native API and includes the results in its Prometheus output. Never write custom exporter code outside of LangGraph.
  - Label conventions: `mad`, `tool`, `status` (see guide). Standard metrics: `mcp_requests_total`, `mcp_request_duration_seconds`, `mcp_requests_errors_total` on gateways.
- **Verification:** MAD gateway config includes `metrics_get` tool; langgraph exposes `/metrics` and `/metrics_get` via StateGraph invocation (route handler calls graph.ainvoke, not generate_latest); backing services use exporter sidecars when metrics are required
- **Reference:** `docs/guides/mad-prometheus-metrics-guide.md`

**4.12 Imperator Requirements** (ADR-054, HLD-joshua26-agent-architecture.md, HLD-conversational-core.md)
- **What:** Every TE in the ecosystem MUST include an Imperator as its prime agent. This applies to both pMAD TEs and eMAD TEs.
- **Detail:**
  - **Identity and Purpose (mandatory):** The Imperator MUST declare a unique Identity (what it is) and Purpose (what it is for). These are fixed properties of the TE package — not runtime configuration and not derivable from calling context.
  - **Intent is dynamic:** The Imperator's Intent is generated at runtime as its Purpose meets current circumstances. It is never hardcoded or pre-scripted. This is what distinguishes the Imperator from an Executor.
  - **Rogers on startup:** The Imperator MUST call `conv_retrieve_context` (Rogers) at the start of every invocation to assemble conversation history and relevant context before processing. This applies to all Imperators regardless of whether they are pMAD or eMAD.
  - **Sutherland for inference:** The Imperator MUST route all LLM calls through Sutherland (`llm_chat_completions`, `llm_embeddings`, etc.). No direct calls to external LLM providers are permitted (enforced also by §4.10).
  - **Rogers for decision recording:** The Imperator MUST write its decisions, reasoning paths, and outcomes to Rogers. This record is the operational corpus from which the DTR and Executor tiers of the PCP learn.
  - **Executor distinction:** Executors within the same TE may be cognitive but MUST NOT be assigned Identity or Purpose. An Executor's Intent is entirely derivative of the calling system and circumstances. Code review must reject any Executor that defines its own purpose or acts autonomously.
- **Verification:** TE package declares Imperator Identity and Purpose in code; startup trace shows `conv_retrieve_context` call; all inference routes through Sutherland; Rogers accumulates decision records with Imperator metadata.
- **Reference:** `docs/designs/HLD-joshua26-agent-architecture.md` (Imperator anatomy), `docs/designs/HLD-conversational-core.md` (Rogers/Sutherland contracts), `docs/concepts/d2-progressive-cognitive-pipeline.md` (PCP tiers), ADR-054

**Key Principle:** MCP over HTTP/SSE. Tools named with domain prefixes. Compatible with Sam relay. MCP gateways use config-driven template pattern with standard libraries. Only the MCP gateway container exposes MCP - langgraph and backing services do not.

**Applicability by container type:**
- `[mad]` (MCP gateway): All requirements apply
- `[mad]-langgraph`: N/A (no MCP exposure)
- `[mad]-[technology]`: N/A (backing services)

### 5. Logging and Observability
**Purpose:** Ensure components produce observable, structured logs and expose health status.

**Requirements:**

**5.1 Logging to stdout/stderr** (ADR-047)
- **What:** All logs must go to stdout/stderr, not to files inside containers
- **Detail:**
  - Application logs written to stdout (normal operation) or stderr (errors)
  - No log files created inside container filesystem
  - Docker captures stdout/stderr and makes available via `docker logs`
  - Log rotation handled by Docker daemon, not application
  - Logs accessible via `docker logs <container>` command
- **Verification:** `docker logs <container>` shows application logs; no log files in container filesystem
- **Example:** `console.log()` in Node.js, `print()` in Python - NOT writing to `/var/log/` or `/app/logs/`

**5.2 Structured Logging Format** (ADR-047)
- **What:** Logs must use structured format (JSON) with one entry per line
- **Detail:**
  - JSON format: `{"timestamp": "...", "level": "INFO", "message": "...", "context": {...}}`
  - One complete JSON object per line (newline-delimited JSON)
  - Consistent field names across all containers
  - Timestamp in ISO 8601 format
  - Log level field (DEBUG, INFO, WARN, ERROR)
  - Context fields for request tracing (request_id, user_id, etc.)
- **Verification:** `docker logs <container>` output is valid JSON, one object per line
- **Example:** `{"timestamp":"2026-01-30T10:15:30Z","level":"INFO","message":"Request processed","request_id":"abc123"}`

**5.3 Health Check Endpoint** (ADR-045, MAD consolidation)
- **What:** MCP gateway containers must expose HTTP `/health` endpoint
- **Detail:**
  - HTTP `/health` endpoint provided by health-aggregator-lib
  - Health endpoint returns 200 OK when healthy, 503 when unhealthy
  - Health check verifies critical dependencies (database connections, etc.)
  - Endpoint accessible from overlay network
  - Response format: `{"status": "healthy", "checks": {...}}`
- **Verification:** `curl http://[mad]:PORT/health` returns 200 with JSON status
- **Example:** `GET http://[mad]:6340/health` → `{"status":"healthy"}`

**5.4 Dockerfile HEALTHCHECK** (ADR-045, MAD consolidation)
- **What:** Dockerfile must include HEALTHCHECK directive
- **Detail:**
  - Use `curl` or `wget` to check `/health` endpoint
  - Timing varies by service complexity: `start_period` can be 10s to 120s
  - Pattern: `HEALTHCHECK --interval=30s --timeout=3s --start-period=60s --retries=3 CMD curl -f http://localhost:PORT/health || exit 1`
  - Install curl/wget in Dockerfile if needed for healthcheck
  - Longer start_period for services with slow initialization (databases, embeddings)
- **Verification:** `docker inspect <container>` shows HEALTHCHECK configuration; `docker ps` shows health status
- **Example:** `HEALTHCHECK --interval=30s --timeout=3s --start-period=60s --retries=3 CMD curl -f http://localhost:6340/health || exit 1`

**5.5 MCP Request Logging** (ADR-047)
- **What:** MCP tool requests and responses automatically logged by mcp-protocol-lib
- **Detail:**
  - mcp-protocol-lib automatically logs all incoming MCP requests
  - Log includes: tool name, parameters, request_id, timestamp
  - Responses logged with: result status, execution time
  - No additional application code needed for request logging
  - Request logs help debug tool invocation issues
  - Follows structured logging format (5.2)
- **Verification:** `docker logs <container>` shows MCP request/response entries when tools are invoked
- **Example:** `{"timestamp":"...","level":"INFO","message":"MCP request","tool":"conv_add_turn","request_id":"..."}`

**5.6 No File-Based Logging** (ADR-047)
- **What:** Containers must not write logs to files inside container
- **Detail:**
  - No `/var/log/` directories for application logs
  - No `/app/logs/` or similar application log directories
  - No log rotation scripts inside container
  - All logging via stdout/stderr only
  - Exception: System package logs (e.g., PostgreSQL logs) may go to files if required by official image
- **Verification:** Search Dockerfile and code for log file paths - should find none; container filesystem has no log files
- **Example:** ❌ `fs.writeFile('/app/logs/app.log')` ✅ `console.log()`

**5.7 Log Level Guidelines** (ADR-047)
- **What:** Use appropriate log levels for different event types
- **Detail:**
  - **DEBUG**: Detailed diagnostic info (function calls, variable values) - off by default in production
  - **INFO**: Normal operational events (service started, request completed, successful operations)
  - **WARN**: Recoverable issues (degraded mode, retry triggered, deprecated feature used)
  - **ERROR**: Failures requiring attention (request failed, timeout, invalid input)
  - Log level configurable via `/storage/config/[mad-name]/logging.json` or environment variable
  - Changes to log level should take effect without container restart
  - Default level: INFO
- **Verification:** Change log level dynamically, verify new level takes effect; DEBUG logs appear only when DEBUG enabled
- **Example:** Config file: `{"level": "DEBUG"}` or ENV: `LOG_LEVEL=DEBUG`

**5.8 Log Content Standards** (ADR-047)
- **What:** Log appropriate information, exclude sensitive data and noise
- **Detail:**
  - **DO log**: Service lifecycle events, errors with context (request_id, tool_name), performance metrics (duration_ms)
  - **DO NOT log**: Secrets/credentials, full request/response bodies (may contain PII), health check requests (too noisy)
  - Include context fields: container_name, mad_name, request_id, tool_name (for MCP requests)
  - Health checks should not log on every execution - only log state changes (healthy→unhealthy)
- **Verification:** Grep logs for secrets (find none), verify health checks don't log every 30s
- **Example:** ✅ `{"level":"ERROR","tool":"mem_search","error":"timeout","request_id":"abc"}` ❌ `{"level":"INFO","message":"health check passed"}` (every 30s)

**5.9 Health Check Architecture** (ADR-045, MAD consolidation)
- **What:** Two-layer health check system: per-container process health and pMAD group dependency health
- **Detail:**
  - **Docker HEALTHCHECK (per container)**: Lightweight process check in Dockerfile, does NOT check dependencies or other containers
  - **HTTP `/health` endpoint (MCP gateway only)**: Actively tests dependencies and returns aggregated status
  - `/health` endpoint implementation: Connects to each dependency, runs lightweight check (database: simple query, cache: ping)
  - Response includes per-dependency status: `{"status": "healthy|degraded|unhealthy", "database": "ok", "cache": "unreachable"}`
  - External monitoring systems query `/health` endpoint for full pMAD group status
  - Docker HEALTHCHECK does NOT query other Docker containers - just checks own process
- **Verification:** Docker HEALTHCHECK only checks local process; `/health` endpoint tests actual connections to dependencies
- **Example:** MCP gateway `/health` returns `{"status":"degraded","database":"ok","cache":"unreachable"}` when cache is down

**5.10 Specific Exception Handling**
- **What:** The use of blanket `except Exception:` or `except:` blocks is forbidden.
- **Detail:** Exception handling **MUST** catch specific, anticipated exceptions. Unhandled exceptions should be allowed to propagate. The `ruff` linter rule `BLE001` helps enforce this.

**5.11 Resource Management**
- **What:** All external resources (e.g., file handles, database connections) **MUST** be reliably closed.
- **Detail:** This **MUST** be achieved using context managers (`with` statements) or `try...finally` blocks to prevent resource leaks.

**5.12 Error Context**
- **What:** All logged errors and raised exceptions **MUST** include sufficient context to be debuggable.
- **Detail:** Context should include relevant identifiers (e.g., `session_id`, `user_id`), function names, and the operation being attempted.

**Key Principle:** All logs to stdout/stderr (Docker captures). Structured JSON logging with appropriate levels. Log level configurable at runtime. Exclude secrets and noise. Health checks log state changes only. MCP requests logged automatically. Two-layer health: Docker checks process, `/health` endpoint checks dependencies.

### 6. Documentation and Discoverability
**Purpose:** Ensure components are discoverable, understandable, and deployable with clear documentation.

**Requirements:**

**6.1 REQ Document** (ADR-045)
- **What:** Component-specific requirements document defining complete specification
- **Detail:**
  - Location: `mads/[mad-name]/docs/REQ-[component].md`
  - Must include: purpose, MCP tools (with schemas), dependencies, credentials, volumes, ports
  - Tool specifications include input/output schemas, error conditions, examples
  - Dependency specifications include versions, connection details, failure modes
  - Credential specifications include paths, format, required fields
  - Volume mount specifications include paths, purposes, permission requirements
- **Verification:** REQ document exists and covers all sections; tool schemas are complete and valid
- **Example:** `mads/[mad-name]/docs/REQ-[mad-name].md` with complete tool table and dependency list

**6.2 README.md** (ADR-045)
- **What:** Component documentation with architecture, configuration, and operational guidance
- **Detail:**
  - Location: `mads/[mad-name]/README.md`
  - Must include: description, architecture diagram/explanation, deployment steps, configuration options
  - Recovery procedures for common failure scenarios
  - Container startup sequence and dependencies
  - Environment variables and configuration files
  - Health check endpoints and expected responses
- **Verification:** README exists and covers all required sections; deployment steps are executable
- **Example:** README with architecture section, deployment steps, configuration table, troubleshooting guide

**6.3 Registry Entry** (ADR-043, ADR-045)
- **What:** One entry per MAD in registry.yml defining the gateway's identity and network configuration
- **Detail:**
  - One registry entry per MAD — the MCP gateway (the only container on joshua-net)
  - Sub-container topology (langgraph, backing services) is defined in docker-compose.yml, not in the registry
  - For ppMAD groups: all containers share same UID (one UID per group, not per container) — configured in docker-compose.yml and Dockerfiles
  - Registry entry must include: name, UID, GID, port, host, description, mcp_endpoints
  - UID must be unique across ecosystem (per pMAD group)
  - GID must be 2001 (administrators)
  - Port is the MCP gateway port on joshua-net; must not conflict with other services
  - Host must match deployment target
  - mcp_endpoints specifies health and stream endpoints (e.g., {health: /health, stream: /mcp})
- **Verification:** registry.yml contains one entry per MAD (gateway only); UID unique across ecosystem; port unique; values match container configuration
- **Example:** See ADR-043 for complete registry pattern

**6.4 Directory Structure** (ADR-045)
- **What:** Each MAD Group must have a single parent directory within `mads/`, which in turn contains a subdirectory for each container in the group.
- **Detail:**
  - The top-level MAD Group folder (`mads/[mad-name]/`) holds group-level documentation like the main `README.md` and `docs/`.
  - The source code for each container, including its `Dockerfile`, resides in a nested subdirectory (e.g., `mads/[mad-name]/[mad-name]/`, `mads/[mad-name]/[mad-name]-langgraph/`).
  - This structure is required because the `docker-compose.yml` build context is the project root (`.`).
- **Verification:** The MAD follows the nested directory structure.
- **Example (`hamilton` MAD):**
  ```
  mads/
  └── hamilton/              <-- MAD Group Folder
      ├── hamilton/          <-- Source code for 'hamilton' gateway container
      │   ├── Dockerfile
      │   └── server.js
      ├── hamilton-langgraph/  <-- Source code for 'hamilton-langgraph' container
      │   ├── Dockerfile
      │   └── server.py
      └── README.md          <-- Group-level README for the Hamilton MAD
  ```
- **Reference:** For the full architectural pattern, see `docs/designs/HLD-MAD-container-composition.md`.

**6.5 Tool Documentation** (ADR-045)
- **What:** MCP tools documented with descriptions, schemas, and examples
- **Detail:**
  - Tool table in README with: name, description, inputs, outputs
  - Tool schemas in REQ document with JSON schema format
  - Examples showing typical usage and edge cases
  - Error conditions and response codes documented
  - Only required for MCP gateway container (not langgraph or backing services)
- **Verification:** README contains tool table; REQ document contains complete schemas
- **Example:** Tool table with `[domain]_[action]` names, input/output schemas, example requests/responses

**Key Principle:** Three required docs: REQ (complete specification), README (operational guidance), registry entry (network identity). Standard directory structure for discoverability. Tool documentation for MCP gateway only.

**Applicability by container type:**
- `[mad]` (MCP gateway): All requirements apply
- `[mad]-langgraph`: 6.1, 6.2, 6.4 (REQ, README, directory structure - no registry or tool docs)
- `[mad]-[technology]`: 6.4 only (may have Dockerfile if custom, otherwise use official docs)

### 7. Resilience, Safety, and Deployment
**Purpose:** Ensure components handle failures gracefully, have safety mechanisms, and are deployed correctly.

**Requirements:**

**7.1 Graceful Degradation** (ADR-046)
- **What:** Component must operate in degraded mode when external dependencies are unavailable
- **Detail:**
  - External dependencies (other MADs, external APIs) failure causes degradation, NOT crash
  - Degraded mode: limited functionality, cached data, error responses (not service failure)
  - Internal dependencies (within pMAD group) can be hard dependencies
  - Health endpoint reports degraded status when dependencies unavailable
  - Service continues serving requests that don't require unavailable dependency
- **Verification:** Stop external dependency, verify service continues with degraded status; health endpoint returns "degraded"
- **Example:** Cache service down → MCP gateway returns cached data with "stale" flag instead of failing

**7.2 MAD Group Boundaries** (ADR-046)
- **What:** Clear distinction between internal hard dependencies and external soft dependencies
- **Detail:**
  - **Internal (hard)**: Containers within same pMAD group (e.g., `[mad]` → `[mad]-postgres`)
  - **External (soft)**: Other MADs, external services (e.g., `[mad]` → other MADs via Sam)
  - Internal dependency failure may stop service (acceptable)
  - External dependency failure must degrade gracefully
  - ppMAD groups deployed together on same host for performance
- **Verification:** Identify all dependencies; classify as internal/external; verify external failures degrade gracefully
- **Example:** MCP gateway hard-depends on its own database (internal), soft-depends on other MADs (external)

**7.3 Independent Container Startup** (ADR-046)
- **What:** Containers can start and become healthy without waiting for dependencies
- **Detail:**
  - Container starts and binds ports immediately
  - Health check passes when container process is healthy (not waiting for dependencies)
  - Dependency unavailability handled at request time (degradation)
  - No blocking waits during container initialization
  - Allows parallel startup and faster recovery
- **Verification:** Start container with dependencies down; verify it reaches healthy state
- **Example:** MCP gateway starts and serves health endpoint even if database is unavailable

**7.4 Overlay Network DNS Usage** (MAD consolidation)
- **What:** Use container names for all inter-container communication, never IP addresses
- **Detail:**
  - Pattern: `http://[container-name]:PORT` for all network requests
  - Works for both same-host and cross-host communication via overlay network DNS
  - Overlay network: `joshua-net` for cross-MAD communication
  - VXLAN FDB entries can become stale when containers move between hosts - DNS avoids this
  - Never hardcode IP addresses in configuration or code
- **Verification:** Grep code for IP addresses - should find none; all network config uses container names
- **Example:** ✅ `http://[mad-name]-postgres:5432` ❌ `http://172.18.0.5:5432`

**7.4.1 Per-MAD Private Networks** (ADR-046, ADR-053)
- **What:** Each pMAD group operates on a private network in addition to joshua-net
- **Detail:**
  - Each pMAD group defines a private bridge network: `[mad]-net` (e.g., `hamilton-net`, `rogers-net`)
  - MCP gateway (`[mad]`) connects to both `joshua-net` and `[mad]-net` — it is the **sole bidirectional network boundary**
  - LangGraph container (`[mad]-langgraph`) connects to `[mad]-net` only — absolute requirement, no exceptions
  - Backing services (`[mad]-postgres`, etc.) connect to `[mad]-net` only — absolute requirement, no exceptions
  - Internal containers are never directly reachable from joshua-net
  - **Outbound peer calls:** When langgraph must call a tool on a peer MAD, it calls the gateway's `/peer/{peer}/{tool}` endpoint on `[mad]-net`. The gateway proxies the call to the peer using MCP JSON-RPC 2.0 (`POST /mcp`, `tools/call`, sessionless) on `joshua-net`. Peer gateways are plain MCP clients — no custom endpoint required. Peers must be declared in `config.json` under `peers`.
  - LangGraph containers must never be added to `joshua-net` to enable peer calls — use the gateway proxy instead
- **Verification:** In docker-compose.yml, gateway has both networks; langgraph and backing services have only `[mad]-net`; no langgraph container appears in `joshua-net`
- **Example:** `hamilton` on `joshua-net` + `hamilton-net`; `hamilton-langgraph` and `hamilton-postgres` on `hamilton-net` only; `rogers-langgraph` calls Hamilton via `POST http://rogers:6380/peer/hamilton/embed_text`

**7.5 Docker Compose Configuration** (MAD consolidation)
- **What:** All service definitions exist in master docker-compose.yml at project root
- **Detail:**
  - Master file: `docker-compose.yml` (project root)
  - Override file: `docker-compose.override.yml` (project root, for local dev)
  - Never create MAD-specific docker-compose.yml files
  - All deployments use master docker-compose.yml
  - Build context: `.` (project root), not `mads/[mad-name]`
  - Dockerfile COPY paths relative to project root: `COPY mads/[mad-name]/...`
- **Verification:** Service definition exists in master docker-compose.yml; build context is `.`; COPY paths are `mads/...`
- **Example:** docker-compose.yml at project root defines all services; build context: `.`

**7.6 Host Affinity Configuration** (ADR-046, registry.yml)
- **What:** Containers deployed to correct host per registry.yml affinity rules
- **Detail:**
  - registry.yml specifies host affinity for each service (the `host` field)
  - ppMAD groups should co-locate on same host for performance (local workspace I/O)
  - Host affinity enforced via **profiles in per-host override files** (not Swarm placement constraints)
  - Pattern: services are defined in master `docker-compose.yml`; non-native hosts suppress them with `profiles: ["[host]-only"]` in their override file (e.g. `docker-compose.m5.yml`)
  - A service runs on its designated host by default (no override needed on native host)
  - See `docs/guides/docker-compose-file-strategy.md` for full override file documentation
- **Verification:** registry.yml has host affinity; non-native host override files suppress the service with a profile
- **Example:** Hamilton runs on Irina: `docker-compose.m5.yml` and `docker-compose.hymie.yml` both add `hamilton: { profiles: ["irina-only"] }`

**7.7 Git Safety Mechanisms** (ADR-048)
- **What:** Components that modify git repositories must include safety features
- **Detail:**
  - Backup branch created before destructive operations
  - Dry-run mode available for preview without changes
  - Rollback capability to restore previous state
  - User confirmation required for destructive operations
  - All git operations logged with commit hashes
  - Only applies to MADs that perform git operations
- **Verification:** Git-modifying MAD has backup, dry-run, and rollback features; destructive ops require confirmation
- **Example:** Git operation tool creates backup branch, shows diff, asks for confirmation before push

**7.8 Conversation Data Integration** (ADR-049)
- **What:** Components conducting conversations must write directly to Rogers (preferred) or use conversation watcher (legacy)
- **Detail:**
  - **Preferred**: Write conversation data directly to Rogers via MCP tools
  - **Legacy**: File-based conversation files ingested via conversation watcher
  - File-based approach: Write JSON files to watched directory with required fields (conversation_id, timestamp, turns)
  - Watcher detects files and ingests to Rogers conversation pipeline
  - Only applies to components that produce conversation data
  - Direct Rogers integration eliminates file-based intermediary overhead
- **Verification:** Conversation data appears in Rogers; either via direct MCP calls or watcher file processing
- **Example:** Direct: Call Rogers MCP tool `conv_add_turn`; Legacy: Write to `/storage/conversations/incoming/` for watcher pickup

**7.9 Asynchronous Correctness**
- **What:** Blocking I/O operations **MUST NOT** be used in asynchronous functions.
- **Detail:** Synchronous calls like `time.sleep()` or standard (non-async) library calls for network or file I/O will block the entire event loop and are forbidden. `await asyncio.sleep()` and asynchronous libraries (e.g., `aiohttp`, `asyncpg`) **MUST** be used for all I/O operations.

**7.10 Input Validation**
- **What:** All data received from an external source (e.g., an MCP tool's input, a response from a peer MAD or external API) **MUST** be validated before use.
- **Detail:** For MCP tools, this is enforced via the `inputSchema` in `config.json`. For other inputs, this can be done via manual checks or data validation libraries like Pydantic.

**7.11 Null/None Checking**
- **What:** Variables that could reasonably be `None` (e.g., the result of a database query that might find nothing) **MUST** be explicitly checked before their attributes or methods are accessed.

**7.12 Container-Only Deployment**
- **What:** All services run as containers. Bare-metal installs are not permitted unless there is no container-based alternative.
- **Detail:**
  - Every Joshua26 service (MADs, observability, backing services) runs inside Docker containers
  - No direct installation of Prometheus, Loki, Grafana, or other stack components on host OS
  - Log shippers (e.g. Promtail) run as containers that mount host paths (e.g. `/var/lib/docker/containers`) where needed
  - Exceptions require justification and approval per Part 1 (e.g. host-level monitoring agent with no container image)
- **Verification:** No install scripts or docs that install services directly on the host; all components defined in docker-compose.yml or equivalent
- **Example:** Apgar runs Prometheus, Loki, Grafana in containers; Promtail runs as one container per host with bind-mount to Docker log directory

**7.13 State 3 — AE/TE Package Architecture**
- **What:** State 3 pMADs separate the bootstrap kernel (container — irreducible core) from both the AE and TE, each delivered as independent versioned Python packages published to Alexandria and installed at runtime. All State 3 requirements are additive to State 2. See `HLD-state3-mad.md` for full design.
- **Detail:**

  **Two package kinds — distinguished by entry_points group:**

  Each State 3 pMAD defines two entry_points groups, named for the pMAD: `[pmad-name].ae` and `[pmad-name].te`. The bootstrap kernel scans both groups on startup and after each `install_stategraph()` call. The group tells the kernel how to handle the package.

  **AE StateGraph packages** (`[pmad-name].ae` entry_points group):
  - Provide: MCP tool handler implementations, infrastructure wiring, message routing, peer proxy configuration, Executor-driven processes
  - The bootstrap wires AE packages into the web server's routing table — their MCP tools become available on joshua-net
  - Entry_point form: `{name} = "{module}.register:build_graph"` — `build_graph(params: dict) -> StateGraph`
  - AE packages are stable relative to TE; updates occur when adding new MCP tools or wiring changes
  - Example: `[project.entry-points."kaiser.ae"]` / `core_tools = "kaiser_ae.register:build_graph"`

  **TE StateGraph packages** (`[pmad-name].te` entry_points group):
  - Provide: the Imperator and its cognitive apparatus — PCP, inference flows, domain reasoning
  - The bootstrap makes TE packages available for internal invocation by the AE. The web server routes nothing directly to the TE; the AE calls into the TE when cognitive work is needed.
  - Entry_point form: `{name} = "{module}.register:build_graph"` — `build_graph(params: dict) -> StateGraph`
  - eMAD TE packages register under the **host pMAD's** TE entry_points group (e.g. `kaiser.te`)
  - Example: `[project.entry-points."kaiser.te"]` / `hopper = "hopper_emad.register:build_graph"`

  **install_stategraph:**
  - `install_stategraph(package_name)` is the single baked-in bootstrap tool for dynamic package management
  - Works for both AE and TE packages — the entry_points group in the installed package determines how it is handled
  - Triggers `registry.scan()` which evicts old modules from `sys.modules` before reimporting; new version is live immediately, no container restart required
  - Packages MUST be published to Alexandria (`root/internal` devpi index) before install
  - `PIP_INDEX_URL` in State 3 containers: `http://[pmad]:PORT/pypi/root/internal/+simple/` (proxied through the pMAD's nginx to Alexandria at `irina:3141`)

  **Kaiser eMAD host state contract:**
  - Initial state provided by Kaiser to any eMAD TE: `messages`, `rogers_conversation_id`, `rogers_context_window_id`
  - Output state MUST include `final_response`
  - eMAD packages run inside the Kaiser container (UID 2036); NFS mounts (`/storage`, `/workspace`) accessible at the same paths as the host pMAD

  **TE naming convention (Imperator-based):**
  - File: `flows/imperator.py`, state class: `[Name]ImperatorState`, graph builder: `build_imperator_graph()`, registered via `register.py`
  - The graph builder calls into the Imperator's cognitive apparatus (see §4.12)

- **Verification:** Publish an AE or TE package to Alexandria; call `install_stategraph(package_name)`; verify new capability or updated logic is live without restarting the container.

**Key Principle:** No hard dependencies on peers (except within ppMAD groups). Use overlay DNS for networking. Master docker-compose.yml is source of truth. Graceful degradation for external dependencies. ppMAD groups co-locate for performance.

### 8. Exceptions and Special Cases
**Purpose:** Ensure deviations from requirements are documented, approved, and mitigated.

**Requirements:**

**8.1 Exception Documentation** (REQ-000-exception-registry)
- **What:** Components that cannot comply with requirements must document exceptions
- **Detail:**
  - Each exception includes: requirement ID, reason, impact, mitigation
  - Distinguish "exception" (can't comply) from "N/A" (doesn't apply)
  - All exceptions recorded in REQ-000-exception-registry central registry
  - Temporary exceptions include remediation plan and date
- **Verification:** Exception in REQ-000-exception-registry with justification, mitigation, approval
- **Example:** "Exception to Req 3.7: Using AWS RDS (not workspace). Mitigation: VPC co-location, connection pooling."

**8.2 Exception Approval** (REQ-000-exception-registry)
- **What:** All exceptions require explicit approval from Joshua/Aristotle9
- **Detail:**
  - Approval documented in REQ-000-exception-registry or audit record
  - Undocumented violations are blockers
  - Retroactive exceptions allowed but same approval required
  - Exceptions apply only to specific component, not ecosystem-wide
- **Verification:** REQ-000-exception-registry entry includes approver name and date
- **Example:** "Exception approved by Joshua on 2026-01-30"

**Key Principle:** Exceptions are rare and explicitly approved. Each requires justification, mitigation, and REQ-000-exception-registry entry. No undocumented violations.

---

## Document Metadata

**Version History:**
- v1.0 (2026-01-31): Initial draft - extracted from planning session

**Related Documents:**
- ADR-037: Offline Build Support
- ADR-038: Hybrid Runtime Environments
- ADR-039: Radical Simplification
- ADR-040: Sam Relay Protocol
- ADR-042: Shared MAD Core Library
- ADR-043: Centralized Identity With Lsyncd
- ADR-044: Credentials Management
- ADR-045: MAD Template Standard
- ADR-046: MAD Groups and Database Storage
- ADR-047: Logging Standards
- ADR-048: Git Safety Mechanisms
- ADR-049: Conversation Management
- ADR-054: AE/TE Framework, Effector Retirement, and Agent Taxonomy
- REQ-000-exception-registry: Approved Exceptions
- Audit Checklist Template: `docs/audits/ADR-compliance-checklist-template.md`

**Approval Status:** Draft - awaiting review

**Change Control:** Changes to this document require approval from Joshua/Aristotle9


