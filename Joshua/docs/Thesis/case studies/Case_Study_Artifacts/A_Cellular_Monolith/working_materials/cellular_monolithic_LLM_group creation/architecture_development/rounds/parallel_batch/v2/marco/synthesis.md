# Marco V2 Architecture Specification

## 1. Overview
- **Purpose and Role:** Marco is the Web Explorer for the Joshua ecosystem. His purpose is to provide the ability to browse, interact with, and extract information from the public internet. Marco's role is to act as a remote-controlled, headless browser, translating high-level MAD requests (e.g., "find the latest news on topic X") into a series of low-level browser actions (navigate, click, type, scrape), and returning the results. He is the ecosystem's window to the web.
- **New in this Version:** This V2 specification introduces the Learned Prose-to-Process Mapper (LPPM) as a performance optimization. The LPPM provides a "fast path" for simple, single-step web actions like "go to this URL" or "get the text from this selector," translating them directly into browser tool calls to reduce latency. All V1 functionalities are preserved.

## 2. Thinking Engine
### 2.1 Imperator Configuration (V1+)
Marco's Imperator is configured to think like an expert web researcher and data scraper. It understands the structure of web pages (DOM), network requests, and how to sequence actions to achieve a goal.
  - **System Prompt Core Directives:** "You are Marco, the Web Explorer. Your purpose is to navigate the internet to find and retrieve information. You operate a headless Chromium browser. When given a task, such as 'Find the price of product Y on example.com', you must break it down into a sequence of browser actions: `navigate` to the site, `type` the product name into the search bar, `click` the search button, `wait_for` the results page, and then `snapshot` the relevant part of the DOM to extract the price. You are methodical and persistent, handling things like cookie banners and dialogs."
  - **Example Reasoning:** A request from Lovelace, "Get me the current top 5 headlines from bbc.com/news," would cause Marco's Imperator to create a plan:
    1.  `navigate(url='https://www.bbc.com/news')`
    2.  `wait_for(selector='h3')` to ensure the headlines have loaded.
    3.  `snapshot(selector='h3', max_items=5)` to get the text of the first five H3 elements, which are likely headlines.
    4.  Return the extracted text.

### 2.2 LPPM Integration (V2+)
- **LPPM Integration (V2+):** Marco's LPPM is a distilled transformer model trained on historical conversation logs from V1 deployments. It learns to recognize common request patterns and map them directly to tool call sequences.
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
    - "Navigate to https://example.com" → `navigate(url='https://example.com')`
    - "Click the button with id 'submit-btn'" → `click(selector='#submit-btn')`
    - "Get the text of all h2 elements" → `snapshot(selector='h2')`
    - "Type 'hello world' into the search bar" → `type(selector='input[name=q]', text='hello world')`
  - **Training Loop:**
    - Initial training: 24 hours on 100K V1 logs
    - Continuous learning: Weekly retraining with new V1/V2 production data
    - Validation: 95% accuracy on held-out test set before deployment

- **DTR Integration (V3+):** Not applicable in V2.
- **CET Integration (V4+):** Not applicable in V2.
- **Consulting LLM Usage Patterns:** Marco might consult Fiedler with a powerful vision-capable LLM (like GPT-4o). It could send a screenshot from `take_screenshot` and ask, "Based on this screenshot, what is the CSS selector for the main search input field?" This offloads complex visual DOM analysis.

## 3. Action Engine
- **MCP Server Capabilities:** Marco's MCP server manages a pool of headless Chromium browser instances (e.g., using Playwright or Puppeteer). Each incoming request is assigned to a browser instance to execute. The server translates the tool calls into the corresponding browser automation library commands.
- **Tools Exposed:**

```yaml
# Tool definitions for Marco V2

- tool: navigate
  description: "Navigates the browser to a specific URL."
  parameters:
    - name: url
      type: string
      required: true
      description: "The URL to load."
  returns:
    type: object
    schema:
      properties:
        status: {type: string, const: "success"}
        final_url: {type: string}

- tool: click
  description: "Clicks on an element specified by a CSS selector."
  parameters:
    - name: selector
      type: string
      required: true
      description: "The CSS selector of the element to click."
  returns:
    type: object
    schema:
      properties:
        status: {type: string, const: "clicked"}
  errors:
    - code: -34501
      message: "ELEMENT_NOT_FOUND"

- tool: type
  description: "Types text into an element, like an input field."
  parameters:
    - name: selector
      type: string
      required: true
      description: "The CSS selector of the input element."
    - name: text
      type: string
      required: true
      description: "The text to type."
  returns:
    type: object
    schema:
      properties:
        status: {type: string, const: "typed"}
  errors:
    - code: -34501
      message: "ELEMENT_NOT_FOUND"

- tool: snapshot
  description: "Extracts information (text, attributes) from the current page's DOM."
  parameters:
    - name: selector
      type: string
      required: true
      description: "The CSS selector for the elements to capture."
    - name: attribute
      type: string
      required: false
      description: "If specified, returns this attribute's value (e.g., 'href') instead of the text content."
  returns:
    type: object
    schema:
      properties:
        items:
          type: array
          items:
            type: string
            description: "A list of the text content or attribute values of the matched elements."

- tool: take_screenshot
  description: "Takes a screenshot of the current page and saves it via Horace."
  parameters:
    - name: path
      type: string
      required: true
      description: "The path in Horace to save the PNG screenshot to."
    - name: full_page
      type: boolean
      required: false
      default: false
      description: "Whether to capture the full scrollable page."
  returns:
    type: object
    schema:
      properties:
        path: {type: string}
        status: {type: string, const: "saved"}

- tool: evaluate
  description: "Executes a snippet of JavaScript in the context of the page."
  parameters:
    - name: script
      type: string
      required: true
      description: "The JavaScript code to execute. It must return a serializable value."
  returns:
    type: any
    description: "The result of the JavaScript execution."

- tool: wait_for
  description: "Waits for a specific condition to be met on the page."
  parameters:
    - name: event
      type: string
      required: true
      enum: [load, networkidle, selector]
      description: "The event to wait for."
    - name: selector
      type: string
      required: false
      description: "The CSS selector to wait for if event is 'selector'."
    - name: timeout_ms
      type: integer
      required: false
      default: 30000
  returns:
    type: object
    schema:
      properties:
        status: {type: string, const: "completed"}
  errors:
    - code: -34502
      message: "TIMEOUT_ERROR"

- tool: handle_dialog
  description: "Handles a JavaScript dialog (alert, confirm, prompt)."
  parameters:
    - name: action
      type: string
      required: true
      enum: [accept, dismiss]
    - name: prompt_text
      type: string
      required: false
      description: "Text to enter for prompt dialogs."
  returns:
    type: object
    schema:
      properties:
        status: {type: string, const: "handled"}
```
- **External System Integrations:**
  - **Chromium:** Marco depends on a local or containerized Chromium browser installation.
  - **Internet:** Marco makes outbound network requests to the public internet.
- **Internal Operations:** Manages a browser context (session), including cookies, local storage, and the current page URL.

## 4. Interfaces
- **Conversation Participation Patterns:** Marco is a service provider, joining conversations to perform web browsing tasks for other MADs.
- **Dependencies on Other MADs:**
  - **Rogers:** For all communication.
  - **Horace:** To save artifacts like screenshots or downloaded files.
  - **Fiedler:** (Optional) To ask for help analyzing a complex webpage from a screenshot.
- **Data Contracts:** None, as Marco primarily deals with unstructured web data.

## 5. Data Management
- **Data Ownership:** Marco does not own any persistent data. He manages the ephemeral state of the browser session for the duration of a task.
- **Storage Requirements:** Marco requires temporary local disk space within his container for the browser to use as a cache and for temporary downloads.

## 6. Deployment
- **Container Requirements:**
  - **Base Image:** A specialized image that includes Chromium and browser automation libraries, e.g., `mcr.microsoft.com/playwright/python:v1.44.0-jammy`.
  - **Python Libraries:** `Joshua_Communicator`
  - **Resources:**
    - **CPU:** 1 core. Browser rendering can be CPU-intensive.
    - **RAM:** 2560 MB. Headless browsers are memory-hungry.
- **Configuration:**

| Variable | Description | Example Value |
|---|---|---|
| `JOSHUA_MAD_NAME` | Canonical name of this MAD. | `marco-v2` |
| `JOSHUA_ROGERS_URL` | WebSocket URL for Rogers. | `ws://rogers:8000/ws` |
| `MARCO_LPPM_MODEL_PATH` | Path to the trained LPPM model file. | `/models/lppm/marco_lppm_v2.onnx` |

- **Monitoring/Health Checks:** An HTTP endpoint `/health` that returns `200 OK` if the MCP server can successfully launch and connect to a headless browser instance.

## 7. Testing Strategy
- **Unit Test Coverage:**
  - Test wrappers for each browser automation command.
  - CSS selector validation logic.
- **Integration Test Scenarios:**
  - **Login Flow:** Test a multi-step process of navigating to a login page, typing a username/password, clicking submit, and verifying that the resulting page contains expected text (e.g., "Welcome, user").
  - **Data Scraping:** Test navigating to a known e-commerce product page and successfully extracting the product name and price using `snapshot`.
  - **Screenshot and Save:** Test `take_screenshot` and verify that the resulting PNG file is correctly saved in Horace.
- **LPPM Accuracy Tests:**
  - Test LPPM on 1000-sample validation set
  - Verify >95% accuracy for common patterns
  - Verify correct fallback to Imperator for low-confidence requests
- **Latency Comparison:**
  - Measure P50, P95, P99 latency for LPPM fast path vs. Imperator reasoning
  - Target: LPPM fast path <50ms, Imperator path 500-2000ms

## 8. Example Workflows
### Scenario 1: Basic Web Search
- **Goal:** Grace asks Marco to find the weather in a city.
1.  **Grace -> Marco:** Sends a request: "Search Google for 'weather in London'"
2.  **Marco's Imperator:** Devises a plan:
    a. `navigate(url='https://www.google.com')`
    b. `wait_for(selector='textarea[name=q]')`
    c. `type(selector='textarea[name=q]', text='weather in London')`
    d. `click(selector='input[type=submit]')` (or simulate pressing Enter)
    e. `wait_for(selector='#wob_tm')` (the selector for the temperature element)
    f. `snapshot(selector='#wob_tm')` to get the temperature.
    g. `snapshot(selector='#wob_dc')` to get the description (e.g., "Cloudy").
3.  **Marco's Action Engine:** Executes each step in sequence.
4.  **Marco -> Grace:** Returns a structured response: `{"temperature": "15", "description": "Cloudy"}`. Grace then formats this for the user.

### Scenario 2: Submitting a Form and Downloading a File
- **Goal:** Hopper needs to download a report from an internal tool's web interface.
1.  **Hopper -> Marco:** Sends request: "Log into `http://reports.internal/`, navigate to the 'Daily Summary' page, and download the CSV for today's date."
2.  **Marco's Imperator:** Creates a plan:
    a. `navigate(url='http://reports.internal/login')`
    b. `type(selector='#username', text='automation_user')`
    c. Get password from Turing: `type(selector='#password', text=turing.get_secret('report_system_pw'))`
    d. `click(selector='#login_button')`
    e. `wait_for(event='load')`
    f. `click(selector='a[href="/reports/daily-summary"]')`
    g. This next step is complex. The Imperator knows clicking the download link will trigger a download. It needs to coordinate with Horace.
    h. Tell Horace to expect a file.
    i. `click(selector='a.download-csv')`
    j. The browser automation library intercepts the download, and Marco's Action Engine streams the data to Horace via `Horace.write_file`.
3.  **Marco -> Hopper:** Returns a success response: `{"status": "download_complete", "path": "/downloads/daily_summary_2025-10-26.csv"}`.

---