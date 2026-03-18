# Starret Requirements

- **Role**: Git Management
- **Version**: V0.10
- **Home**: `mads/starret/`

---

## 1. Overview

- **Purpose**: Starret is the specialist MAD for all Git and source code repository operations.
- **V0.10 Scope Definition**: Provide a robust, programmatic API for Git commands and GitHub interactions, serving as a foundational service for `Hopper` and `Deming`. In V0.10, Starret is a pure Action Engine MAD with no conversational capabilities.

---

## 2. Tool Exposure Model

This MAD follows the Direct Tool Exposure architecture (ADR-023). Its public tools are exposed directly on its MCP server and are discoverable via the Rogers registry. As a V0.10 infrastructure MAD, Starret has no Thought Engine, so any communication that is not a valid MCP call for an exposed tool will result in an error.

> **Note on Tool List:** The tools listed in this document are a *provisional set* based on the MAD's high-level requirements. The final, authoritative list of tools, their specific parameters, and their return schemas will be defined in a dedicated Design Document prior to implementation.

---

## 3. Public Action Engine Tools

### `starret_clone`
- **Description:** Clones a Git repository to the local filesystem.
- **Input Schema:**
    - `repo_url` (string, required): The URL of the repository to clone.
    - `local_path` (string, required): The local path to clone the repository into.
- **Output Schema:** `{"status": "success", "path": "/path/to/repo"}`

### `starret_checkout`
- **Description:** Checks out a specific branch of a local repository.
- **Input Schema:**
    - `local_path` (string, required): The path to the local repository.
    - `branch_name` (string, required): The name of the branch to check out.
    - `create_new` (boolean, optional, default: false): Whether to create the branch if it doesn't exist.
- **Output Schema:** `{"status": "success", "branch": "main"}`

### `starret_add`
- **Description:** Stages one or more files for the next commit.
- **Input Schema:**
    - `local_path` (string, required): The path to the local repository.
    - `files` (array[string], required): A list of file paths to add. Use `["."]` to add all changes.
- **Output Schema:** `{"status": "success", "added_files_count": 3}`

### `starret_commit`
- **Description:** Commits the currently staged changes.
- **Input Schema:**
    - `local_path` (string, required): The path to the local repository.
    - `message` (string, required): The commit message.
- **Output Schema:** `{"status": "success", "commit_hash": "abc123def456"}`

### `starret_push`
- **Description:** Pushes committed changes to a remote repository.
- **Input Schema:**
    - `local_path` (string, required): The path to the local repository.
    - `remote_name` (string, optional, default: "origin"): The name of the remote.
    - `branch_name` (string, optional): The branch to push. Defaults to the current branch.
- **Output Schema:** `{"status": "success"}`

### `starret_create_pr`
- **Description:** Creates a pull request on a platform like GitHub.
- **Input Schema:**
    - `local_path` (string, required): The path to the local repository.
    - `title` (string, required): The title of the pull request.
    - `body` (string, required): The description of the pull request.
    - `head_branch` (string, required): The source branch for the PR.
    - `base_branch` (string, required): The target branch for the PR.
- **Output Schema:** `{"status": "success", "pr_url": "http://github.com/...", "pr_number": 123}`

---

## 4. Future Evolution (Post-V0)

Starret's role as the Git and repository management platform remains focused on reliable version control operations throughout the ecosystem's evolution.

*   **Phase 1 (Foundation / V0.10):** Starret is hardened and quality-gated for flawless Direct Communication, becoming the reliable Git operations platform for the V0.10 Core Fleet. All MADs depend on Starret for version control operations, including Hopper's autonomous development workflows.
*   **Phase 2 (Conversation / V1.0):** Starret is re-platformed to communicate exclusively via the Rogers Conversation Bus (pure Kafka), using `Joshua_Communicator` for all inter-MAD communication. All Git operations and repository events flow through the durable conversation log, enabling complete version control history reconstruction.
*   **Phase 5 (Autonomy / V7.0):** Starret integrates with Joshua MAD's strategic orchestration, receiving top-down directives for system-wide repository management policies, constitutional constraints on commit patterns, and strategic enforcement of version control best practices across the entire ecosystem.

---