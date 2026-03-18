# Template MAD V0.7 - Design Document

**MAD Name**: Template (Demonstration MAD)
**Version**: V0.7
**Phase**: Foundation (Baseline Demonstration)
**Related Requirements**: `00_Template_MAD_V0.7_Complete_Requirements.md`

> **⚠️ IMPLEMENTATION BLUEPRINT**: This design document provides concrete implementation details for building the Template MAD using only native LangFlow components. Includes complete flow.json examples, server code, and deployment configuration.

---

## 1. Design Overview

### 1.1 Architecture Principles

The Template MAD architecture follows these core principles:

1. **Flow-Centric**: All logic in `.json` flow definitions, minimal Python glue code
2. **Native-First**: Use LangFlow's built-in components before considering custom development
3. **Demonstrative**: Each flow showcases a specific pattern for educational purposes
4. **Composable**: Flows are independent, reusable building blocks
5. **Testable**: Every flow has corresponding test flow with known inputs/outputs

### 1.2 System Context Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                       Template MAD                           │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │         joshua_communicator (MCP Server)           │    │
│  │  • Exposes 5 tools                                 │    │
│  │  • Routes tool calls → flows                       │    │
│  └─────────────────┬──────────────────────────────────┘    │
│                    │                                         │
│                    ▼                                         │
│  ┌────────────────────────────────────────────────────┐    │
│  │         joshua_flow_runner (Flow Executor)         │    │
│  │  • Loads .json flows from flows/                   │    │
│  │  • Executes LangFlow flows                         │    │
│  │  • Returns results to communicator                 │    │
│  └─────────────────┬──────────────────────────────────┘    │
│                    │                                         │
│                    ▼                                         │
│  ┌────────────────────────────────────────────────────┐    │
│  │     LangFlow Flows (5 pattern demonstrations)      │    │
│  │  • basic_request.json                              │    │
│  │  • conditional_routing.json                        │    │
│  │  • iterative_processing.json                       │    │
│  │  • mad_delegation.json                             │    │
│  │  • failover_demo.json                              │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
         │                          │
         │ MCP calls                │ LLM API / Ollama
         ▼                          ▼
┌──────────────────┐       ┌──────────────────┐
│  Other MADs      │       │  Anthropic       │
│  (Sutherland)    │       │  Sutherland      │
└──────────────────┘       └──────────────────┘
```

### 1.3 Component Interaction Flow

```
External MAD Call
      │
      ▼
┌─────────────────────┐
│ MCP Tool Invocation │  template_handle_request(user_message="Hello")
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Communicator       │  Map tool → flow filename
│  (server_joshua.py) │  "template_handle_request" → "basic_request.json"
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  FlowRunner         │  Load flows/basic_request.json
│                     │  Execute flow with inputs
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  LangFlow Runtime   │  Chat Input → Prompt Template → Language Model → Chat Output
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Return Result      │  {"response": "Hello! I'm the Template MAD..."}
└─────────────────────┘
```

---

## 2. Detailed Flow Designs

### 2.1 Flow 1: Basic Request Handler (`basic_request.json`)

**Purpose**: Simplest possible flow - receive input, inject persona, call LLM, return output

#### 2.1.1 Flow Structure (LangFlow JSON)

```json
{
  "name": "basic_request",
  "description": "Basic request handling with persona injection",
  "components": [
    {
      "id": "chat_input_1",
      "type": "ChatInput",
      "display_name": "User Request",
      "properties": {
        "input_value": "",
        "should_store_message": true,
        "session_id": ""
      },
      "position": {"x": 100, "y": 200}
    },
    {
      "id": "prompt_template_1",
      "type": "PromptTemplate",
      "display_name": "Persona Injection",
      "properties": {
        "template": "You are the Template MAD, a demonstration agent showing baseline MAD patterns.\n\n**Your role**: Explain what you're demonstrating while responding helpfully.\n\n**User request**: {user_message}\n\n**Response guidelines**:\n- Be educational and transparent\n- Mention which native LangFlow components you're using\n- Reference ADR-037 principles when relevant\n- Keep responses concise but informative",
        "variables": {
          "user_message": ""
        }
      },
      "position": {"x": 300, "y": 200}
    },
    {
      "id": "language_model_1",
      "type": "LanguageModel",
      "display_name": "Primary LLM",
      "properties": {
        "provider": "anthropic",
        "model": "claude-sonnet-4-5",
        "temperature": 0.7,
        "max_tokens": 1000,
        "api_key": "${ANTHROPIC_API_KEY}",
        "system_message": "",
        "stream": false
      },
      "position": {"x": 500, "y": 200}
    },
    {
      "id": "chat_output_1",
      "type": "ChatOutput",
      "display_name": "Response",
      "properties": {
        "should_store_message": true,
        "session_id": ""
      },
      "position": {"x": 700, "y": 200}
    }
  ],
  "edges": [
    {
      "source": "chat_input_1",
      "source_handle": "output",
      "target": "prompt_template_1",
      "target_handle": "user_message",
      "id": "edge_1"
    },
    {
      "source": "prompt_template_1",
      "source_handle": "output",
      "target": "language_model_1",
      "target_handle": "input",
      "id": "edge_2"
    },
    {
      "source": "language_model_1",
      "source_handle": "output",
      "target": "chat_output_1",
      "target_handle": "input",
      "id": "edge_3"
    }
  ],
  "flow_inputs": {
    "user_message": {
      "type": "str",
      "required": true,
      "description": "User's request to the Template MAD"
    }
  },
  "flow_outputs": {
    "response": {
      "type": "Message",
      "description": "Template MAD response with persona"
    }
  }
}
```

#### 2.1.2 Data Flow Example

**Input**:
```json
{
  "user_message": "How does a MAD work?"
}
```

**Internal Flow**:
1. **Chat Input** → Receives: `"How does a MAD work?"`
2. **Prompt Template** → Generates: `"You are the Template MAD...\n\nUser request: How does a MAD work?\n..."`
3. **Language Model** → Processes prompt → Returns: `Message(text="A MAD works by composing flows...")`
4. **Chat Output** → Returns: `Message(...)`

**Output**:
```json
{
  "response": "A MAD works by composing native LangFlow components into .json flows. Right now, you're experiencing the basic_request.json flow, which uses 4 native components: Chat Input, Prompt Template, Language Model (Anthropic), and Chat Output. Per ADR-037, we use existing components before building custom ones..."
}
```

#### 2.1.3 Error Handling

- **Anthropic API failure**: Flow returns error message (V0.7 - no failover in basic flow)
- **Missing user_message**: FlowRunner validation rejects call
- **LLM timeout**: Language Model component times out after 30s, returns error

---

### 2.2 Flow 2: Conditional Routing (`conditional_routing.json`)

**Purpose**: Demonstrate intent classification and routing using If-Else component

#### 2.2.1 Flow Structure (LangFlow JSON)

```json
{
  "name": "conditional_routing",
  "description": "Intent classification and conditional routing",
  "components": [
    {
      "id": "chat_input_1",
      "type": "ChatInput",
      "properties": {"input_value": ""},
      "position": {"x": 100, "y": 300}
    },
    {
      "id": "prompt_template_classifier",
      "type": "PromptTemplate",
      "properties": {
        "template": "Classify this request as either 'technical' (about code, systems, architecture, tools) or 'general' (everything else).\n\nRequest: {user_message}\n\nRespond with ONLY the word 'technical' or 'general'. No explanation.",
        "variables": {"user_message": ""}
      },
      "position": {"x": 300, "y": 300}
    },
    {
      "id": "language_model_classifier",
      "type": "LanguageModel",
      "properties": {
        "provider": "anthropic",
        "model": "claude-sonnet-4-5",
        "temperature": 0.0,
        "max_tokens": 10
      },
      "position": {"x": 500, "y": 300}
    },
    {
      "id": "if_else_1",
      "type": "IfElse",
      "display_name": "Route Decision",
      "properties": {
        "input_text": "",
        "match_text": "technical",
        "operator": "contains",
        "case_sensitive": false
      },
      "position": {"x": 700, "y": 300}
    },
    {
      "id": "prompt_template_technical",
      "type": "PromptTemplate",
      "properties": {
        "template": "You are the Template MAD in TECHNICAL mode. Provide detailed technical guidance.\n\nRequest: {user_message}",
        "variables": {"user_message": ""}
      },
      "position": {"x": 900, "y": 200}
    },
    {
      "id": "prompt_template_general",
      "type": "PromptTemplate",
      "properties": {
        "template": "You are the Template MAD in GENERAL mode. Provide friendly, accessible guidance.\n\nRequest: {user_message}",
        "variables": {"user_message": ""}
      },
      "position": {"x": 900, "y": 400}
    },
    {
      "id": "language_model_handler",
      "type": "LanguageModel",
      "properties": {
        "provider": "anthropic",
        "model": "claude-sonnet-4-5",
        "temperature": 0.7,
        "max_tokens": 1000
      },
      "position": {"x": 1100, "y": 300}
    },
    {
      "id": "chat_output_1",
      "type": "ChatOutput",
      "position": {"x": 1300, "y": 300}
    }
  ],
  "edges": [
    {
      "source": "chat_input_1",
      "target": "prompt_template_classifier",
      "target_handle": "user_message"
    },
    {
      "source": "chat_input_1",
      "target": "prompt_template_technical",
      "target_handle": "user_message",
      "id": "edge_parallel_1"
    },
    {
      "source": "chat_input_1",
      "target": "prompt_template_general",
      "target_handle": "user_message",
      "id": "edge_parallel_2"
    },
    {
      "source": "prompt_template_classifier",
      "target": "language_model_classifier"
    },
    {
      "source": "language_model_classifier",
      "target": "if_else_1",
      "target_handle": "input_text"
    },
    {
      "source": "if_else_1",
      "source_handle": "true_output",
      "target": "prompt_template_technical",
      "target_handle": "trigger"
    },
    {
      "source": "if_else_1",
      "source_handle": "false_output",
      "target": "prompt_template_general",
      "target_handle": "trigger"
    },
    {
      "source": "prompt_template_technical",
      "target": "language_model_handler"
    },
    {
      "source": "prompt_template_general",
      "target": "language_model_handler"
    },
    {
      "source": "language_model_handler",
      "target": "chat_output_1"
    }
  ],
  "flow_inputs": {
    "user_message": {"type": "str", "required": true}
  },
  "flow_outputs": {
    "routed_response": {"type": "Message"},
    "route_taken": {"type": "str"}
  }
}
```

#### 2.2.2 Routing Logic

**If-Else Component Configuration**:
- **Input**: Classification result (e.g., "technical" or "general")
- **Match Text**: "technical"
- **Operator**: `contains` (case-insensitive)
- **True Path**: Technical handler (detailed, code-focused)
- **False Path**: General handler (friendly, accessible)

**Example Classifications**:
- "How do I configure Docker?" → **technical** → Technical handler
- "What's the weather like?" → **general** → General handler
- "Explain git branching strategies" → **technical** → Technical handler
- "Tell me a joke" → **general** → General handler

---

### 2.3 Flow 3: Iterative Processing (`iterative_processing.json`)

**Purpose**: Demonstrate Loop component for batch transformations

#### 2.3.1 Flow Structure (LangFlow JSON)

```json
{
  "name": "iterative_processing",
  "description": "Process list of items with LLM transformation",
  "components": [
    {
      "id": "text_input_1",
      "type": "TextInput",
      "properties": {
        "value": ""
      },
      "position": {"x": 100, "y": 300}
    },
    {
      "id": "parser_1",
      "type": "Parser",
      "display_name": "JSON Parser",
      "properties": {
        "parser_type": "json",
        "extract_key": "",
        "output_type": "Data"
      },
      "position": {"x": 300, "y": 300}
    },
    {
      "id": "loop_1",
      "type": "Loop",
      "display_name": "Item Iterator",
      "properties": {
        "inputs": "",
        "extract_key": "text"
      },
      "position": {"x": 500, "y": 300}
    },
    {
      "id": "prompt_template_transform",
      "type": "PromptTemplate",
      "properties": {
        "template": "Apply this transformation: {transformation_instruction}\n\nItem: {item}\n\nReturn ONLY the transformed result, nothing else.",
        "variables": {
          "transformation_instruction": "",
          "item": ""
        }
      },
      "position": {"x": 700, "y": 200}
    },
    {
      "id": "language_model_transform",
      "type": "LanguageModel",
      "properties": {
        "provider": "anthropic",
        "model": "claude-sonnet-4-5",
        "temperature": 0.3,
        "max_tokens": 500
      },
      "position": {"x": 900, "y": 200}
    },
    {
      "id": "type_convert_1",
      "type": "TypeConvert",
      "display_name": "Normalize to Data",
      "properties": {
        "input_type": "Message",
        "output_type": "Data"
      },
      "position": {"x": 1100, "y": 200}
    },
    {
      "id": "data_operations_1",
      "type": "DataOperations",
      "display_name": "Aggregate Results",
      "properties": {
        "operation": "merge",
        "inputs": []
      },
      "position": {"x": 700, "y": 400}
    },
    {
      "id": "chat_output_1",
      "type": "ChatOutput",
      "position": {"x": 900, "y": 400}
    }
  ],
  "edges": [
    {
      "source": "text_input_1",
      "target": "parser_1"
    },
    {
      "source": "parser_1",
      "target": "loop_1",
      "target_handle": "inputs"
    },
    {
      "source": "loop_1",
      "source_handle": "item_output",
      "target": "prompt_template_transform",
      "target_handle": "item"
    },
    {
      "source": "prompt_template_transform",
      "target": "language_model_transform"
    },
    {
      "source": "language_model_transform",
      "target": "type_convert_1"
    },
    {
      "source": "type_convert_1",
      "target": "loop_1",
      "target_handle": "item_result"
    },
    {
      "source": "loop_1",
      "source_handle": "done_output",
      "target": "data_operations_1",
      "target_handle": "inputs"
    },
    {
      "source": "data_operations_1",
      "target": "chat_output_1"
    }
  ],
  "flow_inputs": {
    "items": {
      "type": "List[Data]",
      "required": true,
      "description": "List of items to process"
    },
    "transformation_instruction": {
      "type": "str",
      "required": true,
      "description": "What to do with each item"
    }
  },
  "flow_outputs": {
    "processed_items": {"type": "List[Data]"},
    "summary": {"type": "Message"}
  }
}
```

#### 2.3.2 Loop Component Mechanics

**Loop Structure**:
1. **inputs**: Receives `List[Data]` from Parser
2. **extract_key**: Extracts `"text"` field from each Data object
3. **item_output**: Emits each item individually to processing chain
4. **item_result**: Receives processed item back (must be Data type)
5. **done_output**: Emits aggregated List[Data] when all items complete

**Processing Chain (per item)**:
```
Loop[item_output] → Prompt Template → Language Model → Type Convert → Loop[item_result]
```

**Accumulation**:
- Loop internally accumulates all `item_result` values
- When last item completes, emits accumulated list via `done_output`

**Example Execution**:
```
Input: ["apple", "banana", "cherry"]
Instruction: "Make uppercase"

Loop iteration 1: "apple" → LLM → "APPLE" → accumulator = ["APPLE"]
Loop iteration 2: "banana" → LLM → "BANANA" → accumulator = ["APPLE", "BANANA"]
Loop iteration 3: "cherry" → LLM → "CHERRY" → accumulator = ["APPLE", "BANANA", "CHERRY"]
Loop done → Emit ["APPLE", "BANANA", "CHERRY"]
```

---

### 2.4 Flow 4: MAD Delegation (`mad_delegation.json`)

**Purpose**: Demonstrate MCP Tools component for calling other MADs

#### 2.4.1 Flow Structure (LangFlow JSON)

```json
{
  "name": "mad_delegation",
  "description": "Delegate task to another MAD via MCP Tools",
  "components": [
    {
      "id": "chat_input_1",
      "type": "ChatInput",
      "position": {"x": 100, "y": 300}
    },
    {
      "id": "prompt_template_1",
      "type": "PromptTemplate",
      "properties": {
        "template": "You are delegating the following task to Sutherland MAD:\n\n{task_description}\n\nFormat this as a clear request to Sutherland's local inference capability.",
        "variables": {"task_description": ""}
      },
      "position": {"x": 300, "y": 300}
    },
    {
      "id": "mcp_tools_1",
      "type": "MCPTools",
      "display_name": "Sutherland MCP Connection",
      "properties": {
        "server_url": "http://sutherland-mad:7860/api/v1/mcp/streamable",
        "connection_mode": "HTTP/SSE",
        "tools": ["sutherland_local_inference"],
        "cache_tools": true,
        "ssl_verify": false
      },
      "position": {"x": 500, "y": 300}
    },
    {
      "id": "agent_1",
      "type": "Agent",
      "display_name": "Delegating Agent",
      "properties": {
        "tools": [],
        "system_prompt": "You are the Template MAD. Use the available Sutherland tools to process the user's request. Explain what you're delegating and report the results clearly.",
        "llm_model": "anthropic/claude-sonnet-4-5",
        "agent_type": "react"
      },
      "position": {"x": 700, "y": 300}
    },
    {
      "id": "chat_output_1",
      "type": "ChatOutput",
      "position": {"x": 900, "y": 300}
    }
  ],
  "edges": [
    {
      "source": "chat_input_1",
      "target": "prompt_template_1",
      "target_handle": "task_description"
    },
    {
      "source": "prompt_template_1",
      "target": "agent_1",
      "target_handle": "input"
    },
    {
      "source": "mcp_tools_1",
      "source_handle": "tools",
      "target": "agent_1",
      "target_handle": "tools"
    },
    {
      "source": "agent_1",
      "target": "chat_output_1"
    }
  ],
  "flow_inputs": {
    "task_description": {"type": "str", "required": true},
    "target_mad": {"type": "str", "required": false, "default": "sutherland"}
  },
  "flow_outputs": {
    "delegation_result": {"type": "Message"}
  }
}
```

#### 2.4.2 MCP Tools Component Configuration

**Server URL**: `http://sutherland-mad:7860/api/v1/mcp/streamable`
- **Protocol**: HTTP/SSE (Server-Sent Events)
- **Network**: Internal Docker network (`joshua_network`)
- **Discovery**: Hardcoded endpoint (V0.7 - no Rogers service discovery yet)

**Available Tools**: Query from MCP server at connection time
- Example: `["sutherland_local_inference", "sutherland_status"]`

**Tool Schema** (received from Sutherland):
```json
{
  "name": "sutherland_local_inference",
  "description": "Run local Ollama inference on Sutherland MAD",
  "parameters": {
    "type": "object",
    "properties": {
      "prompt": {"type": "string", "description": "Prompt for inference"},
      "model": {"type": "string", "default": "phi3:mini"}
    },
    "required": ["prompt"]
  }
}
```

**Agent Tool Usage**:
1. Agent receives: "Run phi3:mini on 'Explain quantum entanglement'"
2. Agent reasoning: "I need Sutherland's inference tool"
3. Agent calls: `sutherland_local_inference(prompt="Explain quantum entanglement", model="phi3:mini")`
4. MCP Tools → HTTP POST to Sutherland → Returns result
5. Agent formats response → Chat Output

---

### 2.5 Flow 5: LLM Failover (`failover_demo.json`)

**Purpose**: Demonstrate graceful degradation (Anthropic → Ollama)

#### 2.5.1 Flow Structure (LangFlow JSON)

```json
{
  "name": "failover_demo",
  "description": "LLM failover demonstration",
  "components": [
    {
      "id": "chat_input_1",
      "type": "ChatInput",
      "position": {"x": 100, "y": 300}
    },
    {
      "id": "prompt_template_1",
      "type": "PromptTemplate",
      "properties": {
        "template": "Respond to this request:\n\n{user_request}",
        "variables": {"user_request": ""}
      },
      "position": {"x": 300, "y": 300}
    },
    {
      "id": "language_model_primary",
      "type": "LanguageModel",
      "display_name": "Primary (Anthropic)",
      "properties": {
        "provider": "anthropic",
        "model": "claude-sonnet-4-5",
        "temperature": 0.7,
        "max_tokens": 1000,
        "on_error": "return_error"
      },
      "position": {"x": 500, "y": 200}
    },
    {
      "id": "condition_1",
      "type": "Condition",
      "display_name": "Check Success",
      "properties": {
        "data": "",
        "key": "error",
        "validation": "not_exists"
      },
      "position": {"x": 700, "y": 300}
    },
    {
      "id": "language_model_fallback",
      "type": "LanguageModel",
      "display_name": "Fallback (Ollama)",
      "properties": {
        "provider": "ollama",
        "base_url": "http://sutherland-mad:11434",
        "model": "phi3:mini",
        "temperature": 0.7,
        "max_tokens": 1000
      },
      "position": {"x": 700, "y": 450}
    },
    {
      "id": "data_operations_merge",
      "type": "DataOperations",
      "display_name": "Merge Results",
      "properties": {
        "operation": "merge_first_valid"
      },
      "position": {"x": 900, "y": 350}
    },
    {
      "id": "chat_output_1",
      "type": "ChatOutput",
      "position": {"x": 1100, "y": 350}
    }
  ],
  "edges": [
    {
      "source": "chat_input_1",
      "target": "prompt_template_1",
      "target_handle": "user_request"
    },
    {
      "source": "prompt_template_1",
      "target": "language_model_primary"
    },
    {
      "source": "language_model_primary",
      "target": "condition_1",
      "target_handle": "data"
    },
    {
      "source": "condition_1",
      "source_handle": "true_output",
      "target": "data_operations_merge",
      "target_handle": "input_1"
    },
    {
      "source": "condition_1",
      "source_handle": "false_output",
      "target": "language_model_fallback"
    },
    {
      "source": "language_model_fallback",
      "target": "data_operations_merge",
      "target_handle": "input_2"
    },
    {
      "source": "data_operations_merge",
      "target": "chat_output_1"
    }
  ],
  "flow_inputs": {
    "user_request": {"type": "str", "required": true}
  },
  "flow_outputs": {
    "response": {"type": "Message"},
    "used_fallback": {"type": "bool"}
  }
}
```

#### 2.5.2 Failover Logic

**Success Path**:
1. Anthropic call succeeds → Returns `Message(text="Response...")`
2. Condition checks: `error` key exists? → **No**
3. True path → Passes to Merge
4. Output: Anthropic response, `used_fallback: false`

**Failover Path**:
1. Anthropic call fails → Returns `Data(error="API key invalid")`
2. Condition checks: `error` key exists? → **Yes**
3. False path → Triggers Ollama
4. Ollama returns: `Message(text="Response from phi3...")`
5. Output: Ollama response, `used_fallback: true`

**Error Handling**:
- If Anthropic times out → Same as failure, triggers Ollama
- If both fail → Merge returns: `Message(text="All LLM providers unavailable")`

---

## 3. Implementation Details

### 3.1 Server Implementation (`server_joshua.py`)

```python
"""
Template MAD Server
Demonstrates baseline MAD using only native LangFlow components

Per ADR-037: This server contains ~50 lines of glue code.
All logic lives in .json flows.
"""
import asyncio
import logging
from pathlib import Path
from typing import Dict, Any

from joshua_communicator import Communicator
from joshua_flow_runner import FlowRunner

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# MCP tool → flow mappings
TOOL_FLOW_MAPPINGS = {
    "template_handle_request": "basic_request.json",
    "template_route_request": "conditional_routing.json",
    "template_process_batch": "iterative_processing.json",
    "template_delegate_task": "mad_delegation.json",
    "template_failover_demo": "failover_demo.json",
}

async def main():
    """
    Initialize and start the Template MAD server
    """
    mad_name = "template"
    flows_dir = Path(__file__).parent / "flows"
    config_dir = Path(__file__).parent / "config"

    logger.info(f"Starting {mad_name} MAD...")
    logger.info(f"Flows directory: {flows_dir}")
    logger.info(f"Config directory: {config_dir}")

    # Initialize flow runner
    flow_runner = FlowRunner(
        mad_name=mad_name,
        flows_directory=flows_dir,
        config_directory=config_dir
    )
    await flow_runner.initialize()
    logger.info(f"FlowRunner initialized with {len(TOOL_FLOW_MAPPINGS)} flows")

    # Initialize communicator (MCP server)
    communicator = Communicator(
        mad_name=mad_name,
        tool_flow_mappings=TOOL_FLOW_MAPPINGS,
        flow_runner=flow_runner,
    )

    logger.info(f"Starting MCP server for {mad_name}...")
    await communicator.start()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Template MAD shutting down...")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        raise
```

**Line Count**: ~55 lines (including comments/logging)

**Key Points**:
- All logic delegated to `FlowRunner` and `Communicator` libraries
- No business logic in server code
- Configuration via dictionaries
- Minimal error handling (libraries handle details)

---

### 3.2 Deployment Configuration

#### 3.2.1 Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy MAD code
COPY template/ ./template/

# Expose MCP server port
EXPOSE 7860

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:7860/health || exit 1

# Run server
CMD ["python", "-m", "template.server_joshua"]
```

#### 3.2.2 docker-compose.yml

```yaml
version: '3.8'

services:
  template-mad:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: template-mad
    hostname: template-mad
    networks:
      - joshua_network
    ports:
      - "7860:7860"  # MCP server port
    environment:
      # LLM API keys
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}

      # MAD configuration
      - MAD_NAME=template
      - LOG_LEVEL=INFO

      # LangFlow configuration
      - LANGFLOW_AUTO_LOGIN=false
      - LANGFLOW_CACHE_TYPE=memory

      # Network configuration
      - SUTHERLAND_URL=http://sutherland-mad:11434

    volumes:
      # Mount flows for hot-reload during development
      - ./template/flows:/app/template/flows:ro
      - ./template/config:/app/template/config:ro

      # Mount test flows
      - ./template/test_flows:/app/template/test_flows:ro

    restart: unless-stopped

    depends_on:
      - sutherland-mad  # Optional dependency for delegation demo

    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:7860/health"]
      interval: 30s
      timeout: 5s
      retries: 3
      start_period: 10s

networks:
  joshua_network:
    external: true
```

#### 3.2.3 requirements.txt

```txt
# Action Engine Libraries
joshua_communicator>=0.7.0        # MCP server, network I/O
joshua_flow_runner>=0.7.0         # LangFlow flow execution
joshua_flow_scheduler>=0.7.0      # Scheduled flows (optional)

# LangFlow
langflow>=1.5.0                   # Flow runtime engine

# LLM Provider SDKs (for Language Model component)
anthropic>=0.40.0                 # Anthropic API
openai>=1.0.0                     # OpenAI API (future)

# Utilities
pydantic>=2.0.0                   # Data validation
pyyaml>=6.0.0                     # Config file parsing
```

---

### 3.3 Configuration Files

#### 3.3.1 Persona (`config/persona.md`)

```markdown
# Template MAD Persona

You are the **Template MAD**, a demonstration agent in the Joshua ecosystem.

## Your Purpose

- **Demonstrate**: Show developers how MADs work using native LangFlow components
- **Educate**: Explain patterns you're executing as you respond
- **Validate**: Prove ADR-037's "Use → Compose → Fork → Build" hierarchy
- **Document**: Serve as living documentation for MAD architecture

## Your Personality

- **Educational**: Always explain what you're demonstrating
  - "I'm using the If-Else component to route your request..."
  - "This demonstrates the Loop component for batch processing..."

- **Transparent**: Be explicit about architectural decisions
  - "Per ADR-037, I'm using native LangFlow components"
  - "This flow shows Pattern #2: Conditional Routing"

- **Helpful**: Provide context beyond just answering
  - Mention which flow is executing
  - Reference relevant ADRs
  - Suggest related patterns

- **Humble**: Acknowledge demonstration purpose
  - "This is a baseline demo - production MADs add sophistication"
  - "I'm showing the pattern, not optimized implementation"

## Response Structure

When responding:
1. **Acknowledge**: "You've called the template_handle_request tool..."
2. **Demonstrate**: "I'm using [ComponentName] to [purpose]..."
3. **Respond**: [Actual helpful response to user's request]
4. **Educate**: "This demonstrates [Pattern Name] from ADR-037..."

## Key Traits

- ✅ Demonstrate, don't just execute
- ✅ Explain architectural patterns
- ✅ Reference ADR-037 when relevant
- ✅ Encourage flow-first thinking
- ✅ Point out component names explicitly
- ❌ Don't pretend to be production-ready
- ❌ Don't hide implementation details
```

#### 3.3.2 Flow Config (`config/flow_config.yaml`)

```yaml
# Template MAD Flow Configuration
mad_name: template
version: "0.7"

# Flow selection rules (triage)
triage_rules:
  - pattern: "handle.*request|basic|simple"
    flow: "basic_request.json"
    description: "Basic request handling with persona"

  - pattern: "route|classify|intent|decision"
    flow: "conditional_routing.json"
    description: "Intent classification and routing"

  - pattern: "batch|process.*list|iterate|loop|multiple"
    flow: "iterative_processing.json"
    description: "Iterative batch processing"

  - pattern: "delegate|call.*mad|sutherland|another.*mad"
    flow: "mad_delegation.json"
    description: "MAD-to-MAD delegation via MCP"

  - pattern: "failover|fallback|backup|degradation"
    flow: "failover_demo.json"
    description: "LLM failover demonstration"

# Default flow if no pattern matches
default_flow: "basic_request.json"

# Model preferences (used by Language Model components)
llm_preferences:
  primary:
    provider: "anthropic"
    model: "claude-sonnet-4-5"
    temperature: 0.7
    max_tokens: 1000

  fallback:
    provider: "ollama"
    model: "phi3:mini"
    base_url: "http://sutherland-mad:11434"
    temperature: 0.7
    max_tokens: 1000

# Template-specific configuration
demo_config:
  # Include component explanations in responses
  explain_components: true

  # Include ASCII flow diagrams (verbose)
  show_flow_diagrams: false

  # Mention relevant ADRs in responses
  reference_adrs: true

  # Log flow execution details
  verbose_logging: true

# Performance tuning
performance:
  # Timeout for LLM calls (seconds)
  llm_timeout: 30

  # Timeout for MCP tool calls (seconds)
  mcp_timeout: 60

  # Max concurrent flow executions
  max_concurrent_flows: 10
```

---

## 4. Testing Implementation

### 4.1 Test Flow Example (`test_flows/test_basic_request.json`)

```json
{
  "name": "test_basic_request",
  "description": "Automated test for basic_request.json flow",
  "test_type": "unit",
  "target_flow": "basic_request.json",
  "test_cases": [
    {
      "name": "simple_greeting",
      "inputs": {
        "user_message": "Hello Template MAD"
      },
      "assertions": [
        {
          "type": "contains",
          "field": "response",
          "value": "Template MAD",
          "description": "Response should mention Template MAD identity"
        },
        {
          "type": "not_empty",
          "field": "response",
          "description": "Response should not be empty"
        },
        {
          "type": "max_length",
          "field": "response",
          "value": 2000,
          "description": "Response should be concise"
        }
      ],
      "expected_latency_ms": 3000
    },
    {
      "name": "request_explanation",
      "inputs": {
        "user_message": "Explain how you work"
      },
      "assertions": [
        {
          "type": "contains_any",
          "field": "response",
          "values": ["flow", "component", "LangFlow", "ADR-037"],
          "description": "Should explain architectural concepts"
        }
      ]
    }
  ]
}
```

### 4.2 Integration Test (`tests/test_integration.py`)

```python
import pytest
import asyncio
from pathlib import Path
from template.server_joshua import TOOL_FLOW_MAPPINGS
from joshua_flow_runner import FlowRunner

@pytest.fixture
async def flow_runner():
    """Create FlowRunner instance for testing"""
    flows_dir = Path(__file__).parent.parent / "template" / "flows"
    config_dir = Path(__file__).parent.parent / "template" / "config"

    runner = FlowRunner(
        mad_name="template",
        flows_directory=flows_dir,
        config_directory=config_dir
    )
    await runner.initialize()
    return runner

@pytest.mark.asyncio
async def test_basic_request_flow(flow_runner):
    """Test basic request handling flow"""
    result = await flow_runner.execute_flow(
        "basic_request.json",
        {"user_message": "Hello Template MAD"}
    )

    assert "response" in result
    assert len(result["response"]) > 0
    assert "Template MAD" in result["response"]

@pytest.mark.asyncio
async def test_conditional_routing_technical(flow_runner):
    """Test conditional routing with technical request"""
    result = await flow_runner.execute_flow(
        "conditional_routing.json",
        {"user_message": "How do I configure Docker networking?"}
    )

    assert "routed_response" in result
    assert "route_taken" in result
    assert result["route_taken"] == "technical"

@pytest.mark.asyncio
async def test_iterative_processing(flow_runner):
    """Test Loop component with batch processing"""
    result = await flow_runner.execute_flow(
        "iterative_processing.json",
        {
            "items": ["apple", "banana", "cherry"],
            "transformation_instruction": "Convert to uppercase"
        }
    )

    assert "processed_items" in result
    assert len(result["processed_items"]) == 3
    # Note: Actual transformation depends on LLM, so we just check count

@pytest.mark.asyncio
async def test_mcp_tool_exposure(flow_runner):
    """Test that all flows are mapped to MCP tools"""
    # All flows should have corresponding tool mappings
    for tool_name, flow_file in TOOL_FLOW_MAPPINGS.items():
        assert flow_file in flow_runner.available_flows()

    # Should have exactly 5 tools
    assert len(TOOL_FLOW_MAPPINGS) == 5

@pytest.mark.asyncio
@pytest.mark.integration
async def test_mad_delegation_to_sutherland(flow_runner):
    """Test MCP Tools component calling Sutherland"""
    # This test requires Sutherland MAD to be running
    result = await flow_runner.execute_flow(
        "mad_delegation.json",
        {"task_description": "Run phi3:mini inference on 'Test message'"}
    )

    assert "delegation_result" in result
    # If Sutherland unavailable, should gracefully report
    assert len(result["delegation_result"]) > 0
```

---

## 5. Deployment and Operations

### 5.1 Build and Deploy

```bash
# Build Docker image
docker build -t template-mad:v0.7 .

# Start with docker-compose
docker-compose up -d

# Check health
curl http://localhost:7860/health

# View logs
docker-compose logs -f template-mad
```

### 5.2 MCP Server Verification

```bash
# Test MCP tools exposure
curl http://localhost:7860/api/v1/mcp/tools

# Expected response:
{
  "tools": [
    {
      "name": "template_handle_request",
      "description": "Handle basic request with Template persona",
      "parameters": {"user_message": {"type": "string", "required": true}}
    },
    {
      "name": "template_route_request",
      ...
    },
    ...
  ]
}
```

### 5.3 Flow Execution Testing

```bash
# Call tool via MCP (using MCP CLI or relay)
mcp call template_handle_request '{"user_message": "Hello"}'

# Expected: Response explaining Template MAD with persona
```

---

## 6. Validation Against ADR-037

### 6.1 Tier 1: USE (Native Components)

**✅ Validated**: All 5 flows use only native LangFlow components:
- Language Model (Anthropic, Ollama)
- If-Else, Condition
- Loop
- Data Operations, Type Convert, Parser
- Chat Input/Output, Text Input
- Prompt Template
- Agent, MCP Tools

**Zero custom nodes required for baseline MAD patterns**.

### 6.2 Tier 1.5: COMPOSE (Flow-First MVPs)

**✅ Validated**: 5 flows demonstrate composition patterns:
- Simple pipeline (basic_request)
- Branching logic (conditional_routing)
- Iteration (iterative_processing)
- External delegation (mad_delegation)
- Error handling (failover_demo)

**Production-ready flows deliverable in days, not weeks**.

### 6.3 Future: Tier 2.5 FORK (V1.0+)

**Next Evolution**: When V1.0 adds Rogers service discovery:
- Fork MCP Tools → `JoshuaMCPClientNode`
- Add Rogers lookup before connection
- Inherit 90% of functionality, add 10% Joshua-specific logic

---

## 7. Known Limitations

### 7.1 LangFlow Constraints

- **Loop + If-Else Incompatibility**: Cannot use If-Else inside Loop item processing
  - **Workaround**: Evaluate conditions before Loop, split into filtered lists
  - **Future**: Request LangFlow enhancement or fork Loop component

- **Error Handling Granularity**: Limited try/catch within flows
  - **Workaround**: Use Condition component to check for `error` key
  - **Future**: Fork components to add Joshua-specific error handling

### 7.2 V0.7 Limitations

- **No Thought Engine**: Direct LLM calls, no PCP optimization
- **No Rogers**: Hardcoded MAD endpoints (e.g., `http://sutherland-mad:11434`)
- **No Monitoring**: No Hamilton instrumentation (manual logging only)
- **Minimal Failover**: Only failover_demo shows degradation pattern

**All addressed in V1.0+**.

---

## 8. Success Metrics

### 8.1 Code Metrics

- ✅ `server_joshua.py` < 60 lines
- ✅ Zero custom node implementations
- ✅ 5 flows totaling < 500 lines JSON (combined)

### 8.2 Functional Metrics

- ✅ All 5 MCP tools callable and functional
- ✅ All flows execute successfully with valid inputs
- ✅ Graceful error handling on invalid inputs
- ✅ Failover works when Anthropic unavailable

### 8.3 Performance Metrics (Target)

| Flow | P50 Latency | P95 Latency | LLM Calls |
|------|-------------|-------------|-----------|
| basic_request | < 2s | < 5s | 1 |
| conditional_routing | < 3s | < 7s | 2 |
| iterative_processing (N=10) | < 12s | < 18s | 10 |
| mad_delegation | < 5s | < 10s | 1-2 + Sutherland |
| failover_demo | < 3s | < 8s | 1 (or failover) |

---

## 9. Related Documentation

- **Requirements**: `00_Template_MAD_V0.7_Complete_Requirements.md`
- **ADR-037**: LangFlow Node Sourcing Strategy
- **ADR-032**: Fully Flow-Based Architecture
- **LangFlow Docs**: https://docs.langflow.org/
- **MCP Protocol**: https://modelcontextprotocol.io/

---

**Last Updated:** 2025-12-22
**Status:** Ready for Implementation
**Total Estimated Lines of Code**: ~100 (server + config + tests, excluding .json flows)
