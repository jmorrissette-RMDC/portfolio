# REQ-horace: Horace MAD — Delta Requirements

**Version:** 0.1 (Phase A)
**Date:** 2026-03-05
**Status:** Draft

This document is a delta REQ. It describes only what differs from the standard MAD template baseline (`mads/_template/docs/REQ-langgraph-template.md`). All template defaults apply unless explicitly overridden here.

---

## 1. Purpose

Horace is the filesystem domain MAD. It owns the filesystem as a domain of the Joshua26 ecosystem, providing two distinct capabilities:

**Capability 1 — Knowledge Services:** Horace builds and maintains a rich, queryable knowledge base about the contents of the filesystem. For code repositories, this includes semantic search at function/class granularity and structural knowledge about code relationships (call graphs, import graphs). For general files, this includes semantic search augmented by document relationship graphs. This knowledge is exposed to other MADs and agents via MCP tools, enabling intelligent code navigation, impact analysis, and context engineering.

**Capability 2 — Filesystem Access Management:** All agent filesystem operations in the Joshua26 ecosystem are mediated through Horace. Agents do not access the filesystem directly. Horace exposes a set of MCP filesystem tools (`fs_list`, `fs_read`, `fs_write`, etc.) that enforce a policy-and-intent-based access model. Every mutating operation requires a stated intent. Decisions are made by reconciling the intent of the governing policy against the intent of the requested action. This model is defined in `docs/concepts/concept-intent-based-filesystem-management.md`.

---

## 2. Registry Allocation

| Field | Value |
|---|---|
| Name | horace |
| UID | 2037 |
| GID | 2001 (administrators) |
| Port | 9227 |
| Host | m5 |

---

## 3. MCP Interface (Phase A — Tool List)

All tool names follow the `horace_[action]` convention.

### 3.1 Knowledge Tools

#### `horace_code_search`
**Purpose:** Semantic search over indexed code. Returns the most relevant functions, classes, or code blocks matching the query. Results are scoped to a project or searched globally.

**Inputs:** `query` (string), `project` (string, optional), `limit` (int, default 10)
**Output:** Array of `{ file_path, symbol_name, symbol_type, snippet, score }`

#### `horace_code_find_callers`
**Purpose:** Structural query — find all locations in the codebase that call a given function or method. Uses the AST-derived code graph.

**Inputs:** `symbol` (string — fully qualified function/method name), `project` (string)
**Output:** Array of `{ file_path, line_number, calling_symbol, snippet }`

#### `horace_code_find_imports`
**Purpose:** Structural query — find all files that import a given module, file, or symbol.

**Inputs:** `target` (string — module or file path), `project` (string)
**Output:** Array of `{ file_path, import_statement, line_number }`

#### `horace_file_search`
**Purpose:** Hybrid semantic + relationship search over general files (`/storage/files`). Combines vector similarity with graph-based authority scoring (document links, mentions, similarity relationships).

**Inputs:** `query` (string), `limit` (int, default 10)
**Output:** Array of `{ file_path, snippet, score, related_files }`

---

### 3.2 Filesystem Tools

All filesystem tools enforce the intent-based access model. Mutating operations (`fs_write`, `fs_delete`) require a mandatory `intent` parameter. Read operations (`fs_list`, `fs_find`, `fs_read`) apply policy checks but do not require a stated intent.

#### `horace_fs_list`
**Purpose:** List the contents of a directory.

**Inputs:** `path` (string), `recursive` (bool, default false), `max_depth` (int, default 1)
**Output:** Structured list of `{ name, type, size, modified }` entries; filtered per policy.

#### `horace_fs_find`
**Purpose:** Find files matching a glob pattern within a search path.

**Inputs:** `pattern` (string), `search_path` (string, default `/`)
**Output:** Array of matching file paths; filtered per policy.

#### `horace_fs_read`
**Purpose:** Read the contents of a file, optionally bounded to a line range.

**Inputs:** `path` (string), `start_line` (int, optional), `end_line` (int, optional)
**Output:** File content string; denied with reason if policy blocks access.

#### `horace_fs_write`
**Purpose:** Write content to a file. `intent` is mandatory.

**Inputs:** `path` (string), `content` (string), `intent` (string, required), `create_if_not_exists` (bool, default false)
**Output:** Success with diff summary; or denial with reason and optional corrective suggestion.

#### `horace_fs_delete`
**Purpose:** Delete a file. `intent` is mandatory. Highest scrutiny level — structural dependency check always performed.

**Inputs:** `path` (string), `intent` (string, required)
**Output:** Success; or denial with reason (including dependency information if applicable).

---

## 4. Dependencies

### 4.1 Sutherland
- Embeddings: `llm_embeddings` tool with `m2-bert-80M-32k-retrieval` model (32k context, 768-dim vectors)
- LLM inference: Sutherland alias for the `file_manager` Executor (small, fast, rule-following model) and the Horace Imperator (reasoning model)

### 4.2 Rogers
- Conversation state for the Horace Imperator (admin conversations, policy management)
- Standard agent hydration pattern: `conv_retrieve_context` on startup

---

## 5. Container List (Phase A — Preliminary)

| Container | Role | Notes |
|---|---|---|
| `horace` | Gateway | Standard Nginx gateway; bridges joshua-net + horace-net |
| `horace-langgraph` | Primary logic | Receives all MCP requests; routes to knowledge flows or access management flows |
| `horace-redis` | Queue + cache | Async indexing job queue; DTR policy cache |
| `horace-qdrant` | Vector store | Semantic knowledge (code chunks, file chunks); per-project collections |
| `horace-neo4j` | Graph store | Structural code knowledge (AST graph) + file relationship graph + access pattern KG |
| `horace-postgres` | Policy store | Intent-based access policy records; audit log of access decisions |

---

## 6. Internal Agents

Horace hosts two internal agents within its langgraph container. These are not exposed as direct MCP tools — they are invoked internally by the routing logic.

### 6.1 Horace Imperator
- **Class:** Imperator
- **Role:** Conversational front door for complex, multi-step filesystem goals and administrator policy management
- **Activated by:** `horace_chat` tool (not listed above — to be added in Phase B)
- **Model:** Reasoning-capable alias via Sutherland
- **Responsibilities:** Policy management via natural language (translates admin instructions into policy database records); complex analytical goals (e.g., "find all security vulnerabilities in this project")

### 6.2 `file_manager` Executor
- **Class:** Executor
- **Role:** Policy enforcement for all `horace_fs_*` tool calls
- **Activated by:** Every `horace_fs_*` tool call (internal routing)
- **Model:** Small, fast, rule-following alias via Sutherland
- **Flow:** Pre-Check Router (DTR — see `concept-decision-tree-router.md`) → fast path (no LLM) or → LLM policy evaluation → execute or deny

---

## 7. Architectural Notes

### 7.1 Knowledge Indexing

Horace maintains its knowledge base through background indexing pipelines triggered by filesystem change events. Two pipelines run asynchronously via the horace-redis queue:

- **Semantic pipeline:** Chunks code at function/class level; chunks documents at paragraph/section level; generates embeddings via Sutherland `llm_embeddings`; stores vectors in horace-qdrant
- **Structural pipeline:** Parses source files using tree-sitter (AST); extracts function definitions, class definitions, imports, and call relationships; writes nodes and edges to horace-neo4j

### 7.2 Collection Strategy (Qdrant)

| Collection | Contents | Chunk level |
|---|---|---|
| `code_general` | All projects, general code queries | Function/class |
| `code_{project_name}` | Per-project, focused queries | Function/class |
| `files_general` | All content in `/storage/files` | Paragraph/section |

### 7.3 Access Decision Flow

All `horace_fs_*` calls pass through the `file_manager` Executor's StateGraph:

1. **Constitutional pre-filter** — hard-coded absolute denials (e.g., system-critical paths); executes unconditionally before the DTR
2. **DTR (Decision Tree Router)** — fast-path routing based on learned patterns and policy database lookup; routes to ALLOW, DENY, or DEFER
3. **LLM policy evaluation** (DEFER path only) — `file_manager` Executor evaluates policy intent vs action intent; produces structured decision with optional corrective suggestion
4. **Execution** (ALLOW path) — operation is performed; outcome logged to horace-neo4j access KG
5. **Denial response** (DENY path) — structured denial with reason and suggestion returned to caller

### 7.4 Access Pattern Intelligence

Every access decision is logged to horace-neo4j as a structured fact graph. A continuous background process queries this graph for statistically significant patterns (repeated deferrals that consistently result in approval). Detected patterns are surfaced to the Horace Imperator as optimisation proposals. Approved proposals are written to the horace-postgres policy store, promoting those patterns to the DTR fast path.

### 7.5 Embedding Model

Sutherland's `m2-bert-80M-32k-retrieval` model provides 32,000-token context length, enabling large, information-rich chunks. For code, this allows embedding entire classes or modules as single units when appropriate. For documents, this supports embedding long-form sections without losing coherence.
