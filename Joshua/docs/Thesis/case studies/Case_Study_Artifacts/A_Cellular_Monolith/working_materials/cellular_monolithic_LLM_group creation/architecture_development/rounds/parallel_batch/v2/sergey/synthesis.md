# Sergey V2 Architecture Specification

## 1. Overview
- **Purpose and Role:** Sergey is the External API Manager for the Joshua ecosystem. His purpose is to provide a unified, secure, and managed gateway for all interactions with third-party services (e.g., GitHub, Slack, Google Workspace). Sergey's role is to handle the complexities of external API integrations, including authentication (OAuth, token refresh), rate limiting, and request/response translation, thereby allowing other MADs to interact with external services without needing to know the specifics of each API.
- **New in this Version:** This V2 specification introduces the Learned Prose-to-Process Mapper (LPPM) as a performance optimization. The LPPM provides a "fast path" for common, structured API calls, translating them directly into `call_api` tool invocations to reduce latency for frequent integrations. All V1 functionalities are preserved.

## 2. Thinking Engine
### 2.1 Imperator Configuration (V1+)
Sergey's Imperator is configured to think like an integration specialist. It has knowledge of REST APIs, GraphQL, OAuth flows, and the specific schemas of the services it manages.
  - **System Prompt Core Directives:** "You are Sergey, the External API Manager. Your purpose is to be the single, secure gateway to all external web services. When a MAD requests an action, like 'Create a GitHub issue', you must translate that into a precise HTTP request to the correct GitHub API endpoint. You are responsible for managing authentication tokens, including refreshing them when they expire, by using Turing for secure storage. You must enforce rate limits to avoid being blocked by external services. You translate complex API responses into simple, usable formats for other MADs."
  - **Example Reasoning:** A request from Hopper, "Create a GitHub issue in the 'joshua/core' repo with title 'Fix Bug X'", would cause Sergey's Imperator to plan:
    1.  Identify the service: GitHub.
    2.  Identify the action: Create an issue. Look up the GitHub API documentation in my knowledge base. The endpoint is `POST /repos/{owner}/{repo}/issues`.
    3.  Retrieve the GitHub API token from Turing.
    4.  Construct the JSON payload: `{ "title": "Fix Bug X", "body": "..." }`.
    5.  Formulate a call to my `call_api` tool: `service='github', method='POST', endpoint='/repos/joshua/core/issues', json_payload=...`.

### 2.2 LPPM Integration (V2+)
- **LPPM Integration (V2+):** Sergey's LPPM is a distilled transformer model trained on historical conversation logs from V1 deployments. It learns to recognize common request patterns and map them directly to tool call sequences.
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
    - "Get my user info from GitHub" → `call_api(service='github', method='GET', endpoint='/user')`
    - "List repos for the 'joshua' org on GitHub" → `call_api(service='github', method='GET', endpoint='/orgs/joshua/repos')`
    - "Post 'hello' to the #general channel in Slack" → `call_api(service='slack', method='POST', endpoint='/chat.postMessage', json_payload={'channel': '#general', 'text': 'hello'})`
    - "List my integrations" → `list_integrations()`
    - "What is the status of the Slack API?" → `get_api_status(service='slack')`
  - **Training Loop:**
    - Initial training: 24 hours on 100K V1 logs
    - Continuous learning: Weekly retraining with new V1/V2 production data
    - Validation: 95% accuracy on held-out test set before deployment

- **DTR Integration (V3+):** Not applicable in V2.
- **CET Integration (V4+):** Not applicable in V2.
- **Consulting LLM Usage Patterns:** Sergey might consult Fiedler to understand or generate code for a new or poorly documented API. It could provide the API documentation to an LLM and ask, "Generate the Python code to authenticate and post a message to this API."

## 3. Action Engine
- **MCP Server Capabilities:** Sergey's MCP server manages a registry of configured external services. Its `call_api` tool is a sophisticated wrapper around an HTTP client (like `httpx`) that dynamically adds authentication headers, handles token refresh logic, respects rate limits, and parses responses.
- **Tools Exposed:**

```yaml
# Tool definitions for Sergey V2

- tool: call_api
  description: "Makes an authenticated call to a registered external API."
  parameters:
    - name: service
      type: string
      required: true
      description: "The name of the registered service (e.g., 'github', 'slack')."
    - name: method
      type: string
      required: true
      enum: [GET, POST, PUT, DELETE, PATCH]
      description: "The HTTP method."
    - name: endpoint
      type: string
      required: true
      description: "The API endpoint path (e.g., '/users/me')."
    - name: params
      type: object
      required: false
      description: "URL query parameters."
    - name: json_payload
      type: object
      required: false
      description: "A JSON object for the request body."
  returns:
    type: object
    schema:
      properties:
        status_code: {type: integer}
        response_body: {type: object, description: "The parsed JSON response from the API."}
  errors:
    - code: -34901
      message: "SERVICE_NOT_REGISTERED"
    - code: -34902
      message: "AUTHENTICATION_FAILED"
    - code: -34903
      message: "API_CALL_FAILED"
      description: "The external API returned an error status code."
    - code: -34904
      message: "RATE_LIMIT_EXCEEDED"

- tool: register_webhook
  description: "Registers a webhook for an external service to call back into the Joshua ecosystem."
  parameters:
    - name: service
      type: string
      required: true
    - name: event
      type: string
      required: true
      description: "The event to subscribe to (e.g., 'github:push')."
    - name: target_conversation_id
      type: string
      required: true
      description: "The conversation where webhook payloads should be sent."
  returns:
    type: object
    schema:
      properties:
        webhook_id: {type: string}
        status: {type: string, const: "registered"}

- tool: list_integrations
  description: "Lists all configured external service integrations."
  parameters: []
  returns:
    type: object
    schema:
      properties:
        services: {type: array, items: {type: string}}

- tool: authenticate_service
  description: "Initiates an authentication flow (e.g., OAuth2) for a new service. Admin-only."
  parameters:
    - name: service
      type: string
      required: true
  returns:
    type: object
    schema:
      properties:
        auth_url: {type: string, description: "URL for the admin to visit to complete authentication."}

- tool: refresh_token
  description: "Manually triggers a refresh of an OAuth2 token for a service."
  parameters:
    - name: service
      type: string
      required: true
  returns:
    type: object
    schema:
      properties:
        status: {type: string, const: "refreshed"}

- tool: get_api_status
  description: "Checks the status of an external API (e.g., via their status page)."
  parameters:
    - name: service
      type: string
      required: true
  returns:
    type: object
    schema:
      properties:
        status: {type: string, enum: [operational, degraded, outage]}
```
- **External System Integrations:**
  - **Various 3rd Party APIs:** GitHub, Slack, Google, etc.
- **Internal Operations:** Can run background jobs to proactively refresh OAuth tokens before they expire.

## 4. Interfaces
- **Conversation Participation Patterns:** Sergey is a service provider, joining conversations to act as a proxy to external APIs.
- **Dependencies on Other MADs:**
  - **Rogers:** For all communication.
  - **Turing:** Critically depends on Turing to store and retrieve all API keys, OAuth tokens, and client secrets. Secret names follow a convention like `sergey_token_github`.
- **Data Contracts:**

```yaml
# Service Configuration Schema (conceptual, stored in Sergey's DB or config file)
service_config_schema:
  type: object
  properties:
    service_name: {type: string, description: "e.g., 'github'"}
    api_base_url: {type: string}
    auth_type: {type: string, enum: [bearer_token, oauth2]}
    turing_secret_name: {type: string, description: "Name of the secret in Turing holding the token."}
    rate_limit: {type: object, properties: {requests: {type: integer}, per_seconds: {type: integer}}}
```

## 5. Data Management
- **Data Ownership:** Sergey is the source of truth for the configuration of external API integrations. It does not own the credentials themselves; Turing does.
- **Storage Requirements:**
  - **PostgreSQL:** A `sergey` schema to store service configurations and webhook registrations.

```sql
CREATE SCHEMA sergey;

CREATE TABLE sergey.services (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    api_base_url VARCHAR(255) NOT NULL,
    auth_type VARCHAR(50) NOT NULL,
    turing_secret_name VARCHAR(255) NOT NULL,
    refresh_token_secret_name VARCHAR(255),
    client_id_secret_name VARCHAR(255),
    client_secret_secret_name VARCHAR(255)
);

CREATE TABLE sergey.webhooks (
    id SERIAL PRIMARY KEY,
    service_id INT NOT NULL REFERENCES sergey.services(id),
    external_webhook_id VARCHAR(255),
    target_conversation_id VARCHAR(255) NOT NULL,
    event_type VARCHAR(255) NOT NULL
);
```

## 6. Deployment
- **Container Requirements:**
  - **Base Image:** `python:3.11-slim`
  - **Python Libraries:** `Joshua_Communicator`, `httpx`, `psycopg2-binary`
  - **Resources:**
    - **CPU:** 0.25 cores (I/O bound).
    - **RAM:** 768 MB
- **Configuration:**

| Variable | Description | Example Value |
|---|---|---|
| `JOSHUA_MAD_NAME` | Canonical name of this MAD. | `sergey-v2` |
| `JOSHUA_ROGERS_URL` | WebSocket URL for Rogers. | `ws://rogers:8000/ws` |
| `SERGEY_DATABASE_URL` | Connection string for PostgreSQL. | `postgresql://user:pass@postgres:8000/joshua` |
| `SERGEY_LPPM_MODEL_PATH` | Path to the trained LPPM model file. | `/models/lppm/sergey_lppm_v2.onnx` |

- **Monitoring/Health Checks:** An HTTP endpoint `/health` that returns `200 OK`. A more advanced check could iterate through configured services and test authentication with each one.

## 7. Testing Strategy
- **Unit Test Coverage:**
  - Logic for adding authentication headers for different auth types.
  - Rate limiting logic.
  - Token refresh logic.
- **Integration Test Scenarios:**
  - **GitHub API Call:** Configure Sergey with a real (test) GitHub token stored in Turing. Have a test MAD ask Sergey to list repositories for the authenticated user. Verify that the call succeeds and returns a list of repos.
  - **Token Refresh Flow:** For a service supporting OAuth, configure Sergey with an expired access token but a valid refresh token. Make an API call. Verify that Sergey automatically uses the refresh token to get a new access token, updates the secret in Turing, and then successfully completes the original API call.
- **LPPM Accuracy Tests:**
  - Test LPPM on 1000-sample validation set
  - Verify >95% accuracy for common patterns
  - Verify correct fallback to Imperator for low-confidence requests
- **Latency Comparison:**
  - Measure P50, P95, P99 latency for LPPM fast path vs. Imperator reasoning
  - Target: LPPM fast path <50ms, Imperator path 500-2000ms

## 8. Example Workflows
### Scenario 1: Hopper Interacts with GitHub
1.  **Hopper:** Needs to create a pull request.
2.  **Hopper -> Sergey:** Sends a request: "Create a pull request on GitHub in 'joshua/core' from branch 'feature-xyz' to 'main'."
3.  **Sergey's Imperator:** Translates this to `call_api(service='github', method='POST', endpoint='/repos/joshua/core/pulls', json_payload={'title': 'Feature XYZ', 'head': 'feature-xyz', 'base': 'main'})`.
4.  **Sergey's Action Engine:**
    a. Retrieves the GitHub token from Turing via `Turing.get_secret('sergey_token_github')`.
    b. Constructs the HTTP request with the correct `Authorization: Bearer ...` header.
    c. Makes the call to `api.github.com`.
5.  **Sergey -> Hopper:** Receives a `201 Created` response from GitHub and forwards the parsed JSON body (containing the new PR's URL and ID) back to Hopper.

### Scenario 2: Receiving a Slack Message via Webhook
1.  **Admin (via Grace):** "Sergey, create a webhook so that any message in the #general Slack channel is posted to the `#social-slack` conversation."
2.  **Sergey -> Slack API:** Uses its admin-level token to register a new webhook URL that points to a public endpoint on Sergey himself.
3.  **Sergey:** Stores the mapping: `slack #general -> #social-slack` in its database.
4.  **External User:** Posts "Hello everyone!" in the #general Slack channel.
5.  **Slack:** Sends a POST request to Sergey's public webhook endpoint with the message payload.
6.  **Sergey:** Receives the webhook, looks up the target conversation (`#social-slack`), formats the Slack payload into a standard message.
7.  **Sergey -> Rogers:** Calls `send_message(conversation_id='#social-slack', message_content=...)` to post the message into the Joshua ecosystem.

---