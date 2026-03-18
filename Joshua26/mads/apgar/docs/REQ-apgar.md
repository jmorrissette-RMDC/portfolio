# REQ-apgar — Apgar Observability MAD

**Version:** 2.1
**Status:** Design Completed / Ready for Implementation
**Architecture:** State 1 (gateway + langgraph + backing services)
**Host:** m5
**MAD Group:** apgar (gateway) + apgar-langgraph + apgar-prometheus + apgar-loki + apgar-grafana + apgar-promtail-m5 + apgar-promtail-irina + apgar-promtail-hymie
**UID:** 2032 (All Apgar containers)
**GID:** 2001

---

## §1 Purpose

Apgar is the Joshua26 ecosystem observability MAD. It is a State 1 MAD (per HLD-MAD-container-composition): gateway, LangGraph runtime, and backing services. Evolving from its earlier minimal prototype (which scraped docker sockets and relied on in-memory polling), this design introduces a full, persistent telemetry pipeline (Metrics, Logs, and Visualization). 

Apgar's Imperator capabilities within `apgar-langgraph` transition from raw data gathering to intelligent analysis, utilizing standard querying languages (PromQL and LogQL) to synthesize ecosystem health for other MADs or operators.

**Problems solved:**
- Historical logs are lost when a container is restarted or moved.
- No standard metrics endpoints across MADs.
- `docker logs` parsing requires mounting `docker.sock` (violates security policies - EX-APGAR-001).
- Ecosystem needed centralized visualization (Grafana dashboards) instead of querying a JSON string.

---

## §2 Containers & Architecture

| Container | Type | Network(s) | Notes |
|-----------|------|-----------|-------|
| `apgar` | MCP gateway | `joshua-net` + `apgar-net` | Sole network boundary — MCP and Grafana UI proxy |
| `apgar-langgraph` | LangGraph | `apgar-net` only | Observability Query/Imperator |
| `apgar-prometheus`| Backing Service | `apgar-net` only | Time-series metrics DB |
| `apgar-loki` | Backing Service | `apgar-net` only | Persistent log DB |
| `apgar-grafana` | Backing Service | `apgar-net` only | Visualization UI |
| `apgar-promtail-m5` | Log Shipper | `apgar-net` only | M5: tails Docker logs, pushes to Loki |
| `apgar-promtail-irina` | Log Shipper | `apgar-net` only | Irina: tails Docker logs, pushes to Loki |
| `apgar-promtail-hymie` | Log Shipper | `apgar-net` only | Hymie: tails Docker logs, pushes to Loki |

**Network Invariants:**
- To maintain `apgar-net` isolation, Loki, Prometheus, Grafana, and Promtail do *not* sit on `joshua-net`; their ports are not mapped to the host.
- **Log Ingestion:** Promtail runs as separate containers per host (`apgar-promtail-m5`, `apgar-promtail-irina`, `apgar-promtail-hymie`). Each attaches to `apgar-net` (overlay), mounts `/var/lib/docker/containers` from its host, and pushes directly to `apgar-loki:3100`. No gateway proxy; all log traffic stays on `apgar-net`.
- **Grafana UI Access:** Human operator access to Grafana is proxied through the Apgar Gateway (e.g., `http://apgar:6341/ui`) which routes to `apgar-grafana:3000` on `apgar-net`, fully preserving the strict single-boundary network rule.

---

## §3 MCP Tools

Tool naming convention: `apgar_[action]`

### `apgar_query_logs` (AE Flow)
Queries the Loki database for historical container logs using LogQL.

**Schema:**
```json
{
  "input": {
    "type": "object",
    "properties": {
      "logql_query": { "type": "string", "description": "Valid LogQL query" },
      "start_time_iso": { "type": "string", "description": "ISO 8601 start time" },
      "end_time_iso": { "type": "string", "description": "ISO 8601 end time" },
      "limit": { "type": "integer", "default": 100 }
    },
    "required": ["logql_query", "start_time_iso", "end_time_iso"]
  },
  "output": {
    "type": "object",
    "properties": {
      "logs": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "timestamp": { "type": "string" },
            "message": { "type": "string" },
            "labels": { "type": "object" }
          }
        }
      }
    }
  },
  "errors": {
    "400": "Invalid LogQL query syntax or parameters",
    "500": "Failed to connect to Loki database"
  }
}
```

### `apgar_query_metrics` (AE Flow)
Queries the Prometheus database using PromQL to retrieve time-series metrics.

**Schema:**
```json
{
  "input": {
    "type": "object",
    "properties": {
      "promql_query": { "type": "string", "description": "Valid PromQL query" },
      "start_time_iso": { "type": "string", "description": "ISO 8601 start time" },
      "end_time_iso": { "type": "string", "description": "ISO 8601 end time" },
      "step": { "type": "string", "description": "Resolution step (e.g. '1m', '5s')" }
    },
    "required": ["promql_query", "start_time_iso", "end_time_iso", "step"]
  },
  "output": {
    "type": "object",
    "properties": {
      "metrics": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "metric": { "type": "object" },
            "values": { "type": "array", "items": { "type": "array" } }
          }
        }
      }
    }
  },
  "errors": {
    "400": "Invalid PromQL query syntax or parameters",
    "500": "Failed to connect to Prometheus database"
  }
}
```

### `apgar_diagnose_issue` (TE Flow)
A cognitive flow where `apgar-langgraph` autonomously analyzes an issue by generating PromQL and LogQL queries, executing them, and synthesizing a root-cause summary.

**Schema:**
```json
{
  "input": {
    "type": "object",
    "properties": {
      "issue_description": { "type": "string", "description": "Human-readable description of the problem" },
      "time_window_minutes": { "type": "integer", "description": "Lookback window in minutes" }
    },
    "required": ["issue_description", "time_window_minutes"]
  },
  "output": {
    "type": "object",
    "properties": {
      "diagnosis": { "type": "string", "description": "Synthesized root-cause analysis" },
      "queries_executed": { "type": "array", "items": { "type": "string" } }
    }
  },
  "errors": {
    "500": "Failed during query generation or synthesis",
    "503": "Dependencies (Loki/Prometheus/LLM) unavailable"
  }
}
```

---

## §4 Data Models & Storage

Since Apgar uses backing services (State 1 pattern), it requires persistent instance-specific storage per REQ-000 §3.4.

- **Prometheus Storage:** `/workspace/apgar/data/prometheus/`
- **Loki Storage:** `/workspace/apgar/data/loki/`
- **Grafana Storage:** `/workspace/apgar/data/grafana/`

---

## §5 LangGraph Flow Architecture

### 1. `query_logs_flow` (AE)
Deterministic execution to retrieve logs.
- Node: Validate `logql_query` syntax (basic checks).
- Node: Call `http://apgar-loki:3100/loki/api/v1/query_range`.
- Edge: Return structured JSON of logs or error message.

### 2. `query_metrics_flow` (AE)
Deterministic execution to retrieve metrics.
- Node: Call `http://apgar-prometheus:9090/api/v1/query`.
- Edge: Return structured JSON of time-series data.

### 3. `diagnose_issue_flow` (TE)
Cognitive analysis of system state.
- **Node: Planner** - Analyze `issue_description`, determine what PromQL and LogQL queries to run (e.g. "rogers memory extraction queue backing up" -> `sum(rate(rogers_queue_depth[5m]))`, `{mad_logical_actor="rogers"} |= "error"`).
- **Node: Query Execution** - Concurrently trigger `query_logs_flow` and `query_metrics_flow` via internal tool calls.
- **Node: Synthesis** - LLM reviews returned log chunks and metric trends, synthesizes a root-cause hypothesis and recommends actions.

---

## §6 Health Strategy

**Critical Dependencies (Hard Fail):**
- `apgar-loki` (If down, Apgar cannot observe logs)
- `apgar-prometheus` (If down, Apgar cannot observe metrics)

**Optional Dependencies (Graceful Degradation):**
- `apgar-grafana` (If down, UI is unavailable but programmatic querying via LangGraph still works)
- **LLM Provider:** The TE flow `apgar_diagnose_issue` uses Sutherland alias `agent-small` (Qwen2.5-7B). If Sutherland or the model is unavailable: return 503 with `{"error": "diagnosis_unavailable", "reason": "LLM dependency unreachable"}`; do not crash. AE tools (`apgar_query_logs`, `apgar_query_metrics`) continue to function. Gateway `/health` reports `diagnosis: degraded` when LLM is unreachable, `diagnosis: ok` otherwise.

---

## §7 Configuration Mappings

**`apgar/config.json` (Gateway):**
```json
{
  "name": "apgar",
  "tools": {
    "apgar_query_logs": {
      "target": "apgar-langgraph:8000",
      "endpoint": "/apgar_query_logs"
    },
    "apgar_query_metrics": {
      "target": "apgar-langgraph:8000",
      "endpoint": "/apgar_query_metrics"
    },
    "apgar_diagnose_issue": {
      "target": "apgar-langgraph:8000",
      "endpoint": "/apgar_diagnose_issue"
    }
  },
  "health": {
    "dependencies": {
      "prometheus": "http://apgar-prometheus:9090/-/healthy",
      "loki": "http://apgar-loki:3100/ready"
    }
  }
}
```

**`apgar-langgraph/config.json`:**
```json
{
  "loki_url": "http://apgar-loki:3100",
  "prometheus_url": "http://apgar-prometheus:9090",
  "te_flow_model": "agent-small"
}
```

The TE flow `apgar_diagnose_issue` uses Sutherland alias `agent-small` (Qwen2.5-7B) for planning and synthesis. All LLM calls go through Sutherland.

---

## §8 Promtail (Log Shipper)

**Choice:** Promtail — purpose-built for Loki, native Docker container label support.

**Deployment:** One container per Docker host with distinct names: `apgar-promtail-m5`, `apgar-promtail-irina`, `apgar-promtail-hymie`. Deployed via host-specific compose overrides (`docker-compose.m5.yml`, `docker-compose.irina.yml`, `docker-compose.hymie.yml`). No bare-metal installs. Each attaches to `apgar-net` (overlay). Binds `/var/lib/docker/containers` from its host read-only to tail the json-file logs.

**Configuration:**
- **Push URL:** `http://apgar-loki:3100/loki/api/v1/push` — direct to Loki on `apgar-net`. No gateway proxy.
- **Ports:** Promtail does not expose ports; it is a push client only.
- **Labels:** Attach `mad.logical_actor`, `container_name`, `host` from Docker labels to each log stream for LogQL filtering.

**Implementation:** Use official Grafana Promtail image. Config via bind-mounted file or env. Document exact compose entry and config in Implementation Phase.

---

## §9 Metrics Collection

**Constraint:** Joshua-net carries MCP traffic only. Prometheus runs on `apgar-net` and cannot reach MAD gateways on `joshua-net` directly.

**Approach:**
- Every MAD exposes a metrics MCP tool (e.g. `metrics_get`) that returns Prometheus exposition format.
- Apgar scraper runs on `apgar-net` and calls the gateway's peer proxy: `POST /peer/{mad}/metrics_get`.
- Gateway crosses to `joshua-net`, invokes the peer's MCP tool, returns metrics to scraper.
- Scraper aggregates (with `instance` labels per MAD), exposes `/metrics` for Prometheus to scrape.
- Apgar's own gateway metrics: scraped directly (`apgar:6341/metrics`) since gateway is on `apgar-net`.

**Scraper location:** Gateway (scheduled job + route) or separate `apgar-metrics-scraper` container on `apgar-net`. Requires `apgar/config.json` peers section for sutherland, rogers, henson, etc.

---

## §10 Configuration Defaults

**Image versions (pin in docker-compose):**

| Container | Image | Notes |
|-----------|-------|-------|
| Prometheus | `prom/prometheus:v2.47.0` | Or current stable |
| Loki | `grafana/loki:2.9.2` | Or current stable |
| Grafana | `grafana/grafana:10.2.0` | Or current stable |
| Promtail | `grafana/promtail:2.9.2` | Or current stable |

**Retention:** Prometheus 15d, Loki 30d. Configurable via environment or config file. Document in Implementation Phase.

**Credentials:** No auth between MADs. Metrics collection, log shipping, and internal Apgar traffic use no credentials.

**Grafana provisioning:** Provision Loki and Prometheus as datasources on first run. No default dashboards in initial scope.