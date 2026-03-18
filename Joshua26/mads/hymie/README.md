# Hymie - Desktop Automation MAD

Human-like desktop automation via kernel-level uinput injection.

## Overview

Hymie provides MCP tools for controlling a physical desktop environment with input that appears indistinguishable from real hardware. Unlike browser automation tools (Playwright/Selenium), Hymie's kernel-level input injection evades anti-bot detection.

**Key Features:**
- Kernel-level input via `/dev/uinput` (appears as real USB hardware)
- Human-like timing profiles (instant, fast, human, slow)
- Bezier curve mouse movements
- Screenshot capture and template matching
- Window management via X11

## Architecture

```
[Claude Code] --> [Sam] --> [Hymie Container] --> /dev/uinput --> kernel --> X server
                                  |                                              |
                                  +--- X11 socket (read-only) ------------------+
                                       (screenshots, window queries)
```

**Note:** VNC (port 5902) is available for remote monitoring but is NOT part of the automation path.

## ADR-050 Exceptions

This MAD requires approved exceptions to standard policies:

| ADR | Standard | Exception |
|-----|----------|-----------|
| ADR-039 | Two-volume policy | `/dev/uinput` device mount (rw) |
| ADR-039 | Two-volume policy | `/tmp/.X11-unix` socket mount (ro) |
| ADR-045 | Standard permissions | `input` group membership (GID 995) |

## Container Details

| Property | Value |
|----------|-------|
| Name | hymie |
| UID | 2009 |
| GID | 2000 (joshua-services) |
| Port | 9223 |
| Host | Hymie (192.168.1.130) |
| Base Image | python:3.11-slim |

## MCP Tools (21)

### Input Simulation
| Tool | Description |
|------|-------------|
| `desktop_click` | Click at coordinates (left/right/middle button) |
| `desktop_double_click` | Double-click at coordinates |
| `desktop_type` | Type text with human-like timing |
| `desktop_press_key` | Press single key (Enter, Tab, Escape, F1, etc.) |
| `desktop_hotkey` | Key combination (e.g., Ctrl+C) |
| `desktop_mouse_move` | Move mouse with optional bezier curve |
| `desktop_drag` | Drag from point to point |
| `desktop_scroll` | Scroll wheel (up/down/left/right) |

### Screen Capture
| Tool | Description |
|------|-------------|
| `desktop_screenshot` | Capture full screen or region (base64 PNG) |
| `desktop_get_screen_size` | Get screen dimensions |
| `desktop_get_pixel` | Get pixel color at coordinates |
| `desktop_find_image` | Find template image on screen (OpenCV) |

### Window Management
| Tool | Description |
|------|-------------|
| `desktop_list_windows` | List all visible windows |
| `desktop_focus_window` | Focus window by title (regex) |
| `desktop_close_window` | Close window by title |
| `desktop_get_active_window` | Get info about focused window |

### Process Control
| Tool | Description |
|------|-------------|
| `desktop_launch` | Launch application |

### Clipboard
| Tool | Description |
|------|-------------|
| `desktop_get_clipboard` | Read clipboard contents |
| `desktop_set_clipboard` | Set clipboard contents |

### Timing
| Tool | Description |
|------|-------------|
| `desktop_set_timing` | Set timing profile |
| `desktop_wait` | Wait for milliseconds |

## Timing Profiles

| Profile | Key Delay | Mouse Speed | Use Case |
|---------|-----------|-------------|----------|
| instant | 0ms | instant | Testing, debugging |
| fast | 10-30ms | 50-100ms | Light bot detection |
| human | 50-150ms | 300-800ms | Medium bot detection (default) |
| slow | 100-300ms | 500-1500ms | Strict bot detection |

## Dependencies

### Python Packages
- mad-core-py (MCP server framework)
- evdev (uinput interface)
- python-xlib (X11 window management)
- mss (screen capture)
- Pillow (image processing)
- opencv-python-headless (template matching)
- httpx (health checks)

### Host Requirements
- X server running on display :2
- `/dev/uinput` device with input group access
- User in `input` group
- udev rule: `/etc/udev/rules.d/99-uinput.rules`

## Deployment

### Build
```bash
cd /mnt/storage/projects/Joshua26
docker build -t hymie -f mads/hymie/Dockerfile .
```

### Run
```bash
cd /mnt/storage/projects/Joshua26/mads/hymie
docker compose up -d
```

### Add to Sam
Add to `/mnt/workspace/sam-hymie/config/backends.yaml`:
```yaml
- name: hymie
  url: http://hymie:9223
```

Then restart Sam:
```bash
cd /mnt/workspace/sam-hymie
docker compose restart sam
```

## Usage Examples

### Click at coordinates
```python
desktop_click(x=100, y=200, button='left')
```

### Type with human timing
```python
desktop_set_timing(profile='human')
desktop_type(text='Hello World')
```

### Take screenshot
```python
result = desktop_screenshot()
# Returns {"success": true, "image_base64": "...", "format": "png"}
```

### Find and click image
```python
result = desktop_find_image(template_base64="...", threshold=0.8)
if result['found']:
    desktop_click(x=result['x'], y=result['y'])
```

## Troubleshooting

### Container won't start
- Check uinput permissions: `ls -la /dev/uinput` (should be `crw-rw---- root input`)
- Verify hymie user in input group: `id hymie`
- Check X11 socket: `ls -la /tmp/.X11-unix/X2`

### Tools not appearing in Sam
- Restart Sam after adding to backends.yaml
- Check Hymie logs: `docker logs hymie`
- Verify network: `docker exec sam-hymie ping hymie`

### Permission denied on /dev/uinput
Add udev rule:
```bash
echo 'KERNEL=="uinput", GROUP="input", MODE="0660"' | sudo tee /etc/udev/rules.d/99-uinput.rules
sudo udevadm control --reload-rules
sudo udevadm trigger /dev/uinput
```

## References

- [REQ-016: Hymie Desktop Automation](../../docs/requirements/REQ-016-hymie-desktop-automation.md)
- [ADR-050: Approved Exceptions](../../docs/ADRs/ADR-050-approved-exceptions.md)
- [Planning Document](../../docs/planning/hymie-desktop-automation-implementation.md)
