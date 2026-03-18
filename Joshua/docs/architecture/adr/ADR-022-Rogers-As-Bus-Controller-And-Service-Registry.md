# ADR-022: Centralized Service Discovery via Rogers Registry

**Version:** 1.0
**Status:** Accepted
**Date:** 2025-11-30

## Context

In a distributed ecosystem of specialist MADs, a fundamental problem is service discovery: how does one MAD (e.g., `Hopper`) find another MAD that provides a specific capability (e.g., `"image_processing"`)?

Previous architectural discussions considered two models:
1.  **Decentralized Broadcast ("Lobby" Model):** MADs announce their capabilities to a public channel, and every other MAD is responsible for listening to these announcements and building its own local registry.
2.  **Conversational Discovery:** A MAD asks a general question on the bus ("Who can process images?") and waits for a capable MAD to respond.

Both of these models are inefficient, introduce state management burdens on every MAD, and are prone to data staleness. A more robust and efficient pattern is needed.

## Decision

1.  **Rogers' Dual Role:** The `Rogers` MAD will have two primary responsibilities:
    *   **Bus Manager:** Its existing role as the content-agnostic transport layer for all bus conversations.
    *   **Service Registry:** A new, authoritative role as the central service and capability registry for the entire ecosystem.

2.  **Registration on Startup:** When any MAD starts up and connects to Rogers, it **must** send a `rogers_register_tools` command. This command provides Rogers with a manifest of its public tools and the abstract capabilities they fulfill.

    *Example Registration Payload from `Bass`:*
    ```json
    {
      "tools": ["bass_analyze", "bass_transform"],
      "capabilities": ["image_processing", "computer_vision"]
    }
    ```

3.  **Discovery via Direct Query:** When a MAD needs to find a service, it will send a direct query to Rogers. Rogers will provide two query tools:
    *   **`rogers_find_capability(capability: str)`:** To find which MAD(s) provide a general capability (e.g., `'diagram_generation'`).
    *   **`rogers_find_tool(tool_name: str)`:** To find which specific MAD provides a named tool (e.g., `'viz_create_diagram'`).

4.  **Content-Agnostic Transport:** This new registry role does **not** change Rogers' primary function as a bus manager. Rogers remains entirely agnostic to the *content* of messages in conversations between other MADs. Its registry function is a separate service it provides through its own exposed tools.

## Consequences

### Positive

*   **Efficiency:** Service discovery becomes a single, fast, direct query to an in-memory registry, rather than a noisy broadcast or a slow conversational process.
*   **Authoritative Source of Truth:** The registry in Rogers is the single, definitive source for the ecosystem's capabilities. This eliminates data staleness and state inconsistencies.
*   **Simple Client Logic:** MADs do not need to implement their own registry logic. They only need to know how to ask Rogers. This adheres to the "Don't Repeat Yourself" principle.
*   **Foundation for Future Intelligence:** A centralized registry allows Rogers to evolve to provide more intelligent routing in the future (e.g., load balancing, health-aware recommendations) without changing the client-side discovery pattern.
*   **Clean Separation of Concerns:** Rogers specializes in network-level concerns: transport (the bus) and discovery (the registry). Other MADs can focus on their own domain logic.

### Negative

*   **Centralization:** Rogers becomes a more critical single point of failure. If Rogers is down, both communication and service discovery are unavailable. This is an acceptable trade-off for the V1.0 architecture, and Rogers can be made highly available in future versions.
*   **Startup Dependency:** All MADs have a hard dependency on Rogers to be able to register themselves and discover other services. (This is already implicitly true for the conversation bus).

---
