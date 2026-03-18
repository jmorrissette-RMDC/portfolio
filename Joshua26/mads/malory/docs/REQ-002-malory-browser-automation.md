# REQ-002: Malory Browser Automation

**Status:** Approved
**Date:** 2026-01-10
**Updated:** 2026-01-13
**Priority:** High (blocks Joshua testing)

## Overview

Malory provides headless browser automation capabilities via MCP, enabling Joshua to interact with web pages for testing and web scraping.

## Scope

Malory handles **headless browser automation** only:
- Playwright with Chromium headless
- Standard MCP tools
- Fast, containerized
- Suitable for sites without anti-bot measures

For **human-like browser automation** (physical desktop, kernel-level input, anti-bot evasion), see **REQ-016: Hymie Desktop Automation**.

## Specification

### Container Details

| Property | Value |
|----------|-------|
| Name | malory |
| UID | 2008 |
| GID | 2000 |
| Port | 9222 |
| Server | M5 |
| Base | ADR-045 template |

### Browser

- Playwright with Chromium only
- Headless mode
- Single browser instance (can have multiple pages)

### MCP Tools

#### Navigation

| Tool | Parameters | Description |
|------|------------|-------------|
| navigate | url | Go to URL |
| go_back | - | Browser back |
| go_forward | - | Browser forward |
| refresh | - | Reload page |

#### Interaction

| Tool | Parameters | Description |
|------|------------|-------------|
| click | selector | Click element |
| type | selector, text, submit? | Type text into element |
| select_option | selector, value | Select dropdown value |
| hover | selector | Hover over element |
| press_key | key | Press keyboard key |

#### Content

| Tool | Parameters | Description |
|------|------------|-------------|
| screenshot | selector?, full_page? | Capture image (base64) |
| get_text | selector | Extract text from element |
| get_html | selector | Get element's HTML |
| get_page_content | - | Full page text |
| snapshot | - | Accessibility tree |

#### State

| Tool | Parameters | Description |
|------|------------|-------------|
| get_url | - | Current URL |
| get_title | - | Page title |
| wait | time?, selector?, state? | Wait for condition |

#### Advanced

| Tool | Parameters | Description |
|------|------------|-------------|
| evaluate | script | Run JavaScript |
| get_cookies | - | Read all cookies |
| set_cookie | name, value, domain? | Set a cookie |
| pdf | path? | Generate PDF |

### Use Cases

1. **Testing Joshua UI** - Automated testing of Langflow interface
2. **Web scraping** - Extract data from websites
3. **Web automation** - Fill forms, navigate workflows

### Non-Goals

These are explicitly out of scope for Malory (see Hymie for human-like automation):

- Anti-bot evasion (use Hymie)
- Human-like timing (use Hymie)
- Multi-browser support (Firefox, WebKit)
- Multiple concurrent browser instances

## Dependencies

- mad-core-js (ADR-042)
- Playwright npm package

## References

- ADR-039: Radical Simplification
- ADR-045: MAD Template Standard
