# Hopper V1 Architecture Revision Prompt - Iteration 3

**Date:** 2025-10-13
**Pathfinder:** Hopper V1
**Iteration:** 3 (Major Architectural Revision)

---

## Mission

Revise the Hopper V1 architecture to resolve a **critical architectural contradiction** discovered in iteration 2 review. The synthesis described two mutually incompatible filesystem models that make the core software development workflow non-functional.

---

## Critical Issue: Filesystem Model Contradiction

**Iteration 2 Verdict:** 4/5 ACCEPT (80%), failed 86% quorum due to 1 REJECT with critical objection

### The Problem

The current synthesis mixes two incompatible operational models:

**Local Workspace Model (Implied by Git Tools):**
- Tools: `git_status`, `git_commit`, `git_push` operate on local filesystem
- Assumes: Repository cloned into Hopper's `/workspace` directory
- Section 5: States "requires temporary storage to clone repositories"

**Remote Filesystem Model (Horace Dependency):**
- Dependencies list Horace for `read_file`, `write_file`, `list_directory`
- Example Workflow 1, Step 2: "Hopper -> Horace: read `/workspace/src/components/Login.js`"
- Example Workflow 1, Step 5: "Hopper -> Horace: write `/workspace/src/components/Login.js`"

**Why This is Broken:**
```
Current (Broken) Workflow:
1. Hopper asks Horace to read file from NAS
2. Hopper modifies content in memory
3. Hopper asks Horace to write file to NAS
4. Hopper runs git_commit (local) ← FAILS! Git can't see NAS files
```

Git commands in Hopper's container **cannot see or stage files** stored on the NAS and accessed via Horace API. The local git repository and Horace-managed files exist in completely disconnected filesystems.

---

## Required Solution: Local-First Architecture

### 1. Add Local File I/O Tools to Action Engine

**Add these tools AFTER `analyze_codebase` and BEFORE Git tools:**

```yaml
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
```

### 2. Update Horace Dependency Scope

**Current (Iteration 2):**
```markdown
- **Horace (File System):**
    - `read_file`: To read source code, configuration, and test results.
    - `write_file`: To save new or modified code.
    - `list_directory`: To understand the project structure.
```

**Revised (Iteration 3):**
```markdown
- **Horace (File System):**
    - `read_file`: To read files OUTSIDE the repository context (e.g., shared configuration templates, organizational standards documents from NAS).
    - `write_file`: To save artifacts OUTSIDE the repository (e.g., build reports, test coverage summaries to a shared location).
    - **Note:** Horace is NOT used for routine code manipulation within a cloned repository. Use local file I/O tools for in-repository operations.
```

### 3. Rewrite Example Workflows for Local-First Pattern

**Example 1: Simple Bug Fix (REVISED)**

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

**Example 2: Add Feature with Code Review (REVISED)**

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

**Optional: Add Example 3 Using Horace for Non-Repo Files**

*   **Participants:** Grace, Hopper, Horace
*   **Conversation:** `_task_apply_coding_standards`

1.  **Grace -> Hopper:** "Hopper, apply our organization's ESLint configuration (stored at `/nas/shared/configs/eslint.json` on the NAS) to the `webapp` repository."
2.  **Hopper -> Horace:** (New conversation) "Horace, read `/nas/shared/configs/eslint.json`."
3.  **Horace -> Hopper:** (Returns ESLint config content)
4.  **Hopper (Action Engine):** Executes `git_clone` for `webapp`.
5.  **Hopper (Action Engine):** Executes `write_local_file` with path `.eslintrc.json` and content from Horace.
6.  **Hopper (Action Engine):** Executes `run_build` or linting tool.
7.  **Hopper (Action Engine):** Commits and pushes.
8.  **Hopper -> Grace:** "ESLint configuration from shared NAS applied to webapp repository."

### 4. Update Integration Test Scenarios

**Scenario 1 (Revised - Local Workflow):**
```markdown
**Scenario 1 (Local Development Workflow):** Test that Hopper can clone a repository, read a file locally, modify it, write it locally, and commit the change.
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
```

**Scenario 2 (Horace for External Files):**
```markdown
**Scenario 2 (Horace Integration):** Test that Hopper can retrieve a configuration file from Horace (NAS) and apply it to a local repository.
- **Setup:** Horace has file `/test/config.json` with content `{"setting": true}`. Test repo is cloned.
- **Steps:**
  1. Hopper requests `read_file` from Horace for `/test/config.json`
  2. Horace returns content
  3. Hopper executes `write_local_file` with path `config.json` and Horace content
  4. Hopper executes `read_local_file` to verify
- **Success Criteria:**
  - Horace returns correct content
  - Local file matches Horace content
  - File exists in `/workspace/config.json`
```

**Keep Scenario 3 (Turing & Git) and Scenario 4 (Full Workflow) - Update to use local file I/O**

### 5. Update Data Management Section

**Current (Iteration 2):**
> Requires temporary file system storage within its container's `/workspace` directory to clone repositories and store build artifacts.

**Revised (Iteration 3):**
> Requires temporary file system storage within its container's `/workspace` directory for:
> - Cloned Git repositories (via `git_clone` tool)
> - Local source code manipulation (via `read_local_file`, `write_local_file` tools)
> - Build artifacts and test outputs
> - This storage is ephemeral and cleared between tasks. Hopper does not persist state; completed work is pushed to Git remotes.

### 6. Address Minor Objections from Iteration 2

**A. Add `git_push` parameters (Grok-4):**
```yaml
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
    - name: output
    - name: error
      description: "Common errors: 'Authentication failed', 'Remote branch not found', 'Push rejected (non-fast-forward)'. Contains raw git output."
```

**B. Add error handling test scenario (Grok-4):**
```markdown
**Scenario 5 (Error Handling):** Test Hopper's behavior when Turing denies secret retrieval.
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
```

**C. Add McNamara to dependencies (DeepSeek-R1):**
```markdown
- **McNamara (Security/Ops Coordinator):**
    - Listens to `#logs-hopper-v1` for security and operational monitoring.
    - No direct tool calls from Hopper to McNamara, but McNamara observes Hopper's behavior.
```

**D. Add SSH ForceCommand details (DeepSeek-R1):**
```markdown
**Monitoring/Health Checks:**
- Conforms to the standard MAD diagnostic interface via `joshua_ssh`. The SSH server enforces `ForceCommand` to restrict users to read-only diagnostic commands: `mad-status`, `mad-logs`, `mad-config`.
- The `mad-status` command will report current activity (e.g., `IDLE`, `CLONING_REPO`, `RUNNING_TESTS`).
- McNamara will monitor the `#logs-hopper-v1` channel for excessive errors or test failures.
```

**E. Clarify logging format (Qwen):**
Add to Section 5 (Data Management):
```markdown
**Logging Format:** All logs published to `#logs-hopper-v1` use structured JSON format via `joshua_logger`:
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
```

---

## Quality Checklist

Before returning the revised document, verify:
- [ ] Added 4 local file I/O tools: `read_local_file`, `write_local_file`, `list_local_directory`, `git_clone`
- [ ] Clarified Horace dependency scope (external files only, NOT in-repo code)
- [ ] Rewrote Example Workflow 1 for local-first pattern
- [ ] Rewrote Example Workflow 2 for local-first pattern
- [ ] Optionally added Example Workflow 3 showing Horace for external config
- [ ] Updated Scenario 1 to test local workflow
- [ ] Added Scenario 2 for Horace integration
- [ ] Updated Scenarios 3-4 to use local file I/O
- [ ] Added Scenario 5 for error handling
- [ ] Updated Data Management section to clarify ephemeral local storage
- [ ] Added `remote` and `branch` parameters to `git_push`
- [ ] Added McNamara to dependencies list
- [ ] Added SSH ForceCommand details to Deployment section
- [ ] Added logging format specification to Data Management section
- [ ] All YAML tool definitions remain valid

---

## Context Documents Available

You have access to:
1. **synthesis.md from iteration 2** - The document to revise
2. **reviews_aggregated.md from iteration 2** - Full details of critical architectural issue
3. All **anchor package documents** - For reference

---

**Execute comprehensive revision now. This is a major architectural change affecting multiple sections.**
