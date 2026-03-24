# HLD: Blueprint — Architect's Workbench

**Version:** 2.0
**Date:** 2026-03-04
**Status:** Phase 1 Complete — Phase 2 Design
**Requirements:** `mads/blueprint/docs/REQ-blueprint.md`

---

## 1. Purpose

Blueprint is the architect's multi-agent workbench for Joshua26. It provides a browser-based environment for working simultaneously with multiple AI agents — both CLI-based tools (Claude Code, Gemini CLI) and API-based chat agents (any OpenAI-compatible model endpoint) — against Linux execution environments on irina.

**Blueprint is not a MAD.** It sits outside the Joshua26 ecosystem logical boundary, with no dependency on Sutherland, Rogers, Henson, or any other MAD. If Joshua26 is completely down, Blueprint remains fully operational — which is precisely when it is most needed.

---

## 2. Design Principles

- **Zero ecosystem dependency:** All backing services are self-contained. No Sutherland, no Rogers, no Hopper required for core operation.
- **Human in the loop:** The architect drives all agent interactions. Blueprint is not an autonomous orchestrator. The human watches terminal frames and chat interfaces, retains direct control, and intervenes when needed.
- **No MAD compliance overhead:** No Nginx gateway, no Imperator, no Apgar metrics. These exist for autonomous MADs — Blueprint is a workbench.
- **LangGraph for ALL programmatic logic — no exceptions.** Every piece of backend logic — request handling, background tasks, polling loops, sync processes, data pipelines — lives in a LangGraph StateGraph. LangGraph is specifically built for loops, cycles, conditional branching, and long-running flows. Code written outside a StateGraph is only acceptable when it is literally impossible to express in LangGraph, or so trivially mechanical (e.g. a one-line format conversion) as to make no practical difference. Transport layer wiring in server.py (route handlers that call `graph.ainvoke()`) is acceptable; logic inside those handlers is not. When in doubt: put it in the graph.

---

## 3. Container Architecture

```
blueprint-core          — Quart + LangGraph. UI server, PTY multiplexer,
                          chat agent engine, Blueprint MCP server, Rogers sync.
blueprint-claude        — Claude Code CLI in isolated container.
blueprint-gemini        — Gemini CLI in isolated container.
blueprint-openai        — Codex CLI in isolated container.
blueprint-postgres      — Agent team metadata, chat history, custom agent catalog.
blueprint-playwright    — @playwright/mcp. Headless Chromium, browser automation.
```

**Phase 1 containers removed in Phase 2:**
- `blueprint-qdrant` — memory/search delegated to Rogers
- `blueprint-qdrant-mcp` — same
- `blueprint-memory` — same

All containers run on `blueprint-net`. CLI containers are additionally connected to `joshua-net`.

---

## 4. Network Topology

```
Browser (Windows)
    │ port 6342
    ▼
blueprint-core  ──── blueprint-net ────┬── blueprint-postgres
    │            └── joshua-net ───┐   └── blueprint-playwright
    │ SSH (PTY control)            │
    ├── blueprint-claude ──────────┤
    ├── blueprint-gemini ──────────┤
    └── blueprint-openai ──────────┘
                                   │
                              joshua-net ──── Rogers, and other internal MADs

blueprint-core on joshua-net: required for Rogers sync (chat agent turns).
CLI containers on joshua-net: MCP tool calls to Rogers directly.

blueprint-core also calls external APIs directly:
    ├── OpenAI-compatible endpoints (chat agents, quorum)
    └── Quorum: Claude, Gemini Pro, OpenAI APIs
```

CLI containers are dual-homed, enabling them to call internal Joshua26 MCP endpoints natively without those endpoints being exposed to the physical host.

---

## 5. Agent Types

Every pane in a Blueprint workspace is an **agent**. Two types:

### 5.1 CLI Agent

A full interactive terminal connected to a dedicated CLI container via SSH + tmux PTY streaming.

- Container: `blueprint-claude`, `blueprint-gemini`, `blueprint-openai`
- Transport: WebSocket → `tmux attach-session` → SSH → CLI process
- Capabilities: file editing, shell commands, MCP tool use, full CLI feature set
- Provisioned at team creation with: instruction file (CLAUDE.md / GEMINI.md / AGENTS.md), MCP config pointing at all Blueprint services

### 5.2 Chat Agent

A minimal LangGraph ReAct chat interface running directly in `blueprint-core`. No dedicated container.

- Model: any OpenAI-compatible endpoint, configured by the architect in the admin settings
- Transport: browser chat UI → REST API → LangGraph flow → OpenAI-compatible API
- Capabilities: conversation, MCP tool use (same tools as CLI agents), file context via drag-and-drop
- Architecture: ReAct agent (LangGraph `create_react_agent`) + compaction node + postgres message history
- No system persona — the architect establishes the working role through conversation

**Why not OTS?** OTS chatbots come with unwanted chrome. The LangGraph implementation gives exactly what's needed: chat loop, tool use, compaction, history. Nothing more.

---

## 6. Agent Team Concept

An **agent team** is a named workspace with 1–4 configured agents (any mix of CLI and chat), a working directory, and shared tooling (tasks, notes, file browser).

- Teams are organized in a hierarchical folder navigator on the home dashboard
- Each team opens in its own browser tab
- Teams persist indefinitely — no archive concept; the folder hierarchy is the organizational structure
- Agent active/inactive state persists in the DB — reopening a team restores exactly what was open

**Agent team member composition examples:**
- 2 CLI agents: Claude Code + Gemini CLI — pair programming, peer review
- 1 CLI + 1 chat: Claude Code CLI + GPT-4o chat — agent doing the work, model providing strategy
- 4 agents: Claude Code + Gemini CLI + Gemini Pro chat + Claude Haiku chat — full review board
- 1 CLI alone: single agent deep work session

---

## 7. Workspace Layout and Pane Management

### 7.1 Pane Views

Three view modes, switchable within the workspace:

```
1-pane:                2-wide:                4-square:
┌──────────────┐       ┌───────┬───────┐       ┌───────┬───────┐
│              │       │       │       │       │       │       │
│   Slot 0     │       │ Slot0 │ Slot1 │       │ Slot0 │ Slot1 │
│              │       │       │       │       ├───────┼───────┤
│              │       │       │       │       │ Slot2 │ Slot3 │
└──────────────┘       └───────┴───────┘       └───────┴───────┘
```

File browser is a **resizable sidebar** — always available, never occupying a pane slot.

### 7.2 Slot-Based Agent Assignment

A pane is a **viewport slot**, not bound to a specific agent. Any team agent can occupy any slot. The agent is selected via a dropdown in the pane header (right side of header): `[Claude Code ▾]`.

**Exclusive assignment:** Each agent appears in at most one slot. No agent can be shown twice.

**Swap behavior:** If Slot 0 shows Agent A and Slot 1 shows Agent B, and the user picks Agent A from Slot 1's dropdown — they swap. Agent B moves to Slot 0, Agent A moves to Slot 1. No agent is ever displaced without a home.

**1-pane view as tab switcher:** In 1-pane view the dropdown functions as a tab switcher. All team agents keep running in their background sessions; only the selected one is visible. Switching is instant — connects to the new agent's session.

**Slot assignments persisted per team** — reopening the workspace restores the view mode and which agent was in which slot.

### 7.3 Status-Based Pane Border Colors

All pane borders share the same base styling — color conveys **state**, not identity. Identity is shown by the label in the header.

| State | Border | Meaning |
|---|---|---|
| Idle | Dim neutral | Agent at prompt, waiting for input |
| Working | Bright active (green) | Generating response or running tools |
| Notification | Amber | Activity in this agent while it was not the focused pane |

The notification state solves 1-pane view: if you're focused on Claude and you broadcast, Gemini starts working in the background. Its entry in the agent dropdown pill glows amber — you know to switch without having to guess.

**Activity detection:**

- **Chat agents** — explicit. LangGraph flow sends a WebSocket state event (`{type:"agent_state", state:"working"|"idle"}`) when generation starts and ends.
- **CLI agents** — heuristic. TerminalPane tracks when PTY bytes last arrived. Data within ~2 seconds → `working`. Silence → `idle`. Purely client-side, no backend polling.
- **Notification** — when an agent's session produces output (PTY data or chat response) while its slot is not currently visible, its dropdown pill transitions to amber notification state.

### 7.4 Token Count Display

A thin fill bar (3-4px) at the bottom of each pane shows context window usage. Color: green → amber → red as it fills. Hover tooltip: `"X,XXX / Y,XXX tokens (ZZ%) — compaction at 90%"`.

**Token count sources — no tokenizer library required:**

| Agent type | Source | How accessed |
|---|---|---|
| Claude Code CLI | JSONL session file: last assistant entry `usage.input_tokens + cache_creation_input_tokens + cache_read_input_tokens` | blueprint-core SSHes into blueprint-claude, reads latest `/home/blueprint/.claude/projects/*/*.jsonl` |
| Gemini CLI | JSON session file: last gemini entry `tokens.input` | blueprint-core SSHes into blueprint-gemini, reads latest `/home/blueprint/.gemini/tmp/*/chats/session-*.json` |
| Codex CLI | Session file format TBD — investigate `/home/blueprint/.codex/` on first deploy of blueprint-openai | blueprint-core SSHes into blueprint-openai, same pattern as above |
| Custom agent | OpenAI-compatible API response `usage.prompt_tokens` — stored in `agent_team_chats.token_count` at message write time | Read from postgres: `SUM(token_count)` for this member's chat history |

Each model counts tokens in its own tokenizer natively and reports the real count in API responses. We never estimate — we always use the authoritative source. The `custom_agents.max_context_tokens` field provides the Y (denominator) for the bar.

---

## 8. Interaction Model

**Routing:** `/` → Home dashboard. `/settings` → Admin config. `/team/{team_id}` → Team workspace.

**Home dashboard:** Hierarchical folder tree. Agent teams are leaf nodes sorted by `last_active DESC` within folders. Right-click / inline buttons for create subfolder, create team, delete. Drag teams between folders. Metadata pane shows CWD, last active, editable description, shared team notes. Launch button opens workspace in new browser tab.

**Workspace:**
- Agent panes fill the main area in 2-wide or 4-square layout
- File browser sidebar (resizable) — drag files onto any agent pane to inject path at cursor
- **Broadcast button** in header — opens popout with textarea, checkboxes for which agents receive, Ctrl+Enter to send. Types message directly into each selected agent's PTY (CLI) or queues as user turn (chat). Slash commands blocked.
- **Escape All** — sends SIGINT to all active CLI terminals
- **Fork** — creates a branched copy of the current agent team

**CLI agent pane:** xterm.js terminal. Click to focus, then type directly. Full ANSI rendering. Scrollback preserved on reconnect (tmux session survives browser close). Per-pane: YOLO toggle, Export scrollback as .md, Session notes, Close/Reactivate.

**Chat agent pane:** Scrollable message history (markdown rendered). Input textarea at bottom. Tool use shown inline (collapsible). Drag file from browser → path injected at cursor in input. Per-pane: Session notes, Clear context (keeps history, resets context window), Close/Reactivate.

**File browser (sidebar):** Tree rooted at team CWD. Navigate up to `/storage/` root. Drag file → drops path into whichever agent pane you release it on. Double-click → opens artifact tab (rendered content, auto-polls for changes).

**Artifact tabs:** Float in header row. Text/code/markdown rendered with syntax highlighting. Auto-refreshes every 4 seconds if file changed.

**Popout tabs:** Tasks, Team Notes, Global Notes, Session Notes (per-agent). Team notes also editable in home dashboard metadata pane — same data.

---

## 9. Blueprint MCP Server

`blueprint-core` exposes an MCP server at `http://blueprint:6342/mcp`. Provisioned to all agents (CLI via config files, chat via LangGraph tool loading).

| Tool | Description |
|---|---|
| `blueprint_message_agent_team_member` | Send a message to a peer agent in this team via file bridge (CLI) or message queue (chat). Delivery only. |
| `blueprint_read_core_docs` | Read Joshua26 core architecture documents. Called automatically at team start. |
| `blueprint_ask_quorum` | Lightweight three-model quorum. Parallel ask → Lead synthesis → one review round → Lead decides. |
| `blueprint_add_task` / `blueprint_complete_task` / `blueprint_list_tasks` | Shared task list for the agent team. |
| `blueprint_write_session_notes` / `blueprint_read_session_notes` | Per-agent private scratchpad scoped to this team. |
| `blueprint_write_team_notes` / `blueprint_read_team_notes` | Shared notepad for all agents in this team. |
| `blueprint_write_global_notes` / `blueprint_read_global_notes` | Shared scratchpad across all teams. |
| `blueprint_fork_team` | Fork this agent team into a new isolated branch. |

All agents also have access to: `blueprint-qdrant-mcp` (vector search), `blueprint-memory` (knowledge graph), `blueprint-playwright` (browser automation).

---

## 10. Chat Agent Architecture

The chat agent LangGraph flow runs inside `blueprint-core`.

```
user_message
     │
     ▼
react_agent_node  ──[tools needed]──► tool_executor ──► react_agent_node
     │
     ▼ (final response)
compaction_check
     │ (if token count > threshold)
     ▼
summarize_history_node
     │
     ▼
store_message_node
     │
     ▼
response → browser
```

**Model client:** `langchain_openai.ChatOpenAI(base_url=..., api_key=..., model=...)` — one adapter for all endpoints. Points at the LLM configured in this custom agent's catalog entry.

**System prompt:** Injected as the system message on every invocation from the custom agent's `system_prompt` field. This is what differentiates two agents backed by the same model.

**Tool loading:** `langchain_mcp_adapters.MultiServerMCPClient` pointing at `http://blueprint:6342/mcp` (self-referential within the container). Loads all Blueprint MCP tools at session start.

**Compaction:** Each model entry in the admin config includes a `max_context_tokens` field. When accumulated message tokens reach **90% of max_context_tokens**, compaction triggers. The oldest **80%** of the history is summarized into a single "prior context" summary message (~20% of original size). The most recent **10%** of messages are kept verbatim. Result: the context window after compaction is ~30% full (20% summary + 10% recent), leaving substantial room before the next compaction.

**Storage:** All messages stored in `agent_team_chats` table in postgres. History loads on workspace open, persists across browser close.

---

## 11. Admin Configuration — Custom Agent Catalog

`/settings` page (accessible from home dashboard). Manages the catalog of **custom agents** available for inclusion in agent teams.

A custom agent is not a model — it is a configured persona backed by an LLM. Two custom agents can share the same underlying model with completely different aliases and system prompts. For example: "GPT SW Engineer" and "GPT Document Writer" are both backed by GPT-4o but have distinct behaviors via their system prompts.

Each custom agent entry:
- **Alias** — the display name shown in the pane header and agent picker (e.g., "GPT SW Engineer")
- **Model ID** — API model string (e.g., `gpt-4o`, `claude-opus-4-6`, `llama-3.1-70b`)
- **Base URL** — OpenAI-compatible endpoint (OpenAI, Together AI, Groq, Ollama, etc.)
- **Max context tokens** — the model's context window size; drives compaction threshold (90%)
- **System prompt** — TEXT; establishes persona and behavior. Written as the system message on every invocation.
- **Credentials ref** — filename in `/storage/credentials/blueprint/models/`; API key stored as file, not in DB

CLI agents (Claude Code, Gemini CLI) are **not** configurable here. Their LLM is controlled from within the CLI itself. Blueprint only provisions their environment (instruction files, MCP config).

---

## 12. Memory and Rogers Integration

### 12.1 What Blueprint Owns (Always Works)

Blueprint is responsible for one thing with respect to memory: **chat agent context management**. The compaction flow (§10) manages the context window for custom agents. This must always work regardless of ecosystem state — if it breaks, the chat agents break.

Chat turns are stored in `agent_team_chats` in blueprint-postgres. This is Blueprint's source of truth for chat history.

### 12.2 What Rogers Owns (Graceful Degradation)

Rogers provides the real memory capability for the ecosystem:
- Optimised context retrieval
- Conversation history search (vector)
- Knowledge graph extraction and query

When Rogers is reachable (via `joshua-net`), Blueprint sends chat turns to Rogers and exposes Rogers search tools to agents. When Rogers is down or unavailable, **memory search is simply not available** — no error, the core functionality continues unaffected. Blueprint's purpose is to fix the ecosystem, not depend on it.

### 12.3 Agent Team = Rogers Conversation

Rogers has a **conversation** concept. A Blueprint agent team maps 1:1 to a Rogers conversation — one forever-conversation per team, accumulating all agent activity across all sessions.

`agent_teams` has a `rogers_conversation_id TEXT` column (nullable). Null until Rogers has been reached and the conversation created.

### 12.4 Sync Flow (LangGraph)

`agent_team_chats` has a `synced_to_rogers BOOLEAN NOT NULL DEFAULT FALSE` column.

The sync is implemented as a **long-running LangGraph StateGraph with a cycle** — `rogers_sync_flow` in `flows/rogers_sync.py`. This is the correct pattern: LangGraph is built for exactly this kind of persistent, conditional, polling loop. It is started as a background coroutine at server startup and runs for the lifetime of blueprint-core.

```
check_rogers_health
    │ unhealthy                  │ healthy
    ▼                            ▼
wait_node               get_unsynced_records
    │                            │ none        │ records exist
    │                            ▼             ▼
    │                       wait_node    ensure_conversations_exist
    │                            │             │
    └────────────────────────────┘             ▼
                                         sync_batch_to_rogers
                                               │
                                               ▼
                                          wait_node ──► check_rogers_health (cycle)
```

**Nodes:**
- `check_rogers_health` — calls `GET http://rogers:6380/health`, sets state flag
- `get_unsynced_records` — queries postgres for `synced_to_rogers = FALSE`
- `ensure_conversations_exist` — for any team with `rogers_conversation_id IS NULL`, creates Rogers conversation and stores the returned ID
- `sync_batch_to_rogers` — sends unsynced turns to their team's Rogers conversation via `conv_store_message`, marks `synced_to_rogers = TRUE`
- `wait_node` — asyncio sleep (configurable interval, default 60s)

Best-effort. Records accumulate while Rogers is down and drain when it comes back.

### 12.5 CLI Agent Memory

CLI agents are on `joshua-net` and call Rogers MCP tools directly. At session start, blueprint-core writes the team's `rogers_conversation_id` into the agent's instruction file — so the CLI knows which Rogers conversation it belongs to and can store its own turns there directly. One unified conversation history per agent team, across all agent types.

---

## 14. Persistence

PostgreSQL (`blueprint-postgres`):
- `folders` — hierarchical folder structure for agent team organization
- `agent_teams` (formerly `task_teams`) — name, CWD, description, notes, last_active, folder_path
- `agent_team_members` (formerly `task_team_agents`) — per-agent slot: agent_type (cli|chat), chat_model_id, position (0-3), active state
- `agent_team_tasks` — shared task list per team
- `custom_agents` — admin-configured agent catalog (alias, model_id, base_url, max_context_tokens, system_prompt, credentials_ref)
- `agent_team_chats` — custom agent message history (team_id, member_id, role, content, tool_calls, token_count, created_at)

Notes layers:
- Per-agent session notes: markdown file `/workspace/blueprint/notes/{team_id_short}_{agent_slot}.md`
- Team notepad: `agent_teams.notes` column
- Global notes: `/workspace/blueprint/notes/global.md`

CLI auth tokens and history persist in agent home directories on the workspace volume.

---

## 15. Host Affinity

Blueprint runs exclusively on **irina** (192.168.1.110). UID 2035, GID 2001, port 6342.
