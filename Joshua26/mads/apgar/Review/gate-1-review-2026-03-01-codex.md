**Reviewer:** Codex
**Gate:** 1
**MAD:** apgar
**Date:** 2026-03-01

- **Gate 1: FAILED** — Design conflicts with REQ-000 network boundary rules, UID model, and storage policy. Several required schema/registry details are missing or inconsistent.
- **Blockers:**
  - Backing services (`apgar-prometheus`, `apgar-loki`, `apgar-grafana`) are specified on `joshua-net`, which violates the “gateway is the sole bidirectional network boundary” rule (REQ-000 §7.4.1, HLD-MAD-container-composition). These services must be on `apgar-net` only, or a formal exception must be approved and recorded. This also implies Grafana UI access should be proxied through the gateway (or another approved boundary) instead of direct exposure on `joshua-net`.
  - The REQ lists distinct UIDs for apgar backing services (2034/2035/2036). MAD-group containers must share the gateway UID (REQ-000 compliance checklist 6.3; HLD-MAD-container-composition). Align all apgar containers to UID 2032 or document a formal exception.
  - Data storage paths are specified under `/storage/databases/apgar/...` for Prometheus/Loki/Grafana. REQ-000 §3.4/§3.7 require database data to live in `/workspace/[mad]/databases/...` with backups in `/storage/...`. Update storage strategy or request an exception with mitigation.
  - Tool schema definitions are incomplete. The delta REQ only shows input examples for tools, but does not define full JSON schemas (input/output) or error cases required by the design guide and needed for `config.json` validation (REQ-000 §7.10 + design guide Phase C). Provide full schemas and error responses for each tool before implementation.
  - Registry exposure for backing services is inconsistent with the “gateway-only MCP” pattern. `registry.yml` lists ports for apgar-prometheus/loki/grafana, but REQ-000 compliance checklist 6.3 requires only the gateway to have MCP ports/endpoints. Either remove ports and avoid direct exposure, or formally document and approve an exception.
- **Observations:**
  - The plan lists the TE tool as `apgar_diagnose`, while the REQ defines `apgar_diagnose_issue`. Align tool names in the plan and REQ to avoid tool mismatch during implementation.
  - “State 2” is referenced, but the ecosystem HLD only defines State 0 and State 1. If “State 2” is a new architecture phase, it should be defined in system-level docs or explicitly mapped to State 1 composition to avoid ambiguity.
  - Host log shipping is left undecided (“Fluent Bit or Promtail”). This affects deployment steps, credentials, and network flow. The delta REQ should choose one and specify its configuration, ports, and host-level install steps so implementation and deployment are unambiguous.
  - Health strategy omits how LLM/TE dependencies are handled (e.g., if TE relies on Sutherland or external APIs). If any external dependency is used, graceful-degradation behavior and health reporting should be defined.
- **Recommendations:**
  - Use gateway proxying for all external reachability: expose Grafana UI via the apgar gateway (or a sanctioned UI proxy) to keep backing services off `joshua-net`.
  - Prefer push-based metrics/log ingestion (host agents pushing to the gateway or a dedicated ingest endpoint) to avoid placing Prometheus/Loki on `joshua-net`. This preserves the private-network requirement while still collecting telemetry.
  - Pin exact container image versions for Prometheus, Loki, and Grafana in the design to satisfy REQ-000 §1.4/§1.7 during implementation.
  - Add explicit credential paths under `/storage/credentials/apgar/` for Grafana admin, Loki/Prometheus auth (if any), and log shipper tokens. Document how credentials are loaded and rotated.
