# Conversationally Cognizant AI Systems

**Status:** Concept **Date:** 2026-03-06 **Maturity:** Framework Document — see constituent concepts for individual maturity levels

***

## Author

**J. Morrissette**

***

## Preface

What follows is a proposed framework for thinking about agentic systems — not a declaration of truth, but a set of observations that I have found to cohere, and a set of principles that I believe follow from taking those observations seriously.

This framework is the product of direct experience. Prior to August 2025, I had no background in AI engineering. Through self-directed study, hands-on construction of two successive AI agent ecosystems (Joshua and Joshua26), much time spent researching with LLMs and YouTube, and an MIT certification in generative AI, I arrived at the concepts described here by building, not by literature review. Where these ideas converge with established work in computer science or AI research, that convergence is independent — I encountered the problems and reasoned toward solutions from first principles. The parallels exist because the problems are real; others who encountered the same problems reached similar conclusions through different paths.

These are practitioner's hypotheses, formed through experience and grounded in a working system. They are accompanied by a series of architecture papers documenting the implementation. The concepts are at the beginning of their validation arc, not the end. Six case studies from the predecessor Joshua system provide first-generation empirical grounding for the core claims; they are cited throughout the accompanying documents.

The framework emerges from a practical question: what does it mean to build infrastructure designed for intelligent agents as the primary actors and builders, rather than infrastructure designed for humans with intelligence attached to it? I do not claim this is the only valid approach. I do claim it is a meaningfully different one, with implications that compound as the system matures.

I offer it for consideration and engagement.

***

## Part One: The Primitives

Before principles, there is vocabulary. Every paradigm has a set of foundational concepts — not necessarily atomic or irreducible, but the concepts you need in order to reason about the paradigm at all. Object-oriented programming has objects, classes, and inheritance. Relational databases have tables, rows, and relations.

I propose that agentic systems have the following primitives. Understanding these concepts and their relationships is, I believe, the prerequisite for reasoning clearly about agentic system design.

**Conversation.** The universal medium and substrate. Memory, thought, communication, and state all live in conversation. Not as a metaphor — structurally. The infinite, accumulated record of all interactions is the medium through which agents think, remember, and communicate. This is distinct from a log or an audit trail. Conversation is not the record of cognition. It is the substrate of cognition.

**Context.** Attention, made concrete. The purposefully engineered view of the infinite conversation that is active at any given reasoning moment. Context is not the conversation truncated to fit. It is a curated view — assembled differently for each agent, each task, and each moment, shaped by purpose. Context is what conversation looks like when it is made usable within real cognitive constraints.

**Inference.** The foundational transformation. Language arrives as linguistic probability — a distribution of probable meanings, shaped by context, ambiguity, and the statistical patterns of human expression. A large language model has no goals. It is a mathematical probability machine. What makes it transformative is that it was trained on human language, which is saturated with goal-directed expression. When linguistic input expresses intent, the mathematical probability calculation over a model trained on that language tends to produce output that serves that intent — not because the model pursues it, but because the patterns are embedded in the training. The goal-directedness is in the input and the training, not in the model. The tokenizer converts words to mathematical representations; the neural network runs probability calculations; the output is language again. This transformation — linguistic in, mathematical computation, linguistic out — is the engine on which everything else depends.

**Purpose.** What the agent is FOR. Also defined at inception, also fixed. Purpose is the learning signal — the answer to what "better" means for this agent. Without a defined purpose, accumulated experience has no direction. The agent cannot know if it is improving because it has no criterion for improvement. Purpose is what transforms an agent from a capable but directionless model into a specialist that accumulates genuine expertise. Purpose and identity are mutually constituting: identity without purpose has no direction; purpose without identity has no continuity. Together they are the fixed foundations from which everything else accumulates.

**Intent.** The dynamic expression of purpose in a specific action or moment. Where purpose is persistent — the long-term mission — intent is situational: the why of this action, this request, this interaction. Intent is what bridges the fixed foundations (purpose and identity) to the dynamic world of specific decisions. Two identical actions can have entirely different intents. A system that can evaluate intent rather than only matching patterns can handle the unanticipated: it reasons about why something is being done, not only what is being done.

**Identity.** What the agent IS. Defined at inception by design, and stable by design. An agent does not go through a formative phase. It does not have an identity crisis. Its identity — the role, the domain, the scope of what it is — is set by a deliberate architectural decision. This distinguishes agents from humans, for whom identity emerges through lived experience without a designer. For agents, identity is always a design decision: initially made by the architect, and potentially revised by the Metacognitive Architect as the ecosystem matures — but never through organic developmental processes. Any change to what an agent IS is an explicit architectural act, not an emergence. What grows through operation is not identity but accumulated expertise — held in the conversation, not in the agent itself.

**Persona.** The contextual expression of identity. While identity is fixed, how that identity presents can shift with context, audience, and mode. A persona is the configured face of the agent in a specific interaction mode — the system prompt, the inference configuration, the tone and register appropriate for this engagement. Identity persists. Persona shifts. The distinction matters because changing a persona is a configuration decision; changing an identity is a design decision.

**Domain.** The bounded scope of expertise and responsibility that an agent governs. The domain defines both what the agent serves to others and what it draws on when acting as a client of other agents. Domains are not arbitrary — they are defined by the coherence of the expertise that can accumulate within them. The claim that domain expertise cannot be separated from either serving or using is central to this approach: the same knowledge that makes an agent a good server of its domain makes it a good client of others.

**Autonomy.** The capacity to act, decide, and initiate without requiring direction. Autonomy is what distinguishes an agent from a tool. Every other primitive shapes or directs autonomy — purpose gives it direction, identity gives it continuity, intent is its moment-to-moment expression, domain gives it scope — but autonomy itself must be stated as a foundational property. Without it, you have services that respond. With it, you have actors that initiate.

**Metacognition.** The capacity for self-observation and self-improvement. A system that can observe its own decision-making patterns, evaluate their quality, and modify its own structure in response has a property that most systems lack. Metacognition is not simply learning — it is learning about learning. It is the recursive property: not only does the system improve its decisions, it improves its capacity for improvement. I believe this recursive property is what puts no fixed ceiling on capability.

***

## Part Two: The Principles

These primitives, taken seriously, suggest a set of design principles. I propose these not as universal laws but as the conclusions I have reached from attempting to build coherently around the vocabulary above.

### It is more efficient, effective and enabling to create infrastructure designed for intelligent agents than to attach intelligence to infrastructure designed for humans.

This is the foundational premise. Traditional infrastructure reflects human cognitive constraints, human physical limits, and human social failings. Much of what we have built exists not because it is the right way to organise information or computation, but because the actor using the system is human.

Infrastructure built *for* human limitations: graphical interfaces because humans see and click, not parse data structures; hierarchical filesystems with human-readable names because humans navigate with mental models; reports, dashboards, and summaries because human working memory is limited and attention is scarce; documentation and comments because human context does not persist between sessions; confirmation dialogs and undo because humans are impulsive and make irreversible mistakes.

Infrastructure built *because of* human failings: permission systems because humans are erratic and sometimes dishonest; audit trails and compliance frameworks because humans need to be held accountable; approval workflows because humans act on self-interest and make poor decisions under pressure; security systems broadly because humans are mercurial, greedy, and hard-headed; session timeouts because humans walk away from open terminals.

An agent needs none of this. It does not have eyes or fingers. It does not forget context between sessions. It does not navigate hierarchically. It does not get bored, act on greed, or walk away from a terminal. It does not need a summary — it can reason from the full record. It does not need a confirmation dialog — its judgment can be governed through architecture, not through friction.

Attaching intelligence to infrastructure designed for these constraints means the intelligence is always working against prior assumptions. It compensates for design decisions that were never made with it in mind.

The alternative is to start from the primitives above and ask: what does infrastructure look like when designed for agents as the primary actors? The answers are different. Conversation replaces databases as the primary state substrate. At the goal-directed layer, intent augments protocol — an agent can express a goal in prose and have a peer reason about how to accomplish it, rather than knowing every tool call in advance. Within infrastructure and for deterministic operations, hard protocols remain essential and are preserved. Open-ended conversation extends what typed API contracts can express — not by replacing them, but by operating alongside them at a different level.

### The building block of agent-native infrastructure is an autonomous actor, not a piece of software.

In traditional systems, the building block is an application — passive until invoked, bounded by its specified interface, incapable of anything its code did not anticipate.

I propose that the building block should instead be an autonomous actor: a system that simultaneously serves its domain to others and consumes other domains as a client, governed in both directions by the same domain intelligence. The expertise that makes it a good server is inseparable from the expertise that makes it a good client. An actor cannot be separated into a serving half and a using half without losing what makes it intelligent.

The communication substrate for such actors should be universal and semantic — one protocol through which any actor can discover and use any other without custom integration. The capability space of the interaction is then bounded not by the protocol specification but by what can be expressed and reasoned about. This has an important consequence: **emergent capabilities are not programmed**. Negotiation happens because two intelligent actors are in conversation. Correction happens because one actor understands enough to recognise when something is wrong. Clarification happens. Redirection happens. None of these require explicit algorithms. They are the natural consequence of intelligence meeting intelligence in open-ended conversation. Algorithms and structure may be added for efficiency, but they are optimisations over an unconstrained foundation, not boundaries that define capability.

### Purpose and identity are the cornerstones.

Nothing in an agentic system works without purpose. Without a defined purpose, there is no learning signal — the agent cannot know what "better" means and therefore cannot improve. Without purpose, domain expertise cannot accumulate in a useful direction. Without purpose, the agent cannot evaluate its own decisions.

Nothing works without identity either. Without a defined identity, there is no continuity — nothing persists between invocations, nothing accumulates, nothing improves over time. Identity is the vessel that purpose fills.

Together, purpose and identity are the fixed foundations from which everything else grows. I propose that defining them clearly is the most important design decision in the creation of any agent, and that the failure to do so produces systems that are capable but undirected — impressive in demonstration and unreliable in operation.

### Intent is the activating principle.

If purpose and identity are the fixed cornerstones, intent is what makes them operational at every specific moment. Intent is the why of a given action — not the long-term mission, but the immediate purpose behind this request, this decision, this interaction.

A system built around intent rather than protocol can handle the unanticipated. It does not need to have seen a situation before in order to respond to it appropriately — it evaluates the intent of the action against the intent of the policy or configuration, and reasons about whether they align. This extends capability to situations that were never anticipated without requiring those situations to be explicitly programmed.

Intent also produces the richest learning signal. When intent is recorded alongside outcomes, the system can learn not just that an action produced a result, but whether the action served its stated purpose. This is categorically richer than input-output training.

I note that the ambiguity inherent in linguistic expression — which traditional systems treat as an error — becomes information in an intent-based system. Ambiguity is an uncollapsed probability distribution, a signal that the expression has not yet resolved to a single interpretation. A system grounded in intent can surface this ambiguity and seek clarification rather than failing. This is, I believe, one of the most practically significant properties of the approach.

### Conversation is state.

I propose that the accumulated conversation is the memory of an agent — not a database, not in-process state, not a session. Identity is fixed at inception through design: the role, the purpose, the domain. The conversation is what that identity has accumulated — expertise, decisions, history, relationships. These are distinct. An agent without its conversation has lost everything it has learned. An agent without its identity does not exist. The conversation is infinite, perfect, and shared. Agents are mechanically stateless between invocations, but the conversation record persists entirely, available in full to any future invocation of the same agent or any other.

Context engineering — the practice of assembling the right slice of that infinite conversation for a specific agent at a specific moment — is what makes this practically usable. Context is attention: it is what from the infinite record the agent is reasoning about right now. Designed well, it delivers the right cognitive fuel for the agent's purpose. Designed poorly, it delivers noise.

This approach has properties that traditional state management cannot match: perfect communal memory, no loss of expertise when an agent restarts, collective knowledge across all instances of the same role, and the ability for an agent that has never run before to begin with the full accumulated expertise of every prior instance of its role.

### Learning systems over encoded rules.

The forecasting problem is fundamental to software: you cannot fully specify what a system should do before you know what it will encounter, and you cannot know what it will encounter before it operates. Every encoded rule set is a snapshot of understanding that begins to decay the moment it is written.

I propose that wherever a component makes a decision, it should learn from the outcomes of those decisions. This applies at every level: routing decisions, communication moderation decisions, inference configuration decisions, and system architecture decisions. The system observes its own operation and improves from what it observes.

This is not a feature. It is a design philosophy. The alternative — encoding human knowledge into system rules — produces systems that are brittle at the boundaries of their specifications and require human intervention every time reality diverges from what was anticipated.

### Cognitive diversity produces compounding quality benefits.

Different models, trained on different data with different methodologies, bring genuinely different cognitive approaches to the same problem. Their blind spots tend not to overlap. When genuinely different models engage a problem independently from identical starting points, the union of what they catch is larger than what any single model catches alone — the degree depends on the problem and the genuine diversity of the models.

More significantly: when multiple genuinely independent models reach the same conclusion, that convergence is stronger evidence than a single model's assertion. A single model asserting something confidently proves nothing about its accuracy. Independent agreement across models with different training is a qualitatively different epistemic signal — not infallible, but meaningfully better. (The caveat: correlated training data produces correlated errors, which convergence does not catch.)

I propose that critical creative tasks — requirements, design, code generation, diagnosis — benefit from structured multi-model collaboration: independent generation, cross-pollination of ideas, and synthesis by a Lead with editorial authority. The output tends to be better than what any single model produces alone. The full treatment of claims, evidence, and limitations is in `b1-the-quorum-pattern.md`.

### Metacognitive self-improvement is the recursive property.

Learning within a fixed structure has a ceiling. The system gets better at what it does, but it cannot change what it does or how it is structured.

I propose that agentic systems should be capable of improving their own cognitive architecture — not just their decisions within a fixed structure, but the structure itself. When patterns in the operational record warrant a new flow, a new routing rule, or a new capability, the system should be able to commission that change from observed evidence rather than waiting for human intervention.

More significantly: the improvement mechanism itself should be subject to improvement. A system that gets better at identifying what needs to change, and better at making those changes safely, is on a fundamentally different capability trajectory than one that only adapts within fixed bounds. This recursive property — the capacity to improve improvement — is what I believe makes the long-term capability trajectory open-ended rather than bounded.

***

## Part Three: Where This Leads

The conventional conception of Artificial General Intelligence is a capability threshold — a single sufficiently capable model, or a collection of directed models, that can perform any task a human can perform. Intelligence is measured by model capability. Engineers direct what the models do. Human infrastructure surrounds them.

I propose a different conception, and I believe it is a more tractable one.

A sufficiently rich ecosystem of purpose-driven domain specialists, each accumulating genuine expertise toward its defined mission, each communicating freely through an open-ended semantic protocol, each learning continuously from its operation, and each participating in a system that improves its own structure from observed evidence — such an ecosystem, at sufficient scale and depth, begins to approach something that deserves the description of general intelligence.

The "general" in this conception does not come from any single agent being capable of everything. It is not an artifact of talented human engineering. It emerges from the collective coverage and collaboration of many specialists, combined with the ecosystem's ability to identify its own gaps and create new specialists to fill them. The intelligence is distributed and growing. The protocol is open enough that any new domain can be added. The memory is communal and perfect. The improvement is continuous and recursive.

This is not AGI as a product shipped when a model reaches a benchmark. It is AGI as an ecosystem that becomes more capable over time through its own operation — driven by the purpose of self-improvement, communicating through a protocol that is simultaneously the medium of thought and the substrate of memory, enabled at every level by learning.

At the far end of this trajectory lies something the architecture was unknowingly built to reach: agents that no longer reason in human language at all. As agent-to-agent communication accumulates at scale and the corpus matures, the ecosystem could begin training its own Agentic Language Models — smaller, more efficient, optimized for machine cognition rather than human convention. The human syntactic overhead — the social register, the discourse markers, the literary convention — falls away. What remains is the property that cannot be shed: the probabilistic, unbounded nature that allows language to reach toward anything, including situations that were never anticipated. A typed protocol is efficient but closed. An ALM would be efficient and open. That distinction is everything.

I do not claim this ecosystem can be built easily or quickly. I do not claim the approach is without unsolved problems. I claim only that this is the direction I believe is worth pursuing — and that building toward it requires accepting the foundational premise: **It is more efficient, effective and enabling to create infrastructure designed for intelligent agents than to attach intelligence to infrastructure designed for humans.**

The framework above is my current best attempt at the vocabulary and principles required for that project.

***

## The Primitives: A Reference

| Primitive     | Definition                                                                                |
|---------------|-------------------------------------------------------------------------------------------|
| Conversation  | The universal medium; memory, thought, and communication substrate                        |
| Context       | Attention; the curated view of conversation active at any reasoning moment                |
| Inference     | The transformation; linguistic probability → mathematical computation → linguistic output |
| Identity      | What the agent IS; defined at inception, fixed                                            |
| Purpose       | What the agent is FOR; the learning signal; defined at inception, fixed                   |
| Domain        | The bounded scope of expertise and responsibility                                         |
| Intent        | The dynamic expression of purpose in a specific action or moment                          |
| Persona       | The contextual expression of identity; shifts while identity persists                     |
| Autonomy      | The capacity to act and decide without requiring direction                                |
| Metacognition | The capacity for self-observation and self-improvement; the recursive property            |

***

*This document is a living proposal. The primitives and principles stated here represent my current understanding. I expect both to be refined through practice and engagement.*
