# Gate 1 Review — vannevar
**Reviewer:** Gemini
**Date:** 2026-03-03
**Verdict:** FAILED

---

## Blockers

1. **REQ-000 §4.10 (LLM Routing) Violation:** The REQ states that `vannevar-amux` will run Claude Code and Gemini CLI. These CLI tools communicate directly with Anthropic and Google APIs by default. REQ-000 §4.10 strictly forbids any MAD (other than Sutherland) from making direct external LLM API calls. You must either configure the CLIs to use Sutherland as their base URL (if supported) or explicitly list an exception for REQ-000 §4.10 in Section 22.

2. **REQ-000 §3.2 (Volume Mount Correctness) Violation:** Section 11 specifies environment mounts like `/workspace/vannevar/home/claude/ -> ~/.claude/`. REQ-000 §3.2 strictly forbids mounting subdirectories. Containers must mount the root volume `workspace:/workspace`. To map home directories inside the container, create a symlink during container startup (e.g., in a `start.sh` script: `ln -s /workspace/vannevar/home/claude ~/.claude`) rather than using docker-compose volume sub-mounts.

3. **REQ-000 §3.1 (Anonymous Volume / ADR-052) Missing Exception:** Section 12 specifies the postgres data path, but the `postgres:16-alpine` image declares a `VOLUME` at `/var/lib/postgresql/data`. Per REQ-000 §3.1 and ADR-052, this will create an untracked anonymous volume unless explicitly bind-mounted. You must either add the bind mount to the design and declare the ADR-052 exception in Section 22, or use the `template-postgres` pattern correctly to address this.

4. **State 2 Architecture (OTS Infrastructure) Clarification:** `vannevar-amux` is a heavily custom-built container (Python + Node.js + tmux + amux + multiple CLIs), contradicting the State 2 Principle 1 that the only custom-built container is `[mad]-langgraph`. While the REQ justifies it as a "utility container", this is a significant architectural deviation. It must be explicitly listed as an approved exception in Section 22.

---

## Observations

1. **amux Logging:** `amux serve` likely does not output structured JSON logs by default. You may need to wrap its execution or configure its logging to comply with REQ-000 §5.2 (Structured Logging Format).

2. **Nginx WebSocket Proxy:** The nginx configuration for `/ws/` sets `proxy_read_timeout 3600s;`. WebSocket connections can still drop due to intermediate network states. Ensure the UI handles WebSocket reconnects gracefully.

3. **Session Persistence:** Storing session state in PostgreSQL is solid, but ensure `van_archive_session` actually stops the underlying `tmux` sessions in `vannevar-amux` to reclaim memory. Verify the langgraph flow explicitly handles the `amux` teardown.

---

## Recommendations

1. **Security:** Consider adding an authorization layer to the nginx gateway for the React SPA, as this MAD will expose direct CLI access to the ecosystem and potentially external APIs. Even though it's on a private network (`joshua-net`), basic auth at the nginx layer provides defense-in-depth.

2. **Codex CLI:** Deferring Codex to Phase 2 is a wise decision given the complexity of auth and integration.
