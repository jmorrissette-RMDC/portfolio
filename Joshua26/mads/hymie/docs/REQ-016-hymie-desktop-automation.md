# REQ-016: Hymie Desktop Automation

**Status:** Implemented
**Date:** 2026-01-13
**Updated:** 2026-01-14
**Priority:** High

## Overview

Hymie provides human-like desktop automation via MCP, enabling Joshua to control the native Wayland/GNOME desktop environment with kernel-level input simulation. This evades anti-bot detection by injecting input events through uinput, making them indistinguishable from real hardware input.

## Scope

Hymie handles **human-like desktop automation**:
- Kernel-level input via uinput (appears as real hardware)
- Native Wayland/GNOME desktop (not VNC)
- PrintScreen-based screenshot capture (human-like)
- Configurable human-like timing
- General desktop automation (not just browsers)
- Anti-bot evasion capable

For **fast headless browser automation** (Playwright, no anti-bot evasion), see **REQ-002: Malory Browser Automation**.

## Architecture

```
[Claude Code] --> [Sam] --> [Hymie Container] --> /dev/uinput --> kernel --> libinput --> Wayland compositor
                                  |                                                              |
                                  +--- Screenshots via Shift+PrintScreen -------------------------+
                                       (uinput keypress → GNOME saves → Hymie reads → cleanup)
```

### Input Path (Human-like)

```
Hymie container
    ↓
/dev/uinput (kernel device)
    ↓
Linux kernel input subsystem
    ↓
libinput (userspace input daemon)
    ↓
Wayland compositor (GNOME/Mutter)
    ↓
Application receives input
```

This path is **identical to physical hardware input**. Bot detection cannot distinguish Hymie's input from a real keyboard/mouse.

### Screenshot Path (Human-like)

```
Hymie presses Shift+PrintScreen via uinput
    ↓
GNOME captures full desktop (all Wayland surfaces)
    ↓
Saved to ~/Pictures/Screenshots/
    ↓
Hymie reads file, returns base64 PNG
    ↓
File auto-deleted after read
```

This approach bypasses GNOME's D-Bus screenshot security restriction while appearing as a human pressing PrintScreen.

### Key Design Decisions

1. **uinput for input**: Events injected at kernel level appear as real hardware input
2. **Native Wayland session**: Targets the actual desktop, not a VNC virtual display
3. **PrintScreen for screenshots**: Human-like capture that bypasses security restrictions
4. **Container isolation**: MCP server runs containerized on joshua-net
5. **AppArmor unconfined**: Required for D-Bus session access

**Note:** VNC is available for remote monitoring but is not part of the automation architecture.

### ADR-050 Exceptions

Hymie requires exceptions to standard MAD policies:

| ADR | Requirement | Exception | Justification |
|-----|-------------|-----------|---------------|
| ADR-039 | Two-volume policy | `/dev/uinput` device mount | Kernel-level input injection |
| ADR-039 | Two-volume policy | `/tmp/.X11-unix` socket mount (ro) | Xwayland app queries |
| ADR-039 | Two-volume policy | `/run/user/1000` mount | D-Bus/Wayland session access |
| ADR-039 | Two-volume policy | `~/Pictures/Screenshots` mount | PrintScreen capture |
| ADR-045 | Standard permissions | `input` group (GID 995) | uinput device access |
| ADR-045 | Standard permissions | AppArmor unconfined | D-Bus session bus access |

**Justification**: Hymie's core purpose requires kernel-level input injection and native desktop access. This cannot be achieved with standard container isolation.

## Container Details

| Property | Value |
|----------|-------|
| Name | hymie |
| UID | 1000 (host user) |
| GID | 1000 (host user) |
| Port | 9223 |
| Host | Aristotle9 workstation |
| Base | ADR-045 template (with exceptions) |

### Special Mounts

| Mount | Source | Target | Mode | Purpose |
|-------|--------|--------|------|---------|
| uinput | /dev/uinput | /dev/uinput | rw | Kernel input injection |
| X11 socket | /tmp/.X11-unix | /tmp/.X11-unix | ro | Xwayland app access |
| XDG runtime | /run/user/1000 | /run/user/1000 | rw | D-Bus/Wayland session |
| Screenshots | ~/Pictures/Screenshots | /screenshots | rw | PrintScreen capture |

### Environment Variables

| Variable | Value | Purpose |
|----------|-------|---------|
| DISPLAY | :0 | Xwayland display |
| WAYLAND_DISPLAY | wayland-0 | Native Wayland socket |
| XDG_RUNTIME_DIR | /run/user/1000 | Runtime directory |
| DBUS_SESSION_BUS_ADDRESS | unix:path=/run/user/1000/bus | D-Bus session |

### Security Configuration

| Setting | Value | Purpose |
|---------|-------|---------|
| user | 1000:1000 | Run as host user for session access |
| group_add | 995 (input) | uinput device permissions |
| security_opt | apparmor:unconfined | D-Bus session access |

### Security Mitigations

Access to `/dev/uinput` grants significant privileges. If compromised, the container could inject malicious input to the host. The following mitigations are in place:

| Mitigation | Implementation | Rationale |
|------------|----------------|-----------|
| Minimal base image | python:3.11-slim | Reduce attack surface |
| Network isolation | joshua-net only, no exposed ports | Limit network attack vectors |
| Read-only storage | /storage mounted read-only | Prevent data modification |
| Session binding | Runs as host user 1000 | Access only current session |

**Risk Assessment:** Hymie runs on a dedicated automation workstation. The host desktop is the user's primary workstation but is isolated from production systems.

## MCP Tools

All tools use the `desktop_` prefix per ADR-045.

### Input Simulation

| Tool | Parameters | Description |
|------|------------|-------------|
| desktop_click | x, y, button? | Click at coordinates (button: left/right/middle) |
| desktop_double_click | x, y | Double-click at coordinates |
| desktop_type | text, delay_ms? | Type text with optional per-key delay |
| desktop_press_key | key | Press single key (Enter, Tab, Escape, etc.) |
| desktop_hotkey | keys[] | Key combination (e.g., ["ctrl", "c"]) |
| desktop_mouse_move | dx, dy, duration_ms? | Move mouse relative (optional smooth curve) |
| desktop_drag | x1, y1, x2, y2, duration_ms? | Drag from point to point |
| desktop_scroll | direction, amount | Scroll (direction: up/down/left/right) |

### Screen Capture

| Tool | Parameters | Description |
|------|------------|-------------|
| desktop_screenshot | region? | Capture via PrintScreen, returns base64 PNG |
| desktop_get_screen_size | - | Get screen dimensions |
| desktop_get_pixel | x, y | Get pixel color at coordinates |
| desktop_find_image | template_base64, threshold? | Find image on screen, returns coordinates |

### Window Management

| Tool | Parameters | Description |
|------|------------|-------------|
| desktop_list_windows | - | List all open windows with titles and geometry |
| desktop_focus_window | title_pattern | Focus window by title (regex) |
| desktop_close_window | title_pattern | Close window by title |
| desktop_get_active_window | - | Get info about focused window |

### Process Control

| Tool | Parameters | Description |
|------|------------|-------------|
| desktop_launch | command, wait_ms? | Launch application |

### Clipboard

| Tool | Parameters | Description |
|------|------------|-------------|
| desktop_get_clipboard | - | Read clipboard contents (wl-paste) |
| desktop_set_clipboard | text | Set clipboard contents (wl-copy) |

### Human-like Timing

| Tool | Parameters | Description |
|------|------------|-------------|
| desktop_set_timing | profile | Set timing profile (instant/fast/human/slow) |
| desktop_wait | ms | Wait for specified milliseconds |

## Timing Profiles

Human-like automation requires realistic timing. Configurable profiles:

| Profile | Key Delay | Mouse Speed | Use Case |
|---------|-----------|-------------|----------|
| instant | 0ms | instant | Testing, debugging |
| fast | 10-30ms | 100ms moves | Light bot detection |
| human | 50-150ms | 300-800ms moves | Medium bot detection |
| slow | 100-300ms | 500-1500ms moves | Strict bot detection |

Default: `human`

## Screenshot Implementation

GNOME/Wayland restricts programmatic screenshots via D-Bus for security (prevents screen capture malware). Hymie bypasses this using the same method a human would:

1. **Press Shift+PrintScreen** via uinput (kernel-level, trusted by GNOME)
2. **GNOME captures** full desktop including all Wayland surfaces
3. **File saved** to `~/Pictures/Screenshots/Screenshot from YYYY-MM-DD HH-MM-SS.png`
4. **Hymie reads** the file and returns base64 PNG
5. **Auto-cleanup** deletes the file after reading

**Latency:** ~300-500ms (human-like, not instant)

This approach:
- Captures ALL desktop content (Wayland + Xwayland)
- Is indistinguishable from a human taking a screenshot
- Has natural latency that helps avoid bot detection

## Use Cases

1. **Anti-bot browser automation** - Interact with sites that detect Playwright/Selenium
2. **Desktop application automation** - Automate any GUI application
3. **Visual testing** - Screenshot comparison, pixel-perfect testing
4. **RPA workflows** - Robotic process automation for legacy applications
5. **Human simulation** - Tasks that require appearing human

## Implementation Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| MCP Server | mad-core-py | FastMCP wrapper |
| Input | python-evdev | uinput device creation and events |
| Screenshots | Shift+PrintScreen | Human-like full desktop capture |
| Image Processing | Pillow | Image manipulation and encoding |
| Window Mgmt | wmctrl, xdotool | Window queries and control |
| Image Match | opencv-python | Template matching for find_image |
| Clipboard | wl-copy, wl-paste | Wayland clipboard access |
| D-Bus | dbus-python | Session bus communication |

## Non-Goals

- Multiple simultaneous desktops
- GPU acceleration
- Video recording (future consideration)
- Audio control
- Region-specific screenshots (full screen only via PrintScreen)

## Dependencies

### Python Packages
- mad-core-py (ADR-042)
- evdev (kernel uinput interface)
- python-xlib (X11 queries via Xwayland)
- Pillow (image processing)
- opencv-python-headless (template matching)
- httpx (health checks)
- dbus-python (D-Bus session access)

### System Packages
- scrot (X11 screenshot fallback)
- wmctrl (window management)
- xdotool (window queries)
- wl-clipboard (Wayland clipboard)

### Host Requirements
- Native Wayland/GNOME session running
- /dev/uinput device available
- Host user in `input` group
- ~/Pictures/Screenshots directory accessible
- D-Bus session bus available

## References

- ADR-039: Radical Simplification
- ADR-045: MAD Template Standard
- ADR-050: Approved Exceptions
- REQ-002: Malory Browser Automation (headless alternative)
- HLD-hymie-desktop-automation: High-level design document
