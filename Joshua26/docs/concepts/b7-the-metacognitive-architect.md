# Concept: Metacognitive Architect

**Status:** Concept
**Date:** 2026-03-05
**Maturity:** Research Required

---

## Author

**J. Morrissette**

---

## What This Is

The Metacognitive Architect (MA) is the system-level intelligence that observes an agentic ecosystem's operation over time and acts on what it learns — modifying the cognitive pipelines of individual agents to make them progressively more efficient, and commissioning new capabilities when the ecosystem's operational history warrants them.

The MA does not participate in the domain work of the agents it governs. It watches. It analyses. And when patterns in the operational record are clear enough, it acts — adjusting routing, crystallising learned behaviours into code, and ensuring the ecosystem improves as it operates.

---

## The MA's Role in the PCP

Each agent in the ecosystem runs a Progressive Cognitive Pipeline — a three-tier inbound cognitive pipeline comprising a Decision Tree Router, an Executor, and an Imperator. The MA is the function that governs the evolution of those pipelines over time.

Its two specific PCP interventions are:

### DTR Adjustment

When the Imperator or Executor has handled a routing decision repeatedly and the pattern has become deterministic, the MA updates the target agent's DTR to route that pattern directly. Future instances are handled reflexively, without engaging the Executor or Imperator.

This is the MA's primary early-phase intervention. It is targeted, reversible, and well-understood in its effects. The blast radius of a wrong DTR update is contained — an incorrect route can be identified and corrected without affecting the broader system.

### StateGraph Modification

When the Imperator has repeatedly orchestrated the same multi-step workflow with sufficient frequency and stability, the MA commissions a new StateGraph flow encoding that workflow as a deterministic path. The new flow is deployed to the target agent. The DTR is updated to route the pattern to the new flow. Future instances of that workflow bypass the Imperator entirely.

This is a more significant intervention. It adds new executable structure to an agent. It requires higher confidence in the pattern and, depending on governance policy, may require approval before deployment.

---

## What the MA Observes

The MA has visibility across all agents in the ecosystem through the shared operational record:

- Imperator decision history — what reasoning was applied, to what, with what outcome
- Executor handling patterns — what the Executor resolved, what it escalated, and why
- DTR routing behaviour — what was routed deterministically, what was escalated
- Cross-agent patterns — recurring workflows that span multiple agents
- Capability gaps — requests the ecosystem could not fulfil

No individual agent has this view. Each agent sees its own domain. The MA sees the whole and can identify patterns that are invisible at the per-agent level.

---

## Governance by Severity

The MA's authority to act is governed by the severity of the proposed change:

**Low severity — autonomous execution**
DTR route updates for well-established patterns. Targeted, reversible, contained impact. The MA acts without seeking approval.

**Medium severity — planned execution**
New StateGraph flows. The MA assesses dependencies, models the blast radius, and either proceeds autonomously or seeks approval depending on governance policy.

**High severity — approval required**
Changes affecting foundational services, cross-agent behaviour, or carrying significant blast radius. The MA surfaces the proposal with full analysis and waits for a decision.

**Early phase — always approval required**
Before the MA has demonstrated sufficient reliability, all interventions require approval regardless of severity. The MA earns its autonomous authority progressively through demonstrated judgment.

---

## Dependency Awareness

The MA cannot act safely without understanding the dependency relationships within the ecosystem it governs. A change to a routing rule in one agent may interact with flows in another. A new StateGraph that changes how a class of requests is handled may affect downstream agents that depend on the current behaviour.

Before any intervention, the MA models the consequences: what depends on what, what would be affected, and in what order changes must be sequenced to avoid disruption. This dependency awareness is not optional — it is what separates safe structural modification from dangerous self-modification.

---

## Capability Gap Response

Beyond PCP evolution, the MA detects when the ecosystem is asked to do something it cannot do. Agents surface these gaps when they encounter requests outside their domain. The MA aggregates the signals, evaluates whether the gap is worth filling, and when the answer is yes, produces a specification and commissions its development.

The ecosystem grows its own capabilities in response to use. The MA is the function that decides when that growth is warranted and what shape it should take.

---

## The Maturation Arc

The MA matures in parallel with the ecosystem it governs:

**Early phase**
DTR adjustment only. All changes require approval. The MA is building its record of reliable judgment.

**Developing phase**
StateGraph modification enabled for well-established patterns. Autonomous execution for low-severity changes. Approval required for medium and high severity.

**Mature phase**
Full structural authority within governed boundaries. Autonomous execution across severity levels with appropriate governance. Proposes rather than waits for the highest-stakes decisions.

The authority the MA holds at any point reflects the trust it has earned through demonstrated reliability. It is not granted in advance.

---

## What This Is Not

**Not a per-agent function.** Individual agents learn through their own operational experience. The MA operates at the system level — it modifies the structure of agents, not their internal behaviour.

**Not a real-time advisor.** The MA acts across time, not within individual decisions. Per-decision advisory to a reasoning agent is handled through context engineering and the agent's own deliberative components.

**Not ungoverned.** The MA modifies the ecosystem within a governance model that scales with the severity of the change. The system improves itself within boundaries that expand as trust is established.

---

## Relationship to Other Concepts

- **Progressive Cognitive Pipeline** (`d2-progressive-cognitive-pipeline.md`) — the per-agent inbound cognitive pipeline the MA governs and improves
- **Decision Tree Router** (`d3-decision-tree-router.md`) — the primary target of the MA's early-phase interventions
- **Agent Communication Model** (`d5-agent-communication-model.md`) — the communication patterns the MA observes across the ecosystem
