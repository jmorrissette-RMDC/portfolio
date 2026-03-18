# ADR-050: Approved ADR Exceptions

**Status:** Accepted
**Date:** 2026-01-13
**Deciders:** System Architect

---

## Important Notice

**Each exception in this document is approved on a strictly case-by-case basis requiring explicit user approval.**

**No exception listed here should be interpreted as approval for any other component, pattern, or situation.** The existence of one exception does not imply that similar exceptions will be granted. Each case must be evaluated on its own merits and requires separate approval.

This document serves as a central registry of all approved deviations from Joshua ADRs.

---

## Approved Exceptions

### 1. Sam (MCP Relay)

**Component:** Sam - MCP stdio-to-HTTP relay

**ADRs Excepted:**
| ADR | Requirement | Exception |
|-----|-------------|-----------|
| ADR-039 | Two-volume mounting policy (storage:/storage, workspace:/workspace) | No container volumes |
| ADR-043 | Service account with UID from registry | Runs as local process, no container user |
| ADR-045 | MAD template standard (Dockerfile, container, service account) | Not containerized |

**Justification:**

Sam has a unique architectural role in the Joshua ecosystem (per ADR-040). It must:

1. **Run as a local process** - Claude Code communicates via stdio, which requires a local process, not a containerized service
2. **Bridge protocols** - Translates between stdio (Claude Code) and HTTP/SSE (containerized MADs)
3. **Run on the developer workstation** - Must be co-located with Claude Code

Sam cannot be containerized without breaking Claude Code's MCP integration. This is a fundamental architectural constraint, not a preference.

**Approved:** 2026-01-13

---

### 2. GPUStack Runner Containers (Sutherland)

**Component:** Inference backend containers spawned by GPUStack v2.x within Sutherland

**ADRs Excepted:**
| ADR | Requirement | Exception |
|-----|-------------|-----------|
| ADR-039 | Two-volume mounting policy | Runner containers mount only model cache directory |
| ADR-043 | Service account with UID from registry, GID 2000 | Runners execute as root |
| ADR-045 | MAD template (non-root service accounts, HEALTHCHECK, etc.) | Third-party containers, privileged mode |

**Additional Security Considerations:**

GPUStack v2.x runner containers require:
- `--privileged` mode
- Docker socket mount (`/var/run/docker.sock`)
- Host network mode
- Root user execution

**Justification:**

These containers are:

1. **Third-party infrastructure** - Not built by Joshua project; spawned automatically by GPUStack for inference workloads (vLLM, llama-server, etc.)
2. **Ephemeral** - Created on model deployment, destroyed when model is undeployed
3. **Isolated to dedicated GPU server** - Only run on M5 (192.168.1.120), a dedicated compute node
4. **Required by upstream architecture** - GPUStack v2.0 dropped native backend support; containerized backends are the only option

**Risk Mitigation:**
- M5 is a dedicated GPU server with no sensitive data
- Runner containers are ephemeral and purpose-specific
- GPUStack is the only component with Docker socket access
- Future: Monitor GPUStack issue #3968 for native backend or CDI support

**References:**
- [GPUStack Issue #3968](https://github.com/gpustack/gpustack/issues/3968) - Security concerns about privileged mode
- GPUStack v2.0 release notes - Native llama-box support removed

**Approved:** 2026-01-13

---

### 3. Hymie (Desktop Automation)

**Component:** Hymie - Desktop automation via uinput for native Wayland/GNOME session

**ADRs Excepted:**
| ADR | Requirement | Exception | Approved |
|-----|-------------|-----------|----------|
| ADR-039 | Two-volume mounting policy | `/dev/uinput` device mount | 2026-01-13 |
| ADR-039 | Two-volume mounting policy | `/tmp/.X11-unix` socket mount (read-only) | 2026-01-13 |
| ADR-045 | Standard container permissions | `input` group membership (GID 995) | 2026-01-13 |
| ADR-039 | Two-volume mounting policy | `/run/user/1000` → `/run/user/1000` (D-Bus/Wayland session) | 2026-01-14 |
| ADR-039 | Two-volume mounting policy | `~/Pictures/Screenshots` → `/screenshots` (PrintScreen capture) | 2026-01-14 |
| ADR-045 | Standard container permissions | `apparmor:unconfined` (D-Bus session access) | 2026-01-14 |

**Justification:**

Hymie's core purpose is human-like desktop automation that evades anti-bot detection. This requires:

1. **uinput access** - Kernel-level input injection creates virtual devices that appear as real hardware. Without this, input events are detectable as synthetic.
2. **X11 socket access** - Required for Xwayland app queries and window management.
3. **Input group** - uinput device access requires `input` group membership.
4. **XDG runtime directory** - `/run/user/1000` provides access to D-Bus session bus and Wayland socket for native session interaction.
5. **Screenshots directory** - PrintScreen-based capture saves to `~/Pictures/Screenshots`. Container reads and deletes after capture.
6. **AppArmor unconfined** - Required for D-Bus session bus access from within container. AppArmor blocks D-Bus connections otherwise.

**Architecture Note:** Hymie targets the native Wayland/GNOME session (not VNC). Screenshots are captured via Shift+PrintScreen through uinput, which bypasses GNOME's D-Bus screenshot security restrictions while appearing as human input.

**Risk Mitigation:**
- Container runs as user 1000 (session owner), not root
- Network isolated to joshua-net only
- /storage mounted read-only
- Screenshots directory is single-purpose location
- Limited to single physical machine (aristotle9 workstation)

**References:**
- REQ-016: Hymie Desktop Automation
- REQ-002: Malory Browser Automation (headless alternative)
- HLD-hymie-desktop-automation: High-level design

**Initial Approval:** 2026-01-13
**Updated:** 2026-01-14 (native Wayland exceptions)

---

## Adding New Exceptions

To request a new exception:

1. Document which ADRs are affected and why
2. Explain why the standard cannot be followed
3. Describe risk mitigation measures
4. Obtain explicit user approval
5. Add entry to this document with approval date

**Reminder:** Exception approval is not automatic. Each case requires individual evaluation and explicit approval.
