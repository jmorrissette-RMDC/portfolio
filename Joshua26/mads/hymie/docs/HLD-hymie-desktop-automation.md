# High-Level Design: Hymie Desktop Automation

**Version:** 1.0
**Date:** 2026-01-14
**Status:** Implemented
**Owner:** Aristotle9
**Related Documents:** REQ-016-hymie-desktop-automation.md, hymie-desktop-automation-implementation.md

---

## Executive Summary

Hymie is a desktop automation MAD (MCP Application Daemon) that provides human-like input simulation for the Joshua ecosystem. It enables AI agents to control a native Wayland/GNOME desktop in a way that is indistinguishable from human interaction, making it suitable for scenarios where bot detection must be evaded.

**Key Innovation:** Hymie uses kernel-level input injection via `/dev/uinput` for all operations, including screenshot capture. This ensures all actions follow the same path as physical hardware, bypassing security restrictions and bot detection.

**Architecture Overview:**

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              JOSHUA ECOSYSTEM                                    │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│   ┌──────────────┐     ┌──────────────┐     ┌──────────────────────────────┐   │
│   │ Claude Code  │────▶│     Sam      │────▶│      Hymie Container         │   │
│   │   (Client)   │     │   (Relay)    │     │                              │   │
│   └──────────────┘     └──────────────┘     │  ┌────────────────────────┐  │   │
│                              MCP            │  │   NativeDesktopManager │  │   │
│                                             │  │   - Screenshot capture │  │   │
│                                             │  │   - Window management  │  │   │
│                                             │  └────────────────────────┘  │   │
│                                             │                              │   │
│                                             │  ┌────────────────────────┐  │   │
│                                             │  │     UInputDevice       │  │   │
│                                             │  │   - Virtual keyboard   │  │   │
│                                             │  │   - Virtual mouse      │  │   │
│                                             │  └───────────┬────────────┘  │   │
│                                             └──────────────┼──────────────┘   │
│                                                            │                   │
├────────────────────────────────────────────────────────────┼───────────────────┤
│                         LINUX KERNEL                       │                   │
│                                                            ▼                   │
│   ┌────────────────────────────────────────────────────────────────────────┐  │
│   │                         /dev/uinput                                     │  │
│   │                    (Virtual Input Device)                               │  │
│   └────────────────────────────────────────────────────────────────────────┘  │
│                                    │                                          │
│                                    ▼                                          │
│   ┌────────────────────────────────────────────────────────────────────────┐  │
│   │                      Input Subsystem                                    │  │
│   │            (Identical path to physical hardware)                        │  │
│   └────────────────────────────────────────────────────────────────────────┘  │
│                                    │                                          │
├────────────────────────────────────┼──────────────────────────────────────────┤
│                         USERSPACE  │                                          │
│                                    ▼                                          │
│   ┌────────────────────────────────────────────────────────────────────────┐  │
│   │                          libinput                                       │  │
│   │                  (Input Event Processing)                               │  │
│   └────────────────────────────────────────────────────────────────────────┘  │
│                                    │                                          │
│                                    ▼                                          │
│   ┌────────────────────────────────────────────────────────────────────────┐  │
│   │                    GNOME/Mutter (Wayland)                               │  │
│   │                                                                         │  │
│   │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │  │
│   │  │   Firefox   │  │  Terminal   │  │   Files     │  │   Other     │   │  │
│   │  │  (Wayland)  │  │ (Wayland)   │  │  (Wayland)  │  │    Apps     │   │  │
│   │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘   │  │
│   │                                                                         │  │
│   └────────────────────────────────────────────────────────────────────────┘  │
│                                                                               │
└───────────────────────────────────────────────────────────────────────────────┘
```

---

## Problem Statement

### Anti-Bot Detection Challenge

Modern web applications employ sophisticated bot detection that identifies automation tools by:

1. **Synthetic Event Detection**: X11's XSendEvent flag marks programmatic input
2. **Device Fingerprinting**: Checking for physical device characteristics
3. **Timing Analysis**: Perfect timing indicates automation
4. **Input Patterns**: Lack of natural movement curves and variance

Traditional tools (Playwright, Selenium, xdotool) fail these checks because they inject events at the application level, not the kernel level.

### Wayland Screenshot Security

GNOME/Wayland restricts programmatic screenshots to prevent screen capture malware:

- **D-Bus org.gnome.Shell.Screenshot**: Returns "Screenshot is not allowed"
- **XDG Desktop Portal**: Requires user consent dialog
- **X11 tools (scrot, mss)**: Only capture Xwayland apps, miss native Wayland

---

## Solution Architecture

### Design Principles

1. **Kernel-Level Everything**: All operations go through `/dev/uinput` for authenticity
2. **Human-Like Behavior**: Configurable timing profiles with natural variance
3. **Container Isolation**: MCP server runs containerized with minimal privileges
4. **Native Session**: Target the actual desktop, not a virtual display

### Input Path

```
Hymie Container (python-evdev)
         │
         ▼
    /dev/uinput
         │
         ▼
  Linux Kernel Input Subsystem
         │
         ▼
      libinput
         │
         ▼
  Wayland Compositor (GNOME/Mutter)
         │
         ▼
    Application
```

This path is **identical to physical USB keyboard/mouse input**. No software can distinguish Hymie's input from real hardware.

### Screenshot Path

```
Hymie presses Shift+PrintScreen via uinput
         │
         ▼
  Kernel treats as physical keypress
         │
         ▼
  GNOME receives trusted input
         │
         ▼
  GNOME captures ALL Wayland surfaces
         │
         ▼
  Saves to ~/Pictures/Screenshots/
         │
         ▼
  Hymie polls, reads, returns base64
         │
         ▼
  Hymie deletes file (cleanup)
```

This approach:
- Captures **all** desktop content (Wayland + Xwayland)
- Bypasses D-Bus security restrictions
- Appears as human pressing PrintScreen
- Has natural ~300-500ms latency

---

## Component Design

### UInputDevice Class

Manages virtual keyboard and mouse devices via the Linux uinput interface.

```python
class UInputDevice:
    """Virtual input devices via uinput."""

    def __init__(self):
        # Create virtual keyboard with all keys
        self.keyboard = UInput({
            ecodes.EV_KEY: list(KEY_MAP.values())
        }, name='hymie-keyboard')

        # Create virtual mouse with relative movement
        self.mouse = UInput({
            ecodes.EV_KEY: [BTN_LEFT, BTN_RIGHT, BTN_MIDDLE],
            ecodes.EV_REL: [REL_X, REL_Y, REL_WHEEL]
        }, name='hymie-mouse')

    def press_key(self, key_code: int) -> None:
        self.keyboard.write(ecodes.EV_KEY, key_code, 1)
        self.keyboard.syn()

    def release_key(self, key_code: int) -> None:
        self.keyboard.write(ecodes.EV_KEY, key_code, 0)
        self.keyboard.syn()

    def move_mouse_relative(self, dx: int, dy: int) -> None:
        self.mouse.write(ecodes.EV_REL, ecodes.REL_X, dx)
        self.mouse.write(ecodes.EV_REL, ecodes.REL_Y, dy)
        self.mouse.syn()
```

### NativeDesktopManager Class

Handles screenshots, window management, and clipboard operations.

```python
class NativeDesktopManager:
    """Desktop operations for native Wayland/GNOME."""

    SCREENSHOTS_DIR = '/screenshots'
    SCREENSHOT_TIMEOUT = 2.0

    def screenshot(self, region=None) -> bytes:
        """Capture via Shift+PrintScreen."""
        existing = self._get_existing_screenshots()

        # Press Shift+PrintScreen via uinput
        device = self._get_uinput()
        device.press_key(KEY_LEFTSHIFT)
        device.press_key(KEY_SYSRQ)
        device.release_key(KEY_SYSRQ)
        device.release_key(KEY_LEFTSHIFT)

        # Wait for file to appear
        new_file = self._wait_for_new_screenshot(existing)

        # Read and cleanup
        with open(new_file, 'rb') as f:
            png_data = f.read()
        os.unlink(new_file)

        return png_data
```

### HumanTiming Class

Provides configurable human-like timing with natural variance.

```python
class HumanTiming:
    """Human-like timing profiles."""

    PROFILES = {
        'instant': {'key_delay': (0, 0), 'mouse_speed': (0, 0)},
        'fast':    {'key_delay': (10, 30), 'mouse_speed': (50, 100)},
        'human':   {'key_delay': (50, 150), 'mouse_speed': (300, 800)},
        'slow':    {'key_delay': (100, 300), 'mouse_speed': (500, 1500)},
    }

    def key_delay(self) -> float:
        min_ms, max_ms = self.config['key_delay']
        delay = random.randint(min_ms, max_ms)
        variance = random.uniform(0.9, 1.1)  # +/- 10%
        return (delay * variance) / 1000.0
```

---

## Container Configuration

### Docker Compose

```yaml
services:
  hymie:
    build:
      context: /mnt/storage/projects/Joshua26
      dockerfile: mads/hymie/Dockerfile
    container_name: hymie
    restart: unless-stopped

    # Run as host user for session access
    user: "1000:1000"

    # Device mount for kernel-level input
    devices:
      - /dev/uinput:/dev/uinput

    # Input group for uinput access
    group_add:
      - "995"

    # AppArmor disabled for D-Bus access
    security_opt:
      - apparmor:unconfined

    environment:
      - DISPLAY=:0
      - WAYLAND_DISPLAY=wayland-0
      - XDG_RUNTIME_DIR=/run/user/1000
      - DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus
      - MCP_PORT=9223

    volumes:
      - /mnt/storage:/storage:ro
      - /mnt/workspace:/workspace
      - /tmp/.X11-unix:/tmp/.X11-unix:ro
      - /run/user/1000:/run/user/1000
      - /home/aristotle9/Pictures/Screenshots:/screenshots

    networks:
      - joshua-net
```

### ADR-050 Exceptions

| Exception | Purpose | Risk Mitigation |
|-----------|---------|-----------------|
| /dev/uinput device | Kernel input injection | Network isolation, minimal image |
| /tmp/.X11-unix | Xwayland queries | Read-only mount |
| /run/user/1000 | D-Bus/Wayland session | Session-bound to user 1000 |
| ~/Pictures/Screenshots | PrintScreen capture | Auto-cleanup after read |
| input group (995) | uinput permissions | Specific to input devices |
| apparmor:unconfined | D-Bus session access | Network isolation |

---

## MCP Tools

### Tool Categories

| Category | Tools | Description |
|----------|-------|-------------|
| Input | 8 tools | Keyboard and mouse simulation |
| Screen | 4 tools | Screenshot and pixel operations |
| Window | 4 tools | Window management |
| Process | 1 tool | Application launch |
| Clipboard | 2 tools | Copy/paste operations |
| Timing | 2 tools | Timing control |

### Input Tools

```
desktop_click(x, y, button='left')      # Click at coordinates
desktop_double_click(x, y)              # Double-click
desktop_type(text, delay_ms=0)          # Type text with timing
desktop_press_key(key)                  # Single key press
desktop_hotkey(keys[])                  # Key combination
desktop_mouse_move(dx, dy, duration_ms) # Relative mouse move
desktop_drag(x1, y1, x2, y2, duration)  # Drag operation
desktop_scroll(direction, amount)       # Scroll wheel
```

### Screen Tools

```
desktop_screenshot(region?)             # Capture via PrintScreen
desktop_get_screen_size()               # Get dimensions
desktop_get_pixel(x, y)                 # Get pixel color
desktop_find_image(template, threshold) # Template matching
```

---

## Security Considerations

### Threat Model

| Threat | Mitigation |
|--------|------------|
| Malicious input injection | Network isolation (joshua-net only) |
| Container escape | Minimal base image, no root |
| Credential theft | No sensitive data on workstation |
| Session hijacking | Bound to user 1000 session only |

### Defense in Depth

1. **Network Layer**: No exposed ports, internal network only
2. **Container Layer**: Minimal image, non-root user
3. **Session Layer**: Bound to specific user session
4. **Host Layer**: Workstation isolated from production

---

## Performance Characteristics

| Operation | Latency | Notes |
|-----------|---------|-------|
| Key press | <1ms | Direct uinput write |
| Mouse move | <1ms | Relative movement |
| Screenshot | 300-500ms | PrintScreen + file I/O |
| Window focus | 50-100ms | wmctrl execution |
| Clipboard | 50-100ms | wl-copy/wl-paste |

### Screenshot Latency Breakdown

```
Shift+PrintScreen press:   ~50ms
GNOME capture:            ~100ms
File write:               ~100ms
File detection poll:      ~100ms
File read:                 ~50ms
Cleanup:                   ~10ms
─────────────────────────────────
Total:                   ~400ms
```

This latency is a **feature**, not a bug. It matches human behavior and helps avoid bot detection.

---

## Comparison with Alternatives

### Hymie vs Playwright/Selenium

| Aspect | Hymie | Playwright/Selenium |
|--------|-------|---------------------|
| Input method | Kernel uinput | Browser DevTools Protocol |
| Bot detection | Evades | Easily detected |
| Desktop apps | Full support | Browser only |
| Screenshot | Full Wayland | Browser viewport |
| Timing | Human-like | Instant |

### Hymie vs Malory

| Aspect | Hymie | Malory |
|--------|-------|--------|
| Target | Native desktop | Headless browser |
| Speed | Human-like (slow) | Fast |
| Detection | Evades | Detectable |
| Scope | Any GUI app | Web pages |
| Use case | Anti-bot, RPA | Testing, scraping |

**Recommendation:** Use Malory for fast headless operations, Hymie when bot evasion is required.

---

## Future Enhancements

### Potential Improvements

1. **Multi-monitor support**: Handle multiple displays
2. **Video recording**: Capture automation sessions
3. **OCR integration**: Text recognition from screenshots
4. **Gesture support**: Multi-touch gestures
5. **Audio control**: Volume and playback

### Not Planned

- GPU acceleration (not needed)
- Multiple simultaneous desktops (complexity)
- Mobile device support (different architecture)

---

## References

- **REQ-016**: Hymie Desktop Automation Requirements
- **ADR-039**: Radical Simplification (volume policy)
- **ADR-045**: MAD Template Standard
- **ADR-050**: Approved Exceptions
- **Linux uinput**: https://www.kernel.org/doc/html/latest/input/uinput.html
- **python-evdev**: https://python-evdev.readthedocs.io/

---

**Document Version:** 1.0
**Last Updated:** 2026-01-14
**Status:** Implemented and Operational
