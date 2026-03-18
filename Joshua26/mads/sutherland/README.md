# Sutherland — AI Compute Center

Sutherland is the AI compute platform for the Joshua26 ecosystem. It is a **State 1** MAD (gateway + langgraph + backing services) per HLD-MAD-container-composition.

## Overview

Sutherland provides:
- **Unified inference** — LLM chat, embeddings, reranking, and video generation via model aliases
- **Ray Serve cluster** — Local GPU models deployed on Ray with config-driven model management
- **OpenAI-compatible API** — Drop-in replacement for cloud LLM APIs
- **Cloud fallback** — Gemini, xAI, OpenAI, Anthropic, Together for cloud-routed aliases

## Architecture (Ray Iteration)

| Component | Role |
|-----------|------|
| sutherland | Node.js MCP gateway (port 11435) |
| sutherland-langgraph | Python inference router (alias resolution, Ray/cloud routing) |
| sutherland-postgres | Model alias registry |
| sutherland-ray-head | Ray cluster head + Ray Serve HTTP API (port 8000) |
| Ray Workers | m5, Irina (P4), J-Desktop — GPU compute nodes |

## MCP Tools

| Tool | Description |
|------|-------------|
| `llm_chat_completions` | Unified LLM inference via model alias (imperator-gunner, agent-small, cloud aliases) |
| `llm_embeddings` | 768-dim text embeddings (single or batch, max 32) |
| `llm_rerank` | Cross-encoder reranking (bge-reranker-v2-m3) |
| `video_extend` | Extend or generate video using Wan 2.2 VACE-A14B on V100 |

## Model Aliases

| Alias | Backend | Notes |
|-------|---------|-------|
| imperator-gunner | xai | xai/grok-4-fast (cloud) |
| agent-small | local_ray | Qwen2.5-7B on P40, via GGUFDeployment |
| vace-14b | local_ray | Wan2.2-VACE-A14B on V100, via DiffusersVideoDeployment |
| imperator-grace | gemini | Gemini 2.5 Pro |
| imperator-henson | openai | GPT-4o |
| embed-default | local_ray | Embeddings on P4 (Irina) |
| bge-reranker-v2-m3 | local_ray | Reranker on P40s |

## Model Management

### Where the config lives

The operator config lives at `/workspace/sutherland/serve_config.yaml` on m5 (workspace volume). A documented template is committed at `mads/sutherland/sutherland-ray-head/serve_config.yaml.example`.

`serve_app.py` is pure infrastructure — it is **never edited for model swaps**. All model choices, paths, and GPU assignments live in the YAML.

### Model swap playbook

```bash
# 1. Ensure weights are on disk (download if needed)
docker exec sutherland-ray-head python3 -c "
from huggingface_hub import snapshot_download
snapshot_download('org/model-id', local_dir='/workspace/sutherland/models/model-name')
"

# 2. Edit the workspace config on m5
#    Add/remove/change application entry in /workspace/sutherland/serve_config.yaml

# 3. Apply to live Ray cluster (no restart, no rebuild)
docker exec sutherland-ray-head serve deploy /workspace/sutherland/serve_config.yaml

# 4. Update postgres alias (one SQL upsert)
docker exec sutherland-postgres psql -U sutherland sutherland -c "
INSERT INTO model_aliases (alias, backend_type, backend_url, model_name, active)
VALUES ('my-alias', 'local_ray', 'http://sutherland-ray-head:8000/route', 'ModelName', true)
ON CONFLICT (alias) DO UPDATE SET backend_url=EXCLUDED.backend_url, active=true;
"
```

### Supported deployment types

| Import path | Class | Use for |
|-------------|-------|---------|
| `serve_app:agent_small_app` | `GGUFDeployment` | Any GGUF model (llama-cpp-python) |
| `serve_app:vace_app` | `DiffusersVideoDeployment` | Any diffusers video pipeline |
| `serve_app:embedding_app` | `EmbeddingDeployment` | BGE embeddings (fixed, P4) |
| `serve_app:reranker_app` | `RerankerDeployment` | BGE reranker (fixed, P40) |
| `serve_app:health_app` | `HealthDeployment` | /-/healthz (no GPU) |

### GPU resource labels

| Label | Hardware |
|-------|----------|
| `gpu_class_v100` | Tesla V100 32GB (3x on m5, SXM2 + PCIe) |
| `gpu_class_p40` | Tesla P40 24GB (m5) |
| `accelerator_type:P4` | Tesla P4 8GB (irina) |

### Runtime pip deps via Alexandria

Video pipelines and other packages with heavy deps specify `pip_index_url` in `runtime_env`:

```yaml
runtime_env:
  pip:
    - "diffusers>=0.31.0"
    - "accelerate>=0.26.0"
  pip_index_url: "http://irina:3141/root/pypi/+simple/"
```

This routes pip through Alexandria's cached PyPI mirror — no internet access required.

## Ports

| Port | Service |
|------|---------|
| 11435 | MCP gateway |
| 8000 | Ray Serve (internal, sutherland-net) |

## Building and Deployment

From the Joshua26 project root:

```bash
docker compose build sutherland sutherland-langgraph
docker compose up -d sutherland sutherland-langgraph
```

See `docs/guides/mad-deployment-guide.md` for full deployment steps.

## References

- [REQ-sutherland](docs/REQ-sutherland.md) — Delta REQ for Ray iteration
- [sutherland-plan](docs/sutherland-plan.md) — Build and deployment plan
- [TEST-PLAN-sutherland](docs/TEST-PLAN-sutherland.md) — Test cases
