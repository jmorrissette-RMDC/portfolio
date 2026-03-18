**Reviewer:** Gemini
**Gate:** 2
**MAD:** kaiser
**Date:** 2026-03-11

- **Gate 2: FAILED**

**Blockers:**
1. **Sutherland Peer Proxy Port Mismatch:** In `kaiser/nginx.conf`, the `/peer/sutherland/` location proxies all traffic to `http://sutherland:11435`. However, `registry.yml` notes that Sutherland's MCP endpoint is on `11435` and its API is on port `80`. In `kaiser-langgraph/flows/imperator.py`, the Imperator uses `http://kaiser:9226/peer/sutherland/v1` to send OpenAI Chat Completion requests. Proxying these `/v1` API requests to the MCP port (`11435`) instead of the API port (`80`) will cause all Imperator inference to fail.
   *Fix:* Update `kaiser/nginx.conf` to explicitly map paths to the correct ports (e.g., proxy `/peer/sutherland/v1/` to `sutherland:80/v1/` and `/peer/sutherland/mcp` to `sutherland:11435`).

**Observations:**
1. **Unused Dependency:** `quart` is still listed in `kaiser-langgraph/requirements.txt`, but `kaiser-langgraph/server.py` successfully implemented the migration to `Starlette` (along with FastMCP's integration). `quart` can be safely removed.
2. **Deferred Digest Pinning:** `nginx:1.27.4-alpine` and `postgres:16-alpine` base images are unpinned. This aligns with the approved `EX-KAISER-003` deviation, but remember that the exact digests must be pinned during the Gate 3 deployment phase.
3. **Starlette Lifespan Override:** In `kaiser-langgraph/server.py`, the custom `_lifespan` generator is passed directly to the `Starlette` app instance, bypassing `_mcp_app.lifespan`. While this mirrors the established pattern in Alexandria, be aware that it will skip any future startup/shutdown hooks built into FastMCP itself.

**Recommendations:**
1. **Explicit API vs MCP Peer Paths:** Given the mixed-port nature of MADs like Sutherland (serving both MCP and HTTP APIs on different ports), consider adopting a stricter peer proxy convention in `nginx.conf` (e.g., `/peer/{peer}/mcp` and `/peer/{peer}/api`) to prevent opaque protocol errors when routing traffic.
2. **Alexandria Outage Handling:** Although the `EX-KAISER-001` exemption allows runtime pip installation via the `/pypi/` proxy, verify that `kaiser_install_package` gracefully catches connection timeouts to the nginx proxy and returns a structured status error, ensuring clear diagnostics if Irina or Alexandria are unreachable during eMAD provisioning.
