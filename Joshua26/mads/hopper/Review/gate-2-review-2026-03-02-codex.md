**Reviewer:** Codex
**Gate:** 2
**MAD:** hopper
**Date:** 2026-03-02

- **Gate 2: FAILED** — Hopper has substantial implementation progress in `hopper-langgraph`, but the built containers still point to template artifacts and the current gateway/runtime wiring cannot satisfy `REQ-hopper.md` at deploy time.

## Blockers

1. **Gateway config is still template config, not Hopper config (hard runtime mismatch).**
   - `mads/hopper/hopper/config.json:2-53` still defines `template` identity, port `6340`, template tools (`template_query_db`, `template_select_table`, `template_call_service`), and `template-postgres` dependency.
   - `REQ-hopper` requires `hopper_chat` on port `9225` and Rogers/Sutherland dependencies (`mads/hopper/docs/REQ-hopper.md:399-460`).
   - `peers` is empty in `mads/hopper/hopper/config.json:62`, but Hopper code uses peer-proxy calls to Rogers/Sutherland; this will fail immediately for `/peer/*` calls (REQ-000 §7.4.1 requires peer declarations).

2. **Gateway Dockerfile builds and runs template files, not Hopper files.**
   - `mads/hopper/hopper/Dockerfile:9-10` sets `USER_NAME=template`, `USER_UID=2031` instead of Hopper UID `2034` from `registry.yml:200-204`.
   - `mads/hopper/hopper/Dockerfile:52-62` copies `mads/_template/template/...` into image.
   - `mads/hopper/hopper/Dockerfile:64-67` exposes and healthchecks port `6340` instead of Hopper’s `9225`.
   - Result: deployed `hopper` container image will not serve Hopper tooling.

3. **LangGraph Dockerfile also builds template backend, not Hopper backend.**
   - `mads/hopper/hopper-langgraph/Dockerfile:8-9` uses template identity/UID (`template-langgraph`, `2031`) rather than Hopper group UID `2034`.
   - `mads/hopper/hopper-langgraph/Dockerfile:20-27` copies `mads/_template/template-langgraph/...` (packages, requirements, server, flows, start script) instead of `mads/hopper/hopper-langgraph/...`.
   - Result: built container does not contain the implemented Hopper Imperator/Quorum code.

4. **`/chat` endpoint will error at runtime due to missing import.**
   - `mads/hopper/hopper-langgraph/server.py:104` returns `Response(...)`, but `Response` is not imported (`from quart import Quart, request, jsonify` at line 11).
   - This is a direct runtime failure path for the primary tool endpoint.

5. **Imperator flow does not implement required Hopper orchestration behavior.**
   - Current graph in `mads/hopper/hopper-langgraph/flows/imperator.py:78-87` ends after triage; it does not dispatch into `develop_software` / `software_engineer` execution graphs.
   - `REQ-hopper` explicitly requires dispatch to those flows and shared Rogers context pattern (`mads/hopper/docs/REQ-hopper.md:47, 92-97, 171-210`).
   - There is `conv_create_conversation` call, but no `conv_retrieve_context` path despite REQ language requiring context retrieval behavior.

6. **Model alias usage in code diverges from alias contract in REQ.**
   - Code calls raw model names (`"GPT"`, `"Gemini Pro"`, `"Sonnet"`, `"Grok Fast"`, `"GPT Codex"`) in `imperator.py`, `quorum.py`, `agents.py`.
   - `REQ-hopper` defines an alias roster (`imperator-fast`, `imperator-strategy`, `quorum-*`) and states model access should be alias-driven via Sutherland (`mads/hopper/docs/REQ-hopper.md:370-384`).
   - This mismatch creates configuration drift risk and can break inference routing when aliases change.

7. **Required test coverage for new programmatic logic is missing.**
   - New LangGraph/agent logic is introduced under `mads/hopper/hopper-langgraph/flows/`, but no Hopper tests exist under `mads/hopper/tests/`.
   - REQ-000 §1.10 requires corresponding unit tests for new programmatic logic.

## Observations

1. **Compose and registry integration is mostly aligned.**
   - Hopper services are present in `docker-compose.yml` (`hopper`, `hopper-langgraph`, `hopper-net`) and host overrides suppress non-M5 hosts (`docker-compose.irina.yml:95-99`, `docker-compose.hymie.yml:75-79`).
   - `registry.yml` has Hopper entry with UID `2034`, port `9225`, host `m5`.

2. **Network topology shape is correct at compose level.**
   - Gateway is on `joshua-net` + `hopper-net`; langgraph is on `hopper-net` only (`docker-compose.yml:1111-1144`), matching REQ-000 §7.4.1 architecture.

3. **Template residue is still extensive in Hopper codebase.**
   - Template-only flows (`query_flow.py`, `simple_ops.py`) and template references remain under Hopper langgraph.
   - This increases risk of accidental route/tool leakage and maintenance confusion.

4. **Host affinity uses both mechanisms.**
   - Profiles are correctly used in override files, but Hopper services also include Swarm-style `deploy.placement.constraints` in `docker-compose.yml`.
   - REQ-000 §7.6 prefers profile-based host affinity over Swarm placement constraints.

## Recommendations

1. **Re-baseline Hopper containers from template pattern (like Hamilton) and then re-apply deltas.**
   - `mads/hamilton/hamilton/Dockerfile` shows the expected finalized pattern: same template structure, but all paths/UID/ports replaced consistently.
   - For Hopper, update all `_template` COPY paths and identity/port values to Hopper equivalents before additional logic changes.

2. **Make `config.json` the single source of truth first.**
   - Implement only `hopper_chat` plus correct dependencies and `peers` (`rogers`, `sutherland`) in `mads/hopper/hopper/config.json`, then validate gateway startup and `/health`.

3. **Fix chat endpoint runtime path immediately.**
   - Add missing `Response` import and run syntax/lint checks (and lightweight endpoint-level test) before further feature work.

4. **Close the REQ-to-code gap for Imperator orchestration.**
   - Implement explicit handoff from triage → `develop_software` / `software_engineer` graphs.
   - Add Rogers context retrieval node (not just conversation creation) to satisfy the shared-agent pattern in the REQ.

5. **Normalize to alias-driven Sutherland calls.**
   - Replace raw model family strings with the alias names specified in `REQ-hopper`.
   - This keeps Hopper resilient to model backend swaps and aligns with the documented architecture contract.

6. **Add targeted Hopper unit tests before Gate 2 re-run.**
   - Prioritize: peer proxy envelope parsing, triage routing parser robustness, PM consensus parser/safety-valve behavior, and `/chat` SSE event emission contract.
