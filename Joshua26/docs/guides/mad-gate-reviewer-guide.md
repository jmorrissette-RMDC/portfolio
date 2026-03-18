# MAD Gate Reviewer Guide

The gate reviewer session is the quality gate between every phase of the MAD build lifecycle. Unlike the lean sessions (design, implementation, deployment) which run with small focused contexts, the gate reviewer earns a large context budget — it reads the full ecosystem documentation, ingests the codebase, and investigates actively. It is not a checklist-ticker. It catches what focused sessions cannot see.

The gate reviewer runs three times per MAD build:

1.  **Post-design (Gate 1)** — review the delta REQ before implementation begins
2.  **Post-implementation (Gate 2)** — review the code before deployment begins
3.  **Post-deployment (Gate 3)** — full compliance audit against the running system

**How it works:** The gate reviewer is an external reviewer — Gemini, Claude, or Codex — invoked via CLI (see `docs/guides/using-gemini-cli-locally.md`, `docs/guides/using-claude-cli-locally.md`, and `docs/guides/using-codex-cli-locally.md`). **Invoke from the Joshua26 project root** (CWD = directory containing `mads/`, `docs/`, `registry.yml`) so output paths resolve correctly. The reviewer writes the review or audit directly to the dated file in `mads/[mad-name]/docs/Review/`. The invoking session presents the findings to the user for discussion and records decisions in the plan file. **No changes are made until the user has reviewed and decided which findings to address.**

**Multi-model review:** Consider getting reviews from more than one model (e.g., Gemini and Claude, or Claude and Codex). Different models catch different issues; aggregating findings improves coverage.

**Review folder:** All gate outputs go to `mads/[mad-name]/docs/Review/`. Create this folder if it does not exist. Use dated filenames; each run creates a *new* file. **Include the reviewer name** (claude, gemini, codex) in the filename so results are identifiable when multiple models run.

| Gate | Filename |
|------|----------|
| Gate 1 | `gate-1-review-[YYYY-MM-DD]-[reviewer].md` |
| Gate 2 | `gate-2-review-[YYYY-MM-DD]-[reviewer].md` |
| Gate 3 | `REQ-000-compliance-audit-[YYYY-MM-DD]-[reviewer].md` (filled checklist) |

**[reviewer]** = `claude` | `gemini` | `codex` (lowercase). For same-day re-runs, append `-run2` before the reviewer: `gate-2-review-2026-02-28-run2-claude.md`.

**Permission bypass by CLI:** Without it, the reviewer may not be able to write the file.

| CLI | Flag |
|-----|------|
| Claude | `--dangerously-skip-permissions` |
| Gemini | `--approval-mode yolo` |
| Codex | `--yolo` (with `codex exec`) |

**Invocation prompts:** The invoking session uses one of these prompts (substitute `[mad-name]`, `[YYYY-MM-DD]`, and `[reviewer]`). The reviewer writes the output file directly. **Use the CLI's permission bypass** so file writes are auto-approved: `--dangerously-skip-permissions` (Claude), `--approval-mode yolo` (Gemini), `--yolo` (Codex). Without it, the reviewer may not be able to create the file.

- **Gate 1:** Run Gate 1 (post-design) review for [mad-name]. Read and follow `docs/guides/mad-gate-reviewer-guide.md` in full. Write your review to `mads/[mad-name]/docs/Review/gate-1-review-[YYYY-MM-DD]-[reviewer].md`. Use the write tool to save the file.
- **Gate 2:** Run Gate 2 (post-implementation) review for [mad-name]. Read and follow `docs/guides/mad-gate-reviewer-guide.md` in full. Write your review to `mads/[mad-name]/docs/Review/gate-2-review-[YYYY-MM-DD]-[reviewer].md`. Use the write tool to save the file.
- **Gate 3:** Run Gate 3 (post-deployment) audit for [mad-name]. Read and follow `docs/guides/mad-gate-reviewer-guide.md` in full. Use `docs/audits/REQ-000-compliance-checklist.md` as the audit instrument. Write your filled checklist to `mads/[mad-name]/docs/Review/REQ-000-compliance-audit-[YYYY-MM-DD]-[reviewer].md`. Use the write tool to save the file.

***

## Reading List

Load all of the following before beginning any review. This is the gate reviewer's full context.

| Document                                                                  | Why                                                                             |
|---------------------------------------------------------------------------|---------------------------------------------------------------------------------|
| `docs/designs/HLD-Joshua26-system-overview.md`                            | Ecosystem orientation — what exists, where it runs                              |
| `docs/designs/HLD-MAD-container-composition.md`                           | pMAD container architecture: States 1–3, AE/TE package pattern, networking    |
| `docs/requirements/REQ-000-Joshua26-System-Requirements-Specification.md` | Authoritative specification — the primary reference for all gates               |
| `registry.yml`                                                            | UIDs, ports, host assignments — verify every container                          |
| `docs/guides/docker-compose-file-strategy.md`                             | Compose patterns — verify service definitions                                   |
| `docs/guides/mad-build-checklist.md`                                      | What the implementation session was told to do — verify it was followed         |
| `docs/audits/REQ-000-compliance-checklist.md`                             | The audit instrument — used at gate 3 to verify the live system against REQ-000 |
| `docs/guides/mad-testing-guide.md`                                    | How to design and execute comprehensive tests during deployment         |
| `docs/guides/mad-design-guide.md`                                         | Verify the design session followed its process                                  |
| `docs/guides/mad-implementation-guide.md`                                 | Verify the implementation session followed its process                          |
| `docs/guides/mad-deployment-guide.md`                                     | Verify the deployment session followed its process                              |
| `mads/[mad-name]/docs/REQ-[mad-name].md`                                  | The delta REQ — what this MAD is supposed to do                                 |
| `mads/[mad-name]/docs/[mad-name]-plan.md`                                  | The plan file — read current state before reviewing (path is designated by the user) |

Also read: this guide.

**Do not load INF-001** — host IPs and SSH details are inlined below. The VNC, lsyncd, and NFS content is not relevant to gate review.

***

## Gate 1: Post-Design Review

**Input:** Delta REQ document (`mads/[mad-name]/docs/REQ-[mad-name].md`)

**Approach:** Investigative and advisory. Find what the design session couldn't see — conflicts with existing pMADs, contradictions with REQ-000, missing deviations, bad assumptions. Go looking for problems. In addition, provide recommendations: code quality considerations, industry standards, alternative approaches, general advice. A design that passes REQ-000 may still benefit from suggestions. Read actual files; if something looks borrowed from another MAD, check that MAD. A design error caught here costs nothing to fix; the same error after implementation means rework.

**Output:** Write the review to `mads/[mad-name]/docs/Review/gate-1-review-[YYYY-MM-DD]-[reviewer].md`. Structure: blockers (must fix before implementation), observations (worth noting but not blocking), recommendations (code quality, industry standards, alternatives, advisory notes). The invoking session presents the findings to the user. Changes are only made after the user decides which items to address.

***

## Gate 2: Post-Implementation Review

**Input:** Committed code in `mads/[mad-name]/`

**Approach:** Investigative and advisory. Read the source files — Dockerfiles, server.py, config.json, requirements.txt, docker-compose additions — and reason about them against the delta REQ and `REQ-000` (including the Code and Implementation Standards in Part 4). Find implementation errors: things that compile and commit cleanly but will fail at build or runtime, contradict the design, or violate a requirement. In addition, provide recommendations: code quality, industry standards, alternative approaches, maintainability advice. Compare against other pMADs in the codebase. If the sutherland or rogers Dockerfile solved a problem a certain way and this one did it differently, understand why — and suggest improvements where applicable. No containers run yet.

**Output:** Write the review to `mads/[mad-name]/docs/Review/gate-2-review-[YYYY-MM-DD]-[reviewer].md`. Structure: blockers, observations, recommendations. The invoking session presents the findings to the user. Changes are only made after the user decides which items to address.

***

## Gate 3: Post-Deployment Audit

**Input:** Running containers on the target host

**Approach:** Full compliance audit. In addition to following the instructions in `docs/audits/REQ-000-compliance-checklist.md` for overall compliance, leverage `docs/guides/mad-testing-guide.md` to design and execute comprehensive interface and state verification tests against the live system. Every item must be verified — not inferred from code. SSH to the host and inspect directly. The compliance checklist is an audit instrument for live systems; it cannot be meaningfully applied before containers are running.

**Verification commands:**

```bash
# Container status and networks
ssh aristotle9@[ip] "docker ps --filter 'name=[mad]' --format 'table {{.Names}}\t{{.Status}}\t{{.Networks}}'"

# UID/GID inside container
ssh aristotle9@[ip] "docker exec [mad] id"

# Health endpoint
ssh aristotle9@[ip] "curl -s http://localhost:[port]/health | python3 -m json.tool"

# Structured log check
ssh aristotle9@[ip] "docker logs [mad] --tail 20"

# Volume mounts
ssh aristotle9@[ip] "docker inspect [mad] --format '{{json .Mounts}}' | python3 -m json.tool"
```

**Output:** Fill the compliance checklist and write it to `mads/[mad-name]/docs/Review/REQ-000-compliance-audit-[YYYY-MM-DD]-[reviewer].md`. If there are failures, the session fixes them and re-runs — create a *new* dated file; do not update the previous one. Gate 3 sign-off (after blockers are addressed) unlocks the session wrap-up (archiving the plan).

***

## Communication

Write the review or audit to the designated file. **Start the file with a Reviewer line** so attribution is clear even if the filename is lost:

```
**Reviewer:** [Claude|Gemini|Codex]
**Gate:** [1|2|3]
**MAD:** [mad-name]
**Date:** [YYYY-MM-DD]
```

The invoking session presents the findings to the user. Use this format:

-   **Gate N: PASSED** or **FAILED** — brief summary.
-   **Blockers:** [specific items — must fix before proceeding]. (G1, G2, G3)
-   **Observations:** [non-blocking notes for the session to consider]. (G1, G2, G3)
-   **Recommendations:** [code quality, industry standards, alternatives, advice]. (G1 and G2 only — consultative; user may adopt or defer)

Be specific. "Dockerfile doesn't follow REQ-000" is not useful. "sutherland-langgraph/Dockerfile uses `python:3.12-slim:latest` instead of a digest-pinned image (REQ-000 §1.4)" is.

**Important:** The invoking session must discuss findings with the user before making any changes. The user decides which findings to address and how. Decisions and resulting changes are recorded in the plan file.

***

## Host Reference

| Host  | IP            | Role                           |
|-------|---------------|--------------------------------|
| Irina | x.x.x.110 | Storage leader (ZFS, 44TB)     |
| M5    | x.x.x.120 | Compute manager (5x GPU, NVMe) |
| Hymie | x.x.x.130 | Desktop automation             |

**SSH:** `ssh aristotle9@[ip]` — key-based auth, no password, no sudo needed for docker. **Project path:** `/mnt/storage/projects/Joshua26`

See `docs/guides/remote-docker-access-via-ssh.md` for known SSH gotchas (known_hosts conflicts, docker group issues).

***

## Critical Rules

1.  **Never write "business logic"** — always "programmatic logic"
2.  **LangGraph IS the architecture** — Flask is HTTP transport only
3.  **Langflow is a running MAD** — not "under evaluation"
4.  **Templates are the baseline** — delta REQs only describe what differs
5.  **REQ-000 is authoritative** — all other docs defer to it
6.  `REQ-000-compliance-checklist.md` **is the audit instrument** — it verifies live systems at gate 3. The build checklist is for the implementation session, not the gate reviewer.

***

**Related:** [Build Checklist](./mad-build-checklist.md) · [Design Guide](./mad-design-guide.md) · [Implementation Guide](./mad-implementation-guide.md) · [Deployment Guide](./mad-deployment-guide.md)
