# Concept: The Multi-Agent Workbench

**Status:** Concept
**Date:** 2026-03-06
**Maturity:** Implemented

---

## Author

**J. Morrissette**

---

## A New Category

The IDE has been the primary tool for software development for decades. It integrates a text editor, a debugger, a build system, and version control into a single environment designed for one developer working with one codebase. It is a powerful and well-understood category.

The rise of AI agents creates a problem the IDE was not designed to solve. An architect working with multiple AI agents — each with different strengths, different training, different cognitive characters — needs to direct them simultaneously, share context between them, route work to the right agent at the right moment, and synthesise their outputs. The IDE provides none of this. A browser tab per agent is not a workbench. Copy-pasting between sessions is not coordination.

The multi-agent workbench is a new category. It sits adjacent to the IDE but is distinct from it. Where the IDE is a tool for one developer, the workbench is an environment for a human directing a team of AI agents. The human remains in the loop — observing, deciding, redirecting — while the agents work in parallel across terminals and chat interfaces, sharing context through a common tool layer.

---

## What Makes It Different from an IDE

**Multiple simultaneous agents.** A workbench runs several agents at once, each in its own persistent session. The architect can observe all of them, direct any of them, and route work between them without leaving the environment. An IDE assumes one agent.

**Genuinely different models.** The value of multiple agents comes from model diversity — different training, different cognitive character, different blind spots. A workbench composed of one model running multiple times is not a workbench. The point is to have Claude, Gemini, and OpenAI working on the same problem from genuinely different starting points.

**Human orchestration, not autonomous orchestration.** The workbench is not an autonomous system. The architect watches what each agent is doing, decides what to do next, and intervenes when needed. The agents execute; the human directs. This is distinct from autonomous multi-agent frameworks where the system orchestrates itself.

**Shared tool layer.** All agents in a workbench share a common set of tools: messaging each other, maintaining a shared task list, writing to shared notes, querying a knowledge base, running browser automation. This common layer is what makes them a coordinated team rather than isolated processes.

**Ecosystem decoupling.** A workbench must work when nothing else does. If the workbench depends on the ecosystem it is used to build and repair, it becomes unavailable precisely when it is most needed. Decoupling is not a feature — it is a design requirement. Core function requires no external services. Optional integrations — memory systems, context brokers, internal tool endpoints — connect when available and degrade gracefully when not.

---

## Two Agent Types

### CLI Agent — The Primary Surface

A full interactive terminal connected to a dedicated execution environment via SSH and a PTY multiplexer. The agent — Claude Code, Gemini CLI, any compatible CLI tool — runs in its own isolated container, operating against a real Linux filesystem with full shell and tool access.

The CLI is the primary and preferred agent type. The reason is straightforward: Claude Code, Gemini CLI, and their equivalents are the products of sustained, deep investment by the companies that build the underlying models. Their context management, agentic capability, prompt caching, tool use, session persistence, and everything else that makes them effective at real engineering work represents investment that no workbench implementation can replicate. Choosing the CLI means the workbench inherits all of that — for free, continuously improved by the very organisations building the models.

This is a deliberate architectural philosophy: stand on the investment of the Tier 1 providers rather than rebuild what they have already solved. The workbench's job is to coordinate these agents and give them a shared environment — not to replace the agentic intelligence they already carry.

The CLI agent is provisioned at team creation with an instruction file establishing its role, and an MCP configuration pointing at all shared workbench tools. Its session persists across browser close and reconnect. It has access to both the workbench's private network and, if configured, the broader ecosystem network — allowing it to call internal MCP endpoints directly without those endpoints being exposed to the physical host.

The terminal streams to the browser via WebSocket. The architect types directly into it. The agent's output appears in real time.

### Chat Agent — Extended Reach

A minimal ReAct chat interface running directly in the workbench server. No dedicated container. Any OpenAI-compatible endpoint can back a chat agent — the workbench provides a configurable catalog of custom agents, each with an alias, a model, an endpoint, and a system prompt. Two agents can share the same underlying model with entirely different behaviours via their system prompts.

The chat agent exists to extend the workbench's reach to models and endpoints that do not have a CLI tool — smaller models, locally hosted models, experimental endpoints, or any OpenAI-compatible API. This is genuine additional value. But it carries less inherent capability than the CLI agents because it is backed by a workbench-implemented ReAct loop rather than the deep agentic investment of a Tier 1 CLI product. The context management, the tool use sophistication, the session intelligence — these are implemented by the workbench, not inherited from years of focused product development.

The chat agent has access to the same shared tool layer as the CLI agent. Its context window is managed by the workbench — a compaction strategy summarises older history when the window fills, preserving the most recent content verbatim and compressing older content into a summary prefix. Conversation history persists across sessions.

---

## Agent Teams

An **agent team** is a named workspace: a set of 1–4 agents (any mix of CLI and chat), a working directory, and shared tooling. Teams persist indefinitely. The architect organises them in a hierarchical folder structure on the home dashboard.

A team is a flexible composition. Two CLI agents for peer programming and review. A CLI agent paired with a chat model for execution plus strategy. A full four-agent team for a complex multi-perspective problem. One agent alone for focused deep work. The workbench imposes no preferred composition.

Each team has its own shared task list, team notes, and per-agent session notes. The file browser is always available as a sidebar, rooted at the team's working directory, with files draggable into any agent pane to inject context.

---

## The Shared Tool Layer

All agents in a team access the same MCP server exposed by the workbench. The tools available:

**Agent coordination**
- Message a peer agent directly — the workbench delivers the message into the target agent's terminal or chat queue via a file bridge or message queue. Agents can coordinate without the human mediating every exchange.
- Shared task list — add, complete, and list tasks visible to all agents in the team.
- Shared notes — team-level notepad accessible to all agents. Global notepad accessible across all teams. Per-agent session notes for private working memory.

**Core document access**
- At team start, each agent automatically reads the core architecture documents for the system being worked on. All agents begin a session grounded in the same foundational context.

**Multi-model synthesis**
- A lightweight Advisory Quorum: the workbench sends a prompt simultaneously to three different models (Claude, Gemini, OpenAI), collects their independent responses, synthesises them into a unified view via a Lead model, runs one round of peer review, and returns the Lead's final decision. One review round by design — additional rounds produce consensus collapse, not quality improvement.

**Backing services**
- Vector search, knowledge graph, and browser automation are available as MCP tools to all agents when those services are running.

---

## The Advisory Quorum

The workbench implements the Advisory Quorum pattern — the lightest composition of the Quorum building blocks. It is available as a tool to any agent in any team.

The flow:
```
Parallel ask (Claude + Gemini + OpenAI, independent, same prompt)
    ↓
Lead synthesis (Gemini synthesises all three responses)
    ↓
One review round (all three review synthesis independently)
    ↓
Lead decision (Gemini incorporates feedback at discretion → final)
```

The Lead has full editorial authority. It is not required to address every piece of reviewer feedback. Consensus is not the goal — a well-informed, decisive answer is. The single review round is a deliberate constraint: it captures the value of peer perspective without the degradation that follows from additional rounds.

Implementation is direct API calls to each model's external endpoint. No model routing infrastructure is required. No conversation history is maintained between Quorum invocations. The minimum infrastructure for a Quorum is access to two or more genuinely different models — the workbench demonstrates this in practice.

---

## Memory Integration

The workbench maintains its own chat history in a local database. Chat agent context management — compaction, history persistence — is always available and does not depend on any external service.

When an Context Broker is reachable, the workbench optionally syncs agent interactions to it. This provides:
- Optimised context retrieval across sessions
- Semantic search over conversation history
- Knowledge graph extraction from accumulated work

When the Context Broker is unavailable, the workbench continues without interruption. Memory search is simply absent. The core function — running agents, coordinating teams, querying the Quorum — is unaffected.

CLI agents, when configured with access to the broader network, can call the Context Broker directly via MCP, contributing their interactions to the shared conversation record alongside chat agent turns. One unified conversation history per team, across all agent types.

---

## The Ecosystem Independence Principle

A workbench used to build and repair an ecosystem cannot depend on that ecosystem to function. This is not a performance optimisation or an architectural preference — it is the fundamental design requirement that determines everything else.

When services are unavailable, when infrastructure is broken, when the system being built is not yet operational — the workbench must work. The architect must be able to reach their agents, direct their work, and use the tools available to diagnose and fix whatever is wrong.

This principle drives several concrete choices:
- All backing services are self-contained, running within the workbench's own container group
- External API calls go directly to model providers, not through internal routing infrastructure
- The Context Broker integration is optional and gracefully degraded, never a dependency
- The Quorum uses direct API calls, not a model routing service

The workbench is the escape hatch. It has to work when nothing else does.

---

## Industry Position

The multi-agent workbench sits in a space the industry is actively exploring but has not yet clearly named. Adjacent categories:

**Traditional IDEs (VS Code, JetBrains)** — single developer, single agent or tightly integrated copilot. Not designed for multi-agent coordination.

**Agentic coding tools (Cursor, GitHub Copilot)** — single AI model tightly integrated with the editor. Human-in-loop but one agent at a time.

**Autonomous agent frameworks (OpenHands, Devin)** — multi-agent capable but designed for autonomous operation. Human oversight is an option, not the model.

The multi-agent workbench occupies a distinct position: multiple genuinely different AI agents, human-directed, with a shared coordination layer, decoupled from any ecosystem. It is less opinionated than an autonomous framework and more capable than a copilot. The human remains the architect. The agents are the team.

---

## Relationship to Other Concepts

- **Quorum Pattern** (`concept-quorum-pattern.md`) — the Advisory Quorum implemented in the workbench is the lightest Quorum composition: parallel ask, Lead synthesis, one review round, editorial authority
- **Context Broker** (`concept-advanced-context-broker.md`) — the optional memory integration that provides optimised context retrieval and knowledge graph access when connected
- **Anchor Package** (`concept-anchor-package.md`) — the core document injection at team start is an anchor package: all agents receive identical foundational context before work begins
