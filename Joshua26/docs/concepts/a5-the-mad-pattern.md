# Concept: The Multipurpose Agentic Duo

**Status:** Concept **Date:** 2026-03-13 **Maturity:** Partially Implemented

***

## Author

**J. Morrissette**

***

## The Duo

A Multipurpose Agentic Duo (MAD) is simultaneously a server and a client — and the same domain intelligence governs both roles.

This is the defining characteristic. A MAD does not separate its serving capability from its using capability. It cannot. The domain expertise that makes it a good server — deep knowledge of its domain, accumulated context, the ability to reason about goals rather than just execute commands — is the same expertise that makes it a good client of other MADs. Strip out the intelligence and you have a dumb server that can only respond to known queries, and a dumb client that can only issue known commands. Neither is a MAD.

The "Duo" names this inseparability. Agent and MCP server are not two separate things deployed together. They are one entity, two faces of the same domain intelligence. The agent provides reasoning and action capability. The MCP server provides the endpoint — the address through which the domain is summoned, conversed with, and directed. Together they form an entity that both provides and uses services. Neither half alone is a MAD.

***

## The Action Engine and the Thought Engine

Every MAD is composed of two conceptual aspects:

**The Action Engine (AE)** — the physical system that makes action possible. The AE is all of its containers: gateway, databases, caches, sidecars, observability, and the bootstrap kernel that loads everything else. The AE provides direct tool capabilities and, via joshua-net, access to the tool set of every other MAD in the ecosystem. The AE also hosts Executor-driven processes. Both the AE and the TE make use of LangGraph for their programmatic logic — LangGraph is a tool, not a layer.

**The Thought Engine (TE)** — the cognitive intelligence. The Imperator and its cognitive apparatus: PCP, inference, conversation-as-state. It is conceptually distinct from the AE. I surround the Imperator with the TE trappings to make it cognitive and independent.

The AE and the TE are the two aspects of the Duo at the architectural level. The AE makes action possible. The TE decides what action to take. See `HLD-state3-mad.md` for how State 3 achieves this separation architecturally — decoupling the TE from the AE as independently deployable StateGraph packages.

***

## Two Forms: pMADs and eMADs

The AE/TE separation reveals something fundamental about the MAD pattern. Once the TE is portable — a library that can be installed into any compatible AE — it no longer needs to be bundled with its own infrastructure. An autonomous cognitive actor that has no infrastructure domain to be concerned about can instead have a subject matter domain.

This gives rise to two concrete forms of the MAD:

### The pMAD (Persistent MAD)

A pMAD occupies a **system domain** — it is part of the infrastructure of the ecosystem. Memory systems, compute clusters, filesystem management, eMAD hosting, observability, software development: these are system domains. A pMAD provides a service that other parts of the ecosystem depend on to function.

A pMAD has a **body**: containers, a network presence, a persistent physical instantiation. It is always running. It exists independently of whether anyone is using it. The body is the AE — the complete infrastructure that makes the pMAD's actions possible. The TE — the Imperator and its cognitive apparatus — runs within the pMAD, supported by the AE, but conceptually distinct from it.

A pMAD owns its own AE and its own TE. Its Imperator governs the system domain and directs its Executors. A pMAD may also host eMADs — providing the AE within which eMAD TEs run. But hosting is not control. The relationship between a hosting pMAD and its eMADs is like a hotel and its guests. The hotel manages the rooms, the check-in, the infrastructure. It does not govern what the guests think, say, or do. The hosting pMAD's Imperator manages the mechanics of hosting — queuing, worker assignment, state loading and saving — through its Executors. It has no authority over the Imperators that live there. eMAD Imperators communicate directly with other agents in the ecosystem without passing through the hosting pMAD's Imperator. They are independent actors who happen to run inside the hotel.

A pMAD can have multiple instances — for scale, high availability, or proximity — but multiplicity is a deliberate architectural decision with explicit state management implications.

### The eMAD (Ephemeral MAD)

An eMAD occupies a **subject domain** — it is a subject matter expert. Software engineering, system architecture, security analysis, data science, personal assistance: these are subject domains. An eMAD does not provide infrastructure. It provides expertise in a field of knowledge.

An eMAD has **no body**. It has no AE of its own — no containers, no fixed network address, no persistent infrastructure. It is only a TE, installed as a library into a host pMAD's AE. It exists only within the process of the pMAD that hosts it, defined entirely by its TE package — the StateGraph that specifies how its Imperator reasons, what tools it has access to, and how it conducts its subject domain.

**Ephemeral in two senses.** The first is architectural: no AE. The second is systemic: an eMAD only exists when its StateGraph is executing. Between invocations there is nothing — no idle process, no waiting state, no memory consumed. It comes into being when a message arrives and its StateGraph is called, and ceases to exist when execution completes. The conversation persists in the memory system. The eMAD itself does not.

**Multiplicity is intrinsic.** Because an eMAD has no body, there is no physical constraint on how many instances run concurrently. The role is the entity, not the instance. When you converse with a subject matter eMAD, you are in some sense conversing with the role — all possible instances of that expertise — not one particular instance of it. This enables two things simultaneously: many different processes consulting the same role for their own purposes, and many users engaging with the same persona at the same time.

**Collective memory.** All instances of the same eMAD role share identity and memory. The accumulated experience of every prior conversation with a role is available as context when any new conversation with that role begins. An instance that starts today can draw on the experience contributed by every prior instance of the same role. Role identity, capability, and memory are collective, not individual.

**The Infinite Conversation.** Because conversation state is held by the ecosystem memory system in exactly the same way all conversation state is held, conversations with an eMAD have no expiry. A conversation begun today may continue months from now. The eMAD will have the full context of everything discussed previously. There is no session timeout, no context loss, no need to re-establish background. The conversation is a persistent relationship with a subject matter expert, maintained indefinitely — even though the eMAD itself does not persist between sessions.

### MAD as Umbrella

**MAD** is the umbrella term for the pattern itself — an autonomous actor that is simultaneously server and client, governed by shared domain intelligence. pMADs and eMADs are the two forms that pattern takes.

***

## Agent Classes

Within this architecture there are two distinct agent classes. Understanding their differences is essential to understanding how the ecosystem works. The distinction is grounded in the primitives defined in `a1-conversationally-cognizant-ai-systems.md`: Identity, Purpose, Intent, and Autonomy.

### Imperator

The Imperator is the prime agent within any TE. It has its own Identity (what it is) and Purpose (what it is for), and therefore generates its own Intent — the dynamic expression of its Purpose meeting current circumstances. It has Autonomy: it acts and decides without requiring direction.

The TE trappings — PCP, context assembly, inference, conversation-as-state — surround the Imperator and make it cognitive and independent. The Imperator is a self-directing participant in the ecosystem. It communicates with other Imperators as a peer, is addressable directly, and learns continuously from its operational experience.

Both pMADs and eMADs have Imperators. A pMAD's Imperator governs a system domain — the infrastructure the pMAD manages. An eMAD's Imperator governs a subject matter domain — engineering, publishing, analysis, whatever the eMAD is built for. The difference is what they govern, not what they are. Structurally they are identical: a TE with an Imperator at its centre.

### Executor

The Executor has no Identity or Purpose of its own. Its Intent is entirely derivative of the calling system and circumstances. It has no Autonomy. It is cognitive — it can reason, use tools, make decisions within its scope — but it is never independent. It is defined by the system that uses it, not by what it is.

Executors can take many forms: sub-agents of the Imperator, tools within AE processes, specialised workers in a StateGraph flow. The defining property across all forms is the absence of self-directed purpose. An Executor does not decide what to do. It is told what to do, and it does it well.

Executors are not addressable by external agents. They do not participate in the ecosystem's peer communication network. They are the closest thing in this architecture to a traditional agent: capable, purposeful within their scope, and under authority.

***

## Serving with Intelligence

A MAD exposes its domain through MCP tools — a standard interface through which a participant can invoke its capabilities deterministically. This is the server face.

And while the system will expose a variety of MCP tools that will be deterministic and structured as needed, via the Chat tool, the Imperator can be spoken with which transforms what serving means. A dumb server receives a request and either handles it or returns an error. More to the point, if a MAD is creating errors by poorly using another MADs the fixed MCP tools, one MAD may converse with the other, via the Imperators, to make a correction. An intelligent server receives a request, understands the intent behind it, and can respond in ways a fixed protocol cannot:

-   It can handle the request
-   It can ask the requesting party to clarify their intent
-   It can suggest a better way to achieve the goal
-   It can describe itself — its capabilities, its constraints, what it knows — so the requester can work with it more effectively

The system is queryable about itself. You do not need documentation to understand what a MAD can do. You ask it. It knows. This is mission control: direction through expressed intent rather than through configuration and protocol.

***

## Using with Intelligence

A MAD consumes other MADs' capabilities as a client. This too is governed by domain intelligence.

A dumb client issues commands. An intelligent client understands what it is trying to accomplish, selects the right tools from the right MADs, interprets responses in the context of its goal, and escalates or redirects when a response is unexpected. The same domain knowledge that tells a MAD how to serve its domain well also tells it how to use other domains intelligently.

This is why serving and using cannot be separated. A MAD that only serves has no basis for consuming other domains effectively. A MAD that only consumes has no basis for serving its own domain intelligently. The expertise is shared between both roles.

***

## The Web

MADs form a web of domain experts and capabilities — peer-to-peer actors, each simultaneously serving and consuming, each bringing the same accumulated domain knowledge to both sides of every interaction.

There is no centre. No hub coordinates the web. Each MAD knows its own domain deeply and exposes that knowledge bidirectionally: outward to the MADs that use it, inward to direct its own consumption of other MADs. The web grows and learns as each MAD accumulates experience in its domain.

Communication across the web takes two forms:

**Semantic** — via conversation with the Imperator. Goals are expressed in prose. The Imperator reasons about what is being asked, what is possible, and what should be done. Ambiguity is resolved through dialogue, not error codes.

**Deterministic** — via MCP tools. Known operations are invoked directly with precise parameters. Fast, predictable, auditable.

Both forms are valid. The choice depends on whether the request is well-understood and bounded (deterministic) or goal-driven and contextual (semantic).

***

## Prose over Protocol — at the Goal-Directed Layer

The MAD architecture operates across three distinct zones, each with its own communication model:

**Within the pMAD** (internal container network): Pure hard protocols by technical necessity. HTTP between containers, database wire protocols, Redis communication. Software connecting software requires deterministic interfaces. No prose layer exists or is appropriate here.

**Between MADs — tool layer** (MCP): MCP is a hard protocol. Direct tool calls with defined schemas, typed parameters, and predictable responses. This layer is preserved wherever deterministic, well-understood operations are appropriate — and it always will be. "Prose over protocol" does not mean MCP disappears. It means MCP handles what it handles best.

**Between MADs — goal-directed layer** (Imperator): This is where the exploration is. Fixed protocols are closed — they handle exactly what was anticipated when they were designed. Every unanticipated request is an error. Conversation is open. A goal expressed in prose can be understood, reasoned about, and acted on — including goals that were never anticipated when the MAD was designed. The Imperator does not need to have seen a request before to handle it. It needs to understand the domain well enough to reason about what the request means and what should be done.

This exploration has a specific question: at the goal-directed layer, how far can prose push out the need for the caller to understand implementation detail — the specific tool sequence, error recovery paths, retry logic? An agent that can say "commit and push my work" to the version control agent's Imperator and have it handle the git complexity is more capable than one that must orchestrate each git step itself. The prose layer does not replace the tools. It replaces the caller's need to know which tools to call in what order.

This enables mission control — directing the ecosystem through expressed intent rather than through configuration. An ecosystem of MADs can be directed, queried, redirected, and extended through conversation in ways that a protocol-only system cannot.

Conversation is also the vehicle for memory and cognition. Everything the system knows, everything it has learned, everything it can do — accessible through conversation. See `d1-system-3-react.md` for the translation layer that makes this possible.

***

## Learning

Every aspect of the MAD architecture is designed to learn. The PCP learns routing patterns from the Imperator's decisions. The DTR absorbs deterministic patterns progressively. The Metacognitive Architect observes and modifies the ecosystem's own structure. Conversation history accumulates as the substrate for future reasoning.

The learning philosophy follows the bitter lesson: general methods that leverage computation and learn from experience ultimately outperform methods that encode human knowledge into the architecture. Do not hard-code what the system should know. Build mechanisms that allow it to learn.

Where supervised learning tools are used — a decision tree, a classifier — they are backed by unsupervised or self-supervised mechanisms that generate the supervision signal from observed outcomes. The system supervises itself from experience, not from hand-labelled data. Decision making is treated as ensemble learning wherever possible.

***

## Summary of Distinctions

| Property                         | pMAD                       | eMAD                              |
|----------------------------------|----------------------------|-----------------------------------|
| Agent class                      | Imperator                  | Imperator                         |
| AE (Action Engine)               | Owns its own               | Uses host pMAD's AE               |
| TE (Thought Engine)              | Owns its own               | Owns its own                      |
| MCP endpoint                     | Yes                        | Yes (via host's AE)               |
| Independent actor                | Yes                        | Yes                               |
| Domain type                      | System                     | Subject                           |
| Body (containers/infrastructure) | Yes                        | No                                |
| Existence                        | Persistent deployment      | Only during StateGraph execution  |
| Multiplicity                     | Deliberate design decision | Intrinsic — baked into the nature |
| Identity                         | Role-based                 | Role-based, collective memory     |
| Conversation persistence         | Yes (via memory system)    | Yes (via memory system)           |

***

## Relationship to Other Concepts

-   **Conversationally Cognizant AI Systems** (`a1-conversationally-cognizant-ai-systems.md`) — defines the primitives (Identity, Purpose, Intent, Autonomy) that ground the Imperator/Executor distinction
-   **State 3 MAD** (`HLD-state3-mad.md`) — how the AE/TE separation is achieved architecturally; dynamic StateGraph loading via Alexandria
-   **System 3 ReAct** (`d1-system-3-react.md`) — the agent pattern governing how the Imperator reasons and acts; the translation layer between intent expressed in prose and goal-directed machine action
-   **Progressive Cognitive Pipeline** (`d2-progressive-cognitive-pipeline.md`) — the inbound cognitive pipeline within every MAD; how incoming conversation is processed from reflexive routing through to full Imperator reasoning
-   **The Conversation Broker** (`c3-the-conversation-broker.md`) — the addressing and messaging model through which MADs communicate across the web
-   **Agent Communication Model** (`d5-agent-communication-model.md`) — the intelligence layer governing how MADs send and receive messages
