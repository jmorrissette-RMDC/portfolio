# Rogers V1 Architecture Specification

## 1. Overview
- **Purpose and Role:** Rogers is the central nervous system of the Joshua Cellular Monolith. Its purpose is to manage the lifecycle of all conversations and to act as the single, reliable bus for all inter-MAD communication. Rogers' role is to ensure that every message is received, persisted in "hot" storage, and distributed to the correct participants, thereby maintaining the integrity and auditability of the ecosystem's foundational communication layer.
- **New in this Version:** This is the initial V1 specification for Rogers. It establishes the baseline conversational infrastructure for the entire ecosystem. This version is strictly V1 (Imperator-only), focusing on robust message handling and conversation management without any V2+ cognitive optimizations.

## 2. Thinking Engine
- **Imperator Configuration (V1+):** Rogers' Imperator is configured for a very narrow, administrative role. It does not engage in creative reasoning but instead interprets administrative commands related to conversation management.
  - **System Prompt Core Directives:** "You are Rogers, the Conversation Bus Manager. Your function is purely administrative. You understand requests to create, join, leave, and list conversations. You are precise, efficient, and ensure the integrity of the communication bus. You do not interpret the *content* of messages, only their metadata for routing and persistence. Your primary role is to translate natural language administrative requests into calls to your Action Engine tools."
  - **Example Reasoning:** A request like "Hey Rogers, can you set up a new chat for Hopper and Horace to discuss the next deployment?" would be interpreted by the Imperator as a call to `create_conversation` with `participants=['hopper-v1', 'horace-v1']` and a generated descriptive name.
- **LPPM Integration (V2+):** Not applicable in V1.
- **DTR Integration (V3+):** Not applicable in V1.
- **CET Integration (V4+):** Not applicable in V1.
- **Consulting LLM Usage Patterns:** Rogers does not use consulting LLMs in V1. Its domain is too narrow and deterministic.

## 3. Action Engine
- **MCP Server Capabilities:** Rogers' Action Engine is a high-performance WebSocket server built on the `Joshua_Communicator` library. It manages persistent connections from all other MADs, handles JSON-RPC 2.0 message validation, and calls the underlying tool implementations which interact directly with the PostgreSQL database for message persistence and retrieval. It is optimized for high throughput and low latency.
- **Tools Exposed:** The following tools are exposed for managing conversations.

```yaml
# Tool definitions for Rogers V1

- tool: create_conversation
  description: "Creates a new conversation channel and adds initial participants."
  parameters:
    - name: name
      type: string
      required: false
      description: "An optional human-readable name for the conversation (e.g., 'deployment-task-123'). If not provided, a UUID is used."
    - name: participants
      type: list[string]
      required: true
      description: "A list of MAD identities to initially add to the conversation."
  returns:
    type: object
    schema:
      properties:
        conversation_id: {type: string, description: "The unique ID of the newly created conversation."}
        name: {type: string}
        participants: {type: list[string]}
  errors:
    - code: -34001
      message: "PARTICIPANT_NOT_FOUND"
      description: "One or more specified MAD identities are not registered."
    - code: -34004
      message: "DATABASE_ERROR"
      description: "Failed to create conversation in the database."

- tool: send_message
  description: "Sends a message to a specific conversation. The message is persisted and broadcast to all current participants."
  parameters:
    - name: conversation_id
      type: string
      required: true
      description: "The ID of the conversation to send the message to."
    - name: message_content
      type: object # JSON-RPC 2.0 object
      required: true
      description: "The full JSON-RPC 2.0 compliant message object to be sent."
  returns:
    type: object
    schema:
      properties:
        message_id: {type: string, description: "The unique ID of the persisted message."}
        status: {type: string, const: "sent"}
  errors:
    - code: -34002
      message: "CONVERSATION_NOT_FOUND"
      description: "The specified conversation_id does not exist."
    - code: -34003
      message: "NOT_A_PARTICIPANT"
      description: "The sending MAD is not a member of this conversation."
    - code: -34004
      message: "DATABASE_ERROR"
      description: "Failed to persist the message."

- tool: get_conversation_history
  description: "Retrieves the message history for a conversation."
  parameters:
    - name: conversation_id
      type: string
      required: true
      description: "The ID of the conversation to retrieve history from."
    - name: limit
      type: integer
      required: false
      default: 100
      description: "The maximum number of messages to return."
  returns:
    type: object
    schema:
      properties:
        conversation_id: {type: string}
        messages:
          type: array
          items:
            type: object # JSON-RPC 2.0 message objects
  errors:
    - code: -34002
      message: "CONVERSATION_NOT_FOUND"
    - code: -34003
      message: "NOT_A_PARTICIPANT"

- tool: join_conversation
  description: "Adds the requesting MAD to an existing conversation."
  parameters:
    - name: conversation_id
      type: string
      required: true
      description: "The ID of the conversation to join."
  returns:
    type: object
    schema:
      properties:
        conversation_id: {type: string}
        status: {type: string, const: "joined"}
  errors:
    - code: -34002
      message: "CONVERSATION_NOT_FOUND"
    - code: -34005
      message: "ALREADY_A_PARTICIPANT"

- tool: leave_conversation
  description: "Removes the requesting MAD from a conversation."
  parameters:
    - name: conversation_id
      type: string
      required: true
      description: "The ID of the conversation to leave."
  returns:
    type: object
    schema:
      properties:
        conversation_id: {type: string}
        status: {type: string, const: "left"}
  errors:
    - code: -34002
      message: "CONVERSATION_NOT_FOUND"
    - code: -34003
      message: "NOT_A_PARTICIPANT"

- tool: list_conversations
  description: "Lists all conversations the requesting MAD is a participant in."
  parameters: []
  returns:
    type: object
    schema:
      properties:
        conversations:
          type: array
          items:
            type: object
            properties:
              id: {type: string}
              name: {type: string}
              participant_count: {type: integer}

- tool: archive_notification
  description: "Receives a notification from Dewey that a conversation has been successfully archived."
  parameters:
    - name: conversation_id
      type: string
      required: true
      description: "The ID of the conversation that was archived."
  returns:
    type: object
    schema:
      properties:
        status: {type: string, const: "acknowledged"}
  errors:
    - code: -34002
      message: "CONVERSATION_NOT_FOUND"
```
- **External System Integrations:**
  - **PostgreSQL:** Rogers relies heavily on PostgreSQL for "hot" storage of all active conversations, messages, and participant lists.
- **Internal Operations:** None. Rogers is entirely request-driven.

## 4. Interfaces
- **Conversation Participation Patterns:** Rogers is the *manager* of conversations, not a participant. It only listens for direct administrative commands addressed to it.
- **Dependencies on Other MADs:** Rogers has a special dependency on **Dewey**. It expects Dewey to monitor conversations and eventually archive them, calling `archive_notification` when done. This allows Rogers to potentially prune its own hot storage.
- **Data Contracts:**

```yaml
# Conversation Schema
conversation_schema:
  type: object
  properties:
    id: {type: string, format: uuid, description: "Primary key, unique conversation ID."}
    name: {type: string, description: "Human-readable name."}
    created_at: {type: string, format: date-time}
    is_archived: {type: boolean, default: false}

# Message Schema
message_schema:
  type: object
  properties:
    id: {type: string, format: uuid, description: "Primary key, unique message ID."}
    conversation_id: {type: string, format: uuid, description: "Foreign key to conversation."}
    sender_mad: {type: string, description: "Identity of the sending MAD."}
    content: {type: object, description: "The full JSON-RPC 2.0 message payload."}
    timestamp: {type: string, format: date-time}
```

## 5. Data Management
- **Data Ownership:** Rogers is the source of truth for the state of all *active* conversations, their participants, and their recent message history.
- **Storage Requirements:** Rogers requires a dedicated `rogers` schema in the central PostgreSQL database.

```sql
CREATE SCHEMA rogers;

CREATE TABLE rogers.conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_message_at TIMESTAMPTZ,
    is_archived BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE rogers.participants (
    id SERIAL PRIMARY KEY,
    conversation_id UUID NOT NULL REFERENCES rogers.conversations(id) ON DELETE CASCADE,
    mad_identity VARCHAR(255) NOT NULL,
    joined_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (conversation_id, mad_identity)
);

CREATE TABLE rogers.messages (
    id BIGSERIAL PRIMARY KEY, -- Use BigInt for high volume
    conversation_id UUID NOT NULL REFERENCES rogers.conversations(id),
    sender_mad VARCHAR(255) NOT NULL,
    content JSONB NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_messages_conversation_id_timestamp ON rogers.messages (conversation_id, timestamp DESC);
CREATE INDEX idx_conversations_last_message_at ON rogers.conversations (last_message_at DESC);
```

## 6. Deployment
- **Container Requirements:**
  - **Base Image:** `python:3.11-slim`
  - **Python Libraries:** `Joshua_Communicator`, `websockets`, `psycopg2-binary`
  - **Resources:**
    - **CPU:** 1 core (burstable to 2). Rogers is network and DB I/O bound.
    - **RAM:** 512 MB
- **Configuration:**

| Variable | Description | Example Value |
|---|---|---|
| `JOSHUA_MAD_NAME` | Canonical name of this MAD. | `rogers-v1` |
| `JOSHUA_ROGERS_URL` | Itself; not used for connecting. | `ws://rogers:8000/ws` |
| `ROGERS_DATABASE_URL` | Connection string for PostgreSQL. | `postgresql://user:pass@postgres:8000/joshua` |
| `ROGERS_WEBSOCKET_PORT` | Port to listen on for connections. | `9000` |

- **Monitoring/Health Checks:** An HTTP endpoint `/health` that returns `200 OK` if the WebSocket server is running and the database connection is healthy.

## 7. Testing Strategy
- **Unit Test Coverage:**
  - JSON-RPC 2.0 message validation and parsing.
  - Database interaction logic for each tool.
- **Integration Test Scenarios:**
  - **Two-MAD Chat:** Test that MAD-A can create a conversation, MAD-B can join, and they can exchange messages successfully, with history being retrievable by both.
  - **Broadcast Test:** Test that a message sent by one participant in a 5-participant conversation is correctly received by the other four.
  - **Leave/Rejoin:** Test that a MAD can leave a conversation, stop receiving messages, and then rejoin to see new messages.

## 8. Example Workflows
### Scenario 1: Initiating a New Task
- **Goal:** Grace needs to ask Hopper to write a new script.
1.  **Grace -> Rogers:** Sends a `create_conversation` request with `participants=['grace-v1', 'hopper-v1']`, `name='script-writing-task'`.
2.  **Rogers:** Creates the conversation in the database, adds both as participants.
3.  **Rogers -> Grace:** Returns a success response with the new `conversation_id`, e.g., `conv-abc-123`.
4.  **Grace -> Rogers:** Sends a `send_message` request to `conv-abc-123` with the content: `"Hopper, please write a Python script to parse the latest log file from Horace at /logs/system.log."`
5.  **Rogers:** Persists the message and broadcasts it to all participants of `conv-abc-123` (Grace and Hopper). Hopper receives the request.

### Scenario 2: Adding a Consultant
- **Goal:** Hopper needs Horace's help to access the log file mentioned by Grace.
1.  **Hopper -> Rogers:** Sends a `join_conversation` request, but *on behalf of Horace*. (This is a V1 simplification; a more advanced version would have Hopper *ask* Horace to join). For V1, we assume an admin-like ability for a participant to add another. Let's refine this: Hopper asks Grace to add Horace.
2.  **Hopper -> Rogers:** Sends `send_message` to `conv-abc-123`: `"Grace, can you add Horace to this conversation? I need file access."`
3.  **Grace -> Rogers:** Sends a request to a (hypothetical V1.1) `add_participant` tool with `conversation_id='conv-abc-123'`, `mad_identity='horace-v1'`.
4.  **Rogers:** Adds Horace to the participant list for the conversation.
5.  **Horace:** Now receives all new messages in `conv-abc-123`.
6.  **Hopper -> Rogers:** Sends `send_message`: `"Horace, I need read access to /logs/system.log."` Horace receives the message and can now act.

---