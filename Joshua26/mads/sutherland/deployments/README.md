# Sutherland (GPUStack) Deployment History

## Overview

Sutherland is a GPU-accelerated LLM inference service powered by GPUStack. It provides local LLM capabilities through MCP tools, enabling chat, text generation, and model management across multiple GPUs.

**Container Name:** `sutherland`
**Host:** M5 (192.168.1.120)
**Image:** `joshua26/sutherland:latest`

## Deployment Sessions

### 2026-02-02: GPU Integration Verification & MCP Integration
- **Status:** ✅ Completed
- **Summary:** Verified GPU access after X.org/VNC fix, confirmed MCP integration with sam-irina, validated model distribution across GPUs
- **Key Findings:**
  - All 4 GPUs accessible and actively used by GPUStack
  - 3 models deployed: llama-3.2-3b, qwen2.5-72b, mistral-small-24b
  - Model sharding/distribution working across GPUs (~67% VRAM utilization)
  - 13 MCP tools exposed through sam-irina
  - `llm_chat` verified working through ecosystem
  - X.org/VNC no longer using NVIDIA GPUs (0 MB usage)
- **Document:** [2026-02-02-GPU-Integration-M5.md](./2026-02-02-GPU-Integration-M5.md)

## Current Status

### Container Configuration
- **Name:** `sutherland`
- **Status:** Running (healthy)
- **Runtime:** NVIDIA (GPU-enabled)
- **Network:** `joshua-net` (IP: 10.0.1.13)
- **Uptime:** 11+ hours (as of verification)

### Ports
- **11435/tcp:** MCP server endpoint (HTTP/SSE)
- **11434/tcp:** GPUStack API endpoint

### GPU Configuration
- **GPUs Available:** All 4 (3x Tesla P40, 1x Tesla V100-PCIE-32GB)
- **Total VRAM:** 104GB (72GB P40 + 32GB V100)
- **Current Usage:** ~70GB (67% utilization)
- **Distribution:** Models sharded/distributed across all GPUs

### Deployed Models

| Model | Size | GPUs | VRAM | Port | Purpose |
|-------|------|------|------|------|---------|
| llama-3.2-3b-instruct | 3B | 0,1,3 | ~16GB | 40036 | Fast general-purpose |
| mistral-small-24b-instruct | 24B | 2,3 | ~19GB | 40001 | Balanced quality/speed |
| qwen2.5-72b-instruct | 72B | 2,3 | ~35GB | 40033 | High-quality reasoning |

### MCP Tools (13 total)

**Management:**
- `sutherland_health_check` - Service health status
- `llm_list_workers` - GPU worker status
- `llm_list_models` - Available models
- `llm_list_deployments` - Active deployments
- `llm_list_zones` - GPU zones configuration

**Operations:**
- `llm_deploy_model` - Deploy new model
- `llm_undeploy_model` - Remove deployed model
- `llm_scale_model` - Scale model instances

**Inference:**
- `llm_generate` - Text completion
- `llm_chat` - Chat interface

**Monitoring:**
- `llm_model_status` - Model state
- `llm_gpu_status` - GPU utilization
- `llm_model_info` - Model details

### MCP Integration
- **Connected to:** sam-irina (192.168.1.110:6000)
- **Status:** Healthy
- **Protocol:** HTTP/SSE
- **Endpoints:**
  - Health: `http://sutherland:11435/health`
  - Stream: `http://sutherland:11435/mcp`

## Quick Reference

### Start Container
```bash
sudo docker start sutherland
```

### Stop Container
```bash
sudo docker stop sutherland
```

### View Logs
```bash
sudo docker logs sutherland
sudo docker logs -f sutherland  # Follow mode
```

### Check GPU Access
```bash
sudo docker exec sutherland nvidia-smi
sudo docker exec sutherland nvidia-smi -L  # List GPUs
```

### Check Model Status
Via sam-irina MCP tools (from Claude Code Desktop):
```
llm_list_models - List all available models
llm_list_deployments - See active deployments
llm_gpu_status - Check GPU utilization
```

### Chat with Model
Via sam-irina MCP tools:
```
llm_chat - Interactive chat with deployed models
```

### Monitor GPU Memory
```bash
watch -n 1 nvidia-smi  # Real-time GPU monitoring on M5
```

## Model Management

### Deploy New Model
1. Use `llm_deploy_model` MCP tool through sam-irina
2. Specify model name, size, and optional GPU constraints
3. GPUStack automatically assigns GPUs based on availability

### Remove Model
1. Use `llm_undeploy_model` MCP tool
2. Specify deployment ID or model name
3. GPU memory freed automatically

### Model Selection Guidelines
- **< 10B params:** Single GPU (P40 or V100)
- **10-30B params:** 1-2 GPUs (sharding if needed)
- **> 30B params:** Multi-GPU sharding required

## Performance Characteristics

### Inference Speed (Typical)
- **3B model:** Near real-time (< 1s)
- **24B model:** 1-3 seconds
- **72B model:** 3-7 seconds

*Varies based on prompt length, generation length, and load*

### Concurrent Capacity
- GPUStack handles multiple concurrent requests through worker RPC servers
- Request queuing and batching managed automatically
- Load distributed across model instances on different GPUs

### Memory Headroom
- **Current:** ~34GB VRAM available
- **Can support:** Additional models or larger context windows
- **Max models:** Limited by total VRAM (104GB)

## Troubleshooting

### Model Not Responding
1. Check deployment status: `llm_list_deployments`
2. Verify GPU availability: `llm_gpu_status`
3. Check container logs: `sudo docker logs sutherland`

### GPU Out of Memory
1. Check current usage: `nvidia-smi`
2. Undeploy unused models: `llm_undeploy_model`
3. Consider quantizing models for lower VRAM usage

### MCP Connection Issues
1. Verify container running: `sudo docker ps | grep sutherland`
2. Check sam-irina status: `relay_get_status` MCP tool
3. Restart if needed: `sudo docker restart sutherland`

## Registry Configuration

From `registry.yml`:
```yaml
sutherland:
  uid: 2007
  gid: 2001
  port: 11435  # MCP endpoint
  host: m5
  gpu: v100-32gb, p40-pool (3x24gb)
  description: GPUStack cluster manager for local LLMs
  mcp_endpoints:
    health: /health
    stream: /mcp
```

## Related Documentation
- **HLD:** `docs/designs/HLD-model-selection-framework.md`
- **Registry:** `registry.yml` (sutherland service)
- **Infrastructure:** `docs/infrastructure/INF-001-bare-metal-machine-configuration.md`
- **Related Services:** Muybridge (FaceSwap), Bass (FaceOrganizer)
- **MCP Integration:** Sam-irina relay aggregator
