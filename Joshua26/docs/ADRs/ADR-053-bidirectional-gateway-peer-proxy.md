# ADR-053: Bidirectional Gateway as Network Boundary with Peer Proxy

**Status:** Accepted
**Date:** 2026-02-20
**Deciders:** System Architect
**Related:** ADR-046 (Graceful Degradation / MAD Groups), ADR-051 (MCP Gateway Library Pattern), REQ-000 §7.4.1

---

## Context

ADR-046 established the per-MAD private network pattern: each MAD group has a private bridge network (`[mad]-net`) for internal containers, and only the MCP gateway joins both `[mad]-net` and `joshua-net`. LangGraph containers and backing services are `[mad]-net` only.

This pattern provides strong isolation. However, as the ecosystem matures, some MADs require their LangGraph container to call tools on peer MADs. For example:

- **Rogers** needs Hamilton (embeddings, `irina:6335`) and Sutherland (LLM, `m5:11435`) from within `rogers-langgraph`'s ingest flow
- Both peers are reachable only via `joshua-net` overlay DNS — their container names resolve only on `joshua-net`
- `rogers-langgraph` connects to `rogers-net` only and cannot resolve `hamilton` or `sutherland`

This creates a gap: the isolation invariant prevents direct access, but the programmatic logic requires it.

---

## Decision

Extend the MCP gateway to serve as the **bidirectional network boundary** for all cross-network traffic — both inbound and outbound.

### Two HTTP endpoints on every gateway

**`POST /mcp`** — Standard MCP endpoint (session and sessionless)
- **With `?sessionId`:** Routes to an existing SSE session (existing behaviour).
- **Without `?sessionId`:** Sessionless mode — processes `tools/call` synchronously and returns the JSON-RPC 2.0 response directly in the HTTP response body. No SSE session required.
- Body: `{"jsonrpc":"2.0","method":"tools/call","params":{"name":"...","arguments":{...}},"id":"..."}`
- Returns: `{"jsonrpc":"2.0","result":{"content":[...]},"id":"..."}` on success
- Peer gateways are plain MCP clients — they use `POST /mcp` like any other MCP consumer. No special endpoint is needed on the receiving side.

**`POST /peer/{peer-name}/{tool-name}`** — Proxy to peer MAD *(inbound from langgraph only)*
- Looks up `peer-name` in `config.peers`; returns 404 if not declared
- Parses request body as params
- Calls `router.callMCP(toolName, params, "{peer.host}:{peer.port}", requestId)`
- `callMCP()` sends a proper MCP `tools/call` JSON-RPC 2.0 request to `POST /mcp` on the peer (sessionless)
- Returns peer's unwrapped result on success, 502 on peer error
- Logging: structured entry at INFO level with `peer`, `tool`, `request_id`

### Peer declaration in `config.json`

```json
{
  "peers": {
    "hamilton": { "host": "hamilton", "port": 6335 },
    "sutherland": { "host": "sutherland", "port": 11435 }
  }
}
```

- `host`: Container DNS name on `joshua-net`
- `port`: Peer's MCP gateway port (from `registry.yml`)
- Validation: if present, must be object; each entry requires `host` (string) and `port` (integer 1-65535)
- Template config.json includes `"peers": {}` as a documented extension point

### No new npm packages

- No new npm packages — routing-lib gains a `callMCP()` method that reuses the existing `_doRequest()` / `withRetry()` infrastructure
- `callMCP()` sends proper MCP JSON-RPC 2.0 body to `POST /mcp` and unwraps the content result; it is the only method used for gateway-to-gateway calls

### Call chain

```
rogers-langgraph
  → POST http://rogers:6380/peer/hamilton/embed_text  {"text": "hello"}

rogers gateway  (_handlePeerCall)
  → router.callMCP("embed_text", {"text":"hello"}, "hamilton:6335", uuid)
  → POST http://hamilton:6335/mcp
     {"jsonrpc":"2.0","method":"tools/call",
      "params":{"name":"embed_text","arguments":{"text":"hello"}},"id":uuid}

hamilton gateway  (_handlePostMessage — sessionless)
  → router.forward("embed_text", {"text":"hello"}, "hamilton-langgraph:8000", "/embed_text", uuid)
  → POST http://hamilton-langgraph:8000/embed_text  {"tool":"embed_text","params":{"text":"hello"}}

hamilton-langgraph
  → processes embedding, returns result
  ← {"embedding": [...]}
← {"jsonrpc":"2.0","result":{"content":[{"type":"text","text":"[...]"}]},"id":uuid}
← unwrapped: {"embedding": [...]}
```

All traffic on `joshua-net` between gateways is standard MCP JSON-RPC 2.0 via `POST /mcp`. Plain HTTP is used only on private `[mad]-net` segments (gateway → langgraph backend), which is internal and acceptable.

---

## Invariant

**LangGraph containers and backing services must never be added to `joshua-net`. No exceptions.**

This invariant is absolute. The bidirectional gateway pattern exists precisely so this invariant never needs to be broken. Any future use case that appears to require adding a langgraph container to joshua-net must instead be solved by routing through the gateway's `/peer` endpoint.

---

## Consequences

### Positive

- The isolation invariant holds completely — no langgraph container ever joins joshua-net
- The gateway's role expands coherently: "sole network boundary" now means both directions
- No langgraph containers need special network treatment — uniform pattern across all MADs
- All inter-MAD traffic on `joshua-net` is standard MCP JSON-RPC 2.0 via `POST /mcp` — no custom endpoints, protocol invariant fully preserved
- Peer gateways are plain MCP clients — consistent with how all other MCP consumers work
- Uses existing routing-lib infrastructure — no new retry/pool logic needed
- Pattern scales: any future peer calls follow the same config + endpoint pattern

### Negative

- Each outbound peer call adds one hop (langgraph → gateway → peer gateway → peer langgraph)
- The gateway must declare peers explicitly — cannot call arbitrary MADs on the fly
- Gateway restart required if peers section changes (config parsed at startup)

### Neutral

- MADs whose langgraph containers make no peer calls are unaffected (empty `peers: {}` in config)

---

## Alternatives Considered

**Option A: Add langgraph to joshua-net when needed**
- Rejected: Breaks the isolation invariant. Once any langgraph container joins joshua-net, the invariant weakens and future deviations follow. Security and clarity of the two-network pattern depends on the invariant being absolute.

**Option B: Custom stateless endpoint (`/mcp/rpc`) on receiving gateway**
- Rejected: Unnecessary. `POST /mcp` without `?sessionId` already means sessionless — the standard MCP streamable HTTP transport. There is no difference between peer gateways and any other MCP client; creating a custom endpoint implies a difference that does not exist. The gateway's `_handlePostMessage()` handles the sessionless case directly.

**Option C: Sidecar proxy container on both networks**
- Rejected: Adds deployment complexity (extra container per MAD), violates the principle of minimal containers, and solves the same problem the gateway already solves.

---

## Implementation

Changes to the following files:

| File | Change |
|---|---|
| `lib/mcp-protocol-lib/lib/server.js` | `_handlePostMessage()` extended to handle sessionless mode (no `?sessionId`); `/peer/{peer}/{tool}` uses `router.callMCP()`; removed custom `/mcp/rpc` and `/tool/{name}` endpoints |
| `lib/routing-lib/lib/router.js` | Add `callMCP()` — sends MCP JSON-RPC 2.0 `tools/call` to `POST /mcp` on peer, unwraps content result |
| `lib/routing-lib/tests/router.test.js` | Tests for `callMCP()` including path assertion (`/mcp`) |
| `lib/mcp-protocol-lib/lib/gateway.js` | Pass `config.peers ?? {}` to MCPServer |
| `lib/mcp-protocol-lib/lib/validator.js` | Optional `peers` validation |
| `mads/_template/template/config.json` | Add `"peers": {}` extension point |
| `mads/_template/template-langgraph/server.py` | Commented peer call example |
| `mads/_template/README.md` | "Calling Peer MADs from LangGraph" section |
| `mads/_template/docs/REQ-langgraph-template.md` | §12 Peer Proxy Pattern |
| `docs/designs/HLD-MAD-container-composition.md` | Updated Network Architecture section |
| `docs/requirements/REQ-000-Joshua26-System-Requirements-Specification.md` | §4.2, §7.4.1 updates |
