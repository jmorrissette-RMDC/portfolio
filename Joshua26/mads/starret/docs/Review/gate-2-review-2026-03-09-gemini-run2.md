**Reviewer:** gemini
**Gate:** 2
**MAD:** starret
**Date:** 2026-03-09

**Gate 2: FAILED**

**Blockers:**
1. **Docker Socket Mount:** `docker-compose.yml` mounts `/var/run/docker.sock:/var/run/docker.sock` in the `github-runner` container. REQ-starret.md explicitly states that `deploy.py` uses SSH to execute deployments on target hosts. Mounting the Docker socket is a massive security escalation, violates the principle of least privilege, and directly contradicts the SSH-based deployment model outlined in the design. Remove this volume mount.
2. **Runner Image Unpinned:** In `docker-compose.yml`, the `github-runner` image is specified as `ghcr.io/actions/actions-runner:2.332.0`. REQ-000 §1.4 strictly requires all external images to be digest-pinned (e.g., `@sha256:...`).
3. **Runner UID/GID:** The `github-runner` container definition in `docker-compose.yml` lacks a `user:` directive. REQ-000 §2.1 and §2.2 mandate that all service containers must run as a non-root user matching the registry-allocated UID/GID (2001:2001 for Starret).

**Observations:**
1. **Unused Metrics Recorders:** In `flows/metrics.py`, the `record_request` and `record_error` custom metrics functions are defined but are never invoked from `server.py` or the tool execution paths. The `/metrics` endpoint will return data, but the custom MCP tool metrics (`mcp_requests_total`, etc.) will remain unpopulated.
2. **Missing Error Handling in Git Tools:** In `flows/imperator.py`, tools like `git_push` and `gh_create_pr` parse the remote URL assuming it will exactly match `https://github.com/`. If an SSH remote or a differently structured HTTPS remote is encountered, these functions may fail to inject credentials or crash during regex parsing.

**Recommendations:**
1. **Metrics Integration:** Implement explicit calls to `record_request` and `record_error` within the `starret_chat` and `starret_github` tool handlers in `server.py` to ensure observability metrics accurately reflect tool utilization.
2. **Refactor PR Creation:** Refactor `gh_create_pr` in `flows/imperator.py` to leverage the established GitHub API infrastructure in `flows/github_ops.py`. Currently, it duplicates token loading, header construction, and raw `httpx` API calling, increasing the risk of split-brain bugs.
3. **Robust Remote Parsing:** Update the remote URL parsing logic in `imperator.py` to handle standard SSH git URLs (e.g., `git@github.com:owner/repo.git`), as agents or human users might configure the repository with SSH rather than HTTPS remotes.