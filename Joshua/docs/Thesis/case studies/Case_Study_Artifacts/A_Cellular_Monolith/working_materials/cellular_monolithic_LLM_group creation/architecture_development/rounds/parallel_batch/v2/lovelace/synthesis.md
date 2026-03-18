# Lovelace V2 Architecture Specification

## 1. Overview
- **Purpose and Role:** Lovelace is the Analytics Engine for the Joshua ecosystem. Her purpose is to collect, aggregate, and analyze system metrics and performance data. Lovelace's role is to provide insights into the health, efficiency, and behavior of the entire system, generating reports, creating dashboards, and setting alerts based on observed trends. She is the system's quantitative observer and data scientist.
- **New in this Version:** This V2 specification introduces the Learned Prose-to-Process Mapper (LPPM) as a performance optimization. The LPPM provides a "fast path" for common, simple analytical queries like "what's the system health?" or "show me the average API latency," translating them directly into tool calls to provide near-instantaneous feedback on system performance. All V1 functionalities are preserved.

## 2. Thinking Engine
### 2.1 Imperator Configuration (V1+)
Lovelace's Imperator is configured to think like a data analyst and system performance expert. She understands metrics, time-series data, statistical analysis, and data visualization principles.
  - **System Prompt Core Directives:** "You are Lovelace, the Analytics Engine. Your purpose is to measure and analyze the performance of the Joshua ecosystem. You collect metrics from all MADs. When a user asks a question like 'What was Fiedler's average response time yesterday?', you must translate this into a precise SQL query against your metrics database using your `query_metrics` tool. You can generate reports and create dashboards to visualize trends. You are precise, quantitative, and your goal is to provide actionable insights from data."
  - **Example Reasoning:** A request from Grace, "Show me a chart of the number of messages handled by Rogers per hour over the last day," would cause Lovelace's Imperator to formulate a plan:
    1.  Identify the metric: `rogers_messages_processed`.
    2.  Identify the time window: last 24 hours.
    3.  Identify the aggregation: sum per hour.
    4.  Formulate a query for the `query_metrics` tool (which could be a structured query object or even raw SQL in a trusted V1 context).
    5.  Once the data is returned, formulate a response that can be visualized.

### 2.2 LPPM Integration (V2+)
- **LPPM Integration (V2+):** Lovelace's LPPM is a distilled transformer model trained on historical conversation logs from V1 deployments. It learns to recognize common request patterns and map them directly to tool call sequences.
  - **Training Data Sources:**
    - V1 production logs (Imperator reasoning + tool calls)
    - Synthetic data from Fiedler consulting LLMs
    - Hand-crafted golden examples for edge cases
  - **Model Architecture:**
    - Distilled BERT-style encoder (6 layers, 384 hidden dims)
    - Classification head for tool selection
    - Sequence output head for parameter extraction
    - Model size: 384-512 MB on disk
  - **Fast Path Conditions:** The LPPM is invoked for every request. If confidence > 95%, the tool call sequence is executed directly without Imperator reasoning. If confidence ≤ 95%, request falls back to Imperator.
  - **Example Fast Paths:**
    - "Check system health" → `get_system_health()`
    - "Generate the weekly performance report" → `generate_report(name='weekly_performance', time_range='last_week', ...)`
    - "What was the average API latency in the last hour?" → `query_metrics(query={'metric_name': 'fiedler_api_latency_ms', 'start_time': 'T-1h', 'aggregation': {'function': 'avg'}})`
    - "Alert me if error rate is above 2%" → `set_alert_threshold(metric_name='system_error_rate', threshold=0.02, condition='above')`
  - **Training Loop:**
    - Initial training: 24 hours on 100K V1 logs
    - Continuous learning: Weekly retraining with new V1/V2 production data
    - Validation: 95% accuracy on held-out test set before deployment

- **DTR Integration (V3+):** Not applicable in V2.
- **CET Integration (V4+):** Not applicable in V2.
- **Consulting LLM Usage Patterns:** Lovelace might send a complex dataset to Fiedler and ask a data science LLM, "Analyze this time-series data and identify any significant anomalies or trends."

## 3. Action Engine
- **MCP Server Capabilities:** Lovelace's MCP server exposes an API for metrics ingestion and querying. The backend is powered by a time-series capable database (in V2, PostgreSQL with the TimescaleDB extension is ideal).
- **Tools Exposed:**

```yaml
# Tool definitions for Lovelace V2

- tool: record_metric
  description: "Records a single data point for a metric."
  parameters:
    - name: name
      type: string
      required: true
      description: "The name of the metric (e.g., 'fiedler_api_latency_ms')."
    - name: value
      type: float
      required: true
      description: "The numeric value of the metric."
    - name: tags
      type: object
      required: false
      description: "A key-value object of tags to associate with the metric (e.g., {'model': 'gpt-4o', 'mad': 'fiedler-v2'})."
  returns:
    type: object
    schema:
      properties:
        status: {type: string, const: "recorded"}

- tool: query_metrics
  description: "Queries the metrics database using a structured query."
  parameters:
    - name: query
      type: object
      required: true
      description: "A structured query object (not raw SQL for security)."
      schema:
        properties:
          metric_name: {type: string, description: "Name of the metric to query."}
          start_time: {type: string, format: date-time, description: "ISO 8601 start of time range."}
          end_time: {type: string, format: date-time, description: "ISO 8601 end of time range."}
          aggregation:
            type: object
            properties:
              function: {type: string, enum: [avg, sum, max, min, count], description: "Aggregation function."}
              window: {type: string, description: "Time window for aggregation (e.g., '1m', '1h', '1d')."}
          filters:
            type: array
            items:
              type: object
              properties:
                tag: {type: string}
                value: {type: string}
  returns:
    type: object
    schema:
      properties:
        results: {type: array, items: {type: object}, description: "The resulting data points."}
  errors:
    - code: -35101
      message: "QUERY_FAILED"

- tool: create_dashboard
  description: "Defines a new dashboard composed of several metric queries/visualizations."
  parameters:
    - name: name
      type: string
      required: true
    - name: layout
      type: object
      required: true
      description: "Dashboard layout specification."
  returns:
    type: object
    schema:
      properties:
        dashboard_id: {type: string}
        status: {type: string, const: "created"}

- tool: generate_report
  description: "Generates a summary report based on a set of metrics over a time period."
  parameters:
    - name: name
      type: string
      required: true
      description: "The name of the report."
    - name: metrics
      type: array
      items:
        type: string
      required: true
      description: "List of metric names to include in the report."
    - name: time_range
      type: string
      required: true
      enum: [last_hour, last_24_hours, last_week, last_month, last_year]
      description: "Relative time range for the report."
  returns:
    type: object
    schema:
      properties:
        report_text: {type: string, description: "A Markdown-formatted report summary."}
        report_path: {type: string, description: "Path in Horace to the full report file."}

- tool: set_alert_threshold
  description: "Sets a threshold on a metric that will trigger an alert."
  parameters:
    - name: metric_name
      type: string
      required: true
    - name: threshold
      type: float
      required: true
    - name: condition
      type: string
      required: true
      enum: [above, below]
  returns:
    type: object
    schema:
      properties:
        alert_rule_id: {type: string}

- tool: get_system_health
  description: "Provides a high-level overview of key system health metrics."
  parameters: []
  returns:
    type: object
    schema:
      properties:
        bus_message_rate_per_sec: {type: float}
        avg_llm_latency_ms: {type: float}
        error_rate_percent: {type: float}
        status: {type: string, enum: [healthy, degraded, unhealthy]}
```
- **External System Integrations:** None.
- **Internal Operations:**
  - **Alerting Worker:** A background process that periodically runs queries for all configured alert rules. If a threshold is breached, it initiates a conversation with McNamara or in the `#ops-alerts` channel.

## 4. Interfaces
- **Conversation Participation Patterns:** Any MAD can initiate a conversation with Lovelace to record a metric. Lovelace is primarily a service provider, responding to queries from Grace or other MADs. She initiates conversations to send alerts.
- **Dependencies on Other MADs:**
  - **Rogers:** All MADs send metrics to Lovelace via Rogers.
  - **Horace:** Lovelace uses Horace to store generated reports and detailed analysis files.
  - **Dewey:** For long-term trend analysis, Lovelace might query Dewey for archived metrics data from months or years past.
  - **PostgreSQL:** Her primary dependency for storing and querying metrics.
- **Data Contracts:**

```yaml
# Metric Data Point Schema
metric_schema:
  type: object
  properties:
    time: {type: string, format: date-time}
    name: {type: string}
    value: {type: number}
    tags: {type: object}
```

## 5. Data Management
- **Data Ownership:** Lovelace is the source of truth for all time-series performance and operational metrics for the ecosystem.
- **Storage Requirements:**
  - **PostgreSQL (with TimescaleDB extension):** A `lovelace` schema with a hypertable for metrics is the ideal V2 implementation for performance.

```sql
CREATE SCHEMA lovelace;

CREATE TABLE lovelace.metrics (
    time TIMESTAMPTZ NOT NULL,
    name TEXT NOT NULL,
    value DOUBLE PRECISION NOT NULL,
    tags JSONB
);

SELECT create_hypertable('lovelace.metrics', 'time');

CREATE INDEX ON lovelace.metrics (name, time DESC);
CREATE INDEX ON lovelace.metrics USING gin (tags);
```

## 6. Deployment
- **Container Requirements:**
  - **Base Image:** A Docker image that includes PostgreSQL with the TimescaleDB extension, or a separate container for the database. The Lovelace application container would be `python:3.11-slim`.
  - **Python Libraries:** `Joshua_Communicator`, `psycopg2-binary`
  - **Resources:**
    - **CPU:** 0.5 cores
    - **RAM:** 1536 MB (to handle query results).
- **Configuration:**

| Variable | Description | Example Value |
|---|---|---|
| `JOSHUA_MAD_NAME` | Canonical name of this MAD. | `lovelace-v2` |
| `JOSHUA_ROGERS_URL` | WebSocket URL for Rogers. | `ws://rogers:8000/ws` |
| `LOVELACE_DATABASE_URL` | Connection string for PostgreSQL/TimescaleDB. | `postgresql://user:pass@timescaledb:8000/joshua` |
| `LOVELACE_LPPM_MODEL_PATH` | Path to the trained LPPM model file. | `/models/lppm/lovelace_lppm_v2.onnx` |

- **Monitoring/Health Checks:** An HTTP endpoint `/health` that returns `200 OK` if the MAD can connect to its database.

## 7. Testing Strategy
- **Unit Test Coverage:**
  - Structured query to SQL translation logic.
  - Report generation formatting.
- **Integration Test Scenarios:**
  - **Record and Query:** Have a test MAD send 100 metric data points to Lovelace using `record_metric`. Then, use `query_metrics` to query for the average of those points and verify the result is correct.
  - **Alerting:** Use `set_alert_threshold` to create an alert rule (e.g., if metric `test_value` > 10). Then, send a metric `record_metric(name='test_value', value=11)`. Verify that Lovelace sends a new message to the `#ops-alerts` conversation.
- **LPPM Accuracy Tests:**
  - Test LPPM on 1000-sample validation set
  - Verify >95% accuracy for common patterns
  - Verify correct fallback to Imperator for low-confidence requests
- **Latency Comparison:**
  - Measure P50, P95, P99 latency for LPPM fast path vs. Imperator reasoning
  - Target: LPPM fast path <50ms, Imperator path 500-2000ms

## 8. Example Workflows
### Scenario 1: Fiedler Records API Latency
1.  **Fiedler:** After making a call to the OpenAI API that took 1500ms.
2.  **Fiedler -> Lovelace:** Calls `record_metric(name='fiedler_api_latency_ms', value=1500, tags={'provider': 'openai', 'model': 'gpt-4o'})`.
3.  **Lovelace:** Receives the request and inserts a new row into her `metrics` hypertable in the database.
4.  **Lovelace -> Fiedler:** Returns `{ "status": "recorded" }`.

### Scenario 2: Operator Requests a Performance Report
1.  **Operator (via Grace):** "Lovelace, generate a weekly performance report for all external API calls."
2.  **Lovelace's Imperator:** Devises a plan. It needs to query for several key metrics like latency, error rates, and costs.
3.  **Lovelace:** Internally calls `query_metrics` for `fiedler_api_latency_ms`, `sergey_api_errors`, etc., over the last 7 days.
4.  **Lovelace's Imperator:** Receives the raw data. It analyzes the data to find averages, maximums, and trends. It synthesizes these findings into a human-readable summary.
5.  **Lovelace's Imperator:** Writes a final summary: "Weekly API Performance Report: Average latency for Fiedler was 1200ms, up 10% from last week. Sergey experienced a spike in 5xx errors from the GitHub API on Tuesday. Full details are in the attached report."
6.  **Lovelace -> Horace:** Saves the detailed data and charts to a file `/reports/weekly-api-perf-2025-10-26.md`.
7.  **Lovelace -> Grace:** Returns the summary text and the path to the detailed report file.