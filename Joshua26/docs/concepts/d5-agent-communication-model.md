# Concept: Agent Communication Model

**Status:** Concept
**Date:** 2026-03-05
**Maturity:** Implementable

---

## Author

**J. Morrissette**

---

## Overview

Agents in an agentic ecosystem need to communicate with each other in ways that are reliable, auditable, loop-safe, and intelligent. This document defines the communication model: how messages are addressed, how recipients are notified, how moderator logic within each agent governs sending and receiving behaviour, and how the ecosystem learns from those decisions over time.

---

## 1. The Addressing Model

Every message in the ecosystem carries three addressing fields, borrowed from the proven email model:

- **From** — the sender
- **To** — the primary addressees; a response is expected from each
- **CC** — the secondary addressees; a response is optional and at their discretion

**Participants are an artifact of the message, not the conversation.** A conversation has no fixed participant list declared upfront. Participation is derived from the message history — who has appeared in From, To, or CC across the messages of a conversation. This is simpler than managing membership at the conversation level and more accurately reflects how communication actually works.

**No reply-to-all.** When an agent responds to a message, the default is to address the original sender only. The CC list is not inherited. Additional recipients must be explicitly chosen. This is the primary structural safeguard against cascading loops.

---

## 2. To vs CC Semantics

The distinction between To and CC is not about whether context is built — the ecosystem's memory system builds context for all agents regardless. The distinction is about **obligation**:

- **To** — the sender expects a reply. The receiving agent is obligated to respond.
- **CC** — the sender extends an invitation. The receiving agent may contribute if it has something relevant to add. No response is expected or assumed.

This difference governs how each agent handles incoming messages and is the foundation of the moderator logic described below.

---

## 3. The Trigger System

Because messages are stored in the Conversation Broker before any notification is sent, message delivery is always safe. The trigger is a lightweight notification — it carries no content, only the signal that new content exists in a conversation. The recipient reads the content from the Conversation Broker directly.

**The Conversation Broker is in the trigger path.** This is deliberate. Because every message passes through the Conversation Broker on the way to storage, it has visibility into all communication patterns and can apply safety logic before firing any trigger. This centralised position is what enables loop protection.

### 3.1 Loop Protection

The Conversation Broker applies the following checks before firing any trigger:

- **Hop counting** — each message carries a hop count, incremented with each agent-to-agent exchange. If the count exceeds a threshold, the trigger is not fired. This is the primary loop-breaking mechanism, borrowed directly from email's Received header model.
- **Rate limiting** — per-agent limits on trigger frequency within a time window. A single agent generating an unusual volume of messages is throttled.
- **Deduplication** — a trigger is never fired twice for the same message. Message IDs are tracked to prevent double delivery.

### 3.2 Trigger Delivery Reliability

The message is already safe in the Conversation Broker before any trigger is fired. A failed trigger does not mean a lost message — it means an unnotified recipient. The recipient can always recover by polling the Conversation Broker directly.

Nevertheless, triggers are delivered reliably:
- Retry with exponential backoff if the recipient is temporarily unavailable
- Dead letter handling if retries are exhausted — the sender is notified that real-time delivery failed, but the message remains available in the Conversation Broker

### 3.3 The Trigger Endpoint

Every agent exposes a standard trigger endpoint as part of its template. The endpoint receives a lightweight notification containing only the `conversation_id`. The agent's internal routing logic then decides what to do — it does not respond to the trigger itself, it reads the conversation from the Conversation Broker and acts from there.

---

## 4. The Moderator Executor

Every agent contains a Moderator — an internal Executor (see agent architecture) that governs communication behaviour. The Moderator is not conversational; it makes structured decisions at defined points in the agent's workflow.

There are two Moderator roles, each with its own system prompt:

### 4.1 The Sending Moderator

Invoked when the agent is about to write a message. It takes the composed message and decides the addressing:

- Who belongs in To — whose response is required?
- Who belongs in CC — who might benefit from knowing?

It may apply programmatic rules, call a small inference model for deliberation, or query the moderation knowledge graph for learned patterns. The decision is domain-specific — what good addressing looks like for a security agent differs from what it looks like for a data engineering agent.

**The sending moderator system prompt** defines the agent's communication philosophy: which roles it typically collaborates with, what signals in a message suggest certain participants should be included, and what the agent's default addressing posture is.

### 4.2 The Receiving Moderator

Invoked when the trigger endpoint fires. It reads the conversation context from the Conversation Broker and makes a routing decision:

**For To messages** — the agent is obligated to respond. The receiving moderator determines the appropriate internal handler and invokes it.

**For CC messages** — the agent is invited but not obligated. The receiving moderator applies deliberation: given the message content and the agent's current context, is there something relevant to contribute? If yes, it invokes the appropriate handler. If no, it does nothing.

**The receiving moderator system prompt** defines when optional participation is warranted: which topics are within the agent's domain, what kinds of CC messages typically merit a response, and what the agent's default engagement posture is.

### 4.3 Routing Tiers

The receiving moderator's internal routing is not one-size-fits-all. The appropriate implementation depends on the agent's volume and decision complexity:

**Tier 1 — Programmatic routing:** For low-volume agents or agents with simple, stable routing decisions. Direct programmatic rules determine which handler to invoke. No inference model required.

**Tier 2 — Inference-assisted routing:** For agents where routing decisions are contextual and benefit from deliberation. A small inference model evaluates the message and selects the appropriate handler.

**Tier 3 — Learned routing (DTR):** For high-volume agents with learnable routing patterns. A Decision Tree Router (see `d3-decision-tree-router.md`) sits before the inference model. It routes high-confidence patterns immediately without inference, and defers novel or ambiguous cases to the inference model. The DTR learns from every routing decision, progressively absorbing the repetitive, deterministic decisions that would otherwise consume inference capacity.

The appropriate tier is determined during agent design and documented in the agent's requirements. The DTR tier is the default recommendation for any agent expected to receive high volumes of triggers.

### 4.4 The Moderator and Agent Classes

The Moderator is an Executor — it is internal to the agent, not addressable from outside, and invoked programmatically at defined points in the agent's workflow. The receiving moderator may invoke the Imperator for conversational messages, any other internal Executor for operational work, or do nothing. The Imperator is not always the first handler — the receiving moderator routes based on the nature of the incoming message.

---

## 5. The Moderation Decision Knowledge Graph

The ecosystem accumulates knowledge about communication decisions over time. This knowledge is stored as a graph with a three-part relationship structure:

1. **Trigger** — what the moderator observed that caused it to make a decision (signals in the message content, patterns detected)
2. **Decision** — what choice was made (who was addressed, whether to engage, which handler was invoked)
3. **Quality** — was the decision good or bad (did the CC recipient contribute? did the engagement add value? did a loop result?)

This graph does not duplicate conversation content. It captures the decision process in abstract — the trigger is a representation of observed signals, not a copy of the message. The graph is queried by the sending and receiving moderators when making their decisions, providing institutional memory of what communication patterns have worked well historically.

The graph lives within the Context Broker, as a distinct collection from conversation content and general context knowledge. The Conversation Broker stores messages; the Context Broker maintains the knowledge graph built from those messages.

---

## 6. The Curation Cycle

Moderation decisions are evaluated through a two-stage process:

### Stage 1 — Decision Log (Immediate)

When a moderator makes a decision, a record is written immediately to a structured log:
- The observed trigger signals
- The decision made
- The conversation and agent context
- Status: `pending_evaluation`

This write is fast and synchronous. No quality assessment is made at this point.

### Stage 2 — Background Curation (Delayed)

A background process runs continuously, evaluating pending decisions against observable signals:

- **Immediate signals** — loop events, handler failures, clean completions
- **Short-term signals** — did the CC recipient engage? did the To recipient respond appropriately?
- **Long-term signals** — did the conversation reach its goal? did the task complete?

When sufficient signal is available, the curation process:
1. Writes a quality score back to the decision log
2. Promotes the three-part relationship (trigger → decision → quality) into the moderation knowledge graph
3. Generates a training example for the DTR (if the agent uses one)

This means quality assessments for long-running conversations arrive well after the decision was made. The curation process handles retroactive updates — a decision made early in a conversation may be re-evaluated when the conversation closes days later.

### 6.1 The DTR Training Pipeline

For agents using the DTR tier, the curation cycle serves a second function: it observes the Imperator's routing decisions over time, recognises repetition, and feeds those patterns as training data to the Hoeffding tree. This enables the DTR to absorb the Imperator's repetitive, deterministic decisions progressively. The Imperator is freed for genuinely novel and complex work as the DTR matures.

The maturation arc of a high-volume agent:
- **Early:** Imperator handles most triggers; DTR is in learning mode
- **Developing:** DTR begins routing well-understood patterns directly
- **Mature:** DTR routes the majority; Imperator is reserved for the novel and complex

---

## 7. The Sending Side and Receiving Side as Symmetric Intelligence

The same intelligence layer — the moderator, the 7B inference model, the knowledge graph — applies symmetrically to both sending and receiving:

- **Sending:** "Given what I'm about to say, who should be in To and who should be in CC?"
- **Receiving:** "Given what was just said, should I contribute?"

Both questions are answered using the same tools: domain-specific system prompts, inference model deliberation for ambiguous cases, and the moderation knowledge graph for learned patterns. The sending and receiving system prompts are distinct because the questions are different, but the underlying mechanism is shared.

Over time, both sides improve together. Better sending decisions produce better conversations. Better receiving decisions mean agents engage when they add value and stay silent when they do not.

---

## Relationship to Other Concepts

- **Decision Tree Router** (`d3-decision-tree-router.md`) — the Tier 3 receiving moderator routing mechanism for high-volume agents
- **The Conversation Broker** (`c3-the-conversation-broker.md`) — the Conversation Broker foundation: message store, addressing model, trigger delivery, loop protection
- **Context Broker** (`c1-the-context-broker.md`) — hosts the moderation knowledge graph and draws on the Conversation Broker's message store to assemble context for agents
- **The JoshuaAgent Base Pattern** (`HLD-joshua26-agent-architecture.md`) — the Executor agent class is what the Moderator is; the Imperator is one possible target of the receiving moderator's routing decision
