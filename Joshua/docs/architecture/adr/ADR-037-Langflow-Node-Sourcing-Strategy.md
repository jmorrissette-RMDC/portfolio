# ADR-037: LangFlow Node Sourcing Strategy - Use, Compose, Fork, Build Hierarchy

**Status:** Accepted
**Date:** 2025-12-22 (Updated with Tier 2.5 and Component Evolution Lifecycle)
**Deciders:** System Architect
**Related:** ADR-032 (Fully Flow-Based Architecture), ADR-036 (Node Library Architecture), ADR-033 (Hopper Metaprogramming)

---

## Context and Problem Statement

Per **ADR-032**, the Joshua ecosystem adopts a fully flow-based architecture where logic is defined in LangFlow `.json` flows, not imperative Python code. MADs compose functionality by connecting nodes in visual flows.

Our initial approach (documented in ADR-036 and `joshua_core` requirements) was to **build custom nodes from scratch**:
- `LLMCLINode`, `IfElseNode`, `LoopNode`, `SwitchNode`
- `FilterNode`, `MergeNode`, `TransformNode`, `LogNode`

However, **we designed these nodes before fully exploring the LangFlow ecosystem**. Research reveals that LangFlow provides:

1. **Extensive Default Nodes**: Dozens of pre-configured nodes (Models, Vector Stores, Embeddings, Helpers/Logic, Inputs/Outputs)
2. **Community Store**: Marketplace of community-contributed components (hundreds to thousands of nodes)
3. **LangChain Wrapper Capability**: Since LangFlow is built on LangChain, any LangChain tool/chain/agent can be wrapped as a node with minimal code
4. **Custom Component Framework**: Python-based node creation for truly unique functionality

**The Problem**: Building custom nodes for generic functionality (flow control, data transformation, LLM access) duplicates work that likely already exists in the LangFlow ecosystem. This wastes development time and creates maintenance burden.

**The Question**: What is the correct strategy for sourcing nodes for Joshua MADs?

---

## Decision

We adopt a **multi-tier node sourcing hierarchy** that prioritizes reuse and composition over custom development:

**Update (2025-12-22)**: Following deeper ecosystem research and Gemini conversation analysis, we've refined the hierarchy to include:
- **Tier 1.5: COMPOSE** - Build capabilities as reusable flows (flow-first MVP strategy)
- **Tier 2.5: FORK** - Extend existing components when 90% of functionality exists
- **Component Evolution Lifecycle** - Data-driven strategy for hardening flows into custom nodes

### Tier 1: **USE** - Native LangFlow Nodes (Highest Priority)

**Definition**: Nodes available in LangFlow's default palette or community Store.

**When to Use**:
- Functionality exists in LangFlow's built-in components
- Community Store has a well-maintained, validated component
- Node provides standard capabilities (LLM access, vector stores, data manipulation)

**Process**:
1. Search LangFlow default palette by category (Models, Helpers, Logic, etc.)
2. Search LangFlow Store for community components
3. Evaluate quality (documentation, maintenance, compatibility)
4. Use if meets requirements

**Examples**:
- LLM access → Use native Language Model component (OpenAI/Anthropic/Google)
- Conditional logic → Use LangFlow's If-Else and Condition nodes
- Iteration → Use LangFlow's Loop component (v1.1.2+)
- Data transformation → Use Data Operations, Parser, Type Convert nodes
- **MAD-to-MAD communication** → Use native **MCP Tools component** (see Critical Discovery section)
- Vector search → Use Pinecone/ChromaDB/AstraDB/Qdrant nodes

**Rationale**: Zero development cost, community-maintained, battle-tested.

### Tier 1.5: **COMPOSE** - Reusable Flows (Flow-First MVP Strategy)

**Definition**: Build capabilities as LangFlow `.json` flows that compose existing native nodes into reusable patterns.

**When to Use**:
- Need emerges for new functionality
- Can be satisfied by combining existing native nodes
- Want to deliver value immediately without custom development
- Exploring solution space before committing to custom implementation

**Process**:
1. Identify native nodes that provide required primitive operations
2. Design flow connecting these nodes to achieve desired behavior
3. Create `.json` flow file with clear naming and documentation
4. Test flow execution via FlowRunner
5. Deploy as reusable component (can be called by other flows)
6. Monitor performance via Hamilton MAD (see Component Evolution Lifecycle below)

**Examples**:
- **FFmpeg Processing Flow**: Compose MCP Tools calls (to Fiedler → Sutherland) for GPU offloading
- **Multi-Step Reasoning Flow**: Chain Language Model → Critic → Refiner nodes
- **Data Validation Pipeline**: File → Parser → Data Operations (filter) → Loop → Output
- **Complex MAD Delegation**: Chat Input → Agent[MCP Tools to multiple MADs] → Aggregation → Output

**Advantages**:
- **Speed**: Assemble and test in minutes, not days
- **Transparency**: Logic is visual, easy to understand and modify (even by non-programmers)
- **Zero Code**: No Python required, minimizes bug surface area
- **Immediate Value**: Functional from day one, iterative refinement
- **Version Controlled**: `.json` flows tracked in git like code

**When to Evolve to Custom Node** (see Component Evolution Lifecycle):
- Hamilton reports flow is performance bottleneck
- Flow becomes widely reused, abstraction would reduce complexity
- Hopper can autonomously convert flow → optimized Python node

**Rationale**: Flow-first strategy allows rapid MVP delivery, defers premature optimization until data justifies hardening.

### Tier 2: **WRAP** - Existing Ecosystems (Medium Priority)

**Definition**: Wrapping external tools/libraries as LangFlow Custom Components.

**When to Use**:
- Functionality doesn't exist in LangFlow but exists in another ecosystem
- Well-established tool with active maintenance
- Wrapping effort < building from scratch

**Target Ecosystems to Wrap**:
1. **LangChain Tools**: Any LangChain tool, chain, or agent (native integration path)
2. **Node-RED Nodes**: Thousands of industrial/IoT nodes (via Node-RED wrapper)
3. **n8n Integrations**: Automation-focused integrations (API wrappers, webhooks)
4. **Python Libraries**: Mature libraries with stable APIs (ffmpeg, pandas, requests)

**Process**:
1. Identify external tool that solves the need
2. Create LangFlow Custom Component wrapper
3. Define input/output schemas
4. Implement `build()` method that calls underlying tool
5. Document wrapper in `/docs/integrations/wrappers/`

**Example - Wrapping a Node-RED node**:
```python
from langflow import CustomComponent

class NodeREDWrapperNode(CustomComponent):
    display_name = "Node-RED: MQTT Publisher"
    description = "Wraps Node-RED MQTT node"

    def build_config(self):
        return {
            "broker": {"display_name": "MQTT Broker"},
            "topic": {"display_name": "Topic"},
            "message": {"display_name": "Message"}
        }

    def build(self, broker, topic, message):
        # Call Node-RED runtime via HTTP API
        # or embed Node-RED node.js execution
        result = self._call_nodered_node(...)
        return result
```

**Rationale**: Leverage massive existing ecosystems without reinventing wheels.

### Tier 2.5: **FORK** - Extend Existing Components (Preferred over Build)

**Definition**: Fork and extend existing LangFlow components when functionality is 90% there, adding only Joshua-specific logic.

**When to Use**:
- Existing component provides solid foundation (90%+ of needed functionality)
- Need to add Joshua-specific behavior on top of generic functionality
- Community component has good code quality and maintenance
- Forking effort << building from scratch

**Process**:
1. Identify closest LangFlow component (default palette or community)
2. Fork source code from `langflow-ai/langflow` repository
3. Create Joshua-specific variant (e.g., `JoshuaMCPClientNode` from generic `WebSocketNode`)
4. Add only the delta logic needed (10-20% custom code):
   - Joshua-specific configuration
   - Integration with Joshua services (Rogers, Fiedler, Sutherland)
   - Protocol adaptations (MCP message formatting, service discovery)
5. Document what was added and why in component docstring
6. Consider contributing generic improvements back upstream
7. Maintain fork with periodic upstream syncs

**Examples**:

**Example 1: Fork MCP Tools → JoshuaMCPClientNode**
```python
# Fork LangFlow's native MCP Tools component
# Add: Rogers service discovery for MAD-to-MAD calls
class JoshuaMCPClientNode(MCPToolsComponent):  # Inherit 90% functionality
    display_name = "Joshua MCP Client"
    description = "MCP client with Rogers service discovery"

    def build(self, target_mad: str, tool_name: str, **kwargs):
        # NEW: Query Rogers for MAD endpoint
        mad_endpoint = self._discover_mad_via_rogers(target_mad)

        # INHERITED: Use parent's MCP protocol handling
        return super().build(server_url=mad_endpoint, tool=tool_name, **kwargs)

    def _discover_mad_via_rogers(self, mad_name: str) -> str:
        # Joshua-specific: 10% custom logic
        # Calls rogers_find_tool to get MAD address
        ...
```

**Example 2: Fork Subprocess Node → ClaudeSessionNode**
```python
# Fork LangFlow's generic Bash/Subprocess component
# Add: Claude-specific session management and output parsing
class ClaudeSessionNode(SubprocessComponent):  # Inherit subprocess handling
    display_name = "Claude CLI Session"
    description = "Stateful Claude Code CLI session wrapper"

    def build_config(self):
        config = super().build_config()  # Inherit base fields
        # ADD: Claude-specific fields
        config["session_id"] = {"display_name": "Session ID", "required": False}
        config["auto_compress"] = {"display_name": "Auto-compress context", "default": True}
        return config

    def build(self, prompt: str, session_id: str = None, **kwargs):
        # NEW: Build Claude-specific command
        cmd = ['claude', '--resume', session_id] if session_id else ['claude']
        cmd.append(prompt)

        # INHERITED: Use parent's subprocess execution (90% of complexity)
        output = super()._run_subprocess(cmd)

        # NEW: Parse Claude's specific output format (10% custom)
        return self._parse_claude_output(output)
```

**Advantages**:
- **Reuse 90%**: Leverage community-tested code for complex operations (WebSockets, subprocess management, etc.)
- **Focus on Delta**: Only write Joshua-specific 10%, not entire component
- **Faster than Build**: Fork + extend << build from scratch
- **Upstream Benefits**: Inherit bug fixes and improvements from community
- **Open Source Collaboration**: Can contribute generic improvements back

**When to Fork vs. Build**:
- Fork: Existing component provides clear starting point
- Build: No existing component is even close (Tier 3)

**Maintenance Strategy**:
- Track upstream changes via git remote
- Periodically sync fork with upstream improvements
- Document Joshua-specific deltas clearly for future maintainers

**Rationale**: Intelligent forking minimizes custom development while maximizing community leverage. Prefer extending proven components over building from scratch.

### Tier 3: **BUILD** - Custom Joshua Nodes (Lowest Priority)

**Definition**: Building nodes from scratch for Joshua-specific functionality.

**When to Use** (ALL must be true):
- Functionality is truly unique to Joshua's architecture
- No existing LangFlow/LangChain/ecosystem equivalent
- Cannot be reasonably wrapped from external tool
- Provides strategic value to Joshua ecosystem

**Reserved for**:
- **Joshua-specific orchestration**: Kaiser team assembly, Moses container placement
- **Constitutional enforcement**: Joshua's governance rules
- **PCP-specific nodes** (when V5.0 arrives): DTR routing, LPPM learned patterns, CET context optimization
- **Advanced Rogers integration** (V1.0+): Service discovery patterns beyond basic MCP

**Examples of what NOT to build**:
- ❌ Generic LLM access (use LangFlow's native Language Model component)
- ❌ If/else logic (use LangFlow's If-Else and Condition nodes)
- ❌ Loops/iteration (use LangFlow's Loop component)
- ❌ Data filtering/transformation (use Data Operations, Parser, Type Convert nodes)
- ❌ JSON parsing (use LangFlow's Parser component)
- ❌ **MAD-to-MAD communication** (use native **MCP Tools component**, fork if Rogers integration needed)

**Examples of what TO build**:
- ✅ `KaiserTeamAssemblyNode` - Unique to Kaiser's team composition logic (V6.0)
- ✅ `MosesPlacementNode` - Unique to Moses's container orchestration (V6.0)
- ✅ `ConstitutionalCheckNode` - Unique to Joshua's governance enforcement
- ✅ `DTRRoutingNode` - Unique to PCP Tier 1 dynamic triage (V5.0)
- ✅ `LPPMPatternMatchNode` - Unique to PCP Tier 2 learned patterns (V5.0)

**Process**:
1. Document why Tier 1 and Tier 2 don't apply
2. Create requirements document in `/docs/requirements/Nodes/`
3. Implement as LangFlow Custom Component
4. Comprehensive testing (unit + integration)
5. Publish to internal node registry

**Rationale**: Minimize custom development to only what's truly differentiating.

---

## Revised joshua_core Scope

**Previous Scope** (ADR-036): Universal node library with flow control, data transformation, LLM access, utilities

**New Scope**: Joshua-specific foundational nodes only

### Nodes to REMOVE from joshua_core (use LangFlow native instead):
- `LLMCLINode` → Use LangFlow's **Language Model component** (confirmed exists)
- `IfElseNode` → Use LangFlow's **If-Else component** (confirmed exists)
- `LoopNode` → Use LangFlow's **Loop component** (confirmed exists, v1.1.2+)
- `SwitchNode` → Use LangFlow's **Condition component** (confirmed exists)
- `FilterNode` → Use LangFlow's **Data Operations component** (confirmed exists)
- `MergeNode` → Use LangFlow's **Data Operations component** (confirmed exists)
- `TransformNode` → Use LangFlow's **Type Convert, Parser, Structured Output components** (confirmed exist)
- `LogNode` → Investigate LangFlow's built-in logging (not yet researched)
- `MCPClientNode` → Use LangFlow's **MCP Tools component** (confirmed exists, see Critical Discovery)

### Nodes to KEEP in joshua_core (Joshua-specific):
- **To be determined after LangFlow ecosystem exploration**

**Action Required**:
1. Explore LangFlow default palette comprehensively
2. Explore LangFlow Store for community components
3. Create `/docs/research/langflow_node_catalog.md` documenting available nodes
4. Identify gaps where custom Joshua nodes are truly needed
5. Update `joshua_core` requirements to reflect revised scope

---

## Template MAD Baseline

**Decision**: The MAD Template (`MAD_Template_V0.7_Requirements.md`) should **demonstrate the baseline using only native LangFlow nodes**.

**Rationale**:
- Shows developers what's possible with zero custom development
- Validates that core MAD patterns work with LangFlow defaults
- Identifies real gaps (not hypothetical ones) that require custom nodes

**Template Flows Should Use**:
- Native LLM nodes (OpenAI, Anthropic, Google, or Ollama for Sutherland)
- Native flow control (if LangFlow provides conditional/iteration nodes)
- Native data manipulation (text splitters, transformers)
- Native I/O nodes (chat inputs, file loaders, outputs)

**Custom Nodes in Template**: None initially - only add if demonstrating Joshua-specific functionality becomes necessary

---

## LangFlow Custom Component Structure

When we do build custom nodes (Tier 3), they must follow LangFlow's Custom Component pattern:

### Required Structure

```python
from langflow import CustomComponent
from langflow.field_typing import Text, Data

class MyCustomNode(CustomComponent):
    display_name = "My Custom Node"
    description = "What this node does"
    category = "Joshua/Orchestration"  # Custom category for Joshua nodes

    def build_config(self):
        """Define UI fields that appear in LangFlow"""
        return {
            "input_field": {
                "display_name": "Input Field",
                "field_type": "str",
                "required": True
            },
            "optional_field": {
                "display_name": "Optional Field",
                "field_type": "int",
                "required": False,
                "default": 10
            }
        }

    def build(self, input_field: str, optional_field: int = 10) -> Data:
        """
        Execute node logic.

        This method is called by LangFlow when the flow runs.
        Parameters match the fields defined in build_config().
        """
        # Node logic here
        result = self.process(input_field, optional_field)

        return Data(value=result)
```

### Type System Mapping

LangFlow uses color-coded ports for type safety. Our types map as follows:

| Joshua Type | LangFlow Type | Port Color | Example |
|-------------|---------------|------------|---------|
| `string` | `Text` | Blue | User prompts, file paths |
| `array` | `List[Data]` | Green | Collections, batches |
| `object` | `Data` | Orange | Structured data, configs |
| `llm_message` | `Message` | Purple | LLM responses, chat history |
| `boolean` | `bool` | Yellow | Flags, conditions |

**Example**:
```python
def build(self, prompt: Text, temperature: float) -> Message:
    # LangFlow knows: prompt port is blue, output port is purple
    ...
```

---

## Implementation Phases

### Phase 1: Ecosystem Exploration (IMMEDIATE)

**Goal**: Understand what exists before building anything

**Tasks**:
1. Install LangFlow locally or use DataStax cloud version
2. Catalog all default nodes by category
3. Search LangFlow Store for popular components
4. Document findings in `/docs/research/langflow_ecosystem_exploration.md`
5. Identify confirmed gaps (functionality needed but unavailable)

**Deliverable**: Comprehensive catalog of available nodes

### Phase 2: Template MAD with Native Nodes (AFTER Phase 1)

**Goal**: Prove core MAD patterns work with LangFlow defaults

**Tasks**:
1. Build example flows using only native LangFlow nodes
2. Implement minimal `server_joshua.py` to execute flows
3. Validate flow execution, tool exposure, configuration
4. Document any limitations or gaps encountered

**Deliverable**: Working template MAD with zero custom nodes

### Phase 3: Custom Node Development (ONLY IF NEEDED)

**Goal**: Build only what's truly necessary

**Tasks**:
1. For each identified gap, re-evaluate Tier 1 (Use) and Tier 2 (Wrap)
2. For confirmed Tier 3 needs, create requirements document
3. Implement as LangFlow Custom Components
4. Test and document

**Deliverable**: Minimal set of Joshua-specific nodes

---

## Component Evolution Lifecycle: Flow-First Strategy

**Principle**: Accept MVPs that work, then evolve them agile-ly based on real-world data.

This lifecycle formalize when and how to evolve "soft" components (flows) into "hard" components (custom nodes), guided by observability data rather than premature optimization.

### Stage 1: Flow-First MVP ("Soft" Component)

**Principle**: Start by building required capability as a `.json` flow using existing nodes (Tier 1, 1.5, or 2).

**Why**:
- **Speed**: Incredibly fast to assemble and test (minutes to hours, not days)
- **Transparency**: Logic is visual and easy for anyone (including agents like Hopper) to understand and modify
- **Low Risk**: No custom Python code minimizes bug surface area
- **Immediate Value**: Delivers functionality from day one
- **Iterative**: Easy to refine through visual editing

**Mechanism**:
1. Identify need for new capability
2. Design flow using native LangFlow nodes
3. Create `.json` flow file in MAD's `flows/` directory
4. Test via FlowRunner
5. Deploy to production
6. **Monitor via Hamilton** (critical next step)

**Outcome**: A functional, version-controlled flow that "works." It delivers value immediately without custom development.

### Stage 2: Observe and Measure (Hamilton Monitoring)

**Principle**: Deploy the flow and let it run in the real system. Don't guess what needs optimization—measure it.

**Mechanism**: Hamilton MAD (System Monitoring, per ADR-XXX) observes performance of all running flows, tracking:
- **Execution Frequency**: How often is this flow called?
- **Latency**: Is this flow a bottleneck? P50, P95, P99 latencies
- **Error Rates**: Reliability and failure modes
- **Reuse Patterns**: How many other flows/MADs call this flow?
- **Resource Usage**: CPU, memory, LLM API costs

**Metrics Collection**:
```python
# Hamilton tracks every flow execution
{
  "flow_id": "hopper/code_generation_flow.json",
  "execution_count": 1247,
  "p95_latency_ms": 3420,
  "error_rate": 0.02,
  "calling_flows": ["hopper/main_flow.json", "deming/test_flow.json", ...],
  "llm_calls_per_execution": 3.2
}
```

**Outcome**: Real-world performance data informs optimization decisions.

### Stage 3: Data-Driven Hardening Decision

**Principle**: Evolve a "soft" flow into a "hard" custom node **only when there is a data-driven reason** to do so.

**Triggers for Hardening**:

**Trigger 1: Performance Bottleneck**
- Hamilton reports flow is in top 10% of latency offenders
- Flow execution time significantly higher than necessary
- Overhead of FlowRunner executing many small nodes >> single compiled Python node
- **Example**: Tight loop executing 1000 iterations via Loop node (visual overhead per iteration)

**Trigger 2: High Reusability**
- Flow becomes critical, widely-used component (called by 5+ other flows)
- Encapsulating logic into single node with clean interface reduces complexity
- Internal complexity hidden from users, reducing cognitive load
- **Example**: "Data validation pipeline" called by every MAD's ingestion flow

**Trigger 3: Strategic Abstraction**
- Flow represents core Joshua pattern worthy of formal abstraction
- Publishing as node improves developer experience
- **Example**: "Rogers service discovery + MCP call" pattern used everywhere

**Decision Matrix**:
```
IF (latency_p95 > threshold AND execution_count > min_usage)
   OR (calling_flows.length > reusability_threshold)
   OR (strategic_pattern_identified)
THEN trigger_hardening_workflow()
```

**Non-Triggers** (don't harden prematurely):
- Flow works fine and isn't a bottleneck
- Low usage (called infrequently)
- Logic may still change (in exploration phase)

### Stage 4: Autonomous Evolution (Hopper Metaprogramming)

**Principle**: Hardening should be automated, not manual. Hopper MAD (per ADR-033) performs metaprogramming to convert flows → nodes.

**Workflow**:

1. **Trigger**: Hamilton sends `harden_flow` task to Hopper
   ```json
   {
     "task": "harden_flow",
     "flow_path": "hopper/code_generation_flow.json",
     "reason": "performance_bottleneck",
     "metrics": { "p95_latency_ms": 3420, "execution_count": 1247 }
   }
   ```

2. **Analysis**: Hopper reads `.json` flow and source code of component nodes
   ```python
   flow_definition = json.load("hopper/code_generation_flow.json")
   node_sources = [read_source(node.type) for node in flow_definition.nodes]
   ```

3. **Metaprogramming**: Hopper generates optimized Python custom node
   - Replicates flow logic in imperative code
   - Eliminates FlowRunner overhead
   - Preserves exact same input/output interface
   - Adds performance optimizations (caching, batching, etc.)

4. **Code Generation**: Creates new Custom Component
   ```python
   # Generated by Hopper from hopper/code_generation_flow.json
   class CodeGenerationNode(CustomComponent):
       display_name = "Code Generation (Optimized)"
       description = "Hardened version of code_generation_flow.json"

       def build(self, specification: Text, context: Data) -> Message:
           # Imperative version of flow logic
           # (previously: Prompt Template → Language Model → Parser → Validator)
           prompt = self._build_prompt(specification, context)  # Inline
           response = self._call_llm(prompt)  # Direct API call, no node overhead
           parsed = self._parse_output(response)  # Inline
           validated = self._validate(parsed)  # Inline
           return Message(content=validated)
   ```

5. **Submission**: Hopper creates PR via Starret
   - New node added to appropriate library (e.g., `joshua_core` or domain-specific)
   - Original flow marked as `@deprecated` with pointer to new node
   - Migration guide included

6. **Validation**: Deming tests new node
   - Functional equivalence: Same outputs for same inputs as original flow
   - Performance improvement: Confirms latency reduction
   - Integration tests: Ensures calling flows work with new node

7. **Deployment**: After Deming approval, new node deployed
   - Flows using old flow are gradually migrated
   - Original flow archived for historical reference

**Outcome**: Self-optimizing system. Critical flows autonomously evolve into performant, reusable nodes based on real-world usage data.

### Lifecycle Summary

```
Flow-First MVP → Deploy → Hamilton Monitors → Performance Data
                                                  ↓
                                   Trigger: Bottleneck or High Reuse
                                                  ↓
                               Hopper Metaprograms → Hardened Node
                                                  ↓
                         Deming Validates → Deploy → Repeat Cycle
```

**Benefits**:
- **No Premature Optimization**: Build flows first, harden only when justified
- **Data-Driven**: Real metrics guide evolution, not guesses
- **Autonomous**: Hopper handles hardening, not manual developer work
- **Continuous Improvement**: System gets faster over time without explicit optimization effort
- **Preserved Simplicity**: Most flows stay as flows; only critical paths become nodes

**Anti-Pattern to Avoid**:
- ❌ Building custom nodes upfront for "performance" without data
- ❌ Hardening rarely-used flows
- ❌ Manual conversion (use Hopper metaprogramming)

---

## Critical Discovery: Native MCP Support in LangFlow

**Date**: 2025-12-22 (Follow-up research after Gemini conversation)

During initial ADR drafting, we assumed MAD-to-MAD communication would require custom nodes. **This assumption was incorrect.** LangFlow has **full native MCP (Model Context Protocol) support** as of version 1.4+.

### LangFlow's MCP Tools Component

**Component**: `MCP Tools` (native LangFlow component in Agents category)

**Capabilities**:
- **Connect to any MCP server**: Supports three connection modes:
  - **JSON**: Direct configuration object
  - **STDIO**: Command-based startup (e.g., `uvx mcp-server-fetch`)
  - **HTTP/SSE**: URL-based connections for remote servers
- **Expose MCP server tools to agents**: Discovered tools become available to Agent component
- **Select specific tools or allow all**: Granular control over tool exposure
- **Advanced features**: Caching, SSL verification, multi-tool workflows

**Usage Pattern**:
```
MCP Tools component (configured for target MAD)
  → Connected to Agent component's Tools port
  → Agent autonomously calls target MAD's exposed tools
```

### LangFlow as Both MCP Client AND Server

**Dual Functionality** (unprecedented in MCP ecosystem):

**As MCP Client** (consuming other MCP servers):
- Can connect to "thousands of MCP servers that exist today"
- Native integration with LangFlow's Agent component
- Immediate access to entire MCP ecosystem

**As MCP Server** (exposing flows as tools):
- **Every LangFlow flow can be exposed as an MCP tool**
- **Files uploaded to LangFlow become MCP resources**
- External MCP clients (e.g., Claude Desktop) can call LangFlow flows

**Server Endpoints**:
```
# Project-specific
http://localhost:7860/api/v1/mcp/project/PROJECT_ID/streamable

# Global server (all flows)
http://localhost:7860/api/v1/mcp/streamable
```

### Implications for Joshua Architecture

**1. MAD-to-MAD Communication Works Out of the Box**

Example flow for one MAD calling another:
```json
{
  "components": [
    {
      "type": "Chat Input",
      "id": "user_request"
    },
    {
      "type": "MCP Tools",
      "config": {
        "server": "http://sutherland-mad:7860/api/v1/mcp/streamable",
        "mode": "HTTP/SSE"
      },
      "id": "sutherland_tools"
    },
    {
      "type": "Agent",
      "tools": ["sutherland_tools"],
      "id": "delegating_agent"
    },
    {
      "type": "Chat Output",
      "id": "response"
    }
  ]
}
```

This flow allows any MAD to call Sutherland's exposed tools using only native components!

**2. Revised Custom Node Assessment**

Original assumption: "We need to build MCPClientNode for MAD-to-MAD communication"

**Reality**:

| Scenario | Solution | Tier |
|----------|----------|------|
| **Basic MAD-to-MAD calls** | Use native MCP Tools component | Tier 1 (USE) |
| **Add Rogers service discovery** | Fork MCP Tools → JoshuaMCPClientNode | Tier 2.5 (FORK) |
| **Advanced orchestration patterns** | Compose flows with MCP Tools | Tier 1.5 (COMPOSE) |

**No custom MCPClientNode needed** unless we want Rogers integration (in which case, fork native component, don't build from scratch).

**3. Example: Hopper Calling Starret**

```json
{
  "flow_name": "git_commit_flow",
  "components": [
    {
      "type": "MCP Tools",
      "config": {
        "server": "http://starret-mad:7860/api/v1/mcp/streamable"
      },
      "id": "starret_tools"
    },
    {
      "type": "Agent",
      "tools": ["starret_tools"],
      "system_prompt": "You are Hopper. Use Starret tools to commit code changes.",
      "id": "hopper_agent"
    }
  ]
}
```

Hopper can now call `starret_commit`, `starret_push`, etc. using native components.

**4. V1.0 Conversation Bus Integration**

When V1.0 arrives with Rogers (Kafka-based service bus), we may need to fork MCP Tools to:
- Query Rogers for MAD endpoints (`rogers_find_tool`)
- Cache discovered endpoints
- Handle service mesh routing

But this is a **10% delta on top of existing component**, not a full rebuild.

### Updated Tier 1 Examples

Based on MCP discovery, update Tier 1 examples:

**Before** (speculative):
- "MAD-to-MAD communication → Custom MCPClientNode"

**After** (validated):
- **MAD-to-MAD communication** → Use native **MCP Tools component**
- **Advanced routing with Rogers** → Fork MCP Tools (Tier 2.5)
- **Complex delegation patterns** → Compose MCP Tools in flows (Tier 1.5)

### Sources

- [LangFlow MCP Client Documentation](https://docs.langflow.org/mcp-client)
- [Introducing MCP Integration in Langflow](https://www.langflow.org/blog/introducing-mcp-integration-in-langflow)
- [LangFlow 1.4 Release Notes](https://www.langflow.org/blog/langflow-1-4-organize-workflows-connect-with-mcp)
- [MCP Tutorial](https://docs.langflow.org/mcp-tutorial)

### Lessons Learned

**Mistake**: Assumed LangFlow lacked MCP knowledge based on incomplete research

**Correction**: Always verify ecosystem capabilities through:
1. Official documentation search
2. GitHub repository inspection
3. Community blog posts and release notes
4. Hands-on testing when possible

**Validation of ADR-037 Hierarchy**: This discovery proves the Use → Compose → Fork → Build strategy is correct. We almost built MCPClientNode from scratch when a perfect native component already existed.

---

## Consequences

### Positive

**Massive Time Savings**:
- Avoid building hundreds of generic nodes that already exist
- Leverage community maintenance of popular components
- Focus development on Joshua's unique value proposition

**Better Quality**:
- Battle-tested nodes from LangFlow/LangChain ecosystems
- Active community support and bug fixes
- Regular updates from upstream providers

**Faster Onboarding**:
- Developers familiar with LangFlow can immediately contribute
- Standard patterns reduce learning curve
- Visual debugging via LangFlow UI

**Strategic Focus**:
- Build only what differentiates Joshua
- Invest in orchestration, not plumbing
- More resources for PCP development (V5.0)

### Negative

**Discovery Overhead**:
- Must thoroughly explore LangFlow ecosystem before building anything
- Cataloging effort upfront
- Potential false starts if we miss existing solutions

**External Dependency**:
- Reliance on LangFlow project's stability and direction
- Risk of upstream changes breaking our flows
- Need to track LangFlow updates

**Wrapping Complexity**:
- Tier 2 (Wrap) requires understanding multiple ecosystems
- Integration testing across different wrapped tools
- Potential impedance mismatches between ecosystems

**Potential Limitations**:
- LangFlow's Custom Component framework may have constraints
- Visual flow debugging may be harder than Python debugger for complex logic
- Performance overhead from LangFlow runtime

### Neutral

**joshua_core Redefinition**:
- Existing specification work not wasted (documented thinking)
- Becomes reference for "what we thought we needed vs. what exists"
- Valuable for understanding gaps

**Template MAD Simplicity**:
- Simpler template (no custom nodes) easier to understand
- May need more complex template later to show custom node patterns
- Two templates possible: "baseline native" vs. "advanced custom"

---

## Migration Path

### Existing Work

**joshua_core specification** (`joshua_core_node_library_requirements.md`):
- Mark as **SUPERSEDED BY ADR-037**
- Rename to `joshua_core_node_library_requirements_REFERENCE.md`
- Add banner explaining it was pre-ecosystem exploration
- Keep as reference for understanding initial thinking

**Node Library Architecture** (ADR-036):
- Still valid for Tier 3 (custom nodes we do build)
- Update to reference ADR-037 for sourcing strategy
- Clarify three-tier hierarchy

**MAD Template** (`MAD_Template_V0.7_Requirements.md`):
- Update Section 2.3 (Node Libraries) to reference native LangFlow nodes
- Remove joshua_core dependency from requirements.txt
- Update Section 3 (Flow Architecture) to show native node examples
- Add note: "This template uses only native LangFlow nodes to demonstrate baseline"

### Future Work

**When V5.0 PCP arrives**:
- PCP component libraries (joshua_dtr, joshua_lppm, joshua_cet, joshua_crs) will need custom nodes
- These are Tier 3 (truly unique to Joshua)
- Follow Custom Component pattern defined in this ADR

**When V6.0 eMADs arrive**:
- Kaiser and Moses will need custom orchestration nodes
- These are Tier 3 (unique to Joshua's architecture)
- Follow Custom Component pattern defined in this ADR

---

## Decision Rationale

**Why this hierarchy makes sense**:

1. **Use First**: If it exists and works, use it. Don't rebuild wheels. (Tier 1)
2. **Compose Second**: Build capabilities as flows for rapid MVP delivery. (Tier 1.5)
3. **Wrap Third**: Massive ecosystems (LangChain, Node-RED, n8n) have solved common problems. Leverage via wrappers. (Tier 2)
4. **Fork Fourth**: When 90% exists, extend rather than rebuild. (Tier 2.5)
5. **Build Last**: Only build what's truly unique to Joshua's value proposition. (Tier 3)
6. **Evolve Continuously**: Harden flows → nodes when data justifies (Component Evolution Lifecycle)

**Why we made the original mistake**:
- Designed nodes before understanding the ecosystem
- Assumed "custom system needs custom nodes" (not true for generic functionality)
- Didn't realize the scale of LangFlow's community

**Why this ADR corrects course**:
- Adaptive architecture - learn and adjust
- Research revealed better path forward
- Documented our thinking for future reference

**The Right Way Forward**:
- Explore thoroughly before building
- Reuse aggressively
- Build strategically

---

## Related Decisions

- **ADR-032**: Fully Flow-Based Architecture - Established LangFlow as foundation
- **ADR-036**: Node Library Architecture - Still valid for custom nodes we do build
- **ADR-034**: CLI-First LLM Integration - May be superseded by native LangFlow LLM nodes
- **ADR-030**: Langflow Internal Architecture - Defines Joshua_Flow_Runner for executing flows

---

## References

### LangFlow Documentation
- **LangFlow Documentation**: https://docs.langflow.org/
- **LangFlow GitHub**: https://github.com/langflow-ai/langflow
- **LangFlow Store**: https://www.langflow.store/ (community components)
- **Components Overview**: https://docs.langflow.org/concepts-components
- **Custom Components Guide**: https://docs.langflow.org/components-custom-components

### MCP Integration
- **LangFlow MCP Client**: https://docs.langflow.org/mcp-client
- **MCP Integration Announcement**: https://www.langflow.org/blog/introducing-mcp-integration-in-langflow
- **LangFlow 1.4 Release**: https://www.langflow.org/blog/langflow-1-4-organize-workflows-connect-with-mcp
- **MCP Tutorial**: https://docs.langflow.org/mcp-tutorial
- **Model Context Protocol Spec**: https://modelcontextprotocol.io/

### External Ecosystems
- **LangChain Documentation**: https://python.langchain.com/ (for wrapping LangChain tools)
- **Node-RED**: https://nodered.org/ (industrial/IoT node ecosystem)
- **n8n**: https://n8n.io/ (automation workflow ecosystem)

### Research & Conversations
- **Gemini Conversation** (2025-12-22): Revealed LangFlow ecosystem scale, fork strategy, and Component Evolution Lifecycle
- **LangFlow Ecosystem Exploration**: `/docs/research/langflow_ecosystem_exploration.md` (comprehensive catalog)

### Related ADRs
- **ADR-032**: Fully Flow-Based Architecture - Established LangFlow as foundation
- **ADR-033**: Hopper Metaprogramming - Autonomous flow → node hardening
- **ADR-036**: Node Library Architecture - Still valid for Tier 3 custom nodes
- **ADR-034**: CLI-First LLM Integration - Provider wrapper strategy
- **ADR-030**: Langflow Internal Architecture - Joshua_Flow_Runner implementation

---

**Last Updated:** 2025-12-22 (Updated with Tier 1.5, 2.5, Component Evolution Lifecycle, and MCP discovery)
**Next Review:** After Phase 2 (Template MAD Implementation) completion
