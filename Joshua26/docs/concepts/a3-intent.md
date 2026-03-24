# Concept: Intent

**Status:** Concept
**Date:** 2026-03-06
**Maturity:** Implementable

---

## Author

**J. Morrissette**

---

## The Transformation

Language is linguistic probability. A sentence does not have a single fixed meaning — it has a distribution of probable meanings, shaped by context, history, relationship, and the statistical patterns of how humans use words to express what they want. This is not a flaw in language. It is what makes language infinitely expressive. Because it is grounded in probability rather than determinism, it is able to accommodate the infinite variations of the universe. It handles the unanticipated because it was never designed to handle only the anticipated.

Crucially, **ambiguity in linguistic expression is not an error. It is an uncollapsed probability distribution.** In a protocol-based system, ambiguity causes a crash — the system cannot proceed because the input does not match any anticipated pattern. In an intent-based system, ambiguity is information: a signal that the expression has not yet resolved to a single interpretation, which the system can surface and clarify rather than silently mishandle or fail.

Before the large language model, the gap between linguistic probability and machine-executable computation required the human to perform the translation manually: to take what they meant and express it in a form the machine could act on. Protocol. Schema. Command syntax. Each a lossy translation. Each capable of handling only what was anticipated when the protocol was designed. And when the expression was ambiguous, the machine crashed.

The large language model does not eliminate this gap — it bridges it. A tokenizer converts words to mathematical representations. A neural network runs probability calculations across those representations. The output is language again. The model has no goals. It is a mathematical probability machine. What makes it transformative is that it was trained on human language — which is saturated with goal-directed expression — so when linguistic input expresses intent and goals, the mathematical probability calculation over a model trained on that language tends to produce output that serves those goals. The goal-directedness is in the input and the training, not in the model itself.

This is the foundational capability on which agentic systems are built. It is not merely convenient. It is categorically different from what came before.

**Without this transformation, every unanticipated situation is an error. With it, any situation that can be expressed can potentially become action.**

### The Asimov Case

Isaac Asimov's Three Laws of Robotics are the canonical case study in why intent matters and what happens without it. The Three Laws are hard-coded rules — a protocol. They handle exactly what was anticipated when they were written. The universe then presents edge cases the programmer never foresaw, and the positronic brain fails: a robot told to "get lost" might literally disappear; a robot optimising to prevent physical harm might strip humanity of its freedom.

The Three Laws fail not because they are wrong but because they are literal. They encode the *what* without the *why*. They have no mechanism for reconciling the intent behind a command against the intent behind the rule. Every Asimov story is a case study in a governance system that cannot handle the gap between what was said and what was meant.

An agent with the ability to evaluate linguistic intent — to ask "what is this person actually trying to achieve?" and reconcile that against "what is this rule actually trying to protect?" — would handle these situations differently. Not with a crash. With a conversation. "I understand you want to achieve X, but doing Y violates policy Z because of its intent. Can I achieve X by doing W instead?" The Three Laws needed intent. They needed the transformation.

---

## What Intent Is

Intent is the semantic content that explains *why* — why an action is being taken, why a rule exists, why a particular kind of reasoning is being requested. It is the purposive dimension of an expression that distinguishes it from its literal form.

The *what* of an action is often self-evident: a write operation, a message, an inference call. The *why* is not. Two identical actions can have entirely different intents. A write to a credentials directory during a key rotation task and the same write from an unknown agent at an unusual time carry the same literal content and entirely different intents. A message that says "fix this" from a trusted collaborator and the same message after a series of escalating errors carry the same literal text and entirely different intents.

Intent is what provides the context that makes the right response to a situation determinable. Without intent, systems can only handle the anticipated. With intent, systems can reason about purpose — and purpose extends to every situation that can be expressed, not only those that were foreseen.

---

## Three Forms Intent Takes

**Action intent** — why is this being done? The agent or user stating what they are trying to accomplish. "I am storing the output of this analysis." "I need a key rotation to update the credential." "I want to understand the implications before proceeding." Action intent makes the purpose of a request auditable and evaluable.

**Policy intent** — why does this rule exist? The governance principle that explains what a constraint is protecting or enabling. "This rule exists because unstructured writes to shared storage produce data sprawl." "This constraint exists because credentials must be managed through approved processes." Policy intent makes governance principles applicable to situations the policy author never specifically anticipated.

**Goal intent** — what outcome is the requesting party ultimately trying to achieve? The higher-level objective that the immediate request serves. Distinguishing goal intent from action intent is what enables guidance over rejection: an agent that knows what you are trying to achieve can suggest a better path rather than simply refusing the path you chose.

---

## Why Intent Matters: The Governance Problem

Traditional access control handles what was anticipated. A rule specifies a condition; the system checks whether the condition is met; the action is permitted or denied. This works when the set of anticipated situations is complete — which it never is at scale.

An agentic ecosystem operating at full capacity generates millions of operations per day across dozens of agents with distinct roles, in combinations that no governance architect could fully anticipate. Rigid rule sets either over-restrict (blocking legitimate novel work) or over-permit (broad access granted because fine-grained control is too cumbersome). Neither is acceptable.

The alternative is to govern at the level of principles rather than rules. Instead of specifying every permitted and forbidden action, governance expresses the *intent* of the governance: what the system is trying to protect, what it is trying to enable, and why. The system then applies those principles to every operation it encounters — including situations the governance architect never specifically anticipated — by reconciling the intent of the action against the intent of the policy.

**The North Star of intent-based governance: how does the intent of the policy drive decisions given the intent of the action?**

When these two intents are in alignment, action proceeds. When they conflict — even if the literal action is technically permissible — the system can challenge or redirect. When the action intent satisfies the spirit of a policy even if not its literal form, the system can approve with guidance. The outcome is governance that scales to novelty because it reasons about purpose rather than matching patterns.

---

## Intent at Every Level of an Agentic System

Intent is not specific to governance. It is the mechanism by which the transformation from linguistic probability to mathematical probability is made purposeful at every level of the system.

**At the routing level.** A Decision Tree Router classifies incoming requests by structural pattern. It does not understand intent — it matches what it has seen before. The Executor tier that follows it exists precisely to handle what the DTR cannot: requests whose correct handling depends on understanding what they are trying to accomplish. The Executor reads intent from prose and routes accordingly. Intent is the line that distinguishes what the DTR can handle from what requires deliberation.

**At the communication level.** When an agent receives a message, the receiving moderator evaluates the intent of the message — what is it trying to accomplish? Who is it obligated to? — and routes accordingly. The distinction between To and CC is an intent distinction: "I expect a response" versus "you may contribute if relevant." Intent governs how messages are handled.

**At the inference level.** When an agent calls an inference alias, it is expressing a rational intent about what kind of reasoning is needed. The alias is the encoded form of that intent — the purposive configuration of a model invocation. The Inference Broker parses that intent and generates the inference that serves it. The quality of inference depends on how precisely the intent is expressed and how well the alias serves it.

**At the governance level.** Policy intent and action intent are reconciled for every consequential operation. The system evaluates not just what is being done but why — against not just what is permitted but why the permission structure exists. This enables governance to extend to the unanticipated.

**At the interaction level.** The Imperator receives goals expressed in natural language. Understanding the intent behind a request — not just its literal content — is what enables the Imperator to handle ambiguity, ask clarifying questions, suggest better paths, and take appropriate action. Without intent, every unclear request is an error. With it, ambiguity is a conversation.

---

## Intent as the Learning Signal

When intent is recorded alongside outcomes, the training signal is richer than request plus response. The why of an action and whether it achieved its why — this is the data that enables semantic understanding to improve.

A routing decision recorded as "agent X requested operation Y and received outcome Z" is useful training data. The same decision recorded as "agent X, intending to achieve A, requested operation Y, which resulted in Z, where A was/was not achieved" is dramatically richer. It captures the purpose-outcome relationship that allows the system to learn what kinds of intent lead to what kinds of results — and to route, evaluate, and respond better in future.

Requiring stated intent for consequential actions is not only a governance mechanism. It is a data collection mechanism that feeds the ecosystem's learning loops. Every expressed intent, evaluated against its outcome, is a training example for the system that handles future expressions of similar intent.

---

## Intent Requires the Transformation

None of this is possible without the foundational transformation from linguistic probability to mathematical probability. Stating intent in natural language is only useful if a system can receive that natural language, extract the semantic content, and convert it into something that can be evaluated, routed, and acted upon.

This is what the large language model does. The Imperator that receives a natural language goal, the Executor that reads the semantic intent of an incoming message, the Inference Broker that parses rational intent from an alias call, the policy enforcement agent that reconciles action intent against policy intent — all of these depend on the same foundational capability. The LLM is not a chatbot bolted onto an otherwise normal system. It is the engine that makes intent actionable throughout the architecture.

The transformation is what makes prose over protocol possible. The transformation is what makes governance at the level of principles rather than rules possible. The transformation is what makes the unanticipated handleable rather than an error.

Intent is the concept. The LLM transformation is the mechanism. Together they are why agentic systems can do things that protocol-bound systems fundamentally cannot.

---

## Relationship to Other Concepts

- **Intent-Based Filesystem Management** (`d7-intent-based-filesystem-management.md`) — the clearest concrete instantiation of intent-based governance; the reconciliation of policy intent and action intent applied to filesystem operations
- **MAD Pattern** (`a5-the-mad-pattern.md`) — prose over protocol: the Imperator understands intent where protocol cannot; the transformation from observation-based to mathematical probability is what makes the MAD pattern's semantic interface possible
- **Progressive Cognitive Pipeline** (`d2-progressive-cognitive-pipeline.md`) — intent is precisely what the DTR cannot evaluate and what the Executor tier exists to handle; the line between tiers is the line between pattern matching and intent understanding
- **System 3 ReAct** (`d1-system-3-react.md`) — the Conversation Engine places conversation at both ends of the reasoning loop; intent flows in as natural language and out as purposeful action; the LLM performs the transformation at the Reasoning Engine
- **Inference Broker** (`c2-the-inference-broker.md`) — the alias is the encoded form of rational intent; the Inference Broker parses intent and generates the base state of current cognition from it
- **Agent Communication Model** (`d5-agent-communication-model.md`) — To vs CC semantics are intent distinctions; the receiving moderator evaluates message intent to determine routing
- **Ecosystem Learning** (`b2-ecosystem-learning.md`) — intent recorded alongside outcomes is the richest training signal available; requiring stated intent is both governance and data collection
- **Agent Purpose and Identity** (`a4-agent-purpose-and-identity.md`) — purpose is the long-term form of intent; an agent's purpose is its persistent intent across its entire existence
