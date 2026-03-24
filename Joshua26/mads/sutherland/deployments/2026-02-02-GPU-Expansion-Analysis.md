# Sutherland GPU Expansion Analysis - 2026-02-02

**Date:** 2026-02-02 (Later session)
**Status:** ⚠️ Investigation - Models Stopped
**Related:** 2026-02-02-GPU-Integration-M5.md

## Change Summary

### New GPU Configuration
Two V100-SXM2 GPUs (32GB each) were added to M5, expanding from 4 to 6 total GPUs:

**Previous Configuration (4 GPUs):**
- GPU 0: Tesla P40 (24GB)
- GPU 1: Tesla P40 (24GB)
- GPU 2: Tesla P40 (24GB)
- GPU 3: Tesla V100-PCIE-32GB (32GB)
- **Total VRAM:** 104GB

**New Configuration (6 GPUs):**
- GPU 0: Tesla P40 (24GB)
- GPU 1: Tesla P40 (24GB)
- GPU 2: Tesla P40 (24GB)
- GPU 3: Tesla V100-SXM2-32GB (32GB) - **NEW**
- GPU 4: Tesla V100-SXM2-32GB (32GB) - **NEW**
- GPU 5: Tesla V100-PCIE-32GB (32GB)
- **Total VRAM:** 168GB (+64GB)

## Current State

### Container Status
- **Container:** sutherland (healthy, running)
- **GPU Detection:** All 6 GPUs visible to container
- **RPC Servers:** Running on all 6 GPUs (146-310MB each)
- **Model Instances:** **NONE RUNNING** ⚠️

### GPU Memory Usage (RPC Servers Only)
```
GPU 0 (P40):      ~148 MB - llama-box-rpc-server
GPU 1 (P40):      ~148 MB - llama-box-rpc-server
GPU 2 (P40):      ~148 MB - llama-box-rpc-server
GPU 3 (V100-SXM2): ~309 MB - llama-box-rpc-server
GPU 4 (V100-SXM2): ~309 MB - llama-box-rpc-server
GPU 5 (V100-PCIE): ~310 MB - llama-box-rpc-server
```

### Model Status
All three models were stopped around 08:30:

1. **llama-3.2-3b-instruct** - Stopped
   - Was running on GPUs 0, 1, 3 (previous config)

2. **mistral-small-24b-instruct** - Stopped after restart loop ⚠️
   - Was experiencing restart issues (attempts 1-6)
   - Was running on GPUs 2, 3 (previous config)

3. **qwen2.5-72b-instruct** - Stopped
   - Was running on GPUs 2, 3 (previous config)

## Desired Configuration

User requested model placement:

### Small Model: llama-3.2-3b-instruct (3B params)
- **Target GPU:** V100-PCIE only (GPU 5)
- **VRAM Needed:** ~6-8GB
- **Purpose:** Fast general-purpose inference

### Medium Model: mistral-small-24b-instruct (24B params)
- **Target GPU:** V100-PCIE only (GPU 5)
- **VRAM Needed:** ~15-20GB
- **Purpose:** Balanced quality/speed
- **Note:** Was having restart issues - investigate before redeploying

### Large Model: qwen2.5-72b-instruct (72B params)
- **Target GPUs:** 3x P40s (GPUs 0, 1, 2)
- **VRAM Needed:** ~40-50GB (distributed via sharding)
- **Purpose:** High-quality reasoning

### GPU Assignment Summary
- **V100-PCIE (GPU 5):** Small + Medium models (~25GB total)
- **P40 Pool (GPUs 0-2):** Large model distributed (~17GB per GPU)
- **V100-SXM2 (GPUs 3-4):** Reserved for future use

## Issues Identified

### 1. All Models Stopped
- **Problem:** No model instances are running despite RPC servers being active
- **Evidence:** Only llama-box-rpc-server processes visible in nvidia-smi
- **Impact:** LLM inference unavailable through MCP tools

### 2. Mistral Model Restart Loop
- **Problem:** mistral-small-24b was restarting repeatedly before being stopped
- **Evidence:** Container logs show restart attempts 1-6 around 08:30
- **Possible Causes:**
  - GPU memory issues
  - Model file corruption
  - Configuration problems
  - Port conflicts

### 3. Configuration Needs Update
- **Problem:** Previous model placement doesn't match desired configuration
- **Impact:** Models were distributed across old 4-GPU topology
- **Required:** Redeploy models with new GPU assignments

## Investigation Needed

### 1. Why Were Models Stopped?
Check Sutherland container logs for:
- Shutdown signals
- OOM (Out of Memory) errors
- Model loading failures
- GPUStack scheduler issues

### 2. Mistral Restart Loop Root Cause
Investigate:
- Model loading errors
- GPU memory allocation failures
- Port binding conflicts
- Worker communication issues

### 3. Current GPUStack State
Verify via GPUStack API:
- Deployment status
- Worker status
- Zone configuration
- Model file integrity

## Required Actions

### Step 1: Investigate Logs
```bash
# Check recent Sutherland logs for errors
sudo docker logs --tail 500 sutherland | grep -i "error\|failed\|restart"

# Check GPUStack API deployment status
sudo docker exec sutherland curl -s http://localhost:80/v1/deployments

# Check worker status
sudo docker exec sutherland curl -s http://localhost:80/v1/workers
```

### Step 2: Verify Model Files
```bash
# List available models in GPUStack
sudo docker exec sutherland curl -s http://localhost:80/v1/models
```

### Step 3: Redeploy Models with New GPU Assignments

**Option A: Via GPUStack API**
```bash
# Deploy small model to V100-PCIE
curl -X POST http://localhost:80/v1/deployments \
  -H "Content-Type: application/json" \
  -d '{
    "name": "llama-3.2-3b-instruct",
    "model": "llama-3.2-3b-instruct",
    "gpu_selector": "gpu-index=5"
  }'

# Deploy medium model to V100-PCIE
curl -X POST http://localhost:80/v1/deployments \
  -H "Content-Type: application/json" \
  -d '{
    "name": "mistral-small-24b-instruct",
    "model": "mistral-small-24b-instruct",
    "gpu_selector": "gpu-index=5"
  }'

# Deploy large model to P40 pool
curl -X POST http://localhost:80/v1/deployments \
  -H "Content-Type: application/json" \
  -d '{
    "name": "qwen2.5-72b-instruct",
    "model": "qwen2.5-72b-instruct",
    "gpu_selector": "gpu-index=0,1,2"
  }'
```

**Option B: Via MCP Tools (if available in session)**
```
llm_deploy_model - Deploy with GPU constraints
llm_undeploy_model - Remove old deployments first
llm_model_status - Check deployment progress
```

### Step 4: Verify New Deployment
```bash
# Check GPU memory distribution
nvidia-smi

# Verify models loaded
sudo docker exec sutherland curl -s http://localhost:80/v1/deployments

# Test inference
llm_chat or llm_generate via MCP
```

## Constraints and Considerations

### GPU Memory Budget
- **V100-PCIE (32GB):**
  - Small model: ~7GB
  - Medium model: ~18GB
  - **Total:** ~25GB (78% utilization)
  - **Headroom:** ~7GB for context/batch size

- **P40 Pool (72GB):**
  - Large model: ~45-50GB distributed
  - **Per GPU:** ~15-17GB
  - **Headroom:** ~22GB for larger context windows

### Model Co-location
Two models on V100-PCIE may cause:
- Increased VRAM pressure
- Potential context window limitations
- Request queuing if both models busy
- Monitor for OOM issues

### V100-SXM2 Reserved
- Higher memory bandwidth than V100-PCIE
- Available for future deployments
- Could run additional specialized models

## Expected Performance

### Inference Speed
- **Small (3B on V100):** < 1s (faster than before on P40)
- **Medium (24B on V100):** 1-2s (faster than before)
- **Large (72B on P40s):** 3-7s (similar to previous)

### Advantages of New Configuration
1. **V100 Compute:** Faster inference for small/medium models
2. **Dedicated Resources:** Less GPU sharing/contention
3. **P40 Pool:** Dedicated to large model = more stable sharding
4. **Headroom:** V100-SXM2s available for expansion

## Investigation Results

### Root Cause Identified

**Primary Issue:** Models were deleted from GPUStack database.

**Evidence:**
1. API query shows no models: `{"items":[],"pagination":{"total":0}}`
2. API query shows no deployments: `{"detail":"Not Found"}`
3. Only 1 model file on disk: TinyLlama (638MB test model)
4. Error logs show 404s trying to fetch from Ollama registry
5. All three target models (llama-3.2-3b, mistral-small-24b, qwen2.5-72b) don't exist

**Timeline:**
- 08:22-08:28: Mistral model in restart loop (6 attempts with exponential backoff)
- 08:30: All models stopped (qwen, llama, mistral)
- 08:30+: Continuous 404 errors trying to re-fetch models from Ollama registry
- Current: No models in database, only RPC servers running

**Why Models Failed:**
The model names configured in GPUStack don't exist in Ollama's registry:
- `https://registry.ollama.ai/v2/library/qwen2.5-72b-instruct/manifests/latest` → 404
- `https://registry.ollama.ai/v2/library/llama-3.2-3b-instruct/manifests/latest` → 404
- `https://registry.ollama.ai/v2/library/mistral-small-24b-instruct/manifests/latest` → 404

## Next Steps

### 1. Determine Correct Model Sources

Need to identify where these models should come from:

**Option A: Huggingface Models**
```bash
# Example with correct Huggingface repo IDs
llama-3.2-3b-instruct → meta-llama/Llama-3.2-3B-Instruct
mistral-small-24b-instruct → mistralai/Mistral-Small-Instruct-2409
qwen2.5-72b-instruct → Qwen/Qwen2.5-72B-Instruct
```

**Option B: Correct Ollama Model Names**
```bash
# Check what's actually available in Ollama
llama3.2:3b-instruct (not llama-3.2-3b-instruct)
mistral-small (not mistral-small-24b-instruct)
qwen2.5:72b-instruct (not qwen2.5-72b-instruct)
```

### 2. Re-add Models to GPUStack

Once correct model sources identified, add them via API or Web UI:

**Via Web UI:**
1. Access http://192.168.1.120:11434 (or port 80)
2. Navigate to Models section
3. Add models with correct source URLs/repo IDs
4. Specify GGUF format if using Huggingface

**Via API:**
```bash
# Example: Add model via API
curl -X POST http://sutherland:80/v1/models \
  -H "Content-Type: application/json" \
  -d '{
    "name": "llama-3.2-3b-instruct",
    "hugging_face_repo_id": "meta-llama/Llama-3.2-3B-Instruct-GGUF",
    "hugging_face_filename": "*.Q4_K_M.gguf"
  }'
```

### 3. Deploy Models with New GPU Assignments

After models are added and downloaded:

**Small Model (llama-3.2-3b):**
- GPU: V100-PCIE (GPU 5)
- Command: Deploy with `gpu_selector: "gpu-index=5"`

**Medium Model (mistral-small-24b):**
- GPU: V100-PCIE (GPU 5)
- Command: Deploy with `gpu_selector: "gpu-index=5"`
- Note: Co-located with small model, monitor VRAM usage

**Large Model (qwen2.5-72b):**
- GPUs: 3x P40s (GPUs 0, 1, 2)
- Command: Deploy with `gpu_selector: "gpu-index=0,1,2"`
- Will be sharded across all three P40s

### 4. Verify and Monitor

1. Test all three models via MCP llm_chat
2. Monitor GPU memory usage
3. Watch for restart loops (check logs)
4. Verify performance meets expectations
5. Document final configuration

### 5. Update Documentation

- Update main README.md with new GPU topology
- Document model sources and deployment commands
- Add troubleshooting section for model re-deployment

## References

- Previous deployment: `2026-02-02-GPU-Integration-M5.md`
- GPUStack API: http://sutherland:11434/docs
- MCP Tools: 13 available via sam-irina
- GPU Topology: 6 GPUs (3xP40, 2xV100-SXM2, 1xV100-PCIE)
