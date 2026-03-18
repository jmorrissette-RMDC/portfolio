# ADR-048: Git Safety Net Strategy

Status: Accepted
Date: 2026-01-10

## Context

Agents and tools need git access. Uncommitted work can be lost. Direct git access lacks audit trail and governance potential.

## Decision

Starret provides both automated backup and centralized git operations:

1. Gitwatch auto-commits to a dedicated `gitwatch-backup` branch (local only, no push)
2. MCP tools expose git operations (`git_commit`, `git_status`, `git_push`)
3. When a real commit occurs, the backup branch resets to HEAD
4. All git operations logged via MCP request logging (ADR-047)

Backup branch contains only uncommitted work, not historical auto-saves.

## Consequences

- Uncommitted work protected by automated backup
- Agents use MCP for git (audit trail, future governance)
- Clean separation: backup branch vs working branches
- Foundation for Phase 2 policy enforcement
