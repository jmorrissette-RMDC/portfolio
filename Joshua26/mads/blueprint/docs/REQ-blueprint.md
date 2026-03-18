# REQ-blueprint: Blueprint Multi-Agent CLI Workbench

**Document ID:** REQ-blueprint
**Version:** 1.1 (Draft)
**Date:** 2026-03-04
**Status:** Design — Implementation In Progress
**Group ID:** blueprint
**Host:** irina (192.168.1.110)
**Registry UID:** 2035 | **GID:** 2001 | **Port:** 6342
**Baseline:** Standalone Workbench (Not a MAD)
**Reference Implementation:** N/A (Unique Infrastructure)

---

## 1. Purpose and Scope

Blueprint (formerly Vannevar) is the multi-agent CLI orchestration workbench for Joshua26. It provides a
browser-based interface that allows the architect to run and coordinate multiple AI CLI
agents (Claude Code, Gemini CLI, OpenAI CLI) from a Windows browser against a Linux
execution environment hosted on irina.

**Problem solved:** The architect needs to work simultaneously with Claude, Gemini, and OpenAI
— each with different strengths — sharing context and routing tasks appropriately. Cursor proved
catastrophically expensive due to uncontrolled context management. Blueprint provides a controlled,
session-persistent workbench utilizing standard CLI agents optimized for prompt caching, with zero backend
interference in context escalation.

**Scope:**
- Browser-based dashboard with hierarchical folder tree and task team management
- 4-pane resizable workspace (3 CLI terminals + file navigator)
- Standard `@` autocomplete mentions system (`@claude`, `@gemini`, `@openai`, `@all`)
- PTY terminal streaming via WebSocket
- File-based inter-CLI message passing (File Bridge)
- Task team persistence across browser restarts
- Direct access to joshua-net for the CLI agents to securely interact with internal MCP endpoints

**Out of scope:**
- Imperator / Autonomous orchestration (Blueprint is a human-driven workbench)
- Apgar metrics (Blueprint is not an autonomous actor)
- Nginx Gateway (Direct host exposure is safe for this specific workbench)
- Unified package caching (ADR-037 local caching used instead)

---

## 2. Registry Allocation (Workload Entry)

*Note: Blueprint is not a MAD, but requires a registry entry to assign UIDs and document the host port.*

```yaml
blueprint:
  uid: 2035
  gid: 2001
  port: 6342
  host: irina
  description: Multi-agent CLI orchestration workbench (browser UI + PTY streaming + isolated CLIs)
```

---

## 3. Container Composition

Blueprint is a standalone workbench composed of a central UI/Orchestrator and isolated CLI agent containers.

| Container | Role | Technology | Network |
|---|---|---|---|
| `blueprint-core` | UI & PTY Multiplexer | `python:3.12-slim` (Quart + amux) | `blueprint-net` (port 6342 exposed to host) |
| `blueprint-claude` | Agent CLI | `node:20-slim` (Claude Code) | `blueprint-net` + `joshua-net` |
| `blueprint-gemini` | Agent CLI | `node:20-slim` (Gemini CLI) | `blueprint-net` + `joshua-net` |
| `blueprint-openai` | Agent CLI | `node:20-slim` (OpenAI CLI) | `blueprint-net` + `joshua-net` |
| `blueprint-postgres` | Task Team Database | `postgres:16-alpine` (OTS) | `blueprint-net` only |
| `blueprint-qdrant` | Vector Database | `qdrant/qdrant` (OTS) | `blueprint-net` only |
| `blueprint-qdrant-mcp` | Qdrant MCP Server | `python:3.12-slim` (`mcp-server-qdrant`) | `blueprint-net` only |
| `blueprint-memory` | Knowledge Graph MCP Server | `node:20-slim` (`@modelcontextprotocol/server-memory`) | `blueprint-net` only |
| `blueprint-playwright` | Browser Automation MCP Server | `mcr.microsoft.com/playwright` (`@playwright/mcp`) | `blueprint-net` only |

**Design decision — Isolated CLI Containers:** The CLI agents run in their own isolated containers, connected to both `blueprint-net` and `joshua-net`. This allows them to securely access internal ecosystem MCP endpoints without exposing those endpoints to the physical host. `blueprint-core` connects to these isolated containers via SSH to manage the PTY sessions.

---

## 4. Network Architecture

Blueprint uses a simplified, direct-to-host network model. The `blueprint-core` container serves the UI directly to the host network. The CLI agents are dual-homed, connecting to the private `blueprint-net` for PTY control and `joshua-net` for internal ecosystem access.

```
Browser (Windows)
    │
    ▼
blueprint-core:6342  (Quart serving UI, WebSocket, and REST API)
    ├── /           → React SPA
    ├── /api/       → REST session API
    └── /ws/        → WebSocket terminal streams

blueprint-core:
    └── controls blueprint-claude, blueprint-gemini, etc. via SSH over `blueprint-net`
    └── calls Claude, Gemini Pro, OpenAI APIs directly (blueprint_ask_quorum — external)

blueprint-claude / blueprint-gemini / blueprint-openai:
    └── attached to `joshua-net` to call internal MADs (Rogers, Starret, etc.)
    └── attached to `blueprint-net` for PTY control from blueprint-core

blueprint-postgres:5432
    └── attached to `blueprint-net` only

blueprint-qdrant:6333
    └── attached to `blueprint-net` only

blueprint-qdrant-mcp:8000  (mcp-server-qdrant, SSE transport)
    └── attached to `blueprint-net` only
    └── called by blueprint-claude, blueprint-gemini, blueprint-openai as MCP server

blueprint-memory:3000  (@modelcontextprotocol/server-memory, SSE transport)
    └── attached to `blueprint-net` only
    └── called by blueprint-claude, blueprint-gemini, blueprint-openai as MCP server

blueprint-playwright:8931  (@playwright/mcp, SSE transport, headless Chromium bundled)
    └── attached to `blueprint-net` only
    └── called by blueprint-claude, blueprint-gemini, blueprint-openai as MCP server
```


---

## 5. API Endpoints (Internal)

The `blueprint-core` container exposes a REST API on `blueprint-net` for the UI and internal orchestration. These are not MCP tools.

### `create_team`
```json
{
  "input": {
    "name": { "type": "string", "required": true, "description": "Unique task team name" },
    "cwd": { "type": "string", "required": true, "description": "Absolute Linux path (must start with /)" },
    "description": { "type": "string", "required": false },
    "folder_path": { "type": "string", "required": false, "default": "/", "description": "Hierarchy path e.g. /projects/joshua26" },
    "agents": { "type": "array", "items": { "enum": ["claude", "gemini", "openai"] }, "default": ["claude", "gemini"] },
    "yolo": { "type": "boolean", "default": false, "description": "Enable YOLO mode — amux auto-responds to confirmation prompts in all CLI PTYs" }
  },
  "output": {
    "team_id": "string (uuid)",
    "name": "string",
    "agents_started": "array of agent names"
  }
}
```

### `list_teams`
```json
{
  "input": {
    "folder_path": { "type": "string", "required": false, "description": "Filter by folder" }
  },
  "output": {
    "teams": [
      {
        "team_id": "string",
        "name": "string",
        "description": "string",
        "folder_path": "string",
        "cwd": "string",
        "agents": "array",
        "yolo": "boolean",
        "last_active": "ISO8601",
        "created_at": "ISO8601"
      }
    ],
    "folders": "array of folder paths"
  }
}
```

**Sort order:** `last_active DESC` within each folder — most recently active team floats to the top.

### `get_team`
```json
{
  "input": {
    "team_id": { "type": "string", "required": true }
  },
  "output": {
    "team_id": "string",
    "name": "string",
    "description": "string",
    "folder_path": "string",
    "cwd": "string",
    "agents": [{ "name": "string", "amux_session": "string", "running": "boolean" }],
    "yolo": "boolean",
    "last_active": "ISO8601",
    "created_at": "ISO8601"
  }
}
```

### `move_team`
```json
{
  "input": {
    "team_id": { "type": "string", "required": true },
    "folder_path": { "type": "string", "required": true, "description": "Destination folder path" }
  },
  "output": {
    "team_id": "string",
    "folder_path": "string"
  }
}
```

### `send_message`
```json
{
  "input": {
    "team_id": { "type": "string", "required": true },
    "target": { "type": "string", "enum": ["claude", "gemini", "openai", "all"], "required": true },
    "message": { "type": "string", "required": true }
  },
  "output": {
    "delivered_to": "array of agent names",
    "bridge_file": "string (path written)"
  }
}
```

**Design decision — delivery only:** `send_message` writes the message to a file bridge and injects a read command into the target PTY. It does not scrape or return the target's response. The human reads the response in the xterm.js frame. No idle detection, no response polling.

### `create_folder`
```json
{
  "input": {
    "path": { "type": "string", "required": true, "description": "Full path e.g. /projects/joshua26" }
  },
  "output": {
    "path": "string",
    "created": "boolean"
  }
}
```

## 6. Blueprint MCP Tools

These tools are exposed by the `blueprint-core` MCP server (`http://blueprint-core:8000/mcp`) and are available to all CLI agents via their MCP configuration.

### `blueprint_message_agent_team_member`
Send a message to a peer agent in this team. For CLI agents: delivers via file bridge (read command injected into PTY). For chat agents (Phase 2): queued as user turn. Delivery only — does not return the target's response.
```json
{
  "input": {
    "team_id": { "type": "string", "required": true },
    "target": { "type": "string", "enum": ["claude", "gemini", "openai", "all"], "required": true },
    "message": { "type": "string", "required": true }
  },
  "output": {
    "delivered_to": "array of agent names",
    "bridge_file": "string (path written)"
  }
}
```

### `blueprint_read_core_docs`
Read the Joshua26 core architecture documents and return their contents. Resolves the document list from `docs/guides/core documents.txt` on the workspace volume.
```json
{
  "input": {},
  "output": {
    "documents": [{ "path": "string", "content": "string" }]
  }
}
```
**Usage:** Instructed in each agent's startup file (CLAUDE.md / GEMINI.md / AGENTS.md) to be called automatically at the start of every task team. Ensures the CLI always has current architecture context without manual prompting.

### `blueprint_add_task`
Add a task to the shared task list for the current task team.
```json
{
  "input": {
    "team_id": { "type": "string", "required": true },
    "text": { "type": "string", "required": true },
    "created_by": { "type": "string", "enum": ["claude", "gemini", "openai", "human"], "required": true }
  },
  "output": {
    "task_id": "integer",
    "text": "string",
    "status": "todo"
  }
}
```

### `blueprint_complete_task`
Mark a task as done.
```json
{
  "input": {
    "task_id": { "type": "integer", "required": true }
  },
  "output": {
    "task_id": "integer",
    "status": "done",
    "completed_at": "ISO8601"
  }
}
```

### `blueprint_list_tasks`
List all tasks for a task team. Full history — completed tasks are included.
```json
{
  "input": {
    "team_id": { "type": "string", "required": true }
  },
  "output": {
    "tasks": [{ "task_id": "integer", "text": "string", "status": "string", "created_by": "string", "created_at": "ISO8601", "completed_at": "ISO8601 or null" }]
  }
}
```

### `blueprint_write_session_notes`
Write to the per-agent private scratchpad for this task team. Each agent has its own notes — Claude's notes are separate from Gemini's.
```json
{
  "input": {
    "team_id": { "type": "string", "required": true },
    "agent": { "type": "string", "enum": ["claude", "gemini", "openai"], "required": true },
    "content": { "type": "string", "required": true }
  },
  "output": { "path": "string" }
}
```
**Storage:** `/workspace/blueprint/notes/{team_id_short}_{agent}.md`

### `blueprint_read_session_notes`
Read the per-agent private scratchpad for this task team.
```json
{
  "input": {
    "team_id": { "type": "string", "required": true },
    "agent": { "type": "string", "enum": ["claude", "gemini", "openai"], "required": true }
  },
  "output": { "content": "string" }
}
```

### `blueprint_write_global_notes`
Write to the shared global scratchpad. Visible to all agents across all task teams.
```json
{
  "input": {
    "content": { "type": "string", "required": true }
  },
  "output": { "path": "string" }
}
```
**Storage:** `/workspace/blueprint/notes/global.md`

### `blueprint_read_global_notes`
Read the shared global scratchpad.
```json
{
  "input": {},
  "output": { "content": "string" }
}
```

### `blueprint_write_team_notes`
Write to the shared team notepad. All agents and the human share this notepad — it persists in the `task_teams.notes` database column.
```json
{
  "input": {
    "team_id": { "type": "string", "required": true },
    "content": { "type": "string", "required": true }
  },
  "output": { "team_id": "string" }
}
```

### `blueprint_read_team_notes`
Read the shared team notepad.
```json
{
  "input": {
    "team_id": { "type": "string", "required": true }
  },
  "output": { "content": "string" }
}
```

### `blueprint_fork_team`
Fork a task team — clone the current team's conversation context into a new isolated task team. Useful for branching experimentation without losing the main thread.
```json
{
  "input": {
    "team_id": { "type": "string", "required": true },
    "name": { "type": "string", "required": true, "description": "Name for the forked team" },
    "folder_path": { "type": "string", "required": false, "description": "Destination folder (defaults to same folder as source)" }
  },
  "output": {
    "team_id": "string (new uuid)",
    "name": "string"
  }
}
```

### `blueprint_ask_quorum`
Submit a prompt to Blueprint's lightweight Quorum and receive a synthesized response. Three LLMs respond independently, Gemini Pro synthesizes, one review round, Lead decides what to incorporate.

```json
{
  "input": {
    "prompt": { "type": "string", "required": true, "description": "The question or task to put to the Quorum" }
  },
  "output": {
    "result": "string (Lead's final synthesized response)"
  }
}
```

**Flow (`quorum_graph` in `blueprint-core`):**
```
1. Parallel ask (independent, no cross-visibility):
      Claude  ──┐
   Gemini Pro ──┼── all receive the same prompt
      OpenAI  ──┘

2. Lead synthesis:
   Gemini Pro receives: original prompt + all three responses
   → produces synthesis

3. One review round (independent):
      Claude  ──┐
   Gemini Pro ──┼── all receive: original prompt + synthesis
      OpenAI  ──┘   → each provides feedback

4. Lead decision:
   Gemini Pro receives: synthesis + all three feedbacks
   → incorporates at its discretion → final response
```

**Design principle:** Lead has editorial authority over feedback. No Issue Log, no PM, no forced consensus, no further rounds. Additional rounds cause consensus collapse — responses converge to bland lowest-common-denominator output.

**Model roster:** Flagship reasoning model per provider, configured as environment variables on `blueprint-core` so they can be updated without code changes:
- `QUORUM_MODEL_ANTHROPIC` — flagship reasoning model (e.g. `claude-opus-4-6`)
- `QUORUM_MODEL_GOOGLE` — flagship reasoning model (e.g. `gemini-2.5-pro`)
- `QUORUM_MODEL_OPENAI` — flagship reasoning model (e.g. `o3`)
- `QUORUM_LEAD` — always `google` (Gemini Pro is the Lead)

**Implementation:** Direct API calls from `blueprint-core`. Stateless — no conversation history maintained. API keys from `/storage/credentials/apis/`. No dependency on Hopper or Sutherland.

---

## 7. Data Models

### 7.1 PostgreSQL Schema

**`folders` table**
```sql
CREATE TABLE folders (
    id          SERIAL PRIMARY KEY,
    path        TEXT NOT NULL UNIQUE,   -- e.g. '/projects/joshua26'
    created_at  TIMESTAMPTZ DEFAULT NOW()
);
INSERT INTO folders (path) VALUES ('/');
-- No system-managed archive concept. Users create folders as needed.
```

**`task_teams` table** (Phase 2: renamed `agent_teams`)
```sql
CREATE TABLE task_teams (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name                    TEXT NOT NULL UNIQUE,
    description             TEXT,
    folder_path             TEXT NOT NULL DEFAULT '/',
    cwd                     TEXT NOT NULL,
    agents                  JSONB NOT NULL DEFAULT '["claude","gemini"]',
    yolo                    BOOLEAN NOT NULL DEFAULT FALSE,
    notes                   TEXT,                    -- shared team notepad
    rogers_conversation_id  TEXT,                    -- null until Rogers first reachable
    created_at              TIMESTAMPTZ DEFAULT NOW(),
    last_active             TIMESTAMPTZ DEFAULT NOW(),
    FOREIGN KEY (folder_path) REFERENCES folders(path)
);
-- rogers_conversation_id: the Rogers conversation UUID for this team.
-- 1:1 mapping — one agent team = one Rogers conversation, forever.
-- Populated lazily on first successful Rogers connection after team creation.
```

**`task_team_agents` table**
```sql
CREATE TABLE task_team_agents (
    id              SERIAL PRIMARY KEY,
    team_id         UUID NOT NULL REFERENCES task_teams(id) ON DELETE CASCADE,
    agent_name      TEXT NOT NULL,          -- 'claude' | 'gemini' | 'openai'
    amux_session_id TEXT,                   -- amux session name e.g. 'a1b2c3d4_claude'
    active          BOOLEAN NOT NULL DEFAULT TRUE,  -- FALSE = pane closed by user
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
```

**`task_team_tasks` table**
```sql
CREATE TABLE task_team_tasks (
    id           SERIAL PRIMARY KEY,
    team_id      UUID NOT NULL REFERENCES task_teams(id) ON DELETE CASCADE,
    created_by   TEXT,                      -- 'claude' | 'gemini' | 'openai' | 'human'
    text         TEXT NOT NULL,
    status       TEXT NOT NULL DEFAULT 'todo',  -- 'todo' | 'done'
    created_at   TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);
-- Full history kept — tasks are never deleted, only marked done.
```

### 7.2 amux Session Naming Convention

amux sessions are named: `{team_id_short}_{agent}` — e.g., `a1b2c3d4_claude`, `a1b2c3d4_gemini`.
`team_id_short` = first 8 chars of task team UUID.

### 7.3 File Bridge Convention

Inter-CLI messages using the file bridge write to:
`/workspace/blueprint/bridges/{team_id_short}_{timestamp}.md`

The bridge file is written by `send_message`, then the target CLI receives:
`read /workspace/blueprint/bridges/{filename}` injected via amux.

### 7.4 Notes Storage Convention

| Notes type | Path | Scope |
|---|---|---|
| Per-agent session notes | `/workspace/blueprint/notes/{team_id_short}_{agent}.md` | Private to one agent within one team |
| Team notepad | `task_teams.notes` column in postgres | Shared within one team, all agents |
| Global notes | `/workspace/blueprint/notes/global.md` | Shared across all teams and all agents |

---

## 7. LangGraph Flows

The `blueprint-core` backend logic is implemented as a `StateGraph` to ensure architectural consistency and future extensibility, even though Blueprint is not a MAD. The Quart routes are thin wrappers that invoke the compiled graph.

**`team_ops` flow** — CRUD on task teams and folders
- Nodes: `validate_input` → `execute_db_op` → `format_response`
- Handles: create_team, list_teams, get_team, move_team, create_folder
- DB: asyncpg pool to blueprint-postgres
- Updates `last_active` on any team interaction

**`message_routing` flow** — Send message to CLI agent(s)
- Nodes: `validate_team` → `resolve_targets` → `write_bridge_file` → `send_to_amux` → `confirm_delivery`
- Calls: amux REST API via httpx (`http://localhost:8822/api/sessions/{name}/send`) — amux runs in-process on port 8822 within blueprint-core
- File bridge: writes to `/workspace/blueprint/bridges/` then injects read command

**`task_ops` flow** — CRUD on task team tasks
- Nodes: `validate_input` → `execute_db_op` → `format_response`
- Handles: add_task, complete_task, list_tasks

**`notes_ops` flow** — Read/write session notes, team notepad, global notes
- Nodes: `validate_input` → `execute_notes_op` → `format_response`
- Session notes: file read/write on workspace volume
- Team notepad: postgres UPDATE on task_teams.notes
- Global notes: file read/write on workspace volume

**`fork_team` flow** — Fork a task team
- Nodes: `validate_team` → `clone_amux_sessions` → `create_team_record` → `confirm`
- Uses amux conversation fork API to clone PTY session history into new amux sessions
- Creates new task_team record linked to destination folder

---

## 8. Storage

| Volume | Path | Purpose |
|---|---|---|
| `storage` | `/storage` | Global credentials, shared project files |
| `workspace` | `/workspace` | Task team metadata, bridge files, UI build, DB data, home dirs, notes |

**Workspace layout:**
```
/workspace/blueprint/
├── databases/
│   ├── postgres/data/      # PostgreSQL data files (irina local SSD)
│   ├── qdrant/             # Qdrant vector DB storage (irina local SSD)
│   └── memory/             # Knowledge graph JSON (memory MCP server)
├── bridges/                # Inter-CLI file bridge temp files
├── notes/                  # Per-agent session notes + global notes
│   └── global.md           # Global shared scratchpad
├── ui/                     # React SPA build output (served by Quart)
└── home/
    ├── claude/             # Claude Code auth + history
    ├── gemini/             # Gemini CLI auth
    └── openai/             # OpenAI CLI auth
```

**Credential files:**
- Postgres password: `/storage/credentials/blueprint/postgres.txt`
- CLI auth tokens are persisted via home directory volume mounts.

---

## 9. Container Details

### 9.1 `blueprint-core` Container
**Base image:** `python:3.12-slim`
**Contents:**
- Quart (for serving UI and APIs)
- amux (for PTY management)
- tmux (system package)
- openssh-client (for connecting to CLI agent containers)

**Startup:** `quart --app server:app --host 0.0.0.0 --port 6342`

**Health check:** `GET http://localhost:6342/health` — Returns `{"status": "healthy"}`.

### 9.2 `blueprint-claude`, `blueprint-gemini`, `blueprint-openai`
**Base image:** `node:20-slim`
**Contents:**
- openssh-server (for receiving PTY connections from `blueprint-core`)
- The respective CLI tool (e.g., `@anthropic-ai/claude-code`)

**Home directory persistence:**
Each agent container sets `HOME=/workspace/blueprint/home/<agent>` as an environment variable (e.g., `HOME=/workspace/blueprint/home/claude`). Since `workspace:/workspace` is already mounted, `~/` resolves inside the volume with no additional bind mounts required. This complies with REQ-000 §3.2 (no subdirectory mounts).

**MCP configuration:** At session creation, `blueprint-core` writes MCP server config into each agent's home dir so the CLI has access to all Blueprint MCP servers:
- Blueprint MCP: `http://blueprint-core:8000/mcp` — `blueprint_message_agent_team_member`, `blueprint_read_core_docs`, `blueprint_ask_quorum`, `blueprint_add_task`, `blueprint_complete_task`, `blueprint_list_tasks`, `blueprint_write_session_notes`, `blueprint_read_session_notes`, `blueprint_write_team_notes`, `blueprint_read_team_notes`, `blueprint_write_global_notes`, `blueprint_read_global_notes`, `blueprint_fork_team`
- Qdrant MCP: `http://blueprint-qdrant-mcp:8000` — `qdrant-store`, `qdrant-find`
- Memory MCP: `http://blueprint-memory:3000` — `create_entities`, `search_nodes`, `read_graph`, etc.
- Playwright MCP: `http://blueprint-playwright:8931` — `browser_navigate`, `browser_snapshot`, etc.

**Startup instruction files:** `blueprint-core` writes an instruction file into each agent's home dir at session creation. These files carry no role or persona — the user establishes working roles through conversation. The file paths and formats are:

| Agent | File | Format |
|---|---|---|
| `blueprint-claude` | `~/.claude/CLAUDE.md` | Markdown |
| `blueprint-gemini` | `~/.gemini/GEMINI.md` | Markdown |
| `blueprint-openai` | `~/.codex/AGENTS.md` | Markdown |

**Content (same substance for all three, adapted to each CLI's native filename):**
```
You are running inside Blueprint, a multi-agent CLI workbench on irina (192.168.1.110).

You are one of three CLI agents forming a task team:
- Claude (blueprint-claude)
- Gemini (blueprint-gemini)
- OpenAI/Codex (blueprint-openai)

You can send a message to a peer agent using the `blueprint_message_agent_team_member` MCP tool.
The message is delivered via a file bridge — your peer will receive a read command
pointing to a file containing your message.

Available MCP tools:
- blueprint_message_agent_team_member         — send a message to @claude, @gemini, @openai, or @all
- blueprint_read_core_docs       — read the Joshua26 core architecture documents
- blueprint_ask_quorum           — submit a question to a three-model synthesis quorum
- blueprint_add_task             — add a task to the team's shared task list
- blueprint_complete_task        — mark a task as done
- blueprint_list_tasks           — list all tasks for this task team
- blueprint_write_session_notes  — write to your private scratchpad for this task team
- blueprint_read_session_notes   — read your private scratchpad for this task team
- blueprint_write_team_notes     — write to the shared team notepad
- blueprint_read_team_notes      — read the shared team notepad
- blueprint_write_global_notes   — write to the global shared scratchpad (all teams)
- blueprint_read_global_notes    — read the global shared scratchpad (all teams)
- blueprint_fork_team            — fork this task team into a new isolated branch
- qdrant-store / qdrant-find     — vector search over the codebase and conversation history
- create_entities / search_nodes / read_graph (and others) — persistent knowledge graph
- browser_navigate / browser_snapshot (and others) — headless browser automation

At the start of every task team, call blueprint_read_core_docs to load current
architecture context before beginning work.
```

**MCP config format:** Claude and Gemini use JSON settings files; Codex uses `~/.codex/config.toml` with `[mcp_servers.<name>]` TOML sections. `blueprint-core` writes the correct format for each agent.

### 9.3 `blueprint-postgres` Container
**Base image:** `postgres:16-alpine` (OTS)
**Init schema:** See Section 7.1
**Data path:** `/workspace/blueprint/databases/postgres/data` (local irina SSD for I/O)

### 9.4 `blueprint-qdrant` Container
**Base image:** `qdrant/qdrant` (OTS — digest must be pinned at implementation)
**Data path:** `/workspace/blueprint/databases/qdrant/` (local irina SSD for I/O)
**Collections:**
- `joshua26-codebase` — embeddings of the Joshua26 repository files
- `cli-conversations` — embeddings of CLI conversation history files

### 9.7 `blueprint-playwright` Container
**Base image:** `mcr.microsoft.com/playwright` (OTS — includes all Chromium dependencies)
**Package:** `@playwright/mcp` (npm)
**Transport:** SSE (HTTP), port 8931
**Mode:** Headless — no display required
**MCP tools exposed:** `browser_navigate`, `browser_click`, `browser_type`, `browser_snapshot`, `browser_take_screenshot`, and others
**Purpose:** Self-contained browser automation. Zero dependency on Joshua26 (Malory). Enables CLIs to browse documentation, test web UIs, and scrape pages.
**Health check:** `GET http://localhost:8931/` → 200
**Note:** Chromium bundled in base image. Offline-capable after initial image pull.

### 9.6 `blueprint-memory` Container
**Base image:** `node:20-slim`
**Package:** `@modelcontextprotocol/server-memory` (npm)
**Transport:** SSE (HTTP), port 3000
**Storage:** Knowledge graph persisted to `/workspace/blueprint/databases/memory/memory.json`
**MCP tools exposed:** `create_entities`, `create_relations`, `add_observations`, `search_nodes`, `read_graph`, `delete_entities`, `delete_observations`, `delete_relations`
**Purpose:** Persistent structured knowledge across sessions and across CLI agents. Survives context resets. Claude and Gemini share the same graph — collective understanding of the codebase accumulates over time.
**Health check:** `GET http://localhost:3000/` → 200

### 9.5 `blueprint-qdrant-mcp` Container
**Base image:** `python:3.12-slim`
**Package:** `mcp-server-qdrant` (PyPI)
**Transport:** SSE (HTTP), port 8000
**Embedding model:** `sentence-transformers/all-MiniLM-L6-v2` via FastEmbed — runs on CPU, no GPU dependency, no Joshua26 dependency
**Environment:**
- `QDRANT_URL=http://blueprint-qdrant:6333`
- `FASTMCP_HOST=0.0.0.0`
- `FASTMCP_PORT=8000`
- No default `COLLECTION_NAME` set — callers specify per tool call
**MCP tools exposed:** `qdrant-store`, `qdrant-find` (collection_name specified per call)
**Health check:** `GET http://localhost:8000/` → 200

---

## 10. Identity and Permissions

| Container | UID | GID | User |
|---|---|---|---|
| `blueprint-core` | 2035 | 2001 | `blueprint` |
| `blueprint-claude` | 2035 | 2001 | `blueprint` |
| `blueprint-gemini` | 2035 | 2001 | `blueprint` |
| `blueprint-openai` | 2035 | 2001 | `blueprint` |
| `blueprint-postgres` | 2035 | 2001 | `blueprint` |
| `blueprint-qdrant` | 2035 | 2001 | `blueprint` |
| `blueprint-qdrant-mcp` | 2035 | 2001 | `blueprint` |
| `blueprint-memory` | 2035 | 2001 | `blueprint` |
| `blueprint-playwright` | 2035 | 2001 | `blueprint` |

All containers share the same UID/GID to ensure seamless file access on the shared `/workspace` volume.

---

## 11. Health Strategy

The `blueprint-core` `/health` endpoint checks for connectivity to the `blueprint-postgres` database. The UI is responsible for reporting WebSocket connection status for the PTY streams.

---

## 12. Package Caching (Exception)

**Exception:** Unified package cache not available. Per ADR-037, local `packages/` directories used for offline builds.
- `blueprint-core/packages/pip/`
- `blueprint-claude/packages/npm/`
- etc. for other CLI containers

---

## 13. Python Requirements (`blueprint-core`)

```
quart==0.19.9
asyncpg==0.30.0
httpx==0.28.1
langgraph==0.2.60
langchain-core==0.3.83
```

---

## 14. UI Architecture

The React SPA is served by `blueprint` (blueprint-core) from `/workspace/blueprint/ui/`. Built with React + Vite. Routes: `/` (home), `/team/{team_id}` (workspace).

---

### 14.1 Home Dashboard (`/`)

Two-panel layout:

**Left — Folder tree:**
- Hierarchical folder tree of all folders and task teams
- Create folder button
- Task teams shown under their folder, sorted by `last_active` DESC
- Double-click a task team → open in new browser tab (or focus existing tab)

**Right — Team metadata pane:**
- Shows selected team: name, description, CWD, agents, last_active, yolo state
- **Launch button** → opens team workspace in new browser tab (`window.open('/team/{team_id}', 'blueprint-team-{team_id}')`) — focuses existing tab if already open
- Move team to different folder

---

### 14.2 Team Workspace (`/team/{team_id}`)

Each task team opens in its own **browser tab**. Navigating to `/team/{team_id}` in a browser tab shows the full workspace for that team.

**4-pane layout (resizable):**

| Pane | Contents |
|---|---|
| Pane 1 | Claude terminal (`xterm.js`) |
| Pane 2 | Gemini terminal (`xterm.js`) |
| Pane 3 | OpenAI terminal (`xterm.js`) |
| Pane 4 | File browser |

**Header bar:**
- Team name, CWD
- Global Escape button — sends SIGINT (`\x03`) to all active terminals
- Fork Team button
- Popout tab buttons: Tasks, Team Notes, My Notes (per-agent), Global Notes

**Popout tabs (float over workspace):**
- Tasks — add/complete tasks, full history
- Team Notes — shared team notepad
- My Notes — per-agent session notes (one per CLI pane)
- Global Notes — shared across all teams

---

### 14.3 Terminal Panes

Each terminal pane (`xterm.js`) connects via WebSocket to `/ws/{amux_session_name}` on reconnect. The amux tmux session is already running; scrollback history arrives naturally on reconnect.

**Per-pane controls:**
- **Agent name label** (e.g. "Claude")
- **Active/Inactive indicator** — pane can be closed (agent goes inactive); closed pane shows a reactivate button
- **YOLO toggle** — enables amux auto-response to confirmation prompts in this pane
- **Export chat button** — exports terminal scrollback as `.md` file; dialog lets user choose destination path in the workspace

**Terminal link detection:**
- File paths matching workspace patterns (e.g. `/workspace/...`, `/storage/...`) are clickable → opens artifact tab
- URLs (http/https) are clickable → opens new browser tab

**Keyboard:**
- Escape key when terminal focused → sends SIGINT (`\x03`) to that terminal's PTY

---

### 14.4 File Browser (Pane 4)

Tree view similar to Cursor's Explorer panel.

**Root:** Team's CWD. Workspace mount (`/workspace/`) accessible above it.

**File interactions:**
- **Single click** → inserts file path into command bar
- **Double click** → opens artifact tab showing file contents

---

### 14.5 Command Bar

Fixed at the bottom of the workspace. Single text input for routing prompts to agents.

**`@` autocomplete:**
- Typing `@` opens dropdown showing active agents + `@all`
- Unique first-letter completion: `@c`+Tab→`@claude`, `@g`+Tab→`@gemini`, `@o`+Tab→`@openai`, `@a`+Tab→`@all`
- Autocomplete shows only active agents (inactive agents shown greyed out)

**Mention logic:**
| Input | Effect |
|---|---|
| `@claude` (no message) | Focus the Claude pane |
| `@claude <message>` | Send message to Claude via file bridge; no focus change |
| `@all <message>` | Send message to all **active** agents; no focus change |
| `@claude` when Claude inactive | Reactivate Claude (restart amux session), then apply focus rule |
| `/command` when `@all` active | Blocked — slash commands are CLI-specific, cannot broadcast |

**File bridge:** When message content is large, backend writes to bridge file and injects a short read command into the target PTY(s).

---

### 14.6 Artifact Tabs

Artifact tabs float over the workspace when opened (from file browser double-click or clickable link in terminal).

**Supported types:**
- **Text/code/markdown files** — rendered with syntax highlighting
- **Web pages** — displayed in an `<iframe>`
- **Other file types** — shows the file browser panel for that file's location

**Auto-update:** Artifact tab polls `GET /api/files/content?path={path}` every 4 seconds. If content changed, re-renders automatically.

Multiple artifact tabs can be open simultaneously. Each has a close button.

---

### 14.7 Agent Active/Inactive State

Each agent in a task team can be **active** (PTY session running) or **inactive** (pane closed by user).

- Closing a terminal pane → marks agent inactive, stops the amux session
- Inactive agent shown as closed pane with a "Reactivate" button
- `@agent` mention when agent is inactive → reactivates (calls `POST /api/teams/{team_id}/agents/{agent}/activate`)
- `@all` only sends to active agents

**Schema addition:** `task_team_agents.active BOOLEAN NOT NULL DEFAULT TRUE`

---

### 14.8 Additional API Endpoints (UI-required)

Beyond §5, the UI requires:

```
GET  /api/files?path={path}               # List directory contents
GET  /api/files/content?path={path}       # Read file content (for artifact tab)
POST /api/teams/{team_id}/agents/{agent}/activate   # Reactivate inactive agent
POST /api/teams/{team_id}/agents/{agent}/close      # Deactivate agent (close pane)
POST /api/teams/{team_id}/export?agent={agent}&path={path}  # Export terminal as .md
```

---

## 15. Verification

### Integration Scenarios

1. **Full task team lifecycle:** Create team → send messages via Command Bar → add tasks → complete tasks → move team to folder
2. **File bridge:** Send large code block to `@claude` via file bridge, verify clean delivery
3. **Inter-CLI handoff:** Send message to `@gemini`, get output, send that output to `@claude`
4. **joshua-net access:** From the `@gemini` terminal frame, successfully execute a `curl http://starret:8010/health`
5. **Browser workflow:** Open dashboard, create team, open workspace tab, type in terminal frames and Command Bar
6. **Notes:** Agent writes session notes, reads them back after context reset; team notepad updated by human and visible to all agents
7. **Task list:** Agent adds task via `blueprint_add_task`, human sees it in UI task panel, agent marks complete via `blueprint_complete_task`
8. **Fork team:** Fork active team into new branch, verify separate amux sessions created with cloned context
9. **Quorum:** Agent calls `blueprint_ask_quorum`, receives synthesized multi-model response

---

## 16. Phase 2 — Agent Teams

### 16.1 Terminology Changes (Phase 1 → Phase 2)

| Phase 1 | Phase 2 | Notes |
|---|---|---|
| task team | agent team | The team is defined by its agents |
| `task_teams` table | `agent_teams` | DB rename + migration |
| `task_team_agents` table | `agent_team_members` | + new columns |
| `task_team_tasks` table | `agent_team_tasks` | Rename only |
| `blueprint_message_peer_cli` / `blueprint_send_message` | `blueprint_message_agent_team_member` | Covers CLI + chat agents |
| Command bar | Broadcast button | Removed command bar; broadcast popout with checkboxes |
| Fixed 3-pane layout | 2-wide or 4-square grid | User-configurable at team level |

### 16.2 Agent Types

**CLI Agent** — unchanged from Phase 1. SSH into dedicated container, tmux PTY streaming.

**Chat Agent** — new. Runs as a LangGraph flow inside `blueprint-core`. No dedicated container.
- Model: any OpenAI-compatible endpoint from the admin model catalog
- LangGraph flow: `create_react_agent` (ReAct tool loop) + compaction node + postgres message storage
- Client: `langchain_openai.ChatOpenAI(base_url, api_key, model)` — one adapter for all endpoints
- Tools: same Blueprint MCP tools as CLI agents, loaded via `langchain_mcp_adapters`
- File context: drag file from browser sidebar onto chat pane → path injected at cursor in input

### 16.3 Compaction Algorithm

Each model has a configured `max_context_tokens`. Compaction triggers when accumulated tokens reach **90%** of that limit.

On trigger:
1. Take the oldest **80%** of messages by token count
2. Summarize them → target ~20% of original token count
3. Replace those messages with a single "Prior context summary" message
4. Keep the most recent **10%** of messages verbatim

Post-compaction context: ~30% full (20% summary + 10% recent). Leaves substantial room before next trigger.

### 16.4 Admin Configuration — Custom Agent Catalog

`/settings` page. Manages the catalog of **custom agents** available for inclusion in agent teams.

A custom agent is a configured persona backed by an LLM — not a model configuration. Two custom agents can share the same underlying model (same `model_id` + `base_url`) but have different aliases and system prompts, making them distinct agents with different behaviors. Example: "GPT SW Engineer" and "GPT Document Writer" both backed by `gpt-4o` at `https://api.openai.com/v1`.

CLI agents (Claude Code, Gemini CLI) are **not** in this catalog. Their LLM is controlled from within the CLI itself.

**`custom_agents` table:**
```sql
CREATE TABLE custom_agents (
    id                  SERIAL PRIMARY KEY,
    alias               TEXT NOT NULL UNIQUE,  -- display name, e.g. "GPT SW Engineer"
    model_id            TEXT NOT NULL,          -- API model string, e.g. "gpt-4o"
    base_url            TEXT NOT NULL,          -- OpenAI-compatible endpoint URL
    max_context_tokens  INTEGER NOT NULL,       -- model context window; drives compaction at 90%
    system_prompt       TEXT,                   -- persona / behavior; injected as system message
    credentials_ref     TEXT NOT NULL,          -- filename under /storage/credentials/blueprint/models/
    created_at          TIMESTAMPTZ DEFAULT NOW()
);
```

API key stored at `/storage/credentials/blueprint/models/{credentials_ref}` — credential volume, not in DB.

### 16.5 Extended Agent Team Schema

**`agent_team_members` table (replaces `task_team_agents`):**
```sql
CREATE TABLE agent_team_members (
    id              SERIAL PRIMARY KEY,
    team_id         UUID NOT NULL REFERENCES agent_teams(id) ON DELETE CASCADE,
    agent_type      TEXT NOT NULL DEFAULT 'cli',  -- 'cli' | 'chat'
    agent_name      TEXT,                          -- 'claude' | 'gemini' | 'openai' (cli only)
    custom_agent_id INTEGER REFERENCES custom_agents(id), -- custom agent only
    display_name    TEXT NOT NULL,                 -- shown in pane header
    session_id      TEXT,                          -- tmux session name (cli) or chat session ref
    position        INTEGER NOT NULL DEFAULT 0,   -- 0-3, determines grid position
    active          BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
```

**`agent_team_chats` table (new):**
```sql
CREATE TABLE agent_team_chats (
    id                SERIAL PRIMARY KEY,
    team_id           UUID NOT NULL REFERENCES agent_teams(id) ON DELETE CASCADE,
    member_id         INTEGER NOT NULL REFERENCES agent_team_members(id) ON DELETE CASCADE,
    role              TEXT NOT NULL,        -- 'user' | 'assistant' | 'tool' | 'summary'
    content           TEXT NOT NULL,
    tool_calls        JSONB,                -- tool call details if role='tool'
    token_count       INTEGER,              -- from API response usage field, for compaction
    synced_to_rogers  BOOLEAN NOT NULL DEFAULT FALSE,  -- Rogers sync flag
    created_at        TIMESTAMPTZ DEFAULT NOW()
);
```

`synced_to_rogers` enables graceful Rogers integration: records accumulate in postgres while Rogers is unreachable, drain to Rogers when the connection is restored. Memory search is available when Rogers is up, silently absent when it is not.

### 16.6 Workspace Layout and Pane Management

**View modes:** 1-pane, 2-wide, 4-square. Switchable within the workspace. View mode persisted per team.

**File browser:** Resizable sidebar, never an agent slot.

**Slot-based assignment:** A pane is a viewport slot. Any team agent can occupy any slot. Agent is selected from a dropdown in the pane header (`[Agent Name ▾]`). Slot assignments persisted per team.

**Exclusive:** Each agent appears in at most one slot at a time.

**Swap on conflict:** Picking an already-assigned agent from another slot's dropdown triggers a swap. No agent is displaced without a home.

**1-pane tab switching:** In 1-pane view the dropdown acts as a tab switcher. All agents keep running; only the focused agent is visible.

**Status-based border colors:**

| State | Color | Trigger |
|---|---|---|
| Idle | Dim neutral | No PTY data for ~2s (CLI) or `agent_state: idle` event (chat) |
| Working | Bright green | PTY data flowing (CLI) or `agent_state: working` event (chat) |
| Notification | Amber | Agent produced output while its slot was not visible |

Chat agents emit explicit `{type:"agent_state", state:"working"|"idle"}` WebSocket events from the LangGraph flow. CLI agents use a client-side PTY activity timer (no backend polling).

The notification state enables background awareness in 1-pane view: the agent selector pill for non-visible agents glows amber when they produce output, signalling the user to switch.

**DB additions for slot management:**
```sql
-- In agent_team_members:
ADD COLUMN position INTEGER NOT NULL DEFAULT 0,  -- 0-3, which slot this agent is assigned to
ADD COLUMN view_mode TEXT NOT NULL DEFAULT '2-wide'  -- '1-pane'|'2-wide'|'4-square' on agent_teams
```

### 16.7 Broadcast (Updated)

Broadcast popout includes checkboxes for each agent in the team, defaulting to all checked. The user deselects any agents they want to exclude before sending.

- CLI agents: `tmux send-keys` types message + Enter directly into PTY
- Chat agents: message queued as user turn, triggers a new LangGraph flow invocation

---

## 17. Host Affinity

Blueprint runs exclusively on **irina** (192.168.1.110).

---

## 17. Exceptions from REQ-000

| Item | Exception | Reason | Mitigation |
|---|---|---|---|
| Unified package caching | ADR-037 local packages/ used | Unified cache not yet built | Local packages/ dirs per container |
| REQ-000 §4.10 — LLM routing via Sutherland | Direct external API calls from CLI containers | These CLIs are subscription-based tools whose API routing cannot be redirected to Sutherland; this is the intended design | Controlled by the architect; no automated context escalation |
| ADR-052 — postgres anonymous volume | `postgres:16-alpine` declares internal `VOLUME`; explicit bind mount required | OTS postgres image behaviour | Bind mount to `/workspace/blueprint/databases/postgres/data` specified in docker-compose |
| Codex CLI (blueprint-openai) | Not yet deployed | CLI auth complexity; container not yet built | Container pattern matches blueprint-claude/gemini; deploy when auth flow confirmed |
