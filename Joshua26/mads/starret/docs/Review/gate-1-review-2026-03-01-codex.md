**Reviewer:** Codex
**Gate:** 1
**MAD:** starret
**Date:** 2026-03-03

- **Gate 1: FAILED** - Design has REQ-000 conflicts that must be resolved before implementation.
- **Blockers:**
  - GitHub token storage conflicts with REQ-000 credential rules: REQ-starret §6 states the token is stored in an environment variable, but REQ-000 §3.5/§3.6 require credentials to be loaded from `/storage/credentials/...` (no secrets in env vars). Update the design to load the token from `/storage/credentials/starret/` or request an explicit exception with mitigation.
  - Network boundary violation for backing services: REQ-starret §5 says the `github-runner` is on `starret-net` plus `joshua-net` for access, but REQ-000 §7.4.1 and HLD-MAD-container-composition require backing services to be on the private `[mad]-net` only (gateway is the sole network boundary). Remove `joshua-net` from the runner or document a formal exception.
  - Git safety mechanisms not specified: REQ-000 §7.7 mandates backup branch creation, dry-run, rollback capability, and user confirmation for destructive git operations. REQ-starret describes branch protection rules but does not state these required safety mechanisms for `starret_chat`. Add them explicitly to the design.
- **Observations:**
  - REQ-starret is internally inconsistent about runner exposure: §4 says the runner is not exposed on `joshua-net`, while §5 says it is connected to `joshua-net`. Resolve this contradiction in the delta REQ.
  - Conversation data integration is not specified. `starret_chat` is a conversational tool; if Starret produces conversation data, REQ-000 §7.8 requires direct Rogers integration or the watcher file flow. Clarify whether Starret emits conversation data and how it complies.
  - Degraded-mode behavior is implied but not specified for GitHub outages or runner unavailability. REQ-000 §7.1 expects explicit degraded behavior; add a brief design note describing responses and health status when GitHub or the runner is down.
- **Recommendations:**
  - Add explicit output schemas and error envelope for `starret_chat` (how clarifying questions, refusals, and failures are returned) to tighten MCP contract testing.
  - Define a repository allowlist (or fixed repo default) and path validation rules to reduce the risk of unsafe filesystem operations during git actions.
  - Document the internal dependency map (gateway -> langgraph -> runner/GitHub) with clear hard vs soft dependencies to align with REQ-000 §7.2.
