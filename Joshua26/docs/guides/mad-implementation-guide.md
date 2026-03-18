# pMAD Implementation Guide

**Purpose:** Guide for an implementation session. Copies templates, implements the delta from an approved REQ document.

**Input:** Approved `mads/[mad-name]/docs/REQ-[mad-name].md` (delta REQ)

**Output:** Working pMAD containers ready for deployment

***

## Plan File

The MAD's plan file was created during the design phase at `mads/[mad-name]/docs/[mad-name]-plan.md` (or as designated). Open it and work from it.

**At session start:** Open the existing plan file. Add an `## Implementation Phase` section and fill in the implementation plan template (end of this guide).

**During the session:** Update the plan file as you work:

-   Mark completed chunks with timestamps
-   Log key decisions and their rationale
-   Record any issues encountered and how they were resolved
-   Note deviations from the original plan and why
-   Track which files were created/modified

**The plan file is a retrospective log** spanning all phases. Keep appending — don't overwrite the design phase content.

**Hand-off:** At the end of this phase, tell the gate reviewer the plan file is ready for the deployment session.

***

## What You Need to Know

### Required Reading (in this order)

1.  `docs/designs/HLD-Joshua26-system-overview.md` — and all documents linked within it
2.  `docs/requirements/REQ-000-Joshua26-System-Requirements-Specification.md` — authoritative specification
3.  `mads/[mad-name]/docs/REQ-[mad-name].md` — YOUR delta REQ (the design you are implementing)
4.  `mads/_template/README.md` — template overview and 7-step copy-paste workflow
5.  `mads/_template/docs/REQ-langgraph-template.md` — full LangGraph pattern (baseline)
6.  `registry.yml` — UIDs, ports, host assignments
7.  `docs/guides/mad-build-checklist.md` — compliance checklist (verify before deployment)

### Key Facts

-   **Templates are the starting point.** Copy templates, then implement only the delta.
-   **server.py is the LangGraph entry point** (not graph.py). The template `server.py` is simplified; REQ-langgraph-template.md shows the full pattern.
-   **config.json drives the gateway.** All tool routing logic lives in config.json. server.js should be \< 20 lines.
-   **Networking:** Gateway on both `joshua-net` + `[mad]-net`. LangGraph and backing services on `[mad]-net` only.
-   **Offline builds:** Python packages from Alexandria devpi (`PIP_INDEX_URL=http://irina:3141/root/pypi/+simple/`), Node.js from Alexandria verdaccio (`NPM_CONFIG_REGISTRY=http://irina:4873`). No internet access during build.
-   **No local test environment.** Testing happens on infrastructure after deployment.

***

## What You Need to Do

### Step 1: Copy Templates

```bash
# Copy container directories (adjust for which backing services you need)
cp -r mads/_template/template mads/[mad-name]/[mad-name]
cp -r mads/_template/template-langgraph mads/[mad-name]/[mad-name]-langgraph
cp -r mads/_template/template-postgres mads/[mad-name]/[mad-name]-postgres    # If needed
cp -r mads/_template/template-service mads/[mad-name]/[mad-name]-service      # If needed
```

See `mads/_template/README.md` for the full 7-step workflow. Do NOT duplicate those steps here.

### Step 2: Plan Implementation Chunks

Each MAD is different. Break work into chunks based on complexity:

-   **Simple (1-2 chunks):** Copy template → customize config.json → implement all tools
-   **Medium (3-5 chunks):** Set up structure → database schema + first tool → remaining tools → error handling
-   **Complex (6+ chunks):** Structure → schema → AE flows → TE flows → optimization → edge cases

### Step 3: Implement Each Chunk

For each chunk: implement, verify, then proceed to the next chunk.

**Gateway container (**`[mad]`**):**

-   Edit `config.json`: define tools, schemas, routing targets
-   Tool routing target pattern: `http://[mad-name]-langgraph:8000`
-   server.js should not need changes (template handles it)

**LangGraph container (**`[mad]-langgraph`**):**

-   Edit `server.py`: implement flow logic per delta REQ
-   AE flows: deterministic execution (database queries, calculations, API calls)
-   TE flows: cognitive reasoning (LLM planning, analysis, synthesis)
-   Both flow types use StateGraph with nodes, edges, and state definitions

**Backing services (**`[mad]-postgres`**, etc.):**

-   Edit `init.sql` for database schema
-   Use official images — don't customize backing service Dockerfiles

### Step 4: Add to docker-compose.yml

Add service definitions to the master `docker-compose.yml` at project root:

```yaml
# Gateway — bridges both networks
[mad-name]:
  build:
    context: .
    dockerfile: mads/[mad-name]/[mad-name]/Dockerfile
  container_name: [mad-name]
  networks:
    - joshua-net
    - [mad-name]-net
  # ... ports, volumes, labels

# LangGraph — private network only
[mad-name]-langgraph:
  build:
    context: .
    dockerfile: mads/[mad-name]/[mad-name]-langgraph/Dockerfile
  container_name: [mad-name]-langgraph
  networks:
    - [mad-name]-net
  # ... volumes, environment, healthcheck

# Backing service — private network only
[mad-name]-postgres:
  image: postgres:16-alpine
  container_name: [mad-name]-postgres
  networks:
    - [mad-name]-net
  # ... volumes, environment, healthcheck

networks:
  [mad-name]-net:
    driver: bridge
```

**Build context is always** `.` **(project root).** COPY paths in Dockerfiles are relative to project root: `COPY mads/[mad-name]/...`

### Step 5: Pre-Deployment Verification

Run through `docs/guides/mad-build-checklist.md` before handing off to deployment. In addition, perform the following code quality checks as required by `REQ-000 Part 4`:

-   [ ] **Code Formatting:** Code passes `black --check .` (for Python).
-   [ ] **Code Linting:** Code passes `ruff check .` with no errors (for Python).
-   [ ] **Configuration:** `config.json` matches the delta REQ tool definitions.
-   [ ] **Syntax:** Python syntax is valid (`python -m py_compile server.py`), and all `.json` files have valid syntax.
-   [ ] **Security:** No hardcoded secrets or IP addresses.
-   [ ] **Build Configuration:** Dockerfile and `docker-compose.yml` entries are correct per `mad-build-checklist.md`.
-   [ ] **Error Handling:** All tool endpoints handle errors gracefully.

### Step 6: Gate Reviewer (Gate 2)

Hand off to the gate reviewer for Gate 2 post-implementation review.

1.  **Notify the user that you are ready for Gate 2** — Upon user approval move to step 2.
2.  **Gate reviewer runs Gate 2** — Invoke external reviewer (Gemini, Claude, or Codex) via CLI. Use this prompt (substitute `[mad-name]` and `[YYYY-MM-DD]`):

    > Run Gate 2 (post-implementation) review for [mad-name]. Read and follow `docs/guides/mad-gate-reviewer-guide.md` in full — it contains the Reading List, approach, and output format. Write your review to `mads/[mad-name]/docs/Review/gate-2-review-[YYYY-MM-DD]-[reviewer].md`. Use the write tool to save the file. Substitute [reviewer] with claude, gemini, or codex.

    Consider running multiple models for broader coverage.
3.  **Discuss findings** — the gate reviewer's findings (blockers and observations) are discussed with the user before any changes are made. The user decides which items to address.
4.  **Address blockers** — fix any blockers before proceeding to deployment. Record changes and rationale in the plan file.

### Step 7: Documentation Alignment

-   [ ] `mads/[mad-name]/README.md` updated with tool descriptions
-   [ ] `registry.yml` has entries for all containers
-   [ ] System docs updated if new patterns emerged

***

## Plan File Template (append to existing plan)

Add this section to the existing MAD plan file:

```markdown
---

## Implementation Phase

### Required Reading
- [ ] REQ-[mad-name].md (delta REQ — the design)
- [ ] Template README + REQ-langgraph-template.md
- [ ] mad-build-checklist.md

### Implementation Chunks
1. Copy templates, set up directory structure
2. [Chunk based on REQ complexity]
3. ...
4. Pre-deployment verification + gate reviewer (Gate 2)

### Implementation Output
- Working containers in mads/[mad-name]/
- docker-compose.yml entries
- Updated registry.yml and README

### Implementation Progress Log
<!-- Update as you work -->
```

***

## Session Wrap-Up

**Do NOT move the plan file yet** — it continues into deployment. Tell the gate reviewer the implementation phase is complete.

***

## Next Step

Once implementation is approved → **deployment phase**: `docs/guides/mad-deployment-guide.md`

***

**Related:** [Build Checklist](./mad-build-checklist.md) · [Design Guide](./mad-design-guide.md) · [Gate Reviewer Guide](./mad-gate-reviewer-guide.md) · [Template README](../../mads/_template/README.md)
