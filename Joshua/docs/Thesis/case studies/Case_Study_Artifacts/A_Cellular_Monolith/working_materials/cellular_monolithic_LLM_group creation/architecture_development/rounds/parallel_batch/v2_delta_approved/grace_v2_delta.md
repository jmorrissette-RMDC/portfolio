# === GRACE V2 DELTA ===
# Grace V2 Architecture Specification

**This document assumes the approved V1 architecture as a baseline. It describes ONLY the deltas required to add V2 capabilities.**

## 1. Overview
- **New in this Version:** V2 adds the Learned Prose-to-Process Mapper (LPPM) as a performance optimization layer in the Thinking Engine. The LPPM recognizes common request patterns and maps them directly to tool calls, bypassing full Imperator reasoning for significant speed gains. All V1 functionality is preserved unchanged.

## 2. Thinking Engine
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

## 6. Deployment (Changes from V1)
- **Container Requirements - Resources (UPDATED):**
  - **RAM:** 1536 MB (increased from 1024 MB)
    - V1 baseline: 1024 MB
    - LPPM model: +512 MB
    - Total V2: 1536 MB

- **Configuration (NEW variable):**

| Variable | Description | Example Value |
|---|---|---|
| `GRACE_LPPM_MODEL_PATH` | Path to the trained LPPM model file. | `/models/lppm/grace_lppm_v2.onnx` |

## 7. Testing Strategy (V2 Additions)
- **LPPM Accuracy Tests:**
  - Test LPPM on 1000-sample validation set
  - Verify >95% accuracy for common patterns
  - Verify correct fallback to Imperator for low-confidence requests

- **Latency Comparison:**
  - Measure P50, P95, P99 latency for LPPM fast path vs. Imperator reasoning
  - Target: LPPM fast path <50ms, Imperator path 500-2000ms

## 8. Example Workflows (V2 Enhancements)
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
