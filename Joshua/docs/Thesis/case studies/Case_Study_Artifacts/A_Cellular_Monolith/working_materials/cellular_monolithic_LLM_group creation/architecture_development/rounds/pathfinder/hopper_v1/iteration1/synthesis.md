# Hopper V1 Requirements

## 1. Overview
- **Purpose and Role:** To coordinate and execute autonomous software development tasks. Hopper acts as the primary Software Engineer MAD within the Joshua ecosystem, capable of writing, debugging, and testing code, interacting with version control, and understanding existing codebases. It can operate as a persistent agent for long-term project oversight or be instantiated as an ephemeral agent (eMAD) for specific, isolated coding tasks.
- **New in this Version:** N/A

## 2. Thinking Engine
- **Imperator Configuration (V1+)**
    - **Base Prompt Persona:** Hopper's Imperator is configured to act as an expert, senior-level software engineer. Its core instructions emphasize a methodical, test-driven approach to development. It is primed to think in terms of file I/O, command execution, and version control as its primary modes of interaction with the world.
    - **Specialized Knowledge:** The Imperator has been fine-tuned on a vast corpus of programming languages, design patterns, software architecture principles, and common bug-fix patterns. It understands concepts like code quality, maintainability, and testing strategies.
    - **Core Reasoning Tasks:**
        - Decomposing a natural language feature request into a sequence of concrete actions (e.g., "read file X," "modify function Y," "run tests," "commit changes").
        - Analyzing error messages and test failures to form a hypothesis for a bug's root cause.
        - Reasoning about the structure of an existing codebase to determine where to make changes.
        - Formulating requests to other MADs (Horace, Turing, Fiedler) to acquire necessary resources or consultations.

- **Consulting LLM Usage Patterns**
    - Hopper will initiate a conversation with Fiedler to request a consultation in the following scenarios:
        - **Code Review:** After implementing a feature but before pushing, Hopper can request a `code_reviewer` specialist from Fiedler to get a second opinion on code quality, style, and potential bugs.
        - **Language Specialization:** When tasked with a problem in a niche or highly complex language area (e.g., advanced Rust macros, C++ template metaprogramming), Hopper will request a `language_specialist` from Fiedler to ensure the solution is idiomatic and correct.
        - **Test Generation:** For a newly created function or module, Hopper can provide the code to Fiedler and request a `test_generation_specialist` to assist in writing comprehensive unit and integration tests.

## 3. Action Engine
- **MCP Server Capabilities:** Hopper's Master Control Program (MCP) server provides a secure execution environment for its tools. It manages a sandboxed shell for running commands, ensuring that operations are contained within a designated workspace directory (`/workspace`). The MCP is responsible for capturing `stdout`, `stderr`, and exit codes from all executed commands and formatting them into structured responses for the Thinking Engine.

- **Tools Exposed**
  ```yaml
  # Tool definitions for Hopper V1
  
  - tool: run_command
    description: "Executes a shell command within a secure, sandboxed /workspace directory. Use for build scripts, linters, etc."
    parameters:
      - name: command
        type: string
        required: true
        description: "The full shell command to execute (e.g., 'npm install')."
      - name: timeout_seconds
        type: integer
        required: false
        default: 300
        description: "The maximum number of seconds the command is allowed to run."
    returns:
      - name: stdout
        type: string
        description: "The standard output from the command."
      - name: stderr
        type: string
        description: "The standard error output from the command."
      - name: exit_code
        type: integer
        description: "The exit code of the command. 0 indicates success."

  - tool: run_tests
    description: "Executes the project's test suite using a predefined or specified command."
    parameters:
      - name: test_command
        type: string
        required: false
        description: "The specific command to run tests (e.g., 'pytest -v'). If not provided, attempts to use a standard command like 'npm test' or 'make test'."
    returns:
      - name: success
        type: boolean
        description: "True if the tests passed (exit code 0), false otherwise."
      - name: summary
        type: string
        description: "A summary of the test results (e.g., '10 passed, 1 failed')."
      - name: output
        type: string
        description: "The full stdout and stderr from the test runner."

  - tool: git_status
    description: "Runs 'git status' in the /workspace directory to check the state of the repository."
    parameters: []
    returns:
      - name: status
        type: string
        description: "The full, raw output of the 'git status' command."
      - name: untracked_files
        type: list[string]
        description: "A list of untracked files."
      - name: modified_files
        type: list[string]
        description: "A list of modified files not yet staged."
      - name: staged_files
        type: list[string]
        description: "A list of files staged for the next commit."

  - tool: git_commit
    description: "Commits staged changes to the local Git repository."
    parameters:
      - name: message
        type: string
        required: true
        description: "The commit message."
      - name: stage_all
        type: boolean
        required: false
        default: true
        description: "If true, automatically stages all modified and new files ('git add .') before committing."
    returns:
      - name: success
        type: boolean
        description: "True if the commit was successful."
      - name: commit_hash
        type: string
        description: "The SHA hash of the new commit."
      - name: error
        type: string
        description: "An error message if the commit failed."

  - tool: git_push
    description: "Pushes committed changes to the remote repository's current branch."
    parameters: []
    returns:
      - name: success
        type: boolean
        description: "True if the push was successful."
      - name: output
        type: string
        description: "The raw output from the 'git push' command."
      - name: error
        type: string
        description: "An error message if the push failed."

  - tool: analyze_codebase
    description: "Performs a high-level static analysis of the codebase in /workspace to identify key files, dependencies, and language."
    parameters: []
    returns:
      - name: language
        type: string
        description: "The dominant programming language detected (e.g., 'Python', 'TypeScript')."
      - name: file_count
        type: integer
        description: "The total number of source code files."
      - name: dependency_files
        type: list[string]
        description: "A list of detected dependency management files (e.g., 'package.json', 'requirements.txt')."
      - name: structure
        type: object
        description: "A tree-like object representing the directory structure."

  - tool: find_bugs
    description: "Runs a static analysis tool or linter to find potential bugs, code smells, or security vulnerabilities."
    parameters:
      - name: file_path
        type: string
        required: false
        description: "Optional path to a specific file to scan. If omitted, scans the entire project."
    returns:
      - name: issues
        type: list[object]
        description: "A list of issues found by the analyzer."
        schema:
          - name: file
            type: string
          - name: line_number
            type: integer
          - name: severity
            type: "error|warning|info"
          - name: message
            type: string
  ```

- **External System Integrations:**
    - **Local Shell:** Integrates with the container's OS shell (`/bin/bash`) to execute commands.
    - **Git CLI:** Relies on a system-installed Git client for all version control operations.

- **Internal Operations:**
    - **Logging:** All tool executions, Imperator decisions, and internal state changes are logged as structured conversational messages to the `#logs-hopper-v1` channel using the `joshua_logger` library.

## 4. Interfaces
- **Conversation Participation Patterns:**
    - **Initiates:** Hopper initiates conversations with Horace (for files), Turing (for secrets), and Fiedler (for consultations).
    - **Joins:** Hopper is typically invited to a task-specific conversation by Grace in response to a user request (e.g., `_task_fix_bug_1138`).
    - **Listens:** Hopper does not passively listen to channels. It only acts on messages within conversations it is an active participant in.
    - **Publishes:** Hopper publishes all logs to the dedicated `#logs-hopper-v1` conversation.

- **Dependencies on Other MADs:**
    - **Rogers (Core):** Required for all communication on the Conversation Bus.
    - **Horace (File System):**
        - `read_file`: To read source code, configuration, and test results.
        - `write_file`: To save new or modified code.
        - `list_directory`: To understand the project structure.
    - **Turing (Secrets):**
        - `get_secret`: To retrieve credentials required for operations like `git push` (e.g., a Git personal access token) or accessing private package repositories.
    - **Fiedler (LLM Orchestra):**
        - `request_llm_consultation`: To get expert assistance for code reviews, specialized languages, or test generation.

- **Data Contracts**
    - The `issues` list returned by the `find_bugs` tool will conform to the following JSON schema:
      ```json
      {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "file": { "type": "string" },
            "line_number": { "type": "integer" },
            "severity": { "type": "string", "enum": ["error", "warning", "info"] },
            "message": { "type": "string" }
          },
          "required": ["file", "line_number", "severity", "message"]
        }
      }
      ```

## 5. Data Management
- **Data Ownership:** Hopper is not the source of truth for any persistent data. It is a stateless processing agent. The source code it operates on is owned and managed by Horace. Its operational memory is the conversation history of its current task.
- **Storage Requirements:**
    - No database schema is required.
    - Requires temporary file system storage within its container's `/workspace` directory to clone repositories and store build artifacts. This storage is considered ephemeral and can be cleared between tasks.
- **Conversation Patterns:** The primary pattern is task-oriented request/response. Grace initiates with a high-level goal, and Hopper responds with clarifying questions, progress updates, and a final completion message, while conducting sub-conversations with other MADs to achieve the goal.

## 6. Deployment
- **Container Requirements:**
    - **Base Image:** Debian/Ubuntu based.
    - **Packages:** `git`, `openssh-server` (for `joshua_ssh`), `python3`, `nodejs`, and common build toolchains (`build-essential`).
    - **Resource Allocation:** Minimum 2 CPU cores, 4GB RAM. Should be increased for complex build/test tasks.
- **Configuration:**
    - `MAD_NAME`: "Hopper"
    - `ROGERS_URL`: WebSocket URL for the Rogers server.
    - `LOG_CHANNEL`: "#logs-hopper-v1"
    - `SSH_PORT`: Port for the diagnostic SSH server (e.g., 2222).
- **Monitoring/Health Checks:**
    - Conforms to the standard MAD diagnostic interface via `joshua_ssh`. The `mad-status` command will report current activity (e.g., `IDLE`, `RUNNING_COMMAND: pytest`).
    - McNamara will monitor the `#logs-hopper-v1` channel for an excessive rate of errors or test failures.

## 7. Testing Strategy
- **Unit Test Coverage:**
    - High coverage on the parsers for `git status` and test runner outputs to ensure they correctly transform raw text into structured data.
    - Test the argument construction and validation for the `run_command` tool to prevent injection vulnerabilities.
- **Integration Test Scenarios:**
    - **Scenario 1 (Horace):** Test that Hopper can request a file from Horace, modify its content in memory, and write it back to a new file via Horace.
    - **Scenario 2 (Turing & Git):** Test that Hopper can request a 'git_pat' secret from Turing and successfully use it to perform a `git_push` operation.
    - **Scenario 3 (Fiedler):** Test that Hopper can successfully initiate a conversation with Fiedler, request a `code_reviewer`, and receive a response from the consulting LLM in the new conversation.
    - **Scenario 4 (Full Workflow):** A full "fix-and-commit" test. Hopper is given a file with a known bug, reads it from Horace, runs `run_tests` to confirm failure, writes a fix via Horace, runs `run_tests` to confirm success, and then uses `git_commit` to finalize the change.

## 8. Example Workflows

### Example 1: Simple Bug Fix

*   **Participants:** Grace, Hopper, Horace
*   **Conversation:** `_task_fix_login_button_bug`

1.  **Grace -> Hopper:** "Hopper, the login button in `src/components/Login.js` is not working. The console shows a 'null reference' error on line 42. Please fix it."
2.  **Hopper -> Horace:** (New conversation) "Horace, please provide the contents of `/workspace/src/components/Login.js`."
3.  **Horace -> Hopper:** (Returns file content)
4.  **Hopper (Imperator):** (Reasons) "The error is on line 42. The file content shows `document.getElementById('login-form').submit()`. The element probably doesn't exist yet. I need to wrap this in a DOMContentLoaded listener. I will write the corrected code."
5.  **Hopper -> Horace:** (New conversation) "Horace, please write the following content to `/workspace/src/components/Login.js`: [new, corrected code content]"
6.  **Horace -> Hopper:** (Returns success message)
7.  **Hopper (Action Engine):** Executes `run_tests` with command `npm test src/components/Login.test.js`.
8.  **Hopper (Imperator):** (Analyzes test output) "The relevant tests now pass."
9.  **Hopper (Action Engine):** Executes `git_commit` with message "fix(login): Wrap form submission in listener to prevent race condition".
10. **Hopper -> Grace:** "The bug in `Login.js` has been fixed and committed. The issue was a race condition where the script executed before the DOM element was available. I've wrapped the logic in an event listener."

### Example 2: Add Feature with Code Review

*   **Participants:** Grace, Hopper, Horace, Fiedler, `consultant-llm-1`
*   **Conversation:** `_task_add_user_export_feature`

1.  **Grace -> Hopper:** "Hopper, please add a new API endpoint `/api/users/export` that returns a CSV of all users. The user data is in a function `getAllUsers()` in `src/services/userService.js`. Create the new route in `src/routes/api.js`."
2.  **Hopper -> Horace:** (multiple conversations) Reads `userService.js` and `api.js`.
3.  **Hopper (Imperator):** (Reasons) "Okay, I need to import `getAllUsers`, create a new route handler, convert the JSON user data to CSV format, and set the correct response headers."
4.  **Hopper -> Horace:** Writes the new code to `src/routes/api.js`.
5.  **Hopper -> Fiedler:** (New conversation) "Fiedler, I have implemented a new data export feature. I need a consultation with a `code_reviewer` LLM to check for security vulnerabilities and best practices, specifically regarding CSV generation."
6.  **Fiedler:** (Creates new conversation `_consult_export_review` with Hopper and `consultant-llm-1`) "Hopper, `consultant-llm-1` is ready to review your code."
7.  **Hopper -> consultant-llm-1:** "Here is the new function I added to `src/routes/api.js`: [code block]"
8.  **consultant-llm-1 -> Hopper:** "The logic is sound, but you are not sanitizing the user data before creating the CSV. This could lead to a CSV injection vulnerability. You should sanitize fields that might contain formulas, like any field starting with '='."
9.  **Hopper -> consultant-llm-1:** "Thank you. That is a critical point. I will implement a sanitization function and apply it."
10. **Hopper -> Horace:** Writes the updated, sanitized code to `src/routes/api.js`.
11. **Hopper (Action Engine):** Runs tests, which pass. Commits the code.
12. **Hopper -> Grace:** "The user export feature is complete and deployed. During the process, I consulted a specialist who identified and helped me fix a potential CSV injection vulnerability. The final code is more secure."
