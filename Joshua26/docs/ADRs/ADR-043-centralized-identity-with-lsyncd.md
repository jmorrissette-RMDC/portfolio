# ADR-043: Centralized Identity with Lsyncd

## Status
Accepted

## Date
2026-01-09

## Context

The Joshua ecosystem spans multiple servers (Irina, M5, and future nodes) with:
- Containers requiring consistent UID/GID for file permissions
- Need for automatic synchronization without manual steps
- Single administrator (conflicts not a concern)
- Rare identity changes (only when adding new containers)

Requirements identified:
1. **Scalability** - More servers coming, need identity that scales
2. **Automation** - Zero "remember to do X" manual steps
3. **Simplicity** - Minimal infrastructure, easy to understand
4. **No single point of failure** - Works if either server is down

## Decision

We will use **Lsyncd (Live Syncing Daemon)** to keep identity files synchronized across all servers in real-time.

### Why Lsyncd (Not FreeIPA)

| Factor | Lsyncd | FreeIPA |
|--------|--------|---------|
| Complexity | Low - single daemon | High - LDAP, Kerberos, DNS |
| Setup time | 15 minutes | 2-4 hours |
| New services | 1 (lsyncd) | Multiple (389DS, KDC, etc.) |
| DNS requirements | None | Requires SRV records |
| Immediate sync | Yes | Yes |
| Manual steps | Zero | Zero |

### Why Lsyncd is Safe For Our Use Case

Gemini CLI review identified risks with Lsyncd (conflicts, atomicity, scaling). These are mitigated by our specific situation:

| Risk | Mitigation |
|------|------------|
| Conflicts from simultaneous edits | Single administrator - not possible |
| Atomicity issues | Rare changes, low probability window |
| Scaling complexity | Accept mesh topology for now; migrate to FreeIPA if >4 servers |
| Root SSH trust | Already have root-equivalent access between servers |

### Future Migration Path

When the environment grows beyond 4 servers or requires:
- Centralized SSH key management
- HBAC (Host-Based Access Control)
- Audit trails
- Service authentication (Kerberos)

...we will migrate to FreeIPA. Lsyncd is the "simple now" solution.

## Architecture

```
┌─────────────────┐         ┌─────────────────┐
│     Irina       │         │       M5        │
│  192.168.1.110  │         │  192.168.1.120  │
│                 │         │                 │
│  lsyncd ────────┼────────►│  /etc/passwd    │
│    watches:     │◄────────┼──── lsyncd      │
│  /etc/passwd    │         │    watches:     │
│  /etc/group     │ bidir   │  /etc/passwd    │
│  /etc/shadow    │  sync   │  /etc/group     │
│  /etc/gshadow   │         │  /etc/shadow    │
│  /etc/subuid    │         │  /etc/gshadow   │
│  /etc/subgid    │         │  /etc/subuid    │
│                 │         │  /etc/subgid    │
└─────────────────┘         └─────────────────┘
```

Changes on either machine immediately sync to the other via rsync over SSH.

### Files Synchronized

| File | Purpose |
|------|---------|
| /etc/passwd | User accounts |
| /etc/group | Group definitions |
| /etc/shadow | Password hashes |
| /etc/gshadow | Group passwords |
| /etc/subuid | Container UID mappings |
| /etc/subgid | Container GID mappings |

### User/Group Schema

**Primary Group (All Services):**
| GID | Group Name | Purpose |
|-----|------------|---------|
| 2001 | administrators | ALL service containers use this as primary group |

**Obsolete Groups (Do Not Use):**
| GID | Group Name | Status |
|-----|------------|--------|
| 2000 | joshua-services | OBSOLETE - migrated to administrators (2001) |
| 2002 | joshua-readonly | OBSOLETE - migrated to administrators (2001) |

**Pattern:** All containers run with GID 2001 (administrators) as their primary group. This provides consistent group ownership across all services and simplifies permission management.

**Supplementary Groups:** When containers need to read host files, supplementary groups can be added via `group_add` in docker-compose.yml. The primary group remains 2001.

**User Assignments:** See `registry.yml` for the authoritative list of UID assignments. All users are created with GID 2001 (administrators) as their primary group.

**Note:** All new services follow this pattern. Legacy references to joshua-services (2000) or joshua-readonly (2002) should be updated to administrators (2001).

### State 1 MAD Groups: Identity and Registry

**UID Assignment:**
- One UID per MAD group (not per container)
- All containers in the MAD group share the same UID
- UID sharing is configured in `docker-compose.yml` and Dockerfiles, not in the registry
- Example: Rogers MAD (rogers, rogers-langgraph, rogers-postgres, rogers-neo4j, rogers-redis) all use UID 2002

**Rationale:**
- File permission consistency across containers in the group
- Workspace sharing (`/workspace/[mad-name]`) requires same UID for read/write access
- Database files in `/workspace/[mad-name]/databases/` accessible to all group members
- Simplifies permission management within bounded context

**Registry: One Entry Per MAD (Gateway Only)**

The registry lists MADs, not sub-containers. Each MAD has one entry — the MCP gateway — because that is the only container reachable on joshua-net. Sub-container ports are on private `[mad]-net` networks and are irrelevant to external consumers (Sam, peers, operators). Sub-container topology is fully described in `docker-compose.yml`.

**Registry fields:**

| Field | Required | Description |
|-------|----------|-------------|
| uid | ✅ | Unique per MAD group |
| gid | ✅ | Always 2001 (administrators) |
| port | ✅ | MCP gateway port on joshua-net |
| host | ✅ | Deployment host |
| description | ✅ | What the MAD does |
| mcp_endpoints | ✅ | health and stream endpoints |
| gpu | Optional | If the MAD uses GPU resources |

**Example (Rogers MAD — 5 containers, 1 registry entry):**

```yaml
rogers:
  uid: 2002
  gid: 2001
  port: 6380
  host: m5
  description: Conversation memory + context management (5-container MAD group gateway)
  mcp_endpoints:
    health: /health
    stream: /mcp
```

---

## Implementation

### Prerequisites

SSH key-based access between servers (already completed):
- Irina can SSH to M5 as root
- M5 can SSH to Irina as root

### Step 1: Install Lsyncd (Both Servers)

```bash
sudo apt update
sudo apt install lsyncd
```

### Step 2: Configure Lsyncd on Irina

```bash
sudo mkdir -p /etc/lsyncd
sudo tee /etc/lsyncd/lsyncd.conf.lua << 'EOF'
settings {
    logfile = "/var/log/lsyncd/lsyncd.log",
    statusFile = "/var/log/lsyncd/lsyncd.status",
    nodaemon = false
}

sync {
    default.rsync,
    source = "/etc/",
    target = "m5.joshua.local:/etc/",
    delay = 1,
    rsync = {
        archive = true,
        perms = true,
        owner = true,
        group = true,
        rsh = "/usr/bin/ssh -i /root/.ssh/id_ed25519 -o StrictHostKeyChecking=no"
    },
    filter = {
        '+ passwd',
        '+ group',
        '+ shadow',
        '+ gshadow',
        '+ subuid',
        '+ subgid',
        '- *'
    }
}
EOF
```

### Step 3: Configure Lsyncd on M5

```bash
sudo mkdir -p /etc/lsyncd
sudo tee /etc/lsyncd/lsyncd.conf.lua << 'EOF'
settings {
    logfile = "/var/log/lsyncd/lsyncd.log",
    statusFile = "/var/log/lsyncd/lsyncd.status",
    nodaemon = false
}

sync {
    default.rsync,
    source = "/etc/",
    target = "irina.joshua.local:/etc/",
    delay = 1,
    rsync = {
        archive = true,
        perms = true,
        owner = true,
        group = true,
        rsh = "/usr/bin/ssh -i /root/.ssh/id_ed25519 -o StrictHostKeyChecking=no"
    },
    filter = {
        '+ passwd',
        '+ group',
        '+ shadow',
        '+ gshadow',
        '+ subuid',
        '+ subgid',
        '- *'
    }
}
EOF
```

### Step 4: Set Up Root SSH Keys

```bash
# On Irina (as root)
sudo ssh-keygen -t ed25519 -f /root/.ssh/id_ed25519 -N ''
# Copy to M5
sudo ssh-copy-id -i /root/.ssh/id_ed25519.pub root@m5.joshua.local

# On M5 (as root)
sudo ssh-keygen -t ed25519 -f /root/.ssh/id_ed25519 -N ''
# Copy to Irina
sudo ssh-copy-id -i /root/.ssh/id_ed25519.pub root@irina.joshua.local
```

### Step 5: Create Log Directory and Start Service

```bash
# On both servers
sudo mkdir -p /var/log/lsyncd
sudo systemctl enable lsyncd
sudo systemctl start lsyncd
sudo systemctl status lsyncd
```

### Step 6: Create Initial Group (On Either Server)

```bash
# Primary group (ALL services use this)
sudo groupadd -g 2001 administrators

# Obsolete groups (DO NOT CREATE - for reference only)
# GID 2000 (joshua-services) - OBSOLETE
# GID 2002 (joshua-readonly) - OBSOLETE

# Users are created per registry.yml as needed
# Pattern for user creation:
# sudo useradd -u [UID] -g 2001 -M -s /usr/sbin/nologin [username]
#
# Example:
# sudo useradd -u 2002 -g 2001 -M -s /usr/sbin/nologin [mad-name]
```

Wait a few seconds, then verify on the OTHER server:
```bash
getent group administrators
# Verify any created users show gid=2001(administrators)
id [username]
```

---

## Verification

### Check Lsyncd Status
```bash
sudo systemctl status lsyncd
cat /var/log/lsyncd/lsyncd.status
```

### Test Sync
```bash
# On Irina
sudo useradd -u 9999 -M -s /usr/sbin/nologin testuser

# On M5 (within seconds)
getent passwd testuser

# Cleanup
sudo userdel testuser  # Will sync deletion too
```

---

## Adding New Servers

When adding a 3rd server:

1. Install lsyncd on new server
2. Configure to sync with ONE existing server (not full mesh)
3. That server syncs to others (chain topology)

```
Irina <──► M5 <──► Server3
```

This avoids full mesh complexity. Changes propagate through the chain.

---

## Recovery Procedures

### If Lsyncd Stops
```bash
sudo systemctl restart lsyncd
sudo journalctl -u lsyncd -f  # Watch logs
```

### If Servers Diverge
Pick one server as authoritative, copy its files to the other:
```bash
# Make Irina authoritative
sudo rsync -av /etc/passwd /etc/group /etc/shadow /etc/gshadow /etc/subuid /etc/subgid root@m5:/etc/
```

### If SSH Breaks
Lsyncd requires SSH. If keys are compromised:
1. Regenerate keys on both servers
2. Re-exchange public keys
3. Restart lsyncd

---

## Consequences

### Positive
- Zero manual steps after initial setup
- Immediate synchronization
- Simple to understand and debug
- No new complex infrastructure
- Works if either server is down (changes sync when it returns)

### Negative
- Root SSH trust between servers (accepted risk)
- No audit trail of changes
- Last-write-wins conflict resolution (mitigated by single admin)
- Mesh topology if many servers (mitigated by chain topology)

### Neutral
- Will migrate to FreeIPA when environment grows
- SSH key management remains manual (future enhancement)

---

## References

- Lsyncd documentation: https://lsyncd.github.io/lsyncd/
- Reviewed by: Google Gemini CLI (2026-01-09) - risks acknowledged and mitigated
- Future: ADR-04X for FreeIPA migration when needed
