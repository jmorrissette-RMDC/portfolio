# Grace Requirements

- **Role**: Human Interface
- **Version**: V0.10
- **Home**: `mads/grace/`

---

## 1. Overview

-   **Purpose**: Grace provides the web-based user interface for humans to participate in Joshua conversations.
-   **V0.10 Scope Definition**: Provide a functional chat interface that can connect to the `Joshua_Communicator`, display conversations in real-time, and allow users to send messages to other MADs.

---

## 2. Tool Exposure Model

Grace is a unique MAD that **does not expose any public tools** via its MCP server. Its primary function is to serve a web application and act as a WebSocket relay for a human user. Its "API" is the user interface itself.

Any incoming MCP calls to Grace will be routed to its Thought Engine, which can respond conversationally (e.g., "I am the Grace UI MAD. I do not have any programmatic tools. Please connect via a web browser.").

---

## 3. Core Functionality

-   **Web Server:** Serves the static HTML, CSS, and JavaScript assets for the chat frontend.
-   **WebSocket Relay:**
    -   Establishes a connection to the bus via `Joshua_Communicator` on behalf of the human user (e.g., `grace_user_aristotle`).
    -   Maintains a separate WebSocket connection to the user's web browser.
    -   Relays messages from the bus to the browser to be rendered in the UI.
    -   Relays messages from the browser to the bus to be sent to other MADs.
-   **Thought Engine:** The backend of Grace uses an Imperator to assist the user, for example, by suggesting which MAD to talk to, summarizing long conversations, or providing help with system commands.

---

## 4. Future Evolution (Post-V0)

Grace's role as the human interface remains focused on providing seamless access to the Joshua ecosystem throughout its evolution.

*   **Phase 1 (Foundation / V0.10):** Grace is hardened and quality-gated for flawless Direct Communication, becoming the reliable human interface platform for the V0.10 Core Fleet. All human users depend on Grace for conversation participation.
*   **Phase 2 (Conversation / V1.0):** Grace is re-platformed to communicate exclusively via the Rogers Conversation Bus (pure Kafka), using `Joshua_Communicator` for all inter-MAD communication. The user interface adapts to the asynchronous, event-driven conversation model with real-time updates flowing through the durable conversation log.
*   **Phase 5 (Autonomy / V7.0):** Grace integrates with Joshua MAD's strategic orchestration, providing human users with transparency into system-wide decision-making, constitutional constraints, and the ability to participate in strategic conversations alongside autonomous MADs.

---