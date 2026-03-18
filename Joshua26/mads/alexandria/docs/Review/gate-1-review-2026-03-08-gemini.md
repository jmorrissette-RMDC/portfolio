**Reviewer:** Gemini
**Gate:** 1
**MAD:** alexandria
**Date:** 2026-03-08

- **Gate 1: FAILED** — The architecture is sound and aligns well with the State 2 pattern, but a blocker regarding health check aggregation must be addressed before implementation.

- **Blockers:**
  - **Health Aggregation Implementation:** In State 1, the Node.js gateway utilized `health-aggregator-lib` to automatically poll dependencies and return an aggregated JSON status. In State 2, Nginx acts as the gateway and proxies `/health` directly to `alexandria-langgraph:8000/health`. The design (REQ-alexandria) must be updated to explicitly state that the `alexandria-langgraph` container is now responsible for implementing the health aggregation logic (pinging delphi, pergamum, and nineveh) to satisfy REQ-000 §5.9.

- **Observations:**
  - **Verdaccio (Pergamum) Config and Permissions:** REQ-019 specifies placing `config.yaml` in the workspace directory and supplying it to the official Verdaccio image (which runs as UID 10001). Verify that the directory and config file have appropriate permissions for UID 10001 to read them. Also, ensure the method of passing this config to the official image is sound (e.g., via a command override or custom entrypoint), as official images might not look in `/workspace` by default.
  - **Nineveh Config Mount:** REQ-022 shows a bind mount for `config.yml` directly from the source tree (`./mads/alexandria/alexandria-nineveh/config.yml`). While common, this technically deviates from the strict Two-Volume Policy (REQ-000 §3.1). Consider creating a minimal custom Dockerfile `FROM registry:2` that `COPY`s the config file in, which eliminates the extra volume mount and keeps the compose file cleaner.
  - **Devpi (Delphi) Initialization:** REQ-alexandria notes Devpi requires initialization (`--init`) on the first run. The Docker entrypoint script for the custom `alexandria-delphi` container should be designed to automatically detect if initialization is needed (e.g., checking if the index exists) and run it before starting the server to prevent crash-loops on fresh deployments.
  - **Umask Configuration:** REQ-000 §2.4 requires `umask 000` to be set. Ensure this is explicitly handled in the custom startup scripts for `alexandria-langgraph` and `alexandria-delphi`.
  - **Prometheus Exporters:** REQ-000 §4.11 states backing services should use exporter sidecars if they are to be monitored. Alexandria does not include sidecars for Devpi, Verdaccio, or Nineveh. If you intend to monitor these caches in Prometheus, exporter sidecars are required. If not, this is acceptable but should be noted.

- **Recommendations:**
  - **Align Python Versions:** REQ-018 suggests `python:3.11-slim` as the base image option, while REQ-alexandria specifies `python:3.12-slim`. Standardize the documentation to use 3.12-slim for consistency across the MAD.
  - **Consolidate Naming:** REQ-019 refers to the workspace directory as both `/workspace/alexandria-npm` and `/workspace/pergamum`. Standardize on `/workspace/pergamum` to match the container name `alexandria-pergamum`.
  - **Automated Registry Cleanup:** REQ-022 mentions manual garbage collection and cleanup for Nineveh. Since Alexandria possesses programmatic flows and an Imperator, consider adding a scheduled graph flow in `alexandria-langgraph` to handle Docker registry cleanup automatically.