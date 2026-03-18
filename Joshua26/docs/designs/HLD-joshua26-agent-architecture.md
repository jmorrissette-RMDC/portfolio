# High-Level Design: Joshua26 Agent Architecture

**Version:** 2.0
**Date:** 2026-03-13
**Status:** Active
**Related Documents:** a1-conversationally-cognizant-ai-systems.md, a5-the-mad-pattern.md, HLD-state3-mad.md

---

## 1. Purpose

This document defines how agents are built, composed, and deployed in the Joshua26 ecosystem.
It covers the primitives that define agents, the two agent classes, the composition of the
Thought Engine, the base agent pattern, ReAct execution modes, development principles, and
the relationship between the AE and TE.

---

## 2. The Primitives

All agent architecture in Joshua26 is grounded in the primitives defined in
`a1-conversationally-cognizant-ai-systems.md`. These are not abstract concepts — they directly
determine how agents are built and how agent classes are distinguished.

**Identity** — what the agent IS. The stable core that persists across all interactions. A
context broker's identity is fundamentally different from an engineering agent's identity. Identity
does not change at runtime.

**Purpose** — what the agent is FOR. The reason it exists. Purpose defines the agent's domain
and scope of concern. Like Identity, Purpose is baked in and does not change at runtime.

**Intent** — the dynamic expression of Purpose meeting current circumstances. Intent is not
stored or packaged — it emerges at runtime as the agent's Purpose intersects with the situation
it faces. Intent is what the agent decides to do right now.

**Autonomy** — the capacity to act and decide without requiring direction. An autonomous agent
generates its own Intent from its own Purpose. A non-autonomous agent receives its intent from
the system that invokes it.

**Persona** — the behavioural presentation of the agent: style, tone, communication approach.
Persona is potentially dynamic — it can shift based on context, user, or circumstance. Identity
stays fixed; Persona can adapt. An agent might present differently when explaining something to
a novice versus collaborating with an expert, while remaining the same agent with the same
Identity and Purpose throughout.

**Domain** — the field of knowledge and responsibility the agent operates in. System domains
(infrastructure) for pMAD Imperators. Subject domains (expertise) for eMAD Imperators. Domain
shapes what the agent knows, what tools it needs, and what it reasons about.

---

## 3. Agent Classes

There are two agent classes in Joshua26. The distinction is grounded in which primitives they
possess.

### 3.1 Imperator

The Imperator is the prime agent within any Thought Engine. It possesses Identity, Purpose, and
Autonomy — and therefore generates its own Intent. It is self-directing.

The TE trappings — PCP, context assembly, inference, conversation-as-state — surround the
Imperator and make it cognitive and independent. The Imperator is a fully autonomous participant
in the ecosystem: addressable directly, communicating with other Imperators as a peer, learning
continuously from its operational experience.

Both pMADs and eMADs have Imperators:

- A **pMAD Imperator** governs a system domain. It is persistent — always running as part of
  its pMAD. It is the front door for all external interaction with that pMAD. It directs
  Executors, orchestrates work, and may host eMADs.

- An **eMAD Imperator** governs a subject matter domain. It is ephemeral — it exists only
  during StateGraph execution. Between invocations there is no running process. But during
  execution it is every bit as autonomous and capable as a pMAD Imperator. It has its own
  Identity, Purpose, and Persona. It generates its own Intent. It communicates with other
  agents as a peer.

The difference between pMAD and eMAD Imperators is domain type and lifecycle, not structure.
Both are a TE with an Imperator at its centre.

The Imperator does not typically execute work directly. Its role is to understand goals, maintain
the ongoing conversation via Rogers, and dispatch Executors or invoke eMADs to accomplish the
work. It synthesises results and communicates outcomes.

### 3.2 Executor

The Executor has no Identity or Purpose of its own. Its Intent is entirely derivative of the
calling system and circumstances. It has no Autonomy. It is cognitive — it can reason, use
tools, make decisions within its scope — but it is never independent. It is defined by the
system that uses it, not by what it is.

Executors can take many forms:
- Sub-agents of the Imperator dispatched for specific tasks
- Tools within AE StateGraph processes
- Specialised workers in a StateGraph flow
- Cognitive components within an Executor-driven AE process

The defining property across all forms is the absence of self-directed purpose. An Executor does
not decide what to do. It is told what to do, and it does it well.

Executors are not addressable by external agents. They do not participate in the ecosystem's
peer communication network. They are not eMADs — they have no MCP endpoint of their own, no
independent conversation, no standing in the ecosystem beyond the system that contains them.

---

## 4. Anatomy of the Thought Engine

The TE is the cognitive apparatus that surrounds the Imperator. Understanding what goes into a
TE is essential for building agents in Joshua26.

### 4.1 Identity and Purpose

Identity and Purpose are defined in the TE package and expressed through the system prompt
template. They are the foundation of what makes this agent *this particular agent*. When the
Imperator is invoked, the system prompt establishes who it is, what it's for, and what domain
it operates in.

Identity and Purpose do not change at runtime. They are baked into the TE package.

### 4.2 Persona

Persona is the behavioural layer — how the agent presents itself. Unlike Identity and Purpose,
Persona can be dynamic. The system prompt may select or adjust Persona based on:
- Who the agent is talking to (human vs agent, novice vs expert)
- The nature of the current task (teaching vs executing vs advising)
- Explicit direction ("be concise", "explain thoroughly")

Persona is defined as part of the TE package but may include conditional logic or multiple
Persona profiles that activate based on context.

### 4.3 Progressive Cognitive Pipeline (PCP)

The PCP governs how inbound communication is processed — from reflexive routing of simple
requests through to full Imperator reasoning for complex goals. Not every incoming message
requires the Imperator's full cognitive weight. The PCP determines the appropriate depth of
processing.

See `d2-progressive-cognitive-pipeline.md` for the full concept.

### 4.4 Inference

All LLM inference is delegated to Sutherland via named aliases. The TE never calls an LLM
endpoint directly. This centralises model selection, rate limiting, cost tracking, and alias
routing. Changing the model behind any reasoning or communication role requires only a
Sutherland configuration update — no changes to the TE package.

### 4.5 Context and Memory

The TE is stateless. All conversation state lives in Rogers — the context broker. On invocation,
the Imperator calls `conv_retrieve_context` to receive its curated context window. The agent's
memory of prior relevant work comes from Rogers, not from its own state. On completion, the
agent's work and conversation trace are committed back to Rogers, enabling future invocations
to benefit from accumulated experience.

This is conversation-as-state: the conversation IS the state. See `a2-conversation-as-state.md`.

### 4.6 StateGraph

The StateGraph is the programmatic logic that wires everything together: ReAct loops, tool
orchestration, escalation paths, Executor dispatch. Both the AE and TE express their
programmatic logic as LangGraph StateGraphs.

The TE StateGraph defines the Imperator's reasoning flow — how it receives a goal, assembles
context, reasons about the approach, selects and invokes tools, observes results, and iterates
until the goal is achieved or escalated.

---

## 5. The JoshuaAgent Base Pattern

Every agent in the ecosystem, regardless of class, is built on the same foundation:

- **Rogers for context** — on startup, the agent ensures a Rogers session exists and calls
  `conv_retrieve_context` to receive its curated context window.
- **Sutherland for inference** — all LLM inference is delegated to Sutherland via a named
  alias. The agent never calls an LLM endpoint directly.
- **Stateless by design** — agents carry no persistent state of their own. Conversation state
  lives in Rogers. Task execution state lives in the LangGraph StateGraph for the duration of
  the task, then is committed to Rogers.
- **ReAct execution** — all agents operate as ReAct loops: Thought → Action (tool call) →
  Observation → repeat until complete. The specific ReAct variant is matched to the agent's
  reasoning requirements (see Section 6).

---

## 6. ReAct Execution Modes

All agents are ReAct agents. The execution mode is matched to the nature of the work.
See `d1-system-3-react.md` for the full concept definition.

| Mode | Models | Appropriate for |
|---|---|---|
| **System 3 ReAct** | Reasoner + Actor + Conversation Engine | Imperator (always) |
| **System 2 ReAct** | Reasoner (deep planning) + Actor (precise execution) | Executor (most common) |
| **Standard ReAct** | Single model handles all steps | Executor (simple tasks) |

**Imperators are System 3 ReAct agents.** Conversation is the medium through which they receive
goals, reason, act, and communicate. The Conversation Engine at both ends of their reasoning
loop is not optional or situational. It is fundamental to what they are. Whether the other party
is a human or another agent does not change this — conversation is the universal medium.

**Executors are most commonly System 2**, matching a planning component to a precise execution
component. However, the class does not prescribe the mode. An Executor performing a simple
deterministic task may use standard ReAct. One producing output that requires communication
quality may use System 3. The appropriate mode is determined by the task, not the class.

All model selection is via Sutherland aliases. Changing the model behind any reasoning or
communication role requires only a Sutherland configuration update.

---

## 7. Building on LangChain and LangGraph

Joshua26 agents are built on LangChain and LangGraph, not around them. The principle: rely on
established components over custom implementations.

- **ReAct agents** — use LangGraph's ReAct agent patterns. Do not build custom reasoning loops
  when LangGraph provides them.
- **Tool definitions** — use LangChain's tool abstraction (`@tool` decorators, structured
  schemas). Tools are the unit of capability.
- **StateGraph patterns** — use LangGraph's StateGraph for all programmatic logic. State
  machines, conditional edges, parallel execution, checkpointing — all standard LangGraph.
- **Checkpointing** — use LangGraph's built-in checkpointing for StateGraph persistence during
  execution. Do not build custom state management.

Custom code is for domain logic — what this particular agent knows and does. The framework
handles the plumbing: reasoning loops, state management, tool invocation, graph execution.
This keeps the ecosystem maintainable and benefits from upstream improvements to LangChain and
LangGraph.

---

## 8. TE Package Development and Deployment

A TE is developed and deployed as a standard Python package, published to Alexandria and
installed into a running pMAD via `install_stategraph()`. See `HLD-state3-mad.md` for the full
dynamic loading architecture.

**A TE package contains:**
- StateGraph definitions (the Imperator's reasoning flow)
- System prompt templates (Identity, Purpose, Persona definitions)
- Tool registrations (what tools the Imperator can use)
- PCP configuration (routing rules, escalation thresholds)
- Entry_points registration (so the bootstrap kernel can discover the package)

**Development workflow:**
1. Develop the TE package locally against the host contract
2. Test using LangGraph's testing utilities
3. Publish to Alexandria with semantic versioning
4. Install into the target pMAD via `install_stategraph("[package-name]")`
5. The bootstrap kernel discovers the package and makes it available

The same workflow applies to AE StateGraph packages. Both are Python packages, both are
published to Alexandria, both are discovered via entry_points. The entry_points group
distinguishes AE from TE.

---

## 9. How the AE and TE Relate

The AE and TE are peers within a pMAD, but they are not symmetric in how they interact.

**The AE calls into the TE, not the other way around.** The web server routes incoming MCP tool
requests to AE handlers. When cognitive work is needed — a goal expressed in prose, a decision
requiring the Imperator's reasoning — the AE invokes the TE. The TE does not receive requests
directly from joshua-net. All external communication arrives through the AE.

**The TE has access to the AE's capabilities** via the host contract: peer proxy (to reach
other MADs), connection pools, tool registrations. The TE uses these capabilities as tools —
it calls them, it does not own them. The AE provides; the TE consumes.

**Autoprompting** — the current architecture is reactive: the TE activates only when prompted
via the AE. A truly autonomous system also requires self-initiated TE activation based on
triggers, schedules, queued work, or commitments made during prior conversations. See
`b6-autoprompting.md` for this emerging concept.

---

## 10. Agent Class Summary

| Property | Imperator | Executor |
|---|---|---|
| Identity | Yes — defines what it is | No — defined by its caller |
| Purpose | Yes — defines what it is for | No — derivative of calling system |
| Intent | Self-generated from Purpose + circumstances | Derivative of caller's intent |
| Autonomy | Yes — self-directing | No — under authority |
| Independent actor | Yes | No |
| Lifecycle | Persistent (pMAD) or Ephemeral (eMAD) | Subprocess — invoked inline |
| ReAct mode | System 3 (always) | System 2 most common; situational |
| Rogers session | Yes — ongoing or per-task conversation | Typically not |
| External addressability | Yes — peer in the ecosystem | No — internal to its MAD |
| Concurrent instances | One per pMAD; many per eMAD role | As needed |

---

## 11. Related Documents

- `a1-conversationally-cognizant-ai-systems.md` — the primitives: Identity, Purpose, Intent, Autonomy, Persona, Domain
- `a5-the-mad-pattern.md` — the MAD pattern, AE/TE, pMADs and eMADs, agent classes
- `HLD-state3-mad.md` — AE/TE separation architecture, dynamic StateGraph loading via Alexandria
- `d1-system-3-react.md` — ReAct execution mode concept
- `d2-progressive-cognitive-pipeline.md` — inbound cognitive processing pipeline
- `a2-conversation-as-state.md` — conversation as the substrate of state
- `b6-autoprompting.md` — self-initiated TE activation (stub — architectural design pending)
- `b1-the-quorum-pattern.md` — Quorum pattern for parallel generation and ensemble reasoning
- `HLD-conversational-core.md` — Rogers context hydration pattern
