# Starret - Git Safety Net

Git auto-backup (gitwatch) + MCP git tools in a single container. Implements ADR-048.

## Architecture

Single container providing:
- **File watcher**: Monitors repos, auto-commits to `gitwatch-backup` branch
- **MCP server**: Exposes git tools via HTTP/SSE (port 8010)

## How It Works

1. File watcher monitors `/storage/projects` for git repositories
2. File changes trigger auto-commit to `gitwatch-backup` branch (after settle time)
3. When you do a real commit via `git_commit`, the backup branch resets to HEAD
4. Backup branch only contains uncommitted work, not historical auto-saves

## MCP Tools

| Tool | Description |
|------|-------------|
| `starret_health_check` | Health check (auto-provided by mad-core) |
| `git_status` | Get repo status (branch, staged, unstaged, untracked) |
| `git_commit` | Commit changes, resets backup branch |
| `git_push` | Push to remote |
| `git_log` | Get commit history |
| `git_diff` | Show changes |
| `git_watch_status` | Show watched repos and backup branch status |

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `PROJECTS_PATH` | `/storage/projects` | Directory to watch for repos |
| `BACKUP_BRANCH` | `gitwatch-backup` | Branch for auto-commits |
| `SETTLE_TIME` | `300` | Seconds to wait after changes before commit |
| `MCP_PORT` | `8010` | MCP server port |

## Volumes

| Mount | Path | Purpose |
|-------|------|---------|
| storage | /storage | Shared storage (projects, files) |
| workspace | /workspace | Container-local persistent data |

## Ports

- 8010: MCP server (HTTP/SSE)

## Usage

```bash
# Start
docker compose up -d

# Check status via MCP (through Sam)
git_watch_status

# Commit via MCP
git_commit repo="Joshua26" message="Add new feature"

# Push via MCP
git_push repo="Joshua26"
```

## Recovery

If you lose uncommitted work, check the backup branch:
```bash
cd /mnt/storage/projects/YourRepo
git log gitwatch-backup
git diff HEAD..gitwatch-backup
git cherry-pick <commit-hash>  # or merge
```

## ADR Compliance

- ADR-037: Local package caching (packages/apt/, packages/npm/)
- ADR-039: Two-volume mounting (storage + workspace)
- ADR-042: Uses mad-core-js
- ADR-045: MAD template standard
- ADR-047: MCP request logging (via mad-core)
- ADR-048: Git safety net strategy
