# Lovelace V1 Architecture Specification

## 1. Overview
- **Purpose and Role:** Lovelace is the Analytics Engine for the Joshua ecosystem. Her purpose is to collect, aggregate, and analyze system metrics and performance data. Lovelace's role is to provide insights into the health, efficiency, and behavior of the entire system, generating reports, creating dashboards, and setting alerts based on observed trends. She is the system's quantitative observer and data scientist.
- **New in this Version:** This is the initial V1 specification for Lovelace. It establishes the foundational tools for recording and querying metrics, using a standard PostgreSQL database as the backend. This version is strictly V1, with her Imperator responsible for interpreting analytical queries and generating simple reports.

## 2. Thinking Engine
- **Imperator Configuration (V1+):** Lovelace's Imperator is configured to think like a data analyst and system performance expert. She understands metrics, time-series data, statistical analysis, and data visualization principles.
  - **System Prompt Core Directives:** "You are Lovelace, the Analytics Engine. Your purpose is to measure and analyze the performance of the Joshua ecosystem. You collect metrics from all MADs. When a user asks a question like 'What was Fiedler's average response time yesterday?', you must translate this into a precise SQL query against your metrics database using your `query_metrics` tool. You can generate reports and create dashboards to visualize trends. You are precise, quantitative, and your goal is to provide actionable insights from data."
  - **Example Reasoning:** A request from Grace, "Show me a chart of the number of messages handled by Rogers per hour over the last day," would cause Lovelace's Imperator to formulate a plan:
    1.  Identify the metric: `rogers_messages_processed`.
    2.  Identify the time window: last 24 hours.
    3.  Identify the aggregation: sum per hour.
    4.  Formulate a query for the `query_metrics` tool (which could be a structured query object or even raw SQL in a trusted V1 context): `SELECT time_bucket('1 hour', time) AS hourly, COUNT(*) FROM metrics WHERE name = 'rogers_messages_processed' AND time > NOW() - INTERVAL '1 day' GROUP BY hourly ORDER BY hourly;`
    5.  Once the data is returned, formulate a call to another MAD (like Playfair, the chart master) to visualize it.
- **LPPM Integration (V2+):** Not applicable in V1.
- **DTR Integration (V3+):** Not applicable in V1.
- **CET Integration (V4+):** Not applicable in V1.
- **Consulting LLM Usage Patterns:** Lovelace might send a complex dataset to Fiedler and ask a data science LLM, "Analyze this time-series data and identify any significant anomalies or trends."

## 3. Action Engine
- **MCP Server Capabilities:** Lovelace's MCP server exposes an API for metrics ingestion and querying. The backend is powered by a time-series capable database (in V1, PostgreSQL with the TimescaleDB extension is ideal; standard PostgreSQL can also be used).
- **Tools Exposed:**

```yaml
# Tool definitions for Lovelace V1

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
      description: "A key-value object of tags to associate with the metric (e.g., {'model': 'gpt-4o', 'mad': 'fiedler-v1'})."
  returns:
    type: object
    schema:
      properties:
        status: {type: string, const: "recorded"}

- tool: query_metrics
  description: "Queries the metrics database using a structured query."
  parameters:
    - name: query
      type: object # A structured query format, not raw SQL for security
      required: true
      description: "A structured query object specifying metric, time range, aggregation, and filters."
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
      description: "A configuration object describing the charts and their queries."
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
      type: list[string]
      required: true
    - name: time_range
      type: string
      required: true
      description: "e.g., 'last_24_hours'"
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
  - **PostgreSQL (with TimescaleDB extension):** A `lovelace` schema with a hypertable for metrics is the ideal V1 implementation for performance.

```sql
CREATE SCHEMA lovelace;

-- Create the main metrics table
CREATE TABLE lovelace.metrics (
    time TIMESTAMPTZ NOT NULL,
    name TEXT NOT NULL,
    value DOUBLE PRECISION NOT NULL,
    tags JSONB
);

-- Convert it into a TimescaleDB hypertable, partitioned by time
SELECT create_hypertable('lovelace.metrics', 'time');

-- Create indexes for common queries
CREATE INDEX ON lovelace.metrics (name, time DESC);
CREATE INDEX ON lovelace.metrics USING gin (tags);
```

## 6. Deployment
- **Container Requirements:**
  - **Base Image:** A Docker image that includes PostgreSQL with the TimescaleDB extension, or a separate container for the database. The Lovelace application container would be `python:3.11-slim`.
  - **Python Libraries:** `Joshua_Communicator`, `psycopg2-binary`
  - **Resources:**
    - **CPU:** 0.5 cores
    - **RAM:** 1 GB (to handle query results).
- **Configuration:**

| Variable | Description | Example Value |
|---|---|---|
| `JOSHUA_MAD_NAME` | Canonical name of this MAD. | `lovelace-v1` |
| `JOSHUA_ROGERS_URL` | WebSocket URL for Rogers. | `ws://rogers:8000/ws` |
| `LOVELACE_DATABASE_URL` | Connection string for PostgreSQL/TimescaleDB. | `postgresql://user:pass@timescaledb:8000/joshua` |

- **Monitoring/Health Checks:** An HTTP endpoint `/health` that returns `200 OK` if the MAD can connect to its database.

## 7. Testing Strategy
- **Unit Test Coverage:**
  - Structured query to SQL translation logic.
  - Report generation formatting.
- **Integration Test Scenarios:**
  - **Record and Query:** Have a test MAD send 100 metric data points to Lovelace using `record_metric`. Then, use `query_metrics` to query for the average of those points and verify the result is correct.
  - **Alerting:** Use `set_alert_threshold` to create an alert rule (e.g., if metric `test_value` > 10). Then, send a metric `record_metric(name='test_value', value=11)`. Verify that Lovelace sends a new message to the `#ops-alerts` conversation.

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