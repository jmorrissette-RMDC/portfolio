**Reviewer:** Gemini
**Gate:** 2
**MAD:** alexandria
**Date:** 2026-03-08

### Gate 2: FAILED

**Blockers:**
1. **Missing Exception for Nginx Logging (REQ-000 §5.2):** `alexandria/nginx.conf` disables `access_log` and uses `error_log` which writes plain text warnings. REQ-000 §5.2 strictly requires structured JSON logging. Since Nginx error logs cannot be easily formatted as JSON natively, an explicit exception is required. Please add an exception (e.g., `EX-ALEXANDRIA-008`) to `docs/requirements/REQ-000-exception-registry.md` and the `REQ-alexandria.md` document to formalize this deviation, mirroring the existing Verdaccio and Registry exceptions.

**Observations:**
1. **Template Residue Files:** `mads/alexandria/alexandria/` still contains `server.js`, `package.json`, `package-lock.json`, and `config.json`. The implementation plan notes these were removed during Gate 2 Run 2, but they are still present in the filesystem. Since the `Dockerfile` uses Nginx as the gateway, these Node.js files are unused and should be deleted to prevent confusion.
2. **Dockerfile `USER` Directive Sequence (REQ-000 §2.1):** In `alexandria/Dockerfile`, the `USER ${USER_NAME}` directive occurs *after* the `COPY` and `RUN chmod +x /start.sh` commands. REQ-000 §2.1 states that the `USER` directive must immediately follow user creation, with all application file operations occurring after. `alexandria-langgraph` and `alexandria-devpi` correctly follow this pattern. 
3. **Nginx `chown -R` on `/var/log/nginx`:** In `alexandria/Dockerfile`, `chown -R ${USER_NAME}:administrators /var/log/nginx` is used. The official `nginx:alpine` image symlinks `/var/log/nginx/access.log` and `error.log` to `/dev/stdout` and `/dev/stderr`. Running a recursive `chown` on this directory might follow symlinks and attempt to change ownership of the stdout/stderr targets, which can occasionally cause permission errors in Docker. Consider chowning the directory specifically without `-R`.

**Recommendations:**
1. **FastMCP SSE Route Compatibility:** The plan notes that the FastMCP `http_app()` was verified to serve the stream at `/mcp` directly. By default, standard FastMCP implementations expose the SSE endpoint at `/sse` and the message endpoint at `/messages`. Please ensure that either `alexandria-langgraph` overrides these defaults to `/mcp` or Nginx `proxy_pass` is correctly mapping the URIs. If FastMCP is actually listening on `/sse`, the current Nginx configuration (`proxy_pass http://alexandria-langgraph:8000/mcp;`) will result in a 404 from Starlette.
2. **Delete Unused Template Files:** Delete `mads/alexandria/alexandria/server.js`, `package.json`, `package-lock.json`, and `config.json` as noted in Observation 1.