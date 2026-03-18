# Fiedler Requirements

- **Role**: AI Model Ecosystem Orchestrator
- **Version**: V0.10 (Updated 2025-12-21)
- **Home**: `mads/fiedler/`

---

## Update (2025-12-21): Architectural Pivot

**Per ADR-035: Direct Access AI Model Nodes**, Fiedler's role has fundamentally changed from **execution gateway** to **orchestrator and advisor**.

**What Changed:**
- **Before:** Fiedler executed LLM calls on behalf of MADs (`mcp__fiedler__fiedler_send`)
- **After:** MADs use `joshua_ai_access` library nodes directly (ClaudeSessionNode, AiderSessionNode, etc.)
- **Fiedler's new role:** Maintains Master Model Index (MMI), recommends models, orchestrates GPU resources for all workloads (AI and general compute)

**What Stayed the Same:**
- ✅ Central authority on AI model availability
- ✅ Intelligent model selection (now via recommendations, not execution)
- ✅ Multi-provider management
- ✅ Evolutionary roadmap toward full PCP

**See ADR-034 and ADR-035 for complete architecture.**

---

## 1. Overview

-   **Purpose**: Fiedler is the **AI Model Ecosystem Orchestrator**, maintaining the single source of truth for all AI model availability (Master Model Index) and providing intelligent model recommendations to MADs.
-   **V0.10 Scope Definition**: Maintain Master Model Index (MMI) of all AI models, recommend optimal models based on task requirements, orchestrate GPU resource allocation for all workloads (AI model training and general GPU compute), manage dynamic model configuration.
-   **Integration**: MADs access Fiedler's capabilities through specialized nodes in the Joshua node library ecosystem (see ADR-036 for node architecture).

---

## 2. Tool Exposure Model

This MAD follows the Direct Tool Exposure architecture (ADR-023). Its public tools are exposed directly on its MCP server and are discoverable via the Rogers registry. Any incoming communication that is not a valid MCP call for an exposed tool is routed to the Thought Engine for conversational processing (e.g., asking for advice on model selection).

> **Note on Tool List:** The tools listed in this document are a *provisional set* based on the MAD's high-level requirements. The final, authoritative list of tools, their specific parameters, and their return schemas will be defined in a dedicated Design Document prior to implementation.

---

## 3. Public Action Engine Tools (Updated 2025-12-21)

### Core Orchestration Tools

#### `fiedler_recommend_model`
- **Description:** Analyzes task requirements and recommends the optimal AI model based on constraints (cost, latency, quality). Uses Fiedler's Imperator to reason about MMI data and task characteristics.
- **Input Schema:**
    - `task_description` (string, required): Description of the task (e.g., "multi-turn code review chatbot")
    - `constraints` (dict, optional): Constraints on model selection:
        - `cost` (string): "low", "medium", "high"
        - `latency` (string): "fast", "medium", "slow"
        - `quality` (string): "high", "medium", "low"
    - `capabilities_required` (list, optional): Required capabilities (e.g., `["code-generation", "tool-calling"]`)
- **Output Schema:**
    ```json
    {
      "recommended_node": "ClaudeSessionNode",
      "model_id": "claude-sonnet-4.5",
      "provider": "Anthropic",
      "confidence": 0.95,
      "reasoning": "Claude Sonnet 4.5 excels at code review with 200k context window...",
      "alternatives": [
        {"node": "GPT5Node", "model": "gpt-5", "confidence": 0.88},
        {"node": "GeminiSessionNode", "model": "gemini-2.5-pro", "confidence": 0.82}
      ]
    }
    ```

#### `fiedler_list_available_models`
- **Description:** Returns the current Master Model Index (MMI) with all AI models and their real-time availability status.
- **Input Schema:**
    - `task_type` (string, optional): Filter by task type ("text-generation", "image-generation", "embeddings", etc.)
    - `status_filter` (string, default="online"): Filter by status ("online", "offline", "all")
    - `provider_filter` (string, optional): Filter by provider ("Anthropic", "OpenAI", "local", etc.)
- **Output Schema:**
    ```json
    {
      "models": [
        {
          "model_id": "claude-sonnet-4.5",
          "provider": "Anthropic",
          "access_node": "ClaudeSessionNode",
          "capabilities": ["text-generation", "code-generation", "vision"],
          "status": "online",
          "metadata": {
            "context_window": 200000,
            "cost_per_1k_tokens": 0.003,
            "latency_p95_ms": 1500,
            "uptime_24h": 0.997
          }
        },
        ...
      ],
      "total_count": 42,
      "online_count": 38,
      "last_update": "2025-12-21T14:30:52Z"
    }
    ```

### GPU Resource Management Tools

#### `fiedler_request_gpu_resources`
- **Description:** Request GPU resources for any GPU-intensive workload. Fiedler orchestrates with Sutherland to unload low-priority models and allocate VRAM. Handles both AI workloads (LoRA training, fine-tuning) and general GPU compute (video processing, image processing, etc.). This tool is typically called by Compute Offload Nodes (see ADR-036) like `FFmpegNode`, which implement the full service discovery and failover lifecycle.
- **Input Schema:**
    - `task` (string, required): Task identifier (e.g., "lora_training", "model_fine_tuning", "ffmpeg_video_processing", "video_transcoding", "gpu_image_processing")
    - `vram_needed_gb` (int, required): VRAM required in GB
    - `duration_minutes` (int, optional): Expected duration
    - `priority` (int, default=5): Priority level (1-10, higher = more important)
- **Output Schema:**
    ```json
    {
      "allocated": true,
      "host": "sutherland-host-01",
      "vram_available_gb": 20,
      "models_unloaded": ["stable-diffusion-xl"],
      "allocation_id": "alloc-2025-12-21-001",
      "expires_at": "2025-12-21T16:30:00Z"
    }
    ```

#### `fiedler_release_gpu_resources`
- **Description:** Release previously allocated GPU resources. Fiedler commands Sutherland to reload models.
- **Input Schema:**
    - `allocation_id` (string, required): Allocation ID from `request_gpu_resources`
- **Output Schema:**
    ```json
    {
      "released": true,
      "models_reloaded": ["stable-diffusion-xl"],
      "allocation_duration_minutes": 47
    }
    ```

### Model Health Reporting Tools

#### `fiedler_report_model_health`
- **Description:** Allow joshua_ai_access nodes to report model performance and errors to Fiedler's MMI. Used for tracking model availability and quality.
- **Input Schema:**
    - `model_id` (string, required): Model identifier
    - `response_time_ms` (float, required): Response time in milliseconds
    - `error` (string, optional): Error message if call failed
    - `tokens_used` (int, optional): Tokens consumed
- **Output Schema:**
    ```json
    {
      "recorded": true,
      "mmi_updated": true,
      "model_status": "online"
    }
    ```

### Legacy Tool (Backwards Compatibility)

#### `fiedler_send` (**DEPRECATED** - Use joshua_ai_access nodes instead)
- **Description:** Legacy tool for direct LLM execution. Maintained for backwards compatibility with V0.9 MADs. **New MADs should use `joshua_ai_access` nodes directly.**
- **Status:** Deprecated, will be removed in V1.0
- **Input Schema:**
    - `prompt` (string, required): The prompt to send to the LLM.
    - `model` (string, optional): The specific model ID to use.
    - `params` (dict, optional): Provider-specific parameters.
- **Output Schema:** `{"status": "success", "response_text": "...", "model_used": "gpt-4o"}`
- **Migration Path:** Replace with:
    ```python
    # Old:
    await mcp_call("mcp__fiedler__fiedler_send", {"prompt": "...", "model": "claude"})

    # New:
    from joshua_ai_access import ClaudeSessionNode
    node = ClaudeSessionNode()
    response = await node.build(message="...")
    ```

---

## 4. Master Model Index (MMI) Requirements

The Master Model Index is Fiedler's core responsibility - the single source of truth for all AI model availability in the Joshua ecosystem.

### 4.1 MMI Data Structure

**REQ-MMI-001:** MMI must track all AI models (local and external) with the following schema:
```python
{
  "model_id": str,              # Unique identifier (e.g., "claude-sonnet-4.5")
  "provider": str,              # Provider name (e.g., "Anthropic", "sutherland-host-01")
  "access_node": str,           # joshua_ai_access node name (e.g., "ClaudeSessionNode")
  "capabilities": List[str],    # ["text-generation", "code-generation", "vision"]
  "status": str,                # "online" | "offline" | "maintenance" | "degraded"
  "endpoint": str,              # API endpoint or Sutherland MCP address
  "metadata": {
    "context_window": int,
    "cost_per_1k_tokens": float,
    "latency_p95_ms": float,
    "quality_tier": str,        # "frontier" | "production" | "experimental"
    "max_output_tokens": int,
    "multimodal": bool
  },
  "last_health_check": str,     # ISO 8601 timestamp
  "availability_history": {
    "uptime_24h": float,        # 0.0-1.0
    "error_rate_24h": float     # 0.0-1.0
  }
}
```

**REQ-MMI-002:** MMI must be persisted in durable storage (PostgreSQL or similar)

**REQ-MMI-003:** MMI must support indexing/querying by:
- `model_id`
- `provider`
- `capabilities` (array contains)
- `status`
- `metadata.quality_tier`

### 4.2 MMI Update Mechanisms

**REQ-MMI-004:** Proactive updates (Fiedler-initiated):
- **Scheduled health checks**: Ping Sutherland instances every 5 minutes for local model status
- **Provider API polling**: Query external provider APIs daily for new models
- **Performance monitoring**: Track latency, error rates, token costs from health reports

**REQ-MMI-005:** Reactive updates (event-driven):
- **Sutherland reports**: Update MMI when Sutherland loads/unloads models
- **Health reports from joshua_ai_access nodes**: Update availability when nodes report errors
- **Manual updates**: Admin can manually mark models as offline for maintenance

### 4.3 Dynamic Configuration Management

**REQ-MMI-006:** Fiedler must poll provider APIs daily to detect new models:
```python
# Daily scheduled flow
providers = ["Together AI", "OpenAI", "Anthropic", "Google"]
for provider in providers:
    new_models = poll_provider_api(provider)
    diff = compare_with_joshua_ai_access_config(new_models)
    if diff:
        generate_config_update(diff)
        create_pr_via_starret(diff)
        update_mmi_with_new_models(status="pending")
```

**REQ-MMI-007:** Auto-generated PRs must include:
- List of new models detected
- List of deprecated models
- Updated `joshua_ai_access` configuration files
- Testing recommendations

**REQ-MMI-008:** Models added from provider API polling marked as `status="pending"` until PR merged

---

## 5. Future Evolution (Post-V0)

Fiedler's role as the **AI Model Ecosystem Orchestrator** evolves to become an intelligent, learning-enabled orchestration layer with the full Progressive Cognitive Pipeline.

*   **Phase 1 (Foundation / V0.10):** **CURRENT** - Fiedler establishes Master Model Index (MMI), provides model recommendations, orchestrates GPU resources. Maintains backwards compatibility with `fiedler_send` for V0.9 MADs.
*   **Phase 2 (Conversation / V1.0):** Fiedler is re-platformed to communicate exclusively via the Rogers Conversation Bus (pure Kafka), using `Joshua_Communicator` for all inter-MAD communication. All model recommendations and orchestration flow through the durable conversation log. **Legacy `fiedler_send` removed.**
*   **Phase 3 (Cognition / V2.0-V5.0):** Fiedler receives the full Progressive Cognitive Pipeline in four major upgrades:
    *   **V2.0 (DTR - Tier 1):** Deterministic Task Router provides microsecond-level fast-path recommendations for 60-80% of model selection queries before expensive Imperator reasoning.
    *   **V3.0 (LPPM - Tier 2):** Learned Process and Procedure Memory enables pattern-based model recommendation using historical task-model mappings, handling 15-30% of learned patterns in milliseconds.
    *   **V4.0 (CET - Tier 3):** Context Engineering Transformer analyzes task descriptions and MAD context to recommend models based on learned understanding of task complexity and requirements.
    *   **V5.0 (CRS - Tier 5):** Cognitive Response System adds anomaly detection for model performance degradation, cost anomalies, and availability patterns.
*   **Phase 4 (eMADs / V6.0):** Fiedler becomes eMAD-aware, capable of intelligently recommending models for ephemeral MAD teams and managing specialized model selection for short-lived eMAD workloads. Tracks eMAD-specific model usage patterns.
*   **Phase 5 (Autonomy / V7.0):** Fiedler integrates with Joshua MAD's strategic orchestration, receiving top-down directives for system-wide AI model usage policies, cost optimization strategies, and constitutional constraints on model selection and availability.

---