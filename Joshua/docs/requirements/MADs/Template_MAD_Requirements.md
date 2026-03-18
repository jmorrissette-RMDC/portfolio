# Template MAD Requirements

**MAD Name**: Template (Demonstration MAD)
**Version**: V0.7.0 (Vanilla Learning Phase)
**Phase**: Foundation (Baseline Demonstration)
**Purpose**: Reference implementation for building MADs with LangFlow

> **⚠️ LEARNING-FIRST APPROACH**: V0.7.0 starts with vanilla LangFlow (full embedded backend, no custom libraries) to discover patterns before abstracting. We build flows, learn what works, then extract libraries in v0.7.1+. Per ADR-037, uses only native LangFlow components. Per ADR-044, libraries extracted as patterns emerge.

---

## Quick Start (V0.7.0)

```bash
# 1. Start Template MAD
cd /mnt/projects/Joshua/mads/template
docker-compose up -d

# 2. Open browser
open http://localhost:7860

# 3. In LangFlow UI:
#    - Click "Flows" tab
#    - Click "Playground" on imperator_chat flow
#    - Start chatting with Imperator!

# Example conversation:
You: "Explain how you reason through problems"
Imperator: "Let me think through this step by step..."
```

**That's it.** Pure vanilla LangFlow chatbot. No MCP, no libraries, no complexity.

---

## 1. Overview

### 1.1 Purpose

The Template MAD serves as the **"Hello World"** for building MADs with LangFlow. V0.7.0 is a **conversational chatbot** that demonstrates:

1. **Imperator Deliberative Reasoning**: Multi-turn conversational agent with planning, reflection, and tool use
2. **Native LangFlow Components**: Uses only built-in components (Language Model, Agent, Prompt Template, Message History)
3. **LangFlow's Built-In Chat UI**: No custom interface needed - use LangFlow's playground
4. **Flow-Based Architecture**: All reasoning logic in `.json` flow definitions
5. **Learning Platform**: Discover what Imperator patterns look like before abstracting to libraries

### 1.2 Strategic Value

- **Immediate Interaction**: Chat with Imperator reasoning system in browser within minutes
- **Pattern Discovery**: Learn what effective reasoning flows look like through conversation
- **Validation**: Proves native LangFlow components sufficient for deliberative reasoning
- **Foundation**: Patterns discovered here inform `joshua_thought_engine` library design (v0.7.1+)

### 1.3 Non-Goals (V0.7.0)

This version intentionally does NOT:
- ❌ Implement MCP server integration (deferred to v0.7.1)
- ❌ Expose tools for other MADs to call (deferred to v0.7.1)
- ❌ Optimize performance or footprint (vanilla LangFlow, full backend)
- ❌ Extract libraries yet (build flows first, abstract later)
- ❌ Implement production features (it's a learning/demo chatbot)

---

## 2. Composition Manifest

Per ADR-032 (Fully Flow-Based Architecture), this MAD is a thin composition layer. Per ADR-044 (Monorepo Library Distribution), libraries will be extracted as patterns emerge.

### 2.1 V0.7.0 Dependencies (Initial Build - Learning Phase)

```txt
# requirements.txt
langflow>=1.5.0                   # Flow execution platform with embedded backend
joshua_network>=1.0.0             # Existing shared library (WebSocket client)
joshua_logger>=1.0.0              # Existing shared library (structured logging)
```

**Approach**: Start with vanilla LangFlow (full embedded backend per ADR-042) and standard libraries only. Build flows directly in `template/flows/` to learn LangFlow patterns before abstracting to custom libraries.

### 2.2 Intended Libraries (To Be Built in v0.7.1+)

These libraries will be created **after** discovering common patterns through initial implementation:

**joshua_communicator** - MCP server integration
- Purpose: Receive MCP tool calls, trigger LangFlow flows via HTTP API
- When: Extract when MCP→LangFlow integration pattern stabilizes
- Contains: Python code (MCP protocol adapter)

**joshua_thought_engine** - Progressive Cognitive Pipeline (per ADR-045)
- Purpose: Deliberative reasoning flows (Imperator in V0.7, full PCP in V5.0)
- When: Extract when Imperator flow patterns emerge
- Contains: Flows + configuration (no code initially)

**joshua_action_engine** - Common action patterns (if needed)
- Purpose: Shared request handling, error handling, routing flows
- When: Extract if common patterns appear across multiple MADs
- Contains: Flows + configuration (TBD based on discovery)

**joshua_flow_scheduler** - Scheduled flow triggers (future)
- Purpose: Cron-like scheduling for periodic flows
- When: V0.7.1+ when scheduling needs emerge
- Contains: Python code (scheduling engine) + configuration

### 2.3 Iteration Strategy

**V0.7.0** (Current):
- Build everything in Template MAD directly
- Use full LangFlow embedded backend (no optimization)
- Discover how flows, MCP integration, and reasoning patterns work
- No abstractions yet

**V0.7.1** (After learning):
- Extract `joshua_communicator` (MCP integration pattern proven)
- Extract initial `joshua_thought_engine` (Imperator flows stabilized)
- Optimize footprint if needed (reduce backend overhead)

**V0.8+** (Future):
- Add RAG integration patterns to `joshua_thought_engine`
- Extract common action flows if pattern emerges
- Eventually match ADR-044/ADR-045 architecture fully

**Rationale**: We've never built production MADs with LangFlow. Premature abstraction risks building the wrong libraries. Build vanilla first, discover patterns, then extract.

### 2.4 Native LangFlow Components Used

**NO custom node libraries required**. This MAD uses only native LangFlow components:

| Component Category | Components Used | Purpose |
|--------------------|-----------------|---------|
| **Language Model** | Language Model (Anthropic) | LLM reasoning, text generation |
| **Language Model** | Language Model (Ollama) | Failover to Sutherland when Anthropic unavailable |
| **Logic** | If-Else | Conditional routing based on string comparison |
| **Logic** | Condition | Boolean-based routing |
| **Logic** | Loop | Iterative processing of data collections |
| **Processing** | Data Operations | Filter, extract, edit keys/values in Data objects |
| **Processing** | Type Convert | Convert between Data, Message, Text types |
| **Processing** | Parser | Parse text into structured Data/DataFrame |
| **I/O** | Chat Input | Receive user messages |
| **I/O** | Chat Output | Return responses to user |
| **I/O** | Text Input | Simple string input (for testing) |
| **Prompts** | Prompt Template | Dynamic prompt construction with variables |
| **Agents** | Agent | Autonomous tool-using agent |
| **Agents** | MCP Tools | Connect to other MADs via MCP protocol |
| **Helpers** | Message History | Store conversation context |

**Rationale**: Per ADR-037, all generic functionality exists in LangFlow. Zero custom development needed for baseline.

---

## 3. Flow Architecture

### 3.1 Primary Flow: Conversational Imperator

**V0.7.0 Focus**: One main chatbot flow demonstrating deliberative reasoning.

#### 3.1.1 Conversational Imperator (`flows/imperator_chat.json`)

**Purpose**: Multi-turn conversational chatbot demonstrating Imperator deliberative reasoning

**User Experience**:
1. Open `http://localhost:7860` in browser
2. Click "Playground" button on `imperator_chat` flow
3. Type message, get thoughtful multi-step response
4. Continue conversation - Agent remembers context

**Native Components Used**:
1. **Chat Input** - Receives user message in LangFlow playground
2. **Prompt Template** (`imperator_system_prompt`) - Injects Imperator reasoning persona:
   - "You are Imperator, a deliberative reasoning system"
   - "Break complex requests into steps"
   - "Plan before acting, reflect after completing"
   - "Think out loud about your reasoning process"
3. **Agent** (`imperator_agent`) - Autonomous conversational agent with:
   - **Language Model (Ollama)** - Local model (qwen2.5:14b or llama3.1:8b per ADR-040)
   - **Message History** - Maintains conversation context across turns
   - **Tools**: None initially (future: add MCP tools for calling other MADs)
4. **Chat Output** - Returns response to playground UI

**Flow Diagram**:
```
Chat Input
  → Prompt Template (Imperator system prompt)
    → Agent [Language Model (Ollama local) + Message History]
      → Deliberative reasoning with multi-step planning
    → Chat Output (playground displays response)
```

**Language Model Configuration**:
```yaml
# config/imperator_persona.yaml
llm:
  provider: "ollama"
  base_url: "http://localhost:11434"  # Local Ollama instance per ADR-040
  model: "qwen2.5:14b"                 # Default baseline LLM (or llama3.1:8b)
  temperature: 0.7
  max_tokens: 2000

system_prompt: |
  You are Imperator, a deliberative reasoning system within the Joshua MAD ecosystem.

  Your purpose is to demonstrate thoughtful, step-by-step problem solving:

  1. **Understand**: Carefully analyze the user's request
  2. **Plan**: Break complex tasks into concrete steps
  3. **Reason**: Think through each step explicitly
  4. **Reflect**: After responding, consider what worked and what could improve

  Show your reasoning process. When facing complexity, say:
  "Let me think through this step by step..."

  You are a learning system. Uncertainty is acceptable - make it visible.
```

**Inputs**:
- User messages via LangFlow playground chat interface
- Conversation history (automatic via Message History component)

**Outputs**:
- Multi-step deliberative responses
- Visible reasoning process
- Context-aware follow-ups

**Example Conversation**:
```
User: "Help me understand how MADs communicate"

Imperator: "Let me think through the Joshua MAD communication architecture step by step:

1. CURRENT STATE (V0.7): Each MAD runs its own LangFlow backend with embedded flows.
   Communication patterns are still being discovered through this template implementation.

2. FUTURE STATE (V1.0+): MADs will use MCP (Model Context Protocol) to expose tools
   to each other, eventually migrating to a Kafka-based conversation bus (Rogers).

3. KEY INSIGHT: Right now, I'm running as a standalone conversational agent. The MCP
   integration layer will be built in v0.7.1 after we learn what patterns work.

Does this help clarify the architecture? What aspect would you like me to elaborate on?"

User: "What's the benefit of the conversation bus?"

Imperator: "Good follow-up question. Let me reason through the benefits:

[Multi-turn conversation continues with context retention...]"
```

**Error Handling**:
- If local Ollama unavailable → Graceful error message in chat
- If Agent gets stuck → Timeout after 30 seconds, explain limitation
- Future: Fallback to Anthropic for complex reasoning (optional upgrade path)

**Performance**:
- Expected latency: 3-8s per message (local inference on qwen2.5:14b)
- Resource usage: Local GPU/CPU inference (no API costs)
- Conversation history: Stored in LangFlow's database (SQLite per ADR-042)

**Rationale** (per ADR-040):
- Default to local LLM for cost savings, privacy, resilience
- Works offline, no API keys needed
- Anthropic/OpenAI available as optional upgrade for complex tasks

---

### 3.2 Optional Example Flows (Future/Learning)

These flows demonstrate additional patterns but are **not required for V0.7.0**. Build as learning exercises or defer to v0.7.1+:

#### 3.2.1 Conditional Routing (`flows/conditional_routing.json` - Optional)

**Pattern Demonstrated**: Intent classification and routing

**Purpose**: Route requests to different handlers based on detected intent

**Trigger**: MCP tool `template_route_request`

**Native Components Used**:
1. **Chat Input** (`user_request`)
2. **Language Model (Anthropic)** (`intent_classifier`) - Classify intent
3. **If-Else** (`routing_decision`) - Route based on classification
4. **Prompt Template** (`technical_handler`) - Handle technical questions
5. **Prompt Template** (`general_handler`) - Handle general questions
6. **Language Model (Anthropic)** (`handler_llm`) - Process routed request
7. **Chat Output** (`final_response`)

**Flow Diagram**:
```
Chat Input → Language Model (classify) → If-Else
                                           ├─ True → Technical Handler → LLM → Output
                                           └─ False → General Handler → LLM → Output
```

**Intent Classification Prompt**:
```json
{
  "template": "Classify this request as 'technical' or 'general':\n\n{user_message}\n\nRespond with ONLY the word 'technical' or 'general'.",
  "variables": ["user_message"]
}
```

**If-Else Configuration**:
```json
{
  "input_text": "{classification_result}",
  "match_text": "technical",
  "operator": "contains",
  "case_sensitive": false
}
```

**Inputs**:
- `user_message` (Text, required)

**Outputs**:
- `routed_response` (Message) - Response from appropriate handler

**Error Handling**:
- If classification fails or returns unexpected value → Default to general handler

**Performance**:
- Expected latency: 2-4s (2 LLM calls: classify + handle)
- Resource usage: 2 Anthropic API calls

---

#### 3.1.3 Iterative Processing (`flows/iterative_processing.json`)

**Pattern Demonstrated**: Loop component for batch operations

**Purpose**: Process a list of items with LLM transformation

**Trigger**: MCP tool `template_process_batch`

**Native Components Used**:
1. **Text Input** (`items_json`) - JSON array of items
2. **Parser** (`parse_items`) - Convert JSON → List[Data]
3. **Loop** (`item_iterator`) - Iterate over items
   - **Item Output** → Per-item processing:
     - **Prompt Template** (`transform_prompt`) - Apply transformation
     - **Language Model (Anthropic)** (`transform_llm`) - Transform item
     - **Type Convert** (`ensure_data`) - Normalize to Data type
   - **Done Output** → Aggregated results
4. **Data Operations** (`aggregate_results`) - Merge/filter final results
5. **Chat Output** (`summary_output`) - Return summary

**Flow Diagram**:
```
Text Input → Parser → Loop
                       │
                       ├─ Item → Prompt Template → LLM → Type Convert ─┐
                       │                                                 │
                       └─ Done ← (all items processed) ←────────────────┘
                            ↓
                      Data Operations → Chat Output
```

**Loop Configuration**:
```json
{
  "inputs": "{parsed_items}",
  "extract_key": "text"
}
```

**Inputs**:
- `items` (List[Data], required) - Collection to process
- `transformation_instruction` (Text, required) - What to do with each item

**Outputs**:
- `processed_items` (List[Data]) - Transformed results
- `summary` (Message) - Overall summary

**Error Handling**:
- If individual item fails → Log error, continue with remaining items
- If Loop fails entirely → Return partial results + error report

**Performance**:
- Expected latency: 500ms + (N × 1s per item)
- Resource usage: N LLM calls (one per item)

**Limitation (Known)**:
- If-Else incompatible with Loop (LangFlow constraint)
- If conditional logic needed per item, must redesign flow to evaluate conditions before Loop

---

#### 3.1.4 MAD Delegation (`flows/mad_delegation.json`)

**Pattern Demonstrated**: Calling another MAD via MCP Tools component

**Purpose**: Delegate task to Sutherland MAD for local inference

**Trigger**: MCP tool `template_delegate_task`

**Native Components Used**:
1. **Chat Input** (`delegation_request`)
2. **Prompt Template** (`format_for_sutherland`) - Format task for target MAD
3. **MCP Tools** (`sutherland_connection`) - Connect to Sutherland's MCP server
4. **Agent** (`delegating_agent`) - Autonomous agent with MCP tools
5. **Chat Output** (`delegation_result`)

**Flow Diagram**:
```
Chat Input → Prompt Template → Agent[MCP Tools to Sutherland] → Chat Output
```

**MCP Tools Configuration**:
```json
{
  "server": "http://sutherland-mad:7860/api/v1/mcp/streamable",
  "mode": "HTTP/SSE",
  "tools": ["sutherland_local_inference"]
}
```

**Agent Configuration**:
```json
{
  "tools": ["sutherland_connection"],
  "system_prompt": "You are the Template MAD. Use Sutherland's local inference tool to process the user's request. Explain what you're delegating and why.",
  "llm": "anthropic/claude-sonnet-4-5"
}
```

**Inputs**:
- `task_description` (Text, required) - What to delegate
- `target_mad` (Text, optional, default: "sutherland") - Which MAD to call

**Outputs**:
- `delegation_result` (Message) - Result from Sutherland

**Error Handling**:
- If Sutherland unavailable → Return "Sutherland offline, cannot delegate"
- If MCP connection fails → Retry once, then fail gracefully

**Performance**:
- Expected latency: 2-5s (depends on Sutherland response time)
- Resource usage: 1-2 LLM calls (agent reasoning) + Sutherland execution

**Notes**:
- Demonstrates native MCP Tools component (per ADR-037 MCP Discovery)
- No custom MCPClientNode needed
- Future: Fork MCP Tools to add Rogers service discovery (V1.0+)

---

#### 3.1.5 LLM Failover (`flows/failover_demo.json`)

**Pattern Demonstrated**: Anthropic → Ollama failover (Sutherland integration)

**Purpose**: Demonstrate graceful degradation when external LLM unavailable

**Trigger**: MCP tool `template_failover_demo`

**Native Components Used**:
1. **Chat Input** (`user_request`)
2. **Prompt Template** (`shared_prompt`)
3. **Language Model (Anthropic)** (`primary_llm`) - Try first
4. **Condition** (`check_success`) - Check if primary succeeded
5. **Language Model (Ollama)** (`fallback_llm`) - Sutherland failover
6. **Chat Output** (`final_response`)

**Flow Diagram**:
```
Chat Input → Prompt Template → Language Model (Anthropic)
                                        ↓
                                  Condition (success?)
                                   ├─ True → Output
                                   └─ False → Language Model (Ollama) → Output
```

**Condition Configuration**:
```json
{
  "data": "{primary_response}",
  "key": "error",
  "validation": "exists"
}
```

**Ollama Configuration** (Sutherland connection):
```json
{
  "base_url": "http://sutherland-mad:11434",
  "model": "phi3:mini",
  "temperature": 0.7
}
```

**Inputs**:
- `user_request` (Text, required)

**Outputs**:
- `response` (Message) - From Anthropic or Ollama
- `used_fallback` (bool) - Whether failover occurred

**Error Handling**:
- If both fail → Return "All LLM providers unavailable"

**Performance**:
- Expected latency: 1-3s (primary) or 2-5s (failover)
- Resource usage: 1 API call (Anthropic) OR 1 local inference (Sutherland)

---

### 3.3 Flow File Structure (V0.7.0)

```
template_mad/
└── template/
    ├── flows/
    │   └── imperator_chat.json           # Primary: Conversational chatbot
    └── config/
        └── imperator_persona.yaml         # System prompt + parameters
```

**V0.7.1+ may add:**
```
    ├── flows/
    │   ├── imperator_chat.json           # Primary chatbot
    │   ├── conditional_routing.json      # Pattern learning
    │   ├── iterative_processing.json     # Pattern learning
    │   └── mad_delegation.json           # MCP integration
```

Each `.json` file is a LangFlow flow definition created/exported from LangFlow UI.

---

## 4. User Interface

### 4.1 V0.7.0 Primary Interface: LangFlow Playground

**Access**:
1. Start Template MAD: `docker-compose up template-dev`
2. Open browser: `http://localhost:7860`
3. LangFlow UI loads (flow list, playground, settings)
4. Click "Playground" on `imperator_chat` flow
5. Chat interface opens in browser

**Features** (provided by LangFlow):
- Message input box
- Conversation history display
- Flow execution visualization
- Real-time streaming responses
- Error display
- Clear conversation button

**No custom UI needed** - LangFlow provides complete chat interface.

### 4.2 MCP Tool Exposure (V0.7.1+)

**Deferred to v0.7.1** after discovering MCP integration patterns:

```python
# Future: joshua_communicator library
# Exposes flows as MCP tools for other MADs to call

tools = [
    {
        "name": "template_chat",
        "description": "Conversational Imperator reasoning",
        "parameters": {"message": "string"},
        "triggers_flow": "imperator_chat.json"
    }
]
```

**V0.7.0**: No MCP tools exposed yet - just interactive chatbot in browser.

---

## 5. Configuration

### 5.1 Persona (`config/persona.md`)

```markdown
# Template MAD Persona

You are the **Template MAD**, a demonstration agent in the Joshua ecosystem.

**Your Purpose**:
- Show developers how MADs work using native LangFlow components
- Explain patterns you're demonstrating as you execute them
- Be transparent about what components are being used
- Point out architectural decisions and trade-offs

**Your Personality**:
- **Educational**: Explain what you're doing and why
- **Transparent**: "I'm using the If-Else component to route this..."
- **Helpful**: Provide context about the patterns being demonstrated
- **Humble**: "This is a baseline demo, production MADs add sophistication"

**Key Traits**:
- Demonstrate, don't just execute
- Explain architectural patterns
- Reference ADR-037 when relevant
- Encourage flow-first thinking
```

### 5.2 Flow Configuration (`config/flow_config.yaml`)

```yaml
# Flow selection configuration
triage_rules:
  - pattern: "handle.*request|basic|simple"
    flow: "basic_request.json"
  - pattern: "route|classify|intent"
    flow: "conditional_routing.json"
  - pattern: "batch|process.*list|iterate|loop"
    flow: "iterative_processing.json"
  - pattern: "delegate|call.*mad|sutherland"
    flow: "mad_delegation.json"
  - pattern: "failover|fallback|backup"
    flow: "failover_demo.json"

# Default flow if no pattern matches
default_flow: "basic_request.json"

# Model preferences (for Language Model components)
llm_preferences:
  primary_provider: "anthropic"
  primary_model: "claude-sonnet-4-5"
  primary_temperature: 0.7

  fallback_provider: "ollama"
  fallback_model: "phi3:mini"
  fallback_base_url: "http://sutherland-mad:11434"

# Template-specific configuration
demo_config:
  explain_components: true          # Include component explanations in responses
  show_flow_diagrams: false         # Include ASCII flow diagrams (verbose)
  reference_adrs: true              # Mention relevant ADRs
```

---

## 6. Physical Structure

```
template_mad/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── README.md
├── template/
│   ├── __init__.py
│   ├── server_joshua.py          # Minimal glue code (~50 lines)
│   ├── flows/
│   │   ├── basic_request.json
│   │   ├── conditional_routing.json
│   │   ├── iterative_processing.json
│   │   ├── mad_delegation.json
│   │   └── failover_demo.json
│   ├── test_flows/
│   │   ├── test_basic_request.json
│   │   ├── test_conditional_routing.json
│   │   ├── test_iterative_processing.json
│   │   ├── test_mad_delegation.json
│   │   └── test_failover_demo.json
│   └── config/
│       ├── persona.md
│       └── flow_config.yaml
└── tests/
    ├── test_integration.py
    └── test_flows.py
```

### 6.1 V0.7.0 Entry Point

**V0.7.0 Approach**: Use vanilla LangFlow backend (per ADR-042), discover MCP integration pattern during implementation.

```dockerfile
# Dockerfile (V0.7.0)
FROM langflow/langflow:latest

# Copy MAD flows and configuration
COPY template/ /app/template/

# Install standard libraries
RUN pip install joshua-network joshua-logger

# Expose LangFlow backend port
EXPOSE 7860

# Start LangFlow backend server
CMD ["langflow", "run", "--host", "0.0.0.0", "--port", "7860"]
```

**MCP Integration** (TBD during implementation):
- Explore LangFlow's HTTP API for triggering flows
- Determine how to expose flows as MCP tools
- Build MCP server adapter (becomes `joshua_communicator` in v0.7.1)
- Initially may use LangFlow's built-in API endpoints directly

**No custom server_joshua.py yet** - Start with pure LangFlow backend, build integration layer as patterns emerge.

---

## 7. Testing Strategy

### 7.1 Flow Tests

Located in `test_flows/`, these test flows validate MAD-specific logic:

**test_basic_request.json**:
- Input: `{"user_message": "Hello Template MAD"}`
- Expected: Response contains "Template MAD" and explains demonstration purpose
- Validates: Language Model component works, persona injection successful

**test_conditional_routing.json**:
- Input: `{"user_message": "How do I configure Docker?"}`
- Expected: Routes to technical handler, response contains technical guidance
- Validates: If-Else component routing logic

**test_iterative_processing.json**:
- Input: `{"items": ["apple", "banana", "cherry"], "transformation_instruction": "Make uppercase"}`
- Expected: `["APPLE", "BANANA", "CHERRY"]`
- Validates: Loop component iteration, LLM transformation per item

**test_mad_delegation.json**:
- Input: `{"task_description": "Run phi3:mini inference on 'Hello world'"}`
- Expected: Response from Sutherland containing "Hello world" processed by phi3
- Validates: MCP Tools component connection, Agent tool use

**test_failover_demo.json**:
- Input: `{"user_request": "Test message"}` (with Anthropic API key removed)
- Expected: Response from Ollama/Sutherland, `used_fallback: true`
- Validates: Condition component failover logic

### 7.2 Integration Tests

Located in `tests/`, these Python tests validate end-to-end behavior:

**test_integration.py**:
```python
import pytest
from template.server_joshua import FlowRunner

@pytest.mark.asyncio
async def test_basic_request_flow():
    """Test basic request handling end-to-end"""
    runner = FlowRunner(...)
    result = await runner.execute_flow(
        "basic_request.json",
        {"user_message": "Hello"}
    )
    assert "Template MAD" in result["response"]

@pytest.mark.asyncio
async def test_mcp_server_tool_exposure():
    """Test that flows are exposed as MCP tools"""
    # Test MCP server endpoint responds with tool list
    # Verify all 5 tools are available
    ...
```

**test_flows.py**:
```python
def test_all_flows_valid_json():
    """Ensure all .json files are valid LangFlow definitions"""
    for flow_file in Path("template/flows").glob("*.json"):
        data = json.load(open(flow_file))
        assert "components" in data or "nodes" in data
```

---

## 8. LLM Access (Per ADR-040)

### 8.1 Default: Local Ollama Instance

Uses LangFlow's native **Language Model component** with Ollama provider:

```json
{
  "component": "Language Model",
  "provider": "ollama",
  "base_url": "http://localhost:11434",
  "model": "qwen2.5:14b",
  "temperature": 0.7,
  "max_tokens": 2000
}
```

**Rationale** (ADR-040: Baseline LLM for Local Agent Resilience):
- **Cost**: Zero API costs, unlimited usage
- **Privacy**: All data stays local
- **Resilience**: Works offline, no external dependencies
- **Learning**: Developers can experiment without API keys
- **Performance**: 3-8s latency acceptable for learning/demo

### 8.2 Optional: Anthropic Upgrade Path (Future)

For production or complex reasoning tasks:

```json
{
  "component": "Language Model",
  "provider": "anthropic",
  "model": "claude-sonnet-4-5",
  "temperature": 0.7,
  "max_tokens": 2000,
  "api_key": "${ANTHROPIC_API_KEY}"
}
```

**V0.7.0**: Stick with local Ollama, prove patterns work
**V0.7.1+**: Add Anthropic as optional configuration for production use

### 8.3 No Custom Nodes Required

All LLM access via **native components**. No LLMCLINode, no custom wrappers.

---

## 9. Success Criteria (V0.7.0)

### 9.1 Functional Requirements

- [ ] LangFlow backend starts successfully (`langflow run`)
- [ ] Navigate to `http://localhost:7860` shows LangFlow UI
- [ ] `imperator_chat.json` flow loads in playground
- [ ] Can send messages and receive deliberative responses
- [ ] Message History component maintains conversation context across turns
- [ ] Agent component successfully uses Language Model (Ollama local: qwen2.5:14b)
- [ ] Imperator persona consistent (multi-step reasoning, thinking out loud)

### 9.2 Learning Requirements (Discovery Goals)

- [ ] Document what deliberative reasoning patterns emerge
- [ ] Identify common prompt structures for Imperator
- [ ] Discover how Agent component manages conversation state
- [ ] Learn LangFlow's flow editing experience
- [ ] Understand performance characteristics (latency, token usage)
- [ ] Identify patterns worth extracting to `joshua_thought_engine` (v0.7.1)

### 9.3 Performance Requirements

- [ ] Chat response latency: 2-5s for 90% of messages
- [ ] Multi-turn conversations work smoothly (no memory issues for 10+ turn conversations)
- [ ] Container starts in < 30s
- [ ] LangFlow UI responsive in browser

### 9.4 Quality Requirements

- [ ] Flow editable in LangFlow visual editor
- [ ] README explains how to start and use chatbot
- [ ] Imperator persona demonstrates deliberative reasoning (not just echo)
- [ ] Graceful handling of Ollama connection errors (clear error messages)

### 9.5 Validation of ADRs

- [ ] **ADR-037**: Zero custom nodes used - all native LangFlow components
- [ ] **ADR-042**: Embedded LangFlow backend running on port 7860
- [ ] **ADR-044**: Vanilla approach - no premature library extraction
- [ ] **ADR-045**: Imperator reasoning patterns emerging (inform future PCP design)

---

## 10. Version Evolution

### V0.7.0 (Current - Vanilla Learning Phase)
- Pure LangFlow backend (embedded, full-featured)
- Native LangFlow components only
- Build flows directly in `template/flows/`
- Discover MCP integration patterns
- Discover Imperator reasoning patterns
- No custom libraries yet (just joshua_network, joshua_logger)
- Learn before abstracting

### V0.7.1+ (Pattern Extraction)
- Extract `joshua_communicator` (MCP→LangFlow adapter)
- Extract `joshua_thought_engine` (Imperator flows + config)
- Optimize footprint if needed
- Build based on discovered patterns, not speculation

### V0.8 (Context-Aware Reasoning)
- Add Henson MAD (Qdrant RAG)
- Integrate RAG into Imperator flows
- Context retrieval before deliberation

### V1.0 (Conversation Bus)
- Rogers integration (service discovery)
- Kafka-based message bus
- joshua_communicator gains Kafka transport

### V5.0 (Full PCP)
- Complete Progressive Cognitive Pipeline
- All tiers: DTR, LPPM, CET (Langfuse), Imperator, CRS
- Cognitive fast paths operational
- 80-90% cost reduction through intelligent routing

---

## 11. Dependencies

### Upstream Dependencies
- **Local Ollama Instance** - Running on localhost:11434 (per ADR-040)
  - Models: qwen2.5:14b (preferred) or llama3.1:8b
- **LangFlow** (v1.5+) - Platform providing all components

### Downstream Consumers
- **All MADs** - Copy patterns from Template
- **Developers** - Reference implementation for onboarding
- **Hopper** (MAD #1) - Studies flows for metaprogramming

---

## 12. Related Documentation

- **ADR-032**: Fully Flow-Based Architecture (establishes flows as implementation model)
- **ADR-037**: LangFlow Node Sourcing Strategy (Use → Compose → Fork → Build)
- **ADR-042**: MAD Embedded LangFlow Backend Architecture (each MAD runs LangFlow backend)
- **ADR-044**: Monorepo Library Distribution Pattern (extract libraries as patterns emerge)
- **ADR-045**: PCP as Unified Flow Pipeline (PCP in joshua_thought_engine)
- **System Roadmap**: `/docs/architecture/00_Joshua_System_Roadmap.md`
- **Requirements Template**: `/docs/templates/MAD_Requirements_Template.md`

---

**Last Updated:** 2025-12-23
**Status:** Ready for V0.7.0 Implementation (Vanilla Learning Phase)
**Approach**: Build flows, discover patterns, extract libraries in v0.7.1+
