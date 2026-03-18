# High-Level Design: Software Factory Core

**Version:** 1.2
**Date:** 2026-03-11
**Status:** Active — Kaiser deployed 2026-03-11; Alexandria deployed 2026-03-09
**Scope:** Kaiser (eMAD host) · Hopper (eMAD library) · Starret · Alexandria · Henson (UI) · Cursor (MCP client)
**Related Documents:** HLD-conversational-core.md, HLD-cicd-architecture.md, HLD-unified-package-caching.md, HLD-state3-mad.md

---

## 1. Purpose and Scope

This document is the macro-architecture reference for the Joshua26 **Software Factory** — the pMADs and eMADs responsible for building, reviewing, testing, and shipping software. It is the counterpart to `HLD-conversational-core.md`, which covers the conversational infrastructure (Henson, Rogers, Sutherland).

The Software Factory covers:

| Concern | Owner |
|---|---|
| Engineering intelligence (quorum, SDLC orchestration) | Hopper eMAD (hosted by Kaiser) |
| eMAD lifecycle and hosting | Kaiser |
| Release mechanics (git, PR, CI/CD trigger, runner) | Starret |
| Long-term project memory and context | Rogers (shared with Conversational Core) |
| AI compute (model inference for quorum models) | Sutherland (shared with Conversational Core) |
| Package caching (PyPI, NPM, Docker) | Alexandria (alexandria-devpi + alexandria-verdaccio + alexandria-registry) |
| Human interface | Henson (design target from day one) |
| Transitional MCP client | Cursor (used while Henson is being built) |

---

## 2. The "One pMAD, One Domain" Principle

Each pMAD owns exactly one domain. The constraints below are architectural invariants, not implementation preferences.

### 2.1 Hopper — The Engineering Department

**Role:** Hopper is the autonomous engineering capability of Joshua26. It takes a requirement from human intent all the way to a deployed, tested system, requiring the human only at approval gates. It runs the Unified Quorum Engine — multi-LLM parallel drafts, adversarial cross-review, and PM-mediated consensus.

**Constraints:**
- **No deployment ownership.** Hopper does not merge PRs, trigger CI/CD, or SSH to hosts. Starret owns all of that.
- **No long-term memory.** Hopper does not store conversation history or project state. Rogers owns context assembly and knowledge graphs.
- **No human interface.** Hopper does not serve a UI. Henson is the interface. Cursor is the transitional MCP client.

### 2.2 Starret — The Release Department

**Role:** Starret owns the full release lifecycle: git operations, PR management, merge execution, CI/CD triggering, and deployment. It exposes MCP tools that Hopper calls to commit, push, merge, and deploy. It also owns the GitHub Actions runner as a backing container.

**Constraints:**
- **No engineering intelligence.** Starret does not analyze code, generate reviews, or produce test plans. Hopper does that.
- **No bare-metal runner.** The GitHub Actions runner is a Starret backing container, not a bare-metal install. No process on a host machine is in the runner's blast radius.

### 2.3 Alexandria — The Supply Chain Wall

**Role:** Alexandria is the unified external package caching layer. It is a single pMAD (deployed 2026-03-09) with three backing containers:
- **alexandria-devpi** — PyPI caching proxy (Devpi). `PIP_INDEX_URL=http://irina:3141/root/pypi/+simple/`
- **alexandria-verdaccio** — NPM caching proxy (Verdaccio). `NPM_CONFIG_REGISTRY=http://irina:4873`
- **alexandria-registry** — Docker image registry (Registry 2.0). `irina:5000`

Cache ports (3141/4873/5000) are host-bound directly from the backing service containers. The `alexandria` nginx gateway exposes only the MCP port (9229). See `mads/alexandria/docs/REQ-alexandria.md`.

**Constraints:**
- **No model caching.** All HuggingFace / ML model caching lives in **Sutherland**. Alexandria does not own HF. Any env var or config pointing `HF_ENDPOINT` at Alexandria is incorrect.

### 2.4 Rogers — The Memory Layer (Shared)

Rogers is defined fully in `HLD-conversational-core.md`. In the Software Factory context, Rogers is the context broker for Hopper's TE — storing the ongoing engineering dialogue, requirement threads, and decision history for each project. Hopper's Imperator calls `conv_retrieve_context` on startup like every other Imperator in the ecosystem.

### 2.5 Sutherland — The Compute Layer (Shared)

Sutherland is defined fully in `HLD-conversational-core.md`. In the Software Factory context, Sutherland is the inference broker for Hopper's TE — all quorum model calls (Lead, Reviewer Alpha, Reviewer Beta, Executor) resolve their model aliases through Sutherland. No TE in the ecosystem calls an LLM endpoint directly. Sutherland also owns all model caching (HuggingFace downloads, GGUF files, etc.).

### 2.6 Henson — The Human Interface (Design Target)

**Role:** Henson hosts the UI for all human interaction with the Software Factory. The Hopper Imperator is designed to serve Henson from day one — it exposes `hopper_chat` as an MCP tool with SSE streaming for real-time Quorum observability directly in the Henson UI.

**Design choice:** There are no "eras" — Henson is the target from the start. The Hopper REQ is written for Henson as the interface. Cursor serves as the MCP client while Henson is being built (see §4 below).

### 2.7 Cursor — The Transitional MCP Client

Cursor (Composer) can call `hopper_chat` and other Starret tools via MCP (JSON-RPC / curl) before Henson is deployed. This is a practical bridging mechanism, not an architectural target. Once Henson is running, Cursor continues to be useful for local development sessions but is no longer the primary interface.

---

## 3. Network and Container Architecture

The Software Factory pMADs follow the same isolation pattern defined in `HLD-conversational-core.md` §4.

### 3.1 pMAD Container Groups

```
Starret pMAD group (on irina):
  starret          — MCP Gateway (joshua-net + starret-net)
  starret-langgraph — LangGraph orchestrator (starret-net)
  github-runner     — GitHub Actions runner (starret-net, outbound only)

Kaiser pMAD group (on m5) — eMAD host (State 3):
  kaiser           — MCP Gateway (joshua-net + kaiser-net, port 9226)
  kaiser-langgraph — Bootstrap kernel + eMAD registry (kaiser-net)

  Hopper eMAD (hosted by Kaiser — no standalone containers):
    hopper-emad    — TE package installed from Alexandria via install_stategraph()

Alexandria pMAD group (on irina):
  alexandria           — nginx MCP gateway (joshua-net + alexandria-net, port 9229)
  alexandria-langgraph — LangGraph + Imperator (alexandria-net)
  alexandria-devpi     — PyPI caching proxy (alexandria-net, host-bound :3141)
  alexandria-verdaccio — NPM caching proxy (alexandria-net, host-bound :4873)
  alexandria-registry  — Docker image registry (alexandria-net, host-bound :5000)
```

### 3.2 The GitHub Actions Runner

The runner is a **Starret backing container**:

- Lives on `starret-net`; not exposed to `joshua-net`
- Polls GitHub outbound; requires no inbound webhook or open port
- Has volumes: repo checkout path, SSH keys for `deploy.py`
- Executes: `git_pull.py`, `deploy.py`, `validate.py`
- **Bare-metal runner installs are forbidden.** Containerizing the runner limits its blast radius and aligns with the "no host-level processes" invariant.

### 3.3 Cross-pMAD Call Patterns

```
Henson UI
  → kaiser:9226/mcp       (kaiser_chat emad_name=hopper)

Kaiser-LangGraph (Hopper eMAD executing) → kaiser-net → kaiser gateway → joshua-net
  → starret:8010/mcp      (starret_chat, starret_github)
  → rogers:6380/mcp       (context read/write)
  → sutherland:11435/mcp  (quorum model inference)

GitHub Actions runner → internet
  → api.github.com        (status polling, outbound only)
```

---

## 4. Cursor as Transitional MCP Client

While Henson is being built, Cursor can issue MCP calls to Hopper directly via `curl` or the Cursor MCP client config. This requires no special integration — Hopper's gateway listens on `joshua-net` and accepts standard MCP JSON-RPC calls.

Example (Cursor MCP config pointing at Hopper):
```json
{
  "mcpServers": {
    "hopper": {
      "url": "http://irina:9225/mcp"
    }
  }
}
```

This is a bridge, not a design target. Hopper does not build its interface for Cursor. It builds its interface for Henson's SSE-capable UI.

---

## 5. Build Sequence

The Software Factory is built in dependency order. Each component is required by the one that follows it.

### Step 1: Alexandria

**Why first:** Every subsequent container build uses `pip install` and `npm install`. Without Alexandria, every build hits the internet and is subject to PyPI/NPM outages, rate limits, and slow LAN-over-internet routing. Standing up Alexandria first makes all subsequent development fast and offline-capable.

**Status: DEPLOYED 2026-03-09.** All 5 containers healthy on irina.

**Deliverables (completed):**
- `alexandria-devpi` on irina, `http://irina:3141/root/pypi/+simple/`
- `alexandria-verdaccio` on irina, `http://irina:4873`
- `alexandria-registry` on irina, `irina:5000`
- Base images configured: `PIP_INDEX_URL`, `NPM_CONFIG_REGISTRY` set; Docker daemon insecure-registries updated

**REQ:** `mads/alexandria/docs/REQ-alexandria.md` (supersedes proposals REQ-018, REQ-019, REQ-022)

### Step 2: Starret (CI/CD Upgrade)

**Why second:** Hopper depends on Starret for every release action — commit, push, PR creation, merge, and CI/CD trigger. Starret exposes `starret_github` (structured GitHub API calls — get issues, PR status, post comments) that Hopper needs to understand the context of issues before acting on them.

**Status: DEPLOYED 2026-03-09.** Containers healthy on irina. Gate 3 pending.

**Deliverables (completed):**
- `starret` nginx gateway on irina (joshua-net + starret-net, port 8010)
- `starret-langgraph` Imperator: `starret_chat` (git operations), `starret_github` (GitHub API)
- `github-runner` backing container (starret-net, outbound only)
- Push to main fires runner via `on: push`; `workflow_dispatch` for rollback/ad-hoc only
- `deploy.py`, `validate.py` exposed via runner volumes
- Packages: migrated to Alexandria devpi (2026-03-09) — no `packages/` directory

**REQs:** [mads/starret/docs/REQ-starret.md](mads/starret/docs/REQ-starret.md)

### Step 3: Hopper

**Why third:** Hopper depends on Starret (for releases) and Sutherland (for quorum inference). Once Starret is up, Hopper can be built and Cursor can immediately use it via MCP — no Henson required.

**Deliverables:**
- `hopper_chat` MCP tool with SSE streaming
- Unified Quorum Engine (Lead + Reviewer Alpha + Reviewer Beta + Executor)
- `develop_software` flow: requirements → HLD → code → deploy → test
- `software_engineer` flow: issue → fix → deploy → verify

**REQs:** REQ-hopper.md, HLD-hopper-quorum-engine.md

### Step 4: Henson UI for Hopper

**Why fourth:** The design target from the start. Once Hopper is running and accessible via MCP, Henson provides the full human interface: chat UI, SSE-rendered Quorum visibility, approval gates, and project history. This is not an "upgrade" from Cursor — it is the designed interface that Hopper was always built to serve.

**Deliverables:**
- Henson UI connected to `hopper_chat` MCP tool
- SSE stream rendered in real time (Quorum round-by-round visibility)
- Approval gate UI (human approves requirements, HLD, final deploy)
- Project history via Rogers context

---

## 6. Domain Ownership Summary

| Domain | Owner | Not Owner |
|--------|-------|-----------|
| Engineering intelligence, quorum, SDLC | Hopper | — |
| Git, PR, merge, CI/CD trigger | Starret | Hopper |
| GitHub Actions runner | Starret (backing container) | bare metal |
| PyPI package caching | Alexandria (alexandria-devpi) | Sutherland, Hopper |
| NPM package caching | Alexandria (alexandria-verdaccio) | Sutherland, Hopper |
| Docker image registry | Alexandria (alexandria-registry) | — |
| HuggingFace / ML model caching | **Sutherland** | Alexandria |
| Conversation/project memory | Rogers | Hopper, Starret |
| AI compute (all inference) | Sutherland | Hopper, Rogers |
| Human UI (chat, approvals) | Henson | Cursor |
| Transitional MCP client | Cursor | — |

---

## 7. Archiving Obsolete REQs

When a REQ becomes irrelevant — due to scope changes, supersession by a new design, or pMAD consolidation — it is archived to `Z:\archive`. It is not deleted; it retains its history. The archive is the single location for all retired design artefacts.

Examples of REQs that should be archived:
- Any REQ that assigned HuggingFace caching to Alexandria (superseded: HF moved to Sutherland)
- Any REQ that described the GitHub cacher component of Alexandria (eliminated)

---

## 8. Related Documents

- `HLD-conversational-core.md` — Rogers, Sutherland, Henson (conversational infrastructure)
- `HLD-state3-mad.md` — AE/TE separation, bootstrap kernel, dynamic StateGraph loading (Kaiser is State 3)
- `HLD-joshua26-agent-architecture.md` — Agent classes, TE anatomy, development workflow
- `HLD-cicd-architecture.md` — Detailed CI/CD pipeline mechanics (Starret)
- `HLD-unified-package-caching.md` — Alexandria package caching details
- `HLD-hopper-quorum-engine.md` — Unified Quorum Engine design
- `mads/hopper/docs/REQ-hopper.md` — Hopper requirements
- `mads/starret/docs/REQ-starret.md` — Starret (Imperator, starret_chat + starret_github)
- `mads/alexandria/docs/REQ-alexandria.md` — Alexandria (deployed; supersedes REQ-018, REQ-019, REQ-022)
