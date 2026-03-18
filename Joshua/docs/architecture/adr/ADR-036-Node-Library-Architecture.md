# ADR-036: Node Library Architecture and Acquisition Strategy

**Status:** Accepted
**Date:** 2025-12-21
**Deciders:** System Architect

---

## 📝 Integration with ADR-037 (2025-12-22)

This ADR's organizational principles remain valid and are **complementary** to ADR-037 (LangFlow Node Sourcing Strategy):

**Three-Tier Acquisition Strategy:**
1. **Adopt** - Use LangFlow native nodes wherever possible (e.g., Language Model component for basic LLM API access)
2. **Wrap** - Build custom nodes wrapping provider CLIs for model-specific optimizations (see ADR-034)
3. **Build** - Create custom nodes for Joshua-specific capabilities (CET, Imperator, multi-MAD orchestration)

**Library Structure:**
- Fine-grained architecture (one library per capability) remains valid
- Specific library names are design decisions, not architectural requirements
- Provider CLI wrapper nodes will be organized into appropriate libraries as implementation proceeds

---

## Context and Problem Statement

With the adoption of Langflow as the internal architecture for MAD Thought Engines (ADR-030, ADR-032), we need a clear strategy for organizing, acquiring, and managing the custom nodes that MADs will use in their flows.

Key questions:
- How should node libraries be structured and scoped?
- What should be universally available vs. domain-specific?
- Should we build all nodes from scratch, or leverage existing ecosystems?
- How do we balance rapid capability delivery with long-term optimization?

## Decision

We will adopt a **fine-grained, multi-tiered node library architecture** with three distinct strategies for node acquisition and a clear evolution path for optimization.

### 1. Library Granularity: One Library Per Capability

Node libraries will be **fine-grained** - typically one library per distinct capability or service integration, rather than aggregating multiple related capabilities into monolithic libraries.

**Rationale:**
- **Precise dependencies**: Each library carries only what it needs (e.g., `joshua_ffmpeg` needs no AI libraries)
- **Independent versioning**: Update Claude integration without touching Gemini integration
- **Minimal bloat**: MADs install exactly what they use
- **Clear ownership**: Each library has a single, well-defined responsibility
- **Hopper-friendly**: Easy to identify optimization candidates (one node = one library)

### 2. Three-Tier Organization

Node libraries are organized into three tiers based on their role and scope:

#### Tier 1: Core Libraries (Universal - Every MAD)

Fundamental capabilities required by all MADs, prioritizing LangFlow native components:

**Flow Control:** Use LangFlow's native flow control nodes where available, build custom only when needed
**Utilities:** Standard data transformation and formatting nodes
**Service Discovery:** Shared utilities for Fiedler integration and inter-MAD communication

**Note:** Basic LLM API access uses LangFlow's native Language Model component (ADR-037).

#### Tier 2: Provider CLI Libraries (Opt-in for Provider-Specific Optimizations)

Custom nodes wrapping provider CLIs to access model-specific optimizations (see ADR-034):

**Provider CLIs:** Nodes wrapping Anthropic Claude Code, Google Gemini CLI, OpenAI ChatGPT CLI, xAI Grok CLI, etc.
**Cross-Provider Tools:** Nodes wrapping Aider (model-agnostic agentic code editing)

**Rationale:** Providers continuously innovate on CLI features optimized for their specific models (compression algorithms, session management, context handling). Their native implementations outperform generic alternatives. Wrapping CLIs leverages billions in provider R&D investment.

**Note:** Specific library names and organization are implementation details determined during development.

#### Tier 3: Domain Libraries (Opt-in for Specialized Compute)

Specialized capabilities for specific domains or workloads:

```
joshua_ffmpeg/
└── ffmpeg_node.py             # GPU-accelerated video processing

joshua_stable_diffusion/
└── stable_diffusion_node.py   # Image generation

joshua_whisper/
└── whisper_node.py            # Speech-to-text
```

**Compute Offload Node Pattern:**

Domain nodes that require heavy compute (like `FFmpegNode`) implement a self-contained lifecycle:

1. **Query Fiedler** for available compute endpoints: `mcp__fiedler__request_gpu_resources(...)`
2. **Receive endpoint list** from Fiedler (service registry, not router)
3. **Implement client-side selection** - Try first endpoint, failover to next on error
4. **Execute workload** via `mcp__sutherland__execute_compute_job(...)`
5. **Return result** to flow

This pattern abstracts all complexity (service discovery, failover, resource allocation) from the MAD's main flow logic.

### 3. Three Acquisition Strategies

Node capabilities can be acquired through three distinct strategies, listed in priority order:

#### Strategy 1: Adopt (The Ideal)

Find and install pre-existing, packaged Langflow node libraries from the community.

- **When**: Always try this first
- **Benefit**: Zero development cost, community-vetted
- **Reality**: Limited ecosystem currently exists
- **Action**: Search Langflow community, GitHub, PyPI

#### Strategy 2: Wrap (The Accelerator)

Create bridge nodes to mature ecosystems like Node-RED using the **Polyglot Subprocess Pattern** (ADR-024).

**How it works:**
```python
# Generic NodeRedWrapperNode in Langflow
class NodeRedWrapperNode(CustomComponent):
    def build(self, node_name: str, inputs: dict) -> dict:
        # 1. Spawn Node.js subprocess
        # 2. Pass inputs via stdin
        # 3. Execute Node-RED node logic
        # 4. Return results via stdout
```

- **When**: Capability exists in another ecosystem (Node-RED, n8n, etc.)
- **Benefit**: Access to thousands of pre-built integrations (IoT, APIs, etc.)
- **Cost**: Small IPC overhead, one-time wrapper engineering
- **Future**: Hopper can autonomously refactor wrapped nodes to native Python (see Strategy 3)

**Examples:**
- MQTT integration (wrap Node-RED's mature MQTT node)
- AWS service integrations (wrap existing automation nodes)
- IoT device protocols (leverage Node-RED's extensive library)

#### Strategy 3: Build (The Necessity)

Create native Python implementations for capabilities unique to Joshua or where wrapping isn't viable.

**Two sub-strategies:**

**3a. Wrap Python Libraries:**
```python
# Wrap boto3 for AWS integration
class DescribeCommunicationsNode(CustomComponent):
    def build(self, case_id: str) -> dict:
        import boto3
        client = boto3.client('support')
        return client.describe_communications(caseId=case_id)
```

**3b. Build from Scratch:**
```python
# Unique Joshua architecture integration
class FiedlerQueryNode(CustomComponent):
    def build(self, requirements: dict) -> list:
        # Query Fiedler's MMI for service endpoints
        # Implement client-side selection logic
        # Return list of available endpoints
```

- **When**: No existing implementation exists, or capability is unique to Joshua
- **Focus**: Joshua-specific integrations (Fiedler, Sutherland, inter-MAD communication)
- **Priority**: Build what gives us unique architectural value

### 4. Hopper Optimization Cycle (Wrap → Native Evolution)

Wrapped nodes represent a **strategic choice**: rapid capability delivery now, with autonomous optimization later.

**The Evolution Lifecycle:**

**Phase 1: Inception (Wrapping)**
- Developer needs MQTT capability
- Finds robust Node-RED MQTT node
- Creates `MqttWrapperNode` using Polyglot Subprocess Pattern
- Capability available to ecosystem immediately

**Phase 2: Observation (Hamilton)**
- Hamilton monitors flow executions
- Logs that `MqttWrapperNode` is frequently used
- Records consistent 150ms IPC overhead per call

**Phase 3: Identification (Hopper)**
- Hopper queries Hamilton for bottlenecks
- Hamilton flags `MqttWrapperNode` as high-impact optimization candidate

**Phase 4: Autonomous Refactoring (Hopper)**
- Hopper analyzes wrapper and underlying Node.js source
- Finds native Python MQTT library (`paho-mqtt`)
- Writes new `MqttNativeNode` with identical interface
- Generates unit and integration tests

**Phase 5: Deployment (Hopper, Starret, Deming)**
- Hopper commits via Starret
- Deming runs tests
- New performant node available to ecosystem

**Phase 6: Migration (Hopper)**
- Hopper identifies flows using old wrapper
- Submits PRs to update them to native node
- System progressively optimizes itself

**Result**: Bootstrap ecosystem quickly with thousands of wrapped capabilities, then let autonomous AI engineer progressively replace "cheap but slow" wrappers with "performant native code."

### 5. Repository Structure

All node libraries live in the Joshua monorepo under a top-level `nodes/` directory:

```
Joshua/
├── lib/                       # Shared libraries (joshua_network, etc.)
├── mads/                      # MAD implementations
├── nodes/                     # Node library ecosystem
│   ├── [core_libraries]/     # Tier 1: Universal capabilities
│   ├── [cli_wrappers]/       # Tier 2: Provider CLI nodes
│   ├── [domain_libraries]/   # Tier 3: Specialized compute
│   └── ...
└── docs/
```

**Note:** Specific library names and directory structure are implementation details. The architecture requires fine-grained organization (one library per capability) and selective installation (MADs install only what they need).

**Benefits:**
- **Monorepo simplicity**: Easier dependency management, cross-library changes
- **Selective packaging**: MADs install only what they need
- **Clear organization**: Easy to find and browse available capabilities

## Consequences

### Positive

- **Rapid Capability Delivery**: Wrap existing ecosystems to bootstrap quickly
- **Minimal Bloat**: Fine-grained libraries mean MADs ship only what they use
- **Clear Responsibility**: One library = one capability = clear ownership
- **Universal LLM Access**: Every MAD gets resilient, multi-provider LLM via `joshua_core`
- **Autonomous Optimization**: Hopper progressively refactors wrapped nodes to native
- **Ecosystem Leverage**: Access to Node-RED's 4000+ nodes via wrapping strategy
- **Independent Evolution**: Update Claude integration without touching Gemini

### Neutral

- **New Development Pattern**: Developers must learn node creation vs traditional coding
- **Testing Paradigm Shift**: Integration-style testing of flows vs unit testing of classes
- **Wrapping Overhead**: Small IPC cost for wrapped nodes (eliminated by Hopper over time)

### Negative

- **Polyglot Complexity**: Wrapped nodes require maintaining Node.js subprocess infrastructure
- **Discovery Challenge**: Developers need clear catalog of available nodes
- **Fragmentation Risk**: Fine-grained approach requires discipline to avoid duplication

## Related ADRs

- **ADR-015**: Joshua GPU Compute Cluster (Sutherland) - GPU resource management and Compute Offload Node pattern
- **ADR-024**: Polyglot Subprocess Pattern (Malory) - Foundation for wrapping strategy
- **ADR-030**: Langflow Internal Architecture - Why we need custom nodes
- **ADR-032**: Fully Flow-Based Architecture - How nodes are used in flows
- **ADR-033**: Metaprogramming via Hopper-Orchestrated Optimization - Autonomous refactoring
- **ADR-034**: CLI-First LLM Integration Strategy - Provider wrapping approach
- **ADR-035**: Direct Access AI Model Nodes - Service discovery pattern

## Related Requirements

- **Fiedler Requirements (04)**: GPU resource orchestration and AI model ecosystem management

## Implementation Notes

### Immediate Next Steps

1. Create `joshua_core/` with:
   - Basic flow control nodes (if/else, loop, switch)
   - `LLMCLINode` for universal LLM access
   - Shared utilities (string format, JSON parse)

2. Document the Compute Offload Node Pattern for heavy workloads

3. Create catalog/registry of available nodes for developer discovery

### Future Work

1. Build generic `NodeRedWrapperNode` harness for Strategy 2
2. Integrate Hopper optimization cycle into CI/CD pipeline
3. Create node performance monitoring in Hamilton
4. Establish node contribution guidelines and review process
