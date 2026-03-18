# TEST PLAN: Apgar

**MAD Group:** apgar **Version:** 2.1 **Date:** 2026-03-01

---

## 1. Environment Setup

- [ ] Apgar MAD group is deployed on m5 (192.168.1.120)
- [ ] All Apgar containers are running: `docker ps --filter "label=mad.logical_actor=apgar"` (apgar, apgar-langgraph, apgar-prometheus, apgar-loki, apgar-grafana, apgar-metrics-scraper)
- [ ] Malory is running on m5 (port 9222) for UI tests
- [ ] Run from Windows: `py -3.12 scripts/deployment/verify_apgar.py` (SSH to m5) or on m5: `python3 mads/apgar/tests/test_apgar_ui.py`

---

## 2. Tier 1: Interface & Contract Tests

### Gateway health

- **Test 1.1:** `GET http://apgar:6341/health` (or localhost:6341 from m5) returns 200 and `{"status":"healthy",...}`

### Tool: `apgar_query_logs`

- **Test 1.2 (Happy path):** MCP `tools/call` with `logql_query`, `start_time_iso`, `end_time_iso`, `limit`. Expected: `{"logs": [...]}` (may be empty if no Promtail yet); no `error` in result.
- **Test 1.3 (Error):** Missing required `logql_query`. Expected: JSON-RPC error or 4xx.

### Tool: `apgar_query_metrics`

- **Test 1.4 (Happy path):** MCP `tools/call` with `promql_query`, `start_time_iso`, `end_time_iso`, `step`. Expected: `{"metrics": [...]}`; no `error` in result.
- **Test 1.5 (Error):** Missing required parameter. Expected: JSON-RPC error or 4xx.

### Tool: `apgar_diagnose_issue`

- **Test 1.6 (Smoke):** MCP `tools/call` with `issue_description`, `time_window_minutes`. Expected: result with `diagnosis` text or JSON-RPC error if Sutherland unavailable; may SKIP on timeout.

### Metrics pipeline

- **Test 1.7:** `GET http://apgar-metrics-scraper:9091/metrics` (from m5) returns 200 and Prometheus exposition text (at least one metric or `# source:` line).
- **Test 1.8:** `GET http://apgar:6341/metrics` returns 200 and Prometheus text (e.g. `mcp_gateway_up`).

### Grafana UI proxy

- **Test 1.9:** `GET http://apgar:6341/` returns 200 or 302 with Grafana HTML or redirect to login.

---

## 3. Tier 2: Integration & State Verification Tests

- **Test 2.1:** After `apgar_query_logs`, Loki has received data (optional: query Loki API or rely on tool result).
- **Test 2.2:** After scraper has run, Prometheus has scraped the scraper target (e.g. query `up{job="apgar-scraper"}` via Prometheus API or apgar_query_metrics).

---

## 4. UI Tests (Malory — Grafana)

- **Test 4.1:** Malory `browser_navigate` to `http://apgar:6341/`; page loads.
- **Test 4.2:** `get_title` or `get_page_content` contains "Grafana" or "Welcome" or login form.
- **Test 4.3 (Optional):** If Grafana allows anonymous or test user, open Explore and run a trivial PromQL/LogQL query; datasources Loki and Prometheus are available.

---

## 5. Overall Verification

- [ ] README.md and REQ-apgar.md are up to date.
- [ ] No unexpected errors in `docker logs apgar`, `docker logs apgar-metrics-scraper`, `docker logs apgar-langgraph`.
- [ ] Health endpoints for apgar, apgar-metrics-scraper, apgar-langgraph respond.

---

## 6. Test Results Log

See `mads/apgar/tests/TEST-RESULTS.md` for run history.
