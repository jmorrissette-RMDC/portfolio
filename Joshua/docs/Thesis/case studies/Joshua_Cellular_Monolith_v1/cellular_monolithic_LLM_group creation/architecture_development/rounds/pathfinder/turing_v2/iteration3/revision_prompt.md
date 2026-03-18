# Turing V2 Iteration 3 - Technical Completeness Fixes

## Issues from Iteration 2 (5/7 ACCEPT, 71%)

### Valid Critical Issues (DeepSeek + GPT-4o)

**Issue #1: Missing Validation Metrics**
DeepSeek critical: Training pipeline only mentions accuracy (>90%), but review criteria require "validation metrics (accuracy, precision, recall)".

**Fix:** In Section 2.2 Training Pipeline, step 4 (Validation), update to:
```
4. **Validation:** The newly trained model is validated against a held-out test set of historical data. A model must achieve:
   - Accuracy: >95% (updated from 90% to match performance target)
   - Precision: >92% (to minimize false positives/incorrect tool selection)
   - Recall: >90% (to minimize false negatives/missed patterns)
```

**Issue #2: Missing Data Contract for Dewey**
Both reviewers: Document doesn't specify the schema of what Dewey's `search_archives` returns.

**Fix:** In Section 4.3 Data Contracts, add new subsection after ACL Schema:

```markdown
#### Dewey Log Retrieval Contract
When Turing requests logs from Dewey using `search_archives`, the returned data follows this structure:

**Request to Dewey:**
```json
{
  "method": "search_archives",
  "params": {
    "conversation_id": "#logs-turing-v1",
    "filters": {
      "level": "INFO",
      "context.source": ["imperator", null],
      "context.tool_called": {"$exists": true}
    },
    "time_range": {"start": "2023-10-01T00:00:00Z", "end": "2023-10-07T23:59:59Z"}
  }
}
```

**Response from Dewey:**
```json
{
  "result": [
    {
      "timestamp": "2023-10-27T10:00:05.123Z",
      "level": "INFO",
      "message": "Successfully granted READ access...",
      "context": {
        "requesting_mad": "grace-v1",
        "tool_called": "grant_access",
        "tool_params": {...},
        "original_request": "grant Hopper read access to prod_db_password"
      }
    }
  ]
}
```

Each log entry provides the `original_request` (natural language) and `tool_called` + `tool_params` (structured action), which become training pairs.
```

**Issue #3: Accuracy Target Conflict**
DeepSeek important: Validation uses >90% but performance target says >95%.

**Fix:** Already addressed in Issue #1 (change validation to >95%).

**Issue #4: Clarify search_archives in LPPM Section**
GPT-4o critical: Step 1 of training pipeline doesn't explicitly name the Dewey tool.

**Fix:** In Section 2.2, Training Pipeline step 1, change:
```
OLD: "Dewey periodically retrieves conversation logs from `#logs-turing-v1`, filtering..."
NEW: "Dewey's `search_archives` tool periodically retrieves conversation logs from `#logs-turing-v1`, filtering..."
```

---

## Task

Revise iteration 2 synthesis to:
1. Update validation metrics to include precision >92%, recall >90%, and fix accuracy to >95%
2. Add Dewey log retrieval data contract in Section 4.3
3. Add explicit mention of `search_archives` tool in Section 2.2 step 1
4. Keep all other V2 content unchanged

This addresses 2 critical objections from DeepSeek and 1 critical from GPT-4o.
