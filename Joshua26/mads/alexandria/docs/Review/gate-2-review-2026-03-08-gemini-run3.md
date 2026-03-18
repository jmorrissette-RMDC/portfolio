**Reviewer:** Gemini
**Gate:** 2
**MAD:** alexandria
**Date:** 2026-03-08

- **Gate 2: FAILED**

- **Blockers:**
  1. **Docker Registry Persistence Configuration (`config-templates/registry/config.yml`)**: `alexandria-registry` in `docker-compose.yml` mounts the shared host volume via `- storage:/storage`, but the config file directs the registry to store image layers at `/var/lib/registry`. Because `/var/lib/registry` is not explicitly mapped to a persistent volume in `docker-compose.yml`, the image layers will be lost to an ephemeral anonymous volume and will not persist in the Joshua26 `storage` volume. The `rootdirectory` in `config-templates/registry/config.yml` must be updated to `/storage/images/nineveh` (or similar subpath) to align with the compose volume mount, just as the Verdaccio config correctly points to `/storage/packages/npm`.
  2. **MCP SSE Routing Mismatch (`alexandria-langgraph/server.py` and `alexandria/nginx.conf`)**: Nginx proxies the `/mcp` path exactly as `proxy_pass http://alexandria-langgraph:8000/mcp;`. However, the Starlette app in `server.py` mounts the FastMCP app at the root: `Mount("/", mcp.http_app(stateless_http=True))`. This means FastMCP expects requests at `/sse` and `/messages`, but Nginx is sending them to `/mcp/sse` and `/mcp/messages`. Starlette will return a 404 for these routes. You must change the mount point in `server.py` to `Mount("/mcp", mcp.http_app(stateless_http=True))` to match the Nginx proxy path.

- **Observations:**
  1. **Base Image Tagging (`docker-compose.yml`)**: `alexandria-registry` uses `image: registry:2` and `alexandria-verdaccio` uses `image: verdaccio/verdaccio` (implicit latest). REQ-000 §1.4 requires pinning base images. Consider pinning these to explicit versions or sha256 digests (e.g., `verdaccio/verdaccio:5.x.x@sha256:...`) to guarantee reproducible offline builds and prevent unexpected updates.
  2. **Anonymous Volumes**: Because the official Verdaccio and Registry 2.0 Dockerfiles declare `VOLUME /verdaccio/storage` and `VOLUME /var/lib/registry`, and these specific paths are not bound in `docker-compose.yml` (since it mounts `- storage:/storage` instead), Docker will still create empty anonymous volumes on the host for them. This won't cause data loss (since the configs redirect the actual storage to `/storage/...`), but it will leave unused anonymous volumes on the Docker host.

- **Recommendations:**
  1. **Pin Official Images**: Update `docker-compose.yml` to use specific sha256 digests for `registry` and `verdaccio` to comply fully with the ecosystem's offline-capable requirements.
