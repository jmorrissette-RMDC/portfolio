**Reviewer:** Gemini
**Gate:** 1
**MAD:** kaiser
**Date:** 2026-03-11

# Gate 1 Review: kaiser (Post-Design)

## Status: PASSED (with Observations and Recommendations)

Kaiser is an ambitious and well-architected addition to the Joshua26 ecosystem, representing the first "State 3" MAD. The design has been significantly matured following the initial Gate 1 run, addressing previous concerns regarding the State 3 definition, the inclusion of an Imperator, and the functional role of the web framework. The transition to a configuration-driven gateway with all logic (including metrics and dispatch) residing in LangGraph is correctly specified.

---

## Blockers

*None identified.* The design is compliant with REQ-000 and the State 2/3 architectural patterns.

---

## Observations

### 1. State 3 Architectural Extension
The definition of State 3 in `REQ-kaiser.md` (separating stable infrastructure from dynamic intelligence) is a powerful extension to the ecosystem. It successfully addresses the "agent-building-agents" research premise by allowing the deployment of new capabilities (eMADs) without infrastructure changes. The update to `HLD-MAD-container-composition.md` to formalize this state is noted and approved.

### 2. EX-KAISER-001: Runtime pip install
The exception for runtime package installation from Alexandria is well-justified. Since Alexandria is an internal service on the same physical infrastructure (Irina), this satisfies the "offline-first" requirement of REQ-000 §1 while enabling the core functionality of a State 3 MAD. The networking solution (nginx PyPI proxy) is an elegant way to maintain the private network boundary for the LangGraph container.

### 3. Concurrency Model (Asyncio vs. Redis)
The decision to use `asyncio` for Phase 1 concurrency instead of a Redis-backed queue is accepted. Given that eMAD workloads are primarily I/O-bound (Sutherland/Rogers calls), the overhead of a task queue is not strictly necessary for single-host execution on M5. However, see Recommendation #3 regarding long-running tasks.

### 4. Metrics Implementation
The design correctly identifies the requirement for metrics to be produced via a LangGraph StateGraph (`REQ-kaiser.md` §3.8, §9.4), adhering to the mandate in `docs/guides/mad-prometheus-metrics-guide.md`. This ensures that even observability logic is "in the graph."

---

## Recommendations

### 1. eMAD "Host Contract" Enforcement
The host contract in `REQ-kaiser.md` §6.5 defines the interface for eMAD libraries.
*   **Recommendation:** During implementation, ensure that Kaiser performs a "dry run" or validation check on the `build_graph` output when an eMAD is registered or first invoked. If the returned object is not a compiled `StateGraph` or if it lacks the required input/output schema, Kaiser should report a structured error rather than crashing the dispatch node.

### 2. Version Pinning for eMADs
The `kaiser_install_package` tool takes an optional `version` parameter.
*   **Recommendation:** While the registry stores `installed_version`, it is recommended that the `emad_instances` table also optionally stores a `required_version`. This would prevent a "v1" instance from accidentally running against a "v2" package if multiple versions are allowed to coexist in the environment (though currently, pip installs to a single environment). At a minimum, `kaiser_list_emads` should clearly show which version of the package is currently "backing" the instance.

### 3. Timeout Management
`REQ-kaiser.md` §6.1 mentions a 300s timeout for eMAD executions.
*   **Recommendation:** Since Kaiser uses Quart (async), ensure that the HTTP timeout is coordinated with the LangGraph `ainvoke` timeout. If an eMAD hangs, Kaiser should have a deterministic "kill" mechanism to prevent leaking asyncio tasks or hanging the dispatch node. Consider using `asyncio.wait_for` with the specified timeout.

### 4. Testing Strategy for the "Dispatch" Node
The dispatching node in `kaiser_chat` is a critical failure point.
*   **Recommendation:** Include unit tests that mock the `importlib` and `entry_points` layer to verify that Kaiser correctly handles:
    - Missing packages.
    - Malformed eMAD libraries (missing `build_graph`).
    - eMAD graphs that raise unhandled exceptions.

### 5. Permission Verification
Confirm that the `kaiser-postgres` data directory on M5 follows the `REQ-000 §2.6` requirement for `750/640` permissions, especially since it will store potentially sensitive eMAD parameter sets.

---

**End of Review**
