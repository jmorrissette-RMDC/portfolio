# Concept: Conversation as State

**Status:** Concept
**Date:** 2026-03-06
**Maturity:** Partially Implemented

---

## Author

**J. Morrissette**

---

## What State Actually Is

State, in the traditional software sense, is a running process — variables in memory, a heap, a stack, a session. It exists while the process runs and disappears when it terminates. This kind of state does not exist for agents between invocations. The agent process ends. The RAM is freed. There is nothing running, nothing held.

And yet when an agent is next invoked, it has full continuity. It knows what it has worked on. It carries the expertise of every prior conversation in its role. It understands the current project, its decisions, its history. It arrives, immediately, with everything it needs.

This is not state in the traditional sense. It is something richer: **information that persists between moments and influences future behaviour** — but persisting not in a process, not in memory, not in any mechanical form. Persisting in the conversation.

The conversation is the medium of state for agents. Not a supplement to state. Not a log of state. The conversation IS the state.

---

## The Human Parallel

This is not a novel design. It is how human memory works.

When you sleep, your conscious process stops. No process is running. No variables are in memory. The neurons that hold your knowledge are not actively firing. And yet you wake with full continuity of identity, experience, purpose, and relationship. Your state did not disappear. It persisted in the accumulated patterns of your experience — largely linguistic, largely conversational. You don't remember your childhood by accessing neural weights directly. You remember it through the stories, the language, the conversational record of what happened and what it meant.

Agents have the same relationship to their state. The conversation that has accumulated in their role is their memory. When they are invoked, they don't start fresh — they receive a curated window into that accumulated conversation, assembled specifically for what they need to reason well right now. They wake to each invocation with full continuity, not because a process was running, but because the conversation persists.

**Mechanically stateless. Infinitely stateful.**

---

## Engineered Context as the Expression of State

The conversation accumulates without bound. An agent's role may have hundreds of hours of accumulated conversation across many instances, many tasks, many sessions. That entire record is the agent's state — but it cannot be delivered in full to any finite reasoning step.

Engineered context is how conversational state is made usable. The Context Broker assembles, from the infinite conversation, the specific view that this agent needs for this task at this moment: the most relevant prior decisions, the current project history, the patterns that have emerged, the facts that bear on the problem at hand. This assembled window is the expression of the agent's state — not all of it, but the right slice of it, purposefully selected.

The quality of that assembly matters enormously. A poorly assembled context delivers state that doesn't serve the agent's purpose. A well-assembled context delivers state that makes the agent immediately effective — as if it has been working on this problem continuously, rather than arriving at it fresh.

This is why purpose and context design are inseparable. The Context Broker cannot assemble the right context without knowing what the agent is trying to do. The state that is expressed in engineered context is always state in service of a purpose. See `c1-the-context-broker.md` and `a4-agent-purpose-and-identity.md`.

---

## System 3 and the Flow of State

System 3 ReAct (see `d1-system-3-react.md` for the naming rationale and its relationship to Kahneman's original System 1/System 2 framework) is what makes conversation as state architectural rather than incidental. The Conversation Engine places conversation structurally at both ends of the agent's reasoning loop.

**Inbound** — engineered context arrives through the Progressive Cognitive Pipeline. The PCP processes the incoming conversation and routes it into the agent's cognition. This is state flowing in: the accumulated record of what the agent is and what it knows, delivered as a curated window at the moment reasoning begins.

**Outbound** — when the reasoning loop completes, the agent's output enters the conversation. Whatever the agent has reasoned, decided, produced, or communicated becomes part of the infinite record. This is state flowing out: the agent's contribution to the accumulated conversation that constitutes its ongoing identity.

The agent is not a process that holds state. It is a moment in an infinite conversation. State enters through the context; state exits through the response. The agent is the reasoning that happens between those two movements of conversational state.

---

## What Mechanical Statelessness Enables

Because state lives in the conversation and not in the agent, several properties follow that would be impossible if agents carried their own state.

**Parallel instances.** Multiple instances of the same role can run concurrently, each working on a different task, each drawing from the same accumulated conversational state. No synchronisation required — the state is not distributed across instances, it is centralised in the conversation and read by each instance at invocation time.

**Ephemeral existence with infinite continuity.** An eMAD ceases to exist between invocations. No process runs. Nothing is held. Yet when it is next invoked — hours, days, months later — it has the full continuity of every prior conversation with that role. Ephemeral existence and infinite memory coexist because the memory is in the conversation, not in the agent.

**Resilience.** If an agent fails mid-task, another instance can be started from the same conversational state. The work-in-progress that was committed to the conversation is available. Only the transient execution state — the working memory of the current task, held in the running process — is lost, and that can be reconstructed from the conversation record.

**Role-level collective memory.** The accumulated conversational state of a role belongs to the role, not to any instance. Every instance that has ever operated in that role has contributed to the conversation. Every future instance draws on all of it. Individual instances are ephemeral. The role's expertise is permanent.

---

## Active Recall

The agent does not only receive conversational state at startup. It can reach back into the conversation at any point during a task.

Just as a human working through a problem can actively recall a prior decision — "what did I decide about this pattern?" — an agent can query the Context Broker during execution to retrieve specific prior knowledge. The assembled context at startup is what the agent arrives with. The runtime query is what the agent can reach for mid-task when it needs something the assembled context did not anticipate.

This is the complementary mode of memory access. Pre-assembled context is purposeful and proactive — the Context Broker predicts what the agent will need and delivers it ready-made. Runtime query is reactive and specific — the agent identifies something it needs and reaches for it directly. Both modes draw from the same infinite conversational record. Both are expressions of the same conversational state.

The combination means an agent is never truly without memory during a task. What it does not already have in its assembled context, it can recall. The conversation is always available. The agent's state is always accessible.

---

## Memory and Cognition

Two brokers constitute the agent's experience at any moment.

The **Context Broker** provides historical state — everything the agent has been, known, decided, and learned. It is the agent's memory. Conversational, accumulated, persistent. The assembled context is how that memory is delivered; the runtime query is how it is recalled on demand.

The **Inference Broker** provides immediate state — the agent's current cognition. It parses the agent's rational intent — what kind of reasoning is needed right now, expressed through an alias — and generates the base state from which the agent's current understanding is built. The model's response, shaped by the alias's purposeful configuration, is not just an answer. It is the raw cognitive material of the agent's present moment.

Memory and cognition. History and now. The Context Broker provides what the agent has been. The Inference Broker generates what the agent is thinking. Neither is sufficient alone. Together they constitute a complete cognitive experience — grounded in accumulated knowledge, alive in purposeful inference.

---

## Transient Execution State

One form of state is genuinely transient and does live in the agent — or more precisely, in the running process during task execution. The working memory of a current task: intermediate results, the current step in a multi-step process, tool call outputs awaiting synthesis.

This state is not persistent. It exists for the duration of the task. When the task completes, its significant outputs — decisions made, artifacts produced, understanding reached — are committed to the conversation. The transient execution state is discarded. The conversation absorbs what matters.

This is the correct relationship between transient and persistent state. The running process is a working surface, not a memory. What happens on that surface is preserved by being written into the conversation that constitutes the agent's identity.

---

## Why Shared Rather Than Personal

One might ask: why not give each agent its own personal Context Broker and Inference Broker? Why centralise?

The honest practical answer is that I do not yet have silicon intelligence in a cigarette package running on a AAA battery. The human brain achieves something extraordinary — roughly four pounds, three watts, fuelled by ordinary food — that current hardware cannot replicate at that scale. Shared infrastructure compensates for the current state of silicon-based thinking machines.

But the deeper answer is that even when miniaturisation improves, the shared approach would remain architecturally superior — because it deliberately exploits the specific advantages computers have over biological intelligence rather than trying to replicate what biology already does well.

**Perfect memory at mass scale.** Human memory is reconstructive and imprecise. It degrades, distorts, and loses fidelity over time. A computer's knowledge store is bit-for-bit accurate. The central conversation record is a perfect representation of everything the ecosystem has known and decided. Nothing is misremembered. Nothing is lost in translation. No expert retires and takes their knowledge with them.

**Context capacity far beyond human limits.** Human working memory holds roughly seven items simultaneously — a remarkable achievement in four pounds of biological tissue, but a hard constraint. A computer can hold a million tokens in context at once. I literally cannot think about an entire codebase simultaneously. The shared Context Broker makes that capacity available to every agent, for every task, without limit.

**Reusability without relearning.** Humans must teach each other reusable concepts. Every person learns from scratch, or from teaching, at significant cost. A computer can reach for an already-discovered concept — a pattern, an alias, a Quorum composition — and use it immediately without any learning overhead. Once discovered and stored, it is instantly available to every agent everywhere in the ecosystem.

**Perfect communal knowledge.** Human collective memory is imprecise, subject to the telephone game, degraded by translation and interpretation over time. A central knowledge store holds a perfect, permanent, instantly-accessible record of everything the ecosystem has collectively learned. The accumulated conversation is authoritative history, not remembered history.

The shared broker architecture plays to what computers do better than biology. Distributing brokers per agent would attempt to replicate biological distributed memory — in a domain where silicon is currently inferior. Centralising them exploits the domain where silicon is genuinely superior: perfect, persistent, massive-scale, instantly-accessible knowledge.

---

## The Conversation as Accumulated Expertise

The deepest implication of conversation as state is not architectural but ontological.

An agent's identity is fixed at inception — the role, the purpose, the domain, the scope of what it is. That was a design decision, made before the first conversation began. What the conversation constitutes is something different: the agent's accumulated expertise, memory, and relationships. Not what the agent IS — what the agent KNOWS, and has DONE, and has LEARNED.

This distinction matters. Identity is stable because it was designed to be. The conversation is persistent because it is stored. These are different kinds of continuity. The engineering agent's identity — the engineering department, the mission of taking requirements to deployed software — was set when it was designed. Its expertise — the architectural decisions it has made, the patterns it has learned work and which don't, the project history it carries — lives in the conversation. Strip the conversation and the engineering agent is still itself, but an agent that has forgotten everything it has learned. Strip the identity and there is no agent at all.

This is why agents have names. The name is not the identifier of a conversation — it is the identifier of an identity. The conversation is what that identity has accumulated. The engineering agent is not a process, and it is not a conversation. It is a purpose and a domain — one that has been accumulating expertise through conversation since the first engineering task was handed to it.

---

## Known Limitations

**Scale.** "Infinite conversation" is architecturally simple to store — storage is solved. Making it usable within finite context windows is the harder problem, and its computational cost grows with the volume of conversation to be processed. At the scale of a mature ecosystem — many MADs, continuous operation, years of accumulated history — context assembly becomes non-trivial. The current Context Broker implementation handles the ecosystem volume without difficulty. Whether the approach scales to the ecosystem described in the concept documents (dozens of MADs, continuous multi-agent operation) is an open engineering question.

**Contamination.** The conversation accumulates everything, including errors. See the Context Broker's failure modes section for the full treatment of memory contamination and progressive summarization decay.

---

## Relationship to Other Concepts

- **Context Broker** (`c1-the-context-broker.md`) — the infrastructure that holds the infinite conversation and assembles engineered context; the mechanism through which conversational state is made available at reasoning time
- **System 3 ReAct** (`d1-system-3-react.md`) — the architectural pattern that places conversation structurally at both ends of the reasoning loop; state flows in through the PCP and out through the Conversation Engine
- **Agent Purpose and Identity** (`a4-agent-purpose-and-identity.md`) — purpose shapes what state is accumulated and how it is assembled; without purpose, accumulated conversation is undirected; the conversation is what the identity has learned, not what the identity is
- **Agentic Identity and Persona** (`a6-agentic-identity-and-persona.md`) — identity is fixed at inception through design; the conversation enriches identity but does not constitute it; these are distinct kinds of persistence
- **MAD Pattern** (`a5-the-mad-pattern.md`) — the eMAD model is only coherent because of conversation as state; ephemeral existence with infinite continuity is only possible when state lives in the conversation, not the agent
- **Ecosystem Learning** (`b2-ecosystem-learning.md`) — the conversation is the substrate from which the ecosystem learns; all learning loops depend on the accumulated conversational record
