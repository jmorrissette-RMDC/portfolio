# High-Level Design: Unified Package Caching Architecture

**Version:** 4.0
**Date:** 2026-03-09
**Status:** Deployed — Gate 3 closed 2026-03-09
**Related Documents:** HLD-software-factory-core.md, ADR-037, ADR-038, REQ-alexandria.md (REQ-018-delphi-pypi-mirror.md, REQ-019-pergamum-npm-mirror.md, REQ-022-nineveh-docker-registry.md are historical proposals superseded by REQ-alexandria.md)

---

## Executive Summary

The Unified Package Caching Architecture implements a "Supply Chain Wall" via the **Alexandria pMAD** — a full State 2 pMAD on Irina with three backing services: **alexandria-devpi** (PyPI/Devpi), **alexandria-verdaccio** (NPM/Verdaccio), and **alexandria-registry** (Docker Registry 2.0).

Alexandria is a full State 2 pMAD: nginx gateway on `joshua-net`, LangGraph container with Imperator, Prometheus metrics, and MCP tools for cache management.

**Key constraint:** pip/npm/docker traffic is not MCP and cannot traverse `joshua-net`. The Alexandria nginx gateway serves **MCP traffic only** on port 9229. Cache ports 3141/4873/5000 are exposed **directly by the backing service containers** to the host — nginx does not proxy them. See EX-ALEXANDRIA-001 and the Network Model in REQ-alexandria.md.

**Scope:** PyPI package caching, NPM package caching, Docker image storage.

**Out of scope:**
- **HuggingFace / ML model caching** — owned by **Sutherland**. `HF_ENDPOINT` is never pointed at Alexandria.
- APT package caching — not in scope.

**Key Capabilities:**
- Transparent proxying for PyPI (`pip install`) via `alexandria-devpi` at `http://irina:3141`
- Transparent proxying for NPM (`npm install`) via `alexandria-verdaccio` at `http://irina:4873`
- Docker image storage and distribution via `alexandria-registry` at `irina:5000`
- MCP tools for cache management and status (`alex_*` tools) via nginx gateway on port 9229
- Centralized storage on Irina (`/storage/packages/`, `/storage/images/`)

## Problem Statement

### Current State (ADR-037/038)

The existing local package caching pattern requires:

1. **Manual cache management**: Agents must run `pip download -d packages/` before builds
2. **Per-project duplication**: Each project maintains its own `packages/` folder
3. **Cognitive overhead**: Agents must "remember" the caching workflow
4. **Storage waste**: Common packages (numpy, react, etc.) duplicated across projects

### Example: Current Workflow

```bash
# Agent must know to do this:
pip download -q -r requirements.txt -d packages/

# Then in Dockerfile:
COPY packages/ /tmp/packages/
RUN pip install --find-links=/tmp/packages/ -r requirements.txt
```

### Desired State

```bash
# Agent just runs:
pip install -r requirements.txt

# Proxy handles caching transparently
```

### The Proxy Caching Pattern

alexandria-devpi and alexandria-verdaccio implement the same transparent proxy pattern:

| Aspect | ADR-037 (Local Folder) | Network Proxy (After) |
|--------|------------------------|---------------------------|
| Agent knowledge required | High | None |
| Deduplication | Per-project | Global |
| First-time setup | Manual download step | Automatic |
| Offline builds | Yes (after manual prep) | Yes (after first fetch) |

---

## Architecture Overview

### The Supply Chain Wall

```
Ã¢â€Å’Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€Â
Ã¢â€â€š                              INTERNET                                    Ã¢â€â€š
Ã¢â€â€š              Ã¢â€Å’Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€Â                 Ã¢â€Å’Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€Â                        Ã¢â€â€š
Ã¢â€â€š              Ã¢â€â€š PyPI  Ã¢â€â€š                 Ã¢â€â€š  NPM  Ã¢â€â€š                        Ã¢â€â€š
Ã¢â€â€š              Ã¢â€â€š .org  Ã¢â€â€š                 Ã¢â€â€šjs.com Ã¢â€â€š                        Ã¢â€â€š
Ã¢â€â€š              Ã¢â€â€Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€Â¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€Ëœ                 Ã¢â€â€Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€Â¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€Ëœ                        Ã¢â€â€š
Ã¢â€â€Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€Â¼Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€Â¼Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€Ëœ
                   Ã¢â€â€š                         Ã¢â€â€š
                   Ã¢â€â€š First fetch only         Ã¢â€â€š
                   Ã¢â€“Â¼                         Ã¢â€“Â¼
Ã¢â€Å’Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€Â
Ã¢â€â€š                         IRINA (Storage Server)                           Ã¢â€â€š
Ã¢â€â€š                                                                          Ã¢â€â€š
Ã¢â€â€š  Ã¢â€Å’Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€Â  Ã¢â€â€š
Ã¢â€â€š  Ã¢â€â€š               ALEXANDRIA (Package Cache pMAD Group)                Ã¢â€â€š  Ã¢â€â€š
Ã¢â€â€š  Ã¢â€â€š               Scope: PyPI + NPM + Docker imagesÃ¢â€â€š  Ã¢â€â€š
Ã¢â€â€š  Ã¢â€â€š                                                                   Ã¢â€â€š  Ã¢â€â€š
Ã¢â€â€š  Ã¢â€â€š  Ã¢â€Å’Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€Â    Ã¢â€Å’Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€Â            Ã¢â€â€š  Ã¢â€â€š
Ã¢â€â€š  Ã¢â€â€š  Ã¢â€â€š  alexandria-devpi    Ã¢â€â€š    Ã¢â€â€š  alexandria-verdaccioÃ¢â€â€š            Ã¢â€â€š  Ã¢â€â€š
Ã¢â€â€š  Ã¢â€â€š  Ã¢â€â€š  (PyPI cache)        Ã¢â€â€š    Ã¢â€â€š  (NPM cache)          Ã¢â€â€š            Ã¢â€â€š  Ã¢â€â€š
Ã¢â€â€š  Ã¢â€â€š  Ã¢â€â€š  Devpi  :3141        Ã¢â€â€š    Ã¢â€â€š  Verdaccio  :4873     Ã¢â€â€š            Ã¢â€â€š  Ã¢â€â€š
Ã¢â€â€š  Ã¢â€â€š  Ã¢â€â€Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€Â¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€Ëœ    Ã¢â€â€Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€Â¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€Ëœ            Ã¢â€â€š  Ã¢â€â€š
Ã¢â€â€š  Ã¢â€â€Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€Â¼Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€Â¼Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€Ëœ  Ã¢â€â€š
Ã¢â€â€š                Ã¢â€“Â¼                            Ã¢â€“Â¼                            Ã¢â€â€š
Ã¢â€â€š  Ã¢â€Å’Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€Â   Ã¢â€â€š
Ã¢â€â€š  Ã¢â€â€š                    /mnt/storage/packages/                        Ã¢â€â€š   Ã¢â€â€š
Ã¢â€â€š  Ã¢â€â€š      Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ pypi/              # Python wheels & sdists            Ã¢â€â€š   Ã¢â€â€š
Ã¢â€â€š  Ã¢â€â€š      Ã¢â€â€Ã¢â€â‚¬Ã¢â€â‚¬ npm/               # NPM tarballs                      Ã¢â€â€š   Ã¢â€â€š
Ã¢â€â€š  Ã¢â€â€Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€Ëœ   Ã¢â€â€š
Ã¢â€â€Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€Ëœ
             Ã¢â€â€š LAN Speed                   Ã¢â€â€š LAN Speed
             Ã¢â€â€š (~1 GB/s)                   Ã¢â€â€š (~1 GB/s)
             Ã¢â€“Â¼                             Ã¢â€“Â¼
Ã¢â€Å’Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€Â
Ã¢â€â€š                         AGENT / BUILD CONTAINERS                         Ã¢â€â€š
Ã¢â€â€š                                                                          Ã¢â€â€š
Ã¢â€â€š  Environment Variables (set in base images):                            Ã¢â€â€š
Ã¢â€â€š  Ã¢â€Å’Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€Â   Ã¢â€â€š
Ã¢â€â€š  Ã¢â€â€š PIP_INDEX_URL=http://irina:3141/root/pypi/+simple/             Ã¢â€â€š   Ã¢â€â€š
Ã¢â€â€š  Ã¢â€â€š NPM_CONFIG_REGISTRY=http://irina:4873                         Ã¢â€â€š   Ã¢â€â€š
Ã¢â€â€š  Ã¢â€â€š                                                                  Ã¢â€â€š   Ã¢â€â€š
Ã¢â€â€š  Ã¢â€â€š # HF_ENDPOINT is NOT set here.                                   Ã¢â€â€š   Ã¢â€â€š
Ã¢â€â€š  Ã¢â€â€š # HuggingFace / ML model caching is owned by Sutherland.        Ã¢â€â€š   Ã¢â€â€š
Ã¢â€â€š  Ã¢â€â€Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€Ëœ   Ã¢â€â€š
Ã¢â€â€š                                                                          Ã¢â€â€š
Ã¢â€â€š  Agents run standard commands - proxies handle caching transparently:   Ã¢â€â€š
Ã¢â€â€š  Ã¢â‚¬Â¢ pip install pandas        Ã¢â€ â€™ alexandria-devpi serves (caches on miss)          Ã¢â€â€š
Ã¢â€â€š  Ã¢â‚¬Â¢ npm install express       Ã¢â€ â€™ alexandria-verdaccio serves (caches on miss)        Ã¢â€â€š
Ã¢â€â€Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€Ëœ
```

**HuggingFace model caching:** Owned by Sutherland. All ML model downloads, storage, and serving are managed within Sutherland's own infrastructure. The `HF_ENDPOINT` env var, if used, points at a Sutherland endpoint Ã¢â‚¬â€ never at Alexandria.

### Data Flow

**First-time package install (cache miss):**
1. Agent runs `pip install pandas`
2. pip contacts `alexandria-devpi` at `http://irina:3141/root/pypi/+simple/`
3. `alexandria-devpi` checks local cache — miss
4. `alexandria-devpi` fetches from PyPI.org, saves to `/storage/packages/pypi/`
5. `alexandria-devpi` serves package to agent
6. Agent installs package

**Subsequent installs (cache hit):**
1. Agent runs `pip install pandas`
2. pip contacts `alexandria-devpi`
3. Cache hit — served instantly from local storage
4. No internet access required

---

## Component Design

### `alexandria-devpi` (PyPI Cache)

**Purpose:** Transparent caching proxy for Python packages

**Technology:** Devpi-Server v6

**Why Devpi:**
- Battle-tested in enterprise environments
- Supports both caching (mirror) and private packages
- Preserves pip compatibility completely
- Handles wheels, sdists, and metadata

**Container Identity:**
- Container name: `alexandria-devpi`
- UID: 2017 (alexandria-devpi)
- GID: 2001 (administrators)

**Configuration:**
```ini
[server]
host = 0.0.0.0
port = 3141
serverdir = /storage/packages/pypi

[mirror]
url = https://pypi.org/simple/
cache_expiry = 86400
```

**Volumes:**
- `storage:/storage` - Package cache at `/storage/packages/pypi`
- `workspace:/workspace` - Runtime config at `/workspace/alexandria-devpi`

**Network:**
- Container is on `alexandria-net` only — NOT on `joshua-net`
- Port 3141 is **host-bound directly** (EX-ALEXANDRIA-001) — clients connect via `irina:3141`
- Not accessible by container DNS from other networks

**Client Configuration:**
```bash
# Environment variable (preferred)
PIP_INDEX_URL=http://irina:3141/root/pypi/+simple/

# Or pip.conf
[global]
index-url = http://irina:3141/root/pypi/+simple/
trusted-host = irina
```

---

### `alexandria-verdaccio` (NPM Cache)

**Purpose:** Transparent caching proxy for Node.js packages

**Technology:** Verdaccio 5.31.1

**Why Verdaccio:**
- Most popular self-hosted npm registry
- Zero-config caching mode
- Full npm/yarn/pnpm compatibility
- Lightweight (~50MB container)

**Container Identity:**
- Container name: `alexandria-verdaccio`
- Image: official `verdaccio/verdaccio:5.31.1` — runs as UID 10001 (verdaccio internal user). EX-ALEXANDRIA-002.

**Configuration:**
```yaml
storage: /storage/packages/npm
uplinks:
  npmjs:
    url: https://registry.npmjs.org/
    cache: true
packages:
  '@*/*':
    access: $all
    proxy: npmjs
  '**':
    access: $all
    proxy: npmjs
```

**Volumes:**
- `storage:/storage` - Package cache at `/storage/packages/npm`
- `workspace:/workspace` - Runtime config at `/workspace/alexandria-verdaccio`

**Network:**
- Container is on `alexandria-net` only — NOT on `joshua-net`
- Port 4873 is **host-bound directly** (EX-ALEXANDRIA-001) — clients connect via `irina:4873`
- Not accessible by container DNS from other networks

**Client Configuration:**
```bash
# Environment variable (preferred)
NPM_CONFIG_REGISTRY=http://irina:4873

# Or .npmrc
registry=http://irina:4873
```

---

### `alexandria-registry` (Docker Registry)

**Purpose:** Local Docker image storage and distribution

**Technology:** Docker Registry 2.0 (registry:2.8.3)

**Why local registry:**
- Eliminates re-pulls of large images from Docker Hub on every host
- Supports private images that cannot go to public registries
- Controlled versioning of ecosystem images

**Container Identity:**
- Container name: `alexandria-registry`
- Image: official `registry:2.8.3` — runs as root. EX-ALEXANDRIA-003.

**Volumes:**
- `storage:/storage` - Image data at `/storage/images/alexandria-registry`

**Network:**
- Container is on `alexandria-net` only — NOT on `joshua-net`
- Port 5000 is **host-bound directly** (EX-ALEXANDRIA-001) — clients connect via `irina:5000`

**Client Configuration:**
```json
// /etc/docker/daemon.json on all hosts (irina, m5, hymie)
{
  "insecure-registries": ["irina:5000"]
}
```
```bash
# Push an image
docker tag myimage:latest irina:5000/myimage:latest
docker push irina:5000/myimage:latest

# Pull an image
docker pull irina:5000/myimage:latest
```

---

### HuggingFace / ML Model Caching (Not Alexandria)

HuggingFace model caching is **not** part of the Alexandria pMAD. All model caching is owned by **Sutherland**. See `HLD-conversational-core.md` Ã‚Â§6 and `mads/sutherland/` for the Sutherland model storage design. The `HF_ENDPOINT` env var is configured in Sutherland's own compose file and base images, never in Alexandria's.

---

## Storage Layout

### Irina Storage Server

```
/mnt/storage/
├── models/                          # Owned by Sutherland (NOT Alexandria)
│   └── sutherland/                  # HuggingFace models, GGUFs, etc.
│
├── packages/                        # Owned by Alexandria (devpi + verdaccio)
│   ├── pypi/                        # alexandria-devpi storage
│   │   ├── +files/                  # Package files
│   │   ├── root/
│   │   │   └── pypi/                # Mirror index
│   │   └── .serverstate/            # Devpi metadata
│   │
│   └── npm/                         # alexandria-verdaccio storage
│       ├── @modelcontextprotocol/
│       ├── express/
│       ├── react/
│       └── .verdaccio-db.json       # Verdaccio metadata
│
└── images/
    └── alexandria-registry/         # alexandria-registry storage
        └── docker/registry/v2/      # Registry blob store
```

### Size Estimates

| Cache | Container | Typical Size | Growth Rate |
|-------|-----------|--------------|-------------|
| PyPI (Devpi) | `alexandria-devpi` | 20-50GB | Moderate (new deps) |
| NPM (Verdaccio) | `alexandria-verdaccio` | 10-30GB | Moderate (new deps) |
| Docker (Registry 2.0) | `alexandria-registry` | 50-200GB | High (base images) |

---

## Base Image Configuration

All base images must set the following environment variables to route package installs through Alexandria automatically:

| Base Image Type | Required Environment Variables |
|----------------|-------------------------------|
| Python | `PIP_INDEX_URL=http://irina:3141/root/pypi/+simple/` and `PIP_TRUSTED_HOST=irina` |
| Node.js | `NPM_CONFIG_REGISTRY=http://irina:4873` |
| Hybrid (Python + Node.js) | Both of the above |

**HuggingFace:** `HF_ENDPOINT` is **never** set in base images. HuggingFace model caching is owned by Sutherland. Any container needing HF access configures its own Sutherland endpoint.

---

## Migration from ADR-037/038

### Phase 1: Deploy Infrastructure

**Status: COMPLETE (deployed 2026-03-09).**

1. alexandria-devpi container deployed with Devpi
2. alexandria-verdaccio container deployed with Verdaccio
3. Both proxies verified functional
4. Cache ports host-bound directly from backing service containers (3141, 4873) — NOT proxied through nginx

### Phase 2: Update Base Images

**Status: COMPLETE (2026-03-09).**

1. `PIP_INDEX_URL=http://irina:3141/root/pypi/+simple/` and `NPM_CONFIG_REGISTRY=http://irina:4873` set on base images and in Docker daemons (irina, m5, hymie via SIGHUP)
2. Docker daemon `insecure-registries: ["irina:5000"]` configured on all hosts

### Phase 3: Validate

**Status: COMPLETE (2026-03-09).** Alexandria deployed and all 5 containers healthy. PyPI/NPM/Docker proxies verified working.

1. starret-langgraph built using devpi — packages download through proxies confirmed
2. Cache hits verified on rebuild

### Phase 4: Cleanup

**Status: IN PROGRESS.**

1. Remove `packages/` directories from repositories — **started**: `mads/starret/starret-langgraph/packages/` removed 2026-03-09. Remaining: `mads/alexandria/alexandria-langgraph/packages/` (bootstrap — pending). Other pMADs as built.
2. Update ADR-037/038 status to "Superseded" — pending
3. Create new ADR referencing this HLD — pending

### Rollback Plan

If issues arise, agents can bypass proxies by unsetting environment variables:
```bash
unset PIP_INDEX_URL
unset NPM_CONFIG_REGISTRY
```

---

## Comparison: Before and After

| Aspect | ADR-037 (Before) | Unified Caching (After) |
|--------|------------------|-------------------------|
| Agent workflow | `pip download` then `pip install` | Just `pip install` |
| Storage location | Per-project `packages/` folder | Centralized `/storage/packages/` |
| Deduplication | None (per-project copies) | Global (single copy) |
| Disk usage (10 projects) | 10x package size | 1x package size |
| Dockerfile complexity | COPY packages, --find-links | Standard pip install |
| New dependency workflow | Download, commit, rebuild | Just add to requirements.txt |
| Offline builds | Yes (after manual prep) | Yes (after first fetch) |
| Agent knowledge required | Must know caching pattern | None |

---

## Service Summary

| Container | Purpose | Software | Host Port | Storage Path | Client Config |
|-----------|---------|----------|-----------|--------------|---------------|
| `alexandria-devpi` | Python packages | Devpi v6 | 3141 | /storage/packages/pypi | `PIP_INDEX_URL=http://irina:3141/root/pypi/+simple/` |
| `alexandria-verdaccio` | NPM packages | Verdaccio 5.31.1 | 4873 | /storage/packages/npm | `NPM_CONFIG_REGISTRY=http://irina:4873` |
| `alexandria-registry` | Docker images | Registry 2.8.3 | 5000 | /storage/images/alexandria-registry | `insecure-registries: ["irina:5000"]` in daemon.json |
| `alexandria-langgraph` | LangGraph + Imperator + MCP | Python 3.12 | — (alexandria-net) | — | MCP via `alexandria` nginx on port 9229 |
| `alexandria` | nginx MCP gateway | nginx 1.27.4-alpine | 9229 | — | `http://irina:9229/mcp` |

**HuggingFace model caching** is owned by Sutherland. `HF_ENDPOINT` is a Sutherland concern, not Alexandria's.

---

## Future Enhancements

1. **Cache analytics**: Track most-used packages for pre-warming
2. **Storage quotas**: LRU eviction when cache limits reached
3. **Private packages**: Host internal packages alongside cached public ones
4. **Replication**: Mirror caches to secondary storage for redundancy

---

**Document Version:** 4.0
**Last Updated:** 2026-03-09
**Status:** Deployed — Gate 3 closed 2026-03-09. All 5 containers healthy on irina.
