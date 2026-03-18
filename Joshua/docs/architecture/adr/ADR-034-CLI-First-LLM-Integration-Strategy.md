# ADR-034: CLI-First LLM Integration Strategy

**Status:** Accepted
**Date:** 2025-12-21
**Deciders:** System Architect
**Supersedes:** Portions of ADR-031 (implementation approach)

---

## 📝 Integration with ADR-037 (2025-12-22)

This ADR's principles remain valid and are **complementary** to ADR-037 (LangFlow Node Sourcing Strategy):

**LangFlow Native (ADR-037):**
- Use LangFlow's native Language Model component for basic LLM API access
- Use LangFlow's standard components wherever available

**CLI Wrappers (This ADR):**
- Build custom nodes to wrap provider CLIs for accessing provider-specific innovations
- Providers (Anthropic, Google, OpenAI, xAI) continuously optimize their CLIs for their specific models
- Their native implementations (compression, session management, context handling) are optimized for their architectures in ways we cannot match
- Wrapping CLIs gives us automatic access to provider innovation and competition

**Combined Strategy:**
- Basic LLM calls → LangFlow native Language Model component
- Provider-specific optimizations → Custom CLI wrapper nodes (built via wrap/fork/extend as needed)
- Focus Joshua development on unique multi-MAD orchestration capabilities

---

---

## 🔄 CRITICAL ARCHITECTURAL PIVOT (2025-12-21)

**This ADR represents a fundamental shift in Fiedler's role:**

**Before (ADR-008, ADR-009):**
- Fiedler was an **LLM execution gateway/proxy**
- MADs called `fiedler_send` to execute LLM requests
- Fiedler routed calls and returned responses

**After (ADR-034 + ADR-035):**
- MADs use `joshua_ai_access` nodes to access LLMs **directly**
- Fiedler is an **orchestrator/advisor** only (recommendations, MMI)
- Direct access eliminates proxy bottleneck

**Key Change:** The `joshua_ai_access` shared library (described below) enables **direct access**, completely bypassing Fiedler for LLM execution. See ADR-035 for complete execution pattern and ADR-036 for node library architecture.

---

## Context and Problem Statement

ADR-030, ADR-031, and ADR-032 established a flow-based architecture with modular PCP component libraries providing custom Langflow nodes. The design documents for `joshua_imperator` specified 12 custom nodes including ChatSessionNode, PlanNode, CritiqueNode, and others—each implementing sophisticated capabilities like:

- Session management across multi-turn conversations
- Context window management and compression
- Agentic multi-step reasoning loops
- Vision and multimodal support
- File system operations and git integration
- Tool calling and workflow automation

However, implementing these features from scratch would require:

1. **Duplicating existing capabilities**: Major LLM providers (Anthropic, Google, OpenAI, xAI) already provide battle-tested CLI tools with these exact features
2. **Ongoing maintenance burden**: Each CLI continuously improves as providers compete for market share
3. **Playing perpetual catch-up**: New features are added monthly; custom implementations would always lag behind
4. **Resource misallocation**: Development effort spent on LLM plumbing instead of unique Joshua capabilities

The fundamental question: Should Joshua reimplement what LLM providers already do better, or should it focus on its unique value proposition (multi-MAD orchestration and distributed cognition)?

---

## Decision

Joshua will adopt a **CLI-First Integration Strategy** where custom Langflow nodes wrap existing LLM provider CLI tools to leverage provider-specific optimizations, rather than reimplementing their capabilities from scratch.

### Core Principles

**1. Wrap, Don't Reimplement**

Custom nodes wrap provider CLIs to expose their full feature sets through standard Langflow node interfaces. This leverages provider-specific optimizations rather than attempting to replicate them.

**2. Provider CLIs Deliver Model-Specific Optimizations**

Providers continuously innovate on their CLIs with features optimized for their specific model architectures. We delegate the following capabilities to provider CLIs because their native implementations outperform any generic replication:
- Session management (`--resume <session_id>`)
- Context compression/compaction (`/compact`, `/compress`)
- Agentic multi-step loops (ReAct patterns, tool orchestration)
- Vision and multimodal handling (image/PDF/video processing)
- File system operations (`@file.md`, `--include-all-files`)
- Git integration (automatic commits, branch management)
- Project context awareness (folder-based context loading)
- Model-specific optimizations (prompt caching, token management)

**3. Joshua Focuses on Unique Value**

Joshua's development resources focus on capabilities no LLM provider offers:
- Multi-MAD communication and orchestration
- Distributed Progressive Cognitive Pipeline across specialized MADs
- MAD role specialization and expertise domains
- Cross-MAD workflows and data passing
- Ecosystem-level knowledge sharing
- Novel cognitive architectures (PCP tiers, reflection systems)

**4. Flows Orchestrate CLI Sessions**

Flows use `joshua_ai_access` nodes directly to orchestrate CLI sessions. Flows remain simple, delegating complexity to battle-tested CLIs.

**5. Competitive Innovation Leverage**

By wrapping CLIs, Joshua automatically benefits from provider competition and innovation:
- Anthropic improves Claude Code's compression algorithm → All MADs benefit immediately
- Google optimizes Gemini CLI's context handling for their models → Available next day
- OpenAI enhances ChatGPT CLI's session management → Propagates instantly
- Aider community fixes bugs → Ecosystem gains improvements automatically
- Zero development effort required to stay current with provider optimizations

**6. LangFlow Native + CLI Wrappers**

MADs use LangFlow's native Language Model component for basic LLM API access, and custom CLI wrapper nodes when provider-specific optimizations are needed. Custom nodes are built via wrap/fork/extend approaches as determined during implementation. Fiedler's role is **orchestrator** (maintaining the Master Model Index, recommending models, allocating GPU resources), not **executor**.

---

## Architecture

### The `joshua_ai_access` Shared Library

A shared Python library providing Langflow-compatible nodes for direct AI model access via provider CLIs.

#### Node Catalog

**Text Generation Nodes:**
- `ClaudeSessionNode` - Wraps Claude Code CLI for Anthropic models
- `GeminiSessionNode` - Wraps Gemini CLI for Google models
- `AiderSessionNode` - Wraps Aider CLI for model-agnostic code editing
- `GrokSessionNode` - Wraps Grok CLI for xAI models with real-time data
- `CodexSessionNode` - Wraps OpenAI Codex CLI for GPT-4/5 and o-series models

**Local Model Nodes:**
- `SutherlandLLMNode` - Local LLM inference via Sutherland (Ollama backend)

**Future Expansion:**
- Image generation, speech-to-text, embeddings, vision models (see ADR-035)

---

### 1. ClaudeSessionNode

Wraps Claude Code CLI for Anthropic models.

#### Node Configuration

**Parameters:**
- `message` (str, required): User prompt or instruction
- `session_id` (str, optional): Session identifier for conversation continuity
- `files` (List[str], optional): Files to include in context (e.g., `["@requirements.md", "@src/**"]`)
- `auto_compress` (bool, default=True): Automatically trigger `/compact` when context full
- `enable_tools` (bool, default=True): Allow Claude to use built-in tools (file edit, bash, etc.)
- `model` (str, default="sonnet"): Claude model variant (sonnet, opus, haiku)

**Returns:**
- `response` (str): Claude's response
- `session_id` (str): Session ID for future turns
- `tool_calls` (List[dict]): Tools Claude invoked (if any)
- `files_modified` (List[str]): Files edited during session
- `git_commit` (str, optional): Commit hash if changes were committed
- `compressed` (bool): Whether context was compressed this turn
- `tokens_used` (dict): Token usage details

**CLI Command Executed:**
```bash
claude --resume <session_id> --model <model> "<message>"
```

#### Node Implementation Sketch

```python
from langflow.custom import CustomComponent
from typing import Dict, Any, List
import subprocess
import os

class ClaudeSessionNode(CustomComponent):
    display_name = "Claude Session"
    description = "Multi-turn conversation with Claude via Claude Code CLI"
    category = "AI Models / Text Generation"

    async def build(
        self,
        message: str,
        session_id: str = "",
        files: List[str] = [],
        auto_compress: bool = True,
        enable_tools: bool = True,
        model: str = "sonnet",
    ) -> Dict[str, Any]:
        """Execute Claude Code CLI directly."""

        # Fetch API key from Turing (or env initially)
        api_key = await self._get_api_key("ANTHROPIC_API_KEY")

        # Build CLI command
        cmd = ["claude"]
        if session_id:
            cmd.extend(["--resume", session_id])
        cmd.extend(["--model", model])
        if not enable_tools:
            cmd.append("--no-tools")
        for file in files:
            cmd.extend(["--file", file])
        cmd.append(message)

        # Execute
        env = os.environ.copy()
        env["ANTHROPIC_API_KEY"] = api_key

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            env=env,
            timeout=120
        )

        if result.returncode != 0:
            raise ClaudeSessionError(f"CLI error: {result.stderr}")

        # Parse CLI output into structured response
        return self._parse_cli_output(result.stdout)

    async def _get_api_key(self, key_name: str) -> str:
        """Fetch API key from Turing or environment."""
        # Phase 1: Environment variables
        # Phase 2: mcp__turing__get_secret(key_name)
        return os.getenv(key_name)
```

---

### 2. GeminiSessionNode

Wraps Gemini CLI for Google models.

**Parameters:**
- `message` (str): User prompt or instruction
- `session_id` (str, optional): Session identifier
- `files` (List[str], optional): Files to include
- `compress_threshold` (float, default=0.7): Trigger compression at this % of context window
- `enable_web_search` (bool, default=False): Allow real-time web searches
- `model` (str, default="gemini-2.5-pro"): Gemini model variant

**Returns:**
- `response` (str): Gemini's response
- `session_id` (str): Session ID
- `web_results` (List[dict], optional): Web search results if used
- `compressed` (bool): Whether compression occurred
- `context_window_used` (float): Percentage of context window filled
- `tokens_used` (dict): Token usage details

**CLI Command:**
```bash
gemini --resume <session_id> --model <model> "<message>"
```

---

### 3. AiderSessionNode

Wraps Aider CLI for model-agnostic agentic code editing.

**Parameters:**
- `message` (str): Task description or instruction
- `session_id` (str, optional): Session identifier
- `model` (str, default="claude"): Model to use (claude, gpt-4, llama, grok, etc.)
- `architect_model` (str, optional): Separate model for planning (e.g., "gpt-o3" for thinking, "llama" for coding)
- `files` (List[str], optional): Files to edit
- `auto_commit` (bool, default=True): Automatically commit changes
- `auto_test` (bool, default=False): Run tests after changes

**Returns:**
- `response` (str): Aider's summary
- `session_id` (str): Session ID
- `files_modified` (List[str]): Files that were edited
- `git_commits` (List[str]): Commit hashes created
- `test_results` (dict, optional): Test output if auto_test enabled
- `repo_map_tokens` (int): Tokens used for repository context map

**CLI Command:**
```bash
aider --model <model> --architect-model <architect> --message "<message>" --yes
```

**Special Feature:** Aider provides model-agnostic interface - can use ANY provider's models (Claude, GPT, Llama, Grok, etc.) for code editing tasks.

---

### 4. GrokSessionNode

Wraps Grok CLI for xAI models with real-time data access.

**Parameters:**
- `message` (str): User prompt
- `session_id` (str, optional): Session identifier
- `enable_x_search` (bool, default=True): Search X (Twitter) for real-time info
- `enable_web_search` (bool, default=True): Search broader web
- `model` (str, default="grok-4"): Grok model variant

**Returns:**
- `response` (str): Grok's response
- `session_id` (str): Session ID
- `x_posts` (List[dict], optional): Relevant X posts found
- `web_results` (List[dict], optional): Web search results
- `real_time_data` (bool): Whether real-time data was used
- `tokens_used` (dict): Token usage details

**CLI Command:**
```bash
grok --resume <session_id> --model <model> "<message>"
```

**Unique Capability:** Real-time access to X (Twitter) data and broader web for current events.

---

### 5. CodexSessionNode

Wraps OpenAI Codex CLI for GPT-4/5 and o-series reasoning models.

**Parameters:**
- `message` (str): User prompt
- `session_id` (str, optional): Session identifier
- `files` (List[str], optional): Files to include
- `model` (str, default="gpt-5"): OpenAI model (gpt-5, o3, o3-mini)
- `enable_thinking` (bool, default=False): Use extended reasoning mode (o3 models)
- `thinking_budget` (int, optional): Reasoning token budget for o3 models

**Returns:**
- `response` (str): Model's response
- `session_id` (str): Session ID
- `thinking_trace` (str, optional): Chain-of-thought if thinking enabled
- `reasoning_tokens` (int, optional): Tokens used for reasoning (o3 models)
- `files_modified` (List[str]): Files edited
- `tokens_used` (dict): Token usage details

**CLI Command:**
```bash
codex resume <session_id> --model <model> "<message>"
```

**Unique Capability:** Extended reasoning mode for o3 models with configurable thinking budgets.

---

### MAD Usage Pattern

MADs import nodes from `joshua_ai_access` and use them directly in Langflow flows:

```python
# In a MAD's flow definition (Python API)

from joshua_ai_access import ClaudeSessionNode

# Create node instance
claude_node = ClaudeSessionNode()

# Use in flow logic
response = await claude_node.build(
    message=user_prompt,
    session_id=conversation_id,  # Persists across turns
    files=["@config/persona.md"],
    auto_compress=True,  # Claude Code manages context
    enable_tools=True,  # Allow file editing, etc.
    model="sonnet"
)

# Claude Code CLI handles:
# - Loading session history from disk
# - Managing context window (auto-compress when full)
# - File ingestion and processing
# - Tool calling (file edits, bash commands)
# - Git commits for code changes
# - Session state persistence
```

### Flow Orchestration Example

```json
{
  "name": "chatbot_session_flow",
  "description": "Multi-turn chatbot using Claude Code session management",
  "nodes": [
    {
      "id": "claude_chat",
      "type": "ClaudeSessionNode",
      "inputs": {
        "message": "{{input.user_message}}",
        "session_id": "{{input.session_id}}",
        "files": ["@config/persona.md", "@config/instructions.md"],
        "auto_compress": true,
        "enable_tools": true,
        "model": "sonnet"
      }
    }
  ],
  "edges": [],
  "output": {
    "response": "{{claude_chat.response}}",
    "session_id": "{{claude_chat.session_id}}",
    "modified_files": "{{claude_chat.files_modified}}"
  }
}
```

**Compare to original design** (would require building ChatSessionNode, SessionManager, ContextWindowManager, etc. from scratch):
```json
{
  "name": "complex_chatbot_flow",
  "nodes": [
    {"id": "session_mgr", "type": "SessionManager"},  // WOULD NEED TO BUILD
    {"id": "context_mgr", "type": "ContextWindowManager"},  // WOULD NEED TO BUILD
    {"id": "chat_node", "type": "ChatSessionNode"}  // WOULD NEED TO BUILD
  ]
}
```

**With CLI-first approach:** All of the above is provided by Claude Code CLI - zero implementation needed.

---

### Fiedler's Role: Orchestrator, Not Executor

As defined in **ADR-035**, Fiedler does NOT execute AI model calls on behalf of MADs. Instead:

**What Fiedler Does:**
- Maintains **Master Model Index (MMI)** - single source of truth for all AI model availability
- Provides **model recommendations** - `mcp__fiedler__recommend_model(task, constraints)` analyzes MMI and recommends best node/model for a task
- Orchestrates **GPU resource allocation** - `mcp__fiedler__request_gpu_resources()` manages VRAM for competing workloads
- Manages **dynamic configuration** - polls provider APIs, detects new models, auto-generates PRs for `joshua_ai_access` updates

**What Fiedler Does NOT Do:**
- Execute AI model calls (MADs use `joshua_ai_access` nodes directly)
- Proxy requests (no bottleneck in critical path)
- Manage API keys (nodes fetch from Turing or environment)

**Example Fiedler Consultation:**
```python
# MAD asks Fiedler which model to use
recommendation = await communicator.call_tool(
    "mcp__fiedler__recommend_model",
    {
        "task_description": "multi-turn code review chatbot",
        "constraints": {"cost": "medium", "latency": "low", "quality": "high"}
    }
)

# Fiedler responds with recommendation (queries MMI, reasons about constraints)
# {
#   "recommended_node": "ClaudeSessionNode",
#   "model_id": "claude-sonnet-4.5",
#   "confidence": 0.95,
#   "reasoning": "Claude Sonnet 4.5 excels at code review..."
# }

# MAD uses recommended node directly
from joshua_ai_access import ClaudeSessionNode
claude_node = ClaudeSessionNode()
response = await claude_node.build(message=user_prompt, model="sonnet")
```

**See ADR-035 for complete Fiedler orchestrator architecture.**

---

## Consequences

### Positive

**Immediate Capability Access:**
- MADs gain production-ready session management, compression, vision, agentic loops immediately
- No months-long development cycle for basic features
- All features are battle-tested by thousands of users

**Zero Maintenance Burden:**
- CLI improvements automatically benefit all MADs
- Bug fixes propagate instantly
- New features available without code changes to `joshua_ai_access` nodes

**Competitive Innovation Leverage:**
- Anthropic, Google, OpenAI, xAI compete to improve their CLIs
- Joshua benefits from billions in R&D investment
- Always have cutting-edge LLM capabilities

**Resource Allocation:**
- Development focuses on unique Joshua value:
  - Multi-MAD orchestration
  - Distributed PCP architecture
  - Cross-MAD workflows
  - Novel cognitive patterns
- Not spent reimplementing what providers do better

**Model Diversity:**
- Aider provides model-agnostic interface
- Easy to compare Claude vs. Gemini vs. GPT for same task
- Can use different models for different reasoning stages (architect vs. editor)

**Vision/Multimodal Support:**
- CLIs handle model-specific image formatting
- Avoids LiteLLM fragility issues
- Native support for PDFs, videos, screenshots

**Real-Time Data:**
- Grok CLI provides access to live X and web data
- Gemini CLI can search web in real-time
- No need to build custom web search integration

**Architectural Purity:**
- Nodes are composable, reusable Langflow components
- MADs use nodes directly (no proxy bottleneck)
- Follows flow-based architecture principles (ADR-032)

**No Single Point of Failure:**
- Fiedler crash does not block AI access
- MADs continue using nodes directly
- Only orchestration temporarily unavailable (see ADR-035)

### Negative

**External Dependency:**
- Relies on CLI tools maintained by third parties
- CLI interface changes could break nodes
- Mitigation: Version pinning, wrapper abstraction layer

**Less Granular Control:**
- Can't customize every aspect of LLM interaction
- CLI tool decides compression algorithm, tool calling logic
- Mitigation: Most MADs don't need granular control; CLIs are highly configurable

**Subprocess Overhead:**
- Launching CLI processes has ~50-200ms latency vs. direct API
- Mitigation: Session reuse minimizes overhead; latency acceptable for chatbot use cases

**CLI Availability:**
- Requires CLIs installed in MAD containers (or shared volume)
- Mitigation: Standard installation in Dockerfile or mounted `/usr/local/bin`

**Multiple CLI Interfaces:**
- Each provider has slightly different CLI syntax
- Mitigation: Node abstraction normalizes interfaces for flow authors

### Neutral

**Design Documents Still Valuable:**
- joshua_imperator requirements/design documents become specifications
- Define what `joshua_ai_access` nodes must provide
- Serve as fallback plan if custom nodes needed later

**Custom Nodes Not Ruled Out:**
- If CLI capabilities insufficient, can still build custom nodes
- Likely rare; CLIs cover 95%+ of use cases

---

## Implementation

### Phase 1: joshua_ai_access Library Foundation (Weeks 1-2)

**Timeline:** 1-2 weeks

1. **Create Library Structure:**
   - Repository: `joshua_ai_access`
   - Package structure: `joshua_ai_access/nodes/`
   - Setup: Poetry for dependency management
   - Base class: `BaseAINode` extending Langflow `CustomComponent`

2. **Implement Core Nodes:**
   - `ClaudeSessionNode` (priority 1)
   - `AiderSessionNode` (priority 2)
   - `GeminiSessionNode` (priority 3)

3. **API Key Management:**
   - Phase 1: Read from environment variables
   - Utility: `get_api_key(key_name)` helper
   - Documentation: How to set env vars in MAD containers

4. **CLI Output Parsing:**
   - Standardized response schema across all nodes
   - Error handling for CLI failures
   - Session ID extraction from CLI output

5. **Testing:**
   - Unit tests for each node (mock CLI execution)
   - Integration tests with actual CLIs (require API keys)
   - Example flows demonstrating usage

6. **Documentation:**
   - Node usage guide for MAD developers
   - CLI installation instructions
   - Troubleshooting common CLI errors

### Phase 2: Expansion and Integration (Weeks 3-4)

7. **Add Remaining Nodes:**
   - `GrokSessionNode`
   - `CodexSessionNode`
   - `SutherlandLLMNode` (for local models via Sutherland)

8. **Turing Integration:**
   - Update `get_api_key()` to call `mcp__turing__get_secret()`
   - Migrate from env vars to runtime key fetching
   - Security: Never store keys in code or version control

9. **Performance Optimization:**
   - Connection pooling for CLI sessions
   - Caching for frequently-used session state
   - Async execution for parallel node usage

10. **MAD Migration:**
    - Update Template MAD to use `joshua_ai_access` nodes
    - Example flows: chatbot, code review, multi-step reasoning
    - Migration guide for existing MADs

### Phase 3: Advanced Features (Weeks 5-6)

11. **Health Reporting:**
    - Nodes report performance to Fiedler MMI
    - Track: response time, error rate, token costs
    - Automatic degradation detection

12. **Failover Strategies:**
    - Nodes implement fallback logic (e.g., Claude → Gemini → local Ollama)
    - Configurable per node instance
    - Logged for observability

13. **Node Catalog Expansion:**
    - Vision nodes (ClaudeVisionNode, GPT4VisionNode)
    - Image generation (StableDiffusionNode, DallE3Node)
    - Speech nodes (WhisperNode, ElevenLabsNode)
    - Embedding nodes (SentenceTransformerNode, VoyageAINode)

14. **Documentation:**
    - Comprehensive node reference
    - Cookbook: Common flow patterns
    - Best practices: When to use which node

15. **Testing:**
    - End-to-end workflow tests
    - Load testing (concurrent node usage)
    - Failover scenario validation

---

## Relationship to Other ADRs

**ADR-029 (Ollama Failover):**
- Still valid: Local failover for when external providers unavailable
- Nodes can implement degradation to Sutherland's local Ollama
- CLI tools can be configured to use local models

**ADR-030 (Langflow Architecture):**
- Still valid: Nodes must be Langflow-compatible `CustomComponent` classes
- Flows orchestrate logic by composing nodes
- Hopper designs flows visually in Langflow UI

**ADR-031 (Modular PCP Components):**
- **Partially superseded**: Implementation approach changes
- `joshua_imperator` library may not be built (or built much later)
- PCP components may be CLI orchestration patterns, not custom reasoning nodes
- Document remains valid as requirements specification

**ADR-032 (Flow-Based Architecture):**
- Fully valid: Flows define reasoning logic
- Flows compose `joshua_ai_access` nodes directly
- Distributed decision-making maintained (flows choose which node, when to call)

**ADR-035 (Direct Access AI Model Nodes):**
- **Complements this ADR**: Defines execution pattern (direct access)
- This ADR defines CLI-first philosophy and node capabilities
- ADR-035 defines Fiedler orchestrator role and Sutherland integration
- Together: Complete AI access architecture

---

## Migration Impact

### Existing Documents

**joshua_imperator_library_requirements.md:**
- **Status:** Specification document
- **New role:** Defines requirements for `joshua_ai_access` node capabilities
- **Update:** Add implementation note explaining CLI-first approach

**joshua_imperator_library_design.md:**
- **Status:** Design reference
- **New role:** Capability map for what MADs should achieve
- **Update:** Add mapping from designed nodes to `joshua_ai_access` CLI nodes

**MAD_Template_V0.7_Requirements.md:**
- **Status:** Update needed
- **Changes:** Replace custom node references with `joshua_ai_access` node usage

**MAD_Template_V0.7_Design.md:**
- **Status:** Update needed
- **Changes:** Show CLI session node usage instead of custom ChatSessionNode implementation

### Code Impact

**Minimal:** Most code hasn't been written yet. This decision prevents months of wasted implementation effort.

**joshua_ai_access:** New library (not refactoring)

**MADs:** No impact; they'll use `joshua_ai_access` nodes from the start

**Fiedler:** Focus on orchestration (MMI, recommendations, GPU allocation) not execution proxy (see ADR-035)

---

## Success Criteria

This decision will be considered successful when:

1. **joshua_ai_access library published** with at least 3 core nodes (Claude, Aider, Gemini)
2. **Template MAD demonstrates multi-turn chatbot** using `ClaudeSessionNode`
3. **Context compression works automatically** without custom code
4. **Vision/multimodal support works** via CLI native handlers
5. **Development effort shifts** from LLM plumbing to multi-MAD orchestration
6. **MADs stay current** with latest CLI features without code changes
7. **Nodes are composable** - multiple nodes can be used in single flow
8. **No bottleneck** - Fiedler crash doesn't block AI access (direct node usage)

---

## Alternatives Considered

### Alternative 1: Build Custom Nodes (Original Plan)

**Pros:**
- Full control over implementation
- No external dependencies
- Could be optimized for Joshua-specific use cases

**Cons:**
- Months of development time
- Perpetual maintenance burden
- Always behind provider CLIs in features
- Duplicates what providers do better
- Wastes development resources

**Rejected because:** Development resources better spent on unique Joshua capabilities.

### Alternative 2: Direct API Integration (No CLIs)

**Pros:**
- Slightly faster (no subprocess overhead)
- More direct control

**Cons:**
- Loses all CLI features (session management, compression, tools, git)
- Have to reimplement all those features ourselves
- No agentic capabilities
- No file operations, git integration

**Rejected because:** CLI features too valuable to lose.

### Alternative 3: Fiedler as Execution Proxy (Original ADR-034)

**Pros:**
- Centralized LLM access management
- Single place to monitor all AI calls

**Cons:**
- Single point of failure (Fiedler crash = no AI access)
- Performance bottleneck (all requests serialized)
- Violates architectural purity (nodes should be direct)
- Tight coupling (MADs depend on Fiedler for basic operations)

**Rejected because:** Creates unnecessary bottleneck and single point of failure. See ADR-035 for direct access architecture.

### Alternative 4: Hybrid (CLI for Some, Custom for Others)

**Pros:**
- Could optimize specific use cases

**Cons:**
- Complexity of managing two systems
- Unclear which approach for which use case
- Still have maintenance burden for custom nodes

**Rejected because:** YAGNI - build custom nodes only when proven necessary.

---

## References

- **Discussion Transcript:** Gemini/Claude conversation on CLI feature comparison and architectural implications
- **Claude Code Documentation:** https://docs.anthropic.com/claude-code
- **Gemini CLI Documentation:** https://ai.google.dev/gemini-api/docs/cli
- **Aider Documentation:** https://aider.chat/
- **Grok CLI Documentation:** https://docs.x.ai/grok-cli
- **OpenAI Codex Documentation:** https://platform.openai.com/docs/guides/codex
- **ADR-035:** Direct Access AI Model Nodes with Fiedler as Ecosystem Orchestrator

---
