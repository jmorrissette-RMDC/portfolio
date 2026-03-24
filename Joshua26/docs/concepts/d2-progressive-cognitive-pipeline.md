# Concept: Progressive Cognitive Pipeline

**Status:** Concept
**Date:** 2026-03-05
**Maturity:** Designed, Not Yet Built

---

## Author

**J. Morrissette**

---

## What This Is

The Progressive Cognitive Pipeline (PCP) is the inbound cognitive messaging pipeline resident within each agent. It governs how incoming messages and triggers are processed — routing deterministic cases immediately, handling routine decisions through a lightweight agent, and reserving full reasoning for genuine novelty.

Its core principle is simple: not every decision requires expensive intelligence. Operations that can be handled by fast pattern matching should never reach a reasoning agent. Operations that require judgment but not full deliberation should not consume full reasoning capacity. Only genuine novelty should reach the most capable and costly tier.

The result is a pipeline that handles routine work reflexively, handles straightforward decisions through a capable but lightweight agent, and reserves the full reasoning tier for situations that genuinely require it — while becoming more efficient over time as patterns emerge and are absorbed into faster tiers.

---

## Biological Inspiration

The PCP is inspired by how biological cognition manages cost and capability.

Humans do not apply conscious deliberation to every action. Touch a hot surface and muscles contract before the brain is involved — a spinal reflex operating in milliseconds. Walk a familiar route and the motor patterns execute automatically, freeing conscious attention for other work. Encounter a genuinely novel problem and conscious deliberation engages, expensive and slow but capable of creative synthesis.

The PCP applies this same progressive architecture to agentic systems. Routine, deterministic operations are handled reflexively. Operations requiring intent understanding are handled by lightweight deliberation. Genuinely novel situations reach the full reasoning tier. The system reserves its most expensive capability for the work that actually needs it.

---

## The Three Tiers

### Tier 1 — Decision Tree Router (DTR)

The DTR handles deterministic pattern recognition at the reflexive level. It classifies incoming operations based on structural features and routes them directly to the appropriate function or flow.

The DTR does not understand intent. It does not read prose semantically. It recognises patterns — structural markers, command formats, known signatures — and routes with high confidence what it has seen before. Operations it cannot classify with sufficient confidence are escalated to the next tier.

**Characteristics:**
- Microsecond latency
- Non-semantic — pattern matching only
- Routes to specific functions or flows
- Online learning — improves as training data accumulates
- Conservative — false negatives acceptable, false positives are not

The DTR is the fastest and cheapest tier. In a mature system it handles the majority of operations.

### Tier 2 — Executor

The Executor bridges the gap between the DTR and the Imperator. Where the DTR cannot classify because it cannot understand intent, the Executor reads the operation semantically, exercises judgment, and handles it — or escalates to the Imperator when the situation genuinely exceeds its capability.

The Executor is a full agent, tuned to its role in the PCP. It handles rudimentary decisions end-to-end: understanding what an incoming message is trying to do, applying its domain knowledge, and either resolving the operation itself or escalating with context. It does not tackle novel problems or complex multi-step reasoning — that is the Imperator's domain. Its value is in handling the broad middle ground of operations that are too semantic for the DTR but too routine to warrant the Imperator.

**Characteristics:**
- Tuned to its domain and its protective role before the Imperator
- Handles rudimentary decisions end-to-end, not just routing
- Escalates genuine novelty to the Imperator with context
- Domain-specific configuration on top of shared agent class

### Tier 3 — Imperator

The Imperator is the full reasoning tier. It handles situations that neither the DTR nor the Executor could resolve — genuine novelty requiring creative synthesis, strategic planning, complex multi-step reasoning, or ambiguous situations that demand deep deliberation.

The Imperator is not a single reason-then-act pair. It is a composite of reasoning and acting components — a collection of cognitive tools that work together to address complex, novel situations. What those components are and how they are composed is specific to the agent's domain and purpose. The PCP describes how messages reach the Imperator. What the Imperator does with them is a separate concern.

The Imperator records everything. Every decision, every reasoning path, every outcome is captured. This record is the corpus from which the DTR and Executor learn. The Imperator's deliberate, expensive processing in early phases is not inefficiency — it is the investment that makes future efficiency possible.

**Characteristics:**
- Full reasoning capability — composite of reasoning and acting components
- Records all decisions for downstream learning
- Reserved for genuine novelty
- The only tier present in early-phase deployments

---

## Context Engineering

Context engineering — assembling the right information for the Imperator to reason effectively — is not a PCP tier. It is a separate architectural concern that operates alongside the pipeline. A capable context engineering system ensures the Imperator receives purpose-built context rather than generic conversation history, improving reasoning quality without changing the tier structure.

---

## The Learning Arc

The PCP matures through deliberate phases:

**Phase 1 — Imperator Only**
All operations reach the Imperator. Every decision is recorded. This phase is expensive and intentionally so — it builds the corpus that subsequent tiers learn from. No optimisation is possible without patterns to optimise from.

**Phase 2 — DTR Active**
The DTR is trained on the Phase 1 corpus. Deterministic patterns that the Imperator handled repeatedly are now routed directly. The Imperator is freed for less routine work. The pipeline begins its efficiency improvement.

**Phase 3 — Executor Active**
The Executor begins handling operations that are too semantic for the DTR but too routine for the Imperator. The Imperator is increasingly reserved for genuine novelty.

**Mature State**
The DTR handles the majority of operations. The Executor handles most of the remainder. The Imperator sees only what neither lower tier could resolve. The pipeline is significantly faster and cheaper than Phase 1, and more effective — the Imperator's reasoning is undiluted by routine work.

---

## Bidirectional Flow

The PCP flows in two directions simultaneously:

**Upward escalation** — operations flow toward greater capability when lower tiers cannot handle them. DTR escalates to Executor. Executor escalates to Imperator.

**Downward optimisation** — patterns flow toward faster tiers as they are learned. Imperator decisions inform Executor tuning. Executor patterns become DTR classifications. Novel work handled today becomes routine work handled reflexively tomorrow.

---

## Domain Specialisation

The PCP is a shared architecture with domain-specific instances. The DTR algorithm, the Executor mechanism, and the Imperator class are the same across all deployments. What differs is the training data — the patterns, the routing decisions, the reasoning history specific to each domain.

A DTR trained on filesystem access decisions routes differently from one trained on agent communication routing, even though both use the same underlying mechanism. Domain specialisation is in the data, not the architecture.

---

## What This Is Not

**Not a replacement for full reasoning.** The DTR and Executor exist to protect the Imperator's capacity, not to eliminate it. The Imperator remains the system's full reasoning capability and is essential for genuine novelty.

**Not static.** The PCP is designed to improve continuously. A system running PCP today should be measurably more efficient over time as patterns accumulate and tiers absorb routine work.

**Not uniform.** Not every deployment needs all three tiers from the start. A low-volume agent with simple routing may only ever need the DTR. A high-volume agent with complex semantic intake will benefit from the full cascade. The appropriate configuration is determined by operational characteristics.

---

## Relationship to Other Concepts

- **Decision Tree Router** (`d3-decision-tree-router.md`) — detailed design of the DTR algorithm and its online learning mechanism
- **Metacognitive Architect** (`b7-the-metacognitive-architect.md`) — the system-level function that governs PCP evolution: adjusting DTR routes and programmatically modifying StateGraphs as Imperator patterns mature
- **Context Broker** (`c1-the-context-broker.md`) — the context engineering capability that operates alongside the pipeline, ensuring the Imperator receives purpose-built context
- **Agent Communication Model** (`d5-agent-communication-model.md`) — the receiving moderator is a domain-specific Executor instance applied to incoming trigger handling
- **System 3 ReAct** (`d1-system-3-react.md`) — the Conversation Engine at the front of the reasoning loop IS the PCP; the three tiers describe how inbound conversation becomes cognition
