# Concept: Autoprompting — Self-Initiated TE Activation

**Status:** Stub
**Date:** 2026-03-13
**Maturity:** Not Started

---

## Author

**J. Morrissette**

---

## The Problem

The current architecture is entirely reactive. A TE activates only when a prompt arrives via the
AE from an external source — another MAD, a human, an MCP tool call. If nothing prompts it, the
system does nothing. This is insufficient for a truly autonomous ecosystem.

An autonomous system must be able to self-prompt: activate its own TEs based on events, time,
queued work, or commitments made during prior conversations.

---

## Known Patterns Requiring Autoprompting

**Trigger-based** — an external event occurs that requires a response:
- A file changes in the filesystem → the filesystem agent must be prompted to evaluate it
- A container health check fails → the observability agent must be prompted to investigate
- A new package appears in Alexandria → the relevant host must be prompted to consider installing it
- A git push arrives → the engineering agent must be prompted to review it

**Time-based** — scheduled future activation:
- "Check the deploy status every hour"
- "Run the security scan every night"
- "Follow up on this task next month"
- "Publish a blog post every Tuesday"

**Job queue** — work items accumulate and an Imperator needs to be prompted to process them:
- Build requests queued for the engineering agent
- Publishing tasks queued for the publications agent

**Conversation-derived** — during a conversation, the Imperator determines it needs to act later:
- "I need to revisit this design decision after the dependency is resolved"
- "Remind me to check on this deployment tomorrow"
- The Imperator commits to a future action as part of its reasoning

---

## Key Questions for the Paper

1. **Where does autoprompting live?** Is it an AE concern (the AE watches for triggers and
   prompts the TE), a TE concern (the Imperator registers its own future prompts), or both?

2. **How are scheduled intents stored?** If an Imperator decides during conversation that it
   needs to act next week, where is that commitment recorded? Rogers (conversation state)?
   A dedicated scheduler? The AE's own state?

3. **What is the activation mechanism?** When a trigger fires or a schedule hits, what actually
   constructs the prompt and delivers it to the TE? Is this an Executor within the AE? A
   dedicated autoprompting service? A capability of the bootstrap kernel?

4. **How does this relate to the PCP?** An autoprompt arriving at the TE still needs to go
   through the Progressive Cognitive Pipeline. Is it treated identically to an external prompt?

5. **Cross-MAD autoprompting** — can one MAD schedule a future prompt to another MAD? ("Tell
   the engineering agent to check on this build tomorrow")

6. **Ecosystem-level scheduling** — is there a central scheduler pMAD, or does each pMAD
   handle its own scheduling? Both have tradeoffs.

---

## What This Paper Must Define

- The taxonomy of autoprompt types (trigger, time, queue, conversation-derived)
- The storage and persistence model for scheduled/pending autoprompts
- The activation mechanism — how autoprompts become actual TE invocations
- The relationship between autoprompting and the PCP
- Cross-MAD autoprompting patterns
- How conversation-derived commitments are captured and stored
- The interface between the Imperator and the scheduling system

---

## Relationship to Other Concepts

- `a5-the-mad-pattern.md` — the MAD pattern, AE/TE separation
- `d2-progressive-cognitive-pipeline.md` — inbound processing pipeline
- `d1-system-3-react.md` — how the Imperator reasons and acts
- `HLD-state3-mad.md` — AE/TE architecture, bootstrap kernel
