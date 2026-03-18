# ADR-035: Direct Access AI Model Nodes with Fiedler as Ecosystem Orchestrator

**Status:** Accepted
**Date:** 2025-12-21
**Deciders:** System Architect
**Supersedes:** ADR-034 (Fiedler proxy architecture)
**Updates:** ADR-015 (Sutherland role), ADR-029 (local model strategy)

---

## Context and Problem Statement

ADR-034 established a CLI-first integration strategy where Fiedler would wrap LLM provider CLIs (Claude Code, Gemini CLI, Aider, etc.) as MCP tools. While this leveraged provider innovation effectively, it created a fundamental architectural flaw:

**Fiedler became a mandatory execution proxy** for all AI model access. Every LLM call had to route through Fiedler's MCP tools (`mcp__fiedler__claude_session`, etc.).

### Problems This Created

1. **Single Point of Failure**: If Fiedler crashed or became unreachable, the entire ecosystem lost all AI capabilities
2. **Unnecessary Bottleneck**: Every AI request added latency by routing through Fiedler
3. **Architectural Inconsistency**: Violated the flow-based architecture principle where nodes should be composable, reusable units that MADs can use directly
4. **Tight Coupling**: MADs couldn't directly leverage AI capabilities; they were forced to go through Fiedler's abstraction
5. **Resource Inefficiency**: The original ADR-029 approach of embedding Ollama in each MAD would create N copies of models for N MADs on the same host

### Additional Realization

During architectural review, a critical insight emerged: **The scope extends beyond LLMs**. Joshua needs to manage access to all GPU-accelerated AI models:
- Text generation (LLMs)
- Image generation (Stable Diffusion, DALL-E)
- Speech-to-text (Whisper)
- Embeddings (Sentence Transformers)
- Vision models (LLaVA)
- And future model types

The architecture must support this heterogeneous portfolio of AI capabilities.

---

## Decision

We will adopt a **Direct Access AI Model Node** architecture where:

1. **Shared Node Library (`joshua_ai_access`)**: MADs import and use AI model access nodes directly in their Langflow flows
2. **Fiedler as Active Orchestrator**: Fiedler becomes the AI Model Ecosystem Orchestrator, maintaining the Master Model Index (MMI) as the single source of truth for all AI model availability and configuration
3. **Sutherland as Local Compute Server**: One Sutherland instance per physical host manages all local AI models, eliminating per-MAD resource duplication
4. **Expanded Scope**: Architecture supports all AI model types, not just LLMs

### Core Principles

**Direct Access, Not Proxy:**
- MADs use nodes directly; Fiedler does not execute on their behalf
- No mandatory intermediary in the critical path
- Fiedler orchestrates availability but doesn't gate access

**Active Orchestration:**
- Fiedler maintains live, dynamic state of all AI models
- Proactively manages resource allocation and configuration
- Single source of truth for model availability

**Resource Efficiency:**
- Local models managed centrally per host
- No duplication of multi-GB models in memory
- Intelligent resource allocation for competing workloads

---

## Architecture

### 1. The `joshua_ai_access` Shared Library

A new shared library providing Langflow-compatible nodes for direct AI model access.

#### Node Categories

**Text Generation Nodes:**
- `ClaudeSessionNode` - Wraps Claude Code CLI
- `GeminiSessionNode` - Wraps Gemini CLI
- `AiderSessionNode` - Wraps Aider CLI (model-agnostic code editing)
- `GrokSessionNode` - Wraps Grok CLI (real-time X/web data)
- `CodexSessionNode` - Wraps OpenAI Codex CLI
- `GPT5Node` - Direct OpenAI API access
- `SutherlandLLMNode` - Local LLM via Sutherland

**Image Generation Nodes:**
- `StableDiffusionNode` - Local or external Stable Diffusion
- `DallE3Node` - OpenAI DALL-E 3 API
- `MidjourneyNode` - Midjourney API (if available)

**Speech & Audio Nodes:**
- `WhisperNode` - Speech-to-text (local via Sutherland or OpenAI API)
- `ElevenLabsNode` - Text-to-speech via ElevenLabs API

**Embedding Nodes:**
- `SentenceTransformerNode` - Local embeddings via Sutherland
- `VoyageAINode` - Voyage AI embeddings API
- `OpenAIEmbeddingNode` - OpenAI embeddings API

**Vision Nodes:**
- `ClaudeVisionNode` - Claude with vision capabilities
- `GPT4VisionNode` - GPT-4 vision
- `LlavaNode` - Local vision model via Sutherland

#### Example Node Implementation

```python
# joshua_ai_access/src/joshua_ai_access/nodes/claude_session_node.py

from langflow.custom import CustomComponent
from typing import Dict, Any, List
import subprocess
import os

class ClaudeSessionNode(CustomComponent):
    display_name = "Claude Session"
    description = "Direct access to Claude Code CLI for multi-turn conversations"
    category = "AI Models / Text Generation"

    def build_config(self):
        return {
            "message": {
                "display_name": "Message",
                "info": "User prompt or instruction",
            },
            "session_id": {
                "display_name": "Session ID",
                "info": "Session identifier for conversation continuity",
                "value": "",
            },
            "files": {
                "display_name": "Files",
                "info": "Files to include in context (e.g., ['@requirements.md'])",
                "value": [],
            },
            "auto_compress": {
                "display_name": "Auto Compress",
                "value": True,
                "info": "Automatically trigger /compact when context full",
            },
            "model": {
                "display_name": "Model",
                "options": ["sonnet", "opus", "haiku"],
                "value": "sonnet",
            },
        }

    async def build(
        self,
        message: str,
        session_id: str = "",
        files: List[str] = [],
        auto_compress: bool = True,
        model: str = "sonnet",
    ) -> Dict[str, Any]:
        """
        Execute Claude Code CLI directly.

        Returns:
            dict: {
                "response": str,
                "session_id": str,
                "tool_calls": List[dict],
                "files_modified": List[str],
                "compressed": bool,
                "tokens_used": dict
            }
        """
        # Fetch API key from Turing (or env var initially)
        api_key = await self._get_api_key("ANTHROPIC_API_KEY")

        # Build CLI command
        cmd = ["claude"]
        if session_id:
            cmd.extend(["--resume", session_id])
        cmd.extend(["--model", model])
        cmd.append(message)

        # Set environment
        env = os.environ.copy()
        env["ANTHROPIC_API_KEY"] = api_key

        # Execute CLI
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            env=env,
            timeout=120
        )

        if result.returncode != 0:
            raise ClaudeSessionError(f"CLI error: {result.stderr}")

        # Parse response
        return self._parse_cli_output(result.stdout)

    async def _get_api_key(self, key_name: str) -> str:
        """Fetch API key from Turing or environment."""
        # Initially: read from environment
        # Future: call mcp__turing__get_secret(key_name)
        return os.getenv(key_name)

    def _parse_cli_output(self, output: str) -> Dict[str, Any]:
        """Parse Claude CLI output into structured format."""
        # Implementation details...
        pass
```

#### API Key Management

**Phase 1 (Initial):**
- Keys stored in environment variables
- Each node reads from env on initialization
- Environment managed via Docker compose or deployment config

**Phase 2 (Turing Integration):**
- Nodes call Turing MAD for runtime key fetching
- `await self.mcp_call("mcp__turing__get_secret", {"key_name": "ANTHROPIC_API_KEY"})`
- Keys never stored in node code or version control

#### MAD Usage Pattern

MADs import `joshua_ai_access` as a dependency and use nodes directly in flows:

```json
{
  "name": "chatbot_flow",
  "description": "Direct access to Claude for chatbot",
  "nodes": [
    {
      "id": "claude_1",
      "type": "ClaudeSessionNode",
      "inputs": {
        "message": "{{input.user_message}}",
        "session_id": "{{input.session_id}}",
        "files": ["@config/persona.md"],
        "auto_compress": true,
        "model": "sonnet"
      }
    }
  ],
  "edges": [],
  "output": {
    "response": "{{claude_1.response}}",
    "session_id": "{{claude_1.session_id}}"
  }
}
```

**Key Advantage:** No Fiedler in the execution path. If Fiedler is down, MADs can still access AI models directly.

---

### 2. Fiedler: The AI Model Ecosystem Orchestrator

Fiedler's role transforms from passive proxy to **active orchestrator and single source of truth** for all AI model availability.

#### 2.1 Master Model Index (MMI)

Fiedler maintains a live database of every AI model available to the Joshua ecosystem.

**MMI Schema:**

```python
# Fiedler's MMI data structure

{
  "model_id": "claude-sonnet-4.5",
  "provider": "Anthropic",
  "access_node": "ClaudeSessionNode",
  "capabilities": ["text-generation", "code-generation", "vision"],
  "status": "online",  # online | offline | maintenance | degraded
  "endpoint": "api.anthropic.com",
  "metadata": {
    "context_window": 200000,
    "cost_per_1k_tokens": 0.003,
    "latency_p95_ms": 1500,
    "quality_tier": "frontier",
    "max_output_tokens": 8192
  },
  "last_health_check": "2025-12-21T14:30:52Z",
  "availability_history": {
    "uptime_24h": 0.997,
    "error_rate_24h": 0.002
  }
}
```

**Local Model Example:**

```python
{
  "model_id": "stable-diffusion-xl",
  "provider": "sutherland-host-01",
  "access_node": "StableDiffusionNode",
  "capabilities": ["image-generation"],
  "status": "online",
  "endpoint": "mcp__sutherland__local_inference@host-01",
  "metadata": {
    "vram_required_gb": 8,
    "avg_inference_time_sec": 12,
    "cost_per_image": 0.0,
    "max_resolution": "1024x1024"
  },
  "last_health_check": "2025-12-21T14:28:15Z"
}
```

**MMI Storage:**
- Persisted in Fiedler's database (PostgreSQL or similar)
- Indexed by model_id, capabilities, provider, status
- Versioned for audit trail

#### 2.2 Orchestration Workflows

**Workflow 1: Model Recommendation**

```
MAD → Fiedler: mcp__fiedler__recommend_model(
    task_description="multi-turn chatbot with code review",
    constraints={
        "cost": "medium",
        "latency": "low",
        "quality": "high"
    }
)

Fiedler Imperator reasoning flow:
1. Query MMI: WHERE capabilities CONTAINS "text-generation"
               AND status = "online"
2. Filter by constraints:
   - cost_per_1k_tokens <= 0.01 (medium)
   - latency_p95_ms <= 2000 (low)
   - quality_tier = "frontier" (high)
3. Rank candidates by:
   - Code generation benchmarks
   - Context window size
   - Recent availability
4. Top candidate: claude-sonnet-4.5

Fiedler → MAD: {
    "recommended_node": "ClaudeSessionNode",
    "model_id": "claude-sonnet-4.5",
    "provider": "Anthropic",
    "confidence": 0.95,
    "reasoning": "Claude Sonnet 4.5 excels at code review with 200k context window, low latency, and high quality. Current uptime: 99.7%.",
    "alternatives": [
        {"node": "GPT5Node", "model": "gpt-5", "confidence": 0.88},
        {"node": "GeminiSessionNode", "model": "gemini-2.5-pro", "confidence": 0.82}
    ]
}
```

**Workflow 2: GPU Resource Allocation for LoRA Training**

```
Hopper → Fiedler: mcp__fiedler__request_gpu_resources(
    task="lora_training",
    vram_needed_gb=16,
    duration_minutes=120
)

Fiedler orchestration flow:
1. Query MMI: Find all local models on available hosts
2. Identify candidates for unloading:
   - Host: sutherland-host-01
   - Models: stable-diffusion-xl (8GB), llama-70b (12GB)
   - Total VRAM available if unloaded: 20GB > 16GB needed

3. Command Sutherland:
   await mcp_call("mcp__sutherland__unload_model", {
       "host": "host-01",
       "model_name": "stable-diffusion-xl"
   })

4. Update MMI:
   UPDATE models
   SET status = "offline",
       offline_reason = "GPU allocated to hopper:lora_training",
       offline_until = "2025-12-21T16:30:00Z"
   WHERE model_id = "stable-diffusion-xl"

5. Log allocation:
   INSERT INTO gpu_allocations (host, task, requestor, vram_gb, start_time)
   VALUES ("host-01", "lora_training", "hopper", 16, NOW())

Fiedler → Hopper: {
    "allocated": true,
    "host": "sutherland-host-01",
    "vram_available_gb": 20,
    "models_unloaded": ["stable-diffusion-xl"],
    "allocation_id": "alloc-2025-12-21-001"
}

[... Hopper completes training ...]

Hopper → Fiedler: mcp__fiedler__release_gpu_resources(
    allocation_id="alloc-2025-12-21-001"
)

Fiedler:
1. Command Sutherland:
   await mcp_call("mcp__sutherland__load_model", {
       "host": "host-01",
       "model_name": "stable-diffusion-xl"
   })

2. Update MMI:
   UPDATE models
   SET status = "online",
       offline_reason = NULL,
       offline_until = NULL
   WHERE model_id = "stable-diffusion-xl"

3. Close allocation:
   UPDATE gpu_allocations
   SET end_time = NOW(), status = "completed"
   WHERE allocation_id = "alloc-2025-12-21-001"
```

**Workflow 3: Dynamic Model Configuration Management**

```
Fiedler scheduled flow (runs daily at 02:00 UTC):

Task: Sync external provider model lists

1. Query provider APIs:
   together_models = GET https://api.together.xyz/v1/models
   openai_models = GET https://api.openai.com/v1/models
   anthropic_models = GET https://api.anthropic.com/v1/models

2. Compare with current joshua_ai_access configuration:
   current_config = READ joshua_ai_access/config/aider_models.yaml

3. Detect changes:
   new_models = [
       "meta-llama/Llama-4-Scout-17B-16E-Instruct",
       "meta-llama/Llama-4-Maverick-17B-128E-Instruct"
   ]
   deprecated_models = ["meta-llama/Llama-3.2-405B-Instruct"]

4. Generate updated configuration:
   new_config = {
       "available_models": {
           "llama-4-scout": {
               "provider": "together",
               "model_id": "meta-llama/Llama-4-Scout-17B-16E-Instruct",
               "context_window": 10000000,
               "capabilities": ["text-generation", "long-context"]
           },
           "llama-4-maverick": {
               "provider": "together",
               "model_id": "meta-llama/Llama-4-Maverick-17B-128E-Instruct",
               "context_window": 1000000,
               "capabilities": ["text-generation", "code-generation"]
           }
       }
   }

5. Create pull request via Starret:
   await mcp_call("mcp__starret__create_pull_request", {
       "repo": "joshua_ai_access",
       "branch": "fiedler/update-aider-models-2025-12-21",
       "title": "Update Aider model list with latest from Together AI",
       "description": """
           Auto-generated configuration update.

           **New Models:**
           - Llama-4-Scout (10M token context)
           - Llama-4-Maverick (1M token context)

           **Deprecated:**
           - Llama-3.2-405B-Instruct (no longer available)

           **Testing Recommendations:**
           - Verify Llama-4-Scout with large document ingestion
           - Benchmark Llama-4-Maverick code generation quality
       """,
       "files": {
           "config/aider_models.yaml": new_config,
           "CHANGELOG.md": changelog_entry
       }
   })

6. Notify Hopper for review:
   await mcp_call("mcp__hopper__review_pr", {
       "pr_url": "https://github.com/joshua/joshua_ai_access/pull/42",
       "priority": "low",
       "auto_merge_if_tests_pass": true
   })

7. Update MMI with new models (marked as "pending" until PR merged):
   INSERT INTO models (model_id, provider, status, ...)
   VALUES ("llama-4-scout", "together", "pending", ...)
```

#### 2.3 Fiedler MCP Tool Interface

**Model Recommendation:**
```python
mcp__fiedler__recommend_model(
    task_description: str,
    constraints: dict = {}  # {"cost": "low|medium|high", "latency": "fast|medium|slow", "quality": "high|medium|low"}
) -> dict
```

**Model Catalog:**
```python
mcp__fiedler__list_available_models(
    task_type: str = None,  # "text-generation", "image-generation", etc.
    status_filter: str = "online"  # "online", "offline", "all"
) -> List[dict]
```

**GPU Resource Management:**
```python
mcp__fiedler__request_gpu_resources(
    task: str,
    vram_needed_gb: int,
    duration_minutes: int = None
) -> dict

mcp__fiedler__release_gpu_resources(
    allocation_id: str
) -> dict
```

**Model Status Reporting (from Sutherland):**
```python
mcp__fiedler__report_model_status(
    model_id: str,
    status: str,  # "online", "offline", "degraded"
    metadata: dict = {}
) -> dict
```

**Health Check (from access nodes):**
```python
mcp__fiedler__report_model_health(
    model_id: str,
    response_time_ms: float,
    error: str = None
) -> dict
```

#### 2.4 MMI Update Mechanisms

**Proactive Updates:**
- **Scheduled Health Checks**: Fiedler pings Sutherland instances every 5 minutes for model status
- **Provider API Polling**: Daily sync of external provider model catalogs
- **Performance Monitoring**: Track latency, error rates, token costs from access node logs

**Reactive Updates:**
- **Sutherland Reports**: Real-time status updates when models loaded/unloaded
- **Access Node Failures**: Automatic MMI degradation when node reports errors
- **User Feedback**: MADs can report model quality issues to inform future recommendations

---

### 3. Sutherland: The Local AI Compute Server

One Sutherland instance deployed per physical host, managing all local AI models.

#### 3.1 Responsibilities

**Model Management:**
- Load/unload models in VRAM based on Fiedler's orchestration commands
- Manage model caching and preloading
- Handle concurrent inference requests with batching

**Resource Optimization:**
- Monitor GPU utilization and memory
- Optimize model placement (which models to keep loaded)
- Report capacity and availability to Fiedler

**Inference Execution:**
- Execute local inference for all model types (LLMs, image gen, embeddings, etc.)
- Provide unified interface for heterogeneous models

#### 3.2 MCP Tool Interface

**Unified Inference:**
```python
mcp__sutherland__local_inference(
    model_name: str,        # "phi3:mini", "stable-diffusion-xl", "whisper-large"
    task_type: str,         # "text-generation", "image-generation", "speech-to-text"
    input_data: dict,       # Task-specific input
    parameters: dict = {}   # Model-specific parameters
) -> dict
```

**Model Control (called by Fiedler):**
```python
mcp__sutherland__load_model(
    model_name: str,
    priority: int = 0  # Higher priority models loaded first if VRAM constrained
) -> dict

mcp__sutherland__unload_model(
    model_name: str
) -> dict
```

**Status Reporting:**
```python
mcp__sutherland__get_status() -> dict:
    """
    Returns: {
        "host_id": "sutherland-host-01",
        "gpu_info": {...},
        "loaded_models": [...],
        "vram_used_gb": 14,
        "vram_total_gb": 24,
        "active_requests": 3
    }
    """
```

#### 3.3 Deployment

**One Instance Per Host:**
```yaml
# docker-compose.yml on each compute host

services:
  sutherland:
    image: joshua/sutherland:0.7
    container_name: sutherland
    environment:
      - HOST_ID=host-01
      - FIEDLER_ENDPOINT=http://fiedler:8000
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]
    volumes:
      - /mnt/irina_storage/models:/models
      - /mnt/irina_storage/cache:/cache
```

**Resource Sharing:**
- All MADs on the same host call the shared Sutherland instance
- No per-MAD model duplication
- Example: 10 MADs on one host = 1 copy of `phi3:mini` in VRAM, not 10

---

## Architecture Diagram

```
┌───────────────────────────────────────────────────────────┐
│ Fiedler (AI Model Ecosystem Orchestrator)                 │
├───────────────────────────────────────────────────────────┤
│                                                            │
│  Master Model Index (MMI)                                  │
│  ┌──────────────────────────────────────────────────┐     │
│  │ • All AI models (local + external)               │     │
│  │ • Real-time availability status                  │     │
│  │ • Capabilities, cost, performance metadata       │     │
│  │ • Health history and uptime tracking             │     │
│  └──────────────────────────────────────────────────┘     │
│                                                            │
│  Orchestration Flows:                                      │
│  ├─ recommend_model (reasoning + MMI query)                │
│  ├─ request_gpu_resources (allocate VRAM)                  │
│  ├─ release_gpu_resources (deallocate VRAM)                │
│  ├─ Dynamic config sync (poll providers, create PRs)       │
│  └─ Health monitoring (update MMI status)                  │
│                                                            │
└────────────┬──────────────────────────────────┬───────────┘
             │ commands                         │ queries
             ↓                                  ↓
┌────────────────────────┐         ┌───────────────────────┐
│ Sutherland (per host)  │         │ External Providers    │
├────────────────────────┤         ├───────────────────────┤
│ Host: host-01          │         │ • Anthropic API       │
│                        │         │ • OpenAI API          │
│ Loaded Models:         │         │ • Together AI         │
│ • phi3:mini (4GB)      │         │ • xAI (Grok)          │
│ • sdxl (8GB)           │         │                       │
│                        │         │ Model Lists:          │
│ MCP Tools:             │         │ • Capabilities        │
│ • local_inference      │         │ • Pricing             │
│ • load_model           │         │ • Availability        │
│ • unload_model         │         │                       │
│ • get_status           │         │                       │
│                        │         │                       │
│ Reports status to →    │         │                       │
│ Fiedler every 5 min    │         │                       │
└────────────────────────┘         └───────────────────────┘
             ↑                                  ↑
             └─────────────┬────────────────────┘
                           │ uses directly
                  ┌────────────────────┐
                  │ joshua_ai_access   │
                  │ (Shared Library)   │
                  ├────────────────────┤
                  │ Nodes:             │
                  │ • ClaudeSessionNode│
                  │ • AiderSessionNode │
                  │ • StableDiffusion  │
                  │ • WhisperNode      │
                  │ • ...              │
                  └────────────────────┘
                           ↑
                           │ imports & uses in flows
                  ┌────────────────────┐
                  │ MADs               │
                  │ (Hopper, Starret,  │
                  │  Deming, etc.)     │
                  └────────────────────┘
```

---

## Consequences

### Positive

**No Single Point of Failure:**
- MADs access AI models directly via nodes
- Fiedler crash does not block AI access
- Only orchestration and optimization temporarily unavailable

**No Execution Bottleneck:**
- Requests go directly to providers or Sutherland
- Fiedler not in critical path for latency
- Scales horizontally (more hosts = more Sutherland instances)

**Architectural Purity:**
- Nodes are composable, reusable units
- Follows Langflow paradigm perfectly
- Transparent flows (can see which model node used)

**Resource Efficiency:**
- One copy of each local model per host (not per MAD)
- Massive VRAM savings (10 MADs on host = 1 model copy, not 10)
- Intelligent GPU allocation for competing workloads

**Dynamic Adaptation:**
- Fiedler tracks real-time model availability
- Recommendations reflect current state
- Auto-configuration updates via PR workflow

**Expanded Capabilities:**
- Supports all AI model types (not just LLMs)
- Unified architecture for text, vision, speech, embeddings
- Easy to add new model types

**Competitive Innovation Leverage:**
- Provider CLI improvements benefit MADs immediately (same as ADR-034)
- No manual updates needed when providers add features
- Zero maintenance burden for AI capabilities

### Negative

**More Complex Fiedler Implementation:**
- Fiedler must maintain MMI database
- Orchestration workflows add complexity
- Requires reasoning about resource allocation

**Distributed State Management:**
- MMI must stay in sync with reality
- Health checks and status updates critical
- Potential for MMI/reality divergence if Sutherland unreachable

**Initial Setup Complexity:**
- Requires deploying Sutherland on each compute host
- joshua_ai_access library needs many nodes implemented
- API key management workflow (env vars → Turing migration)

**Testing Complexity:**
- Must test nodes with actual provider CLIs/APIs
- Fiedler orchestration workflows need integration tests
- Sutherland multi-model scenarios need validation

### Neutral

**ADR-034 Partially Retained:**
- CLI-first philosophy remains valid
- Provider innovation leverage unchanged
- Only execution pattern changes (direct vs. proxy)

**Gradual Implementation:**
- Can build nodes incrementally
- Start with most-used models (Claude, GPT, Aider)
- Expand to vision/speech/embeddings later

---

## Implementation Plan

### Phase 1: Foundation (Weeks 1-2)

**joshua_ai_access Library:**
1. Create library structure and repository
2. Implement core nodes:
   - `ClaudeSessionNode`
   - `AiderSessionNode`
   - `GeminiSessionNode`
3. API key management (env vars)
4. Basic error handling

**Fiedler MMI (Initial):**
1. Design MMI database schema
2. Implement basic CRUD operations
3. Create `recommend_model` with static MMI
4. Create `list_available_models`

**Sutherland (Basic):**
1. Implement `local_inference` for Ollama (LLMs only)
2. Implement `get_status`
3. Deploy on one test host

**Testing:**
- Unit tests for each node
- Integration test: MAD flow using `ClaudeSessionNode`
- Fiedler recommendation test

### Phase 2: Orchestration (Weeks 3-4)

**Fiedler Orchestration:**
1. Implement `request_gpu_resources` / `release_gpu_resources`
2. Build orchestration flow for VRAM allocation
3. Implement health check scheduled flow
4. MMI status updates from Sutherland

**Sutherland Expansion:**
1. Implement `load_model` / `unload_model`
2. Add support for Stable Diffusion (image generation)
3. Status reporting to Fiedler
4. Multi-host deployment

**joshua_ai_access Expansion:**
5. Add `StableDiffusionNode`
6. Add `SutherlandLLMNode` (for explicit local model use)
7. Implement health reporting to Fiedler

**Testing:**
- GPU allocation scenario test
- Multi-MAD concurrent access test
- Model load/unload cycle test

### Phase 3: Dynamic Configuration (Weeks 5-6)

**Fiedler Dynamic Sync:**
1. Implement provider API polling flow
2. Build configuration diff detection
3. Integrate with Starret for PR generation
4. Auto-update MMI with new models

**joshua_ai_access Maturity:**
5. Add remaining nodes (Whisper, embeddings, etc.)
6. Implement Turing integration for API keys
7. Performance optimization (caching, connection pooling)

**Documentation:**
8. Node usage guide for MAD developers
9. Fiedler orchestration documentation
10. Sutherland deployment guide

**Testing:**
11. End-to-end workflow tests
12. Load testing (multiple MADs, multiple models)
13. Failover scenario tests (Fiedler down, Sutherland down, provider down)

---

## Migration from ADR-034

### For Existing MADs

**Old Pattern (ADR-034 proxy):**
```python
# MAD calls Fiedler proxy
response = await communicator.call_tool(
    "mcp__fiedler__claude_session",
    {"message": prompt, "session_id": session_id}
)
```

**New Pattern (Direct access):**
```json
{
  "nodes": [
    {
      "type": "ClaudeSessionNode",
      "inputs": {
        "message": "{{input.prompt}}",
        "session_id": "{{input.session_id}}"
      }
    }
  ]
}
```

**Migration Steps:**
1. Add `joshua_ai_access` to MAD dependencies
2. Replace Fiedler MCP tool calls with direct access nodes in flows
3. Test flows with new nodes
4. Deploy updated MAD

### For Fiedler

**Old Implementation (ADR-034):**
- MCP tools wrapping CLI execution
- Session state management
- All LLM calls routed through Fiedler

**New Implementation:**
- Remove execution proxy tools
- Implement MMI database
- Implement orchestration workflows
- Implement consultation tools (`recommend_model`, etc.)

---

## Related Decisions

- **ADR-030**: Langflow Internal Architecture - Nodes must be Langflow-compatible
- **ADR-031**: Modular PCP Component Libraries - joshua_ai_access is similar modular library
- **ADR-032**: Fully Flow-Based Architecture - Flows compose nodes directly
- **ADR-034**: CLI-First LLM Integration Strategy - **SUPERSEDED** (proxy approach only)
  - CLI-first philosophy retained (leverage provider innovation)
  - Execution pattern changed (direct access, not proxy)
- **ADR-015**: Sutherland GPU Orchestrator - **UPDATED** (expanded role to local AI compute server)
- **ADR-029**: Local Ollama Failover Architecture - **UPDATED** (Sutherland replaces per-MAD Ollama)

---

## Success Criteria

This decision will be considered successful when:

1. ✅ **Direct Access Works**: MADs can use `ClaudeSessionNode`, `AiderSessionNode` directly in flows
2. ✅ **No Fiedler Bottleneck**: AI requests proceed even when Fiedler unavailable
3. ✅ **Resource Efficiency**: Single copy of local models per host (not per MAD)
4. ✅ **Fiedler Recommendations**: `recommend_model` provides intelligent suggestions based on live MMI
5. ✅ **GPU Orchestration**: Fiedler successfully allocates/deallocates VRAM for competing workloads
6. ✅ **Dynamic Config**: Fiedler auto-generates PRs when provider model lists change
7. ✅ **Expanded Scope**: Architecture supports vision, speech, embeddings (not just LLMs)
8. ✅ **Performance**: No measurable latency increase vs. direct provider API calls
9. ✅ **Stability**: System operates for 7+ days with no MMI/reality divergence

---

## References

- Discussion transcript: Gemini conversation on Fiedler orchestrator role
- ADR-034: Original CLI-first integration strategy (partially superseded)
- Together AI API: https://docs.together.ai/reference/models
- Anthropic API: https://docs.anthropic.com/claude/reference
- OpenAI API: https://platform.openai.com/docs/api-reference

---
