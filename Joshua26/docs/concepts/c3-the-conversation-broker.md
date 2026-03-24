# Concept: The Conversation Broker

**Status:** Concept
**Date:** 2026-03-05
**Maturity:** Implementable

---

## Author

**J. Morrissette**

---

## What This Is

Agents in an agentic ecosystem need to send messages to each other with clear addressing, reliable delivery, auditable history, and protection against runaway communication loops. This document defines the foundational messaging model that enables this — a model that maps closely to email, the most proven and widely understood addressed messaging system ever built.

This is a distinct capability from context engineering and knowledge brokerage. Though the two may be co-located in a single service in practice, they are architecturally separable concerns. This document describes the messaging capability alone, independent of how or where it is implemented.

---

## Why Email

The email model was not chosen arbitrarily. Every problem that agent-to-agent messaging needs to solve has already been solved by email:

- **Addressed communication** — messages go to named recipients, not broadcast to all
- **Threading** — conversations group messages into coherent exchanges
- **Participant history** — who was involved in a conversation is derivable from the messages themselves
- **Delivery notification** — recipients are notified when new messages exist
- **Loop protection** — mechanisms exist to detect and break delivery loops
- **Reliability** — retry, backoff, and dead letter handling for failed delivery

The analogy is not metaphorical. The model described here applies these same structures to agent communication directly.

What it does not use is the email infrastructure: no SMTP, no IMAP, no MIME, no MX records. Those were designed for communication across the public internet between arbitrary third parties. Agent communication is internal, controlled, and known. The concepts transfer; the infrastructure does not.

---

## The Message

Every message in the system carries the following fields:

- **From** — the sending agent
- **To** — one or more primary recipients; a response is expected from each
- **CC** — zero or more secondary recipients; a response is optional and at their discretion
- **conversation_id** — the thread this message belongs to; new conversations are created on first use
- **message_id** — a unique identifier for this message; used for deduplication
- **hop_count** — the number of agent-to-agent exchanges this conversation has traversed; used for loop detection
- **content** — the message body

### To vs CC

The distinction between To and CC is not about context. The messaging system builds no context — context engineering is a separate concern. The distinction is about **obligation**:

- **To** — the sender expects a response. The recipient is obligated to act.
- **CC** — the sender extends an invitation. The recipient may contribute if they have something relevant to add. No response is assumed or required.

This distinction governs how receiving agents handle incoming messages. It is the primary mechanism through which agents manage optional participation without creating noise or cascade risk.

---

## Participants Are an Artifact of the Message

A conversation has no declared participant list. There is no concept of joining or subscribing to a conversation. Participation is derived from the message history — who has appeared in From, To, or CC across the messages of a conversation thread.

This is simpler, more accurate, and more flexible than managing membership at the conversation level. It maps exactly to how email threads work: you are part of a thread because you were addressed in a message within it, not because you joined it.

An agent that has never been addressed in a conversation has no membership in it and receives no notifications from it.

---

## No Reply-to-All

When an agent responds to a message, the default is to address the original sender only. The CC list from the incoming message is not inherited. The responding agent must explicitly choose to include additional recipients.

This is the primary structural safeguard against cascading communication loops. Without it, a message addressed to ten agents produces ten responses addressed to ten agents, each producing ten more. The no-reply-to-all default keeps exchanges directed.

---

## The Message Store

All messages are written to a durable message store before any notification is sent. The store is the source of truth. Once a message is in the store it is safe — delivery of the notification is a separate, best-effort process that does not affect message durability.

The store supports:
- Retrieval by conversation_id (thread view)
- Retrieval by message_id (single message)
- Retrieval by recipient (messages addressed to a given agent)
- Full message history with all addressing fields preserved

The store is architecturally separable from any context engineering or knowledge brokerage capability. It holds messages. It does not assemble context windows, extract memory, or build knowledge graphs. Those are different concerns.

---

## The Trigger

When a message is stored, the message store notifies the addressed recipients. The trigger is a lightweight notification — it carries no message content, only the `conversation_id` and the nature of the addressing (To or CC). The recipient reads the message content from the store directly.

**Content is never in the trigger.** The trigger is disposable. If it fails to deliver, the message is still safe in the store and the recipient can recover by polling.

### The Store Is in the Trigger Path

The message store fires the trigger, not the sender. This is deliberate. Because every message passes through the store before any trigger is sent, the store has visibility into all communication patterns and can apply safety logic centrally before notifying anyone. This centralised position is what enables reliable loop protection.

### Trigger Delivery

Triggers are delivered to the recipient agent's standard trigger endpoint — a lightweight inbound endpoint that every agent exposes. The trigger endpoint carries no routing logic; it simply signals the agent that new content exists in a conversation.

If the trigger cannot be delivered:
- **Retry with exponential backoff** — attempt redelivery across a configured window
- **Dead letter** — if retries are exhausted, log the failure and notify the sender; the message remains in the store and is always retrievable by polling

---

## Loop Protection

The message store enforces the following before firing any trigger:

### Hop Counting

Each message carries a `hop_count` field. Every time the message store writes a message to a conversation that already has messages in it, it increments the hop count. If the hop count exceeds a configured threshold, the trigger is not fired and the sender is notified.

This is borrowed directly from email's Received header model. It is simple, fast, and does not require pattern analysis — a message that has been through too many agent hands is rejected regardless of content.

### Rate Limiting

The message store tracks message frequency per agent per conversation within a rolling time window. An agent generating an unusual volume of messages is throttled. Triggers are not fired for messages that exceed the rate limit.

### Deduplication

Message IDs are tracked. A trigger is never fired twice for the same message_id. If a message is written twice (due to a retry in the sender's system), only the first instance produces a trigger.

---

## Polling as Fallback

Any agent that cannot receive triggers, or that wishes to check for new messages independently of the trigger system, can poll the message store directly by querying for messages addressed to it in a given conversation since a given timestamp. Polling always works regardless of trigger delivery status.

This also supports multi-party conversations where an agent wants to follow a thread it participates in without relying on real-time notification.

---

## What This Is Not

**Not a message bus or pub/sub system.** Agents do not subscribe to topics or channels. They receive messages addressed to them. Participation is through addressing, not subscription. The subscription model implies a broadcaster and passive consumers — the email model implies directed communication between known parties.

**Not an actual email server.** SMTP, IMAP, JMAP, and related infrastructure solve problems specific to communication across the public internet: arbitrary senders, hostile environments, unknown clients, external delivery. None of those problems apply in a controlled agentic ecosystem. The email model applies; the email infrastructure does not.

**Not context engineering.** This system stores messages and delivers notifications. It does not assemble context windows, extract semantic memory, build knowledge graphs, or retrieve relevant prior work. Those are the concerns of a context engineering and brokerage capability, which may or may not be co-located with the message store in a given implementation.

---

## Architectural Separability

The messaging capability described here — message store, addressing model, trigger delivery, loop protection — is architecturally independent of context engineering and knowledge brokerage. They are distinct concerns with distinct data models, distinct interfaces, and distinct operational characteristics.

The **Conversation Broker** owns the messaging layer: message storage, From/To/CC addressing, trigger delivery, loop protection. It is complete and useful without any context engineering capability present.

The **Context Broker** owns context assembly: engineered context windows, knowledge graph management, semantic search, summarisation. It draws on the Conversation Broker's message store as its source of conversational history but does not own message storage itself.

In early deployments, a single service may implement both concerns. As the ecosystem matures, separation into distinct services becomes appropriate — the Conversation Broker handles all communication infrastructure; the Context Broker focuses entirely on turning that conversation record into purposeful cognitive fuel.

---

## Relationship to Other Concepts

- **Agent Communication Model** (`d5-agent-communication-model.md`) — the intelligence layer built on top of this foundation: moderator executors, sending and receiving prompts, the moderation knowledge graph, the curation cycle
- **Decision Tree Router** (`d3-decision-tree-router.md`) — used within the receiving moderator for high-volume agents to route incoming triggers without inference overhead
- **Context Broker** (`c1-the-context-broker.md`) — the context engineering and brokerage capability that is architecturally separable from but may be co-located with the agent messaging service
