# Turing V1 Architecture Synthesis Prompt

## Context

You are creating the **V1 (Imperator-only)** architecture specification for **Turing**, the Secrets Manager MAD in the Joshua Cellular Monolith ecosystem.

## Your Task

Produce a complete MAD architecture document following the **Standardized MAD Architecture Template** defined in the anchor package. This document must be immediately "Deployable" (as defined in ARCHITECTURE_GUIDELINES.md) - meaning an experienced engineer can implement Turing V1 from this document alone without additional clarification.

## Anchor Package Reference

You MUST thoroughly read and adhere to these 7 anchor documents:

1. **ANCHOR_OVERVIEW.md** - System vision, V0-V4 definitions, architectural principles
2. **SYSTEM_DIAGRAM.md** - Visual architecture showing all 13 MADs and interactions
3. **NON_FUNCTIONAL_REQUIREMENTS.md** - Performance, security, logging requirements
4. **MAD_ROSTER.md** - Canonical description of all MADs including Turing's role
5. **V1_PHASE1_BASELINE.md** - Current baseline (Rogers + Dewey V1 complete)
6. **ARCHITECTURE_GUIDELINES.md** - Template structure and "Deployable" definition
7. **REVIEW_CRITERIA.md** - What reviewers will check (completeness, feasibility, consistency, clarity)

## Turing's Role (from MAD_ROSTER.md)

**Purpose:** To provide secure, centralized management of all cryptographic secrets.

**Primary Responsibilities:**
- Store and retrieve secrets (API keys, passwords, certificates) in an encrypted format
- Manage access control, ensuring only authorized MADs can request specific secrets
- Handle secret rotation and lifecycle management
- Log all secret access events for auditing

**Key Capabilities/Tools:**
- Encryption/decryption services
- Secure database for secret storage
- Access control list (ACL) management

**Lifecycle:** Persistent. Must be available early in the system boot sequence.

**Key Interfaces:** Exposes `get_secret` tool to authorized MADs.

**Key Dependencies:** Rogers (communication), PostgreSQL (for encrypted storage).

## V1 Requirements

For V1, Turing must have:

### 1. Imperator Integration
- Dedicated LLM (via CET-P) for secrets management reasoning
- System prompts that emphasize:
  - Security best practices (least privilege, encryption at rest, audit logging)
  - Access control enforcement
  - Threat detection (unusual access patterns)
  - Clear reasoning about why secrets are being accessed or modified

### 2. Conversation Bus Integration
- Join conversations via Rogers when secrets are needed
- Receive requests from other MADs in JSON-RPC 2.0 format
- Send responses with secrets or error messages
- All communication over Conversation Bus (no direct inter-MAD connections)

### 3. Core Secrets Management Tools
Define these tools using the YAML format from ARCHITECTURE_GUIDELINES.md:
- **get_secret**: Retrieve a secret by name
- **set_secret**: Store a new secret or update existing one
- **delete_secret**: Remove a secret
- **list_secrets**: List available secret names (NOT values) for a MAD
- **rotate_secret**: Update a secret and mark old version as deprecated

Each tool must specify:
- Complete parameter list with types and whether required
- Return value with explicit data contract (JSON schema for complex types)
- Error conditions with specific error codes/messages

### 4. Access Control
- ACL system that maps MAD identity → allowed secret names
- Default deny (MAD can only access secrets explicitly granted)
- `get_secret` must check ACL before returning value
- All access attempts (allowed and denied) must be logged

### 5. Encryption at Rest
- All secrets encrypted in PostgreSQL database
- Use industry-standard encryption (e.g., AES-256)
- Encryption keys managed securely (specify approach: KMS, local file, etc.)

### 6. Logging as Conversations
- All Turing actions logged to `#logs-turing-v1` conversation
- **CRITICAL:** Logging format must be **JSON-RPC 2.0 compliant** per NON_FUNCTIONAL_REQUIREMENTS.md
- Example log structure:
```json
{
  "jsonrpc": "2.0",
  "method": "log_event",
  "params": {
    "timestamp": "2025-10-13T12:34:56.789Z",
    "level": "INFO",
    "mad": "turing-v1",
    "message": "Secret accessed successfully",
    "context": {
      "secret_name": "github_pat",
      "requesting_mad": "hopper-v1",
      "access_granted": true
    }
  },
  "id": "log-<uuid>"
}
```
- Use `joshua_logger` library for automatic JSON-RPC formatting
- Sensitive data (secret values) MUST NEVER appear in logs, only metadata (names, requesters, success/failure)

### 7. Integration Tests
Define at least 2 integration test scenarios:
- **Scenario 1:** Hopper requests a Git PAT, Turing checks ACL, returns secret
- **Scenario 2:** Unauthorized MAD requests secret, Turing denies and logs attempt
- **Scenario 3:** Secret rotation workflow

## Lessons from Previous Pathfinder (Hopper V1)

Apply these quality improvements to avoid common objections:

### 1. JSON-RPC 2.0 Logging Must Be Explicit
- Show complete JSON-RPC 2.0 structure in logging examples
- Clarify that `joshua_logger` handles formatting automatically
- Do NOT show plain JSON objects without JSON-RPC wrapper

### 2. Imperator Configuration Must Detail Tool Integration
- In "Thinking Engine" section, explicitly describe how Imperator:
  - Reasons about access control decisions
  - Detects unusual access patterns
  - Handles error conditions
  - Uses each tool (get_secret, set_secret, etc.)
- Include example reasoning workflow

### 3. Data Contracts Must Have Explicit Schemas
- All complex return types need full JSON schema (in YAML format)
- Don't say "returns object with fields..." - show the schema:
```yaml
secret_schema:
  type: object
  properties:
    name: {type: string}
    value: {type: string}
    created_at: {type: string, format: date-time}
    last_accessed: {type: string, format: date-time}
  required: [name, value, created_at]
```

### 4. Error Handling Must Be Detailed
- Each tool needs specific error codes/messages
- Example for `get_secret`:
  - `SECRET_NOT_FOUND` - Secret name does not exist
  - `ACCESS_DENIED` - Requesting MAD not authorized
  - `DECRYPTION_FAILED` - Database encryption issue
  - `DATABASE_ERROR` - PostgreSQL connection failure

### 5. Security Must Be Concrete
- Don't say "use encryption" - specify algorithm (AES-256)
- Don't say "access control" - describe ACL data structure
- Include threat model (what attacks are mitigated)

### 6. Deployment Must Specify Resources
- CPU/RAM requirements
- Database schema definition
- Environment variables needed
- Container startup sequence

## Turing's Simplicity Advantage

Turing has a **simpler conceptual scope** than Hopper, making it ideal for pathfinder validation:

1. **Clear boundaries:** Key-value store with access control (no complex workflows)
2. **Discrete operations:** get/set/delete are atomic and easily testable
3. **Minimal dependencies:** Rogers only (no Horace/Fiedler complications)
4. **Well-defined success criteria:** Secret stored → can be retrieved, ACL works
5. **Foundational:** Unblocks Tier 3 MADs (Hopper) for future implementation

Use this simplicity to create an exceptionally clear, complete, and implementable V1 specification.

## Example Workflows

Include at least 2 concrete example workflows showing:
1. **Hopper requests Git PAT:**
   - Grace → Hopper: "Push changes to GitHub"
   - Hopper → Turing (via Rogers): `get_secret("github_pat")`
   - Turing checks ACL: `hopper-v1` is authorized for `github_pat`
   - Turing retrieves encrypted secret from PostgreSQL
   - Turing decrypts secret
   - Turing → Hopper: Returns secret value
   - Turing logs access event to `#logs-turing-v1`
   - Hopper uses PAT for `git push`

2. **Unauthorized access attempt:**
   - Marco → Turing: `get_secret("database_password")`
   - Turing checks ACL: `marco-v1` NOT authorized for `database_password`
   - Turing → Marco: Returns error `ACCESS_DENIED`
   - Turing logs denied access to `#logs-turing-v1` with severity `WARN`
   - McNamara observes log, correlates with other security events

## Quality Standards

Your synthesis will be reviewed by a 7-LLM panel against these criteria:

1. **Completeness:** All template sections filled, all tools defined, all dependencies listed
2. **Feasibility:** Implementable with standard libraries, realistic performance expectations
3. **Consistency:** Aligns with anchor documents, terminology consistent, dependencies match MAD_ROSTER.md
4. **Version Compatibility:** V1-appropriate (no V2/V3/V4 features)
5. **Clarity:** Unambiguous requirements, concrete examples, clear rationale

**Target:** 6/7 ACCEPT verdict (86% quorum) on first iteration.

## Output Format

Follow the exact template structure from ARCHITECTURE_GUIDELINES.md:

1. Overview
2. Thinking Engine (Imperator Configuration for V1)
3. Action Engine (MCP Server + all tools in YAML)
4. Interfaces (dependencies on Rogers, tools exposed to other MADs)
5. Data Management (PostgreSQL schema, encryption, logging format)
6. Deployment (container config, resources, startup sequence)
7. Testing Strategy (at least 2 integration scenarios)
8. Appendix (glossary, references)

## Begin Synthesis

Create the complete Turing V1 architecture document now, applying all lessons learned and adhering to all anchor package requirements.
