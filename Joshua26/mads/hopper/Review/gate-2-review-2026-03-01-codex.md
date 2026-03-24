**Reviewer:** Codex
**Gate:** 2
**MAD:** hopper
**Date:** 2026-03-01

- **Gate 2: FAILED** — Hopper's baseline wiring is now mostly restored, but core behavioral requirements from `REQ-hopper.md` remain unimplemented or mismatched in ways that will break the intended SDLC flow at runtime.

## Blockers

1. **Imperator does not retrieve Rogers context before triage.**
   - `REQ-hopper` requires context retrieval as step 1 of `hopper_chat` processing.
   - Current Imperator graph only creates a conversation and triages the immediate user message; there is no context fetch node.
   - Files:
     - `mads/hopper/hopper-langgraph/flows/imperator.py`
     - `mads/hopper/docs/REQ-hopper.md`

2. **Core SDLC orchestration is not implemented; `develop_software`/`software_engineer` are placeholders.**
   - `build_develop_software_graph()` and `build_software_engineer_graph()` each run a single `execute_task` node that generates a brief plan via one LLM call.
   - This does not implement the required multi-step lifecycle in the delta REQ (requirements -> architecture -> implementation -> test planning -> execution loop).
   - File: `mads/hopper/hopper-langgraph/flows/agents.py`

3. **Quorum engines are implemented but not integrated into the execution path.**
   - `quorum.py` defines quorum graphs, but `server.py` dispatch path does not invoke `develop_doc`/`develop_tech_asset` quorum primitives from agent orchestration.
   - This is a direct mismatch with the architecture where primitives are central to agent execution.
   - Files:
     - `mads/hopper/hopper-langgraph/flows/quorum.py`
     - `mads/hopper/hopper-langgraph/server.py`
     - `mads/hopper/docs/REQ-hopper.md`

4. **Streaming endpoint invokes Imperator twice per request.**
   - `chat_stream()` first iterates `astream_events(...)`, then calls `_imperator_flow.ainvoke(...)` again to compute final output.
   - This can duplicate side effects (e.g., session creation, routing decisions) and produce inconsistent final behavior.
   - File: `mads/hopper/hopper-langgraph/server.py`

5. **Model alias contract in REQ is not followed in code.**
   - REQ defines alias-driven model usage (`imperator-fast`, `quorum-*`), but code hardcodes model family labels (`GPT`, `Gemini Pro`, `Sonnet`, `Grok Fast`, `GPT Codex`).
   - This creates drift and defeats the documented alias indirection pattern.
   - Files:
     - `mads/hopper/hopper-langgraph/flows/imperator.py`
     - `mads/hopper/hopper-langgraph/flows/quorum.py`
     - `mads/hopper/hopper-langgraph/flows/agents.py`
     - `mads/hopper/docs/REQ-hopper.md`

6. **REQ-000 unit testing mandate is not met for new programmatic logic.**
   - No Hopper tests are present for newly added flow logic and parsing/orchestration behavior.
   - File area: `mads/hopper/` (no `tests/` coverage for Hopper logic)

## Observations

1. **Gateway/runtime identity and wiring recovery looks correct now.**
   - `hopper` config and Dockerfiles are no longer template-bound and use Hopper UID/port/paths.
   - Files:
     - `mads/hopper/hopper/config.json`
     - `mads/hopper/hopper/Dockerfile`
     - `mads/hopper/hopper-langgraph/Dockerfile`

2. **Compose topology for networks and host-profile suppression is aligned.**
   - `hopper` is on `joshua-net` + `hopper-net`; `hopper-langgraph` is on `hopper-net` only.
   - Irina/Hymie override suppression is present.
   - Files:
     - `docker-compose.yml`
     - `docker-compose.irina.yml`
     - `docker-compose.hymie.yml`

3. **Template residue remains in langgraph package (`query_flow.py`, `simple_ops.py`).**
   - Not a direct runtime blocker, but this increases review noise and accidental coupling risk.
   - Files:
     - `mads/hopper/hopper-langgraph/flows/query_flow.py`
     - `mads/hopper/hopper-langgraph/flows/simple_ops.py`

4. **Host-affinity mechanism is mixed.**
   - Overrides correctly use profile suppression, but master compose still includes `deploy.placement.constraints`.
   - This is inconsistent with the profile-first guidance in current docs.
   - File: `docker-compose.yml`

## Recommendations

1. **Implement a true Imperator pipeline node set:**
   - `ensure_rogers_session` -> `fetch_rogers_context` -> `triage_request` -> dispatch.
   - Persist/reuse conversation IDs through state to avoid duplicate session churn.

2. **Replace placeholder agent graphs with actual orchestrators:**
   - `develop_software` should explicitly sequence REQ-defined phases.
   - `software_engineer` should implement the fix/deploy/test loop and escalation path.

3. **Integrate quorum primitives into agent execution paths immediately.**
   - `develop_doc`/`develop_tech_asset` should be real callable subgraphs from orchestrator nodes, not isolated modules.

4. **Refactor streaming flow to single-pass execution.**
   - Capture final state/result from one execution path while streaming events; do not invoke Imperator twice.

5. **Normalize inference calls to REQ aliases.**
   - Route all model selection through documented alias keys and keep actual backend targets in Sutherland registry/config only.

6. **Add targeted unit tests before next Gate 2 rerun.**
   - Priority: Imperator routing parser, PM JSON parser/safety-valve behavior, peer proxy response parsing, and stream endpoint single-pass behavior.

