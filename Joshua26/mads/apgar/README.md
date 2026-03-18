# Apgar — Ecosystem Observability MAD

**UID:** 2032 | **Port:** 6341 | **Host:** m5

Apgar is the Joshua26 ecosystem observability MAD. It aggregates metrics (Prometheus), logs (Loki), and provides agentic diagnosis via `apgar_diagnose_issue`. Grafana UI is proxied through the gateway.

## MCP Tools

| Tool | Description |
|------|-------------|
| `apgar_query_logs` | Query Loki for container logs using LogQL |
| `apgar_query_metrics` | Query Prometheus for time-series metrics using PromQL |
| `apgar_diagnose_issue` | Agentic diagnosis: LLM generates queries, executes them, synthesizes root-cause |

## Containers

| Container | Role | Network |
|-----------|------|---------|
| `apgar` | MCP gateway | `joshua-net` + `apgar-net` |
| `apgar-langgraph` | Query/Imperator | `apgar-net` only |
| `apgar-prometheus` | Time-series metrics | `apgar-net` only |
| `apgar-loki` | Log storage | `apgar-net` only |
| `apgar-grafana` | Visualization UI | `apgar-net` only |

## Deploy

```bash
# Create workspace dirs (once)
mkdir -p /workspace/apgar/data/{prometheus,loki,grafana}
chown -R 2032:2001 /workspace/apgar

docker compose -f docker-compose.yml -f docker-compose.m5.yml up -d --build apgar apgar-langgraph apgar-prometheus apgar-loki apgar-grafana
```

## Verify

```bash
# Health
curl -s http://localhost:6341/health

# Query logs (requires Loki to have data)
curl -s -X POST http://localhost:6341/mcp -H "Content-Type: application/json" -d '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"apgar_query_logs","arguments":{"logql_query":"{}","start_time_iso":"2026-01-01T00:00:00Z","end_time_iso":"2026-01-02T00:00:00Z"}},"id":"1"}'

# Grafana UI (proxied)
# Open http://<host>:6341/ in browser — proxied to Grafana
```

## See Also

- [`docs/REQ-apgar.md`](docs/REQ-apgar.md) — full delta REQ
