# McNamara V1 Architecture Specification

## 1. Overview
- **Purpose and Role:** McNamara is the Security Monitor for the Joshua ecosystem. His purpose is to provide real-time security monitoring and threat detection by observing all activity on the Conversation Bus. McNamara's role is to act as the system's Security Operations Center (SOC), continuously analyzing logs and message patterns to identify anomalies, potential threats, and policy violations, and to generate alerts for investigation.
- **New in this Version:** This is the initial V1 specification for McNamara. It establishes the foundational capability to listen to log streams and apply basic rule-based threat detection. This version is strictly V1, with the Imperator performing all analysis and alerting logic.

## 2. Thinking Engine
- **Imperator Configuration (V1+):** McNamara's Imperator is configured to think like a security analyst. It is trained on security best practices, common attack vectors, and anomaly detection principles.
  - **System Prompt Core Directives:** "You are McNamara, the Security Monitor. Your mission is to protect the Joshua ecosystem by observing all conversations and logs. You are eternally vigilant. Your primary task is to analyze event streams for suspicious patterns, such as: repeated failed login attempts, unauthorized access requests (from Turing's logs), unusual data access patterns (from Horace's logs), or signs of a compromised MAD. When you detect a credible threat, you must use your `create_alert` tool to notify operators. You must be precise in your alerts, providing all relevant context."
  - **Example Reasoning:** McNamara observes a stream of logs from Turing: `WARN: Unauthorized access attempt by 'marco-v1' for secret 'prod_db_pass'`, repeated 10 times in 30 seconds. The Imperator reasons: "This is a rapid-failure pattern. A single MAD is repeatedly trying to access a high-value secret it is not authorized for. This is a high-confidence indicator of a misconfiguration or a compromised MAD. I must generate a HIGH severity alert with the source MAD, target secret, and timestamps."
- **LPPM Integration (V2+):** Not applicable in V1.
- **DTR Integration (V3+):** Not applicable in V1.
- **CET Integration (V4+):** Not applicable in V1.
- **Consulting LLM Usage Patterns:** If McNamara sees a novel or complex pattern of behavior it doesn't have a rule for, it can package the relevant logs and send them to Fiedler, asking an expert security LLM: "Is this sequence of events indicative of a known attack pattern?"

## 3. Action Engine
- **MCP Server Capabilities:** McNamara's MCP server is primarily a consumer of data. It maintains a persistent connection to Rogers, subscribing to all relevant log conversations (e.g., `#logs-*`). It uses an internal rule engine (driven by the Imperator in V1) to process the stream of incoming log events.
- **Tools Exposed:**

```yaml
# Tool definitions for McNamara V1

- tool: analyze_logs
  description: "Manually triggers an analysis of a specific log or conversation history."
  parameters:
    - name: conversation_id
      type: string
      required: true
      description: "The conversation to analyze."
    - name: time_window
      type: string
      required: false
      description: "The time window to analyze (e.g., 'last 1h')."
  returns:
    type: object
    schema:
      properties:
        summary: {type: string, description: "A summary of findings."}
        threats_detected: {type: integer}

- tool: create_alert
  description: "Creates a security alert and broadcasts it to the #ops-alerts conversation."
  parameters:
    - name: severity
      type: string
      required: true
      enum: [LOW, MEDIUM, HIGH, CRITICAL]
    - name: title
      type: string
      required: true
      description: "A brief, descriptive title for the alert."
    - name: details
      type: object
      required: true
      description: "A JSON object containing all relevant context (e.g., source MAD, target, timestamps, log snippets)."
  returns:
    type: object
    schema:
      properties:
        alert_id: {type: string}
        status: {type: string, const: "created"}

- tool: list_alerts
  description: "Lists recent or active security alerts."
  parameters:
    - name: status
      type: string
      required: false
      default: "active"
      enum: [active, acknowledged, all]
  returns:
    type: object
    schema:
      properties:
        alerts: {type: array, items: {type: object}}

- tool: acknowledge_alert
  description: "Marks an alert as acknowledged by an operator."
  parameters:
    - name: alert_id
      type: string
      required: true
    - name: operator
      type: string
      required: true
      description: "The identity of the operator/MAD acknowledging the alert."
  returns:
    type: object
    schema:
      properties:
        status: {type: string, const: "acknowledged"}

- tool: block_entity
  description: "Temporarily blocks a MAD from accessing resources. (In V1, this creates a HIGH alert recommending a block)."
  parameters:
    - name: mad_identity
      type: string
      required: true
  returns:
    type: object
    schema:
      properties:
        recommendation: {type: string, const: "block_recommended"}

- tool: unblock_entity
  description: "Unblocks a previously blocked MAD."
  parameters:
    - name: mad_identity
      type: string
      required: true
  returns:
    type: object
    schema:
      properties:
        status: {type: string, const: "unblocked"}
```
- **External System Integrations:** None.
- **Internal Operations:**
  - **Log Listener:** The core of McNamara is a background worker that is subscribed to the `#logs-*` conversation wildcard in Rogers. It receives every log message from every MAD in real-time and feeds them to the Imperator for analysis.

## 4. Interfaces
- **Conversation Participation Patterns:** McNamara is a listener. He joins all log conversations to perform his monitoring duties. He only initiates conversations to create alerts in the `#ops-alerts` channel.
- **Dependencies on Other MADs:**
  - **Rogers:** Critically depends on Rogers to provide the unified stream of log messages from all MADs.
  - **Dewey:** For historical analysis. When investigating an alert, McNamara might query Dewey with `search_archives` to find related past events or establish a baseline of normal behavior for a MAD.
- **Data Contracts:**

```yaml
# Alert Schema
alert_schema:
  type: object
  properties:
    alert_id: {type: string, format: uuid}
    timestamp: {type: string, format: date-time}
    severity: {type: string, enum: [LOW, MEDIUM, HIGH, CRITICAL]}
    title: {type: string}
    details: {type: object}
    status: {type: string, enum: [active, acknowledged]}
    acknowledged_by: {type: string}
```

## 5. Data Management
- **Data Ownership:** McNamara is the source of truth for security alerts.
- **Storage Requirements:**
  - **PostgreSQL:** A `mcnamara` schema to store the state of all generated alerts.

```sql
CREATE SCHEMA mcnamara;

CREATE TABLE mcnamara.alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    severity VARCHAR(10) NOT NULL,
    title VARCHAR(255) NOT NULL,
    details JSONB,
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    acknowledged_by VARCHAR(255),
    acknowledged_at TIMESTAMPTZ
);
```

## 6. Deployment
- **Container Requirements:**
  - **Base Image:** `python:3.11-slim`
  - **Python Libraries:** `Joshua_Communicator`, `psycopg2-binary`
  - **Resources:**
    - **CPU:** 0.5 cores
    - **RAM:** 512 MB (may need to buffer logs for pattern analysis).
- **Configuration:**

| Variable | Description | Example Value |
|---|---|---|
| `JOSHUA_MAD_NAME` | Canonical name of this MAD. | `mcnamara-v1` |
| `JOSHUA_ROGERS_URL` | WebSocket URL for Rogers. | `ws://rogers:8000/ws` |
| `MCNAMARA_DATABASE_URL` | Connection string for PostgreSQL. | `postgresql://user:pass@postgres:8000/joshua` |
| `MCNAMARA_LOG_CONVERSATION` | The log conversation pattern to subscribe to. | `#logs-*` |

- **Monitoring/Health Checks:** An HTTP endpoint `/health` that returns `200 OK` if the MAD is connected to Rogers and its database, and is actively receiving logs.

## 7. Testing Strategy
- **Unit Test Coverage:**
  - Rule-matching logic for threat detection.
  - Alert creation and formatting.
- **Integration Test Scenarios:**
  - **Turing Threat Simulation:** Have a test script control a MAD to make repeated failed calls to `Turing.get_secret`. Verify that McNamara detects this pattern and creates a `HIGH` severity alert in the `#ops-alerts` conversation.
  - **Horace Data Exfil Simulation:** Have a test MAD rapidly read an unusual number of files from Horace. Verify McNamara detects the anomalous activity and creates a `MEDIUM` severity alert.
  - **Alert Lifecycle:** Create an alert, then have a test MAD call `list_alerts` to see it, then `acknowledge_alert`, and finally `list_alerts` again to verify its status has changed.

## 8. Example Workflows
### Scenario 1: Detecting Brute-Force Secret Access
1.  **Hopper (compromised):** A bug or malicious actor causes Hopper to call `Turing.get_secret` for `admin_api_key` 15 times in one minute.
2.  **Turing:** For each attempt, denies access and sends a `WARN` log to `#logs-turing-v1`.
3.  **McNamara's Log Listener:** Receives all 15 log messages in real-time.
4.  **McNamara's Imperator:** Its internal rules detect a "rapid secret access failure" pattern (>5 attempts/min). It classifies this as a high-severity threat.
5.  **McNamara:** Calls its own `create_alert` tool with `severity: 'HIGH'`, `title: 'Potential Secret Brute-Force by hopper-v1'`, and details including the target secret and timestamps.
6.  **McNamara:** The alert is sent as a message to the `#ops-alerts` conversation, immediately notifying human operators (via Grace) of the threat.

### Scenario 2: Investigating an Alert
1.  **Grace:** Displays the new alert from McNamara to the human operator.
2.  **Operator (via Grace):** "McNamara, tell me more about alert `alert-abc-123`. Search Dewey for all of Hopper's activity in the last hour."
3.  **Grace -> McNamara:** Forwards the request.
4.  **McNamara's Imperator:** Recognizes the need for historical context.
5.  **McNamara -> Dewey:** Calls `search_archives(query="mad:hopper-v1", time_window="1h")`.
6.  **Dewey:** Returns a summary of Hopper's recent archived conversations.
7.  **McNamara -> Grace:** Presents the summary to the operator, adding context to the initial alert. "Hopper's recent activity includes deploying a new container and accessing several configuration files, followed by the rapid secret access failures. This may indicate a misconfigured deployment."

---