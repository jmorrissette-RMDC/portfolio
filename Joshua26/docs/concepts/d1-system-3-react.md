# Concept: System 3 ReAct

**Status:** Research Concept **Date:** 2026-03-04
**Maturity:** Partially Implemented

***

## Author

**J. Morrissette**

***

## Background: The ReAct Pattern

ReAct (Reasoning and Acting, Yao et al. 2022) is an agent pattern that interleaves reasoning and tool use in a loop:

```
Thought → Action (tool call) → Observation → Thought → ... → Final Answer
```

A single model handles all steps: reasoning about what to do, generating precise tool calls, observing results, and producing the final response.

***

## The Cognitive Mismatch

Standard ReAct asks one model to perform three cognitively distinct tasks:

1.  **Deep reasoning** — multi-step planning, working through a complex problem, deciding what information is needed
2.  **Precise execution** — generating exact tool calls with correct schemas, parameter types, and values
3.  **Conversation** — producing outbound communication appropriate to the recipient: natural language for a person, structured messaging for another agent

These are genuinely different capabilities. A model optimized for deep multi-step reasoning may produce verbose, unpolished output that is difficult to read. A model optimized for fast, precise instruction following may miss subtle reasoning steps. A model with excellent output style may not be the strongest reasoner.

Most models have varying strengths across these three dimensions. Assigning all three to one model means accepting its weaknesses across all three simultaneously.

The knock-on effect of this separation is what is made possible for the reasoning and execution steps. If human readability is not a requirement for reason or execution, future models can be optimized for machine readable reasoning and execution. Large Language Models will have the opportunity to shift to Agentic Language Models aligning themselves to semantic language for machine processing requiring vastly shorter lexicon, shorter encodings and reduce parameters with the potential for greater deterministic outputs.

***

## System 3 ReAct: Three Cognitive Roles

**A note on naming.** The "System 1" and "System 2" labels are borrowed from Daniel Kahneman's *Thinking, Fast and Slow* (2011), which describes two modes of human cognition: System 1 (fast, automatic, intuitive) and System 2 (slow, deliberate, analytical). That framework is one of the most influential contributions to cognitive science in a generation. This pattern borrows its terminology because the mapping is memorable — fast/automatic maps onto the Actor, slow/deliberate maps onto the Reasoner — not because this work belongs in the same conversation as Kahneman's. "System 3" is not a claim that conversation constitutes a third mode of human cognition. It is a convenient label for the third role in this engineering pattern. The underlying insight — that different cognitive tasks benefit from different model characteristics — stands independently of the naming, and would be the same insight under any labels.

The pattern describes three distinct cognitive modes, each handled by a different model:

**System 2 — The Reasoner** Deep, deliberate planning. Given the problem, context, and prior observations, produces a plan: what needs to be found, what step comes next, what the result means. The Reasoner is isolated from raw tool schemas — it reasons about the problem and the goal, not about JSON parameter formats. It does, however, need capability awareness: a conceptual understanding of what tools exist, what they can accomplish, and what kinds of inputs they require. The distinction matters — "there is a tool that updates user records; it requires identifying the user before updating" is capability awareness. The exact parameter names and types are schema detail the Actor handles. *Required strength:* multi-step reasoning depth. Speed is not required.

**System 1 — The Actor** Fast, precise execution. Receives the Reasoner's plan and translates it into exact tool calls with correct schema and parameters, or structures the final answer. Never needs to reason deeply — it receives a clear plan and executes it precisely. *Required strength:* instruction following, schema adherence, output precision.

**System 3 — The Conversation Engine** Conversational intelligence at the entrance and exit points of the loop. On the front side, the Conversation Engine is the Progressive Cognitive Pipeline — inbound conversation processed and routed into cognition. On the back side, it is the outbound communication layer — producing conversation addressed to other agents or people as appropriate.

Conversation is not just the output format. It is the medium through which the agent receives thought, accumulates memory, and communicates across the ecosystem. The Conversation Engine is what makes conversation that medium — placing it structurally at both ends of the reasoning loop so that everything the agent does is grounded in and expressed through conversation.

*Required strength:* conversational fluency appropriate to the recipient — whether that is a structured message to another agent, a natural language response to a person, or a trigger to an eMAD.

***

## LangGraph Flow Structure

```
[System 3] conversation_engine — inbound (PCP)
    │ receives: conversation / trigger
    │ routes via: DTR → Executor → Imperator
    ▼
[System 2] reasoning_node
    │ produces: plan / thought
    ▼
[System 1] action_node ──[tool call]──► tool_executor
    ▲                                        │
    └──────── [System 2] reasoning_node ◄────┘
              (loop with new observation)
    │
    │ [reasoning complete — no further tool calls needed]
    ▼
[System 3] conversation_engine — outbound
    │ produces: conversation addressed to agents or people
    ▼
   END
```

The Reasoner and Actor cycle until the Reasoner determines no further tool calls are needed. The Conversation Engine runs at both ends — governing inbound conversation into the loop via the PCP, and producing outbound conversation when the loop completes.

***

## Re and Act as Engines, Not Atoms

The original ReAct pattern infers atomicity by virtue of a single model performing all steps. It does not claim that Reasoning and Acting are indivisible — it simply does not address the question. In an agentic implementation that question must be addressed, and the answer is that Re and Act are necessarily collections of components, bound together by process to form an atomic step.

The atomic step remains. From the loop's perspective, Re is a single bounded unit that produces understanding and a plan. Act is a single bounded unit that executes that plan. The loop does not change. What changes is the recognition that each unit is internally composed — a collection of components that the process binds together to behave as one.

**Re — The Reasoning Component** is that collection on the thinking side. Planning, analysis, knowledge retrieval, evaluation, specialist model consultation, metacognitive checking — reasoning activities that may involve different components, different models, or different sub-graphs depending on the agent's domain and the complexity of the problem. The Reasoning Component produces understanding and a plan. It does not execute anything.

**Act — The Execution Component** is that collection on the doing side. Tool execution, state management, external integrations, output construction, domain-specific operations — acting activities that may likewise involve multiple components. The Execution Component executes precisely from the plan it receives. It does not reason about what to execute.

Note: the Reasoning and Execution Components within the ReAct loop are distinct from the Thought Engine (TE) and Action Engine (AE) of the MAD pattern. The TE and AE are architectural aspects of a MAD. The Reasoning and Execution Components are cognitive roles within a single ReAct loop that runs inside the TE.

The ReAct loop structure holds regardless of how complex either component becomes internally. The process binding is what preserves the atomicity of each step.

A direct consequence of this component model: **no agent has a fixed model**. Because the Reasoning and Execution Components are collections of components composed at runtime by the StateGraph, the model invoked at any given step is always potentially dynamic. A DTR route may select a different model based on the nature of the input. A conditional edge may escalate when confidence is low. A StateGraph node may select the model best suited to the specific cognitive demand of that step.

Model selection is not simply a capability dial — it is a cognitive character selection. Different models bring genuinely different strengths, different training emphases, different approaches to the same problem. An agent doing architectural strategy may benefit from one model's structural thinking; the same agent producing prose may benefit from another model's writing quality; a particularly complex reasoning step may call for a third. The right model for each step is the one whose cognitive character best matches what that step requires.

This is the same insight that underlies the Quorum pattern — model diversity is valuable because different models catch different things. Applied within a single agent over time rather than in parallel, it means each component of the Reasoning or Execution Component can draw on the model most suited to its specific task. Model fixing is a design choice, not an architectural constraint. The architecture assumes dynamism; fixity requires deliberate configuration.

**Dynamic model switching is not persona switching.** An agent remains itself regardless of which model it is currently using. The engineering agent stays itself — the same mission, the same domain expertise, the same accumulated knowledge — whether it is using Gemini for strategic planning or Sonnet for prose. Model switching optimises how the agent does what it does. It does not change what the agent is.

When an agent needs expertise outside its domain, the correct response is not to switch models and simulate that expertise — it is to call the appropriate eMAD. A security eMAD has accumulated genuine security knowledge across every conversation it has had in that role. The engineering agent has accumulated genuine engineering knowledge in its role. Neither substitutes for the other. The value of domain expertise is that it accumulates cleanly in one place, deepens over time, and is available through the eMAD model to whoever needs it. Calling the expert is not a workaround. It is the architecture.

## The Conversation Engine

The Conversation Engine is what makes System 3 ReAct distinct from standard agentic ReAct. It is not a reasoning component or an acting component — it is the component that places conversation as the medium at both ends of the loop.

**Front side — the Progressive Cognitive Pipeline.** Inbound conversation enters through the PCP. The Conversation Engine governs how that conversation is received, processed, and routed into the Reasoning and Action Engines. The PCP is not just a routing mechanism — it is the entrance point where the medium of conversation becomes cognition.

**Back side — outbound communication.** When the loop completes, the Conversation Engine produces outbound conversation addressed to the appropriate recipients: a response to a person, or a message to another agent. The form of that conversation is determined by who is receiving it — natural language for a person, structured agent-to-agent messaging for a pMAD, a lightweight trigger for an eMAD.

Conversation is the medium through which agents in this ecosystem receive thought, accumulate memory, and communicate. The Conversation Engine is what makes that true structurally — not as a design preference but as an architectural constraint. Every input enters as conversation. Every output leaves as conversation. The reasoning and acting that happens between those two points is what the rest of the ReAct loop handles.

Human-in-the-loop is one outcome of this design. It is not the primary goal. The primary goal is that conversation is the universal medium — enabling agents and people to participate in the same ecosystem on the same terms.

***

## Key Properties

**Decoupled communication.** Outbound conversation is produced by the Conversation Engine independently of the reasoning and execution process. The Conversation Engine can be tuned for different recipient types — agent-to-agent messaging, person-facing responses, eMAD triggers — without affecting how the agent thinks or acts.

**Cost optimization.** The expensive reasoning model runs once per loop iteration. The fast precise model handles all schema-sensitive execution. The lightweight communication model handles presentation. Cost is matched to requirement at each step.

**Schema isolation with capability awareness.** The Reasoner is isolated from raw tool schemas — parameter names, types, and JSON formats are the Actor's concern. The Reasoner does need capability awareness: a conceptual map of what tools exist and what they can accomplish. This is not schema leakage — it is the Reasoner understanding the landscape of what is possible before planning. A plan built without any awareness of available capabilities will produce steps the Actor cannot execute. A plan built with capability awareness but without schema detail can be executed precisely by an Actor tuned for that purpose.

**Agentic Language Models — a long-term direction.** As the ecosystem matures and agent-to-agent communication accumulates at scale, a natural question emerges: why should agents reason and act in a model trained primarily on human language?

Human language carries enormous overhead that serves human cognition and has no value in machine-to-machine communication: social register, discourse markers, syntactic filler, literary convention, emotional modulation, the ambiguity that exists for human tolerance rather than semantic necessity. These inflate parameter count without contributing to the agent's ability to reason, plan, or act.

An Agentic Language Model would shed this overhead — trained on the ecosystem's own accumulated agent-to-agent communication corpus rather than on human text. Smaller vocabulary, fewer parameters, more direct encoding of semantic intent.

The critical constraint: an ALM must preserve the properties that make language fundamentally different from protocol. A typed schema is efficient but closed — it can only express what was anticipated at design time, and every unanticipated situation is an error. Language is efficient *and* open, because it is probabilistic rather than deterministic. It models a distribution over meaning, which means it can always reach toward something new — a concept with no name yet, a situation never encountered before. It is able to accommodate the infinite variations of the universe. That unboundedness is not overhead. It is the capability. Strip it and you have a compressed protocol, not a language, and you have lost exactly what makes the architecture capable of handling novelty.

What an ALM sheds is the human-specific instantiation of these properties. What it preserves is the probabilistic, unbounded nature itself.

The ecosystem is unknowingly positioned to pursue this. The Conversation Broker is accumulating the corpus. The Semantic ETL pipeline demonstrates that corpus can be structured for training. The Inference Broker alias system already anticipates models being swapped beneath a stable interface. The Metacognitive Architect is the function that would commission such models when the corpus is sufficient and the case is made. This is a long-term speculative direction — not implementable today — but it is a direction the architecture was built to reach.

***

## Practical Constraints

**Latency.** The three-model split adds inference calls to every loop iteration. Where a single-model ReAct loop makes one inference call per reasoning step, a three-model split makes up to three. For interactive, real-time use cases this additional latency is a real cost. The split is appropriate where reasoning quality matters more than response speed — complex multi-step orchestration, autonomous background tasks, high-stakes decisions. For rapid conversational exchanges, a single capable model doing all three roles may be the right choice.

**Cost.** Three inference calls per step at frontier model pricing is meaningfully more expensive than one. The cost is justified when the separation of cognitive roles produces better outcomes — cleaner reasoning, more precise execution — than a single model compromising across all three. Where the task is simple enough that one model handles all three roles well, the split adds cost without benefit.

**Current state.** No Joshua26 MAD currently uses the three-model split. The Imperator pattern (a single reasoning model handling the full loop) is what is deployed. The three-model split is the direction the architecture is moving, not its current state.

***

## Relationship to Other Concepts

- **MAD Pattern** (`a5-the-mad-pattern.md`) — Imperators are System 3 ReAct agents; the Conversation Engine at both ends of the loop is what makes them conversational agents rather than task executors
- **Progressive Cognitive Pipeline** (`d2-progressive-cognitive-pipeline.md`) — the front-side Conversation Engine IS the PCP; inbound conversation is processed through the DTR → Executor → Imperator cascade before reasoning begins
- **Conversation as State** (`a2-conversation-as-state.md`) — state flows in through the front-side Conversation Engine as engineered context; state flows out through the back-side as the agent's contribution to the infinite conversation
- **Inference Broker** (`c2-the-inference-broker.md`) — the dynamic model selection within the Reasoning and Execution Components is enabled by the Inference Broker; cognitive character selection is practical because aliases manage the configuration
- **Agentic Identity and Persona** (`a6-agentic-identity-and-persona.md`) — persona is expressed through the inference configuration the Conversation Engine invokes; identity persists through the conversation the Conversation Engine contributes to
