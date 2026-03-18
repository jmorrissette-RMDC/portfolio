**Reviewer:** Gemini
**Gate:** 2
**MAD:** kaiser
**Date:** 2026-03-11

- **Gate 2: FAILED**
- **Blockers:**
  - **Direct LLM API Call (REQ-000 §4.10 & State 2 Principles):** `mads/kaiser/kaiser-langgraph/flows/imperator.py` uses `ChatOpenAI(base_url="http://kaiser:9226/peer/sutherland/v1")` to call Sutherland's OpenAI-compatible API directly. REQ-000 §4.10 strictly forbids this: "No MAD (other than Sutherland) may call external LLM providers... or local model APIs directly". The Imperator MUST use `langchain-mcp-adapters` to call the `llm_chat_completions` (or similar) MCP tool provided by Sutherland, as defined by the State 2 architectural requirements.
  - **Missing Dependency:** `langchain-mcp-adapters` is not present in `mads/kaiser/kaiser-langgraph/requirements.txt`. It is mandated for making outbound MCP peer calls from LangGraph. You should add `langchain-mcp-adapters` and can likely remove `langchain-openai`.
  - **Incorrect Peer Proxy Routing:** In `mads/kaiser/kaiser/nginx.conf`, the `sutherland` peer block rewrites `/peer/sutherland/(.*)` to `/$1` and passes it to `sutherland:11435`. Hitting port 11435 with `/v1/chat/completions` will fail, because `11435` is Sutherland's FastMCP endpoint, not its OpenAI API endpoint (which is on port 80). Even if it were port 80, routing to the API directly bypasses MCP. When `langchain-mcp-adapters` is properly used, the peer proxy should target the `/mcp` endpoint directly, as shown in the `HLD-MAD-container-composition.md` State 2 docs.

- **Observations:**
  - **FastMCP Route Mounting:** In `mads/kaiser/kaiser-langgraph/server.py`, `_mcp_app = mcp.http_app(stateless_http=True)` is mounted at `/` (via `Mount("/", _mcp_app)`). Verify that FastMCP correctly processes requests proxied to `/mcp`, as `nginx.conf` sets `proxy_pass http://$lg/mcp;`. If FastMCP expects the root path for stateless HTTP, you may need to adjust the mount point or nginx rewrite rule.
  - **Docker Base Images (EX-KAISER-003):** `mads/kaiser/kaiser/Dockerfile` uses `nginx:1.27.4-alpine` and `mads/kaiser/kaiser-postgres/Dockerfile` uses `postgres:16-alpine` without digest pins. This is allowed by EX-KAISER-003, but remember that the digests must be pinned before closing Gate 3.
  - **PostgreSQL Bind Mount (EX-KAISER-002):** Handled correctly in `docker-compose.yml`.

- **Recommendations:**
  - **Review State 2 Peer Calls:** Reference `docs/designs/HLD-MAD-container-composition.md` under "Outbound Calls from LangGraph (Peer Proxy)" for the correct `langchain-mcp-adapters` initialization code using `MultiServerMCPClient`.