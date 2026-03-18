# HLD: Progressive Cognitive Pipeline

**Status:** Design
**Date:** 2026-03-05

---

## Overview

This document describes how the Progressive Cognitive Pipeline (PCP) is implemented within the Joshua26 ecosystem. For the general concept, see `docs/concepts/d2-progressive-cognitive-pipeline.md`. For the Ecosystem Metacognition function that governs the PCP's evolution, see `docs/concepts/b7-the-metacognitive-architect.md`.

The PCP in Joshua26 comprises three cognitive tiers — DTR, Executor, and Imperator — supported by the Context Broker and governed at the ecosystem level by Joshua-pMAD.

---

## Tier 1: Decision Tree Router (DTR)

### Implementation

Each pMAD in Joshua26 that processes incoming triggers or requests hosts a DTR instance. The DTR is implemented as a Hoeffding tree (Very Fast Decision Tree) — an online learning algorithm that updates incrementally with each classified operation without requiring batch retraining.

The DTR sits at the entry point of the pMAD's LangGraph StateGraph, before any LLM invocation. It is the first node in the flow for all incoming operations.

### Routing Targets

The DTR routes to specific LangGraph flows registered within the pMAD. Routing targets include:

- Existing flows defined at design time
- New flows added by Joshua-pMAD as patterns are crystallised from Imperator history

The DTR's routing target registry expands over time. New targets are registered by Joshua-pMAD when new flows are commissioned and deployed.

### Training

Initial DTR training data comes from the Phase 1 corpus — Imperator decision history stored in Rogers. As the pMAD operates, the DTR updates online from each classified operation. Joshua-pMAD may additionally push targeted route updates as patterns are identified at the ecosystem level.

### Per-pMAD Specialisation

Each pMAD's DTR is trained on its own operational domain. The DTR in Horace routes filesystem access patterns. The DTR in the agent communication layer routes incoming trigger patterns. Same algorithm, domain-specific training data.

For the detailed DTR design, see `docs/concepts/d3-decision-tree-router.md`.

---

## Tier 2: Executor

The Executor is a full agent, tuned to its role in the PCP. It sits in the LangGraph flow between the DTR escalation path and the Imperator. Operations that the DTR cannot classify with sufficient confidence are passed to the Executor.

### Function

The Executor understands the intent of an incoming operation, exercises judgment within its domain, and either handles it end-to-end or escalates to the Imperator with context. It handles the broad middle ground of operations — too semantic for the DTR, too routine for the Imperator.

The specific model alias used by the Executor is defined per pMAD based on domain and complexity requirements, resolved via Sutherland.

### Relationship to the Receiving Moderator

The receiving moderator in the agent communication model (see `d5-agent-communication-model.md`) is a domain-specific Executor instance applied to incoming trigger handling — understanding trigger intent, determining whether the agent should engage, and routing to the appropriate internal handler. The PCP Executor and the receiving moderator are the same agent class serving the same structural role in their respective contexts.

---

## Tier 3: Imperator

### Implementation

The Imperator is implemented as a LangGraph StateGraph node invoking a reasoning-capable model via Sutherland. The specific model alias is defined per pMAD based on reasoning requirements.

In Joshua26, the Imperator is present from Phase 1. All pMADs begin with Imperator-only operation. The DTR and Executor are added as the pMAD accumulates sufficient operational history.

### Recording for Learning

All Imperator operations are recorded to Rogers with structured metadata:

- The triggering operation and its context
- The reasoning path taken
- The orchestration steps executed
- The outcome and quality signals
- Tags indicating operation type and complexity

This structured record is the corpus from which the DTR and Executor learn, and from which Joshua-pMAD identifies patterns worth crystallising into new flows.

---

## Context Engineering: Context Broker

Context engineering in Joshua26 is provided by the Context Broker capability within Rogers. This is not a PCP tier — it is a foundational capability that operates alongside the pipeline.

When an operation reaches the Imperator, Rogers assembles purpose-built context: relevant conversation history, prior decisions on similar operations, knowledge graph relationships, and domain-specific knowledge. The Imperator reasons with this assembled context rather than generic history.

See `docs/concepts/c1-the-context-broker.md` for the full design.

---

## Ecosystem Metacognition: Joshua-pMAD

Joshua-pMAD implements the Ecosystem Metacognition function for the Joshua26 ecosystem. See `docs/concepts/b7-the-metacognitive-architect.md` for the general concept.

### Joshua-pMAD's Role in PCP Evolution

Joshua-pMAD observes Imperator operation across all pMADs via Rogers. It identifies patterns in the operational record and acts on them:

**DTR Updates**
When a routing pattern has become deterministic through repetition, Joshua-pMAD updates the relevant pMAD's DTR with a new classification rule pointing to the appropriate existing flow. This is Joshua-pMAD's primary early-phase intervention and the lowest-risk structural change available.

**New LangGraph Flows**
When an Imperator orchestration pattern has repeated with sufficient frequency and stability, Joshua-pMAD commissions a new LangGraph flow encoding that pattern as a deterministic path. The new flow is deployed to the target pMAD. The DTR is updated to route the pattern to the new flow. Future instances bypass the Imperator entirely.

**Capability Gap Response**
When agents surface capability gaps — requests they cannot handle — Joshua-pMAD evaluates whether the gap is worth filling and commissions development of the required capability.

### Early Phase Constraints

In early-phase operation, Joshua-pMAD is constrained to DTR updates only. StateGraph generation and broader system-level decisions require demonstrated reliability before being enabled. All changes in the early phase seek human approval regardless of severity. Joshua-pMAD earns its autonomy progressively.

---

## Implementation Sequence

### Phase 1 — Imperator Foundation

All pMADs operate with Imperator-only routing. The DTR and Executor nodes exist in the StateGraph but pass all operations through without classification. Every operation reaches the Imperator. Rogers accumulates the operational corpus.

Joshua-pMAD is operational but constrained to observation and human-approved DTR updates only.

### Phase 2 — DTR Active

Per-pMAD DTR activation when sufficient training data exists in the Phase 1 corpus. Activation is per-pMAD, not ecosystem-wide — each pMAD transitions when its own corpus is ready.

Joshua-pMAD begins autonomous DTR updates for well-established low-severity patterns.

### Phase 3 — Executor Active

Per-pMAD Executor activation. The semantic intent layer begins handling operations that the DTR cannot classify. The Imperator is increasingly reserved for genuine novelty.

### Phase 4 — Full Metacognition

Joshua-pMAD's StateGraph generation capability is enabled. New flows are commissioned from Imperator patterns. The ecosystem begins structural self-improvement. Joshua-pMAD's governance model expands as trust is established.

---

## Relationship to Other Documents

- **Concept — Progressive Cognitive Pipeline** (`docs/concepts/d2-progressive-cognitive-pipeline.md`) — the general PCP concept this HLD implements
- **Concept — Metacognitive Architect** (`docs/concepts/b7-the-metacognitive-architect.md`) — the MA function Joshua-pMAD implements: DTR adjustment and StateGraph modification
- **Concept — Decision Tree Router** (`docs/concepts/d3-decision-tree-router.md`) — DTR algorithm and online learning design
- **Concept — Context Broker** (`docs/concepts/c1-the-context-broker.md`) — context engineering capability
- **Concept — Agent Communication Model** (`docs/concepts/d5-agent-communication-model.md`) — receiving moderator as domain-specific Executor instance
- **HLD — Joshua26 Agent Architecture** (`docs/designs/HLD-joshua26-agent-architecture.md`) — agent class definitions including Imperator and Executor
