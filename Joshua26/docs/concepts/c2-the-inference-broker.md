# Concept: The Inference Broker

**Status:** Concept
**Date:** 2026-03-06
**Maturity:** Implementable

---

## Author

**J. Morrissette**

---

## The Counterpart to the Context Broker

Two services give agents what they need to reason well.

The Context Broker provides the right information — assembling purpose-built context from the infinite conversation, delivering the right view of accumulated knowledge at the right moment. See `c1-the-context-broker.md`.

The Inference Broker provides the right inference capability — managing how requests reach models, how those models are configured, and how the results are shaped. Together, these two brokers form the foundation of agent cognition: the information environment and the inference environment, each engineered for the agent's purpose, each managed independently of the agents that use them.

---

## Inference Is Not a Model Call

The naive view of inference in an agentic system is a transaction: send a prompt, receive a response. The model is a black box. The caller provides input, the model provides output. Purpose, if considered at all, lives in the prompt.

This view is too thin for a system where agents have defined purposes, accumulated expertise, and ongoing missions. Inference is not a transaction. It is a **purposeful act** — a deliberate configuration of a model, its context, its parameters, its constraints, and its expected output shape, all oriented toward a specific goal. The model is the instrument. The purpose is what you want the instrument to do.

How well inference serves an agent depends not just on model capability but on how precisely the inference is configured for what the agent is trying to accomplish. A powerful model poorly configured for its purpose will produce worse results than a less capable model whose inference is precisely tuned. Purpose is as important as power.

---

## The Agent's Own Expression of Purpose

An agent — an Imperator with a defined purpose and accumulated domain expertise — will express that purpose in inference in many ways. It carries its own system prompt, its own understanding of the task, its own context assembled for its mission. For a specific, one-off, or experimental inference need, the agent may call a model directly with its own configuration. This is natural and valid. The agent owns that inference expression.

Direct calls are appropriate when:
- The inference need is specific to this agent and unlikely to recur elsewhere
- The agent is experimenting with a configuration it has not yet validated
- The purpose is so deeply tied to the agent's specific context that generalisation would lose what matters
- The need is genuinely novel and no proven configuration exists yet

The agent is the primary seat of purpose. Inference is one of many ways it acts on that purpose.

---

## The Alias as General Reusable Purpose

When a purposeful inference configuration has proven itself — when the same intent recurs across multiple agents, or repeatedly within one agent — it earns a name. That name is the alias.

An alias is not a pointer to a model. It is a named expression of a general, reusable purpose for inference. Behind the alias is a StateGraph — a fully executable policy that runs at inference time and encodes everything the inference requires:

- Which model to invoke, and why
- How to configure it — temperature, parameters, constraints
- What context to inject beyond the caller's own
- What output format or shape is expected
- When to route to different backends based on load or availability
- When to escalate, retry, or fail gracefully
- Any other dynamic adjustment the purpose requires

The alias captures this configuration as a shared, managed, stable interface. Any agent that needs "strategic architectural reasoning at large context" calls the alias for that purpose. The alias manages what that means — which model currently fulfils it, how it is configured, how it evolves as better options become available. The calling agents are decoupled from those decisions.

---

## Purpose as the Alias's Reason for Existence

The alias is named for what it does, not what it calls. `imperator-strategy` does not mean Gemini Pro. It means "the inference configuration that best serves strategic architectural reasoning at this moment." Today that is Gemini Pro. If a better option emerges, the StateGraph behind the alias changes. The name stays the same. Every caller keeps working.

This is the alias as a **purpose contract**. The caller declares what kind of reasoning it needs. The alias fulfils that declaration with whatever configuration currently does so best. The contract is stable. The fulfilment evolves.

This decoupling has consequences that compound over time:

**Model evolution is invisible to callers.** When frontier models improve — which they do rapidly — updating to use the better model requires changing the alias StateGraph. No caller code changes. No coordinator notification. The improvement propagates to every agent using the alias immediately.

**Configuration improvement is centralised.** As experience accumulates about what configuration best serves a purpose, that learning improves the alias. All callers benefit from each improvement, including agents that were built before the improvement was known.

**Purpose diversity without configuration sprawl.** Many agents in a system may need variations on the same kind of reasoning. Aliases let those variations be defined once, refined continuously, and used by many — rather than each agent maintaining its own configuration that diverges over time.

---

## What the StateGraph Enables

The StateGraph behind an alias is not a lookup table. It is a program. This distinction matters because inference is rarely as simple as "call this model with these parameters."

A StateGraph can:

**Route dynamically.** Different requests benefit from different models. A request that is primarily a short factual lookup may route to a small fast model. A request requiring multi-step strategic reasoning may route to the most capable available. The alias observes the request and decides.

**Apply load awareness.** If the primary model is at capacity, the StateGraph can route to a capable fallback rather than failing or queuing. The caller experiences consistent inference; the complexity of managing hardware availability is entirely hidden.

**Select hardware.** Different GPU configurations suit different model sizes and types. The StateGraph can route to specific hardware based on what the model requires — a large sovereign model to the high-VRAM cluster, an embedding call to the dedicated embedding hardware.

**Compose multiple models.** A single alias can invoke multiple models in sequence or parallel — a reasoner and an executor, a generator and a validator. The caller sees one inference call. The alias manages the composition.

**Adapt LoRA adapters.** Fine-tuned adapters for specific domains can be applied or swapped based on the request's context. The alias manages which adapter best serves the current need.

**Evolve over time.** The StateGraph is code. It can be updated, improved, and extended as understanding deepens — without any change to callers.

---

## Aliases Are Ecosystem-Level, Not MAD-Level

An alias is not owned by the agent that first needed it. It is an ecosystem-level expression of a general purpose that any agent can invoke when they need what it provides.

A personal companion inference configuration — warm, conversational, relationship-aware — is not specific to any one agent. Any agent that occasionally needs companion-style interaction can call that alias. A personal assistant configuration — task-focused, structured, actionable — is similarly general. The agent that first identified the need benefits immediately. Every subsequent agent that shares the need benefits without any additional work.

This has implications for how aliases should be named. An alias named after its first user (`agent-name-companion`) signals ownership and discourages reuse. An alias named after its purpose (`personal-companion`) signals availability and invites reuse. The naming should reflect what the alias does, not who asked for it first.

**Aliases within a single agent.** A single agent may need multiple aliases to serve different aspects of its purpose. An agent with a personal dimension may switch between `personal-companion` (relational, empathetic, continuity-focused) and `personal-assistant` (task-oriented, structured, efficient) depending on the nature of the current exchange. These are distinct inference purposes served by distinct aliases — which may involve different models, different LoRA adapters, different parameter configurations, or any combination. The agent declares what it needs at each moment. The alias manages the fulfilment.

The LoRA point is important here. The switch between companion and assistant modes may not require changing models at all — a fine-tuned adapter applied to the same base model may be sufficient. The alias hides this entirely. The caller says "I need personal-companion inference." Whether the alias achieves this by swapping a LoRA, routing to a different model, adjusting parameters, or some combination is the alias's concern. The caller is decoupled from the implementation.

## Parser of Rational Intent, Generator of Base State

The Inference Broker's role in the agent's cognitive experience is more fundamental than routing. It is the parser of rational intent and the generator of base state.

**Parser of rational intent.** When an agent calls an alias, it is expressing a rational intent: "I need this kind of reasoning, configured this way, for this purpose." The alias is the encoded form of that intent — not just a model name, but a purposeful specification of what the inference should accomplish. The Inference Broker parses that intent through the alias and translates it into a configured inference operation that serves the stated purpose.

**Generator of base state.** The inference the Broker produces is not merely an answer to a question. It is the raw cognitive material from which the agent's current reasoning is built — the base state of the agent's present moment. What the model returns, shaped by the alias's purposeful configuration, is what the agent thinks right now. It is the foundation from which the current step of reasoning proceeds.

This is the Inference Broker's counterpart role to the Context Broker. The Context Broker provides historical state — the accumulated conversational memory of what the agent has been and known. The Inference Broker generates immediate state — the active cognition of what the agent is thinking now. Memory and cognition. History and present moment. Together they constitute the agent's complete experience at any point in its reasoning.

---

## The Broker as Inference Infrastructure

The Inference Broker transforms inference from a caller responsibility into infrastructure. Individual agents do not need to solve the problem of "which model, configured how, on which hardware, with what fallback." That problem is solved once, centrally, and its solution is shared across the ecosystem.

This mirrors how other infrastructure works. An agent calling a database does not manage connection pooling, failover, or query optimisation — those are infrastructure concerns handled by the database layer. An agent calling an alias does not manage model selection, hardware routing, or configuration optimisation — those are inference infrastructure concerns handled by the broker.

The parallel to the Context Broker is exact. Just as the Context Broker assembles the right informational environment so agents do not have to manage memory, the Inference Broker assembles the right inference environment so agents do not have to manage model selection. Both brokers exist to remove infrastructure concerns from agents so agents can focus entirely on their domain and purpose.

An agent that uses both brokers well arrives at each reasoning step with exactly what it needs: the right context and the right inference. Neither is an afterthought. Both are engineered for the agent's purpose, proactively, as infrastructure.

---

## Relationship to Other Concepts

- **The Context Broker** (`c1-the-context-broker.md`) — the direct counterpart; together the two brokers provide the informational environment and the inference environment that agents need to reason well
- **Agent Purpose and Identity** (`a4-agent-purpose-and-identity.md`) — the alias is purpose made reusable; the quality of inference depends as much on how well the configuration serves the purpose as on the model's raw capability
- **System 3 ReAct** (`d1-system-3-react.md`) — dynamic model selection within the Reasoning and Action Engines is enabled by the Inference Broker; cognitive character selection per task is practical because aliases manage the configuration
- **MAD Pattern** (`a5-the-mad-pattern.md`) — all inference delegated to a named alias is a core property of the agent base pattern; agents never call model endpoints directly
- **Ecosystem Learning** (`b2-ecosystem-learning.md`) — aliases learn and improve over time; the StateGraph behind an alias can be updated as experience accumulates about what configuration best serves a purpose
