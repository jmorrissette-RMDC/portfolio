# joshua_core Node Library Requirements

**⚠️ SUPERSEDED BY ADR-037 (2025-12-22)**

This specification was created before fully exploring the LangFlow ecosystem. **ADR-037: LangFlow Node Sourcing Strategy** establishes a "Use → Wrap → Build" hierarchy that prioritizes:

1. **USE** native LangFlow nodes (highest priority)
2. **WRAP** existing ecosystems (LangChain, Node-RED, n8n)
3. **BUILD** custom nodes only for Joshua-specific functionality (lowest priority)

**Most nodes defined here (LLMCLINode, IfElseNode, LoopNode, FilterNode, etc.) should NOT be built** - LangFlow likely provides equivalent functionality in its default palette or community Store.

**Next Steps**:
1. Explore LangFlow ecosystem comprehensively (see ADR-037 Phase 1)
2. Use native nodes where possible
3. Redefine joshua_core scope to Joshua-specific nodes only

**This document is preserved as reference** for understanding what we initially thought we needed vs. what actually exists in the ecosystem.

---

**Status**: REFERENCE ONLY - Do not implement
**Tier**: 1 (Universal) - CONCEPT
**Version**: 1.0.0 - SUPERSEDED
**Priority**: See ADR-037 for current strategy

---

## 1. Overview

`joshua_core` is the universal node library providing general-purpose, domain-agnostic nodes used across all MADs. Per **ADR-036**, this is the foundation of the node library ecosystem.

**Purpose**: Provide essential building blocks for:
- LLM access (provider-agnostic via CLI wrappers)
- Flow control (conditionals, loops, branching)
- Data transformation (filtering, merging, mapping)
- Utilities (logging, error handling, validation)

**Implementation Approach**: Per **ADR-034 (CLI-First)**, LLM access wraps provider CLIs (Claude Code, Gemini CLI, etc.) rather than implementing custom API clients.

---

## 2. Node Catalog

### 2.1. LLM Access Nodes

#### `LLMCLINode`

**Purpose**: Universal, provider-agnostic LLM access via CLI wrappers

**Node Type**: `LLMCLINode`

**Input Schema**:
```json
{
  "prompt": {
    "type": "string",
    "required": true,
    "description": "The user prompt to send to the LLM"
  },
  "system_prompt": {
    "type": "string",
    "required": false,
    "description": "System-level instructions for the LLM"
  },
  "provider": {
    "type": "string",
    "required": false,
    "enum": ["anthropic", "google", "openai", "sutherland"],
    "description": "LLM provider to use (defaults to config)"
  },
  "model": {
    "type": "string",
    "required": false,
    "description": "Specific model ID (defaults to config for provider)"
  },
  "temperature": {
    "type": "number",
    "required": false,
    "minimum": 0.0,
    "maximum": 2.0,
    "default": 1.0,
    "description": "Sampling temperature for randomness"
  },
  "max_tokens": {
    "type": "integer",
    "required": false,
    "minimum": 1,
    "maximum": 200000,
    "description": "Maximum tokens in response"
  },
  "failover_to_sutherland": {
    "type": "boolean",
    "required": false,
    "default": true,
    "description": "Fallback to local Sutherland on provider failure"
  },
  "tools": {
    "type": "array",
    "required": false,
    "description": "Tool definitions for tool calling (provider-dependent format)"
  }
}
```

**Output Schema**:
```json
{
  "response": {
    "type": "string",
    "description": "LLM response text"
  },
  "provider_used": {
    "type": "string",
    "enum": ["anthropic", "google", "openai", "sutherland"],
    "description": "Which provider was actually used"
  },
  "model_used": {
    "type": "string",
    "description": "Which model was actually used"
  },
  "tokens_used": {
    "type": "integer",
    "description": "Total tokens consumed (if available from provider)"
  },
  "tool_calls": {
    "type": "array",
    "description": "Tool calls made by LLM (if tools were provided)"
  },
  "error": {
    "type": "string",
    "description": "Error message if call failed (null on success)"
  }
}
```

**Behavior Specification**:

1. **Provider Selection**:
   - If `provider` parameter specified → Use that provider
   - Else → Use primary provider from MAD config (`llm_preferences.primary_provider`)

2. **Model Selection**:
   - If `model` parameter specified → Use that model
   - Else if provider specified → Use default model for that provider from config
   - Else → Use primary model from MAD config (`llm_preferences.primary_model`)

3. **CLI Command Construction**:
   ```bash
   # For Anthropic (Claude Code CLI)
   claude --model {model} --temperature {temp} --max-tokens {max} '{prompt}'

   # For Google (Gemini CLI)
   gemini chat --model {model} --temperature {temp} '{prompt}'

   # For OpenAI (via openai CLI or similar wrapper)
   openai chat --model {model} --temperature {temp} '{prompt}'

   # For Sutherland (local HTTP API)
   curl http://localhost:11434/v1/chat/completions \
     -d '{"model": "{model}", "messages": [...]}'
   ```

4. **Execution Flow**:
   - Construct CLI command with parameters
   - Execute via subprocess with timeout (default: 300s)
   - Parse response from stdout
   - Extract token count from response metadata (if available)
   - Return structured output

5. **Failover Behavior** (if `failover_to_sutherland` is true):
   - On primary provider failure (network error, API error, timeout):
     - Log warning: "Provider {provider} failed, falling back to Sutherland"
     - Retry request using Sutherland (local Ollama)
     - Set `provider_used` to "sutherland"
   - On Sutherland failure:
     - Raise `LLMAccessError` with details

**Error Handling**:

- **`InvalidProviderError`**: Provider not in ["anthropic", "google", "openai", "sutherland"]
- **`ProviderUnavailableError`**: Primary provider failed and `failover_to_sutherland` is false
- **`SutherlandUnavailableError`**: Failover attempted but Sutherland unreachable
- **`ValidationError`**: Invalid parameters (e.g., temperature out of range)
- **`TimeoutError`**: CLI command exceeded timeout

**Usage Example** (in Langflow .json flow):
```json
{
  "nodes": [
    {
      "id": "llm_1",
      "type": "LLMCLINode",
      "data": {
        "prompt": "Explain quantum computing in 2 sentences",
        "provider": "anthropic",
        "model": "claude-sonnet-4-5",
        "temperature": 0.7,
        "max_tokens": 150
      }
    }
  ]
}
```

**Testing Requirements**:
- Unit tests for CLI command construction
- Mock subprocess tests for each provider
- Integration test with actual Sutherland instance
- Failover scenario tests (primary down, Sutherland available)

---

### 2.2. Flow Control Nodes

#### `IfElseNode`

**Purpose**: Conditional branching - route flow based on boolean condition

**Node Type**: `IfElseNode`

**Input Schema**:
```json
{
  "condition": {
    "type": "any",
    "required": true,
    "description": "Value to evaluate"
  },
  "operator": {
    "type": "string",
    "required": true,
    "enum": ["==", "!=", ">", "<", ">=", "<=", "contains", "not_contains", "is_empty", "is_not_empty"],
    "description": "Comparison operator"
  },
  "compare_to": {
    "type": "any",
    "required": false,
    "description": "Value to compare against (not needed for is_empty/is_not_empty)"
  },
  "true_value": {
    "type": "any",
    "required": true,
    "description": "Value to output if condition is true"
  },
  "false_value": {
    "type": "any",
    "required": true,
    "description": "Value to output if condition is false"
  }
}
```

**Output Schema**:
```json
{
  "result": {
    "type": "any",
    "description": "Output value from selected branch"
  },
  "branch_taken": {
    "type": "string",
    "enum": ["true", "false"],
    "description": "Which branch was selected"
  },
  "condition_result": {
    "type": "boolean",
    "description": "Actual boolean result of condition evaluation"
  }
}
```

**Behavior Specification**:

**Comparison Logic**:
- `"=="` - Equality (works for strings, numbers, booleans)
- `"!="` - Inequality
- `">"`, `"<"`, `">="`, `"<="` - Numeric comparison (converts strings to numbers if possible)
- `"contains"` - String/list containment (`compare_to in condition`)
- `"not_contains"` - Negated containment
- `"is_empty"` - True if condition is "", [], {}, null, or undefined
- `"is_not_empty"` - Negated is_empty

**Execution Flow**:
1. Evaluate condition using operator and compare_to
2. If condition is true → Return `true_value` with `branch_taken: "true"`
3. If condition is false → Return `false_value` with `branch_taken: "false"`

**Usage Example**:
```json
{
  "nodes": [
    {
      "id": "check_status",
      "type": "IfElseNode",
      "data": {
        "condition": "{{previous_node.status}}",
        "operator": "==",
        "compare_to": "success",
        "true_value": "Deployment succeeded - continuing",
        "false_value": "Deployment failed - aborting"
      }
    }
  ]
}
```

#### `LoopNode`

**Purpose**: Iterate over collection, executing a sub-flow for each item

**Node Type**: `LoopNode`

**Input Schema**:
```json
{
  "items": {
    "type": "array",
    "required": true,
    "description": "Collection to iterate over"
  },
  "sub_flow": {
    "type": "string",
    "required": true,
    "description": "Name of flow to execute for each item (e.g., 'process_item_flow.json')"
  },
  "item_variable_name": {
    "type": "string",
    "required": false,
    "default": "item",
    "description": "Variable name for current item passed to sub-flow"
  },
  "max_iterations": {
    "type": "integer",
    "required": false,
    "default": 1000,
    "description": "Safety limit to prevent infinite loops"
  },
  "parallel": {
    "type": "boolean",
    "required": false,
    "default": false,
    "description": "Execute iterations in parallel (use with caution)"
  }
}
```

**Output Schema**:
```json
{
  "results": {
    "type": "array",
    "description": "Array of sub-flow outputs (one per item)"
  },
  "iterations": {
    "type": "integer",
    "description": "Number of iterations performed"
  },
  "errors": {
    "type": "array",
    "description": "Errors from failed iterations (if any)"
  }
}
```

**Behavior Specification**:

1. **Sequential Execution** (parallel=false):
   - For each item in `items`:
     - Invoke sub-flow with `{item_variable_name: current_item}`
     - Collect output into `results` array
     - If sub-flow raises error → Collect into `errors`, continue (fail-soft)

2. **Parallel Execution** (parallel=true):
   - Spawn async tasks for all items simultaneously
   - Collect results when all complete
   - Timeout individual tasks after 60s (configurable)

3. **Safety Limits**:
   - If `len(items) > max_iterations` → Raise `MaxIterationsExceeded`

**Usage Example**:
```json
{
  "nodes": [
    {
      "id": "process_files",
      "type": "LoopNode",
      "data": {
        "items": ["{{input.file_list}}"],
        "sub_flow": "validate_file_flow.json",
        "item_variable_name": "file_path",
        "max_iterations": 100
      }
    }
  ]
}
```

#### `SwitchNode`

**Purpose**: Multi-way branching (like switch/case statement)

**Node Type**: `SwitchNode`

**Input Schema**:
```json
{
  "value": {
    "type": "any",
    "required": true,
    "description": "Value to switch on"
  },
  "cases": {
    "type": "object",
    "required": true,
    "description": "Map of case values to outputs (keys must be strings)"
  },
  "default": {
    "type": "any",
    "required": false,
    "description": "Default output if no case matches (raises error if not provided and no match)"
  }
}
```

**Output Schema**:
```json
{
  "result": {
    "type": "any",
    "description": "Output value from matched case"
  },
  "case_matched": {
    "type": "string",
    "description": "Which case key was matched ('default' if default used)"
  }
}
```

**Behavior Specification**:

1. Convert `value` to string for comparison
2. Look up `value` in `cases` dictionary
3. If match found → Return corresponding value with `case_matched` set
4. If no match and `default` provided → Return default with `case_matched: "default"`
5. If no match and no default → Raise `NoMatchingCaseError`

**Usage Example**:
```json
{
  "nodes": [
    {
      "id": "route_by_role",
      "type": "SwitchNode",
      "data": {
        "value": "{{input.user_role}}",
        "cases": {
          "admin": "admin_dashboard_flow.json",
          "developer": "dev_workspace_flow.json",
          "viewer": "readonly_view_flow.json"
        },
        "default": "unauthorized_flow.json"
      }
    }
  ]
}
```

---

### 2.3. Data Transformation Nodes

#### `FilterNode`

**Purpose**: Filter collection based on predicate

**Node Type**: `FilterNode`

**Input Schema**:
```json
{
  "items": {
    "type": "array",
    "required": true,
    "description": "Collection to filter"
  },
  "filter_expression": {
    "type": "string",
    "required": true,
    "description": "Python expression to evaluate (truthy = keep item)"
  },
  "item_variable": {
    "type": "string",
    "required": false,
    "default": "x",
    "description": "Variable name for current item in expression"
  }
}
```

**Output Schema**:
```json
{
  "filtered_items": {
    "type": "array",
    "description": "Filtered collection"
  },
  "original_count": {
    "type": "integer",
    "description": "Number of items before filtering"
  },
  "filtered_count": {
    "type": "integer",
    "description": "Number of items after filtering"
  }
}
```

**Behavior Specification**:

1. For each item in `items`:
   - Bind item to `item_variable`
   - Eval `filter_expression` in safe context
   - If result is truthy → Include in output

2. Safe eval context:
   - No access to dangerous builtins (open, exec, eval, etc.)
   - Only allow: len, str, int, float, bool, list, dict, comparison operators

**Usage Example**:
```json
{
  "nodes": [
    {
      "id": "filter_completed",
      "type": "FilterNode",
      "data": {
        "items": "{{input.tasks}}",
        "filter_expression": "x['status'] == 'completed'",
        "item_variable": "x"
      }
    }
  ]
}
```

#### `MergeNode`

**Purpose**: Combine multiple values

**Node Type**: `MergeNode`

**Input Schema**:
```json
{
  "inputs": {
    "type": "array",
    "required": true,
    "description": "Values to merge"
  },
  "strategy": {
    "type": "string",
    "required": true,
    "enum": ["concat", "union", "deep_merge", "sum"],
    "description": "How to merge values"
  }
}
```

**Output Schema**:
```json
{
  "merged": {
    "type": "any",
    "description": "Merged result"
  }
}
```

**Behavior Specification**:

- **`concat`**: Concatenate all inputs (works for strings, lists)
- **`union`**: Set union (deduplicate across all inputs)
- **`deep_merge`**: Deep merge dictionaries (later values override earlier)
- **`sum`**: Numeric sum of all inputs

**Usage Example**:
```json
{
  "nodes": [
    {
      "id": "combine_results",
      "type": "MergeNode",
      "data": {
        "inputs": ["{{node_1.output}}", "{{node_2.output}}", "{{node_3.output}}"],
        "strategy": "concat"
      }
    }
  ]
}
```

#### `TransformNode`

**Purpose**: Apply transformation function to data

**Node Type**: `TransformNode`

**Input Schema**:
```json
{
  "input": {
    "type": "any",
    "required": true,
    "description": "Data to transform"
  },
  "transform": {
    "type": "string",
    "required": true,
    "enum": ["to_upper", "to_lower", "strip", "json_parse", "json_stringify", "length", "keys", "values"],
    "description": "Transformation function to apply"
  }
}
```

**Output Schema**:
```json
{
  "output": {
    "type": "any",
    "description": "Transformed result"
  }
}
```

**Behavior Specification**:

- **`to_upper`**: str.upper()
- **`to_lower`**: str.lower()
- **`strip`**: str.strip()
- **`json_parse`**: json.loads()
- **`json_stringify`**: json.dumps()
- **`length`**: len()
- **`keys`**: dict.keys()
- **`values`**: dict.values()

**Usage Example**:
```json
{
  "nodes": [
    {
      "id": "parse_json_response",
      "type": "TransformNode",
      "data": {
        "input": "{{llm_1.response}}",
        "transform": "json_parse"
      }
    }
  ]
}
```

---

### 2.4. Utility Nodes

#### `LogNode`

**Purpose**: Structured logging within flows

**Node Type**: `LogNode`

**Input Schema**:
```json
{
  "message": {
    "type": "string",
    "required": true,
    "description": "Log message"
  },
  "level": {
    "type": "string",
    "required": false,
    "default": "info",
    "enum": ["debug", "info", "warn", "error"],
    "description": "Log level"
  },
  "context": {
    "type": "object",
    "required": false,
    "description": "Additional structured data"
  }
}
```

**Output Schema**:
```json
{
  "logged": {
    "type": "boolean",
    "description": "True if log was written successfully"
  }
}
```

**Behavior Specification**:

1. Construct structured log entry:
   ```json
   {
     "timestamp": "ISO8601",
     "level": "info",
     "message": "...",
     "context": {...},
     "mad_name": "...",
     "flow_name": "..."
   }
   ```

2. Write to logging backend (via joshua_communicator)

**Usage Example**:
```json
{
  "nodes": [
    {
      "id": "log_deployment",
      "type": "LogNode",
      "data": {
        "message": "Team deployment initiated",
        "level": "info",
        "context": {
          "team_id": "{{team_assembly.team_id}}",
          "role_count": "{{input.roles.length}}"
        }
      }
    }
  ]
}
```

---

## 3. Dependencies

### 3.1. External Packages

```txt
# requirements.txt for joshua_core
python>=3.11
pydantic>=2.0.0         # For input/output validation
subprocess32            # For safe subprocess execution
jsonschema>=4.0.0       # For schema validation
```

### 3.2. Internal Dependencies

- `joshua_communicator>=0.7.0` - For logging infrastructure
- No dependency on other node libraries (joshua_core is the foundation)

---

## 4. Testing Requirements

### 4.1. Unit Tests (per node)

Each node must have:
- Valid input → Expected output tests
- Invalid input → Expected error tests
- Edge cases (empty collections, null values, type mismatches)

**Example Test Structure**:
```python
def test_llm_cli_node_anthropic_success():
    """Test LLMCLINode with Anthropic provider"""
    node = LLMCLINode()
    result = node.execute({
        "prompt": "Say hello",
        "provider": "anthropic",
        "model": "claude-sonnet-4-5"
    })
    assert result["provider_used"] == "anthropic"
    assert "hello" in result["response"].lower()

def test_llm_cli_node_failover_to_sutherland():
    """Test failover when primary provider fails"""
    node = LLMCLINode()
    # Mock primary provider to fail
    with mock_provider_failure("anthropic"):
        result = node.execute({
            "prompt": "Say hello",
            "provider": "anthropic",
            "failover_to_sutherland": True
        })
        assert result["provider_used"] == "sutherland"
```

### 4.2. Integration Tests

- LLMCLINode with actual Sutherland instance
- Flow control nodes in actual flows
- End-to-end flow execution using multiple nodes

---

## 5. Performance Characteristics

| Node Type | Expected Latency | Notes |
|-----------|------------------|-------|
| LLMCLINode | 1-10s | Depends on provider, model, prompt length |
| IfElseNode | < 1ms | Pure logic, no I/O |
| LoopNode | N × sub-flow latency | Linear in number of items |
| SwitchNode | < 1ms | Dictionary lookup |
| FilterNode | O(n) × expression eval | Safe eval adds ~10μs per item |
| MergeNode | O(n) | Depends on strategy |
| TransformNode | < 1ms | Most transforms are O(1) or O(n) |
| LogNode | < 10ms | Async write to log backend |

---

## 6. Implementation Guidance

### 6.1. Node Base Class

All nodes should inherit from `BaseNode`:

```python
from abc import ABC, abstractmethod
from pydantic import BaseModel

class BaseNode(ABC):
    """Base class for all joshua_core nodes"""

    @abstractmethod
    def execute(self, inputs: dict) -> dict:
        """
        Execute the node logic.

        Args:
            inputs: Dictionary matching node's input schema

        Returns:
            Dictionary matching node's output schema

        Raises:
            ValidationError: If inputs don't match schema
            NodeExecutionError: If node execution fails
        """
        pass

    def validate_inputs(self, inputs: dict) -> dict:
        """Validate inputs against schema"""
        # Use pydantic or jsonschema
        pass
```

### 6.2. Langflow Integration

Nodes must be compatible with Langflow's node format:

```python
# Each node should provide:
- display_name: str - Human-readable name
- description: str - What the node does
- input_types: dict - Input schema
- output_types: dict - Output schema
- category: str - "LLM", "Flow Control", "Data Transform", "Utility"
```

---

## 7. Implementation Status

**Current Status**: Detailed specification complete - ready for implementation

**Priority**: CRITICAL - Blocking all MAD development

**Implementation Order**:
1. BaseNode infrastructure + validation
2. Flow control nodes (IfElseNode, LoopNode, SwitchNode) - Most fundamental
3. LLMCLINode - Most complex, highest value
4. Data transformation nodes
5. Utility nodes
6. Comprehensive test suite
7. Langflow integration layer

---

## 8. Related Documentation

- **ADR-036**: Node Library Architecture - Defines three-tier model
- **ADR-035**: Direct Access AI Model Nodes - LLM access pattern
- **ADR-034**: CLI-First LLM Integration Strategy - Why CLIs not APIs
- **ADR-032**: Fully Flow-Based Architecture - How flows use nodes
- **MAD Template**: `/MADs/MAD_Template_V0.7_Requirements.md` - Shows node usage

---

**Last Updated:** 2025-12-22
**Status:** Implementation-ready specification - all nodes fully defined
