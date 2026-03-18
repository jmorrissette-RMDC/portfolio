# `Joshua_Communicator` Library Specification

**Version:** 0.7
**Status:** Adopted (for V0 Ecosystem)
**Date:** 2025-11-30

## 1. Overview

-   **Purpose:** The `Joshua_Communicator` is the single, unified, and mandatory library for all MAD network I/O and routing. It provides a stable, version-agnostic API for MADs to communicate with each other and the outside world.
-   **Core Components:**
    1.  **Communications Router:** The MAD's single entry point for all incoming messages. It performs initial triage, routing requests to either the Action Engine or the Thought Engine.
    2.  **Network Transport:** The underlying implementation for sending and receiving messages. The implementation is swappable based on the ecosystem version.
    3.  **Integrated Logger:** A built-in logging interface that directs logs to the appropriate transport (stdout for V0, Kafka for V1).

## 2. The Communications Router (Ingress Triage)

The Communications Router is the most critical component of this library. It is **not** part of the Thought Engine. It is a simple, fast, deterministic router that acts as the MAD's front door.

### 2.1 Routing Logic (for External Ingress)

For every **external message** received by the Network Transport, the Communications Router applies the following rule:

1.  **Inspect the message:** "Is this a well-formed MCP tool call for a tool publicly exposed by the local Action Engine's MCP server?"
2.  **Triage:**
    *   **If YES (Fast Path):** The message is passed directly to the **Action Engine's MCP server** for execution. The Thought Engine is never engaged for this external request.
    *   **If NO (Default Path):** The message (whether it is conversational prose, a malformed MCP call, a call to a non-existent tool, or an error) is passed to the **Thought Engine** as the default handler.

When the Thought Engine needs to execute its own local Action Engine tools, it does so via a **direct, in-memory MCP call** to the Action Engine's dispatch function, bypassing this ingress router.

### 2.2 Architectural Implications

*   This routing logic lives **entirely within the `Joshua_Communicator` library**, not in the MAD's application code.
*   It enables the perfect decoupling of the Action Engine (a simple MCP server) and the Thought Engine (an intelligent MCP client).
*   It provides a highly efficient "fast path" for programmatic tool calls, bypassing the expensive Thought Engine entirely.

## 3. The Network Transport

The `Joshua_Communicator` library abstracts the underlying network transport via a **version-agnostic API**, allowing MAD code to remain stable as the ecosystem evolves.

### 3.1 V0 Implementation (Direct WebSocket)

*   **Transport:** This version of the library implements a transport based on the `websockets` library.
*   **Behavior:** It enables direct, point-to-point MCP connections between MADs.
*   **Logging:** The integrated logger writes structured JSON to `stdout`.

### 3.2 Future V1+ Evolution (Kafka Bus)

*   **Transport:** A future version of this library will replace the WebSocket transport with an implementation based on `confluent-kafka-python`.
*   **Behavior:** It will act as a producer and consumer on the Rogers/Kafka conversation bus.
*   **Logging:** The integrated logger will be updated to publish log messages to a dedicated Kafka topic.

## 4. API Specification

The public API of the `Joshua_Communicator` is designed to be stable across the V0 and V1+ implementations.

### 4.1 `Communicator` Class

This is the main class instantiated by each MAD.

**Constructor:**
`__init__(self, mad_name: str, action_engine_tools: dict, thought_engine_handler: callable, config: dict)`

*   `mad_name`: The name of the MAD (e.g., "horace").
*   `action_engine_tools`: A dictionary mapping tool names to their handler functions (e.g., `{'horace_file_read': handle_read}`). This is used by the Communications Router.
*   `thought_engine_handler`: The async function to call for all non-MCP traffic.
*   `config`: A dictionary containing version-specific configuration.

**V0 Config Example:**
```python
{
    "version": "v0",
    "port": 8001,
    "relay_url": "ws://mcp-relay:8000"
}
```

**V1 Config Example:**
```python
{
    "version": "v1",
    "rogers_url": "ws://rogers:8000", # For registration
    "kafka_brokers": "kafka:8000"
}
```

**Core Methods:**

*   `async start()`: Starts the network listener (WebSocket server in V0, Kafka consumer in V1).
*   `async stop()`: Gracefully shuts down the network connections.
*   `async send_message(destination: str, message: dict)`: Sends a message to another MAD **(for external communication only)**. In V0, `destination` is a URL. In V1, it's a conversation/topic ID.
*   `log`: An instance of the integrated logger (`.info()`, `.error()`, etc.).

### 4.2 Example Usage (within a MAD's `server.py`)

```python
import asyncio
from joshua_communicator import Communicator

# --- Define Handlers ---

# Action Engine tool handlers
async def handle_file_read(path: str):
    # ... logic to read a file
    return {"status": "success", "content": "..."}

ACTION_ENGINE_TOOLS = {
    "horace_file_read": handle_file_read
}

# Thought Engine default handler
async def thought_engine_entrypoint(message: dict):
    # ... logic to process conversational prose or errors
    # This would typically call the Imperator.
    return {"response": "I have processed your request conversationally."}


# --- Main Application ---
async def main():
    config = get_config_from_env() # Loads V0 or V1 config

    communicator = Communicator(
        mad_name="horace",
        action_engine_tools=ACTION_ENGINE_TOOLS,
        thought_engine_handler=thought_engine_entrypoint,
        config=config
    )

    try:
        await communicator.start()
        await communicator.log.info("Horace MAD is online and connected.")
        # Keep the server running
        await asyncio.Event().wait()
    except Exception as e:
        await communicator.log.error(f"Horace MAD failed to start: {e}")
    finally:
        await communicator.stop()

if __name__ == "__main__":
    asyncio.run(main())
```

This architecture ensures that the MAD's core application logic (`handle_file_read`, `thought_engine_entrypoint`) is completely independent of the underlying network transport, fulfilling the goal of a seamless V0-to-V1 migration path.