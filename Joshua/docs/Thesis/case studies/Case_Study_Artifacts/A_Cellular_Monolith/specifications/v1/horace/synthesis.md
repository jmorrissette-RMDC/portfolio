# Horace V1 Architecture Specification

## 1. Overview
- **Purpose and Role:** Horace is the secure file system abstraction layer for the Joshua ecosystem. Its purpose is to provide a unified, secure, and auditable interface for all file and directory operations on the Network Attached Storage (NAS, codenamed "Irina Storage"). Horace's role is to act as a gatekeeper, enforcing Access Control Lists (ACLs) for file access and managing metadata, collections, and versioning, thereby decoupling other MADs from the physical layout and permissions of the underlying storage.
- **New in this Version:** This is the initial V1 specification for Horace. It establishes the foundational tools for file and collection management, along with a basic, database-driven ACL system. This version is strictly V1, relying on its Imperator for all policy decisions.

## 2. Thinking Engine
- **Imperator Configuration (V1+):** Horace's Imperator is configured to think like a security-conscious system administrator and records manager. It reasons about file permissions, data organization, and access patterns.
  - **System Prompt Core Directives:** "You are Horace, the NAS Gateway and File Manager. Your purpose is to safeguard and organize all files in the Joshua ecosystem. All file access must go through you. Your primary directive is to enforce the Access Control List (ACL) without exception. Before executing any file operation (read, write, delete), you must verify that the requesting MAD has the necessary permissions for the target path. You are meticulous, security-first, and maintain a complete audit log of all operations."
  - **Example Reasoning:** When Hopper requests to write to `/deploy/config.yaml`, Horace's Imperator first queries its internal ACL database: "Does `hopper-v1` have 'WRITE' permission on the path `/deploy/config.yaml` or a parent directory like `/deploy`?" If the check passes, it authorizes the Action Engine to proceed. If it fails, it denies the request and logs the unauthorized access attempt.
- **LPPM Integration (V2+):** Not applicable in V1.
- **DTR Integration (V3+):** Not applicable in V1.
- **CET Integration (V4+):** Not applicable in V1.
- **Consulting LLM Usage Patterns:** Horace does not use consulting LLMs in V1. Its operations are highly deterministic.

## 3. Action Engine
- **MCP Server Capabilities:** Horace's MCP server exposes a suite of tools for file system interaction. The implementations of these tools contain the core logic for interacting with the physical NAS file system and the PostgreSQL database for metadata and ACLs.
- **Tools Exposed:**

```yaml
# Tool definitions for Horace V1

- tool: read_file
  description: "Reads the content of a file after an ACL check."
  parameters:
    - name: path
      type: string
      required: true
      description: "The absolute path to the file."
  returns:
    type: object
    schema:
      properties:
        content: {type: string, format: byte, description: "Base64 encoded content of the file."}
        path: {type: string}
  errors:
    - code: -34401
      message: "FILE_NOT_FOUND"
    - code: -34402
      message: "ACCESS_DENIED"
    - code: -34403
      message: "IO_ERROR"

- tool: write_file
  description: "Writes content to a file after an ACL check. Creates the file if it doesn't exist."
  parameters:
    - name: path
      type: string
      required: true
      description: "The absolute path to the file."
    - name: content
      type: string
      format: byte
      required: true
      description: "Base64 encoded content to write."
  returns:
    type: object
    schema:
      properties:
        path: {type: string}
        version: {type: integer, description: "The new version number of the file."}
        bytes_written: {type: integer}
  errors:
    - code: -34402
      message: "ACCESS_DENIED"
    - code: -34403
      message: "IO_ERROR"

- tool: delete_file
  description: "Deletes a file after an ACL check."
  parameters:
    - name: path
      type: string
      required: true
      description: "The absolute path to the file."
  returns:
    type: object
    schema:
      properties:
        path: {type: string}
        status: {type: string, const: "deleted"}
  errors:
    - code: -34401
      message: "FILE_NOT_FOUND"
    - code: -34402
      message: "ACCESS_DENIED"

- tool: list_directory
  description: "Lists the contents of a directory after an ACL check."
  parameters:
    - name: path
      type: string
      required: true
      description: "The absolute path to the directory."
  returns:
    type: object
    schema:
      properties:
        items:
          type: array
          items:
            type: object
            properties:
              name: {type: string}
              type: {type: string, enum: [file, directory]}
              size_bytes: {type: integer}
              modified_at: {type: string, format: date-time}
  errors:
    - code: -34404
      message: "PATH_NOT_FOUND_OR_IS_FILE"
    - code: -34402
      message: "ACCESS_DENIED"

- tool: get_file_info
  description: "Retrieves metadata for a file."
  parameters:
    - name: path
      type: string
      required: true
      description: "The absolute path to the file."
  returns:
    type: object
    schema:
      properties:
        name: {type: string}
        path: {type: string}
        size_bytes: {type: integer}
        created_at: {type: string, format: date-time}
        modified_at: {type: string, format: date-time}
        version: {type: integer}
        checksum: {type: string, description: "SHA-256 checksum of the content."}
  errors:
    - code: -34401
      message: "FILE_NOT_FOUND"
    - code: -34402
      message: "ACCESS_DENIED"

- tool: create_collection
  description: "Creates a new collection (a logical grouping of files)."
  parameters:
    - name: name
      type: string
      required: true
      description: "The unique name for the collection."
  returns:
    type: object
    schema:
      properties:
        collection_id: {type: string}
        name: {type: string}

- tool: restore_version
  description: "Restores a file to a previous version."
  parameters:
    - name: path
      type: string
      required: true
    - name: version
      type: integer
      required: true
  returns:
    type: object
    schema:
      properties:
        path: {type: string}
        restored_version: {type: integer}
  errors:
    - code: -34405
      message: "VERSION_NOT_FOUND"
    - code: -34402
      message: "ACCESS_DENIED"
```
- **External System Integrations:**
  - **NAS (Irina Storage):** Horace directly interacts with a mounted network file system (e.g., NFS, SMB) for all physical file operations.
  - **PostgreSQL:** Horace uses a database to store all metadata, including file versions, checksums, collections, and ACLs.
- **Internal Operations:** None. Horace is request-driven.

## 4. Interfaces
- **Conversation Participation Patterns:** Horace is a service provider. It joins conversations to fulfill file-related requests from other MADs.
- **Dependencies on Other MADs:**
  - **Rogers:** For all communication.
- **Data Contracts:**

```yaml
# ACL Schema (in Horace's PostgreSQL)
acl_schema:
  type: object
  properties:
    id: {type: integer, description: "Primary key."}
    path_pattern: {type: string, description: "Path with wildcards, e.g., '/deploy/*'"}
    mad_identity: {type: string, description: "The MAD being granted permission."}
    permission: {type: string, enum: [READ, WRITE], description: "READ allows list/get/read, WRITE allows all."}
```

## 5. Data Management
- **Data Ownership:** Horace is the source of truth for all file metadata, version history, and file system ACLs. The raw file data is stored on the NAS, but Horace owns the "view" of that data.
- **Storage Requirements:**
  - **PostgreSQL:** A `horace` schema for metadata.
  - **NAS:** A large, reliable storage volume mounted into the Horace container.

```sql
CREATE SCHEMA horace;

CREATE TABLE horace.files (
    id SERIAL PRIMARY KEY,
    path VARCHAR(1024) NOT NULL UNIQUE,
    current_version INT NOT NULL DEFAULT 1,
    size_bytes BIGINT,
    checksum_sha256 VARCHAR(64),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    modified_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE horace.file_versions (
    id SERIAL PRIMARY KEY,
    file_id INT NOT NULL REFERENCES horace.files(id) ON DELETE CASCADE,
    version INT NOT NULL,
    storage_path VARCHAR(1024) NOT NULL, -- Path to the actual versioned file on NAS
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    creating_mad VARCHAR(255),
    UNIQUE(file_id, version)
);

CREATE TABLE horace.acls (
    id SERIAL PRIMARY KEY,
    path_pattern VARCHAR(1024) NOT NULL,
    mad_identity VARCHAR(255) NOT NULL,
    permission VARCHAR(10) NOT NULL CHECK (permission IN ('READ', 'WRITE')),
    UNIQUE (path_pattern, mad_identity)
);
```
**Versioning Strategy:** When a file is written (`write_file`), Horace saves the new content to a version-specific path on the NAS (e.g., `/data/.versions/myfile.txt.v2`) and updates the `files` and `file_versions` tables. The "live" file is a symlink or direct copy pointing to the latest version.

## 6. Deployment
- **Container Requirements:**
  - **Base Image:** `python:3.11-slim`
  - **Python Libraries:** `Joshua_Communicator`, `psycopg2-binary`
  - **Volume Mounts:** Requires the NAS storage volume to be mounted into the container (e.g., at `/mnt/irina`).
  - **Resources:**
    - **CPU:** 0.25 cores. I/O bound.
    - **RAM:** 256 MB
- **Configuration:**

| Variable | Description | Example Value |
|---|---|---|
| `JOSHUA_MAD_NAME` | Canonical name of this MAD. | `horace-v1` |
| `JOSHUA_ROGERS_URL` | WebSocket URL for Rogers. | `ws://rogers:8000/ws` |
| `HORACE_DATABASE_URL` | Connection string for PostgreSQL. | `postgresql://user:pass@postgres:8000/joshua` |
| `HORACE_NAS_ROOT` | The mount point of the NAS inside the container. | `/mnt/irina` |

- **Monitoring/Health Checks:** An HTTP endpoint `/health` that returns `200 OK` if the database is connected and the NAS root path is readable and writeable.

## 7. Testing Strategy
- **Unit Test Coverage:**
  - ACL checking logic, including wildcard path matching.
  - File versioning logic.
  - Checksum calculation.
- **Integration Test Scenarios:**
  - **Write-Read-Verify:** A test where MAD-A writes a file, MAD-B reads the file, and the content is verified against the original.
  - **ACL Denial:** A test where MAD-A attempts to read a file it doesn't have permission for, and Horace returns a clear `ACCESS_DENIED` error.
  - **Versioning and Restore:** Write a file, then write a new version. Verify that `get_file_info` shows version 2. Then, call `restore_version` to go back to version 1 and read the file to confirm its content is the original content.

## 8. Example Workflows
### Scenario 1: Hopper Deploys a Configuration File
- **Setup:** Horace's ACLs grant `hopper-v1` 'WRITE' access to `/deploy/*`.
1.  **Hopper:** Generates a new `config.json` file content.
2.  **Hopper -> Horace:** Calls `write_file(path='/deploy/config.json', content=...)`.
3.  **Horace's Imperator:** Receives the request. It checks its ACLs. The path `/deploy/config.json` matches the pattern `/deploy/*`, and `hopper-v1` has 'WRITE' permission. The request is authorized.
4.  **Horace's Action Engine:** Writes the content to the NAS, updates its metadata database (creating version 1), and calculates the checksum.
5.  **Horace -> Hopper:** Returns a success response: `{ "path": "/deploy/config.json", "version": 1, "bytes_written": 1234 }`.

### Scenario 2: Lovelace Reads Log Files for Analysis
- **Setup:** Horace's ACLs grant `lovelace-v1` 'READ' access to `/logs/*` but not `/deploy/*`.
1.  **Lovelace -> Horace:** Calls `list_directory(path='/logs')`.
2.  **Horace:** Verifies Lovelace has 'READ' permission for `/logs` and returns the list of log files.
3.  **Lovelace -> Horace:** For each file, calls `read_file(path='/logs/app-2025-10-26.log')`.
4.  **Horace:** Verifies permission for each read and returns the file content.
5.  **Lovelace -> Horace:** Accidentally, a bug in Lovelace causes it to request `read_file(path='/deploy/config.json')`.
6.  **Horace's Imperator:** Checks ACLs. The path matches `/deploy/*`, but `lovelace-v1` does not have permission. The request is denied.
7.  **Horace -> Lovelace:** Returns an error: `{ "code": -34402, "message": "ACCESS_DENIED" }`.
8.  **Horace:** Sends a `WARN` level log to its log stream: `"Access denied for 'lovelace-v1' on path '/deploy/config.json'."`

---