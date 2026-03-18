# ADR-023: Direct Tool Exposure and Deprecation of Unified Converse

**Version:** 1.0
**Status:** Accepted
**Date:** 2025-11-30

## Context

The V0.7 MAD Template design introduced the "Unified Converse" pattern, where each MAD exposed a single, generic `[mad_name]_converse` tool. The intention was to provide a unified interface and an internal routing mechanism ("Direct Dispatch") to handle both conversational and programmatic calls.

However, this pattern has several drawbacks:
1.  **Complexity:** It requires nesting a structured JSON-RPC call inside a string, which is clunky, inefficient, and error-prone.
2.  **Poor Discoverability:** It hides a MAD's true programmatic API. To see what tools a MAD provides, one would have to consult its documentation rather than querying a service registry.
3.  **Redundancy:** With the introduction of the "Communications Router" in `Joshua_Communicator` (ADR-021), the triage logic of the `_converse` tool is now redundant. The router already provides a clean separation between programmatic (MCP) and conversational (prose) messages at the ingress layer.

## Decision

1.  **Deprecate "Unified Converse":** The `[mad_name]_converse` tool as a universal wrapper is officially deprecated. It should be removed from all MADs as their primary interface. A `_converse` tool may still exist, but only as a specific tool for engaging the Thought Engine conversationally, not as a gateway for other tools.

2.  **Direct Tool Exposure:** All public Action Engine tools will be exposed directly as first-class citizens in the MAD's API. For example, `Horace` will directly expose `horace_file_read`, `horace_file_write`, etc.

3.  **Rely on Communications Router:** The `Joshua_Communicator`'s internal **Communications Router** (defined in ADR-021) will be the sole mechanism for routing incoming messages. It will deterministically route valid MCP tool calls to the Action Engine and all other traffic to the Thought Engine.

4.  **Rely on Rogers Registry for Discovery:** The discoverability problem is solved by `Rogers` acting as a service registry (ADR-022). A MAD can query Rogers to discover the complete, explicit API of any other MAD.

## Consequences

### Positive

*   **Simplicity and Clarity:** The public API of each MAD is now explicit and clean. A call to `horace_file_read` does exactly what it says. There is no confusing layer of indirection.
*   **Improved Discoverability:** MADs can register their full, explicit toolset with the Rogers registry, allowing for powerful and accurate automated service discovery.
*   **Efficiency:** Eliminates the overhead of parsing a JSON string nested within another JSON object. Direct tool calls are leaner and faster.
*   **Aligns with Architecture:** This decision perfectly complements the `Joshua_Communicator`'s router (ADR-021) and the `Rogers` registry (ADR-022), creating a cohesive and elegant architectural model.

### Negative

*   This requires a significant documentation effort to update all 31 MAD requirements documents to remove the `_converse` pattern and correctly list their direct tool APIs.
*   The concept of a dedicated tool for "just talking" to the Thought Engine might need to be re-introduced if a purely conversational entry point is desired, but it will no longer be the primary gateway.

---
