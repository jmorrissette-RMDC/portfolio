# Kaiser — eMAD Hosting MAD

**UID:** 2036 | **Port:** 9226 | **Host:** m5 | **State:** 3

Kaiser is the dedicated eMAD hosting MAD and the first State 3 MAD in the Joshua26 ecosystem.
It executes subject-domain eMAD libraries installed from Alexandria (internal PyPI) at runtime —
no container rebuild required to add or update eMADs.

## MCP Tools

| Tool | Description |
|---|---|
| `kaiser_chat` | Send a message to a named eMAD instance and receive a response |
| `kaiser_list_emads` | List all registered eMAD instances with parameters and status |
| `kaiser_install_package` | Install an eMAD package from Alexandria and refresh the registry |
| `kaiser_create_emad` | Register a named eMAD instance backed by an installed package |
| `kaiser_update_emad` | Update the parameters or description of an existing eMAD instance |
| `kaiser_delete_emad` | Remove a named eMAD instance (does not uninstall the package) |
| `kaiser_imperator_chat` | Converse with Kaiser's Imperator for lifecycle management and advice |
| `metrics_get` | Return Prometheus metrics (REQ-000 §4.11) |

## Quick Start

```bash
# Deploy
docker compose -f docker-compose.yml -f docker-compose.m5.yml up -d kaiser kaiser-langgraph kaiser-postgres

# Health
curl http://m5:9226/health

# Install first eMAD
curl -X POST http://m5:9226/mcp ...  # kaiser_install_package("hopper-emad")

# Create instance
# kaiser_create_emad("hopper", "hopper-emad", "Engineering Department", {})

# Chat
# kaiser_chat("hopper", "session-001", "describe your capabilities")
```

## eMAD Library Contract

eMAD packages must expose in their `pyproject.toml`:
```toml
[project.entry-points."kaiser.emads"]
my_emad = "my_emad.register:build_graph"
```

And in their Python module:
```python
EMAD_PACKAGE_NAME = "my-emad"
DESCRIPTION = "What this eMAD does"
SUPPORTED_PARAMS = {"system_prompt": "str", "temperature": "float"}

def build_graph(params: dict) -> StateGraph: ...
```

Initial state received: `messages`, `rogers_conversation_id`, `rogers_context_window_id`.
Must populate `final_response` before returning.

## See Also

- `docs/REQ-kaiser.md` — full requirements
- `docs/concepts/concept-state3-mad.md` — State 3 MAD pattern
