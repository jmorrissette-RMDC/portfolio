# Turing V1 Iteration 2 - Revision Prompt

## Context

You are revising the Turing V1 architecture specification based on feedback from a 7-LLM review panel. Iteration 1 received **3/7 ACCEPT (43% approval)**, failing the 86% quorum threshold.

The iteration 1 synthesis was high-quality and received praise for structure, completeness, and concrete examples. However, it had **4 critical objections** and **6 important objections** that must be addressed to achieve approval.

## Your Task

Revise the Turing V1 architecture document to address all critical and important objections while preserving the quality and structure of iteration 1. The target is **6/7 ACCEPT (86% quorum)** on iteration 2.

## Review Results Summary

**Iteration 1 Results:**
- **ACCEPT:** Gemini 2.5 Pro, Llama 3.3, Qwen 2.5 (3/7)
- **REJECT:** GPT-4o, DeepSeek-R1, Grok-4, GPT-4-turbo (4/7)

**Common Praise:**
- Template structure followed correctly
- Tools well-defined in YAML with schemas
- Concrete integration test scenarios
- Encryption specified (AES-256 GCM)
- Database schema provided
- Reasonable resource requirements

**Critical Issues Identified:**
1. McNamara dependency (not in V1 baseline) - **3 reviewers flagged**
2. Imperator threat detection lacks concrete details - **2 reviewers flagged**
3. ACL missing ADMIN permission - **1 reviewer flagged**
4. JSON-RPC 2.0 logging clarity - **1 reviewer flagged**

## Critical Fixes (MUST ADDRESS)

### 1. Remove McNamara Dependency ⭐⭐⭐ HIGHEST PRIORITY

**Current Problem:**
- Section 2 (Imperator Configuration) states: "initiate a high-priority conversation with McNamara in the `#ops-alerts` channel"
- Section 4.2 (Dependencies) lists: "McNamara: Turing depends on McNamara to receive and act upon security alerts"
- **McNamara is NOT in V1_PHASE1_BASELINE.md** (only Rogers + Dewey are complete)

**Required Changes:**

**In Section 2 (Thinking Engine - Threat Detection directive):**
```
OLD: "If you detect such a pattern, you will initiate a high-priority conversation with McNamara in the `#ops-alerts` channel, detailing the suspicious activity without revealing any secret data."

NEW: "If you detect such a pattern, you will log a CRITICAL-level event to `#logs-turing-v1` with comprehensive context about the suspicious activity (without revealing secret data). In future versions, McNamara will automatically monitor these critical logs and coordinate defensive responses."
```

**In Section 2 (Example Reasoning Workflow - add new threat detection example):**
Add a complete workflow showing:
1. Detect anomaly (e.g., Hopper makes 6 failed access attempts in 30 seconds)
2. Formulate threat assessment
3. Log CRITICAL event to `#logs-turing-v1` with context
4. Continue normal operations (no blocking)

**In Section 4.2 (Dependencies on Other MADs):**
```
OLD:
*   **Rogers:** Turing depends on Rogers for all communication with other MADs. It is a client of the Conversation Bus.
*   **McNamara:** Turing depends on McNamara to receive and act upon security alerts it generates.

NEW:
*   **Rogers:** Turing depends on Rogers for all communication with other MADs. It is a client of the Conversation Bus. All logs are published to Rogers-managed conversations.

(Remove McNamara entirely from this section)
```

**In Section 4.1 (Conversation Participation Patterns):**
```
OLD: *   **Initiates:** Turing initiates conversations only to report threats to McNamara in the `#ops-alerts` channel.

NEW: *   **Initiates:** Turing does not initiate conversations in V1. All threat detection is handled via CRITICAL-level log events in `#logs-turing-v1`.
```

### 2. Add Concrete Threat Detection Details

**Current Problem:**
- Threat detection mentions "unusual number of secrets", "multiple failed requests" without specific thresholds
- No examples of detection algorithms or reasoning workflows
- No false positive handling strategy

**Required Changes:**

**In Section 2 (Imperator Configuration - expand Threat Detection directive):**
```
Add after existing threat detection text:

**Threat Detection Thresholds:**
*   **Rapid Failure Pattern:** If a single MAD makes >5 failed `get_secret` attempts within 1 minute, log as CRITICAL threat (potential brute force or misconfiguration).
*   **Anomalous Volume:** If a MAD requests >10 unique secrets within 5 minutes when its ACL grants access to <5 secrets, log as WARN anomaly (potential lateral movement or privilege escalation).
*   **Credential Stuffing:** If >3 different MADs fail to access the same secret within 10 minutes, log as ERROR (potential coordinated attack).
*   **False Positive Mitigation:** Legitimate batch operations (e.g., system startup, deployment) may trigger volume alerts. Include MAD identity and timing context in logs for human review.
```

**In Section 2 (Example Reasoning Workflow - add Threat Detection example):**
```
Add after the existing success/failure examples:

**Example Reasoning Workflow (Threat Detection):**
1.  **Receive Multiple Failed Requests:** Hopper-v1 has attempted `get_secret('prod_db_password')` 6 times in the last 40 seconds. All attempts resulted in ACCESS_DENIED.
2.  **Pattern Recognition:** This exceeds the threshold of >5 failures within 1 minute.
3.  **Threat Assessment:** Possible scenarios: (a) Hopper is compromised and attempting privilege escalation, (b) Hopper has a bug causing repeated failed requests, (c) ACL is misconfigured and Hopper legitimately needs this secret.
4.  **Formulate Action Plan:**
    *   Invoke the logging tool with `level: "CRITICAL"`.
    *   Context: `{"threat_type": "rapid_failure_pattern", "mad": "hopper-v1", "secret": "prod_db_password", "attempt_count": 6, "time_window": "40_seconds", "recommended_action": "Review Hopper logs and ACL for prod_db_password"}`.
    *   Message: "Potential security threat: Hopper-v1 made 6 failed attempts to access prod_db_password in 40 seconds."
5.  **Continue Operations:** Do not block Hopper or modify ACLs autonomously. Logging enables human operators or McNamara (in future versions) to investigate and respond.
```

### 3. Expand ACL to Include ADMIN Permission

**Current Problem:**
- ACL permissions limited to `READ` and `WRITE` in SQL schema
- `rotate_secret` tool exists but no ADMIN permission to authorize it
- No YAML schema for ACL object

**Required Changes:**

**In Section 4 (Data Contracts - add ACL schema):**
```
Add after existing "ACL Data Structure (Conceptual)" section:

**ACL Entry Schema (YAML):**
​```yaml
acl_entry_schema:
  type: object
  properties:
    mad_identity:
      type: string
      description: "Unique identifier of the MAD (e.g., 'hopper-v1')"
    secret_name:
      type: string
      description: "Name of the secret this ACL entry governs"
    permission:
      type: string
      enum: [READ, WRITE, ADMIN]
      description: "READ: get_secret; WRITE: set_secret, delete_secret; ADMIN: all operations including rotate_secret"
  required: [mad_identity, secret_name, permission]
​```

**Permission Semantics:**
- **READ:** Grants access to `get_secret` for the specified secret
- **WRITE:** Grants access to `set_secret` and `delete_secret` for the specified secret
- **ADMIN:** Grants all permissions including `rotate_secret` (typically reserved for operators or admin MADs like Grace)
```

**In Section 5 (Storage Requirements - SQL schema):**
```
OLD: CHECK (permission IN ('READ', 'WRITE'))

NEW: CHECK (permission IN ('READ', 'WRITE', 'ADMIN'))
```

**In Section 3 (Tool: rotate_secret - clarify permission requirement):**
```
Add to description:
"Creates a new version of a secret and marks the previous version for deprecation. Requires ADMIN permission (not just WRITE)."

Add to errors section:
- code: -35002
  message: "ACCESS_DENIED"
  description: "The requesting MAD does not have ADMIN permission for this secret. WRITE permission is insufficient for rotation."
```

### 4. Clarify JSON-RPC 2.0 Logging

**Current Problem:**
- GPT-4o reviewer missed the logging example in section 5
- Only one example (denied access) provided
- No explicit statement about joshua_logger handling JSON-RPC formatting

**Required Changes:**

**In Section 3 (Action Engine - MCP Server Capabilities):**
```
Add paragraph:
"All logging is performed via the `joshua_logger` library, which automatically wraps log events in JSON-RPC 2.0 format. The MCP server never constructs log messages manually; it invokes `joshua_logger.log(level, message, context)`, and the library handles JSON-RPC structuring, conversation routing, and error handling."
```

**In Section 5 (Logging Format - add second example):**
```
Add before the existing "Denied Access" example:

**Example Log for a Successful Access:**
​```json
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
      "access_granted": true,
      "operation": "get_secret"
    }
  },
  "id": "log-f1e2d3c4-b5a6-7890-1234-567890fedcba"
}
​```
```

(Keep existing denied access example as the second example)

### 5. Remove CET-P Reference

**Current Problem:**
- Section 2 describes Imperator as "via CET-P, a precursor to the full V4 CET"
- V1 should not reference V4 components or precursors

**Required Change:**

**In Section 2 (Imperator Configuration):**
```
OLD: "Turing's Imperator is a dedicated LLM instance (via CET-P, a precursor to the full V4 CET) configured with a specialized system prompt"

NEW: "Turing's Imperator is a dedicated LLM instance configured with a specialized system prompt"
```

---

## Important Fixes (SHOULD ADDRESS for Quality)

### 6. Fix Document Structure to Match Template

**Current Problem:**
- Integration test scenarios under "7.2 Integration Test Scenarios"
- "8. Appendix" used for glossary
- Template requires separate "7. Testing Strategy" and "8. Example Workflows" sections

**Required Changes:**

**Restructure sections 7-9:**
```
7. Testing Strategy
   7.1 Unit Test Coverage
   [Keep existing content]

8. Example Workflows
   [Move current "7.2 Integration Test Scenarios" content here]
   8.1 Scenario 1: Successful Secret Retrieval
   8.2 Scenario 2: Unauthorized Secret Access Attempt
   8.3 Scenario 3: Secret Rotation Workflow

9. Appendix
   [Keep existing glossary]
```

### 7. Standardize Error Codes (MAD-Specific Range)

**Current Problem:**
- Error codes like `-32004` (DATABASE_ERROR) used in multiple tools
- Generic error code range conflicts with JSON-RPC standard

**Required Change:**

**In Section 9 (Appendix - add Error Code Registry):**
```
### Error Code Registry
Turing uses the MAD-specific error code range **-35000 to -35099** for all tools. This avoids conflicts with JSON-RPC standard codes (-32000 to -32999) and other MADs.

| Code | Name | Description |
|------|------|-------------|
| -35001 | SECRET_NOT_FOUND | Requested secret name does not exist |
| -35002 | ACCESS_DENIED | Requesting MAD lacks required permission |
| -35003 | DECRYPTION_FAILED | Secret corrupted or encryption key invalid |
| -35004 | DATABASE_ERROR | PostgreSQL communication failure |
| -35005 | ENCRYPTION_FAILED | Unable to encrypt provided secret value |
```

**Update all tool error codes** to use new range (-35001 through -35005).

### 8. Add Master Key Rotation Procedure

**Current Problem:**
- No procedure for rotating or revoking the master encryption key
- Threat model doesn't address compromised master key

**Required Changes:**

**In Section 6 (Deployment - add Master Key Rotation subsection):**
```
### Master Key Rotation Procedure
1. **Generate New Key:** Operator generates a new AES-256 key using a cryptographically secure random number generator
2. **Dual-Key Mode:** Update Turing configuration to accept both old and new keys during transition
3. **Decrypt-Reencrypt:** Background process iterates through `turing.secrets` table, decrypting with old key and re-encrypting with new key
4. **Version Tracking:** Update `turing.secrets.key_version` column to track which key encrypted each secret
5. **Finalize:** Once all secrets re-encrypted, remove old key from configuration and restart Turing
6. **Audit:** Log all rotation activities to `#logs-turing-v1` with WARN severity

**Recommended Rotation Frequency:** Every 90 days or immediately upon suspected compromise.
```

**In Section 5 (Threat Model - add new threat):**
```
*   **Threat:** Compromised master key; attacker gains access to the key file on host.
    *   **Mitigation:**
        - File permissions restricted to 0400 (read-only by container user)
        - Key stored outside container image
        - Regular key rotation (90-day cycle)
        - HSM integration planned for V2 for hardware-backed key protection
        - If compromise detected: Immediately rotate key using procedure in Section 6
```

### 9. Add Data Retention Policy

**Current Problem:**
- No specification of how long secrets, logs, or historical data are retained

**Required Change:**

**In Section 5 (Data Management - add Data Retention Policy subsection):**
```
### Data Retention Policy
*   **Active Secrets:** Retained indefinitely until explicitly deleted via `delete_secret` tool
*   **Deleted Secrets:** Moved to audit table (`turing.secrets_deleted`) and retained for 30 days before permanent purging (supports recovery from accidental deletion)
*   **Access Logs:** Turing's operational logs in `#logs-turing-v1` are managed by Dewey's archival policies (typically 90-day hot retention, then moved to cold storage)
*   **ACL Changes:** All ACL modifications logged permanently to `#logs-turing-v1` for compliance auditing
*   **Rotation History:** Old secret versions retained in `turing.secrets_history` table for 365 days to support rollback scenarios
```

### 10. Add Secure Key Loading Details

**Current Problem:**
- Startup sequence mentions reading master key but lacks security details

**Required Change:**

**In Section 6 (Startup Sequence - expand step 3):**
```
OLD: 3.  **Load Master Key:** The application reads the master encryption key from the file specified by `TURING_MASTER_KEY_PATH`. If the file is missing or unreadable, the container exits with an error.

NEW: 3.  **Load Master Key Securely:**
    a. Verify file exists at `TURING_MASTER_KEY_PATH`
    b. Check file permissions (must be 0400 or 0600, owned by container UID)
    c. Check file size (must be exactly 32 bytes for AES-256)
    d. Read key into memory-locked buffer (prevents swapping to disk)
    e. Validate key format (all bytes in valid range, no null bytes)
    f. Zero file descriptor immediately after reading
    g. If any checks fail: Log CRITICAL error and exit with code 1
    h. Consider: Future versions will support HSM integration for hardware-backed key storage
```

### 11. Add V0-V4 Version Alignment Statement

**Current Problem:**
- No explicit confirmation of V1-only capabilities

**Required Change:**

**In Section 1 (Overview - New in this Version):**
```
Add paragraph:
"This V1 specification strictly adheres to ANCHOR_OVERVIEW.md V1 capabilities definition: Imperator-only integration with no V2+ components (LPPM, DTR, CET). Turing V1 establishes the foundational secrets management infrastructure upon which future versions will build progressive cognitive enhancements."
```

---

## Preserved Strengths (DO NOT CHANGE)

These aspects received unanimous praise - preserve them exactly:

1. ✅ **YAML tool definitions** - Complete, with parameters, returns, schemas, and error codes
2. ✅ **Database SQL schema** - Concrete table definitions with proper constraints
3. ✅ **Integration test scenarios** - Detailed step-by-step workflows
4. ✅ **Resource requirements** - Specific CPU/RAM allocations
5. ✅ **AES-256 encryption specification** - Concrete algorithm with GCM mode
6. ✅ **System prompt directives** - Clear Imperator identity and security posture
7. ✅ **Example reasoning workflows** - Success and failure ACL check examples (add threat detection, keep these)

---

## Minor Improvements (Optional)

### 12. Error Handling Examples
Add concrete example of how `get_secret` tool implementation logs errors when SECRET_NOT_FOUND occurs. (Suggested by Llama 3.3, low priority)

### 13. Database Schema - Deleted Secrets Audit Table
Since we added data retention policy mentioning `turing.secrets_deleted`, add the SQL for this table:
```sql
CREATE TABLE turing.secrets_deleted (
    id SERIAL PRIMARY KEY,
    original_id INT NOT NULL,
    name VARCHAR(255) NOT NULL,
    deleted_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_by VARCHAR(255),
    purge_after TIMESTAMPTZ NOT NULL DEFAULT (NOW() + INTERVAL '30 days')
);
```

### 14. Secrets History Table for Rotation
Add SQL for `turing.secrets_history` mentioned in retention policy:
```sql
CREATE TABLE turing.secrets_history (
    id SERIAL PRIMARY KEY,
    secret_id INT NOT NULL REFERENCES turing.secrets(id),
    old_value_encrypted BYTEA NOT NULL,
    old_version INT NOT NULL,
    rotated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    rotated_by VARCHAR(255)
);
```

---

## Validation Checklist

Before submitting iteration 2, verify:

- [ ] McNamara removed from ALL sections (2, 4.1, 4.2)
- [ ] Threat detection has specific thresholds (3 concrete examples)
- [ ] ACL permissions include ADMIN in SQL schema and YAML schema
- [ ] Two JSON-RPC 2.0 logging examples (success + failure)
- [ ] CET-P reference removed from section 2
- [ ] Document structure: Section 7 (Testing), Section 8 (Workflows), Section 9 (Appendix)
- [ ] Error codes use -35000 range, listed in appendix registry
- [ ] Master key rotation procedure in section 6
- [ ] Data retention policy in section 5
- [ ] Secure key loading details in section 6
- [ ] V0-V4 alignment statement in section 1
- [ ] All YAML tool definitions preserved unchanged
- [ ] Database schema preserved (with additions for ADMIN, deleted secrets, history)
- [ ] Integration test scenarios preserved (moved to section 8)

---

## Target Outcome

**Goal:** 6/7 ACCEPT (86% quorum) on iteration 2

**Expected Improvements:**
- **Gemini:** Already ACCEPTED (should remain ACCEPT)
- **Llama:** Already ACCEPTED (should remain ACCEPT)
- **Qwen:** Already ACCEPTED (should remain ACCEPT)
- **DeepSeek:** REJECTED due to 3 criticals → Should flip to ACCEPT after fixes
- **Grok:** REJECTED due to 1 critical + 2 important → Should flip to ACCEPT after fixes
- **GPT-4o:** REJECTED due to 1 critical + 3 important → Should flip to ACCEPT after fixes
- **GPT-4-turbo:** REJECTED due to 1 critical + 2 important → May remain REJECT (most demanding reviewer)

Achieving 6/7 requires flipping **3 of 4 REJECT votes** to ACCEPT. The McNamara dependency fix alone should flip DeepSeek and Grok (both flagged it as critical). The combined fixes should flip GPT-4o.

---

## Begin Revision

Create the complete Turing V1 iteration 2 architecture document now, incorporating ALL critical and important fixes while preserving the praised strengths of iteration 1.
