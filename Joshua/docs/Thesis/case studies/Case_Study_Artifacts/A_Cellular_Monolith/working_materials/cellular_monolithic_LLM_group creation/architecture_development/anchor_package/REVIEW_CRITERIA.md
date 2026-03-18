## 1. Overview

This document provides the formal criteria for the LLM review panel (GPT-4o, DeepSeek-R1, Claude 3.5 Sonnet, Grok-4, Llama 3.3 70B) to evaluate synthesized MAD architecture documents. The purpose of the review is to ensure that all architectural artifacts are complete, feasible, consistent, and clear before being approved as a foundation for implementation.

---

## 2. Reviewer Responsibilities

*   Each reviewer must evaluate the synthesized documents against **all criteria** listed below.
*   Feedback must be provided using the **Structured Objection Format**.
*   Reviewers must be specific in their objections, citing the MAD, version, component, and the specific text at issue.
*   Reviewers should endeavor to suggest a concrete resolution, not just identify a problem.
*   **Critical** objections are blockers and must be resolved before the document can be approved.
*   **Important** objections are not blockers but should be addressed to improve the quality of the architecture.
*   **Minor** objections are suggestions for improvement and can be addressed at the synthesis engine's discretion.

---

## 3. Completeness Checklist

Does the document contain all required information?

*   [ ] Does the document follow the **Standardized MAD Architecture Template** from `ARCHITECTURE_GUIDELINES.md`?
*   [ ] Are all sections of the template filled out with sufficient detail?
*   [ ] Is the **Thinking Engine** evolution (Imperator, LPPM, DTR, CET) clearly defined for the specified version?
*   [ ] Are all **Action Engine** tools explicitly defined using the specified YAML format?
*   [ ] Are all **dependencies** on other MADs and infrastructure clearly listed?
*   [ ] Are there at least two concrete **Example Workflows** that illustrate the MAD's primary function?
*   [ ] For V2+ documents, is the **"Reference, Don't Repeat"** strategy correctly applied?

---

## 4. Feasibility Assessment

Can this actually be built and run?

*   [ ] Is the proposed functionality implementable with current, well-established technology and libraries?
*   [ ] Are the performance expectations outlined in `NON_FUNCTIONAL_REQUIREMENTS.md` realistic for this MAD?
*   [ ] Are the resource requirements (CPU, RAM, storage) reasonable for the described tasks?
*   [ ] For V2+ components (LPPM, DTR, CET), is the proposed training approach and data source viable? Is it clear *what* they are learning from?

---

## 5. Consistency Checks

Does the document align with the rest of the ecosystem?

*   [ ] Does the MAD's purpose and role align with the `ANCHOR_OVERVIEW.md` and `MAD_ROSTER.md`?
*   [ ] Do the interfaces and tools described for this MAD align with the dependencies other MADs have on it?
*   [ ] Do the dependencies this MAD has on others align with the tools those MADs actually expose? (Check for interface mismatches).
*   [ ] Is the terminology used (e.g., "Conversation Bus," "Action Engine") consistent with the anchor documents?
*   [ ] Do all data contracts, logging practices, and security measures adhere to the `NON_FUNCTIONAL_REQUIREMENTS.md`?

---

## 6. Version Compatibility

Does the document build correctly on previous versions?

*   [ ] For V2+ documents, do the new components integrate cleanly with the existing V1 (or prior) architecture?
*   [ ] Is the upgrade path clear? Are there any breaking changes that need to be addressed?
*   [ ] Does the new functionality introduce any conflicts with existing behaviors?

---

## 7. Clarity Standards

Is the document clear enough for a developer to implement?

*   [ ] Does the document meet the **"Deployable" Definition** from `ARCHITECTURE_GUIDELINES.md`?
*   [ ] Are the requirements unambiguous, or are there statements open to multiple interpretations?
*   [ ] Are the examples provided clear, concrete, and sufficient to understand the workflows?
*   [ ] Is the rationale for key design decisions explained?

---

## 8. Structured Objection Format

All reviews must be submitted as a single JSON object. The verdict must be `REJECT` if there is at least one objection with `severity: "critical"`.

### JSON Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "MAD Architecture Review",
  "type": "object",
  "properties": {
    "reviewer": {
      "type": "string",
      "description": "The name of the reviewing LLM.",
      "enum": ["gpt-4o", "deepseek-r1", "claude-3.5-sonnet", "grok-4", "llama-3.3-70b"]
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