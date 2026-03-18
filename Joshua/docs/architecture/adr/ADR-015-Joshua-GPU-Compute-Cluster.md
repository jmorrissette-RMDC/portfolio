# ADR-015: Establish the "Joshua AI Compute Cluster" with a Federated, Intelligent Management Model

**Status:** Accepted
**Date:** 2024 (original)
**Updated:** 2025-12-21 (Role expanded per ADR-035)

**Context:**
Joshua's architecture requires a robust strategy for managing local GPU resources for advanced cognitive functions (ADR-003, ADR-014) and general GPU compute workloads. The project's infrastructure includes a powerful, heterogeneous collection of GPUs distributed across multiple host machines. A formal architectural decision is needed to define how these resources are managed, allocated, and accessed. Key challenges include avoiding resource contention, ensuring high resilience, enabling scalability, and providing intelligent placement for GPU-dependent workloads (AI models, video processing, image processing, and other GPU-intensive tasks) for both persistent MADs and ephemeral eMADs.

**Decision:**
The local GPU hardware will be formally established as the **"Joshua GPU Compute Cluster."** Its management will be based on a **fully decentralized, federated "gossip" model** where each GPU host runs an intelligent `Sutherland` instance that acts as both a local manager and a global advisor. This cluster handles both AI model inference and general GPU compute workloads.

1.  **Federated Deployment Model ("Local Warden"):**
    *   A dedicated **`Sutherland` MAD instance will be deployed on *every host* that contains GPU resources.**
    *   Each `Sutherland` instance is the **sole and exclusive master of the GPUs on its local host.** It manages model loading, scheduling, and access for its own hardware.

2.  **Global Awareness via "Gossip Protocol":**
    *   There will be **no "Lead" Sutherland.** All instances are equal peers.
    *   Each `Sutherland` instance will periodically **broadcast its local state** (GPU utilization, free VRAM, loaded models, etc.) to a shared, well-known topic on the bus (e.g., `system.sutherland.heartbeats`).
    *   Every `Sutherland` instance will also **subscribe to this topic**, allowing each one to independently maintain a near real-time, in-memory copy of the **entire cluster's global state.** This provides "common awareness."

3.  **Sutherland's Cognitive Role (Intelligent Placement Recommender):**
    *   `Sutherland` is not just a passive state reporter; it is an intelligent placement advisor.
    *   Higher-level orchestrators (like the `Joshua` MAD for persistent deployments or the `MAD Spawner` for ephemeral ones) will **delegate placement decisions** to a `Sutherland` instance.
    *   The orchestrator will make a high-level request, e.g., `sutherland_recommend_placement(requirements={...})`.
    *   The receiving `Sutherland`'s own internal PCP/Imperator will use its global cluster view and its domain expertise to provide an **actionable recommendation** (e.g., `"Place this workload on host M5 because..."`), which the orchestrator then executes.

4.  **Centralized Model & Inference Management (Locally by each Sutherland):**
    *   Each `Sutherland` instance is responsible for managing the lifecycle of models on its local GPUs, including loading/unloading from a central repository (`Horace`) to prevent VRAM contention.
    *   It will provide access to these models via a local **Inference Server** (e.g., Triton/vLLM), returning a network endpoint to the requesting MAD.

5.  **Unified GPU Compute Management (ADR-035 Expansion):**
    *   Sutherland manages **all GPU compute workloads**, not just GPU allocation:
        -   **AI Models:**
            -   LLMs (via Ollama or other inference engines)
            -   Image generation models (Stable Diffusion, etc.)
            -   Speech models (Whisper)
            -   Embedding models (Sentence Transformers)
            -   Vision models (LLaVA)
        -   **General GPU Compute:**
            -   Video processing (FFmpeg with GPU acceleration)
            -   Image processing (GPU-accelerated operations)
            -   Any GPU-intensive workload requiring VRAM allocation
    *   Provides **unified inference interface** via `mcp__sutherland__local_inference(model_name, task_type, input_data)` for AI models
    *   Provides **GPU resource allocation** via Fiedler orchestration for general compute workloads
    *   One Sutherland instance per **physical host** (not per-MAD) eliminates model duplication
    *   Example: 10 MADs on one host = 1 copy of phi3:mini in VRAM, not 10

6.  **Integration with Fiedler GPU Orchestrator:**
    *   Reports model status to Fiedler's Master Model Index (MMI) every 5 minutes
    *   Reports GPU availability to Fiedler for resource allocation decisions
    *   Receives orchestration commands from Fiedler:
        -   `mcp__sutherland__load_model(model_name, priority)` - Load AI model into VRAM
        -   `mcp__sutherland__unload_model(model_name)` - Free VRAM for competing workloads
    *   Enables dynamic GPU allocation for all workloads (e.g., unload models for LoRA training, FFmpeg video processing, then reload after)
    *   MADs interact with Sutherland through Compute Offload Nodes (see **ADR-036**) that implement service discovery and failover patterns
    *   See **ADR-035** for complete orchestration architecture

**Consequences:**

*   **Positive:**
    *   **Maximum Resilience & No Single Point of Failure:** The decentralized gossip model means the failure of any single `Sutherland` instance or host only affects that host. Global visibility and placement recommendations can still be served by any surviving instance.
    *   **Scalability:** The architecture scales horizontally by default. Adding a new GPU host simply requires deploying a new `Sutherland` instance on it, which will automatically join the gossip protocol.
    *   **Clear Separation of Concerns:**
        *   **Orchestrators (`Joshua`, `MAD Spawner`):** Decide *what* needs to be deployed.
        *   **`Sutherland`:** Provides expert advice on *where* it should be deployed.
        *   **Container Runtime:** Executes the final placement decision.
    *   **Encapsulates Expertise:** All complex logic related to GPU hardware, model placement, workload scheduling, and resource allocation is perfectly encapsulated within the `Sutherland` MAD's domain.
    *   **Resource Efficiency (ADR-035):** One Sutherland per host eliminates massive duplication. Previously, ADR-029 proposed Ollama embedded in each MAD container - 10 MADs = 10 copies of each model. Now: 10 MADs = 1 shared copy via Sutherland. Also enables intelligent unloading of low-priority models to make room for general GPU compute workloads.
    *   **Heterogeneous Workload Support:** Single architecture manages AI models (LLMs, image generation, speech, embeddings) AND general GPU compute (FFmpeg, video processing, image processing).
    *   **Integration with joshua_ai_access:** MADs use `SutherlandLLMNode` to access local models via standardized Langflow node interface.
    *   **Unified GPU Orchestration:** Fiedler coordinates all GPU allocation through Sutherland, enabling intelligent resource sharing between AI models and general compute tasks.

*   **Negative:**
    *   **Eventual Consistency:** The global state maintained by each `Sutherland` is eventually consistent, based on the heartbeat interval. There may be a brief delay (a few seconds) for state changes to propagate. This is an acceptable trade-off for this use case.

*   **Neutral:**
    *   This ADR defines a highly sophisticated, resilient, and scalable architecture for managing Joshua's most critical compute resources, fully aligning with the "Cellular Monolith" and distributed cognition principles.

---

## Integration with ADR-035: Local GPU Compute Server (2025-12-21)

Per **ADR-035: Direct Access AI Model Nodes**, Sutherland's role has expanded from GPU resource manager to **Local GPU Compute Server**.

### Expanded Responsibilities

**1. AI Model Management:**
- LLMs (Ollama, vLLM, custom inference engines)
- Image Generation (Stable Diffusion, ControlNet)
- Speech-to-Text (Whisper)
- Text-to-Speech (Coqui TTS, ElevenLabs self-hosted)
- Embeddings (Sentence Transformers, instructor models)
- Vision (LLaVA, CLIP)

**2. General GPU Compute Allocation:**
- Video processing (FFmpeg with GPU acceleration)
- Image processing (GPU-accelerated operations)
- Model training workloads (LoRA, fine-tuning)
- Any GPU-intensive task requiring VRAM allocation
- MADs access these capabilities through Compute Offload Nodes (ADR-036) that handle service discovery and failover

**3. MCP Tool Interface:**

```python
# Unified inference for any model type
mcp__sutherland__local_inference(
    model_name: str,        # "phi3:mini", "stable-diffusion-xl", "whisper-large"
    task_type: str,         # "text-generation", "image-generation", "speech-to-text"
    input_data: dict,       # Task-specific input
    parameters: dict = {}   # Model-specific parameters
) -> dict
```

**4. Model Lifecycle Management:**

```python
# Load model into VRAM (called by Fiedler orchestrator)
mcp__sutherland__load_model(
    model_name: str,
    priority: int = 0  # Higher priority models loaded first
) -> dict

# Unload model to free VRAM for competing workloads
mcp__sutherland__unload_model(
    model_name: str
) -> dict
```

**5. Status Reporting:**

```python
# Report to Fiedler every 5 minutes for orchestration decisions
mcp__sutherland__get_status() -> dict:
    """
    Returns: {
        "host_id": "sutherland-host-01",
        "gpu_info": {"model": "RTX 4090", "vram_total_gb": 24, "vram_used_gb": 14},
        "loaded_models": [
            {"name": "phi3:mini", "type": "llm", "vram_gb": 4, "priority": 5, "last_used": "2025-12-21T14:30:00Z"},
            {"name": "stable-diffusion-xl", "type": "image-gen", "vram_gb": 8, "priority": 3, "last_used": "2025-12-21T12:15:00Z"}
        ],
        "vram_used_gb": 14,
        "vram_available_gb": 10,
        "vram_total_gb": 24,
        "active_requests": 3,
        "gpu_compute_available": true
    }
    """
```

### One Instance Per Host Architecture

**Before (ADR-029 approach):**
```
Host with 10 MADs:
├─ MAD 1 container (Ollama: phi3:mini = 4GB)
├─ MAD 2 container (Ollama: phi3:mini = 4GB)
├─ ...
└─ MAD 10 container (Ollama: phi3:mini = 4GB)
Total VRAM: 40GB for duplicated models
```

**After (ADR-035 approach with Sutherland):**
```
Host with 10 MADs:
├─ Sutherland container (manages all models)
│   └─ phi3:mini loaded once (4GB)
├─ MAD 1-10 call mcp__sutherland__local_inference(...)
Total VRAM: 4GB for shared model
Savings: 36GB per host
```

### Integration with joshua_ai_access

MADs access Sutherland via `SutherlandLLMNode` from the `joshua_ai_access` library:

```json
{
  "nodes": [
    {
      "type": "SutherlandLLMNode",
      "inputs": {
        "model_name": "phi3:mini",
        "message": "{{input.user_prompt}}",
        "temperature": 0.7
      }
    }
  ]
}
```

### Federated Gossip Protocol Unchanged

The core federated gossip architecture from this ADR remains valid:
- Multiple Sutherland instances (one per host) still use gossip protocol for global awareness
- Placement recommendations for GPU workloads unchanged
- Decentralized coordination still applies

**What changed:** Each Sutherland now manages all GPU compute workloads (AI models AND general GPU tasks like FFmpeg), not just GPU allocation.

### See Related ADRs for Complete Architecture

This ADR defines Sutherland's **federated deployment and gossip protocol**.

**ADR-035** defines Sutherland's **expanded GPU compute management responsibilities and Fiedler integration**.

**ADR-036** defines the **Node Library Architecture** and how MADs interact with Sutherland through Compute Offload Nodes (like `FFmpegNode`) that implement service discovery and failover patterns.

Together: Complete local GPU compute architecture (AI models and general GPU workloads).

---
---

## Appendix A: Detailed Architectural Rationale

### A.1. Rejection of Centralized Models ("Lead Sutherland")

An initial proposal involved a "Lead + Worker" model for Sutherland. This was rejected because a "Lead" instance, while providing a single source of truth for global state, would also represent a single point of failure for *visibility*. If the Lead were to go down, the `eMAD Spawner` would be blind, even if the worker GPUs were still functional. This violates our core resilience principles.

### A.2. The "Gossip" Protocol for Common Awareness

The chosen peer-to-peer model is inspired by modern distributed systems that require high availability and decentralized coordination.
-   Each `Sutherland` instance periodically broadcasting its state to a shared bus topic is a form of "gossip."
-   Each instance listening to these broadcasts and assembling its own global view makes the system robust. Any instance can answer a query about the global state.
-   Failure detection is also decentralized. Any `Sutherland` instance can detect the absence of a peer's heartbeat and raise a system-wide alert, without needing a central manager to poll for liveness.

### A.3. Sutherland's PCP and the "Placement Recommendation" Pattern

This architecture elevates Sutherland from a simple resource monitor to an intelligent agent with its own domain expertise.
-   **The Problem:** A `MAD Spawner` needs to place a GPU-heavy eMAD. A naive approach would be for the Spawner to query the state of all hosts and then run its *own* complex scheduling logic to make a decision. This burdens the Spawner with logic that is outside its core domain.
-   **The Solution:** The Spawner delegates. It makes a high-level request to a `Sutherland` instance: `"I need a home for a workload with these requirements."`
-   **Sutherland's Cognitive Role:** The `Sutherland` MAD's own internal PCP/Imperator is the expert on this. It takes the requirements, compares them against its real-time global view of the cluster, and runs its sophisticated scheduling/placement logic. The output is not raw data; it's a high-confidence **recommendation**. This perfectly encapsulates the domain expertise of compute resource management within the `Sutherland` MAD, keeping the `MAD Spawner`'s logic clean and focused. This is the Cellular Monolith philosophy in action.
