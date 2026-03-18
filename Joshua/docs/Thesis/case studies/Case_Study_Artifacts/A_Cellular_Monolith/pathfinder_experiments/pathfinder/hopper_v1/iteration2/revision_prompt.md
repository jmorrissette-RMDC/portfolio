# Hopper V1 Architecture Revision Prompt - Iteration 2

**Date:** 2025-10-13
**Pathfinder:** Hopper V1
**Iteration:** 2 (Revision)

---

## Mission

Revise the Hopper V1 architecture synthesis to address **critical** and **important** objections raised by the 7-LLM review panel. The iteration 1 synthesis received 3 ACCEPT and 2 REJECT verdicts (60% approval), failing to meet the 6/7 (86%) quorum threshold.

---

## Review Results Summary

**Iteration 1 Verdict:** REJECT (3/5 valid approval, 2 reviews invalid)

**Critical Objections (MUST FIX):**
1. **Security: `run_command` Tool Lacks Input Validation** - Tool allows arbitrary shell commands without sanitization, violating NON_FUNCTIONAL_REQUIREMENTS.md security standards
2. **Missing Data Contract: `analyze_codebase` Structure** - Complex return object lacks formal JSON/YAML schema

**Important Objections (SHOULD FIX):**
1. Missing "New in this Version" section in Overview
2. Ambiguity in `run_command` tool security (duplicate of critical #1)
3. Incorrect container dependency: `openssh-server` not needed for `joshua_ssh`
4. Ambiguous auto-detection logic in `run_tests` tool
5. Error handling in tools lacks detail
6. Incomplete conversation participation patterns explanation
7. Lack of clarity on testing strategy success criteria

---

## Required Changes

### 1. Critical: Fix `run_command` Tool Security

**Current Problem:**
```yaml
- tool: run_command
  description: "Executes a shell command within a secure, sandboxed /workspace directory..."
  parameters:
    - name: command
      type: string
      required: true
      description: "The full shell command to execute (e.g., 'npm install')."
```

**Required Fix (Choose ONE approach):**

**Option A (Recommended):** Remove `run_command` entirely and replace with constrained tools:
```yaml
- tool: run_build
  description: "Executes the project's build process using detected build system."
  parameters:
    - name: build_command
      type: string
      required: false
      description: "Optional override for build command. If not provided, auto-detects (npm run build, make, gradle build, etc.)."

- tool: run_install
  description: "Installs project dependencies using detected package manager."
  parameters: []
  returns:
    - name: success
    - name: output
```

**Option B:** Add strict input validation and command allowlist:
```yaml
- tool: run_command
  description: "Executes a pre-approved shell command within /workspace directory."
  parameters:
    - name: command
      type: string
      required: true
      description: "Command from allowlist: npm install, npm run build, npm test, make, make test, pytest, etc."
  security:
    - command_allowlist: ["npm install", "npm run build", "npm test", "make", "make test", "pytest", "cargo build", "gradle build"]
    - blocked_patterns: ["sudo", "rm -rf", "curl", "wget", ">", ">>", "|", "&&", ";"]
```

### 2. Critical: Add Data Contract for `analyze_codebase` Structure

**Current Problem:**
```yaml
- tool: analyze_codebase
  returns:
    - name: structure
      type: object
      description: "A tree-like object representing the directory structure."
```

**Required Fix:**
Add to **Section 4. Interfaces - Data Contracts**:

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

**Example Structure:**
```json
{
  "name": "src",
  "type": "directory",
  "path": "/workspace/src",
  "size_bytes": 0,
  "children": [
    {
      "name": "main.js",
      "type": "file",
      "path": "/workspace/src/main.js",
      "size_bytes": 1024,
      "children": []
    }
  ]
}
```

### 3. Important: Add "New in this Version" Section

**Location:** Section 1. Overview

**Add After "Purpose and Role":**
```markdown
- **New in this Version:** N/A - Initial V1 baseline implementation with Imperator integration.
```

### 4. Important: Remove `openssh-server` from Container Requirements

**Current Text (Section 6. Deployment):**
> Packages: `git`, `openssh-server` (for `joshua_ssh`), `python3`, `nodejs`, and common build toolchains (`build-essential`).

**Corrected Text:**
> Packages: `git`, `python3`, `nodejs`, and common build toolchains (`build-essential`). Note: `joshua_ssh` library provides its own SSH server implementation.

### 5. Important: Define `run_tests` Auto-Detection Logic

**Current Problem:**
> If not provided, attempts to use a standard command like 'npm test' or 'make test'.

**Required Fix:**
```yaml
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
```

### 6. Important: Add Error Handling Details to Tools

**For Each Tool with Potential Errors, Add:**

Example for `git_commit`:
```yaml
returns:
  - name: success
    type: boolean
  - name: commit_hash
    type: string
    description: "SHA hash if successful, empty string if failed"
  - name: error
    type: string
    description: "Error message if failed. Common errors: 'No changes to commit', 'Commit message required', 'Git repository not initialized'"
```

### 7. Important: Expand Conversation Participation Patterns

**Current Text:**
> Initiates: Hopper initiates conversations with Horace (for files), Turing (for secrets), and Fiedler (for consultations).

**Enhanced Version:**
```markdown
- **Initiates:**
  - `_request_file_read` with Horace: To read source code files
  - `_request_file_write` with Horace: To save modified code
  - `_request_secret` with Turing: To retrieve Git PAT or API keys
  - `_request_consultation` with Fiedler: To request code reviewers, language specialists, or test generation assistance
- **Joins:**
  - Invited by Grace to task-specific conversations (e.g., `_task_fix_bug_1138`, `_task_add_feature_export`)
- **Listens:**
  - Does not passively listen to channels. Only acts on direct messages within active conversations.
- **Publishes:**
  - All operational logs to `#logs-hopper-v1` (via `joshua_logger`)
```

### 8. Important: Add Testing Strategy Success Criteria

**For Each Integration Test Scenario, Add Expected Outcomes:**

Example for Scenario 1:
```markdown
**Scenario 1 (Horace):** Test that Hopper can request a file from Horace, modify its content in memory, and write it back to a new file via Horace.
- **Setup:** Horace has file `/workspace/test.txt` with content "Hello"
- **Steps:**
  1. Hopper sends `read_file` request to Horace for `/workspace/test.txt`
  2. Hopper receives content "Hello"
  3. Hopper modifies content to "Hello World" using Imperator reasoning
  4. Hopper sends `write_file` request to Horace for `/workspace/test_modified.txt`
- **Success Criteria:**
  - Horace returns success for read operation
  - Horace returns success for write operation
  - File `/workspace/test_modified.txt` exists with content "Hello World"
```

---

## Instructions

1. **Read the original synthesis from iteration 1**
2. **Apply ALL critical and important fixes listed above**
3. **Maintain the existing structure and format** (Standardized MAD Architecture Template)
4. **Do NOT make unnecessary changes** to sections that received no objections
5. **Ensure all changes are integrated smoothly** into the document flow
6. **Verify all YAML tool definitions remain valid** after changes
7. **Return the complete revised document** as `synthesis.md`

---

## Quality Checklist

Before returning the revised document, verify:
- [ ] Both critical objections are resolved (security validation + data contract)
- [ ] All 7 important objections are addressed
- [ ] "New in this Version" section added to Overview
- [ ] `openssh-server` removed from deployment requirements
- [ ] `run_tests` has explicit auto-detection logic
- [ ] `analyze_codebase` structure has full JSON schema in Data Contracts section
- [ ] Error handling details added to relevant tools
- [ ] Conversation participation patterns are comprehensive
- [ ] Integration test scenarios include success criteria

---

## Context Documents Available

You have access to:
1. **synthesis.md from iteration 1** - The original document to revise
2. **reviews_aggregated.md** - Full details of all objections
3. All **anchor package documents** - For reference compliance

---

**Execute revision now.**
