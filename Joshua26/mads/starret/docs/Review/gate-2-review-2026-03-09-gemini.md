**Reviewer:** Gemini
**Gate:** 2
**MAD:** starret
**Date:** 2026-03-09

**Gate 2: FAILED**
The implementation successfully implements the Imperator pattern and GitHub API functionality according to the design, heavily utilizing `asyncio` and `httpx` compliant with requirements. However, the `docker-compose.yml` configuration for the `github-runner` container violates the strict volume mounting and image tagging requirements defined in REQ-000. 

### Blockers
1. **Docker Compose - `github-runner` Version Pinning (REQ-000 §1.7):** The `github-runner` image is set to `latest` (`image: ghcr.io/actions/actions-runner:latest`) in `docker-compose.yml`. REQ-000 §1.7 requires all dependencies, including Docker images, to be locked to specific versions.
2. **Docker Compose - `github-runner` Volume Mounts (REQ-000 §3.1 & §3.2):** The `github-runner` container defines four volumes, including a new named volume (`runner-workspace:/runner/_work`) and direct host subdirectory paths (`/mnt/storage/certs/ssh:/home/runner/.ssh:ro`). REQ-000 §3.1 mandates exactly two volumes (`storage:/storage` and `workspace:/workspace`), and §3.2 forbids mounting host subdirectories. If the runner requires specific mount structures or exceptions, they must either be resolved by mounting `storage` and `workspace` and symlinking internally, or a formal exception must be documented and approved in `REQ-000-exception-registry`.

### Observations
1. **GitHub Token Loading Consistency:** In `flows/github_ops.py`, `_GITHUB_TOKEN` is loaded once at the module level when the container starts. In `flows/imperator.py`, `_load_github_token()` is called on every invocation of tools like `git_push`. Both are technically compliant with REQ-000 §3.5, but if the token changes, `github_ops.py` will require a container restart to pick it up, while `imperator.py` will not.
2. **FastMCP Route Mapping in Nginx:** The `nginx.conf` proxies `/mcp` to `starret-langgraph:8000/mcp`. With FastMCP's `stateless_http=True` being mounted at `/` in `server.py` (`Mount("/", _mcp_app)`), please verify that the FastMCP ASGI app is indeed exposing the `/mcp` path locally rather than the root path or `/sse`.
3. **`github-runner` Docker Socket Mount:** The `github-runner` mounts `/var/run/docker.sock`, granting root-level control over the host Docker daemon. While necessary for deployment tasks, this is a significant security privilege and should ideally be explicitly documented in the architectural and REQ documents.

### Recommendations
1. **Refactor `_write_metadata_comment` (Connection Pooling):** In `flows/github_ops.py`, `_write_metadata_comment` uses two separate `async with httpx.AsyncClient(timeout=15.0) as client:` blocks in sequence (one for GET, one for PATCH). This defeats connection pooling. They should be wrapped in a single client context manager block to reuse the connection.
2. **Centralize Token Management:** Create a shared utility function for retrieving the GitHub token that standardizes the behavior across all flows, ensuring both security and ease of rotation without container restarts.
3. **Runner SSH Configuration:** Instead of directly mounting `/mnt/storage/certs/ssh`, mount `storage:/storage` and configure the runner environment or start script to look for its SSH keys in `/storage/certs/ssh` or copy them to `~/.ssh` during container startup.