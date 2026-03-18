# MAD Ingress Architecture: The Communications Router

**Version:** 1.0
**Status:** Adopted
**Date:** 2025-11-30
**Related ADRs:** ADR-021, ADR-023

## 1. Overview

This document defines the standard ingress architecture for all MADs in the Joshua ecosystem. The architecture is built around a unified communication library, `Joshua_Communicator`, which contains a critical component: the **Communications Router**. This model ensures a clean separation of concerns, providing a single, intelligent entry point for every MAD.

## 2. The `Joshua_Communicator` Library

The `Joshua_Communicator` is the mandatory, version-agnostic library responsible for all MAD network I/O. It contains two key internal components:
1.  **The Network Transport:** The low-level component handling the connection (e.g., WebSockets in V0, Kafka in V1).
2.  **The Communications Router:** The high-level component that performs initial message triage.

## 3. The Communications Router: Triage at the Edge

The Communications Router is the most crucial part of the ingress architecture. It is **not** part of the Thought Engine. It lives within the `Joshua_Communicator` library and acts as the MAD's front door, applying a simple, fast, and deterministic rule to every incoming message.

### 3.1 Routing Logic

1.  A message is received by the Network Transport.
2.  The transport passes the raw message to the **Communications Router**.
3.  The router inspects the message and asks one question: **"Is this a well-formed MCP tool call for a tool publicly exposed by the local Action Engine?"**
4.  Based on the answer, it routes the message:
    *   **If YES:** The message is passed directly to the **Action Engine (AE)**. The AE processes the request and sends its response directly back to the Network Transport to be returned to the caller. The Thought Engine is never engaged. This is the **"fast path"** for programmatic tool calls.
    *   **If NO:** The message is passed to the **Thought Engine (TE)** as the default handler. This includes conversational prose, malformed MCP calls, or calls to non-existent tools. The TE can then use its intelligence to process the request, which may involve calling its own AE's tools internally.

### 3.2 Architectural Diagram

This diagram illustrates the definitive flow of information for incoming requests.

```mermaid
graph TD
    subgraph "External World"
        direction LR
        External_Client[External Client / Another MAD]
    end

    subgraph "MAD Boundary"
        direction LR

        subgraph "Joshua_Communicator (Library)"
            Net_Transport[Network Transport<br>(WebSocket/Kafka)]
            Comm_Router[Communications Router]
            Net_Transport -- "Incoming External Message" --> Comm_Router
        end

        subgraph "MAD Core Components"
            TE[Thought Engine]
            AE[Action Engine<br>(MCP Server & Tools)]
        end

        Comm_Router -- "External MCP Call? -> YES (Fast Path)" --> AE
        Comm_Router -- "External MCP Call? -> NO (Default Path)" --> TE

        TE -- "Internal MCP Call (In-Memory)<br>to AE's Dispatch" --> AE

        AE -- "External Response" --> Net_Transport
        TE -- "External Response (via Communicator client)" --> Comm_Router

    end

    External_Client -- "Request (MCP or Prose)" --> Net_Transport
    Net_Transport -- "Response" --> External_Client
```

## 4. Key Principles and Consequences

*   **Protocol Consistency & Decoupling:** The Thought Engine (TE) and Action Engine (AE) maintain a clear operational contract via the MCP standard. While the TE may have deep awareness of the AE's internal workings, all execution of AE tools by the TE occurs via direct, in-memory MCP calls to the AE's server dispatch, ensuring protocol consistency and auditability.
*   **Architectural Purity:** The roles are perfectly defined.
    *   `Joshua_Communicator`: Manages I/O and routing.
    *   `Action Engine`: A deterministic server for executing tools.
    *   `Thought Engine`: An intelligent client for reasoning and handling exceptions.
*   **Efficiency:** The "fast path" allows programmatic tool calls to be executed with minimal overhead, bypassing the expensive LLM reasoning cycle of the Thought Engine.
*   **Intelligent Error Handling:** By making the TE the default handler for any message the AE cannot process, the MAD gains the ability to intelligently interpret and even repair malformed requests.
*   **Simplified API:** This model allows MADs to expose their tools directly and cleanly, as documented in ADR-023, without the need for a "Unified Converse" wrapper. The Communications Router provides the triage that the wrapper was designed to handle.
