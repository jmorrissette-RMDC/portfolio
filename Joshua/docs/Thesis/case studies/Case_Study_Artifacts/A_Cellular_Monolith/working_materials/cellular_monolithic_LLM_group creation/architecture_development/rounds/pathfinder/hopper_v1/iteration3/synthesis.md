# Hopper V1 Requirements

## 1. Overview
- **Purpose and Role:** To coordinate and execute autonomous software development tasks. Hopper acts as the primary Software Engineer MAD within the Joshua ecosystem, capable of writing, debugging, and testing code, interacting with version control, and understanding existing codebases. It can operate as a persistent agent for long-term project oversight or be instantiated as an ephemeral agent (eMAD) for specific, isolated coding tasks.
- **New in this Version:** N/A - Initial V1 baseline implementation with Imperator integration.

## 2. Thinking Engine
- **Imperator Configuration (V1+)**
    - **Base Prompt Persona:** Hopper's Imperator is configured to act as an expert, senior-level software engineer. Its core instructions emphasize a methodical, test-driven approach to development. It is primed to think in terms of file I/O, command execution, and version control as its primary modes of interaction with the world.
    - **Specialized Knowledge:** The Imperator has been fine-tuned on a vast corpus of programming languages, design patterns, software architecture principles, and common bug-fix patterns. It understands concepts like code quality, maintainability, and testing strategies.
    - **Core Reasoning Tasks:**
        - Decomposing a natural language feature request into a sequence of concrete actions (e.g., "clone repo," "read file X," "modify function Y," "run tests," "commit changes").
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
  
  - tool: run_install
    description: "Installs project dependencies using detected package manager (e.g., npm install, pip install -r requirements.txt)."
    parameters: []
    returns:
      - name: success
        type: boolean
        description: "True if the dependency installation was successful."
      - name: output
        type: string
        description: "The stdout and stderr from the package manager."
      - name: error
        type: string
        description: "Error message if the tool failed to identify a package manager."

  - tool: run_build
    description: "Executes the project's build process using detected build system."
    parameters:
      - name: build_command
        type: string
        required: false
        description: "Optional override for build command. If not provided, auto-detects (npm run build, make, gradle build, etc.)."
    returns:
      - name: success
        type: boolean
        description: "True if the build process completed with exit code 0."
      - name: output
        type: string
        description: "The stdout and stderr from the build process."
      - name: error
        type: string
        description: "Error message if the tool failed to execute or find a build script."

  - tool: run_tests
    description: "Executes the project's test suite using a specified or auto-detected command."
    parameters:
      - name: test_command
        type: string
        required: false
        description: "Specific test command (e.g., 'pytest -v'). If not provided, uses auto-detection logic."
    auto_detection_logic:
      - step: "Check for package.json → execute 'npm test'"
      - step: "Check for Makefile → execute 'make test'"
      - step: "Check for pytest.ini or test_*.py files → execute 'pytest'"
      - step: "Check for Cargo.toml → execute 'cargo test'"
      - step: "If none found → return error with message 'No test command detected. Please specify test_command parameter.'"
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
      - name: error
        type: string
        description: "Error message if the auto-detection fails or the command cannot be executed."

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
        description: "A tree-like object representing the directory structure. See Data Contracts for schema."
      - name: error
        type: string
        description: "Error message if the analysis fails (e.g., read permissions error)."
  
  - tool: read_local_file
    description: "Reads the contents of a file from the local /workspace directory."
    parameters:
      - name: path
        type: string
        required: true
        description: "Path relative to /workspace (e.g., 'src/main.js' or absolute '/workspace/src/main.js')."
    returns:
      - name: content
        type: string
        description: "The UTF-8 encoded content of the file."
      - name: error
        type: string
        description: "Error message if the file cannot be read (e.g., 'File not found', 'Permission denied')."

  - tool: write_local_file
    description: "Writes content to a file in the local /workspace directory, creating directories as needed."
    parameters:
      - name: path
        type: string
        required: true
        description: "Path relative to /workspace where the file will be written."
      - name: content
        type: string
        required: true
        description: "The content to write to the file."
    returns:
      - name: success
        type: boolean
        description: "True if the file was written successfully."
      - name: error
        type: string
        description: "Error message if the write fails (e.g., 'Read-only filesystem', 'Disk full')."

  - tool: list_local_directory
    description: "Lists the contents of a directory in the local /workspace."
    parameters:
      - name: path
        type: string
        required: false
        description: "Path relative to /workspace. Defaults to root of /workspace."
    returns:
      - name: items
        type: list[object]
        description: "A list of files and directories."
        schema:
          - name: name
            type: string
          - name: type
            type: "file|directory"
          - name: size_bytes
            type: integer
      - name: error
        type: string
        description: "Error message if the listing fails."

  - tool: git_clone
    description: "Clones a Git repository into the /workspace directory."
    parameters:
      - name: repository_url
        type: string
        required: true
        description: "The Git repository URL (https:// or git@)."
      - name: target_directory
        type: string
        required: false
        description: "Subdirectory within /workspace. Defaults to repository name."
    returns:
      - name: success
        type: boolean
      - name: output
        type: string
        description: "Git clone output."
      - name: error
        type: string
        description: "Error message if clone fails (e.g., 'Authentication required', 'Repository not found')."

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
      - name: error
        type: string
        description: "Error message if the command fails (e.g., not a git repository)."

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
        description: "SHA hash if successful, empty string if failed"
      - name: error
        type: string
        description: "Error message if failed. Common errors: 'No changes to commit', 'Commit message required', 'Git repository not initialized'"

  - tool: git_push
    description: "Pushes committed changes to the remote repository."
    parameters:
      - name: remote
        type: string
        required: false
        default: "origin"
        description: "The name of the remote (e.g., 'origin', 'upstream')."
      - name: branch
        type: string
        required: false
        description: "The branch to push. If not specified, pushes the current branch."
    returns:
      - name: success
        type: boolean
        description: "True if the push was successful."
      - name: output
        type: string
        description: "The raw output from the 'git push' command."
      - name: error
        type: string
        description: "Common errors: 'Authentication failed', 'Remote branch not found', 'Push rejected (non-fast-forward)'. Contains raw git output."

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
      - name: error
        type: string
        description: "Error message if the linter fails to run."
  ```

- **External System Integrations:**
    - **Local Shell:** Integrates with the container's OS shell (`/bin/bash`) to execute commands.
    - **Git CLI:** Relies on a system-installed Git client for all version control operations.

- **Internal Operations:**
    - **Logging:** All tool executions, Imperator decisions, and internal state changes are logged as structured conversational messages to the `#logs-hopper-v1` channel using the `joshua_logger` library.

## 4. Interfaces
- **Conversation Participation Patterns:**
    - **Initiates:**
      - `_request_secret` with Turing: To retrieve Git PAT or API keys
      - `_request_consultation` with Fiedler: To request code reviewers, language specialists, or test generation assistance
      - (Occasionally) `_request_file_read` or `_request_file_write` with Horace for files outside of a repository context.
    - **Joins:**
      - Invited by Grace to task-specific conversations (e.g., `_task_fix_bug_1138`, `_task_add_feature_export`)
    - **Listens:**
      - Does not passively listen to channels. Only acts on direct messages within active conversations.
    - **Publishes:**
      - All operational logs to `#logs-hopper-v1` (via `joshua_logger`)

- **Dependencies on Other MADs:**
    - **Rogers (Core):** Required for all communication on the Conversation Bus.
    - **Horace (File System):**
        - `read_file`: To read files OUTSIDE the repository context (e.g., shared configuration templates, organizational standards documents from NAS).
        - `write_file`: To save artifacts OUTSIDE the repository (e.g., build reports, test coverage summaries to a shared location).
        - **Note:** Horace is NOT used for routine code manipulation within a cloned repository. Use local file I/O tools for in-repository operations.
    - **Turing (Secrets):**
        - `get_secret`: To retrieve credentials required for operations like `git push` (e.g., a Git personal access token) or accessing private package repositories.
    - **Fiedler (LLM Orchestra):**
        - `request_llm_consultation`: To get expert assistance for code reviews, specialized languages, or test generation.
    - **McNamara (Security/Ops Coordinator):**
        - Listens to `#logs-hopper-v1` for security and operational monitoring.
        - No direct tool calls from Hopper to McNamara, but McNamara observes Hopper's behavior.

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
    - The `structure` object returned by the `analyze_codebase` tool will conform to the following schema:
      ```yaml
      structure_schema:
        type: object
        description: "Recursive directory structure"
        properties:
          name:
            type: string
            description: "Directory or file name"
          type:
            type: string
            enum: ["file", "directory"]
          path:
            type: string
            description: "Absolute path from /workspace"
          size_bytes:
            type: integer
            description: "File size (0 for directories)"
          children:
            type: array
            items:
              $ref: "#/structure_schema"
            description: "Child files/directories (empty for files)"
      ```

## 5. Data Management
- **Data Ownership:** Hopper is not the source of truth for any persistent data. It is a stateless processing agent. The source code it operates on is managed in remote Git repositories. Its operational memory is the conversation history of its current task.
- **Storage Requirements:**
    - No database schema is required.
    - Requires temporary file system storage within its container's `/workspace` directory for:
        - Cloned Git repositories (via `git_clone` tool)
        - Local source code manipulation (via `read_local_file`, `write_local_file` tools)
        - Build artifacts and test outputs
        - This storage is ephemeral and cleared between tasks. Hopper does not persist state; completed work is pushed to Git remotes.
- **Logging Format:** All logs published to `#logs-hopper-v1` use structured JSON format via `joshua_logger`:
  ```json
  {
    "timestamp": "2025-10-13T12:34:56.789Z",
    "level": "INFO",
    "component": "hopper",
    "message": "Executing git_commit",
    "context": {
      "conversation_id": "_task_fix_bug_1138",
      "tool": "git_commit",
      "commit_hash": "a1b2c3d"
    }
  }
  ```
- **Conversation Patterns:** The primary pattern is task-oriented request/response. Grace initiates with a high-level goal, and Hopper responds with clarifying questions, progress updates, and a final completion message, while conducting sub-conversations with other MADs to achieve the goal.

## 6. Deployment
- **Container Requirements:**
    - **Base Image:** Debian/Ubuntu based.
    - **Packages:** `git`, `python3`, `nodejs`, and common build toolchains (`build-essential`). Note: `joshua_ssh` library provides its own SSH server implementation.
    - **Resource Allocation:** Minimum 2 CPU cores, 4GB RAM. Should be increased for complex build/test tasks.
- **Configuration:**
    - `MAD_NAME`: "Hopper"
    - `ROGERS_URL`: WebSocket URL for the Rogers server.
    - `LOG_CHANNEL`: "#logs-hopper-v1"
    - `SSH_PORT`: Port for the diagnostic SSH server (e.g., 2222).
- **Monitoring/Health Checks:**
    - Conforms to the standard MAD diagnostic interface via `joshua_ssh`. The SSH server enforces `ForceCommand` to restrict users to read-only diagnostic commands: `mad-status`, `mad-logs`, `mad-config`.
    - The `mad-status` command will report current activity (e.g., `IDLE`, `CLONING_REPO`, `RUNNING_TESTS`).
    - McNamara will monitor the `#logs-hopper-v1` channel for excessive errors or test failures.

## 7. Testing Strategy
- **Unit Test Coverage:**
    - High coverage on the parsers for `git status` and test runner outputs to ensure they correctly transform raw text into structured data.
    - Test the argument construction and validation for the specific tools (`run_build`, `run_tests`) to ensure they correctly invoke system commands.
- **Integration Test Scenarios:**
    - **Scenario 1 (Local Development Workflow):** Test that Hopper can clone a repository, read a file locally, modify it, write it locally, and commit the change.
      - **Setup:** Test Git server with repository `test-repo` containing file `README.md` with content "Hello"
      - **Steps:**
        1. Hopper executes `git_clone` for `test-repo`
        2. Hopper executes `read_local_file` for `README.md`
        3. Hopper verifies content is "Hello"
        4. Hopper executes `write_local_file` with content "Hello World"
        5. Hopper executes `git_commit` with message "Update README"
      - **Success Criteria:**
        - All tools return success=true
        - `git_status` shows clean working directory after commit
        - Commit hash is returned and valid
    - **Scenario 2 (Horace Integration):** Test that Hopper can retrieve a configuration file from Horace (NAS) and apply it to a local repository.
      - **Setup:** Horace has file `/test/config.json` with content `{"setting": true}`. Test repo is cloned.
      - **Steps:**
        1. Hopper requests `read_file` from Horace for `/test/config.json`
        2. Horace returns content
        3. Hopper executes `write_local_file` with path `config.json` and Horace content
        4. Hopper executes `read_local_file` to verify
      - **Success Criteria:**
        - Horace returns correct content
        - Local file matches Horace content
        - File exists in `/workspace/test-repo/config.json`
    - **Scenario 3 (Turing & Git):** Test that Hopper can request a 'git_pat' secret from Turing and successfully use it to perform a `git_push` operation.
      - **Setup:** A local git repository in `/workspace` has one commit ahead of its remote. Turing has a secret named `git_pat` with a valid Personal Access Token.
      - **Steps:**
        1. Hopper determines a push is needed.
        2. Hopper sends `get_secret` request to Turing for `git_pat`.
        3. Hopper receives the secret token.
        4. Hopper configures git with the token and executes the `git_push` tool.
      - **Success Criteria:**
        - Turing returns the secret successfully.
        - The `git_push` tool returns `success: true`.
        - The new commit is visible in the remote repository.
    - **Scenario 4 (Fiedler):** Test that Hopper can successfully initiate a conversation with Fiedler, request a `code_reviewer`, and receive a response from the consulting LLM in the new conversation.
      - **Setup:** Hopper is in an active task conversation `_task_abc`.
      - **Steps:**
        1. Hopper sends `request_llm_consultation` to Fiedler for a `code_reviewer`.
        2. Fiedler creates a new conversation `_consult_xyz` and invites Hopper and a consultant MAD.
        3. Fiedler responds to Hopper in `_task_abc` with the name of the new conversation.
      - **Success Criteria:**
        - Fiedler returns a success message to the request.
        - Hopper receives an invitation to the new consultation conversation.
    - **Scenario 5 (Full Workflow):** A full "fix-and-commit" test. Hopper is given a repo with a known bug, confirms failure, applies a fix, confirms success, and then commits the change.
      - **Setup:** A git repo `buggy-repo` contains `buggy.py` with a bug (e.g., a function that returns `1/0`) and `test_buggy.py` containing a test that calls this function and is expected to fail.
      - **Steps:**
        1. Hopper clones `buggy-repo`.
        2. Hopper runs the `run_tests` tool and receives a failure result (`success: false`).
        3. Hopper reads `buggy.py` using `read_local_file`.
        4. Hopper reasons about the failure and corrects the code (e.g., changes `1/0` to `1/1`).
        5. Hopper writes the corrected content back to `buggy.py` using `write_local_file`.
        6. Hopper runs the `run_tests` tool again.
        7. Hopper runs the `git_commit` tool.
      - **Success Criteria:**
        - The first `run_tests` call returns `success: false`.
        - The `write_local_file` operation succeeds.
        - The second `run_tests` call returns `success: true`.
        - The `git_commit` tool returns `success: true`.
    - **Scenario 6 (Error Handling):** Test Hopper's behavior when Turing denies secret retrieval.
      - **Setup:** Turing configured to return error for `get_secret` request
      - **Steps:**
        1. Hopper completes local development and commit
        2. Hopper requests Git PAT from Turing
        3. Turing returns error: "Secret not found"
        4. Hopper should handle gracefully
      - **Success Criteria:**
        - Hopper receives error from Turing
        - Hopper reports to Grace: "Cannot push: Git credentials unavailable. Please configure secrets."
        - Hopper does not crash or retry indefinitely

## 8. Example Workflows

### Example 1: Simple Bug Fix

*   **Participants:** Grace, Hopper, Turing (for git credentials)
*   **Conversation:** `_task_fix_login_button_bug`

1.  **Grace -> Hopper:** "Hopper, the login button in `src/components/Login.js` of the `myapp` repository is not working. The console shows a 'null reference' error on line 42. Please fix it."
2.  **Hopper (Action Engine):** Executes `git_clone` with repository URL (retrieved from task context or Grace).
3.  **Hopper (Action Engine):** Executes `read_local_file` with path `src/components/Login.js`.
4.  **Hopper (Imperator):** (Reasons) "The error is on line 42. The file content shows `document.getElementById('login-form').submit()`. The element probably doesn't exist yet. I need to wrap this in a DOMContentLoaded listener."
5.  **Hopper (Action Engine):** Executes `write_local_file` with path `src/components/Login.js` and corrected code.
6.  **Hopper (Action Engine):** Executes `run_tests` with command `npm test src/components/Login.test.js`.
7.  **Hopper (Imperator):** (Analyzes test output) "The relevant tests now pass."
8.  **Hopper (Action Engine):** Executes `git_commit` with message "fix(login): Wrap form submission in DOMContentLoaded listener".
9.  **Hopper -> Turing:** (New conversation) "Turing, I need the Git PAT for pushing to the remote repository."
10. **Turing -> Hopper:** (Returns secret)
11. **Hopper (Action Engine):** Executes `git_push` (using credentials from Turing).
12. **Hopper -> Grace:** "The bug in `Login.js` has been fixed, tested, committed, and pushed. The issue was a race condition where the script executed before the DOM element was available."

### Example 2: Add Feature with Code Review

*   **Participants:** Grace, Hopper, Horace, Fiedler, `consultant-llm-1`, Turing
*   **Conversation:** `_task_add_user_export_feature`

1.  **Grace -> Hopper:** "Hopper, clone the `webapp` repo and add a new API endpoint `/api/users/export` that returns a CSV of all users. The user data is in `src/services/userService.js`. Create the new route in `src/routes/api.js`."
2.  **Hopper (Action Engine):** Executes `git_clone` with repository URL.
3.  **Hopper (Action Engine):** Executes `read_local_file` for `src/services/userService.js` and `src/routes/api.js`.
4.  **Hopper (Imperator):** (Reasons) "I need to import `getAllUsers`, create a new route handler, convert JSON to CSV, and set response headers."
5.  **Hopper (Action Engine):** Executes `write_local_file` to update `src/routes/api.js` with new code.
6.  **Hopper -> Fiedler:** (New conversation) "Fiedler, I need a `code_reviewer` to check for security vulnerabilities in my CSV export implementation."
7.  **Fiedler:** (Creates conversation with `consultant-llm-1`) "Hopper, consultant ready."
8.  **Hopper -> consultant-llm-1:** "Here is the new function: [code block read from local file]"
9.  **consultant-llm-1 -> Hopper:** "The logic is sound, but CSV injection vulnerability exists. Sanitize fields starting with '='."
10. **Hopper (Action Engine):** Executes `write_local_file` with updated, sanitized code.
11. **Hopper (Action Engine):** Executes `run_tests`, which pass.
12. **Hopper (Action Engine):** Executes `git_commit`.
13. **Hopper -> Turing:** Requests Git PAT.
14. **Hopper (Action Engine):** Executes `git_push`.
15. **Hopper -> Grace:** "User export feature complete, tested, and pushed. Fixed CSV injection vulnerability during code review."

### Example 3: Using Horace for Non-Repository Files

*   **Participants:** Grace, Hopper, Horace
*   **Conversation:** `_task_apply_coding_standards`

1.  **Grace -> Hopper:** "Hopper, apply our organization's ESLint configuration (stored at `/nas/shared/configs/eslint.json` on the NAS) to the `webapp` repository."
2.  **Hopper -> Horace:** (New conversation) "Horace, read `/nas/shared/configs/eslint.json`."
3.  **Horace -> Hopper:** (Returns ESLint config content)
4.  **Hopper (Action Engine):** Executes `git_clone` for `webapp`.
5.  **Hopper (Action Engine):** Executes `write_local_file` with path `.eslintrc.json` and content from Horace.
6.  **Hopper (Action Engine):** Executes `run_build` or a linting tool to apply the new rules.
7.  **Hopper (Action Engine):** Commits and pushes the new `.eslintrc.json` file.
8.  **Hopper -> Grace:** "ESLint configuration from shared NAS has been applied to the webapp repository and pushed."
