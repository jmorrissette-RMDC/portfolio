# Node Library Requirements

This directory contains requirements documents for node libraries - the fine-grained, reusable building blocks used within Langflow flows.

## What is a Node Library?

Per **ADR-036: Node Library Architecture**, the Joshua ecosystem uses a three-tiered node library model:

### Tier 1: Universal Nodes (core/)
General-purpose nodes used across all MADs and domains:
- **joshua_core** (MISSING) - Flow control, LLM access, utilities
  - `IfElseNode` - Conditional branching
  - `LoopNode` - Iteration and mapping
  - `LLMCLINode` - Universal LLM access (provider-agnostic)
  - `FilterNode`, `MergeNode`, `TransformNode` - Data manipulation

### Tier 2: Provider-Specific Nodes (providers/)
Nodes that expose vendor-specific features:
- **joshua_gemini** (MISSING) - Google Gemini-specific capabilities
  - Multimodal processing nodes
  - Native tool calling nodes
- **joshua_claude** (MISSING) - Anthropic Claude-specific capabilities
  - Extended thinking nodes
  - Artifact generation nodes
- **joshua_openai** (MISSING) - OpenAI-specific capabilities
  - Function calling patterns
  - Structured output nodes

### Tier 3: Domain-Specific Nodes (domain/)
Specialized nodes for specific problem domains:
- **joshua_ffmpeg** (MISSING) - Audio/video processing
  - Video transcoding nodes
  - Audio extraction nodes
- **joshua_stable_diffusion** (MISSING) - Image generation
- **joshua_whisper** (MISSING) - Speech recognition

## Node Library vs. Library vs. PCP Component Library

**Node Library** (this directory):
- Fine-grained, single-purpose building blocks
- Used **within** flows as individual nodes
- Example: `LLMCLINode` from joshua_core

**Library** (`../Libraries/`):
- Foundational infrastructure components
- Entire engines MADs import
- Example: `Joshua_Communicator`, `Joshua_Flow_Runner`

**PCP Component Library** (`../Libraries/pcp/`):
- Cognitive reasoning nodes
- Part of Thought Engine
- Example: `ImperatorNode` from joshua_imperator

## What a Node Library Requirements Document Specifies

1. **Node Catalog** - Complete list of nodes provided
2. **Node Specifications** - For each node:
   - Input parameters (name, type, required/optional)
   - Output format (return type, structure)
   - Behavior description (what the node does)
   - Error handling (failure modes, exceptions)
3. **Dependencies** - External packages or services required
4. **Performance Characteristics** - Expected latency, resource usage
5. **Testing Requirements** - Unit test coverage for each node

## Design Principles (from ADR-036)

### Small, Focused Libraries
Each node library should contain a small, cohesive set of related nodes (typically 3-10 nodes). Prefer splitting over aggregating.

**Good Example**: `joshua_ffmpeg` with 5 video processing nodes
**Bad Example**: `joshua_media_processing` with 50 mixed audio/video/image nodes

### Wrap Strategy
For third-party tools (CLIs, APIs), create thin wrapper nodes:
- Expose tool functionality as Langflow-compatible nodes
- Handle input/output marshaling
- Implement failover and error handling
- Let flows orchestrate the tools

**Example**: `joshua_ffmpeg` wraps FFmpeg CLI commands as individual nodes

### Provider Choice Flexibility
When the same capability exists across providers (e.g., LLM access):
- Use `LLMCLINode` from joshua_core for provider-agnostic access
- Use provider-specific nodes only when leveraging vendor-specific features

## Directory Structure

```
Nodes/
├── README.md (this file)
├── core/
│   └── joshua_core_node_library_requirements.md (MISSING)
├── providers/
│   ├── joshua_gemini_node_library_requirements.md (MISSING)
│   ├── joshua_claude_node_library_requirements.md (MISSING)
│   └── joshua_openai_node_library_requirements.md (MISSING)
└── domain/
    ├── joshua_ffmpeg_node_library_requirements.md (MISSING)
    ├── joshua_stable_diffusion_node_library_requirements.md (MISSING)
    └── joshua_whisper_node_library_requirements.md (MISSING)
```

## Installation

Node libraries are installed via pip alongside other dependencies:

```txt
# requirements.txt
joshua_core>=1.0.0            # Universal nodes
joshua_gemini>=1.0.0          # Provider-specific (if needed)
joshua_ffmpeg>=1.0.0          # Domain-specific (if needed)
```

Flows automatically discover and use nodes from installed libraries.

## Related Documentation

- **ADR-036**: Node Library Architecture - Complete design rationale
- **ADR-035**: Direct Access AI Model Nodes - LLM access pattern
- **ADR-034**: CLI-First LLM Integration Strategy - Provider CLI wrapping approach
- **Libraries**: `../Libraries/` - Infrastructure libraries
- **MADs**: `../MADs/` - How MADs compose node libraries

---

**Last Updated:** 2025-12-21
