**Reviewer:** gemini
**Gate:** 1
**MAD:** alexandria
**Date:** 2026-03-08

- **Gate 1: FAILED** — Blocker issues found related to Nginx SSE configuration, configuration file management, and custom container justification.

### Blockers

1. **Nginx SSE Proxy Configuration (Network Boundary)**
   The design snippet for the Nginx gateway configuration lacks the required directives for Server-Sent Events (SSE). MCP relies on HTTP/SSE for the `GET /mcp` streaming endpoint. If Nginx is configured as a standard reverse proxy without SSE optimizations, it will buffer the stream, causing the MCP connection to hang or fail.
   *Fix:* You must add `proxy_buffering off;`, `proxy_http_version 1.1;`, `proxy_set_header Connection '';`, and an extended `proxy_read_timeout` to the `/mcp` location block in the Nginx configuration.

2. **Configuration File Locations for Verdaccio and Registry (REQ-000 §3.4 & §3.5)**
   The REQ states that Verdaccio and Registry config files "must not live in the repository. They belong in the workspace... The deployment step creates these files in workspace before the containers start." This violates REQ-000 storage principles. 
   *Fix:* If these files contain secrets, they **must** reside in `/storage/credentials/alexandria/`. If they do not contain secrets, they should be committed to the repository and mounted directly, or copied into the container during build. The `workspace` volume is for local, runtime-generated data (like database files or caches), not for static configuration that requires manual, out-of-band creation before `docker-compose up` can succeed.

3. **Custom Devpi Container Justification (HLD State 2 Principle 1)**
   HLD State 2 explicitly mandates "OTS Infrastructure," stating that "The only custom-built container is `[mad]-langgraph`" and that "Building a custom container is a rare, explicitly justified decision." The REQ defines `alexandria-devpi` as a custom `python:3.12-slim` image but fails to justify this departure from the OTS principle.
   *Fix:* Either switch to an existing Off-The-Shelf devpi image, or explicitly document the justification for the custom image (e.g., lack of an official supported image) and potentially register it as an exception.

### Observations

1. **The Bootstrap Problem & Offline Builds**
   The REQ correctly identifies that Alexandria cannot use itself to build its own initial containers and suggests running `pip download` on `irina`. To maintain the reproducible offline build requirement (REQ-000 §1.1), ensure that these pre-downloaded wheels are committed to the `packages/` directories within the repository before deployment. This ensures that the build is completely offline and reproducible on any host without requiring manual pre-steps.

2. **Host-Bound Ports on Nginx (EX-ALEXANDRIA-001)**
   The use of Nginx to expose host-bound ports (3141, 4873, 5000) for standard HTTP/cache traffic while proxying `9229` to `joshua-net` for MCP is an elegant and correct implementation of the State 2 bidirectional gateway pattern. The registration of EX-ALEXANDRIA-001 is appropriate.

3. **Aggregated Health Checks in State 2**
   Proxying `/health` from Nginx to `alexandria-langgraph:8000/health` so that LangGraph can perform the active dependency checks (Devpi, Verdaccio, Registry) is the correct adaptation of REQ-000 §5.9 for the State 2 architecture.

### Recommendations

1. **Expose Cache Stats as Prometheus Metrics**
   The REQ defines `metrics_get` to expose standard MCP metrics. Since Alexandria is the ecosystem's cache proxy, it would be highly valuable to have the `metrics_get` StateGraph also query the backing caches and expose `pypi_package_count`, `npm_package_count`, and `registry_storage_bytes` as custom Prometheus metrics. This aligns with the "Built-in Observability" principle of State 2.

2. **Verdaccio Statelessness**
   Ensure Verdaccio's configuration is strictly stateless. By default, Verdaccio might attempt to write to its configuration file (e.g., when users authenticate or update settings). If you mount the config as read-only or commit it to the repo, you must ensure Verdaccio is configured to not mutate it, or handle it correctly.

3. **Automated Cleanup for Registry**
   Consider defining an Imperator flow or a cron-triggered node within `alexandria-langgraph` to periodically run Docker Registry garbage collection, as layers from deleted tags are not automatically removed from disk in Registry 2.0.