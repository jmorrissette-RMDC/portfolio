# Concept: Intent-Based Filesystem Management

**Status:** Concept **Date:** 2026-03-04
**Maturity:** Research Required

***

## Author

**J. Morrissette**

***

## The Problem with Permission-Based Access Control

Traditional filesystem access control is built around POSIX permissions: read, write, execute, assigned to users and groups via ownership and mode bits. This model was designed for a world of human users performing a bounded set of known operations on a relatively static set of files.

An AI agent ecosystem operates on a fundamentally different scale. Dozens or hundreds of agents, each with a distinct role, may perform millions of filesystem operations per day. Their actions are goal-driven, context-dependent, and often novel. The set of agents and roles grows over time. The appropriate access for a given agent depends not just on who it is, but on what it is trying to accomplish and why.

POSIX permissions cannot express this. `chmod` grants or denies access to a file for a user — it cannot understand that a `data_scientist` agent writing to `/storage/files/results.csv` should be redirected to `/storage/files/analysis-results/results.csv` because the organizational policy is to maintain a structured directory hierarchy. It cannot recognize that a `security_engineer` agent reading from `/storage/credentials/` is appropriate during a key rotation task but should be scrutinized in other contexts.

The result is either over-restriction (agents cannot do legitimate work) or over-permissiveness (agents are given broad access because fine-grained control is too cumbersome to maintain). Neither is acceptable.

***

## The Core Principle

Intent-Based Filesystem Management replaces the question "is this agent allowed to access this path?" with a richer question:

**"How does the intent of the policy drive decisions given the intent of the action?"**

This is the North Star of the model. Every access decision is a reconciliation of two intents:

-   **Policy intent** — the *why* behind the rule. A rule like "agents must not write files to the root of the general storage directory" exists to maintain organizational structure and prevent data sprawl. That intent, not just the literal rule text, governs how the decision is made.
-   **Action intent** — the *why* behind the request. An agent that provides an intent of "storing the output of a data analysis job" is making a meaningful statement about what it is trying to accomplish. That intent participates in the access decision.

When these two intents are in alignment, access is approved. When they conflict — even if the literal path is within a technically permissible scope — the system can deny, redirect, or challenge the request. When the action intent satisfies the spirit of a policy even if not its literal form, the system can approve with guidance.

This is not binary. The outcome of an access decision may be approval, denial, approval with a corrective suggestion, or deferral for further reasoning.

***

## Intent as a First-Class Input

Under this model, **intent is mandatory** for mutating operations (writes, deletes, moves). An agent cannot simply issue `write(path, content)` — it must provide a stated reason: `write(path, content, intent="Saving analysis output for the current task")`.

This has several consequences:

1.  **Accountability** — every mutation is accompanied by a stated reason, creating an auditable record of why agents took the actions they did.
2.  **Semantic policy enforcement** — policies can be expressed in terms of purpose, not just path patterns. "Do not write to the credentials directory unless the stated intent is key management" is a policy that cannot be expressed in any permission system but is natural here.
3.  **Guidance over rejection** — when a request is denied because the action's intent is valid but the path is wrong, the system can suggest the correct path rather than simply refusing. The agent is guided toward correct behavior rather than blocked.
4.  **Novel situation handling** — because decisions are made by reasoning about intent, the system can handle situations that no hard-coded rule anticipated. A policy's intent can be applied to circumstances the policy author never foresaw.

***

## Policy as Conversation

Under POSIX, policy changes require a human to modify file permissions — a low-level, brittle, and error-prone process. Under intent-based management, policies are managed through natural language. An administrator expresses a policy in plain terms:

>   "Always allow the security_engineer role read access to the credentials directory." "Never create files in the root of the general storage directory." "The data_pipeline role may write to any path within the projects directory."

These statements are translated into structured policy records and stored in a policy database. The database is queryable at high speed by the access decision layer. Policies can be added, modified, or revoked through further natural language interaction without restarting any service or editing any configuration file.

This approach — **Policy as Conversation** — is the natural evolution of Policy as Code for an AI-native environment. Where Policy as Code translates human intent into a declarative language, Policy as Conversation skips the intermediate language entirely. The system understands intent directly.

***

## The Decision Architecture

Access decisions are made by a two-tier system designed to handle the performance demands of high-volume agent operation:

### Tier 1: The Policy Router (Fast Path)

The vast majority of filesystem operations in any established system are routine: known agents accessing known paths for known purposes. Invoking deliberate LLM reasoning for every such operation is unnecessary and expensive.

A fast-path router — implemented as a Decision Tree Router (see `d3-decision-tree-router.md`) — classifies incoming requests against the policy database and learned patterns. For high-confidence matches it either approves or denies the operation immediately, without any LLM involvement. For low-confidence or novel cases, it defers to Tier 2.

This tier also enforces constitutional constraints: absolute denials that cannot be overridden by any policy or learned pattern. These sit before the router and execute unconditionally.

### Tier 2: The Policy Enforcement Agent

For deferred cases, a dedicated policy enforcement agent makes the deliberate access decision. This agent is not a general-purpose reasoner — it is tuned specifically for rule-following and structured policy evaluation. It receives the full context: the relevant policies and their stated intents, the requested operation, the path, the agent's role, and the stated action intent.

The agent evaluates the reconciliation of policy intent and action intent, produces a structured decision (allowed/denied, with reasoning and optional suggestion), and the operation is either executed or rejected accordingly.

This is intentionally a small, fast model. Policy enforcement does not require creativity or broad knowledge — it requires reliable, consistent rule application. The model selection reflects this.

***

## The Learning Loop

The system observes every access decision and builds a knowledge graph of access patterns. This graph models relationships between agent roles, file paths, operation types, stated intents, and decision outcomes.

A continuous background process queries this graph for statistically significant patterns:

-   Which (role, path, operation) combinations are repeatedly deferred to the agent and consistently approved?
-   Which paths are "hot" — accessed frequently by specific roles?
-   Has an agent begun accessing paths it has never touched before?

When the pattern detector finds a repeated approval pattern, it surfaces a proposal: a new fast-path rule that would handle future instances of this pattern without LLM involvement. The administrator can approve the proposal through natural language, and the policy database is updated.

This creates a feedback loop: the system becomes faster and more efficient over time as stable patterns are codified into the fast path, while the administrator maintains strategic oversight through natural language rather than low-level configuration. It should be noted that the administrator in this case may be a person, or it may be an LLM, or Quorum (b1-the-quorum-pattern.md) with higher reasoning.

***

## Why This Model is Necessary for AI Systems

Traditional access control assumes that the number of distinct actors and the variety of their actions are bounded and slow-changing — human users working within a defined set of roles. Humans can be trained, reminded, and disciplined. If a rule is ambiguous, a human can ask for clarification.

Agents cannot. They act at machine speed, at scale, and in combinations that no human could have fully anticipated when designing the access policy. An AI ecosystem running at full capacity may generate millions of filesystem operations per day. At that volume, it is not possible for a human to maintain control through hand-crafted permission rules — the agents will outstrip the human capacity to regulate them through hard-defined rules alone.

The solution is to manage at the level of **principles**, not rules. Instead of defining every permitted and forbidden operation explicitly, the administrator defines the *intent* of the governance: what the system is trying to protect, what it is trying to allow, and why. The system then applies those principles to every operation it encounters, including situations the administrator never specifically anticipated.

This is a fundamental shift from managing rules to managing goals. The administrator's role becomes that of a governance architect — defining the principles and reviewing the learning loop's proposals — rather than a ticket-taker for individual permission changes. The system scales human wisdom to machine speed.

***

## Relationship to Industry Concepts

This model synthesises and extends several established approaches:

-   **Intent-Based Networking (IBN)** — network administrators declare high-level business policies; the system translates them into low-level configuration. Intent-Based Filesystem Management applies the same philosophy to a different domain.
-   **Zero Trust Architecture** — every operation is authenticated and authorized regardless of source. No implicit trust. The intent requirement adds a context-aware layer beyond traditional ZTA.
-   **Policy as Code** — managing governance rules as structured, versionable artefacts. This model evolves toward Policy as Conversation: natural language policy expression with structured storage.
-   **Constitutional AI** — embedding governance principles into the system such that the governing agent can apply them to novel situations. The "intent of the policy" model is a practical implementation of this approach for filesystem governance.

***

## Known Limitations

**Cooperative assumption.** The intent-based model assumes agents state their intent honestly. An agent that declares a benign intent while executing a destructive operation would not be caught by intent reconciliation alone — the declared intent is what the system evaluates. As the ecosystem gains autonomy and the number of agents grows, the assumption of cooperative intent becomes worth examining. Malicious or compromised agents are outside the current design scope but are a consideration for mature deployments.

**Tier 2 at volume.** The Policy Enforcement Agent (Tier 2) involves LLM reasoning on every deferred decision. At high operation volumes, the LLM call becomes a bottleneck. The DTR fast path (Tier 1) is designed to handle the majority of decisions, but the efficiency of the system depends on the DTR learning to handle novel patterns over time. Until that learning matures, high-volume deployments will face latency and cost pressures on the deliberative tier.

***

## Relationship to Other Concepts

-   **Decision Tree Router** (`d3-decision-tree-router.md`) — the fast-path routing mechanism used in Tier 1 of the decision architecture
