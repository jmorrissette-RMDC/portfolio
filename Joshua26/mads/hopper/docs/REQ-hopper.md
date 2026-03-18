# Requirements: Hopper (The Engineering Department)

**Version:** 1.0 (Structural Draft)
**Date:** 2026-03-02
**Status:** Proposed
**Related Documents:** HLD-joshua26-agent-architecture.md, HLD-software-factory-core.md, mads/henson/docs/REQ-henson.md

---

## 1. Purpose and Architectural Rationale

### 1.1 The Engineering Department Problem

Prior to Hopper, software development in Joshua26 was bottlenecked by the human. Every code change required the human to initiate a Cursor session, prompt Composer, review the output, and manually trigger deployment. This is not agentic development — it is assisted typing with a human in the driver's seat.

Hopper resolves this by acting as the **Joshua26 Engineering Department**: a fully autonomous set of agents capable of taking a requirement from human intent all the way to a deployed, tested, and verified system — with the human only required at the approval gates.

### 1.2 The Hopper Process

Hopper's core capability is the **Hopper Process** — a multi-LLM Quorum Engine derived from the manually-executed `LLM_Team_Development_Process_v3.0.md`. It does not use single-agent typing loops. Instead, it generates parallel implementations across multiple diverse models, cross-pollinates ideas, and synthesizes holistic solutions based on entire context windows.

The key insight driving this approach: an LLM is not a human typist. It does not need to traverse code line-by-line or maintain a mental model of a 5,000-line codebase. Given a sufficiently large context window, it holds the entire system simultaneously. This fundamentally changes how code should be generated — in holistic parallel drafts, not sequential keystrokes.

### 1.3 Self-Extension Design Principle

Hopper's capability set is not fixed at build time. When Hopper identifies a gap in its own abilities — a new review type needed, a new development pattern required — it uses `develop_software` to design, implement, and deploy that new capability for itself. The system is intentionally self-extending.

### 1.4 Agent Classification

Hopper contains two agent types. See `HLD-joshua26-agent-architecture.md` for the full base class definition.

- **The Hopper Imperator:** An `Imperator` subclass. The front door of the Hopper MAD. Receives natural language from Cursor (Cursor Era) or Henson (Autonomous Era), maintains project conversation state via Rogers, and dispatches to the appropriate internal flow.

- **`software_engineer`:** A `TaskAgent` subclass. The general-purpose execution agent. Handles all technical task execution: writing fixes, deploying code, running verifications, producing reviews. Internally dispatched by the Imperator or by `develop_software`. Not a front door agent.

**What Hopper is NOT:**
- Not a deployment engine. Starret owns git, merges, and CI/CD triggering.
- Not a long-term memory store. Rogers owns context assembly and knowledge graph.
- Not a human interface. Cursor (Cursor Era) or Henson (Autonomous Era) own user interaction.

---

## 2. The Hopper Imperator

### 2.1 Implementation: The Shared Agent Pattern

The Hopper Imperator is built using the same LangGraph base pattern defined in `mads/henson/docs/REQ-henson.md`. It uses the identical `ensure_rogers_session` and `fetch_rogers_context` nodes. The difference from Henson's personas is that the Imperator's inference node is a **tool-calling agent** dispatching to internal flows, not a conversational response node.

### 2.2 The `hopper_chat` MCP Tool

The only external MCP tool Hopper exposes.

- **Input:** Natural language from the user (via Cursor or Henson).
- **Process:**
  1. LangGraph fetches the Rogers context window for the ongoing project.
  2. **Dynamic model shifting:** A fast agentic model (e.g., GPT-4o) handles triage and tool dispatch. For complex strategic discussion, the Imperator shifts to a deep-reasoning model (e.g., Gemini Pro).
  3. **Dispatch:** The Imperator determines which flow to invoke based on the request.
- **Output:** Natural language responses and an SSE stream for real-time Quorum visibility.

### 2.3 Quorum Observability (SSE Streaming)

Hopper exposes a streaming SSE endpoint wrapping LangGraph's native `.astream_events()`. Any web page or Cursor session can subscribe to observe the Quorum in real time: genesis progress, review rounds, PM observations, consensus state.

### 2.4 The SDLC Conversation Flow

```
You: "Hey Hopper, build a network monitoring MAD."
Hopper: "Let's start with requirements..." → develop_software
  → Requirements (with your approval)
  → HLD (with your approval)
  → Code → Deploy → Test/Fix
  → "It's up. Go try it."

You: "Hopper, take care of Issue #212."
Hopper: "On it." → software_engineer
  → Reads issue, gathers context, writes fix, deploys, verifies.
  → "Issue #212 resolved."
```

---

## 3. The Four Components

Hopper's internal capability is organized as four components: two **primitive engines** that run the Quorum, and two **agents** that orchestrate work.

```
PRIMITIVES (Quorum engines):
  develop_doc          — DocumentQuorumGraph (docs, reviews, audits)
  develop_tech_asset   — CreativeQuorumGraph (code, test plans)

AGENTS (do the work):
  develop_software     — Full SDLC orchestrator. Calls both primitives.
  software_engineer    — TaskAgent. Execution and iteration. Calls both primitives as tools.
```

The Imperator dispatches directly to `develop_software` or `software_engineer` based on the request. The primitives are never called directly by the Imperator — only by the agents.

---

## 4. Primitive: `develop_doc`

The document-oriented Quorum engine. Used to create or improve any artifact that is primarily prose or structured text: requirements documents, HLDs, review reports, audit findings, design notes.

**Two-phase Lead structure:** Strategic thinking and prose writing are separated because they require different model strengths. The Lead thinks; the Writer writes.

### DocumentQuorum Phase Structure

- **Strategy**
  - Roles: Lead
  - Components: anchor_context, task_prompt
  - Instructions: *You are the Lead on a document development quorum. Your role is to think strategically before any prose is written. You have been given an anchor package containing the task context, constraints, and any relevant prior decisions. Your job in this phase is not to write the document — it is to produce a strategic skeleton that the Writer will use to produce the final prose. Deliver: a structured outline covering the key decisions, section headings, and the critical points each section must address. Bullet points only. No full prose sentences.*

- **Writing** *(initial)*
  - Roles: Writer
  - Components: anchor_context, task_prompt, strategy_skeleton
  - Instructions: *You are the Writer on a document development quorum. The Lead has produced a strategic skeleton and your job is to turn it into the final document. You have been given the anchor package and the Lead's strategic skeleton. Write clear, structured, unambiguous prose that faithfully executes the strategy. The document must be complete and ready for review. Deliver: the full document in final prose form.*

- **Review** *(parallel, independent)*
  - Roles: 3 Juniors
  - Components: anchor_context, task_prompt, lead_draft, issue_log
  - Instructions: *You are a Junior Reviewer on a document development quorum. Your review must be independent — do not try to guess what other reviewers will say. You have been given the anchor package, the current draft, and the open issue log from prior rounds. Start by checking every prior open issue: did the Writer address it? Is the resolution acceptable? Then review the full document for structure, clarity, completeness, and compliance with the anchor package constraints. Return STATUS: APPROVED only if all prior issues are closed satisfactorily and you have no new issues. Return STATUS: CHANGES REQUESTED otherwise. Tag every unresolved or new issue: [Issue N] description.*

- **PM Check**
  - Roles: PM
  - Components: reviewer_feedbacks, issue_log, round_number
  - Instructions: *You are the Process Manager on a quorum review. You have no engineering authority — you do not evaluate the quality of the work and you do not override the reviewers. You have been given the reviewer feedbacks, the current issue log, and the round number. Make two checks only: (1) Constraint violations — does any reviewer feedback ask for something that contradicts the anchor package constraints? If so, note it. (2) Gridlock — has any reviewer raised the same issue in a prior round without the Lead addressing it? If so, flag it by name and round. If you find nothing to report, say so briefly. Do not summarize the reviews. Do not restate what the reviewers said.*

- **Revision** *(loops until consensus or round 6)*
  - Roles: Writer
  - Components: anchor_context, task_prompt, lead_draft, reviewer_feedbacks, pm_guidance, issue_log
  - Instructions: *You are the Writer on a document development quorum. Your draft has been reviewed by three independent reviewers and the Process Manager has added observations. You have been given the anchor package, your current draft, the verbatim reviewer feedbacks, the PM's process observations, and the open issue log. Revise the draft to close all open issues. For each issue in the log respond explicitly: Fixed: [what you changed] / Denied: [rationale — must reference the anchor package] / Need more information: [what is needed]. Deliver: a revised draft with all issues dispositioned.*

### DocumentQuorum Model Roster

| Role | Model |
|---|---|
| Lead | Gemini Pro (`quorum-lead-strategy`) |
| Writer | Sonnet (`quorum-lead-prose`) |
| Junior — self-critique | Gemini Pro (`quorum-junior-self-critique`) |
| Junior — codex | GPT (`quorum-junior-codex`) |
| Junior — hybrid | Sonnet (`quorum-junior-prose`) |
| PM | Grok Fast (`quorum-pm`) |

---

## 5. Primitive: `develop_tech_asset`

The code-oriented Quorum engine with full Genesis. Used to create or improve any technical artifact that benefits from parallel brainstorming: source code, test plans, structured JSON outputs.

**Full Genesis is used because:** model diversity in parallel generation catches more problems than any single model reviewing its own work. Three models independently implementing the same feature will make three different architectural choices — the synthesis of the best of all three is structurally superior to any single draft.

**Self-critique phenomenon:** Including Gemini Pro as both Lead and a Junior is intentional. A model evaluating a completed artifact uses different attention pathways than the same model generating it. It reliably catches its own blind spots when in evaluation mode.

**No detailed design documents:** Because the LLM holds the entire HLD and codebase in context simultaneously, the human intermediate step of producing UML or function specs is unnecessary. The code is the detailed design.

### CreativeQuorum Phase Structure

- **Genesis** *(parallel, independent)*
  - Roles: Lead + 3 Juniors
  - Components: anchor_context, task_prompt
  - Instructions: *You are a participant in the genesis phase of a creative quorum. Every participant is working independently — you will not see anyone else's work at this stage. That independence is the point: maximum diversity of approach produces a structurally superior synthesis. You have been given the anchor package and the task. Produce a complete, fully working draft entirely on your own terms. Make your own architectural choices. Do not hedge toward what you think others might produce. Deliver: a complete draft.*

- **Cross-Pollination** *(parallel)*
  - Roles: 3 Juniors
  - Components: anchor_context, task_prompt, all genesis_drafts
  - Instructions: *You are a Junior on a creative quorum in the cross-pollination phase. The genesis phase is complete and you can now see all peer drafts. You have been given the anchor package, the task, and all genesis drafts. Read them carefully. Your job is to revise your own draft — not copy, not merge — by adopting the best ideas from your peers and rejecting weak ones. When you adopt a peer idea explain briefly why. Deliver: your revised draft, improved by cross-pollination.*

- **Synthesis** *(initial)*
  - Roles: Lead
  - Components: anchor_context, task_prompt, all genesis_drafts, all revised_drafts
  - Instructions: *You are the Lead on a creative quorum in the synthesis phase. Genesis and cross-pollination are complete. You have the full set of independent and revised drafts in front of you simultaneously. Your job is to synthesize a single master draft that is holistically superior to any individual contribution. This is not a merge or a majority vote — you select the best architecture, the best implementation choices, the clearest patterns from across all drafts and combine them into one coherent whole. Deliver: the master draft.*

- **Review** *(parallel, independent)*
  - Roles: 3 Juniors
  - Components: anchor_context, task_prompt, lead_draft, issue_log
  - Instructions: *You are a Junior Reviewer on a creative quorum. Your review must be independent — do not try to guess what other reviewers will say. You have been given the anchor package, the current master draft, and the open issue log from prior rounds. Start by checking every prior open issue: did the Lead address it? Is the resolution acceptable? Then review the full draft for correctness, architecture, edge cases, and test coverage. Return STATUS: APPROVED only if all prior issues are closed satisfactorily and you have no new issues. Return STATUS: CHANGES REQUESTED otherwise. Tag every unresolved or new issue: [Issue N] description.*

- **PM Check**
  - Roles: PM
  - Components: reviewer_feedbacks, issue_log, round_number
  - Instructions: *(same as DocumentQuorum PM — see above)*

- **Revision** *(loops until consensus or round 6)*
  - Roles: Lead
  - Components: anchor_context, task_prompt, lead_draft, reviewer_feedbacks, pm_guidance, issue_log
  - Instructions: *You are the Lead on a creative quorum. Your master draft has been reviewed by three independent reviewers and the Process Manager has added observations. You have been given the anchor package, your current master draft, the verbatim reviewer feedbacks, the PM's process observations, and the open issue log. Revise the master draft to close all open issues. For each issue respond explicitly: Fixed: [what you changed] / Denied: [rationale — must reference the anchor package] / Need more information: [what is needed]. Deliver: a revised master draft with all issues dispositioned.*

### CreativeQuorum Model Roster

| Role | Model |
|---|---|
| Lead | Gemini Pro (`quorum-lead-strategy`) |
| Junior — self-critique | Gemini Pro (`quorum-junior-self-critique`) |
| Junior — codex | GPT (`quorum-junior-codex`) |
| Junior — hybrid | Sonnet (`quorum-junior-prose`) |
| Junior — grok | Grok (`quorum-junior-grok`) |
| PM | Grok Fast (`quorum-pm`) |

---

## 6. Agent: `develop_software`

The full SDLC orchestrator. Called when the user wants to create or significantly update a software system. Sequences calls to both primitives and spawns `software_engineer` for execution.

**Flow:**
```
1. Requirements (develop_doc — interactive human loop)
   Claude Sonnet leads prose. GPT-5.x reviews for logic gaps.
   Questions returned to Cursor → user answers → loop until zero questions.
   User explicitly approves REQ document.

2. Architecture (develop_doc)
   Gemini Pro leads strategy. Sonnet writes prose.
   User explicitly approves HLD.

3. Implementation (develop_tech_asset)
   Full Genesis code quorum against the approved HLD.
   Internal Quorum consensus is sufficient — no user approval gate.

4. Test Planning (develop_tech_asset)
   Full Genesis test plan quorum.
   Output: ephemeral-test-plan.json

5. Execution (software_engineer)
   Spawns a software_engineer instance.
   software_engineer deploys, tests, iterates until green.
   Reports back to develop_software when complete.

6. Completion
   develop_software reports to Imperator: "It's up."
   Imperator tells user.
```

**Human approval gates:** Requirements and HLD only. Code generation, test planning, deployment, and the test/fix loop run fully autonomously.

---

## 7. Agent: `software_engineer`

A `TaskAgent` subclass. The general-purpose technical execution agent. Handles all work that requires reading files, writing code, calling Starret, running verifications, and iterating. Dispatched both by the Imperator directly (for standalone tasks) and by `develop_software` (as the execution phase of the SDLC).

### 7.1 Classification

`software_engineer` is NOT an Imperator. It is a `TaskAgent` — internally dispatched, not a front door agent. It follows the same base `JoshuaAgent` pattern (Rogers context, Sutherland inference) but its role is execution, not conversation management. See `HLD-joshua26-agent-architecture.md`.

### 7.2 Dynamic Instruction Construction

There is no physical "Instruction Set Library" file system directory. Instead, the intelligence for orchestrating `software_engineer` tasks lives within the Imperator's `personas.json` configuration.

When the Imperator decides to invoke `software_engineer`, it dynamically constructs the required parameters based on the user's intent and context:
- `system_prompt`: Specific instructions for the task (e.g., "You are fixing a test failure. Read the logs, write the fix, and deploy.")
- `model`: The appropriate Sutherland alias for the complexity of the task.
- `tools`: The specific subset of tools the agent needs for this execution.

This makes `software_engineer` a highly adaptive, generic executor rather than a script runner tied to static markdown files.

### 7.3 Tool Set

```
Tools available to software_engineer:
  — read_file(path) / write_file(path, content)
  — call_starret(message, repo?)   — git operations via natural language (commit, push, branch, PR, merge)
  — starret_github(action, params) — single Starret tool for all GitHub API: get_issue, get_pr_comments,
      create_issue, post_pr_comment, write_metadata_comment, add_label, close_issue, etc.
  — run_tests(test_plan)
  — develop_doc(anchor, instructions)    — for producing review/audit documents
  — develop_tech_asset(anchor, instructions)  — for complex design escalation
```

### 7.4 The Fix and Deploy Loop

The core execution loop of `software_engineer`:

```
1. Select instruction set
2. Gather context (using read tools as guided by instruction set)
3. Assess: can I handle this myself or do I need develop_tech_asset?
   — Simple: write the fix directly
   — Complex: call develop_tech_asset for design; apply the result
4. Call Starret to deploy
5. Run tests
6. If green: done. Report back.
7. If red: back to step 3 with new test failure evidence.
8. If escalation exhausted: create GitHub Issue (quorum-impasse). Halt.
```

**Key distinction on escalation:** When `software_engineer` escalates to `develop_tech_asset`, it is not saying "I can't write the code." It is saying "I can't figure out the right solution." The Quorum provides design authority. The agent remains the executor — it writes the files the Quorum produces, calls Starret, and runs the tests.

### 7.5 Reviews and Audits via `develop_doc`

Reviews and audits are not a separate flow. They are tasks `software_engineer` handles using `develop_doc` as a tool. When asked to review a PR or audit a deployment, the agent:

1. Selects the appropriate instruction set (e.g., `review-code.md`, `audit-deployment.md`).
2. Gathers the evidence the instruction set requires (PR diff, Hypatia state, logs, etc.).
3. Calls `develop_doc` with the evidence as the Anchor Package and the instruction set as the Instructions.
4. Routes the `develop_doc` output to the appropriate GitHub destination (PR review thread, GitHub Issue, health confirmation).

---

## 8. The Quorum Mechanics

Shared by both `develop_doc` and `develop_tech_asset`.

### 8.1 The Anchor Package

The Anchor Package is the consolidated block of data that puts all Quorum participants on exactly the same page before generation begins. Every participant receives the identical package. See `docs/concepts/concept-anchor-package.md` for the full concept definition.

For Hopper's Quorums, the package is assembled by the orchestrating agent or StateGraph process that owns the Quorum — not by Rogers. Assembly may be schema-driven (fixed components always included, such as ecosystem architecture documents and REQ-000 compliance rules), reason-driven (the agent selects components based on the specific task), or a hybrid of both.

Typical contents for a Hopper Quorum anchor package:
- The MAD-specific HLD and REQ document for the system under work
- REQ-000 compliance rules
- Relevant past precedents and prior decisions (which may be retrieved from Rogers as components)
- The specific task specification or artifact under review
- Work instructions or scope constraints for this Quorum instance

Rogers may supply retrieved memory and conversation history as *components* that Hopper draws on during assembly. Rogers does not assemble the package — that responsibility belongs to the orchestrator, which alone understands what the Quorum is being anchored to.

**Critical rule:** Junior Reviewers receive only the Anchor Package plus the current artifact — never their own prior conversational history. This preserves maximum context window space for engineering work.

### 8.2 The PM (Process Manager — Advisory Only)

The PM is a **text-in/text-out LLM invocation**. Not an agent. No tool access. LangGraph invokes it between Reviewer outputs and the Lead's next iteration. Its output (`pm_guidance`) is assembled into the lead's revision prompt alongside the verbatim reviewer feedbacks.

**The PM's job (strictly):**
- Observe whether reviewer feedback violates the Anchor Package constraints.
- Detect gridlock: same reviewer raising the same issue 2+ rounds without disposition.
- Return brief observational notes only.

**The PM's absolute constraints:**
- Zero engineering authority.
- Does NOT determine consensus — that is determined programmatically from reviewer STATUS fields.
- Does NOT summarize, paraphrase, or prioritize feedback.
- Does NOT restate what reviewers said — only flags violations and gridlock.

**Model:** Grok 4 Fast or equivalent. Must have massive context (reads all reviewer outputs simultaneously). Must NOT be a reasoning model — it would attempt to engineer solutions. The PM is the non-technical Project Manager in a room of engineers. Its value is entirely in process observation.

### 8.3 The Issue Log

The Quorum communicates through a typed Issue Log, not unstructured chat.

- **Reviewers** append items: `[Issue N] <description>`
- **The Lead** addresses every open item with an explicit status:
  - `Fixed: <explanation>`
  - `Need more information: <what is needed>`
  - `Denied: <rationale referencing HLD or REQ-000>`
- **Consensus** is determined programmatically: all reviewers return `STATUS: APPROVED`. The PM has no vote.

**Persistence:** GitHub PR Review Comment Threads (code reviews) or GitHub Issues tagged `quorum-generated` (design/architecture). No custom database. GitHub is the permanent, searchable record of every architectural decision debated.

### 8.4 Graduated Safety Valve

| Round | Mode | PM Behavior |
|-------|------|-------------|
| 1–3 | Open iteration | Scope filtering only. |
| 4–5 | Warning phase | PM actively identifies degrading/locked loops. |
| 6 | Hard stop | Rollback. GitHub Issue (`quorum-impasse`). Human intervention required. |

A Round 6 impasse indicates a genuine architectural disagreement, not a code bug.

### 8.5 Quorum as Design Pattern

The Quorum is a library of reusable LangGraph nodes, not a parameterized god-object. Reusable nodes: `assemble_anchor_context`, `invoke_genesis_parallel`, `invoke_cross_pollination`, `invoke_lead_synthesis`, `invoke_parallel_reviewers`, `invoke_pm_check`, `evaluate_consensus`.

Two distinct graphs built from those nodes:
- `DocumentQuorumGraph` — used by `develop_doc`
- `CreativeQuorumGraph` — used by `develop_tech_asset`

---

## 9. State Management

Hopper is a **stateless MAD**. No `hopper-postgres`. No `hopper-redis`.

| State Type | Where It Lives |
|-----------|----------------|
| Ongoing project conversation | Rogers (`conv_store_message`) |
| Quorum context windows | Rogers (`conv_retrieve_context`) |
| Quorum execution metadata (Rogers conversation ID, round count) | Hidden HTML comment in GitHub PR/Issue (`<!-- JOSHUA26_METADATA_START -->`) |
| Issue Log (in-flight) | LangGraph state object (JSON array) |
| Issue Log (permanent) | GitHub PR Review Threads or GitHub Issues |
| Past architectural decisions | Rogers Knowledge Graph (Mem0 extraction) |

If Hopper restarts mid-Quorum, it reads the GitHub comment to recover the Rogers conversation ID and resumes from the last known Issue Log state.

---

## 10. Container Composition and Identity

**Registry Allocation:**
- **UID:** 2034
- **GID:** 2001 (administrators)
- **Port:** 9225 (MCP Gateway)
- **Host:** m5

| Container | Role |
|-----------|------|
| `hopper` | MCP Gateway (Envoy). Exposes `hopper_chat` and SSE stream on `joshua-net`. |
| `hopper-langgraph` | Python. Runs the Imperator, the four components, and the two Quorum graphs. |

No database containers. All state is owned by Rogers and GitHub.

---

## 11. Model Roster

All models accessed via Sutherland aliases. Changing a model requires only a database update in `sutherland-postgres`.

| Alias | Role | Current Target |
|-------|------|----------------|
| `quorum-lead-strategy` | Phase 1 Lead in DocumentQuorumGraph; Lead in CreativeQuorumGraph | Gemini Pro |
| `quorum-lead-prose` | Phase 2 Lead in DocumentQuorumGraph | Sonnet |
| `quorum-junior-codex` | Junior — coding specialist | GPT Codex |
| `quorum-junior-self-critique` | Junior — self-critique instance of lead | Gemini Pro |
| `quorum-junior-prose` | Junior — prose + code hybrid | Sonnet |
| `quorum-junior-grok` | Junior — diverse coding model | Grok |
| `quorum-pm` | Process Manager | Grok Fast |
| `imperator-fast` | Imperator triage and dispatch | GPT |
| `imperator-strategy` | Imperator deep strategic discussion | Gemini Pro |

---

## 12. Security and Isolation

- **No GitHub merge rights.** Hopper reads PRs and writes comments. Merges are exclusively Starret's domain.
- **No direct internet access.** All external calls route through Joshua26 caching proxies or `joshua-net`.
- **No direct database access to other MADs.** All cross-MAD calls traverse MCP via the peer proxy pattern (ADR-053).
- **Workspace volume access.** Hopper requires `/workspace` mount for source file read/write during code generation.

---

## Appendix A: Phase C Implementation Details

### A.1 `hopper_chat` MCP Tool Schema

```json
{
  "name": "hopper_chat",
  "description": "The primary conversational interface to the Hopper Engineering Department. Use this to request software development, code reviews, bug fixes, or architectural design.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "message": {
        "type": "string",
        "description": "The natural language request or instruction for Hopper."
      },
      "project_context": {
        "type": "string",
        "description": "Optional. The name of the MAD or project this request pertains to."
      }
    },
    "required": ["message"]
  }
}
```

### A.2 LangGraph State Definitions

**ImperatorGraphState:**
```python
class ImperatorGraphState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    rogers_conversation_id: str
    active_project: str | None
    current_flow: str | None  # e.g., 'develop_software', 'software_engineer'
```

**QuorumGraphState:**
```python
class QuorumGraphState(TypedDict):
    anchor_context: str
    task_prompt: str
    lead_draft: str | None
    reviewer_feedbacks: list[str]
    pm_guidance: str | None
    issue_log: list[dict]
    round_number: int
    status: str  # 'in_progress', 'consensus', 'safety_valve'
```

### A.3 `config.json` Skeleton

```json
{
  "port": 9225,
  "tools": [
    {
      "name": "hopper_chat",
      "target": "http://hopper-langgraph:8000",
      "path": "/chat"
    }
  ],
  "dependencies": {
    "rogers": "http://rogers:6380/health",
    "sutherland": "http://sutherland:11435/health"
  }
}
```

### A.4 Verification Plan

- **Unit Testing:** `pytest` coverage for the PM Layer scope filtering and gridlock detection logic.
- **Integration Testing:**
  - Verify `hopper_chat` successfully retrieves context from Rogers.
  - Verify the Quorum Engine correctly invokes Sutherland aliases in parallel.
  - Verify SSE streaming accurately broadcasts state changes.
- **State Verification:** Ensure the `rogers_conversation_id` is correctly persisted in GitHub PR/Issue hidden comments and retrieved upon restart.
