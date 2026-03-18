# Hopper MAD

**The Engineering Department**

Hopper provides autonomous software development lifecycle management and a multi-LLM Quorum Engine for complex reasoning, code generation, and test planning.

## Architecture

- **Stateless Design:** No internal databases. Conversation and knowledge state is managed by Rogers.
- **Quorum Engine:** Executes parallel multi-LLM drafting, cross-pollination, synthesis, and PM-filtered gridlock resolution.
- **Agent Roles:** 
  - `Imperator`: Triage and conversation management (front door).
  - `software_engineer`: Task execution agent.

## Tools

| Tool | Description | Inputs | Outputs |
|------|-------------|--------|---------|
| `hopper_chat` | Primary conversational interface | `message` (string), `project_context` (optional string) | Natural language response, SSE stream of Quorum state |

## Configuration

See `mads/hopper/docs/REQ-hopper.md` for full implementation and architectural details.

## Deployment

Deploy via the standard Joshua26 deployment script to `m5`:
```bash
py scripts/deployment/deploy.py hopper
```