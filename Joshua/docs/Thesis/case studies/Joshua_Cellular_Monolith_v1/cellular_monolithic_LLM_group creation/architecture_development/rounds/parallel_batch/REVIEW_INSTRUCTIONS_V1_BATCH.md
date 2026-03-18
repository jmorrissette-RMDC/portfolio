# V1 Batch Review Instructions

## Your Role

You are reviewing multiple MAD V1 architecture specifications simultaneously. Each MAD follows the same V1 pattern (Imperator-only, no LPPM/DTR/CET).

## Review Criteria (Same for All)

- **V1 = Imperator only** (single-stage reasoning)
- Complete tool set with full specifications
- Data contracts explicit
- JSON-RPC 2.0 logging
- Performance targets as V1 baseline
- Dependencies correct
- Deployable by engineer

## Output Format

Return ONE JSON object with verdict and objections for ALL MADs in this batch:

```json
{
  "reviewer": "<your-model-name>",
  "batch_verdict": "ACCEPT or REJECT",
  "mad_reviews": [
    {
      "mad_name": "<MAD name>",
      "verdict": "ACCEPT or REJECT",
      "objections": [
        {
          "document_section": "<section>",
          "severity": "critical|important|minor",
          "summary": "<one-line>",
          "detail": "<explanation>",
          "suggested_resolution": "<fix>"
        }
      ]
    }
  ]
}
```

**Batch Verdict Rules:**
- ACCEPT: All MADs individually acceptable (6+ individual ACCEPTs)
- REJECT: Too many MADs failed (3+ individual REJECTs)

Review all MADs in this batch now.
