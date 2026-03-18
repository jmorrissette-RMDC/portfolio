# ADR-040: Baseline LLM for Local Agent Resilience

**Status:** Accepted
**Date:** 2025-12-22

## Context

The Joshua system operates a distributed multi-agent architecture where agents may need to make LLM calls for decision-making, tool use, and reasoning. The current architecture assumes availability of:

1. **Remote commercial LLMs** (GPT-4, Claude, Gemini) - high quality, large context, but network-dependent
2. **Local large models** (13B-70B on V100/P40/K80 clusters) - high quality, but resource-constrained and may be busy with other workloads
3. **Specialized models** (CET on V100s, embeddings on K80) - dedicated to specific tasks

**Problem:** If remote APIs are unavailable (network outage, rate limits, API downtime) and local large models are fully utilized or unavailable, agents have no fallback. This creates a single point of failure where the entire agent ecosystem stops functioning.

**Requirement:** Every machine in the Joshua ecosystem must have a guaranteed baseline LLM capability that can handle basic agent operations even when all other resources are unavailable.

## Decision

### Baseline Model: phi3:mini

Every machine will maintain **phi3:mini** (Microsoft, 3.8B parameters) as the guaranteed baseline LLM:

**Model Specifications:**
- Parameters: 3.8B
- VRAM requirement: 2.2GB (4-bit quantized)
- Context window: 128K tokens
- Capabilities: Instruction following, tool calling, JSON output, basic reasoning
- License: MIT (fully open)
- Deployment: Via Ollama for consistent interface

**Rationale:**
1. **Small enough to fit everywhere:** 2.2GB fits comfortably in 4GB VRAM slice on any GPU
2. **Good enough for agents:** Handles tool use, structured output, basic decision-making
3. **Large context:** 128K window sufficient for most agent tasks with RAG context
4. **Proven reliability:** Well-tested in production agent systems
5. **Standardization:** Same model everywhere simplifies debugging and behavior expectations

### VRAM Reservation Strategy

**Every machine must carve out 4GB VRAM for baseline LLM:**

**Current machines:**

**Client (192.168.1.200) - P1000 4GB:**
- **Allocation:** Entire GPU dedicated to baseline operations
- **Models:** phi3:mini (2.2GB) + nomic-embed-text (274MB) + headroom
- **Usage:** Baseline LLM + legacy Qdrant embedding
- **Justification:** P1000 already serves this role; formalize it

**Irina (192.168.1.210) - No GPU currently:**
- **Requirement:** Install GPU with minimum 4GB VRAM or allocate from future GPU additions
- **Alternative:** CPU fallback via Ollama (slower but functional)

**V100 Cluster (3-4x 32GB):**
- **Allocation:** Reserve 4GB on one V100 for phi3:mini baseline
- **Primary workload:** CET (Mistral Small 24B) uses ~68-90GB
- **Implementation:** Run phi3:mini on same GPUs via Ollama, separate from CET inference engine
- **Coordination:** Sutherland manages allocation to prevent VRAM conflict

**K80 (2x 12GB):**
- **Allocation:** Reserve 4GB on GPU 1 (GPU 0 handles M2-BERT embedding)
- **Primary workload:** M2-BERT 32K embeddings (~500MB model + batching)
- **Headroom:** GPU 0 has ~19GB free; GPU 1 dedicated to baseline + other small models

**P40s (3x 24GB):**
- **Allocation:** Reserve 4GB on each P40
- **Future workload:** Small agentic models (per ADR discussion - not yet formalized)
- **Headroom:** 20GB per GPU remains for other workloads

### Graceful Degradation Pattern

**Agent LLM selection logic (priority order):**

1. **Primary:** Attempt configured model (commercial API or large local model)
2. **Secondary:** Failover to alternative large model if available
3. **Tertiary:** Fall back to machine-local phi3:mini baseline
4. **Critical:** Phi3:mini always available, never fully allocated to other tasks

**Implementation via Sutherland/Fiedler:**
- Agents request LLM capability via standard interface
- Orchestrator attempts primary/secondary options
- On failure, automatically routes to local phi3:mini
- Log degradation events for monitoring

### Deployment Mechanism

**Ollama as standard interface:**
- Every machine runs Ollama service
- Ollama manages phi3:mini lifecycle (load on demand, unload after timeout)
- Agents call via standard OpenAI-compatible API
- Consistent interface regardless of underlying hardware

**VRAM protection:**
- Configure Ollama to reserve 4GB maximum for baseline model
- Use `OLLAMA_MAX_VRAM` environment variable or equivalent
- Prevent baseline model from consuming resources needed for primary workloads

## Consequences

### Positive

1. **Resilience:** System continues functioning during network outages, API failures, or resource contention
2. **Predictable degradation:** Agents always have a fallback, even if quality degrades
3. **Debugging:** Consistent baseline model simplifies troubleshooting agent behavior
4. **Development:** Developers can test agent logic locally without depending on remote APIs
5. **Cost control:** Reduces forced dependency on commercial APIs for simple tasks
6. **Autonomous operation:** Machines can operate independently without cluster/network dependencies

### Negative

1. **VRAM overhead:** 4GB reserved per machine reduces available memory for other workloads
2. **Quality degradation:** phi3:mini significantly less capable than large models (acceptable for fallback)
3. **Management overhead:** Must ensure phi3:mini stays available and updated across fleet
4. **Inconsistent performance:** Baseline degradation may cause unexpected agent behavior changes

### Operational Requirements

1. **Monitoring:** Track fallback events to identify systemic issues (network problems, resource exhaustion)
2. **Alerts:** Notify when agents are consistently using baseline instead of primary models
3. **Testing:** Regularly test agent operation with phi3:mini to ensure fallback path works
4. **Documentation:** Update agent development guide to explain degradation behavior
5. **VRAM management:** Sutherland must account for reserved 4GB when allocating other workloads

### Machine-Specific Implementation

**Client (P1000):**
- Already running Ollama with phi3:mini - formalize as baseline standard
- Continue supporting nomic-embed-text for legacy Qdrant
- Status: ✅ Compliant

**V100 Cluster:**
- Add phi3:mini to Ollama on cluster
- Configure Sutherland to reserve 4GB for baseline
- Coordinate with CET workload (Mistral Small 24B)
- Status: ⚠️ Implementation needed

**K80:**
- Add phi3:mini to Ollama
- Allocate to GPU 1 (GPU 0 busy with embeddings)
- Status: ⚠️ Implementation needed

**P40s:**
- Add phi3:mini to Ollama on each host
- 4GB reservation leaves 20GB for future agentic workloads
- Status: ⚠️ Implementation needed

### Related Decisions

- ADR-015: Joshua GPU Compute Cluster (hardware infrastructure)
- ADR-035: Direct Access AI Model Nodes (inference patterns)
- ADR-038: CET Model Selection (V100 cluster primary workload)
- ADR-039: RAG Embedding Strategy (K80 primary workload)

## References

- phi3-mini: https://huggingface.co/microsoft/Phi-3-mini-128k-instruct
- Ollama: https://ollama.ai/
- Graceful degradation pattern: Industry standard resilience practice for distributed systems
