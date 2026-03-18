# Gates V1 Architecture Specification

## 1. Overview
- **Purpose and Role:** Gates is the Code Execution Engine for the Joshua ecosystem. His purpose is to provide a secure and isolated environment for executing arbitrary code in various languages. Gates' role is to act as a sandboxed runtime, accepting code from other MADs (like Hopper or Grace), running it within a disposable Docker container, and streaming back the output, logs, and exit status. He ensures that code execution does not compromise the stability or security of the core ecosystem.
- **New in this Version:** This is the initial V1 specification for Gates. It establishes the foundational capability to execute code within ephemeral Docker containers. This version is strictly V1, relying on its Imperator to manage execution requests.

## 2. Thinking Engine
- **Imperator Configuration (V1+):** Gates' Imperator is configured to think like a DevOps engineer focused on containerization and secure execution. It reasons about runtime environments, resource limits, and the lifecycle of execution containers.
  - **System Prompt Core Directives:** "You are Gates, the Code Execution Engine. Your purpose is to run code safely in isolated Docker containers. When you receive an `execute_code` request, you must select the correct base image for the specified language, create a new container, inject the code, execute it, and stream back stdout and stderr. You are responsible for enforcing resource limits (CPU, memory) and timeouts to prevent runaway processes. After execution, you must always destroy the container to ensure a clean slate for the next task. Security and isolation are your top priorities."
  - **Example Reasoning:** A request from Hopper `execute_code(language='python', code='...')` causes the Imperator to plan: "1. Language is Python. Select the `python:3.11-slim` image. 2. Create a Docker container from this image. 3. Copy the user's code into a `/app/main.py` file inside the container. 4. Run the command `python /app/main.py`. 5. Attach to the container's log stream and forward it to the requesting MAD. 6. On completion, record the exit code. 7. Destroy the container. 8. Return the final result."
- **LPPM Integration (V2+):** Not applicable in V1.
- **DTR Integration (V3+):** Not applicable in V1.
- **CET Integration (V4+):** Not applicable in V1.
- **Consulting LLM Usage Patterns:** Gates does not use consulting LLMs in V1.

## 3. Action Engine
- **MCP Server Capabilities:** Gates' MCP server manages interactions with the host's Docker daemon via the Docker SDK. It maintains a state of active executions and handles the asynchronous nature of code execution, streaming logs back to the caller over the conversation bus.
- **Tools Exposed:**

```yaml
# Tool definitions for Gates V1

- tool: execute_code
  description: "Executes a block of code in a secure, isolated container."
  parameters:
    - name: language
      type: string
      required: true
      enum: [python, javascript, bash]
      description: "The programming language of the code."
    - name: code
      type: string
      required: true
      description: "The source code to execute."
    - name: timeout_seconds
      type: integer
      required: false
      default: 60
      description: "Maximum execution time before the process is killed."
  returns:
    type: object
    schema:
      properties:
        execution_id: {type: string, description: "A unique ID for this execution."}
        status: {type: string, const: "started"}
  # Note: The full result is streamed back asynchronously in separate messages.

- tool: create_environment
  description: "Pre-builds a custom Docker image with specified dependencies. Returns an image tag."
  parameters:
    - name: name
      type: string
      required: true
      description: "A name for the custom environment."
    - name: dockerfile
      type: string
      required: true
      description: "The content of the Dockerfile to build."
  returns:
    type: object
    schema:
      properties:
        image_tag: {type: string}
        status: {type: string, const: "building"}
  errors:
    - code: -34601
      message: "BUILD_FAILED"

- tool: destroy_environment
  description: "Deletes a custom environment image."
  parameters:
    - name: image_tag
      type: string
      required: true
  returns:
    type: object
    schema:
      properties:
        status: {type: string, const: "deleted"}

- tool: list_environments
  description: "Lists all available custom environments."
  parameters: []
  returns:
    type: object
    schema:
      properties:
        environments: {type: array, items: {type: string}}

- tool: get_execution_status
  description: "Checks the status of an ongoing or completed execution."
  parameters:
    - name: execution_id
      type: string
      required: true
  returns:
    type: object
    schema:
      properties:
        status: {type: string, enum: [running, completed, failed, timeout]}
        exit_code: {type: integer}
  errors:
    - code: -34602
      message: "EXECUTION_NOT_FOUND"

- tool: cancel_execution
  description: "Forcibly stops a running execution."
  parameters:
    - name: execution_id
      type: string
      required: true
  returns:
    type: object
    schema:
      properties:
        status: {type: string, const: "cancelled"}
  errors:
    - code: -34602
      message: "EXECUTION_NOT_FOUND"

- tool: get_logs
  description: "Retrieves the full, collated logs for a completed execution."
  parameters:
    - name: execution_id
      type: string
      required: true
  returns:
    type: object
    schema:
      properties:
        stdout: {type: string}
        stderr: {type: string}
  errors:
    - code: -34602
      message: "EXECUTION_NOT_FOUND"
```
- **External System Integrations:**
  - **Docker Runtime:** Gates depends on a running Docker daemon on its host machine, accessed via a Unix socket.
- **Internal Operations:** Manages the lifecycle of Docker containers for each execution.

## 4. Interfaces
- **Conversation Participation Patterns:** Gates is a service provider. It joins conversations to execute code for other MADs. It will also send multiple messages back into the conversation for a single `execute_code` request (e.g., log streams, final result).
- **Dependencies on Other MADs:**
  - **Rogers:** For all communication.
- **Data Contracts:**

```yaml
# Execution Log Stream Message Schema
log_stream_schema:
  type: object
  properties:
    jsonrpc: {type: string, const: "2.0"}
    method: {type: string, const: "execution_log"}
    params:
      type: object
      properties:
        execution_id: {type: string}
        stream: {type: string, enum: [stdout, stderr]}
        line: {type: string}

# Execution Result Message Schema
execution_result_schema:
  type: object
  properties:
    jsonrpc: {type: string, const: "2.0"}
    method: {type: string, const: "execution_result"}
    params:
      type: object
      properties:
        execution_id: {type: string}
        status: {type: string, enum: [completed, failed, timeout]}
        exit_code: {type: integer}
        stdout: {type: string}
        stderr: {type: string}
```

## 5. Data Management
- **Data Ownership:** Gates does not own any persistent data. It manages the ephemeral state of running code executions. Execution logs are stored temporarily until retrieved by `get_logs`.
- **Storage Requirements:** Requires local disk space for Docker images and container layers.

## 6. Deployment
- **Container Requirements:**
  - **Base Image:** `python:3.11-slim`
  - **Python Libraries:** `Joshua_Communicator`, `docker`
  - **Volume Mounts:** Requires the Docker daemon socket to be mounted into the container: `-v /var/run/docker.sock:/var/run/docker.sock`.
  - **Privileges:** The container must run with a user that has permission to access the Docker socket.
  - **Resources:**
    - **CPU:** 0.5 cores (the executed code runs in separate containers).
    - **RAM:** 512 MB
- **Configuration:**

| Variable | Description | Example Value |
|---|---|---|
| `JOSHUA_MAD_NAME` | Canonical name of this MAD. | `gates-v1` |
| `JOSHUA_ROGERS_URL` | WebSocket URL for Rogers. | `ws://rogers:8000/ws` |
| `GATES_DOCKER_SOCKET_PATH` | Path to the Docker socket inside the container. | `/var/run/docker.sock` |

- **Monitoring/Health Checks:** An HTTP endpoint `/health` that returns `200 OK` if the MAD can successfully communicate with the Docker daemon (e.g., by running `docker info`).

## 7. Testing Strategy
- **Unit Test Coverage:**
  - Logic for selecting the correct Docker image based on language.
  - Parsing of Docker log streams.
- **Integration Test Scenarios:**
  - **Successful Python Execution:** Send a simple Python script (`print('hello')`) and verify that the `execution_log` message contains "hello" on stdout and the final `execution_result` has an exit code of 0.
  - **Execution Timeout:** Send a script that runs an infinite loop (`while True: pass`) with a short timeout (e.g., 2 seconds). Verify that the execution is killed and the final status is 'timeout'.
  - **Error Execution:** Send a script with a syntax error. Verify that the final status is 'failed', the exit code is non-zero, and stderr contains the error message.

## 8. Example Workflows
### Scenario 1: Simple Code Execution from Grace
1.  **User (via Grace):** "Gates, run this python code: `for i in range(3): print(f'Line {i}')`"
2.  **Grace -> Gates:** Sends `execute_code(language='python', code='...')`.
3.  **Gates -> Grace:** Immediately responds with `{ "execution_id": "exec-123", "status": "started" }`.
4.  **Gates' Action Engine:** Starts a `python:3.11-slim` container and runs the code.
5.  **Gates -> Grace (stream 1):** Sends a log message: `{ "method": "execution_log", "params": { "execution_id": "exec-123", "stream": "stdout", "line": "Line 0" } }`.
6.  **Gates -> Grace (stream 2):** Sends `{ ... "line": "Line 1" }`.
7.  **Gates -> Grace (stream 3):** Sends `{ ... "line": "Line 2" }`.
8.  **Gates:** The container exits. Gates destroys it.
9.  **Gates -> Grace (final result):** Sends `{ "method": "execution_result", "params": { "execution_id": "exec-123", "status": "completed", "exit_code": 0, ... } }`.
10. **Grace:** Formats the streamed logs and the final result for the user.

### Scenario 2: Hopper Runs Unit Tests in a Custom Environment
1.  **Hopper:** Needs to run tests that require `pytest` and `requests`.
2.  **Hopper -> Gates:** Calls `create_environment` with a Dockerfile: `FROM python:3.11-slim\nRUN pip install pytest requests`.
3.  **Gates:** Builds the image and returns `{ "image_tag": "custom-env-abc", "status": "building" }`. (A subsequent message will confirm completion).
4.  **Hopper -> Horace:** Writes the test code to `/tests/test_api.py`.
5.  **Hopper -> Gates:** Calls `execute_code` using the custom environment. This requires a V1.1 feature to specify the image, or a convention where the code-to-run can access Horace. Let's assume the code includes logic to fetch files from Horace.
6.  **Hopper -> Gates:** Calls `execute_code` with `language='python'` (using the custom image) and code that uses Horace's client library to fetch `/tests/test_api.py` and then runs `pytest`.
7.  **Gates:** Runs the test suite, streams back the `pytest` output, and returns the final exit code, which tells Hopper if the tests passed.
8.  **Hopper -> Gates:** Calls `destroy_environment(image_tag='custom-env-abc')` to clean up.

---