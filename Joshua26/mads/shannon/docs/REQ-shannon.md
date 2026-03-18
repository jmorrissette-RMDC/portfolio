# REQ-shannon — Shannon Conversation Broker

**Version:** 0.1 (Phase A)
**Date:** 2026-03-06
**Status:** Phase A — Purpose and Registry
**Delta REQ:** Describes only what differs from the MAD template baseline

---

## 1. Purpose

Shannon is the **Conversation Broker** — the MAD responsible for storing and delivering agent-to-agent and agent-to-human conversations. It is the messaging infrastructure of the ecosystem.

Shannon implements the email-for-agents model: every message carries From/To/CC addressing, every conversation accumulates an infinite thread, and every trigger is fired centrally through Shannon, enabling loop protection across the ecosystem. Shannon owns the store-and-forward communication layer. It does not assemble context, perform semantic search, or maintain knowledge graphs — those are the Context Broker's concerns.

**The architectural split from Rogers:** Rogers currently serves two concerns — message storage and context assembly. These are distinct in purpose, data model, and operational characteristics. Shannon takes on the conversation storage and messaging concern. Rogers retains context assembly, knowledge graph management, and engineered context production. Once Shannon is deployed, Rogers' scope narrows to the Context Broker function it was always meant to serve.

Shannon is named after Claude Shannon, who established the mathematical foundations of communication and information theory.

---

## 2. Registry Allocation

```yaml
shannon:
  uid: 2038
  gid: 2001
  port: 9228
  host: m5
  description: Conversation Broker — agent-to-agent and agent-to-human messaging, From/To/CC addressing, trigger delivery, loop protection
```

---

## 3. MCP Interface

All tools follow the `conv_` domain prefix convention.

### Conversation Management

| Tool | Description |
|---|---|
| `conv_create_conversation` | Create a new conversation. Returns `conversation_id`. |
| `conv_store_message` | Store a message with From/To/CC addressing. Triggers deduplication, hop count enforcement, rate limiting, and trigger delivery to addressed recipients. |
| `conv_get_history` | Retrieve full message sequence for a conversation in chronological order. |
| `conv_search_messages` | Search within a conversation or across conversations by sender, date range, or semantic query. |
| `conv_get_participants` | Return participants derived from message history (From/To/CC across all messages). Participants are an artefact of the message, not declared membership. |
| `conv_get_conversation` | Get conversation metadata. |

### Trigger Management

| Tool | Description |
|---|---|
| `conv_register_trigger_endpoint` | Register an agent's trigger endpoint URL so Shannon can notify it when addressed messages arrive. |
| `conv_get_trigger_status` | Query delivery status of a trigger — delivered, retrying, dead-lettered. |

### Loop Protection (Internal — not exposed as MCP tools)

Shannon enforces before firing any trigger:
- **Hop counting** — rejects messages exceeding the configured hop threshold
- **Rate limiting** — throttles agents generating unusual message volume
- **Deduplication** — suppresses duplicate triggers for the same message_id

---

## 4. Message Model

Every message stored by Shannon carries:

| Field | Description |
|---|---|
| `message_id` | Unique identifier. Used for deduplication. |
| `conversation_id` | The thread this message belongs to. |
| `from` | The sending agent (system UID). |
| `to` | One or more primary recipients. Response expected from each. |
| `cc` | Zero or more secondary recipients. Response optional, at their discretion. |
| `hop_count` | Number of agent-to-agent exchanges this conversation has traversed. Incremented by Shannon on each store. |
| `role` | Message role: `user`, `assistant`, `system`, `tool`. |
| `content` | Message body. |
| `sender_id` | System UID of the participant. |
| `created_at` | Timestamp. |

Triggers are lightweight — they carry only `conversation_id` and addressing tier (To or CC). Content is never in the trigger. Recipients read from Shannon directly.

---

## 5. Dependencies

| Dependency | Purpose | Degradation |
|---|---|---|
| Rogers (ACB) | Shannon notifies the ACB of new messages so the ACB can update its context assembly and knowledge graph pipelines | If Rogers unavailable, messages are stored safely in Shannon; ACB sync resumes when Rogers returns |
| Sutherland (AIB) | Optional — for semantic search over message content | Search degrades to structured-only if Sutherland unavailable; core messaging unaffected |

Shannon's core function — store, address, trigger — has no external dependencies. It must work when other services are down.

---

## 6. Container List

| Container | Role |
|---|---|
| `shannon` | MCP gateway. Exposes `conv_*` tools on `joshua-net`. |
| `shannon-langgraph` | LangGraph processing engine. Handles message pipeline, trigger delivery, loop protection. |
| `shannon-postgres` | Durable message and conversation storage. pgvector for semantic search. |
| `shannon-redis` | Async job queue for trigger delivery retry, background processing. |

---

## 7. Architectural Notes

**Shannon is the store-and-forward layer.** Every message in the ecosystem passes through Shannon before any notification is fired. This central position is what enables reliable loop protection — hop counting, rate limiting, and deduplication are enforced here, not in individual agents.

**The ACB reads from Shannon.** The Context Broker draws on Shannon's message store when assembling context windows. Shannon stores; the ACB interprets and assembles. The data flows one way: Shannon → ACB. Shannon does not depend on the ACB.

**Rogers migration.** Shannon's toolset overlaps with Rogers' current `conv_*` tools. The migration path is: Shannon is deployed with the full message storage capability; agents are migrated to use Shannon for message storage while continuing to use Rogers for context retrieval. Once migration is complete, Rogers' message storage tables are retired and Rogers becomes a pure context assembly service.

**Trigger endpoint standard.** Every MAD exposes a standard trigger endpoint as part of the template. Shannon delivers triggers to these endpoints. The trigger model follows the email-for-agents concept: lightweight notification only, content always read from Shannon directly.

See `docs/concepts/concept-email-for-agents.md` and `docs/concepts/concept-agent-communication-model.md` for the full conceptual basis.

---

## 8. Open Questions (Phase B)

- Exact postgres schema — messages, conversations, trigger delivery log
- Trigger retry strategy — backoff intervals, dead letter threshold
- Hop count threshold configuration — per-ecosystem vs per-conversation
- Rate limiting configuration — per-agent, per-conversation, rolling window
- ACB notification interface — how Shannon signals Rogers that new messages are available
- Migration plan from Rogers' current conv_* tools — phased agent migration strategy
