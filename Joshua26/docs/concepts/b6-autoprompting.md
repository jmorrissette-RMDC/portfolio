# Concept: Autoprompting — Self-Initiated TE Activation

**Status:** Concept
**Date:** 2026-03-26
**Maturity:** Conceptual

---

## Author

**J. Morrissette**

---

## The Problem

The current architecture is entirely reactive. A TE activates only when a prompt arrives via the AE from an external source — another MAD, a human, an MCP tool call. If nothing prompts it, the system does nothing. This is insufficient for a truly autonomous ecosystem.

An autonomous system must be able to self-prompt: activate its own TEs based on time, events, or commitments made during prior conversations. Without this capability, agents only think when spoken to. An agent that only thinks when spoken to is not autonomous — it is a tool that waits.

---

## The Key Distinction

The autoprompter does not act. It prompts.

This is the critical design principle and it must not be compromised. The autoprompter never directly executes an action — it composes a prompt and delivers it to the Imperator through the normal conversational path. The Imperator then reasons about what to do.

"Wake me up at 6am" does not set an alarm that buzzes the user. It creates a prompt that tells the Imperator at 6am: "the user asked to be woken up." The Imperator then decides how to accomplish that — send a message, trigger a notification, whatever is appropriate given the current context.

"Check the deploy every 10 minutes" does not call a health endpoint on a timer. It prompts the Imperator every 10 minutes: "it is time to check the deploy." The Imperator decides what checking means, which tools to use, and what to do with the result.

This keeps the Imperator as the single reasoning authority within the TE. The autoprompter has zero intelligence about what to do — it only knows when to ask. The Imperator has all the intelligence about what to do when asked. The separation is clean and inviolable.

This is also consistent with the conversational foundation of the framework. Everything goes through conversation. The autoprompter does not bypass the cognitive pipeline — it feeds into it. An autoprompt enters the TE through the same path as any other message and is processed through the same Progressive Cognitive Pipeline. The Imperator does not know or care whether a prompt came from another agent, a human, or its own autoprompter. It is all conversation.

---

## How People Already Think About This

The autoprompter is best understood through the lens of tools people already use every day. The concepts are familiar — calendars, timers, reminders, alerts. The difference is that instead of buzzing a human's phone, the autoprompter composes a prompt and delivers it to the Imperator.

### Calendar

Specific events at specific times. "The deploy window is Thursday 6-8pm." "There is a design review at 2pm Tuesday." "The security audit is due March 15."

The autoprompter maintains its own internal calendar. It can also be configured to read external calendars — Outlook, Google Calendar, a project management tool, any system that expresses scheduled events. When a calendar event arrives, the autoprompter composes a prompt for the Imperator with the event context.

The internal calendar and external calendars are not different mechanisms — they are both sources of time-anchored events that produce prompts. The distinction is only where the event was created.

### Timers and Periodic Schedules

Recurring on intervals or cycles. "Check the build every 10 minutes." "Run the security scan every night at midnight." "Review the publishing queue every weekday morning." "Process the background job queue every 30 seconds."

These are the cron equivalent — periodic activation at defined intervals. Unlike calendar events, they have no specific context beyond the recurrence pattern and the purpose. The prompt they generate is the same each time: "it is time to do X." The Imperator may reason differently each time based on current context, but the prompt itself is stable.

### Reminders and Alarms

One-shot time-based future prompts. "Remind me to follow up on this deployment tomorrow." "Check on the dependency resolution next Monday." "Alert me at 6am."

These are often generated from conversation. The Imperator, during its reasoning, determines that it needs to act at a specific future time. It registers that commitment with the autoprompter — which stores it and delivers the prompt when the time arrives.

Reminders and alarms are functionally the same mechanism — a time-based one-shot prompt. The difference is connotational: a reminder carries context about what to do ("follow up on the deployment"), while an alarm is more about urgency ("wake up," "time's up"). Both produce a prompt to the Imperator at the specified time.

### Alerts

Event-driven, not time-driven. "Tell me when the build finishes." "Alert me if a container health check fails." "Notify me when a new package appears in Alexandria." "Let me know if the error rate exceeds 5%."

Alerts fire when a condition is met rather than when the clock hits a time. The autoprompter monitors configured event sources — webhooks, filesystem watchers, health check endpoints, message queues — and generates a prompt to the Imperator when the triggering condition is detected.

The prompt includes the event context: what happened, when, and any relevant details the Imperator needs to reason about what to do.

---

## The Four Modes Summarized

| Mode | Trigger | Example | Time or Event |
|------|---------|---------|---------------|
| Calendar | Specific time, specific event | "Design review at 2pm" | Time |
| Timer/Periodic | Recurring interval or schedule | "Every 10 minutes" | Time |
| Reminder/Alarm | One-shot future time | "Tomorrow at 9am" | Time |
| Alert | Condition met | "Build failed" | Event |

The first three are time-based. The fourth is event-based. All four produce the same output: a prompt delivered to the Imperator through the normal conversational path.

---

## Where It Lives

The autoprompter is an AE component — it lives within the Action Engine of each MAD. It is not part of the Thought Engine. This is deliberate: the autoprompter is infrastructure, not intelligence. It manages schedules, monitors events, and delivers prompts. It does not reason about what those prompts mean or what the Imperator should do with them.

Each pMAD has its own autoprompter instance. There is no central ecosystem scheduler — scheduling is a local concern. A MAD's autoprompter manages that MAD's calendar, timers, reminders, and alert subscriptions.

For eMADs, the host pMAD's autoprompter handles scheduling on behalf of hosted eMADs. When an eMAD's Imperator registers a reminder during conversation, the host's autoprompter stores it and delivers the prompt when the time comes — spinning up the eMAD's TE to receive it.

---

## Conversation-Derived Commitments

The most interesting source of autoprompts is the Imperator itself. During conversation, the Imperator may determine that future action is needed:

- "I need to revisit this design decision after the dependency is resolved"
- "I should check on the deployment tomorrow morning"
- "This task requires a follow-up in three days"

These commitments are captured from the conversation and registered with the autoprompter. The mechanism for capture can be explicit — the Imperator calls an autoprompting tool to register the commitment — or it can be extracted by a background process that observes the Imperator's conversation and identifies stated future commitments.

The stored commitment includes the context of why the prompt was created — enough for the Imperator to understand what it was thinking when it made the commitment. When the time arrives, the autoprompter delivers that context as part of the prompt: "Three days ago you said you would follow up on the deployment. Here is the context from that conversation."

This is the autoprompter functioning as the agent's own memory of future intentions — not what it has done, but what it intends to do. The Context Broker holds the past. The autoprompter holds the future.

---

## Cross-MAD Autoprompting

An Imperator may need to schedule a prompt for another MAD: "Tell the engineering agent to check on this build tomorrow." This is cross-MAD autoprompting.

The mechanism is straightforward: the requesting Imperator sends a message to the target MAD's Imperator, and the target MAD's Imperator decides whether to register it with its own autoprompter. The requesting MAD does not directly write into another MAD's schedule. It makes a conversational request, and the target MAD's Imperator — the reasoning authority for its own domain — decides how to handle it.

This preserves the principle that each Imperator is the sole authority over its own cognitive activation. No external agent can force a prompt onto another MAD's schedule without that MAD's Imperator agreeing to it.

---

## Relationship to the PCP

An autoprompt entering the TE goes through the Progressive Cognitive Pipeline like any other prompt. It is not a special case. The DTR may route a recurring timer prompt directly to a known handler. The Executor may handle a routine reminder. Only genuinely novel autoprompts reach the Imperator for full deliberation.

This means autoprompts benefit from the same learning arc as all other prompts. A timer that fires every 10 minutes and always results in the same action will eventually be absorbed into the DTR — handled reflexively without engaging the Imperator at all. The system gets more efficient at handling its own self-generated prompts over time.

---

## What This Enables

**Genuine autonomy.** An agent that can schedule its own future work, monitor events, and act on commitments it made during prior conversations is an agent that operates independently of external direction. The autoprompter is what closes the gap between reactive capability and autonomous operation.

**Proactive behaviour.** Instead of waiting to be asked, an agent can anticipate needs. An engineering agent that schedules a follow-up check after a deploy is being proactive. An observability agent that monitors health checks continuously is being vigilant. Neither requires someone to remember to ask.

**Conversational continuity across time.** A commitment made in conversation today is honoured tomorrow — not because a human remembered to follow up, but because the autoprompter captured the commitment and delivered the prompt when the time came. The conversation spans time without requiring continuous attention.

**External integration without breaking the model.** Calendars, task boards, monitoring systems — any external source of time-based or event-based information can feed into the autoprompter. The Imperator receives it all as conversation. The complexity of integrating with external systems is contained within the autoprompter; the Imperator sees only prompts.

---

## Relationship to Other Concepts

- **The MAD Pattern** (`a5-the-mad-pattern.md`) — the AE/TE separation is what makes the autoprompter's role clear: AE infrastructure that prompts the TE
- **Progressive Cognitive Pipeline** (`d2-progressive-cognitive-pipeline.md`) — autoprompts enter through the PCP like any other prompt
- **System 3 ReAct** (`d1-system-3-react.md`) — the Imperator that receives and reasons about autoprompts
- **Conversation as State** (`a2-conversation-as-state.md`) — autoprompts are conversation; the autoprompter extends the conversational substrate across time
- **Agent Autonomy** (`b3-agent-autonomy.md`) — autoprompting is a prerequisite for genuine autonomy
