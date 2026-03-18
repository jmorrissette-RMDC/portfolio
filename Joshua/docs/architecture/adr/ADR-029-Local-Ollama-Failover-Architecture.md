# ADR-029: Local Ollama Failover Architecture for MAD Resilience

**Status:** Accepted

**Date:** 2025-12-19

**Updated:** 2025-12-21 (Deployment changed per ADR-035: Sutherland replaces per-MAD Ollama)

**Context:**

The Joshua architecture is built on the principle of **graceful degradation**: each MAD must function independently without hard dependencies on other system components. While Fiedler (the LLM orchestration MAD) provides access to powerful external LLMs (GPT-4, Claude, Gemini), a MAD must remain operational even when Fiedler is unavailable due to network issues, maintenance, or system failures.

Prior to V0.7, MADs had a design flaw where the Thought Engine (Imperator) could not function without Fiedler, creating a single point of failure. This violated the core architectural principle that "each MAD can function without any other MAD existing, it just loses capabilities."

**Decision:**

We will implement a **dual-mode LLM architecture** in the `joshua_thought_engine` library where every MAD container includes a local Small Language Model (SLM) via Ollama as a failover path. This ensures true MAD independence while maintaining high-quality reasoning when the full system is available.

---

## Update (2025-12-21): Sutherland Deployment Model

**Per ADR-035: Direct Access AI Model Nodes**, the deployment approach has changed from **per-MAD Ollama instances** to **one Sutherland instance per host**.

### What Changed

**Before (Original ADR-029):**
- Each MAD container included Ollama service at `localhost:11434`
- 10 MADs on one host = 10 separate Ollama instances
- Each instance loaded same model = massive VRAM duplication
- Example: 10 × 4GB (phi3:mini) = 40GB VRAM

**After (ADR-035 Update):**
- One Sutherland container per physical host
- 10 MADs share 1 Sutherland instance via MCP
- Model loaded once in Sutherland's VRAM
- Example: 1 × 4GB (phi3:mini) = 4GB VRAM
- **Savings: 36GB per host**

### What Stayed the Same

✅ **Flow-controlled degradation strategy** - Flows still decide how to handle Fiedler unavailability (fail, degrade, queue)
✅ **Dual-mode architecture** - Primary path: Fiedler (external LLMs), Failover path: local models
✅ **Graceful degradation philosophy** - MADs remain operational when Fiedler down
✅ **No centralized LLM client** - Flows implement their own failover logic

### Updated Sections

- **Section 2:** Now describes Sutherland management instead of per-MAD GPU allocation
- **Section 4:** Flow examples show `mcp__sutherland__local_inference()` instead of localhost Ollama calls
- **Consequences:** Updated to reflect massive VRAM savings

### See Also

- **ADR-035:** Complete Sutherland architecture and Fiedler orchestration
- **ADR-015:** Sutherland's federated gossip protocol

---

## 1. Dual-Mode LLM Strategy

### Primary Path: Fiedler (External LLMs)
- **Default operation:** 100% of reasoning requests go through Fiedler
- **Models available:** GPT-4, Claude, Gemini, Grok, and other frontier LLMs
- **Performance:** High-quality reasoning, tool use, and complex problem-solving
- **Mechanism:** ThoughtEngine connects to Fiedler via the injected `Communicator` instance

### Failover Path: Local Models via Sutherland (Updated 2025-12-21)
- **Activation:** Only when Fiedler is unreachable (connection timeout, service down)
- **Models:** Managed by Sutherland, default `phi3:mini` (shared across MADs on host)
- **Performance:** Degraded but functional (sufficient for operational decisions)
- **Mechanism:** MADs call `mcp__sutherland__local_inference()` - Sutherland manages Ollama backend
- **Resource efficiency:** One model instance per host, not per MAD

## 2. Local Model Management via Sutherland (Updated 2025-12-21)

**Per ADR-035**, local models are now managed by **Sutherland**, the Local AI Compute Server.

### One Sutherland Per Host Architecture

- **Deployment:** One Sutherland container per physical host
- **Shared Access:** All MADs on the host call Sutherland via `mcp__sutherland__local_inference(...)`
- **Resource Efficiency:** Models loaded once in VRAM, shared by all MADs
- **No duplication:** 10 MADs = 1 model copy (not 10)

**Before (Per-MAD Ollama from original ADR-029):**
```
Host with 10 MADs:
├─ MAD 1 container (Ollama: phi3:mini = 4GB VRAM)
├─ MAD 2 container (Ollama: phi3:mini = 4GB VRAM)
├─ ...
└─ MAD 10 container (Ollama: phi3:mini = 4GB VRAM)
Total VRAM: 40GB wasted on duplicates
```

**After (Shared Sutherland per ADR-035):**
```
Host with 10 MADs:
├─ Sutherland container (manages all models)
│   └─ phi3:mini loaded once = 4GB VRAM
├─ MAD 1-10 containers (call Sutherland via MCP)
Total VRAM: 4GB (36GB saved!)
```

### Sutherland MCP Interface

Flows access local models via Sutherland's unified inference tool:

```python
# Call Sutherland for local LLM inference
response = await mcp_call(
    "mcp__sutherland__local_inference",
    {
        "model_name": "phi3:mini",
        "task_type": "text-generation",
        "input_data": {"prompt": user_prompt},
        "parameters": {"temperature": 0.7, "max_tokens": 2000}
    }
)
```

### Model Selection and Priority

Sutherland manages multiple models with priority-based loading:

- **High-priority models:** Always loaded (e.g., `phi3:mini` for failover)
- **On-demand models:** Loaded when requested, unloaded if VRAM needed
- **Orchestrated by Fiedler:** Fiedler can command Sutherland to load/unload models

Example:
```python
# Fiedler orchestrates model loading
await mcp_call("mcp__sutherland__load_model", {
    "model_name": "qwen2.5-coder:7b",
    "priority": 5
})
```

### Architecture Benefits

1. **Massive VRAM Savings:** 36GB saved on 10-MAD host
2. **Simplified Management:** One Ollama instance to monitor/update
3. **Centralized Performance:** GPU utilization optimized across all MADs
4. **Federated Resilience:** Multiple hosts = multiple Sutherlands (per ADR-015)

See **ADR-015** for Sutherland's federated gossip protocol and **ADR-035** for complete architecture.

## 3. Model Selection and Configuration (Updated 2025-12-21)

### Default Model: `phi3:mini`

**Sutherland manages model selection** - MADs request models by name via MCP.

**Rationale for phi3:mini as default:**
- **Best performance-to-size ratio:** Optimized for both GPU and CPU operation
- **Excellent instruction-following:** Critical for tool use and structured output
- **Small footprint:** 4GB VRAM when loaded
- **4K context window:** Sufficient for most operational reasoning tasks

**Alternative models available via Sutherland:**
- `qwen2.5:3b` - Stronger reasoning (validated)
- `qwen2.5-coder:7b` - Code-specialized (for code-heavy tasks)
- Any model Sutherland has access to via Ollama

### Task-Specific Model Selection

Flows can request specific models based on task requirements:

```python
# Code review task - use code-specialized model
response = await mcp_call(
    "mcp__sutherland__local_inference",
    {
        "model_name": "qwen2.5-coder:7b",  # Task-specific
        "task_type": "text-generation",
        "input_data": {"prompt": code_review_prompt},
        "parameters": {"temperature": 0.3}
    }
)

# Fast operational decision - use smallest model
response = await mcp_call(
    "mcp__sutherland__local_inference",
    {
        "model_name": "phi3:mini",  # Default, fastest
        "task_type": "text-generation",
        "input_data": {"prompt": decision_prompt}
    }
)
```

### Configuration via Sutherland

Model configuration managed at Sutherland level (not per-MAD):

```yaml
# sutherland_config.yaml (per host)
models:
  - name: phi3:mini
    priority: 100  # Always loaded (failover default)
    vram_gb: 4
  - name: qwen2.5-coder:7b
    priority: 50   # Load on-demand
    vram_gb: 6
```

**Benefits:**
- ✅ No per-MAD configuration needed
- ✅ Centralized model management
- ✅ Flows choose model per task, not per MAD

## 4. Implementation Architecture

### Flow-Based Failover Strategy

**Critical Architectural Decision**: There is **NO centralized LLM client library** that automatically handles failover. Instead, **flows decide their own degradation strategy** when Fiedler is unavailable.

**Rationale**: Different flows have different requirements when Fiedler fails:
- **Complex reasoning flows**: May require frontier LLMs and should fail rather than degrade
- **Simple summary flows**: Can work adequately with local Ollama
- **Critical decision flows**: Should queue the task for when Fiedler returns
- **Background tasks**: Can attempt Ollama, log failure, and continue

Automatic transparent failover removes flow agency to make these decisions.

### Flow Implementation Pattern

Each flow that requires LLM access implements its own failover logic:

```python
# joshua_imperator/components/plan_node.py

class PlanNode(CustomComponent):
    async def build(self, problem_statement: str, planning_depth: str) -> dict:
        # Build prompt
        prompt = self._build_planning_prompt(problem_statement, planning_depth)

        # Primary path: Try Fiedler
        try:
            response = await self._call_fiedler(
                model="claude",
                prompt=prompt,
                temperature=0.7
            )
            return self._parse_plan(response)

        except FiedlerUnavailableError:
            # Flow decides degradation strategy

            if planning_depth == "deep":
                # Deep planning requires frontier LLM - fail
                raise PlanningError("Deep planning requires Fiedler (unavailable)")

            else:
                # Shallow/medium planning can use local model via Sutherland
                logger.warning("Fiedler unavailable, using Sutherland for planning (degraded)")
                simplified_prompt = self._simplify_prompt_for_ollama(prompt)

                # UPDATED: Call Sutherland instead of localhost Ollama
                response = await self._call_sutherland(
                    model_name="phi3:mini",
                    prompt=simplified_prompt
                )
                return self._parse_plan(response)

    async def _call_fiedler(self, **kwargs):
        """Make MCP call to Fiedler"""
        return await mcp_call("mcp__fiedler__fiedler_send", **kwargs)

    async def _call_sutherland(self, model_name: str, prompt: str):
        """Call Sutherland for local inference (Updated 2025-12-21)"""
        return await mcp_call(
            "mcp__sutherland__local_inference",
            {
                "model_name": model_name,
                "task_type": "text-generation",
                "input_data": {"prompt": prompt},
                "parameters": {"temperature": 0.7}
            }
        )
```

### Common Helper Functions (Optional)

While there's no centralized client, MADs may provide utility functions for common patterns:

```python
# mad_utils/llm_helpers.py (optional, per-MAD)

async def try_fiedler_or_sutherland(
    fiedler_params: dict,
    sutherland_params: dict,
    allow_degradation: bool = True
):
    """
    Helper function for the common "try Fiedler, fallback to Sutherland" pattern.
    Flows can use this OR implement custom logic.

    Updated 2025-12-21: Now calls Sutherland instead of localhost Ollama.
    """
    try:
        return await mcp_call("mcp__fiedler__fiedler_send", **fiedler_params)
    except FiedlerUnavailableError:
        if not allow_degradation:
            raise
        logger.warning("Fiedler unavailable, using Sutherland local inference")
        return await mcp_call("mcp__sutherland__local_inference", **sutherland_params)
```

**Key Architectural Points:**
- **No joshua_llm_client library**: Removed from architecture
- **Flow-controlled degradation**: Each flow decides how to handle Fiedler unavailability
- **Shared Sutherland Instance**: All MADs on a host use the same Sutherland instance via MCP (Updated 2025-12-21)
- **Flexibility**: Flows can fail, degrade, queue, or use alternative strategies

### MAD Dockerfile Pattern (Updated 2025-12-21)

**Simplified - No Ollama Installation Needed:**

```dockerfile
FROM python:3.11-slim

# Install MAD code
COPY . /app
RUN pip install -e /app

# Start MAD (no Ollama needed - calls Sutherland via MCP)
CMD ["python", "-m", "mad_module.server_joshua"]
```

**Key Changes:**
- ❌ No Ollama installation
- ❌ No model download during build
- ❌ No startup script complexity
- ✅ Simpler, smaller containers
- ✅ MADs call Sutherland via MCP for local models

### Container Startup Pattern (Updated 2025-12-21)

**Simplified startup - just launch MAD:**

```bash
# No Ollama service management needed
# MAD calls Sutherland via MCP:
# await mcp_call("mcp__sutherland__local_inference", {...})
python -m ${MAD_MODULE}.server_joshua
```

---

<details>
<summary><strong>Original Dockerfile/Startup (Archived for Reference)</strong></summary>

*This section described per-MAD Ollama installation. Superseded by Sutherland shared deployment.*

### MAD Dockerfile Pattern (Original)

```dockerfile
FROM python:3.11-slim

# Install Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

# Install MAD code
COPY . /app
RUN pip install -e /app

# Download local model during build (prevents cold-start delays)
RUN ollama pull phi3:mini-4k-instruct-q4_0

# Start script launches Ollama, then MAD
CMD ["./start.sh"]
```

### Container Startup Pattern (Original)

```bash
#!/bin/bash
# start.sh - MAD container entrypoint

# 1. Start Ollama service in background
ollama serve &

# 2. Wait for Ollama to be ready
sleep 3

# 3. Load the configured model (GPU if available, CPU otherwise)
ollama pull ${LOCAL_MODEL:-phi3:mini-4k-instruct-q4_0}

# 4. Start the MAD application
python -m ${MAD_MODULE}.server_joshua
```

</details>

## Consequences

### Positive

1. **True MAD Independence:** Each MAD can function completely standalone
   - Survives Fiedler outages
   - Survives network partitions
   - Can bootstrap without full system infrastructure
   - **Updated 2025-12-21:** Uses shared Sutherland for local models (not embedded Ollama)

2. **No Single Point of Failure:** System degrades gracefully
   - Fiedler down → MADs switch to local reasoning via Sutherland
   - Individual MAD failure → Other MADs unaffected
   - Sutherland down → Only affects MADs on that host (federated per ADR-015)

3. **Development Flexibility:** Developers can run individual MADs
   - No need for full Fiedler deployment in dev environment
   - Faster iteration and testing
   - **Updated 2025-12-21:** Simpler container builds (no Ollama installation)

4. **Cost Optimization:** During Fiedler outages
   - No API costs for external LLM calls
   - System remains operational at lower capability

5. **Massive Resource Efficiency (Updated 2025-12-21):**
   - **One Sutherland per host** eliminates model duplication
   - 10 MADs = 1 model copy (not 10) = **36GB VRAM saved**
   - Centralized GPU management via Sutherland
   - Intelligent model loading/unloading coordinated by Fiedler

6. **Simplified Container Architecture (Updated 2025-12-21):**
   - MAD containers no longer include Ollama (~2-4GB smaller)
   - No startup complexity (no Ollama service management)
   - Faster container startup (no model loading)

7. **Task-Specific Model Selection:** Flows choose models per task
   - Code tasks use code-specialized models (`qwen2.5-coder:7b`)
   - Fast decisions use smallest models (`phi3:mini`)
   - Research tasks use reasoning-optimized models (`qwen2.5:3b`)
   - **More granular than per-MAD configuration**

### Negative

1. **~~Increased Container Size~~** (**ELIMINATED per ADR-035**)
   - Original concern: Each MAD includes Ollama + model (~2-4GB)
   - **No longer applicable:** MADs don't include Ollama, they call Sutherland
   - **Benefit:** Containers are now 2-4GB smaller

2. **~~Resource Usage~~** (**MASSIVELY IMPROVED per ADR-035**)
   - Original: 4GB VRAM per MAD × 10 MADs = 40GB
   - **Updated:** 4GB VRAM shared across all MADs via Sutherland
   - **Savings:** 36GB per host for 10 MADs

3. **Degraded Reasoning Quality:** When using local models (unchanged)
   - SLMs less capable than GPT-4/Claude
   - May struggle with complex multi-step reasoning
   - Acceptable for operational decisions, not optimal for complex tasks
   - **Mitigation:** Flow-controlled degradation (flows can choose to fail instead of degrade)

4. **~~Startup Time~~** (**ELIMINATED per ADR-035**)
   - Original concern: Container startup includes Ollama initialization (3-5 seconds)
   - **No longer applicable:** MADs don't start Ollama, they just launch
   - **Benefit:** Faster container startup

5. **Sutherland Dependency (New):**
   - MADs on a host depend on Sutherland for local failover
   - If Sutherland crashes, failover unavailable for that host
   - **Mitigation:** Federated architecture - multiple Sutherlands across hosts (ADR-015)
   - **Acceptable:** Sutherland is simpler/more stable than per-MAD Ollama instances

### Neutral

1. **Maintenance** (**SIMPLIFIED per ADR-035**)
   - Original: Each MAD must update local model versions
   - **Updated:** Models managed centrally by Sutherland (per host)
   - Only need to update Sutherland configuration, not every MAD
   - **Simpler:** One config update per host vs. N MAD updates

## Related Decisions

This ADR defines the local failover mechanism (philosophy unchanged, implementation updated):
- **ADR-015:** Sutherland Federated Gossip Protocol (**UPDATED 2025-12-21** - expanded role to Local AI Compute Server)
- **ADR-021:** Unified I/O and Logging Hub (for Communicator's role)
- **ADR-023:** Direct Tool Exposure and Deprecation of Unified Converse (for TE interaction)
- **ADR-031:** Modular PCP Component Libraries (for Imperator and other TE components that use LLM access)
- **ADR-032:** Fully Flow-Based Architecture (flows control failover strategy, not centralized library)
- **ADR-034:** CLI-First LLM Integration Strategy (defines joshua_ai_access nodes including SutherlandLLMNode)
- **ADR-035:** Direct Access AI Model Nodes (**KEY UPDATE 2025-12-21** - defines Sutherland deployment replacing per-MAD Ollama)

## External References

- `/docs/requirements/joshua_imperator_library_requirements.md` - Specifies LLM access requirements for Imperator nodes (flow-controlled failover)
- `/docs/design/MAD_Template_V0.7_Design.md` - Template implementation with dual-mode LLM
- `/docs/architecture/adr/ADR-026_Henson_Unified_Embedding_Model.md` - Selection of Henson's primary embedding model

## Appendix A: Performance Characteristics (Updated 2025-12-21)

### Sutherland Shared Inference Performance

**With Sutherland (one per host):**

| Deployment | Hardware | Throughput | Resource Usage |
|------------|----------|------------|----------------|
| GPU (Sutherland) | NVIDIA P4/P1000+ | 200-300 tok/s | 4GB VRAM (shared by all MADs) |
| CPU Fallback (Sutherland) | Modern Xeon | 30-40 tok/s | 2GB RAM (shared by all MADs) |
| Concurrent Requests | Any | Batched by Sutherland | Multiple MADs can call simultaneously |

**Key Advantage:** 10 MADs calling Sutherland use same 4GB VRAM (not 40GB)

### Model Comparison

| Model | Size (q4) | VRAM (Sutherland) | Best For |
|-------|-----------|-------------------|----------|
| phi3:mini | ~1.9GB | ~4GB total | Default, best balance, always loaded |
| qwen2.5:3b | ~2.0GB | ~4GB total | Stronger reasoning, on-demand |
| qwen2.5-coder:7b | ~4.3GB | ~6GB total | Code-specialized tasks, on-demand |

**Note:** Sutherland manages model loading/unloading based on demand and VRAM availability.

---

<details>
<summary><strong>Original Appendix A: Per-MAD Ollama Performance (Archived)</strong></summary>

### Ollama Performance by Deployment Mode (Original)

| Deployment | Hardware | Throughput | Use Case |
|------------|----------|------------|----------|
| GPU (8GB) | NVIDIA P4/P1000 | 200-300 tok/s | First 2-4 MADs, optimal performance |
| CPU (64GB RAM) | Modern Xeon | 30-40 tok/s | Overflow MADs, still functional |
| Failed (Fiedler down) | Any | Fallback active | Emergency operation |

</details>

## Appendix B: Testing Strategy (Updated 2025-12-21)

### Failover Validation with Sutherland

1. **Normal Operation Test:**
   - Start MADs with Fiedler available
   - Verify all reasoning requests go to Fiedler
   - Check Sutherland is running but idle (no inference calls)

2. **Failover Test:**
   - Stop Fiedler service
   - Send reasoning request to MAD
   - Verify automatic switch to Sutherland local inference
   - Verify warning logged: "Fiedler unavailable, using Sutherland local inference (degraded mode)"
   - Verify MCP call to `mcp__sutherland__local_inference` succeeds

3. **Recovery Test:**
   - Restart Fiedler
   - Send reasoning request
   - Verify automatic switch back to Fiedler

4. **Sutherland Shared Resource Test (New):**
   - Start 10 MADs on one host with Sutherland
   - Send failover requests from multiple MADs simultaneously
   - Verify Sutherland handles concurrent requests (batching)
   - Verify all MADs receive responses
   - Monitor: Only ONE model instance loaded in VRAM (not 10)

5. **Sutherland Failure Test (New):**
   - Stop Sutherland service
   - Stop Fiedler service (both down)
   - Send reasoning request to MAD
   - Verify MAD logs error appropriately
   - Verify MAD continues operating (flows decide degradation strategy)

---

<details>
<summary><strong>Original Appendix B: Per-MAD Testing (Archived)</strong></summary>

### Failover Validation (Original)

1. **Normal Operation Test:**
   - Start MAD with Fiedler available
   - Verify all reasoning requests go to Fiedler
   - Check Ollama is loaded but idle

2. **Failover Test:**
   - Stop Fiedler service
   - Send reasoning request to MAD
   - Verify automatic switch to local Ollama
   - Verify warning logged: "Fiedler unavailable, using local Ollama (degraded mode)"

3. **Recovery Test:**
   - Restart Fiedler
   - Send reasoning request
   - Verify automatic switch back to Fiedler

4. **GPU Allocation Test:**
   - Start MADs sequentially
   - Monitor GPU memory allocation (nvidia-smi)
   - Verify first N MADs get GPU, rest fall back to CPU
   - Verify all MADs remain functional

</details>

---

**Approved by:** [Pending]
**Implementation Target:** V0.7 Foundation Release
