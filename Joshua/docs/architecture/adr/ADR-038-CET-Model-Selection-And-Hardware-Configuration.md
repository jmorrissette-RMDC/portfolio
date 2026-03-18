# ADR-038: Context Engineering Transformer (CET) Model Selection and Hardware Configuration

**Status:** Accepted
**Date:** 2025-12-22

## Context

The Joshua system requires a Context Engineering Transformer (CET) to perform intelligent pre-processing and optimization of context before sending data to downstream LLMs. This function is critical for:

1. **Context Optimization:** Transforming raw multi-source context (conversations, logs, codebases) into optimized, structured prompts
2. **Static/Dynamic Segregation:** Separating unchangeable static content (codebases, documentation) from dynamic conversational elements
3. **Semantic Chunking:** Identifying logical breakpoints in long conversations for embedding and retrieval
4. **Iterative Refinement:** Supporting a training loop where the CET learns from good/bad LLM outcomes

Key requirements:
- **High reasoning capability** over mathematical performance (logical extraction vs computation)
- **Long context window** to process extensive conversation histories and documentation
- **Local training capability** to iterate on custom context engineering logic
- **Sufficient VRAM headroom** for experimentation and multi-model workflows

The system has access to a 3x Tesla V100 32GB cluster (96GB total VRAM) with plans to expand to 4x V100 (128GB) within 6 months.

## Decision

### Model Selection: Mistral Small 3.2 (24B)

We will use **Mistral Small 3.2 24B** as the CET model for the following reasons:

1. **Reasoning Optimization:** The 24B parameter class provides optimal reasoning density for context engineering tasks, significantly outperforming smaller 7B-8B models on GPQA (science reasoning) and MMLU-Pro (logical depth) benchmarks
2. **Context Window:** Native 128,000 token support allows processing of entire long conversations and documentation sections without chunking
3. **Agentic Workflow Design:** Specifically optimized for instruction adherence and multi-step logical operations - core requirements for context engineering
4. **Training Foundation:** Mistral Small 3.1 Base variant allows custom fine-tuning to embed domain-specific context optimization logic
5. **Apache 2.0 License:** Fully open for local deployment and modification

### Hardware Configuration

**Current (3x V100, 96GB total):**
- **Precision:** FP16 (full precision, no quantization)
- **Context Window:** 80,000 tokens
- **Configuration:** `--max-model-len 81920 --tensor-parallel-size 3 --gpu-memory-utilization 0.90`
- **VRAM Allocation:**
  - Model weights: ~48GB
  - KV Cache (80k context): ~20GB
  - Total: ~68GB
  - Free buffer: ~28GB (for worker models and stability)

**Future (4x V100, 128GB total - within 6 months):**
- **Context Window:** 128,000 tokens (full capability)
- **Configuration:** `--max-model-len 131072 --tensor-parallel-size 4`
- **VRAM Allocation:**
  - Model weights: ~48GB
  - KV Cache (128k context): ~32GB
  - Total: ~80GB
  - Free buffer: ~48GB (multi-model ecosystem support)

### Rationale for FP16 (No Quantization)

1. **Precision-Critical Task:** Context engineering requires high-order reasoning and structural integrity; quantization introduces rounding errors that compound over long contexts
2. **Training Alignment:** V100s train in FP16 (no BF16 support); running inference in same precision avoids quantization drift
3. **Syntax Reliability:** Full precision ensures perfectly valid JSON/XML/Markdown output for downstream LLMs
4. **Hardware Abundance:** With 96GB+ VRAM, we are "VRAM rich" - no penalty for choosing highest precision
5. **Debugging Clarity:** During iterative development, FP16 eliminates quantization as a variable in failure analysis

### Two-Stage Context Engineering Pipeline

The CET will operate in two passes:

**Stage 1: Segregation (Static/Dynamic Separation)**
- Input: Raw multi-source data (up to 80k tokens currently, 128k future)
- Action: Classify and separate static content (code, docs) from dynamic conversational elements
- Output: Stream A (static content pointers), Stream B (dynamic content for optimization)

**Stage 2: Optimization (Context Engineering)**
- Input: Stream B (dynamic content) + user query
- Action: Restructure, highlight, and format content based on trained "good outcome" patterns
- Output: Stream C (optimized context)

**Final Assembly:**
- Combine Stream A + Stream C
- Send to downstream LLM (commercial 1M+ context or local 128k-200k models)

## Consequences

### Positive

1. **Reasoning Quality:** 24B parameter density provides significantly better logical operations than smaller alternatives
2. **Context Capacity:** 80k context (expanding to 128k) handles most real-world conversation and documentation scenarios without chunking
3. **Training Flexibility:** Local cluster supports full fine-tuning for custom context engineering logic with frequent checkpoint rollback
4. **Stable Foundation:** FP16 precision eliminates quantization-related failures during experimental phase
5. **Multi-Model Headroom:** 28GB+ free VRAM allows running supplementary models (small classifiers, routing agents) on same cluster
6. **Expansion Path:** Clean upgrade path to 128k context with 4th V100 without architectural changes

### Negative

1. **Hardware Dependency:** Requires minimum 3x V100s; cannot run on smaller clusters without significant context reduction
2. **Inference Speed:** 24B model slower than 7B-8B alternatives; acceptable for batch context engineering but not real-time interactive use
3. **Initial Context Limitation:** 80k context adequate for most use cases but may require chunking for exceptional scenarios until 4th GPU added
4. **V100 Age:** Pascal architecture lacks modern optimizations (no BF16, older Tensor Cores); future migration to Ampere/Hopper would provide significant speedup

### Migration Notes

When adding 4th V100:
1. Update configuration: `--max-model-len 131072 --tensor-parallel-size 4`
2. Test KV Cache at full 128k to validate stability
3. Re-benchmark two-stage pipeline throughput
4. Consider loading additional specialized models in freed VRAM

### Related Decisions

- ADR-039: RAG Embedding Strategy with CET-Driven Chunking (semantic chunking integration)
- ADR-015: Joshua GPU Compute Cluster (hardware infrastructure)
- ADR-035: Direct Access AI Model Nodes (inference integration)

## References

- Mistral Small 3.2 24B: https://mistral.ai/news/mistral-small-3/
- Context Engineering discipline: Emerging 2025 practice for optimizing LLM context environments
- V100 specifications: 32GB HBM2, 900GB/s memory bandwidth, PCIe 3.0
