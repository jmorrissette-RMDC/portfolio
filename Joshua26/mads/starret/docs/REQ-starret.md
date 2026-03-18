# Requirements: Starret (The Release Department)

**Version:** 1.1
**Date:** 2026-03-09
**Status:** Approved
**Related Documents:** HLD-software-factory-core.md, HLD-cicd-architecture.md, mads/hopper/docs/REQ-hopper.md

**Supersedes:** REQ-007-starret-git-safety-net.md, REQ-020-starret-git-cicd-upgrade.md (both archived)

---

## 1. Purpose and Architectural Rationale

### 1.1 The Release Department

Starret owns the complete release lifecycle for Joshua26: git operations, GitHub API interactions, and deployment triggering. It is the only MAD in the ecosystem with the authority to commit, push, merge, and trigger CI/CD. This centralization is intentional — it creates a single, intelligent control point that enforces repository rules and deployment safety for all callers, regardless of whether the caller is Hopper's `software_engineer`, Cursor, or a future automated agent.

**What Starret is NOT:**
- Not an engineering agent. Starret does not write code, review code, or produce test plans. Hopper owns those.
- Not a long-term memory store. Starret is stateless. GitHub is the database.
- Not a human interface. Callers interact with Starret via MCP tools.

### 1.2 The Two-Tool Design

Starret exposes exactly two external MCP tools:

| Tool | What it handles |
|------|-----------------|
| `starret_chat` | Git operations — commit, push, branch, PR, merge, deploy trigger. Handled by the Starret Imperator. |
| `starret_github` | GitHub API — all structured reads and writes against the GitHub REST API. |

**Why two tools and not one?**

Git operations require reasoning: the Imperator must inspect local filesystem state (branch, dirty working tree, untracked files), resolve ambiguity, enforce branch protection rules, and sequence operations correctly. This is conversational and stateful — it earns an Imperator.

GitHub API operations are structured database calls: fetch issue #212, post comment to PR #45, write metadata block to issue body. No reasoning required. A single parameterized tool handles the full action set.

**Why not atomic tools for git?**

Exposing atomic git tools externally hands the sequencing logic and rule enforcement to the caller. Every caller would need to understand git state, ordering, and Starret's safety rules. The Imperator is the enforcement layer — it is the only code that reasons about git state.

---

## 2. The Starret Imperator (`starret_chat`)

### 2.1 Architecture

The Starret Imperator follows the same LangGraph pattern as the Hopper Imperator (`mads/hopper/hopper-langgraph/flows/imperator.py`).

- **External surface:** One MCP tool: `starret_chat`
- **Internal:** LangGraph graph running in `starret-langgraph` container
- **Internal tools (not exposed):** Git CLI subprocess calls, GitHub API calls
- **State:** Stateless. No database. Conversation context via Rogers if needed.

### 2.2 `starret_chat` MCP Tool

```json
{
  "name": "starret_chat",
  "description": "The primary interface to Starret's git and deployment capabilities. Use natural language to commit, push, create branches, manage PRs, merge, or trigger deployments.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "message": {
        "type": "string",
        "description": "Natural language instruction. Examples: 'commit and push my hopper changes', 'create a PR for this branch', 'merge PR #45'."
      },
      "repo": {
        "type": "string",
        "description": "Optional. Repository path or name. Defaults to Joshua26."
      }
    },
    "required": ["message"]
  }
}
```

### 2.3 What the Imperator Handles

The Imperator receives a natural language instruction and reasons about git state to execute it safely:

**Commit and push:**
```
Caller: "commit and push my hopper changes"
Imperator: inspects git status
  → uncommitted changes in mads/hopper/: commit with message describing changes
  → uncommitted changes in mads/sutherland/ also present:
      "I see uncommitted changes in mads/sutherland/ — were those intentional?"
  → caller: "leave that alone, just push my stuff"
  → stages only mads/hopper/, commits, pushes
  → returns: push confirmed, SHA, URL
```

**Branch operations:**
```
Caller: "create a feature branch for issue #212"
Imperator: checks current branch, creates branch from main, confirms
```

**PR management:**
```
Caller: "create a PR for this branch"
Imperator: checks what's been pushed, drafts PR title and body from commit history, creates PR
```

**Merge:**
```
Caller: "merge PR #45"
Imperator: checks CI status, checks approvals, enforces safety rules, merges
  → push to main triggers runner automatically (on: push: branches: [main])
  → no explicit workflow_dispatch needed for normal deploys
```

**Forced deploy (rollback or re-deploy specific version):**
```
Caller: "re-deploy the last known good version of hopper"
Imperator: calls GitHub workflow_dispatch with specific ref/inputs
```

### 2.4 Branch and Repository Rules

The Imperator enforces these rules unconditionally. No caller can bypass them:

- No direct commits to `main`. All changes go through a feature branch + push.
- No force-pushes to protected branches.
- PR required before merge to `main`.
- CI checks must pass before merge (unless explicitly overridden with reason).
- No committing `.env` files, credentials, or secrets.

### 2.5 Git Safety Mechanisms (REQ-000 §7.7)

The Imperator implements the required safety features for git-modifying MADs:

- **Backup branch:** Create a backup branch before any destructive operation (e.g. before merge or force-push recovery).
- **Dry-run:** Support a dry-run mode (or equivalent) so callers can preview what would happen without applying changes.
- **Rollback:** Document or support rollback capability to restore previous state when applicable.
- **User confirmation:** Require explicit confirmation (or structured approval) for destructive operations before proceeding.
- **Logging:** All git operations logged with commit hashes and operation type for audit.

### 2.6 The Deployment Model

**Normal deploy path:** Push to `main` → GitHub Actions runner picks up the `on: push` trigger automatically → builds → `deploy.py` → done. The Imperator does not need to call `workflow_dispatch` for this path. The agent just pushes and it deploys.

**Ad-hoc / rollback path:** The Imperator calls `workflow_dispatch` with specific inputs when a caller needs to deploy a specific version, trigger a rollback, or re-run a deploy without a new commit.

---

## 3. The GitHub API Tool (`starret_github`)

### 3.1 `starret_github` MCP Tool

A single parameterized tool covering the full GitHub API surface that Hopper and other callers need.

```json
{
  "name": "starret_github",
  "description": "Structured GitHub API operations. Use for reading issues, PR comments, and status, and for writing issues, comments, and metadata.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "action": {
        "type": "string",
        "enum": [
          "get_issue",
          "get_pr_status",
          "get_pr_comments",
          "list_prs",
          "read_metadata_comment",
          "create_issue",
          "post_pr_comment",
          "write_metadata_comment",
          "add_label",
          "close_issue"
        ]
      },
      "params": {
        "type": "object",
        "description": "Action-specific parameters."
      }
    },
    "required": ["action", "params"]
  }
}
```

### 3.2 Action Reference

#### Read Actions

**`get_issue`**
```
params:  { repo, issue_number }
returns: { number, title, body, state, labels, assignees, author, created_at, comments: [...] }
```
*Use case: Hopper's `software_engineer` reads an issue before creating a branch and writing a fix.*

---

**`get_pr_status`**
```
params:  { repo, pr_number }
returns: { number, title, state, mergeable, checks: [...], reviews: [...], url }
```
*Use case: Checking CI status before merging.*

---

**`get_pr_comments`**
```
params:  { repo, pr_number }
returns: { review_comments: [...], issue_comments: [...], reviews: [...] }
```
*Use case: Hopper reads quorum output posted as a PR comment and uses it for the next fix iteration.*

---

**`list_prs`**
```
params:  { repo, state?, author?, limit? }
returns: { prs: [{ number, title, author, state, created_at, url }] }
```

---

**`read_metadata_comment`**
```
params:  { repo, issue_or_pr_number, type: "issue" | "pr" }
returns: { metadata: object | null }
```
*Use case: Hopper recovers mid-Quorum state after a restart by reading the hidden HTML metadata block it previously wrote to the PR.*

---

#### Write Actions

**`create_issue`**
```
params:  { repo, title, body, labels?, assignees? }
returns: { issue_number, issue_url }
```
*Use case: Hopper creates a `quorum-impasse` issue when the Quorum Engine reaches safety valve after 6 rounds.*

---

**`post_pr_comment`**
```
params:  { repo, pr_number, body, comment_type: "issue_comment" | "review_comment", path?, line? }
returns: { comment_id, comment_url }
```
*Use case: Hopper posts quorum output (Issue Log, review findings) to the PR thread.*

---

**`write_metadata_comment`**
```
params:  { repo, issue_or_pr_number, type: "issue" | "pr", metadata: object }
returns: { success }
```
*Writes or updates the hidden HTML metadata block (`<!-- JOSHUA26_METADATA_START -->...<!-- JOSHUA26_METADATA_END -->`) in the PR/Issue body. Used by Hopper to persist Quorum execution state (Rogers conversation ID, round count, Issue Log) so the Quorum can resume after a Hopper restart.*

---

**`add_label`**
```
params:  { repo, issue_or_pr_number, labels: string[] }
returns: { success }
```

---

**`close_issue`**
```
params:  { repo, issue_number, comment? }
returns: { success }
```

---

## 4. REQ-000 Compliance Notes

### 4.1 LLM Routing (REQ-000 §4.10)

All LLM inference calls from `starret-langgraph` must route through **Sutherland**, not directly to any external LLM API. The Imperator LangGraph graph uses Sutherland as its inference backend (via the Sutherland MCP endpoint on `joshua-net`).

### 4.2 Prometheus Metrics (REQ-000 §4.11)

`starret-langgraph` exposes `/metrics` (Prometheus text format) and `/metrics_get` (MCP tool). Both must invoke a compiled StateGraph (`graph.ainvoke()`) — no direct calls to `prometheus_client.generate_latest()` outside a StateGraph node. There is no pre-built Prometheus exporter for the git/GitHub domain, so metrics collection is implemented inside LangGraph.

### 4.3 Gateway Pattern (REQ-000 §4.5/4.8)

Starret uses **Nginx as its MCP gateway** (State 2 pattern). REQ-000 §4.5/4.8 describe a Node.js + `config.json` thin gateway pattern (State 1). These requirements are **N/A for Starret** — the State 2 Nginx gateway is the fully compliant equivalent for a State 2 MAD.

### 4.4 Build Quality (REQ-000 §1.8/1.9/1.10)

All Python in `starret-langgraph` must pass:
- `black --check .` (formatting)
- `ruff check .` (linting)
- `pytest` with tests covering happy path and error conditions for all programmatic logic

### 4.5 Async Correctness (REQ-000 §7.9)

Git subprocess calls inside `async` LangGraph nodes must use `asyncio.create_subprocess_exec()`, not `subprocess.run()`. No blocking I/O in async context.

### 4.6 Exception Handling (REQ-000 §5.10/5.11)

- Catch specific exceptions (e.g. `subprocess.SubprocessError`, `aiohttp.ClientError`) — no bare `except Exception:`.
- Use context managers or `try...finally` for all external resources (file handles, subprocess streams).

---

## 5. Container Composition and Identity

**Registry Allocation:**
- **UID:** 2001
- **GID:** 2001 (administrators) — per registry.yml and REQ-000 §2
- **Port:** 8010 (MCP Gateway)
- **Host:** irina

| Container | Role |
|-----------|------|
| `starret` | MCP Gateway (Nginx). Exposes `starret_chat` and `starret_github` on `joshua-net`. |
| `starret-langgraph` | Python. Runs the Imperator and git operation flows. All LLM calls route through Sutherland (REQ-000 §4.10). |
| `github-runner` | GitHub Actions runner. Backing container in Starret MAD group. Not exposed on `joshua-net`. |

No database containers. Starret is stateless — GitHub is the database.

---

## 6. The GitHub Actions Runner

The runner is a **backing container in the Starret MAD group**, not a standalone MAD.

- **Lives on `starret-net` only** — no backing container may attach to `joshua-net` (REQ-000 §7.4.1). The gateway is the sole network boundary. joshua-net is MCP-only.
- Access to peers (Alexandria for package caches and image registry) is **via the Starret gateway peer proxy only**. Those services are **MCP peers** on joshua-net (not plain HTTP). Runner calls the gateway’s `/peer/{peer}/{tool}` on `starret-net`; the gateway proxies MCP to the peer.
- Polls GitHub outbound — no inbound ports, no webhooks
- SSH key volume for `deploy.py` (SSHes to irina, m5, runs `docker compose` per host)
- **Bare-metal runner installs are forbidden**

**See:** `docs/requirements/proposed/REQ-023-github-runner.md`

---

## 7. Security

### GitHub Token (REQ-000 §3.5, §3.6)
- Token is **loaded from `/storage/credentials/starret/` at startup** (e.g. from a JSON or text file). No credentials in environment variables, code, or images (REQ-000 §3.5, §3.6).
- Scopes required: `repo`, `workflow` (for ad-hoc `workflow_dispatch`), `issues`
- Token never logged, never returned to callers

### Branch Protection
The Imperator enforces branch protection in software, independent of GitHub branch protection settings. Even if GitHub branch rules were misconfigured, the Imperator would still refuse to commit directly to `main`.

### Caller Trust
Starret does not authenticate callers. All callers on `joshua-net` are trusted by network position. The Imperator applies its own rules regardless of who is calling.

### Conversation Data (REQ-000 §7.8)
Starret does **not** produce conversation data for Rogers. Tool responses are returned to the caller; the caller (e.g. Hopper) retains conversation context. REQ-000 §7.8 does not apply.

### Degraded Behavior (REQ-000 §7.1)
When GitHub API or the runner is unavailable, the gateway reports degraded health (dependency down). `starret_chat` and `starret_github` return explicit errors to the caller; the MAD does not crash. Internal dependency map: gateway (critical) → starret-langgraph (critical) → runner / GitHub (soft; deploy can be retried later).

---

## 8. Relationship to Hopper

Hopper's `software_engineer` is the primary caller of both Starret tools:

```python
# In agents.py — git operations
result = await call_peer_tool("starret", "starret_chat", {"message": "commit and push my hopper changes"})

# In agents.py — GitHub API
result = await call_peer_tool("starret", "starret_github", {
    "action": "get_issue",
    "params": {"repo": "Joshua26", "issue_number": 212}
})
```

The existing `call_starret` implementation in Hopper (`agents.py` line 290–299) will be updated to use `starret_chat`. The `read_github_issue` and `read_pr_comment_thread` stubs will be replaced with `starret_github` calls.

---

## Appendix A: Verification Plan

- `starret_chat`: verify commit-and-push with clean working tree
- `starret_chat`: verify dirty working tree triggers clarifying question
- `starret_chat`: verify direct-to-main commit is blocked
- `starret_github get_issue`: verify returns full issue body and comments
- `starret_github create_issue`: verify issue created with correct labels
- `starret_github write_metadata_comment` + `read_metadata_comment`: verify round-trip persistence of Quorum metadata
- Runner: verify `on: push: branches: [main]` trigger fires without explicit `workflow_dispatch`
- Runner: verify `deploy.py` executes correctly via SSH on both irina and m5
