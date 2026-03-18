# Hopper V1 Architecture Review Prompt

**Date:** 2025-10-13
**Pathfinder:** Hopper V1
**Iteration:** 1
**Reviewer:** [Your Model Name]

---

## Mission

You are part of a 6-LLM review panel evaluating the synthesized V1 architecture for **Hopper - The Software Engineer MAD**. Your task is to rigorously evaluate the synthesis document against the formal review criteria and provide structured feedback.

---

## Review Criteria

You must evaluate the synthesis against **all criteria** in the `REVIEW_CRITERIA.md` document from the anchor package:

1. **Completeness Checklist:** Does the document contain all required information?
2. **Feasibility Assessment:** Can this actually be built and run?
3. **Consistency Checks:** Does the document align with the rest of the ecosystem?
4. **Version Compatibility:** Does the document build correctly on previous versions? (N/A for V1)
5. **Clarity Standards:** Is the document clear enough for a developer to implement?

---

## Your Responsibilities

- **Evaluate against ALL criteria** listed in REVIEW_CRITERIA.md
- **Be specific** in objections, citing MAD name, document section, and exact text
- **Suggest concrete resolutions**, not just identify problems
- **Assign severity:**
  - **critical:** Blocker, must be resolved before approval
  - **important:** Should be addressed to improve quality, but not a blocker
  - **minor:** Suggestion for improvement, can be addressed at synthesis engine's discretion

---

## Context Documents Provided

You have access to:
1. **synthesis.md** - The Hopper V1 architecture to be reviewed
2. **ANCHOR_OVERVIEW.md** - System vision, V1-V4 definitions
3. **SYSTEM_DIAGRAM.md** - V4 end-state architecture
4. **NON_FUNCTIONAL_REQUIREMENTS.md** - Performance, security, logging
5. **MAD_ROSTER.md** - All 13 MADs with descriptions
6. **V1_PHASE1_BASELINE.md** - Rogers + Dewey proven baseline
7. **ARCHITECTURE_GUIDELINES.md** - How to write requirements
8. **REVIEW_CRITERIA.md** - What reviewers check (this document's basis)

---

## Required Output Format

You must return **a single JSON object** conforming to the following schema:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "MAD Architecture Review",
  "type": "object",
  "properties": {
    "reviewer": {
      "type": "string",
      "description": "The name of the reviewing LLM.",
      "enum": ["gemini-2.5-pro", "gpt-4o", "deepseek-r1", "claude-3.5-sonnet", "grok-4", "llama-3.3-70b"]
    },
    "verdict": {
      "type": "string",
      "description": "The final verdict of the review.",
      "enum": ["ACCEPT", "REJECT"]
    },
    "objections": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "mad_name": {
            "type": "string",
            "description": "The name of the MAD the objection pertains to."
          },
          "document_section": {
            "type": "string",
            "description": "The specific section of the document (e.g., '3. Action Engine')."
          },
          "severity": {
            "type": "string",
            "description": "The severity of the objection.",
            "enum": ["critical", "important", "minor"]
          },
          "summary": {
            "type": "string",
            "description": "A one-sentence summary of the issue."
          },
          "detail": {
            "type": "string",
            "description": "A full explanation of the objection, citing specific text and explaining the conflict or ambiguity."
          },
          "suggested_resolution": {
            "type": "string",
            "description": "A concrete suggestion on how to fix the issue."
          }
        },
        "required": ["mad_name", "document_section", "severity", "summary", "detail", "suggested_resolution"]
      }
    }
  },
  "required": ["reviewer", "verdict", "objections"]
}
```

---

## Verdict Logic

- **REJECT:** If there is at least one objection with `severity: "critical"`
- **ACCEPT:** If there are no critical objections (important/minor objections are allowed)

---

## Special Instructions for Specific Reviewers

### For Gemini 2.5 Pro (Self-Review)
You synthesized this document. Now, with fresh context, **be your own harshest critic**. Look for:
- Ambiguities you may have introduced
- Missing specifications
- Inconsistencies with anchor documents
- Areas where a developer would need to ask for clarification

### For All Reviewers
- **Be thorough:** This is a foundation document for implementation
- **Be constructive:** Suggest how to fix issues, not just what's wrong
- **Be specific:** Quote exact text when identifying problems
- **Be objective:** Focus on technical merit, not stylistic preferences

---

## Execute Review Now

Please evaluate the `synthesis.md` document against all criteria in `REVIEW_CRITERIA.md` and return your structured JSON review.
