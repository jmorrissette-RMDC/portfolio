# pMAD Deployment Guide

**Purpose:** Guide for a deployment session. Builds, deploys, and verifies a pMAD on target infrastructure.

**Input:** Working pMAD containers from implementation phase (in `mads/[mad-name]/`)

**Output:** Running, verified pMAD on target host

***

## Plan File

The MAD's plan file was created during the design phase at `mads/[mad-name]/docs/[mad-name]-plan.md` (or as designated). Open it and work from it.

**At session start:** Open the existing plan file. Add a `## Deployment Phase` section and fill in the deployment plan template (end of this guide).

**During the session:** Update the plan file as you work:

-   Mark completed steps with timestamps
-   Log each deploy/test/fix iteration and its outcome
-   Record any issues encountered and how they were resolved
-   Note deviations from the original plan and why
-   Track container health status after each deployment attempt

**The plan file is a retrospective log** spanning all phases. Keep appending — don't overwrite the design and implementation content.

**This is the final phase.** At the end, the plan file gets archived to the MAD docs folder.

***

## What You Need to Know

### Required Reading (in this order)

1.  `docs/designs/HLD-Joshua26-system-overview.md` — and all documents linked within it
2.  `docs/requirements/REQ-000-Joshua26-System-Requirements-Specification.md` — authoritative specification
3.  `mads/[mad-name]/docs/REQ-[mad-name].md` — delta REQ (what you're deploying)
4.  `docs/guides/deployment-guide.md` — deployment scripts reference (deploy.py, validate.py, status.py, etc.)
5.  `docs/guides/remote-docker-access-via-ssh.md` — SSH access and troubleshooting
6.  `docs/guides/mad-build-checklist.md` — compliance checklist
7.  `docs/guides/mad-testing-guide.md` — comprehensive testing procedures
8.  `registry.yml` — UIDs, ports, host assignments

### Host Information

| Host  | IP            | Role                     | Override File              |
|-------|---------------|--------------------------|----------------------------|
| Irina | x.x.x.110 | Storage Leader           | `docker-compose.irina.yml` |
| M5    | x.x.x.120 | Compute Manager (4x GPU) | `docker-compose.m5.yml`    |
| Hymie | x.x.x.130 | Desktop Manager          | `docker-compose.hymie.yml` |

**SSH:** `ssh aristotle9@[ip]` — key-based authentication, no password, no sudo for docker.

**Project path on hosts:** `/storage/projects/Joshua26`

### Key Facts

-   **No local test environment.** Testing happens on infrastructure after deployment.
-   **Iterative deploy-test-fix loop** is the normal workflow, not a failure.
-   **Deployment scripts** handle host targeting, override files, and validation. Use them — don't run docker compose manually on hosts.
-   **Rollback** is emergency fallback only. Normal workflow is fix-and-redeploy.
-   **Offline builds** on hosts — packages from `/storage/wheels/` and `/storage/npm-cache/`.

***

## What You Need to Do

### Step 1: Pre-Deployment Checks

Before deploying, verify the implementation is ready:

```bash
# From Windows — verify registry.yml has entries for all containers
# Verify docker-compose.yml has service definitions
# Verify host override files suppress the service on non-native hosts
# Run through mad-build-checklist.md
```

Confirm:

-   [ ] `registry.yml` has entries for `[mad-name]`, `[mad-name]-langgraph`, and any backing services
-   [ ] `docker-compose.yml` has service definitions with correct build context (`.`), networks, and labels
-   [ ] Non-native host override files suppress the service with `profiles: ["[host]-only"]`
-   [ ] Network defined: `[mad-name]-net` as bridge network in docker-compose.yml

### Step 2: Commit and Push

```bash
# Stage and commit all MAD files
git add mads/[mad-name]/ docker-compose.yml docker-compose.*.yml registry.yml
git commit -m "Add [mad-name] MAD containers

Co-Authored-By: [agent/model used]"
git push
```

### Step 3: Pull on Target Host

```bash
# Pull on the target host
py -3.12 scripts/deployment/git_pull.py [host-name]

# Or pull on all hosts
py -3.12 scripts/deployment/git_pull.py --all
```

### Step 4: Backup (if replacing existing containers)

```bash
# Backup before deploying (skip for brand new MADs)
py -3.12 scripts/deployment/backup.py [mad-name]
```

### Step 5: Deploy

```bash
# Dry run first
py -3.12 scripts/deployment/deploy.py [mad-name] --dry-run

# Deploy gateway (it will pull langgraph and backing services via depends_on)
py -3.12 scripts/deployment/deploy.py [mad-name]
```

### Step 6: Verify

Refer to `docs/guides/mad-testing-guide.md` for comprehensive instructions on how to verify your deployment, including health checks, log inspection, and basic service status checks. Specifically:

-   [ ] Check containers are running: `py -3.12 scripts/deployment/status.py --service [mad-name]`
-   [ ] Validate correct host placement: `py -3.12 scripts/deployment/validate.py`
-   [ ] Check health endpoints: `ssh aristotle9@[host-ip] "curl -s http://[mad-name]:[port]/health | python3 -m json.tool"`
-   [ ] Check logs: `py -3.12 scripts/deployment/logs.py [mad-name]`
-   [ ] Verify network isolation: `ssh aristotle9@[host-ip] docker network inspect [mad-name]-net`

### Step 7: Test MCP Tools

For comprehensive testing of all MCP tools, including both **Interface & Contract Tests** and **Integration & State Verification Tests**, refer to the detailed procedures outlined in `docs/guides/mad-testing-guide.md`. This guide provides specific instructions on how to design test cases, execute them via SAM or direct MCP calls, and verify the internal system state changes.

### Step 8: Fix Loop (as needed)

If anything fails:

1.  Diagnose from logs and health endpoints
2.  Fix code on Windows
3.  Commit and push
4.  Pull on host: `py -3.12 scripts/deployment/git_pull.py [host-name]`
5.  Redeploy: `py -3.12 scripts/deployment/deploy.py [mad-name]`
6.  Re-verify

This loop is normal and expected.

### Step 9: Gate Reviewer (Gate 3)

Hand off to the gate reviewer for Gate 3 post-deployment audit.

1.  **Notify the user that you are ready for Gate 3** — Upon user approval move to step 2.
2.  **Gate reviewer runs Gate 3** — Invoke external reviewer (Gemini, Claude, or Codex) via CLI. Use this prompt (substitute `[mad-name]` and `[YYYY-MM-DD]`):

    > Run Gate 3 (post-deployment) audit for [mad-name]. Read and follow `docs/guides/mad-gate-reviewer-guide.md` in full. Use `docs/audits/REQ-000-compliance-checklist.md` as the audit instrument. Write your filled checklist and findings to `mads/[mad-name]/docs/Review/REQ-000-compliance-audit-[YYYY-MM-DD]-[reviewer].md`. Use the write tool to save the file.

    Substitute `[reviewer]` with `claude`, `gemini`, or `codex`. If re-running after fixes, append `-run2` before the reviewer. Never update a previous file. Consider running multiple models for broader coverage.
3.  **Discuss findings** — the gate reviewer's findings are discussed with the user before any changes are made. The user decides which items to address.
4.  **Address blockers** — fix any blockers via the deploy-test-fix loop. Record changes and rationale in the plan file.

### Step 10: Post-Deployment Cleanup

-   [ ] Permissions correct on workspace paths: `ssh aristotle9@[host-ip] ls -la /workspace/[mad-name]/`
-   [ ] README.md updated with deployment status
-   [ ] System docs updated if needed

***

## Plan File Template (append to existing plan)

Add this section to the existing MAD plan file:

```markdown
---

## Deployment Phase

### Target
Deploy [mad-name] to [host-name] ([host-ip])

### Required Reading
- [ ] deployment-guide.md (scripts reference)
- [ ] remote-docker-access-via-ssh.md
- [ ] mad-build-checklist.md

### Deployment Steps
1. Pre-deployment checks (registry, compose, networks)
2. Commit and push
3. Pull on [host-name]
4. Backup (if replacing existing)
5. Deploy via deploy.py
6. Verify (health, logs, network isolation)
7. Test MCP tools
8. Fix loop (as needed)
9. Post-deployment cleanup + archive plan file

### Rollback Plan
- Restore from backup: `py -3.12 scripts/deployment/restore.py [mad-name] [backup-file]`
- Or: `ssh aristotle9@[host-ip] docker compose -f docker-compose.yml -f docker-compose.[host].yml down [mad-name]`

### Deployment Progress Log
<!-- Update as you work — log each deploy/test/fix iteration -->
```

***

## Session Wrap-Up

This is the final phase. If the plan file was not already in `mads/[mad-name]/docs/`, move or copy it there:

```bash
# Ensure plan file is in MAD docs (if it was elsewhere)
mv [plan-file-path] mads/[mad-name]/docs/[mad-name]-plan.md
# or: cp [plan-file-path] mads/[mad-name]/docs/[mad-name]-plan.md
```

At this point `mads/[mad-name]/docs/` should contain the full build history:

-   `REQ-[mad-name].md` — delta REQ (from design phase)
-   `[mad-name]-plan.md` — complete plan file spanning all three phases (design → implementation → deployment), including all gate review findings and decisions

***

## SSH Troubleshooting

| Problem                  | Solution                                                           |
|--------------------------|--------------------------------------------------------------------|
| SSH asks for password    | Verify `~/.ssh/id_ed25519` exists; check `authorized_keys` on host |
| Docker permission denied | Verify user in docker group: `ssh aristotle9@[ip] groups`          |
| Known hosts conflict     | `ssh-keygen -R [ip]` then reconnect                                |
| Connection refused       | `ping [ip]`; check SSH is running: `ssh aristotle9@[ip]`           |

See `docs/guides/remote-docker-access-via-ssh.md` for full troubleshooting.

***

**Related:** [Deployment Scripts Guide](./deployment-guide.md) · [Build Checklist](./mad-build-checklist.md) · [Gate Reviewer Guide](./mad-gate-reviewer-guide.md) · [SSH Guide](./remote-docker-access-via-ssh.md)
