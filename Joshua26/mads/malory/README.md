# Malory

MCP server for Playwright browser automation.

## Architecture

Single container with embedded Chromium browser. No external dependencies.

## MCP Tools

| Tool | Description |
|------|-------------|
| `browser_navigate` | Navigate to a URL |
| `browser_go_back` | Go back to previous page |
| `browser_go_forward` | Go forward to next page |
| `browser_refresh` | Reload current page |
| `browser_click` | Click an element (CSS selector) |
| `browser_type` | Type text into input element |
| `browser_select_option` | Select dropdown option |
| `browser_hover` | Hover over element |
| `browser_press_key` | Press keyboard key |
| `browser_screenshot` | Take screenshot (base64 PNG) |
| `browser_get_text` | Get text content from element |
| `browser_get_html` | Get HTML content from element |
| `browser_get_page_content` | Get full page text |
| `browser_snapshot` | Get accessibility tree snapshot |
| `browser_get_url` | Get current URL |
| `browser_get_title` | Get current page title |
| `browser_wait` | Wait for time or selector |
| `browser_evaluate` | Execute JavaScript in page |
| `browser_get_cookies` | Get all cookies |
| `browser_set_cookie` | Set a cookie |
| `browser_pdf` | Generate PDF of page |

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| None required | | Malory has no external dependencies |

## Usage

```bash
# Build
cd /mnt/storage/projects/Joshua26
docker compose -f mads/malory/docker-compose.yml build

# Start
docker compose -f mads/malory/docker-compose.yml up -d

# Test health
curl http://localhost:9222/health
```

## Registry

- **UID:** 2008
- **GID:** 2000 (joshua-services)
- **Port:** 9222
- **Host:** m5

## Recovery

Container is stateless. Restart to recover:

```bash
docker restart malory
```
