# Turing V1 Iteration 3 - Quick Fix Revision

## Result

**Iteration 2: 5/7 ACCEPT (71%)** - One vote short of 86% quorum

## Valid Critical Issue (Must Fix)

### Missing ACL Management Tools
**Reviewer:** DeepSeek (critical)

**Problem:** The document defines tools for secret operations (get_secret, set_secret, rotate_secret, delete_secret) but provides NO tools for ACL management. How does the ACL get populated? How are permissions granted or revoked?

**Fix Required:** Add two new tools to section 3 (Action Engine):

```yaml
- tool: grant_access
  description: "Grants a MAD permission to access a secret. Requires ADMIN permission on the secret."
  parameters:
    - name: mad_identity
      type: string
      required: true
      description: "The MAD to grant access to (e.g., 'hopper-v1')"
    - name: secret_name
      type: string
      required: true
      description: "The secret to grant access for"
    - name: permission
      type: string
      required: true
      description: "Permission level to grant"
      enum: [READ, WRITE, ADMIN]
  returns:
    type: object
    description: "Confirmation of ACL update"
    schema:
      type: object
      properties:
        mad_identity: {type: string}
        secret_name: {type: string}
        permission: {type: string}
        status: {type: string, const: "granted"}
      required: [mad_identity, secret_name, permission, status]
  errors:
    - code: -35001
      message: "SECRET_NOT_FOUND"
      description: "The specified secret does not exist"
    - code: -35002
      message: "ACCESS_DENIED"
      description: "Requesting MAD does not have ADMIN permission for this secret"
    - code: -35006
      message: "INVALID_PERMISSION"
      description: "Permission value must be READ, WRITE, or ADMIN"
    - code: -35004
      message: "DATABASE_ERROR"
      description: "Failed to update ACL in PostgreSQL"

- tool: revoke_access
  description: "Revokes a MAD's permission to access a secret. Requires ADMIN permission on the secret."
  parameters:
    - name: mad_identity
      type: string
      required: true
      description: "The MAD to revoke access from"
    - name: secret_name
      type: string
      required: true
      description: "The secret to revoke access for"
  returns:
    type: object
    description: "Confirmation of ACL removal"
    schema:
      type: object
      properties:
        mad_identity: {type: string}
        secret_name: {type: string}
        status: {type: string, const: "revoked"}
      required: [mad_identity, secret_name, status]
  errors:
    - code: -35001
      message: "SECRET_NOT_FOUND"
      description: "The specified secret does not exist"
    - code: -35002
      message: "ACCESS_DENIED"
      description: "Requesting MAD does not have ADMIN permission for this secret"
    - code: -35007
      message: "ACL_ENTRY_NOT_FOUND"
      description: "The specified MAD does not have access to this secret"
    - code: -35004
      message: "DATABASE_ERROR"
      description: "Failed to update ACL in PostgreSQL"
```

**Also update Appendix Error Code Registry:**
Add:
- -35006 | INVALID_PERMISSION | Permission value must be READ, WRITE, or ADMIN
- -35007 | ACL_ENTRY_NOT_FOUND | The specified ACL entry does not exist

**Also update Section 2 (Imperator) Tool Usage Protocol:**
Add mention of ACL management: "For ACL operations (`grant_access`, `revoke_access`), you must confirm the requesting MAD has ADMIN permissions for the target secret."

---

## Minor Clarifications (Optional, quick fixes)

### 1. Clarify Section 4.2 Dependencies Heading
Change heading from "Dependencies on Other MADs" to "Dependencies" and keep content as-is (already lists Rogers correctly).

### 2. Add brief note about ACL initialization
In section 5 (Data Management), add after the ACL schema:
"**ACL Initialization:** Initial ACL entries are created via the `grant_access` tool, typically invoked by an admin MAD (e.g., Grace) or during system bootstrap."

---

## Invalid Objections (DO NOT ADDRESS)

These objections from GPT-4o and DeepSeek are out of scope or factually incorrect:

1. **"Logging format violates JSON-RPC 2.0"** (DeepSeek critical) - INCORRECT. The examples DO include all required fields including top-level "id"
2. **"Insufficient threat detection workflows"** (DeepSeek critical) - Already provided in section 2
3. **"Imperator lacks algorithms for complex RBAC"** (GPT-4o critical) - Out of scope for V1 simple ACL
4. **"Dependencies not explicitly listed"** (GPT-4o important) - INCORRECT. Section 4.2 explicitly lists Rogers
5. **"Key rotation conflicts with V1 baseline"** (DeepSeek important) - It's a manual procedure, not requiring background workers
6. **"Missing detailed schemas"** (GPT-4o important) - SQL schema IS provided

---

## Task

Revise iteration 2 to add the two ACL management tools (`grant_access`, `revoke_access`) with full YAML definitions, error codes, and brief clarifications. Keep everything else unchanged.

Target: 6/7 ACCEPT on iteration 3.
