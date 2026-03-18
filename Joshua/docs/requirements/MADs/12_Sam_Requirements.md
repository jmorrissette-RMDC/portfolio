# Sam Requirements

- **Role**: External MCP Gateway
- **Home**: `mads/sam/`

---

## 1. Overview

- **Purpose**: Sam is the sole **external programmatic gateway** to the Joshua ecosystem. It exposes a standard MCP server to the outside world and acts as a sophisticated protocol bridge, translating external requests into the appropriate internal communication protocol for the current ecosystem version.

- **V0.7 Scope Definition**: In the V0 architecture, Sam acts as a direct **MCP Gateway**. It exposes a single WebSocket endpoint to the external world and forwards valid MCP tool calls to the correct internal V0 MADs via their direct WebSocket connections (e.g., `ws://horace:8000`). It is a foundational piece of infrastructure, built manually as part of the initial bootstrap.

- **V1.0 Scope Definition (Kafka Bridge)**: In the V1+ architecture, Sam evolves into a **synchronous-to-asynchronous bridge**. It continues to expose a standard MCP server to external clients but translates their synchronous requests into asynchronous conversations on the internal Kafka-based bus, managing the request-reply workflow with correlation IDs.

---

## 2. Tool Exposure Model

Sam is a unique gateway MAD. It **does not expose any public tools of its own**. Instead, its MCP server acts as a dynamic proxy to the entire Joshua ecosystem.

External clients make tool calls as if they were talking to a single entity (e.g., `horace_file_read`, `fiedler_send`). Sam's Thought Engine intercepts these calls, discovers which MAD provides the requested tool, and then initiates the internal communication to fulfill the request.

Any non-MCP communication sent to Sam is routed to its Thought Engine, which can provide help text or diagnostic information.

---

## 3. Core Functionality: The Sync-to-Async Bridge

Sam's primary architectural pattern is the synchronous-to-asynchronous bridge, which is critical for interacting with external clients that expect a blocking request-reply pattern.

### 3.1 Request-Reply Workflow

1.  **Receive MCP Request:** Sam's MCP server receives a standard tool call from an external client.
2.  **Discover Provider:** Sam's Thought Engine makes a `rogers_find_tool` request to the Rogers service registry to identify which MAD provides the requested tool (e.g., `horace_file_read` is provided by `horace`).
3.  **Initiate Bus Conversation:** Sam uses the `Joshua_Communicator` library to send a request message to the target MAD (`horace`) over the bus. This is an asynchronous operation that includes a unique `correlation_id`.
4.  **Await Response:** Sam's logic then blocks and waits for a response message on the bus that contains the matching `correlation_id`. This is handled by a temporary, dedicated consumer with a configurable timeout.
5.  **Translate and Respond:** Once the response from the target MAD is received, Sam translates it back into a standard MCP response and sends it to the original external client, completing the synchronous call.

This workflow makes the asynchronous, multi-participant nature of the internal ecosystem completely transparent to the external client.

---

## 4. Future Evolution (Post-V0)

Sam's role as the external gateway evolves to become a sophisticated bridge between synchronous external clients and the asynchronous internal ecosystem.

*   **Phase 1 (Foundation / V0.7):** Sam is introduced as the foundational **MCP Gateway**, replacing the generic "Relay" concept. It is built manually to the V0.7 standard, providing a stable, direct WebSocket gateway for external programmatic clients to interact with the V0 MADs.

*   **Phase 2 (Conversation / V1.0):** Sam is upgraded to act as a **synchronous-to-asynchronous bridge** for the pure Kafka architecture. It implements the request-reply pattern using correlation IDs, allowing external MCP clients to make synchronous calls while the internal ecosystem remains fully event-driven and asynchronous.

*   **Phase 3 (Cognition / V5.0):** Sam receives the full PCP stack (DTR, LPPM, CET, CRS), enabling intelligent routing, caching of common requests, and learned optimization of the synchronous-to-asynchronous translation layer. DTR provides microsecond-level fast-path routing for frequent requests.

*   **Phase 4 (eMADs / V6.0):** Sam becomes eMAD-aware, capable of routing external requests to dynamically provisioned eMAD teams and managing correlation IDs for ephemeral participants.

*   **Phase 5 (Autonomy / V7.0):** Sam integrates with Joshua MAD's strategic directives, enforcing top-down access policies and constitutional constraints on external client interactions.

---
