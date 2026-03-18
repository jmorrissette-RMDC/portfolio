# Gemini Analysis Workflow Guide

**Purpose:** General-purpose process for using Gemini to analyse large codebases or document sets that exceed normal context window limits. Applies to terminology corrections, sanitization passes, code bug analysis, architectural review, or any task requiring Gemini to reason over a large body of text at once.

**The core principle:** Do not ask Gemini to read files one by one. When Gemini navigates a repo incrementally, it builds context unevenly — each file processed as it is encountered. When given a single flattened document (the Anchor Package), Gemini loads everything as one uniform context and sees the whole thing coherently at once.

***

## Prerequisites

-   `tools/flatten_repo.py` — directory flattener that produces the anchor document (see below)
-   Access to Gemini (Gemini 1.5 Pro or 2.5 Pro recommended — 1M token context)
-   `Z:\files\gemini-jobs\` job storage directory on Windows (`/mnt/storage/files/gemini-jobs/` on Linux, `/storage/files/gemini-jobs/` from inside containers — all three paths point to the same NFS share)

***

## Step 1 — Create a Job Directory

Job IDs are human-readable and date-prefixed so any job is identifiable at a glance from any session.

```
Z:\files\gemini-jobs\{YYYYMMDD-purpose}\
```

Examples:

-   `20260312-pmad-terminology`
-   `20260315-sanitize-pass-1`
-   `20260320-rogers-bug-analysis`

Create the directory before running the flattener.

***

## Step 2 — Flatten the Repo

Use `tools/flatten_repo.py` to produce the anchor document. The script walks a directory tree, skips binaries/images/lock files and excluded dirs, and outputs a single `.md` file with each text file as a fenced code block under a `## relative/path/to/file` header.

```bash
# Full repo (for sanitization or broad analysis):
python tools/flatten_repo.py \
  --root ./Joshua26 \
  --output "Z:/files/gemini-jobs/20260315-sanitize-pass-1/anchor.md"

# Docs only (for terminology or concept paper review):
python tools/flatten_repo.py \
  --root ./Joshua26/docs \
  --output "Z:/files/gemini-jobs/20260312-pmad-terminology/anchor.md"

# Specific MAD (for focused bug analysis):
python tools/flatten_repo.py \
  --root ./Joshua26/mads/rogers \
  --output "Z:/files/gemini-jobs/20260320-rogers-bug-analysis/anchor.md"

# Markdown files only:
python tools/flatten_repo.py \
  --root ./Joshua26/docs \
  --ext .md \
  --output "Z:/files/gemini-jobs/{job-id}/anchor.md"
```

The script prints a summary: files included, files skipped, total characters, approximate token count.

**Approximate token budget:** Gemini 1.5/2.5 Pro supports \~1M tokens. At \~4 characters per token, the limit is roughly 4MB of text content. The flattener's output file size reported includes markdown overhead, so use the "Approx tokens" count from the summary as the real measure.

***

## Step 3 — Write the Prompt

Write `prompt.md` in the same job directory. The prompt tells Gemini exactly what to find — the rules that govern decisions and the format to report findings in.

**A well-written prompt is as important as the anchor.** Vague prompts produce vague findings. Structured prompts produce structured findings that Claude can act on directly.

### Prompt template

```markdown
# Analysis Task: {task name}

## Context

{Brief description of the codebase and what this analysis is for.}

## Anchor Document

The attached anchor document is a flattened snapshot of {repo name}. Each section begins with:

    ## relative/path/to/file.ext

followed by the file contents in a fenced code block.

## Task

{Precise description of what Gemini should find.}

## Rules

{Decision rules for edge cases. For example:
- If X, report it as Y
- Do not flag Z because ...
- When in doubt, report and let the human decide}

## Output Format

For each finding, report:

    ### Finding N
    **File:** relative/path/to/file.ext
    **Line/Section:** {line number or section heading}
    **Current text:** {exact current text}
    **Recommended change:** {what it should say}
    **Reason:** {why this should change}

List findings in file order (same order as they appear in the anchor document).

At the end, provide a summary count: total findings by category.

## What to Ignore

{Explicit list of things Gemini should NOT flag, to reduce noise.}
```

***

## Step 4 — Load Into Gemini

1.  Open a **fresh** Gemini conversation — do not reuse an existing conversation
2.  Upload or paste the `anchor.md` as the first message
3.  Then paste the `prompt.md` instructions
4.  Let Gemini analyse and respond

**Why a fresh conversation:** Accumulated context from prior work causes drift — Gemini may over-apply patterns from earlier turns. Always start fresh for each round.

**Why upload, not paste-then-ask:** Uploading the anchor as a document gives Gemini a clean context boundary. If pasting, paste the anchor first and then the prompt in the same message so Gemini sees both at once.

***

## Step 5 — Save Gemini's Response

Save the response to:

```
Z:\files\gemini-jobs\{job-id}\round_1\response.md
```

If Gemini's response was truncated (findings mid-list), ask it to continue and append to the same file.

***

## Step 6 — Apply Corrections (Claude)

Claude reads Gemini's findings and applies precise edits to each file. Record corrections in:

```
Z:\files\gemini-jobs\{job-id}\round_1\corrections.md
```

**Corrections log format:**

```markdown
# Corrections Applied — Round 1

## {finding-description}
- **File:** relative/path/to/file.ext
- **Change:** {brief description of what was changed}
- **Status:** applied / skipped (reason)
```

***

## Step 7 — Verify (Fresh Gemini)

1.  Re-run `flatten_repo.py` on the same root → new anchor document (overwrite `anchor.md` or save as a new version)
2.  Open a **new** fresh Gemini conversation — never continue the previous one
3.  Load the new anchor and the same prompt
4.  Ask Gemini to verify: "Please check for any remaining instances of {issue}"

Save verification response to:

```
Z:\files\gemini-jobs\{job-id}\round_2\response.md
```

***

## Step 8 — Loop Until Clean

Repeat steps 6–7 until Gemini reports no remaining findings. Each round gets its own subdirectory (`round_1/`, `round_2/`, etc.).

**Typical rounds needed:**

-   1 round: simple find-and-replace (all instances are mechanical)
-   2 rounds: mixed mechanical + nuanced changes
-   3+ rounds: systemic issues requiring multiple passes

***

## Job Status File

Maintain `status.md` in the job directory throughout. This is the continuity document — if the job spans multiple sessions, `status.md` tells the next session exactly where things stand.

```markdown
# Job Status: {job-id}

**Created:** {date}
**Purpose:** {brief description}
**Current round:** {N}
**Status:** {in progress / complete}

## Round Log

### Round 1
- Anchor generated: {date}
- Gemini response saved: yes/no
- Corrections applied: {N} changes
- Summary: {brief}

### Round 2
- Re-flattened: {date}
- Gemini verification: {clean / N remaining}
- Corrections applied: {N} changes
```

***

## Job Directory Structure Reference

```
Z:\files\gemini-jobs\{job-id}\
  anchor.md          <- flattened repo (re-generated each round)
  prompt.md          <- Gemini instructions (written once, reused each round)
  status.md          <- job log; continuity doc for multi-session work
  round_1\
    response.md      <- Gemini's findings
    corrections.md   <- record of corrections Claude applied
  round_2\
    response.md      <- Gemini's verification findings
    corrections.md   <- any remaining corrections
  ...
```

***

## Storage Path Reference

The `Z:\files\` share is accessible from every machine in the ecosystem:

| Context                        | Path                              |
|--------------------------------|-----------------------------------|
| Windows (this machine)         | `Z:\files\gemini-jobs\`           |
| Linux hosts (irina, M5, Hymie) | `/mnt/storage/files/gemini-jobs/` |
| Inside containers              | `/storage/files/gemini-jobs/`     |

All three paths point to the same NFS share. Job files written on Windows are immediately readable from Linux and from containers.

***

## Reuse: This Pattern Runs Everything

The prompt changes; the workflow does not. The same loop runs:

-   **Sanitization pass** — find private IPs, credentials, internal names
-   **Bug analysis** — find code issues in a specific MAD
-   **Architectural review** — find inconsistencies across HLDs and REQ documents
