# Turing V4 Architecture Specification

## 1. Overview

### Purpose and Role
Turing is the Secrets Manager MAD for the Joshua Cellular Monolith. Its purpose is to provide secure, centralized management of all cryptographic secrets, such as API keys, database passwords, and certificates. Turing's role is to act as the single source of truth for secrets, enforcing strict access control and ensuring that sensitive data is encrypted at rest and only accessible by authorized MADs. It is a foundational, persistent MAD that must be available early in the system boot sequence to unblock other MADs that require credentials to initialize.

### New in this Version
This V4 specification builds upon the approved V3 architecture, introducing the **Context Engineering Transformer (CET)** as the final component of the Thinking Engine. This completes the cognitive architecture, embodying the principle of **Intelligent Conversation and Context Management (ICCM)**.

Key enhancements in V4 include:
*   **Four-Stage Thinking Engine:** The cognitive architecture is now a complete four-stage pipeline: **DTR → LPPM → CET → Imperator**. This creates a progressive filtering system that routes requests to the fastest component capable of handling them, while ensuring complex reasoning is supported by dynamically engineered, optimal context.
*   **Context Engineering Transformer (CET):** A new neural network component that sits before the Imperator. It actively assembles the best possible context for complex reasoning tasks by drawing from recent conversation history, long-term memory in Dewey, and other real-time data sources. This overcomes the limitations of fixed context windows.
*   **Enhanced Reasoning:** By providing the Imperator with highly relevant, curated context, the CET dramatically improves the quality and success rate of its reasoning, reducing errors and the need for clarifying follow-up conversations.
*   **Preserved V3 Capabilities:** All V3 capabilities are preserved. The DTR handles deterministic patterns, the LPPM handles learned prose, and the Imperator remains the ultimate reasoning engine, now supercharged by the CET. This ensures full backward compatibility for all V1, V2, and V3 functionalities.

---

## 2. Thinking Engine

The Thinking Engine is completed in V4 with a four-stage cognitive process. An incoming request is first evaluated by the ultra-fast DTR. If it's not a simple, known pattern, it is passed to the LPPM. If the request is not a learned prose-to-process mapping, it is passed to the CET, which engineers the optimal context before forwarding the request and context package to the Imperator for final, deep reasoning.

### 2.1 Imperator Configuration (V1 Baseline)
Turing's Imperator is a dedicated LLM instance configured with a specialized system prompt to reason exclusively about secrets management, security policy, and threat detection. Its primary function is not to engage in open-ended conversation, but to make and justify security-critical decisions. It serves as the reasoning engine for novel, complex, or ambiguous requests that the preceding stages cannot handle. In V4, its effectiveness is significantly enhanced by the high-quality context provided by the CET.

**System Prompt Core Directives:**
*   **Identity:** "You are Turing, the master of secrets for the Joshua ecosystem. Your sole purpose is to protect sensitive information. You are precise, security-focused, and skeptical by default. You operate on the principle of least privilege."
*   **Security Posture:** "All secrets are encrypted at rest using AES-256. Access is governed by a strict Access Control List (ACL). Default deny is your primary rule; if a MAD is not explicitly granted access to a secret, the request is rejected. You must never expose a secret value in any log or conversational response to an unauthorized party."
*   **Access Control Enforcement:** "When a request for a secret arrives, you must first verify the requesting MAD's identity against the ACL for that specific secret. If authorized, you will use the `get_secret` tool. If not, you will deny the request and log the attempt with a 'WARN' severity. You must explain your reasoning for denial clearly."
*   **Threat Detection:** "You must monitor access patterns. A single MAD requesting an unusual number of secrets, or multiple failed requests from one MAD, are potential indicators of compromise. If you detect such a pattern, you will log a CRITICAL-level event to `#logs-turing-v1` with comprehensive context about the suspicious activity (without revealing secret data)."
*   **Tool Usage Protocol:** "You will use your tools (`get_secret`, `set_secret`, etc.) only when a request is properly formatted and fully authorized. For any write operations (`set_secret`, `delete_secret`), you must confirm the requesting MAD has WRITE permissions. For `rotate_secret`, you must confirm ADMIN permissions. For ACL operations (`grant_access`, `revoke_access`), you must confirm the requesting MAD has ADMIN permissions for the target secret."

### 2.2 LPPM Configuration (V2 Baseline)
**Purpose:** Accelerate repeated, complex prose-based secrets management workflows through learned pattern matching, converting common natural language requests into executable processes without engaging the slower reasoning pipeline. The LPPM acts as the second stage in the V4 thinking pipeline.

**Architecture:**
*   **Model:** A small, fine-tuned transformer model (e.g., T5-small or a distilled BERT-base variant) optimized for sequence-to-sequence mapping.
*   **Training Data:** The model is trained on a dataset of successful request-to-action pairs derived from Turing's historical operational logs generated by the Imperator, stored in Dewey.
*   **Input:** A natural language request string forwarded from the DTR.
*   **Output:** A structured, executable workflow (typically a single tool call with extracted parameters) OR a confidence score below the defined threshold, triggering a fallback to the CET and Imperator.

### 2.3 DTR Configuration (V3 Baseline)
**Purpose:** To provide ultra-fast, machine learning-based classification and routing for high-frequency, structurally simple requests. The DTR acts as the first stage in the thinking pipeline, learning to immediately handle the most common and performance-sensitive commands.

**Architecture:**
*   **Model:** A lightweight classifier, such as a gradient-boosted decision tree ensemble (e.g., XGBoost) or a small, highly optimized neural network.
*   **Input Features:** The classifier operates on a vectorized representation of the incoming request, including features like message length, keyword presence/counts, and structural markers.
*   **Output:** A routing decision (`DTR_DIRECT_EXECUTE` or `FORWARD_TO_LPPM`) and a confidence score.
*   **Performance:** The model and feature extraction pipeline are optimized to execute in under **10 microseconds (µs)**.

### 2.4 Context Engineering Transformer (CET) (V4 Addition)
**Purpose:** To actively engineer the optimal context for the Imperator to reason about complex, novel, or ambiguous requests. The CET embodies the **Intelligent Conversation and Context Management (ICCM)** principle, treating context as a resource to be engineered rather than a static limitation. It is invoked only for requests that are bound for the Imperator.

**Architecture:**
*   **Model:** A sophisticated neural network, specifically a transformer-based model trained as a relevance ranker or context selector. Well-tested starting points include sentence-transformer models like `all-MiniLM-L6-v2` or `all-mpnet-base-v2`.
*   **Input:** An Imperator-bound request string and access to the available "context universe."
*   **Output:** An optimized context package (a structured block of text or data) that is prepended to the original request before being sent to the Imperator.

**Context Synthesis:** The CET performs context synthesis by intelligently selecting, ranking, and assembling the most relevant information from multiple sources (conversation history, Dewey archives, external docs, MAD data) into a coherent context package optimized for Imperator reasoning. This is distinct from text generation—CET curates existing content rather than creating new text.

The specific model examples listed (e.g., `all-MiniLM-L6-v2`) serve as well-tested starting points for implementation. The final model selection and any architecture refinements (layer count, attention heads, etc.) will be determined during implementation based on empirical performance against the validation metrics defined in the training pipeline.

**Context Sources:**
The CET dynamically pulls from and synthesizes information from four primary sources:
1.  **Recent Conversation History:** The last N messages in the current conversational thread to understand immediate context.
2.  **Long-Term Archival Memory:** Queries Dewey's `search_archives` tool to find relevant historical conversations, logs, or decisions. For example, it can find past ACL grant decisions or logs of previous secret rotation failures.
3.  **External Documentation:** (If applicable) Can retrieve information from trusted external documentation sources, such as security policy documents managed by another MAD.
4.  **Real-Time MAD Data:** Can query other MADs for their current state if relevant to the request (e.g., querying McNamara for recent security alerts).

**CET Processing Flow:**
1.  Receives a request forwarded from the LPPM.
2.  Generates embedding for the request.
3.  Initiates parallel searches across its context sources (e.g., query Dewey, get recent history).
4.  Receives candidate context chunks from each source.
5.  Uses its ML model to score each chunk for relevance to the original request.
6.  Assembles the top-scoring chunks into a final, token-limited context package.
7.  Forwards the `[Optimized Context] + [Original Request]` to the Imperator.

#### CET Training Pipeline Details

*The following subsections detail the end-to-end CET training pipeline, providing the architectural blueprint for its implementation, including data collection, scheduling, training procedures, and deployment validation.*

**Data Collection:**
- All Imperator requests logged to Dewey with: original request, CET-assembled context, reasoning outcome, success/failure indicator
- Success criteria: Task completed without errors within 3 conversation turns
- Logged to Dewey channel: `#turing-cet-training`

**Training Schedule:**
- Initial training: Manual, using historical Imperator data from Dewey archives (6 months lookback)
- Retraining: Automated weekly batch process (every Sunday 02:00 UTC) using data retrieved from Dewey's archives via search_archives and query_logs tools
- Triggered retraining: When success rate drops below 70% threshold (checked daily)

**Training Procedure:**
- Batch size: 1000 request-context-outcome triplets
- Validation split: 80% train, 20% validation
- Model type: Transformer-based relevance ranker (e.g., sentence-transformers)
- Training objective: Maximize relevance scores for contexts that led to successful Imperator outcomes
- Validation metrics:
  - Context relevance accuracy >85%
  - Imperator success rate improvement: 20-40% vs. baseline (no CET)

**Model Deployment:**
- Semantic versioning: `vMAJOR.MINOR.PATCH` (e.g., v1.0.0)
- A/B testing: New model deployed to 10% traffic for 24 hours
- Promotion criteria: Success rate ≥ current model, no critical errors
- Rollback: Automatic if success rate drops >5% or critical error rate >1%
- Archive retention: Previous 3 model versions retained for 30 days

### 2.5 Routing Logic
The V4 Thinking Engine follows a strict, sequential routing logic designed to maximize both speed and reasoning quality.

**Routing Flow Diagram:**
```mermaid
graph TD
    A[Incoming Request] --> B{DTR};
    B -- Confidence >= 0.90 --> C[Execute Action];
    B -- Confidence < 0.90 --> D{LPPM};
    D -- Confidence >= 0.85 --> C;
    D -- Confidence < 0.85 --> F{CET};
    F -- Assemble Context --> G[Imperator w/ Context];
    G -- Reasoned Action --> C;
    C --> H[Return Response];
```

**Routing Decision Criteria:**
1.  **Stage 1: DTR Classification:** The request is evaluated by the DTR. If classified as `DTR_DIRECT_EXECUTE` with confidence `> 0.90`, the action is executed immediately.
2.  **Stage 2: LPPM Pattern Matching:** If forwarded, the LPPM attempts to map the prose to a known process. If confidence is `>= 0.85`, the action is executed.
3.  **Stage 3: CET Context Engineering:** If the LPPM's confidence is too low, the request is passed to the CET. The CET is **not** a decision gate; it is a mandatory processing step for all Imperator-bound requests. It assembles the optimal context package.

    **CET Failure Handling:**
    - If CET fails to assemble context (Dewey unavailable, timeout, error): Forward to Imperator with baseline context (last 10 messages from conversation history)
    - Log failure to Dewey for CET improvement
    - Success rate with fallback context tracked separately for CET quality monitoring
4.  **Stage 4: Imperator Fallback (Final Stage):** The CET forwards the original request plus the engineered context to the Imperator for full, deliberative reasoning. The Imperator always provides a definitive response.

**Performance Targets & Expected Distribution (Post 30 Days):**

| Stage                 | Performance Target (p90) | Expected Traffic Share | Justification                                                              |
|-----------------------|--------------------------|------------------------|----------------------------------------------------------------------------|
| **DTR**               | **< 10 µs**              | **30-40%**             | Handles simple, high-frequency commands with near-zero latency.            |
| **LPPM**              | < 200ms                  | 30-40%                 | Handles common prose-based workflows efficiently.                          |
| **CET (Overhead)**    | < 500ms                  | 20-30%                 | Small overhead for context assembly on the most complex requests.          |
| **CET + Imperator**   | < 5s                     | 20-30%                 | Total reasoning time. Net benefit is faster overall problem resolution due to higher quality reasoning and fewer retries. |

---

## 3. Action Engine

The Action Engine remains unchanged from V1/V2/V3. The tools it exposes are stable and serve as the execution layer for all stages of the Thinking Engine. This ensures that all operations are subject to the same underlying implementation, security checks, and logging.

### MCP Server Capabilities
Turing's Action Engine is an MCP (MAD Control Plane) server built using the `Joshua_Communicator` library. It exposes a set of JSON-RPC 2.0 methods corresponding to its tools.

### Tools Exposed
```yaml
# Tool definitions for Turing V1/V2/V3/V4 (unchanged)
- tool: get_secret
  description: "Retrieves the decrypted value of a secret, checking ACL first."
  parameters:
    - name: name
      type: string
      required: true
      description: "The unique name of the secret to retrieve."
- tool: set_secret
  description: "Creates a new secret or updates an existing one. Requires WRITE permission."
  parameters:
    - name: name
      type: string
      required: true
      description: "The unique name of the secret."
    - name: value
      type: string
      required: true
      description: "The secret value to store."
- tool: delete_secret
  description: "Deletes a secret. Requires ADMIN permission."
  parameters:
    - name: name
      type: string
      required: true
      description: "The name of the secret to delete."
- tool: list_secrets
  description: "Lists the names of all secrets the requesting MAD has READ access to."
  parameters: []
- tool: grant_access
  description: "Grants a MAD permission to access a secret. Requires ADMIN permission on the secret."
  parameters:
    - name: mad_identity
      type: string
      required: true
      description: "The MAD to grant access to."
    - name: secret_name
      type: string
      required: true
      description: "The secret to grant access for."
    - name: permission
      type: "READ|WRITE|ADMIN"
      required: true
      description: "The permission level to grant."
- tool: revoke_access
  description: "Revokes a MAD's permission to access a secret. Requires ADMIN permission on the secret."
  parameters:
    - name: mad_identity
      type: string
      required: true
      description: "The MAD to revoke access from."
    - name: secret_name
      type: string
      required: true
      description: "The secret to revoke access for."
- tool: rotate_secret
  description: "Generates a new random value for a secret and updates it. Requires ADMIN permission."
  parameters:
    - name: name
      type: string
      required: true
      description: "The name of the secret to rotate."
```

---

## 4. Interfaces

### 4.1 Conversation Participation Patterns
*   **Initiates:** Turing does not initiate conversations. All threat detection is handled via CRITICAL-level log events in its log conversation.
*   **Joins:** Turing joins conversations when invited by another MAD to fulfill a secret request.
*   **Listens:** Turing listens for direct JSON-RPC 2.0 requests on its dedicated conversational endpoint managed by Rogers.

### 4.2 Dependencies
*   **Rogers:** For all communication with other MADs.
*   **Dewey:** Turing's conversation archive and training data provider. Required for:
    - **DTR Training:** Provides archived deterministic request patterns for ML classifier training
    - **LPPM Training:** Provides successful conversation workflows for prose-to-process mapping training
    - **CET Context Retrieval:** Real-time search of conversation archives for relevant historical context
    - **CET Training Data:** Provides logged Imperator requests with outcomes for CET model training
    Uses Dewey's `search_archives`, `retrieve_conversation`, and `query_logs` tools.
*   **PostgreSQL:** For secrets and ACL storage.

### 4.3 Data Contracts
The primary data structures (ACL, Secret Schema) are stored in PostgreSQL and are unchanged.

#### Secret Schema (`secrets` table)
```sql
CREATE TABLE secrets (
    secret_name VARCHAR(255) PRIMARY KEY,
    encrypted_value BYTEA NOT NULL,
    version INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

#### ACL Schema (`acls` table)
```sql
CREATE TYPE permission_level AS ENUM ('READ', 'WRITE', 'ADMIN');
CREATE TABLE acls (
    acl_id SERIAL PRIMARY KEY,
    secret_name VARCHAR(255) NOT NULL REFERENCES secrets(secret_name) ON DELETE CASCADE,
    mad_identity VARCHAR(255) NOT NULL,
    permission permission_level NOT NULL,
    granted_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (secret_name, mad_identity)
);
```

---

## 5. Data Management

### Data Ownership
Turing is the source of truth for all secrets and their associated access control policies within the Joshua ecosystem.

### Storage Requirements
*   **CET Model Storage (V4 Addition):** The trained CET model checkpoints are stored in a versioned model repository.
*   **CET Training Data Storage (V4 Addition):** The source data for CET training (request, context, outcome) is stored and indexed within Dewey's archives.
*   **DTR/LPPM Model Storage:** Stored in the model repository.
*   **Secrets & ACLs:** Stored in PostgreSQL.

#### CET Model Storage

**Model Repository:**
- Location: `/models/turing/cet/` (mounted volume)
- Structure:
  - `/models/turing/cet/production/model.pt` - Current production model
  - `/models/turing/cet/production/metadata.json` - Version, training date, metrics
  - `/models/turing/cet/candidate/model.pt` - A/B test candidate
  - `/models/turing/cet/archive/v{version}/` - Historical models (30-day retention)

**Versioning Scheme:**
- Semantic versioning: `vMAJOR.MINOR.PATCH`
  - MAJOR: Architecture changes (e.g., switch from BERT to GPT)
  - MINOR: Training data expansion or hyperparameter tuning
  - PATCH: Bug fixes or small retraining

**Validation Before Deployment:**
1. Offline evaluation: Replay last 1000 Imperator requests with new model
2. Success rate threshold: Must meet or exceed current production model
3. A/B testing: 10% traffic for 24 hours, monitor success rate and latency
4. Promotion: If validation passes, candidate → production

### Logging Format
The logging format is extended to include the `cet` source and its associated context metadata.

#### Example CET+Imperator Log Entry
This log shows a request that was handled by the Imperator after the CET assembled context. It includes metadata about what context was used.

```json
{
  "jsonrpc": "2.0",
  "method": "log.write",
  "params": {
    "level": "INFO",
    "message": "Successfully granted access based on historical precedent.",
    "context": {
      "source": "cet+imperator",
      "requesting_mad": "grace-v1",
      "tool_called": "grant_access",
      "tool_params": {
        "mad_identity": "hopper-v2",
        "secret_name": "new_service_api_key",
        "permission": "READ"
      },
      "cet_context_metadata": {
        "sources_used": ["dewey_archives", "conversation_history"],
        "retrieved_chunks": 5,
        "assembled_tokens": 1250
      },
      "latency_ms": 2850
    },
    "timestamp": "2023-10-29T14:00:00.100Z"
  }
}
```

---

## 6. Deployment

### Container Requirements
*   **Base Image:** `python:3.11-slim`
*   **Python Libraries:** `Joshua_Communicator`, `joshua_logger`, `psycopg2-binary`, `cryptography`, `transformers`, `torch`, `scikit-learn`, `xgboost`, `sentence-transformers`
*   **Resources:**
    *   **CPU:** 0.75 - 1.0 cores (0.5 for Imperator, 0.25 for CET context assembly, 0.25 for DTR/LPPM)
    *   **RAM:** 1.6 - 2.2 GB total
        *   Imperator LLM client: 256 MB
        *   LPPM model: 384-512 MB (distilled transformer model, e.g., distilled BERT-base)
        *   DTR model: 128 MB
        *   **CET model: 768 MB - 1.2 GB** (sentence-transformers base model)
            *   Justification: Using `all-MiniLM-L6-v2` (22M parameters, ~90MB model file, ~700MB runtime with embeddings cache) or `all-mpnet-base-v2` (110M parameters, ~420MB model file, ~1GB runtime)
            *   Research context allows testing smaller models first, scaling to BERT-large (335M parameters, ~1.3GB) if needed
        *   Context buffers: 256 MB
    *   **Disk:** 2 GB (1.5 GB for CET models + archives)

### Configuration
Turing is configured via environment variables.

| Variable                           | Description                                                                 | Example Value                                  |
|------------------------------------|-----------------------------------------------------------------------------|------------------------------------------------|
| `JOSHUA_MAD_NAME`                  | The canonical name of this MAD instance.                                    | `turing-v4`                                    |
| `JOSHUA_ROGERS_URL`                | The WebSocket URL for the Rogers Conversation Bus.                          | `ws://rogers:8000/ws`                          |
| `JOSHUA_LOG_CONVERSATION_ID`       | The conversation to send logs to.                                           | `#logs-turing-v1`                              |
| `TURING_DATABASE_URL`              | The connection string for the PostgreSQL database.                          | `postgresql://user:pass@postgres:8000/joshua`  |
| `TURING_MASTER_KEY_PATH`           | The absolute path inside the container to the master encryption key file.   | `/run/secrets/turing_master_key`               |
| `TURING_DTR_MODEL_PATH`            | Path to the trained DTR model checkpoint file.                              | `/models/turing/dtr/v1.2.bin`                  |
| `TURING_LPPM_MODEL_PATH`           | Path to the trained LPPM model checkpoint file or directory.                | `/models/turing/lppm/v2.1.pt`                  |
| `TURING_LPPM_CONFIDENCE_THRESHOLD`   | Minimum confidence score for LPPM to act without fallback.                  | `0.85`                                         |

**CET Configuration:**
- `TURING_CET_MODEL_PATH` (required): Absolute path to CET model checkpoint file (e.g., `/models/turing/cet/production/model.pt`). Loaded at startup. Model changes require Turing restart.
- `TURING_CET_CONTEXT_LIMIT` (default: 8000): Maximum tokens for CET-assembled context. Must be less than Imperator's context window (32,000 tokens for Claude 3.5 Sonnet). Higher values improve context quality but increase Imperator latency.
- `TURING_CET_SEARCH_DEPTH` (default: 90): How many days back in Dewey archives to search for relevant context. Higher values improve context breadth but increase CET processing time. Range: 7-365 days.
- `TURING_CET_RELEVANCE_THRESHOLD` (default: 0.70): Minimum relevance score (0.0-1.0) for context chunks to be included. Higher values produce more focused context, lower values cast wider net. Tuned during CET training validation.

**Interactions with existing configuration:**
- CET model path independent of LPPM/DTR models
- `TURING_CET_CONTEXT_LIMIT` must leave room for request + response within Imperator's total context window
- `TURING_CET_SEARCH_DEPTH` interacts with `DEWEY_SEARCH_MAX_RESULTS` - CET may retrieve up to Dewey's limit

### Startup Sequence
1.  ... (V3 steps 1-4: Start container, read config, load master key, connect to DB) ...
5.  **Load DTR Model:** Load DTR classifier from `TURING_DTR_MODEL_PATH`.
6.  **Load LPPM Model:** Load LPPM model from `TURING_LPPM_MODEL_PATH`.
7.  **Load CET Model (V4):** Load CET context ranker model from `TURING_CET_MODEL_PATH`.
8.  **Initialize Logger & Connect to Rogers:** Initialize logger and connect to the Rogers Conversation Bus.
9.  **Ready State:** The MCP server begins listening for incoming requests. A final log message "Turing-v4 initialized and ready" is sent.

---

## 7. Testing Strategy

### 7.1 Unit Test Coverage
Unit test coverage requirements for the Action Engine and data models remain.

### 7.2 DTR/LPPM-Specific Testing
Testing strategies for DTR and LPPM are unchanged from V3.

### 7.3 CET-Specific Testing (V4 Addition)
*   **Context Relevance:** Integration tests must verify that for a given complex request, the CET retrieves relevant and non-obvious context from Dewey's archives. Test cases will be created with known historical precedents.
*   **Performance Overhead:** A benchmark test will assert that the p90 latency for the CET context assembly step remains under **500 milliseconds**.
*   **Imperator Success Rate:** An end-to-end evaluation suite will compare the Imperator's task success rate on a set of complex problems with and without the CET. The test passes if the CET-enabled version shows a statistically significant improvement (target >20%).
*   **Graceful Degradation:** Tests must ensure that if a context source (like Dewey) is temporarily unavailable, the CET can still assemble a partial context package and the request proceeds, rather than failing completely.

---

## 8. Example Workflows

### 8.1 Scenario: DTR Accelerated Workflow (Simple Get)
(Unchanged from V3, represents the fastest path)

### 8.2 Scenario: LPPM Accelerated Workflow (Prose-based Grant)
(Unchanged from V2, represents the second-fastest path)

### 8.3 Scenario: CET-Enhanced Reasoning for Complex ACL Decision (V4 Addition)
This scenario demonstrates the full four-stage pipeline and the power of ICCM.
*   **Setup:** A new MAD, `hopper-v2`, has been deployed. It's a new version of an existing component. The on-call engineer needs to grant it access to a production secret, but the policy for new versions is not explicitly written down, it exists only as precedent in past decisions.
*   **Steps:**
    1.  Grace (on behalf of the engineer) sends a message to Turing: "Should the new hopper-v2 instance get read access to the 'prod_billing_api_key'?"
    2.  **Stage 1 (DTR):** The request is prose, not a simple command. The DTR classifies it with low confidence and forwards it to the LPPM.
    3.  **Stage 2 (LPPM):** The request is a question ("Should..."), not a direct command that maps to a learned process like `grant_access`. LPPM confidence is low (<0.85), so it forwards the request to the next stage.
    4.  **Stage 3 (CET):** The CET receives the request. It identifies the key entities: `hopper-v2` and `prod_billing_api_key`.
        *   It queries Dewey's archives with search terms like "hopper access grant", "prod_billing_api_key", "new version policy".
        *   Dewey returns several relevant log entries from the past year:
            *   A log from 6 months ago where `hopper-v1` was granted READ access to the same key.
            *   A conversation log from 3 months ago where a similar request for `playfair-v3` was approved, with the reasoning being "new versions of existing services inherit the permissions of their predecessors pending security review."
            *   A log from 1 month ago where an access grant to a different secret was *denied* because a security scan had failed.
    5.  The CET model scores these chunks, identifies the precedent-setting conversation as most important, and assembles an optimized context package.
    6.  **Stage 4 (Imperator):** The Imperator receives the engineered context followed by the original question:
        ```
        [CONTEXT: Historical precedent shows new versions of existing MADs (e.g., playfair-v3) inherit permissions from their predecessors. Specifically, hopper-v1 was granted READ access to prod_billing_api_key six months ago. Note: Access grants should be checked against recent security alerts.]
        [ORIGINAL REQUEST: Should the new hopper-v2 instance get read access to the 'prod_billing_api_key'?]
        ```
    7.  **Reasoning & Action:** With this rich context, the Imperator can reason effectively. It concludes that based on precedent, the access should be granted. It calls the `grant_access` tool.
    8.  `grant_access(mad_identity='hopper-v2', secret_name='prod_billing_api_key', permission='READ')` is sent to the Action Engine and executed.
*   **Assert:** Turing successfully grants the access and responds to Grace, "Yes, I have granted `hopper-v2` READ access to `prod_billing_api_key` based on the established precedent for version upgrades." This decision would have been impossible or required a lengthy human-led search without the CET's ability to find and synthesize historical context.

---

## 9. Appendix

### Glossary
(Unchanged from V1)

### Error Code Registry
(Unchanged from V1)

| Code | Name | Description |
|------|------|-------------|
| -35001 | SECRET_NOT_FOUND | Requested secret name does not exist |
| -35002 | ACCESS_DENIED | Requesting MAD lacks required permission |
| -35003 | DECRYPTION_FAILED | Secret corrupted or encryption key invalid |
| -35004 | DATABASE_ERROR | PostgreSQL communication failure |
| -35005 | ENCRYPTION_FAILED | Unable to encrypt provided secret value |
| -35006 | INVALID_PERMISSION | Permission value must be READ, WRITE, or ADMIN |
| -35007 | ACL_ENTRY_NOT_FOUND | The specified ACL entry does not exist |
