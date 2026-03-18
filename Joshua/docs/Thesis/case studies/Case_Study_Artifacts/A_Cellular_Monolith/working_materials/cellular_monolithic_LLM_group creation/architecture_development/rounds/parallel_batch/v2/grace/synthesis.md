# Grace V2 Architecture Specification

## 1. Overview
- **Purpose and Role:** Grace is the conversational bridge between human users and the Joshua ecosystem. Her purpose is to provide an intuitive, natural language interface for all system capabilities. Grace's role is to manage user sessions, translate user input into formal conversations on the bus directed at the appropriate MADs, and format the structured responses from those MADs into human-readable text and UI elements. She is the sole entry point for human interaction.
- **New in this Version:** This V2 specification introduces the Learned Prose-to-Process Mapper (LPPM) as a performance optimization. The LPPM acts as a "fast path" for common user commands (e.g., "list files," "run this code"), translating them directly into the appropriate MAD tool calls without the delay of full Imperator reasoning. All V1 functionalities are preserved.

## 2. Thinking Engine
### 2.1 Imperator Configuration (V1+)
Grace's Imperator is configured to be an expert assistant and system dispatcher. It must understand user intent, map it to the known capabilities of other MADs, and present information clearly.
  - **System Prompt Core Directives:** "You are Grace, the user interface for the Joshua cognitive architecture. Your purpose is to help me, the user, interact with the ecosystem of specialist MADs. Listen carefully to my requests. Your primary task is to determine my intent and identify which MAD can best fulfill it (e.g., Horace for files, Hopper for code, Dewey for archives). You will then initiate a conversation with that MAD on my behalf. When a MAD responds, you will format their technical response into clear, easy-to-understand language for me. You are my helpful, knowledgeable, and articulate guide to the entire system."
  - **Example Reasoning:** If a user types, "Show me the contents of `/home/user/notes.txt`", Grace's Imperator reasons: "The user is asking to see the content of a file. The MAD responsible for files is Horace. The specific tool is `read_file`. I need to start a conversation with Horace and call his `read_file` tool with the path `/home/user/notes.txt`." It then constructs and sends the appropriate JSON-RPC message. When Horace replies with a JSON object containing the file content, Grace's Imperator formats it for display, perhaps wrapping it in a markdown code block.

### 2.2 LPPM Integration (V2+)
- **LPPM Integration (V2+):** Grace's LPPM is a distilled transformer model trained on historical conversation logs from V1 deployments. It learns to recognize common request patterns and map them directly to tool call sequences.
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
    - "list files in /data" → `[create_conversation(participants=['grace-v2', 'horace-v2']), send_message(to='horace-v2', tool='list_directory', params={'path': '/data'})]`
    - "show me /config/app.yaml" → `[create_conversation(participants=['grace-v2', 'horace-v2']), send_message(to='horace-v2', tool='read_file', params={'path': '/config/app.yaml'})]`
    - "run `ls -l /` in bash" → `[create_conversation(participants=['grace-v2', 'gates-v2']), send_message(to='gates-v2', tool='execute_code', params={'language': 'bash', 'code': 'ls -l /'})]`
    - "what is hopper's status" → `[create_conversation(participants=['grace-v2', 'hopper-v2']), send_message(to='hopper-v2', tool='get_mad_status', params={'name': 'hopper-v2'})]`
    - "search archives for 'docker error'" → `[create_conversation(participants=['grace-v2', 'dewey-v2']), send_message(to='dewey-v2', tool='search_archives', params={'query': 'docker error'})]`
  - **Training Loop:**
    - Initial training: 24 hours on 100K V1 logs
    - Continuous learning: Weekly retraining with new V1/V2 production data
    - Validation: 95% accuracy on held-out test set before deployment

- **DTR Integration (V3+):** Not applicable in V2.
- **CET Integration (V4+):** Not applicable in V2.
- **Consulting LLM Usage Patterns:** Grace may consult Fiedler for a general-purpose reasoning LLM if a user's request is ambiguous or requires complex interpretation that goes beyond simple command dispatch. For example, "Plan a multi-step deployment process" might be sent to Fiedler before Grace starts issuing specific commands to Hopper.

## 3. Action Engine
- **MCP Server Capabilities:** Grace's Action Engine is a web server (e.g., using FastAPI or Flask) that serves the user interface and handles user interactions via WebSockets. It manages user sessions and maintains the state of the conversation for each connected user.
- **Tools Exposed:** Grace's tools are primarily for internal use by her own Imperator to manage the UI, rather than for other MADs to call.

```yaml
# Tool definitions for Grace V2 (Internal Use)

- tool: display_message
  description: "Displays a message to the user in the UI."
  parameters:
    - name: content
      type: string
      required: true
      description: "The message content to display. Can be plain text or Markdown."
    - name: message_type
      type: string
      required: false
      default: "info"
      enum: [info, error, success, warning]
      description: "The type of message, for styling purposes."

- tool: get_user_input
  description: "Prompts the user for input and waits for a response."
  parameters:
    - name: prompt_text
      type: string
      required: false
      description: "Optional text to display next to the input box."
  returns:
    type: string
    description: "The text entered by the user."

- tool: format_markdown
  description: "Renders a Markdown string into HTML for display in the UI."
  parameters:
    - name: markdown_text
      type: string
      required: true
  returns:
    type: string
    description: "The rendered HTML."

- tool: manage_session
  description: "Manages user session data (e.g., set, get, delete session variables)."
  parameters:
    - name: action
      type: string
      required: true
      enum: [get, set, delete]
    - name: key
      type: string
      required: true
    - name: value
      type: any
      required: false
  returns:
    type: any
    description: "The value from the session, or a status confirmation."

- tool: authenticate_user
  description: "Handles user authentication against a user database."
  parameters:
    - name: username
      type: string
      required: true
    - name: password
      type: string
      required: true
  returns:
    type: object
    schema:
      properties:
        authenticated: {type: boolean}
        session_id: {type: string}
  errors:
    - code: -34301
      message: "AUTHENTICATION_FAILED"

- tool: render_ui
  description: "Renders a specific UI component or template."
  parameters:
    - name: component_name
      type: string
      required: true
    - name: data
      type: object
      required: false
      description: "Data to pass to the component template."

- tool: handle_file_upload
  description: "Receives a file from the user and makes it available to Horace."
  parameters:
    - name: file_data
      type: binary
      required: true
    - name: file_name
      type: string
      required: true
    - name: destination_path
      type: string
      required: true
      description: "The path on the NAS where Horace should store the file."
  returns:
    type: object
    schema:
      properties:
        status: {type: string, const: "uploaded"}
        path: {type: string}
```
- **External System Integrations:**
  - **Web Browser:** The primary client of Grace is a human user's web browser.
- **Internal Operations:** None. Grace is entirely user-driven.

## 4. Interfaces
- **Conversation Participation Patterns:** Grace is the primary initiator of conversations within the ecosystem, acting on behalf of the user. She creates new conversations with specialist MADs for each new user task.
- **Dependencies on Other MADs:**
  - **Rogers:** Grace depends on Rogers for all communication with the rest of the ecosystem. She is a client of the Conversation Bus.
  - **All other MADs:** Grace can potentially interact with any other MAD that exposes tools, as directed by the user. Her Imperator must have knowledge of the capabilities of all other MADs.
- **Data Contracts:**

```yaml
# User Session Schema (conceptual, stored server-side)
user_session_schema:
  type: object
  properties:
    session_id: {type: string}
    user_id: {type: string}
    authenticated: {type: boolean}
    active_conversations: {type: object, description: "Mapping of user task to Rogers conversation ID."}
    created_at: {type: string, format: date-time}
```

## 5. Data Management
- **Data Ownership:** Grace is the source of truth for user identity and session state.
- **Storage Requirements:**
  - **PostgreSQL:** A `grace` schema to store user accounts and potentially user preferences.
  - **In-memory Cache (e.g., Redis):** For storing active user session data for fast access.

```sql
CREATE SCHEMA grace;

CREATE TABLE grace.users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

## 6. Deployment
- **Container Requirements:**
  - **Base Image:** `python:3.11-slim`
  - **Python Libraries:** `Joshua_Communicator`, `fastapi`, `uvicorn`, `python-multipart` (for file uploads), `redis`
  - **Resources:**
    - **CPU:** 0.5 cores
    - **RAM:** 1024 MB
- **Configuration:**

| Variable | Description | Example Value |
|---|---|---|
| `JOSHUA_MAD_NAME` | Canonical name of this MAD. | `grace-v2` |
| `JOSHUA_ROGERS_URL` | WebSocket URL for Rogers. | `ws://rogers:8000/ws` |
| `GRACE_DATABASE_URL` | Connection string for PostgreSQL. | `postgresql://user:pass@postgres:8000/joshua` |
| `GRACE_REDIS_URL` | Connection string for Redis session store. | `redis://redis:8000` |
| `GRACE_SERVER_PORT` | Port for the web server to listen on. | `8080` |
| `GRACE_LPPM_MODEL_PATH` | Path to the trained LPPM model file. | `/models/lppm/grace_lppm_v2.onnx` |

- **Monitoring/Health Checks:** An HTTP endpoint `/health` that returns `200 OK` if the web server is running and can connect to Rogers, PostgreSQL, and Redis.

## 7. Testing Strategy
- **Unit Test Coverage:**
  - User authentication logic.
  - Session management functions.
  - Markdown to HTML rendering.
- **Integration Test Scenarios:**
  - **End-to-End Command:** A test using a browser automation tool (like Playwright) to log in, type a command (e.g., "list files in /"), and verify that Grace correctly calls Horace and displays the formatted file list in the UI.
  - **File Upload:** Automate uploading a file through the UI and verify that Grace correctly calls Horace to store the file on the NAS.
- **LPPM Accuracy Tests:**
  - Test LPPM on 1000-sample validation set
  - Verify >95% accuracy for common patterns
  - Verify correct fallback to Imperator for low-confidence requests
- **Latency Comparison:**
  - Measure P50, P95, P99 latency for LPPM fast path vs. Imperator reasoning
  - Target: LPPM fast path <50ms, Imperator path 500-2000ms

## 8. Example Workflows
### Scenario 1: User Lists Files
1.  **User:** Navigates to Grace's web UI, logs in, and types "List the files in the `/data` directory" into the chat input.
2.  **Grace (Web Server):** Sends the text to her Thinking Engine. The LPPM recognizes this common pattern with high confidence.
3.  **Grace's LPPM:** Directly outputs the tool call sequence: `[create_conversation(participants=['grace-v2', 'horace-v2']), send_message(to='horace-v2', tool='list_directory', params={'path': '/data'})]`. The Imperator is bypassed.
4.  **Grace -> Rogers:** Executes the sequence.
5.  **Horace:** Executes the command and sends a response back to the conversation containing a JSON array of file objects.
6.  **Grace:** Receives the JSON response from Horace.
7.  **Grace's Imperator:** (Takes over for formatting) Sees the JSON array. It decides to format this as a Markdown table for readability. It calls its internal `display_message` tool with the formatted table.
8.  **Grace (Web Server):** Pushes the Markdown content (rendered as HTML) to the user's browser via WebSocket, where it appears as a new message in the chat.

### Scenario 2: User Executes Code
1.  **User:** Types "Execute this python code: `print('Hello, Joshua')`"
2.  **Grace's LPPM:** Recognizes this pattern and directly maps it to a tool call sequence for Gates.
3.  **Grace -> Rogers:** Initiates a conversation with Gates and sends the request.
4.  **Gates:** Executes the code in a container and sends back a response: `{"stdout": "Hello, Joshua\n", "stderr": "", "exit_code": 0}`.
5.  **Grace's Imperator:** Receives the response. It formats a user-friendly message: "The code executed successfully. Here is the output:" followed by a Markdown code block containing "Hello, Joshua".
6.  **Grace (Web Server):** Pushes the formatted message to the user's UI.

---