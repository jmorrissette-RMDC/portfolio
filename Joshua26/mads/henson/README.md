# Henson — Human Interaction Hub

Henson is the Universal Human Switchboard for Joshua26. It centralizes all human-facing interaction: hosting chat UIs, routing between persona-driven imperators (guest companions Gunner and Grace, the Henson host persona, and future MAD imperators), and delegating memory to Rogers and compute to LLM backends. Phase 1 establishes the container topology, UI routing, and baseline human-to-imperator interaction. Future phases will introduce the Brain/Voice split (sovereign local prose via Sutherland), agentic tool use, and MAD-to-MAD autonomous communication.

---

## Container Inventory

| Container | Base Image | Port (internal) | Role |
|---|---|---|---|
| `henson` | `node:20-slim` | `9224` (host) | MCP gateway — bridges `joshua-net` + `henson-net`; serves MCP at `/mcp` and UI at `/` via `ui_proxy` |
| `henson-langgraph` | `python:3.12-slim` | `8000` (henson-net) | Quart logic engine — Shared Imperator Graph, OpenAI-compatible API |
| `henson-postgres` | `postgres:16-alpine` | `5432` (henson-net) | Persona registry + session state |
| `henson-nginx` | `nginxinc/nginx-unprivileged:alpine` | `8080` (henson-net) | UI reverse proxy (routes `/v1/` → langgraph, `/` → Open WebUI) |
| `henson-openwebui` | `ghcr.io/open-webui/open-webui:main` | `8080` (henson-net) | Primary chat frontend (Phase 1) |

All containers run on `m5`. Only the `henson` gateway is accessible from outside `henson-net`.

---

## LAN Access

**Chat UI:** `http://192.168.1.120:9224/`

Browser traffic is routed through the gateway's `ui_proxy` feature: `gateway → henson-nginx:8080 → henson-openwebui:8080`. No direct host port binding on nginx or Open WebUI.

---

## MCP Endpoint

**For MAD-to-MAD use (on `joshua-net`):** `http://m5:9224/mcp`

Available MCP tools:

| Tool | Description |
|---|---|
| `henson_chat_turn` | Invoke the Shared Imperator Graph as the Henson host persona |
| `henson_list_personas` | Return all persona IDs and display names |
| `henson_switch_session_persona` | Map a session ID to a persona ID |

---

## Persona Management

Personas are rows in the `henson-postgres.personas` table. To add a new persona, insert a row and it immediately appears in the Open WebUI model picker (via `GET /v1/models`). The `model` field in OpenAI API requests maps directly to the `persona_id` column.

The `henson` persona (host imperator) is the default for `henson_chat_turn` MCP calls. `gunner` and `grace` are Phase 1 guest personas accessible via the UI.

---

## Credentials Setup

The following credential files must exist on `m5` before the first `docker compose up` (see REQ-henson §10.1):

| File | Used by |
|---|---|
| `/storage/credentials/henson/postgres.txt` | `henson-postgres` (POSTGRES_PASSWORD_FILE) |
| `/storage/credentials/henson/openai-api-key.txt` | `henson-langgraph` via `grace` persona row |

Local LLM backends (Henson host, Gunner) use `http://sutherland:11434/v1` with no API key.

---

## Phase Roadmap

- **Phase 1 (current):** Container topology, UI routing, baseline human-to-imperator interaction via Shared Imperator Graph. Single-model calls, generic Rogers context, no tool use.
- **Phase 2:** Brain/Voice split — frontier model for reasoning, sovereign local model (Sutherland) for prose generation. Agentic tool use (web search, Git, Calendar). Fiedler alias routing.
- **Phase 3:** MAD-to-MAD autonomous communication without a human initiator. Custom Rogers context assemblies (CAG for Grace, Mem0 graph RAG for Gunner).
