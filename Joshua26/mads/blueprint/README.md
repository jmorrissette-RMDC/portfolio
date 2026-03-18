# Blueprint — Architect's Workbench

**Host:** irina (192.168.1.110) | **Port:** 6342 | **UID:** 2035

Browser-based multi-agent CLI workbench. Three isolated CLI agents (Claude Code, Gemini CLI, OpenAI CLI) running in separate containers, orchestrated via amux PTY multiplexer. Not a MAD — standalone infrastructure with zero Joshua26 ecosystem dependency.

## Quick Start

```bash
# On irina
docker compose -f docker-compose.yml -f docker-compose.irina.yml up -d \
  blueprint-core blueprint-claude blueprint-gemini \
  blueprint-postgres blueprint-qdrant blueprint-qdrant-mcp \
  blueprint-memory blueprint-playwright

# Open browser
http://192.168.1.110:6342
```

## Pre-Launch Requirements

```bash
# Create credential files
mkdir -p /storage/credentials/blueprint
echo "your-postgres-password" > /storage/credentials/blueprint/postgres.txt
mkdir -p /storage/credentials/apis
echo "your-anthropic-key" > /storage/credentials/apis/anthropic
echo "your-google-key" > /storage/credentials/apis/google
echo "your-openai-key" > /storage/credentials/apis/openai

# Create workspace directories
mkdir -p /mnt/storage/workspace/blueprint/databases/postgres/data
mkdir -p /mnt/storage/workspace/blueprint/databases/qdrant
mkdir -p /mnt/storage/workspace/blueprint/databases/memory
mkdir -p /mnt/storage/workspace/blueprint/bridges
mkdir -p /mnt/storage/workspace/blueprint/notes
mkdir -p /mnt/storage/workspace/blueprint/home/claude
mkdir -p /mnt/storage/workspace/blueprint/home/gemini
mkdir -p /mnt/storage/workspace/blueprint/home/openai
```

## Containers

| Container | Role | Port |
|---|---|---|
| `blueprint-core` | Quart server, amux, LangGraph, MCP endpoint | 6342 (host), 8822 (amux internal) |
| `blueprint-claude` | Claude Code CLI (SSH) | 22 (internal) |
| `blueprint-gemini` | Gemini CLI (SSH) | 22 (internal) |
| `blueprint-postgres` | Task team metadata DB | 5432 (internal) |
| `blueprint-qdrant` | Vector search DB | 6333 (internal) |
| `blueprint-qdrant-mcp` | Qdrant MCP server | 8000 (internal) |
| `blueprint-memory` | Knowledge graph MCP server | 3000 (internal) |
| `blueprint-playwright` | Browser automation MCP server | 8931 (internal) |

## Blueprint MCP Tools

Available to all CLI agents at `http://blueprint-core:6342/mcp`:

| Tool | Description |
|---|---|
| `blueprint_send_message` | Deliver message to target CLI via file bridge |
| `blueprint_read_core_docs` | Read Joshua26 core architecture documents (called at team start) |
| `blueprint_ask_quorum` | Three-model quorum: parallel ask → Gemini synthesis → one review round |
| `blueprint_add_task` | Add task to shared team task list |
| `blueprint_complete_task` | Mark task done |
| `blueprint_list_tasks` | List all team tasks (full history) |
| `blueprint_write_session_notes` | Write to per-agent private scratchpad |
| `blueprint_read_session_notes` | Read per-agent private scratchpad |
| `blueprint_write_team_notes` | Write to shared team notepad |
| `blueprint_read_team_notes` | Read shared team notepad |
| `blueprint_write_global_notes` | Write to global shared scratchpad |
| `blueprint_read_global_notes` | Read global shared scratchpad |
| `blueprint_fork_team` | Fork task team into new isolated branch |

## Health Check

```bash
curl http://192.168.1.110:6342/health
```

## Documentation

- `docs/HLD-blueprint.md` — High-level architecture
- `docs/REQ-blueprint.md` — Full requirements specification
