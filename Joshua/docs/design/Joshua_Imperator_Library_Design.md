# `joshua_imperator` Library Design Document V2

- **Role**: Core Deliberative Reasoning Component (PCP Tier 4)
- **Version**: 0.7
- **Home**: `lib/joshua_imperator/`
- **Related Requirements**: `joshua_imperator_library_requirements_v2.md`
- **ADR References**: ADR-037 (LangFlow Node Sourcing Strategy), ADR-032 (Flow-Based Architecture)

> **⚠️ FLOW-BASED IMPLEMENTATION**: This design implements Imperator capabilities as LangFlow flows using only native components, per ADR-037's "Use → Compose → Fork → Build" hierarchy.

---

## 1. Design Overview

### 1.1 Architecture Summary

The Imperator library provides **deliberative reasoning capabilities** as **reusable LangFlow flow patterns**. Each pattern demonstrates a specific reasoning strategy using only native LangFlow components.

**Key Principles**:
1. **Flow-First**: All logic in `.json` flow definitions
2. **Native Components**: Language Model, If-Else, Loop, Condition, Prompt Template, Parser, Data Operations
3. **Composable**: Flows can be imported and reused by MADs
4. **Testable**: Each flow has corresponding test flow
5. **Evolvable**: Hamilton monitors → Hopper hardens high-value flows to custom nodes (V0.8+)

### 1.2 System Context

```
┌─────────────────────────────────────────────────────────────────┐
│                  joshua_imperator Library                        │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │         Flow Pattern Library (10 patterns)                 │ │
│  │  • planning_pattern.json                                   │ │
│  │  • critique_pattern.json                                   │ │
│  │  • refinement_pattern.json                                 │ │
│  │  • self_critique_loop_pattern.json                         │ │
│  │  • deep_reasoning_pattern.json                             │ │
│  │  • hypothesis_generation_pattern.json                      │ │
│  │  • evidence_evaluation_pattern.json                        │ │
│  │  • verification_pattern.json                               │ │
│  │  • synthesis_pattern.json                                  │ │
│  │  • explanation_pattern.json                                │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                   │
│  All flows use native LangFlow components (ADR-037)              │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
            │
            │ imported by
            ▼
┌─────────────────────────────────────────────────────────────────┐
│                        MAD Flows                                 │
│  (Hopper, Turing, Grace, etc.)                                   │
│                                                                   │
│  Import Imperator patterns via FlowReference component           │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Detailed Flow Designs

### 2.1 Planning Pattern (`flows/planning_pattern.json`)

**Purpose**: Generate structured plan for solving complex problem

#### 2.1.1 Flow Structure (LangFlow JSON)

```json
{
  "name": "planning_pattern",
  "description": "Generate structured plan with steps, dependencies, success criteria",
  "version": "0.7.0",
  "components": [
    {
      "id": "chat_input_problem",
      "type": "ChatInput",
      "display_name": "Problem Statement",
      "properties": {
        "input_value": "",
        "should_store_message": false
      },
      "position": {"x": 100, "y": 300}
    },
    {
      "id": "text_input_depth",
      "type": "TextInput",
      "display_name": "Planning Depth",
      "properties": {
        "value": "medium"
      },
      "position": {"x": 100, "y": 450}
    },
    {
      "id": "text_input_context",
      "type": "TextInput",
      "display_name": "Context (Optional)",
      "properties": {
        "value": "{}"
      },
      "position": {"x": 100, "y": 600}
    },
    {
      "id": "prompt_template_planning",
      "type": "PromptTemplate",
      "display_name": "Planning Instructions",
      "properties": {
        "template": "You are a deliberative reasoning system generating a structured plan.\n\n**Problem to solve:**\n{problem_statement}\n\n**Planning depth:** {planning_depth}\n- shallow: High-level steps only (3-5 steps)\n- medium: Detailed steps with dependencies (5-10 steps)\n- deep: Comprehensive plan with substeps (10+ steps)\n\n**Additional context:**\n{context}\n\n**Generate a structured plan with:**\n1. **Steps**: Numbered list of actions\n2. **Dependencies**: Which steps depend on others\n3. **Success criteria**: How to know each step succeeded\n4. **Estimated complexity**: Per-step difficulty (low/medium/high)\n5. **Overall confidence**: Your confidence in this plan (0.0-1.0)\n\n**Output as JSON:**\n```json\n{\n  \"steps\": [\n    {\n      \"step_number\": 1,\n      \"description\": \"...\",\n      \"dependencies\": [],\n      \"success_criteria\": \"...\",\n      \"complexity\": \"low|medium|high\"\n    }\n  ],\n  \"overall_complexity\": \"low|medium|high\",\n  \"confidence\": 0.85,\n  \"assumptions\": [\"assumption1\", \"assumption2\"],\n  \"risks\": [\"risk1\", \"risk2\"]\n}\n```",
        "variables": {
          "problem_statement": "",
          "planning_depth": "medium",
          "context": "{}"
        }
      },
      "position": {"x": 400, "y": 300}
    },
    {
      "id": "language_model_planner",
      "type": "LanguageModel",
      "display_name": "Planner LLM",
      "properties": {
        "provider": "anthropic",
        "model": "claude-sonnet-4-5",
        "temperature": 0.5,
        "max_tokens": 3000,
        "api_key": "${ANTHROPIC_API_KEY}"
      },
      "position": {"x": 700, "y": 300}
    },
    {
      "id": "parser_json",
      "type": "Parser",
      "display_name": "Parse Plan JSON",
      "properties": {
        "parser_type": "json",
        "output_type": "Data"
      },
      "position": {"x": 1000, "y": 300}
    },
    {
      "id": "chat_output_plan",
      "type": "ChatOutput",
      "display_name": "Structured Plan",
      "properties": {},
      "position": {"x": 1300, "y": 300}
    }
  ],
  "edges": [
    {
      "source": "chat_input_problem",
      "source_handle": "output",
      "target": "prompt_template_planning",
      "target_handle": "problem_statement"
    },
    {
      "source": "text_input_depth",
      "source_handle": "output",
      "target": "prompt_template_planning",
      "target_handle": "planning_depth"
    },
    {
      "source": "text_input_context",
      "source_handle": "output",
      "target": "prompt_template_planning",
      "target_handle": "context"
    },
    {
      "source": "prompt_template_planning",
      "source_handle": "output",
      "target": "language_model_planner",
      "target_handle": "input"
    },
    {
      "source": "language_model_planner",
      "source_handle": "output",
      "target": "parser_json",
      "target_handle": "input"
    },
    {
      "source": "parser_json",
      "source_handle": "output",
      "target": "chat_output_plan",
      "target_handle": "input"
    }
  ],
  "flow_inputs": {
    "problem_statement": {"type": "str", "required": true},
    "planning_depth": {"type": "str", "default": "medium", "enum": ["shallow", "medium", "deep"]},
    "context": {"type": "dict", "default": {}}
  },
  "flow_outputs": {
    "plan": {"type": "Data", "description": "Structured plan with steps, dependencies, criteria"},
    "confidence": {"type": "float", "description": "Plan quality confidence (0.0-1.0)"}
  }
}
```

#### 2.1.2 Example Execution

**Input**:
```json
{
  "problem_statement": "Implement user authentication for web application",
  "planning_depth": "medium",
  "context": {
    "tech_stack": "Python, Flask, PostgreSQL",
    "constraints": "Must support OAuth2, GDPR compliant"
  }
}
```

**Output** (parsed JSON from LLM):
```json
{
  "steps": [
    {
      "step_number": 1,
      "description": "Design database schema for users, sessions, OAuth tokens",
      "dependencies": [],
      "success_criteria": "Schema validated, migrations created",
      "complexity": "medium"
    },
    {
      "step_number": 2,
      "description": "Implement OAuth2 provider integration (Google, GitHub)",
      "dependencies": [1],
      "success_criteria": "OAuth flow completes, tokens stored securely",
      "complexity": "high"
    },
    {
      "step_number": 3,
      "description": "Implement session management with secure cookies",
      "dependencies": [1],
      "success_criteria": "Sessions persist, CSRF protection active",
      "complexity": "medium"
    },
    {
      "step_number": 4,
      "description": "Add GDPR-compliant consent tracking",
      "dependencies": [1, 2],
      "success_criteria": "User can view/revoke consent, audit log complete",
      "complexity": "medium"
    },
    {
      "step_number": 5,
      "description": "Write integration tests for auth flows",
      "dependencies": [2, 3, 4],
      "success_criteria": "All auth scenarios covered, tests pass",
      "complexity": "medium"
    }
  ],
  "overall_complexity": "medium",
  "confidence": 0.82,
  "assumptions": [
    "OAuth providers remain stable",
    "PostgreSQL supports required session features"
  ],
  "risks": [
    "OAuth provider changes may break integration",
    "GDPR requirements may expand"
  ]
}
```

---

### 2.2 Critique Pattern (`flows/critique_pattern.json`)

**Purpose**: Critically evaluate plan, solution, or artifact

#### 2.2.1 Flow Structure (LangFlow JSON)

```json
{
  "name": "critique_pattern",
  "description": "Critical evaluation of artifact with structured feedback",
  "version": "0.7.0",
  "components": [
    {
      "id": "text_input_artifact",
      "type": "TextInput",
      "display_name": "Artifact to Critique",
      "properties": {"value": ""},
      "position": {"x": 100, "y": 200}
    },
    {
      "id": "chat_input_problem",
      "type": "ChatInput",
      "display_name": "Original Problem",
      "properties": {},
      "position": {"x": 100, "y": 350}
    },
    {
      "id": "text_input_focus",
      "type": "TextInput",
      "display_name": "Critique Focus (Optional)",
      "properties": {"value": "correctness,completeness,efficiency"},
      "position": {"x": 100, "y": 500}
    },
    {
      "id": "prompt_template_critique",
      "type": "PromptTemplate",
      "display_name": "Critique Instructions",
      "properties": {
        "template": "You are a critical evaluator reviewing an artifact.\n\n**Original problem:**\n{original_problem}\n\n**Artifact to critique:**\n{artifact}\n\n**Evaluation focus:**\n{critique_focus}\n\n**Provide structured critique:**\n1. **Issues identified**: List specific problems, gaps, errors\n2. **Severity**: Rate each issue (critical/major/minor)\n3. **Suggestions**: Actionable improvement recommendations\n4. **Overall score**: Quality rating 0.0-1.0\n5. **Needs refinement**: Boolean - does this require more work?\n\n**Output as JSON:**\n```json\n{\n  \"issues\": [\n    {\n      \"description\": \"...\",\n      \"severity\": \"critical|major|minor\",\n      \"suggestion\": \"...\"\n    }\n  ],\n  \"overall_score\": 0.75,\n  \"needs_refinement\": true,\n  \"strengths\": [\"strength1\", \"strength2\"],\n  \"weaknesses\": [\"weakness1\", \"weakness2\"]\n}\n```",
        "variables": {
          "artifact": "",
          "original_problem": "",
          "critique_focus": "correctness,completeness,efficiency"
        }
      },
      "position": {"x": 400, "y": 300}
    },
    {
      "id": "language_model_critic",
      "type": "LanguageModel",
      "display_name": "Critic LLM",
      "properties": {
        "provider": "anthropic",
        "model": "claude-sonnet-4-5",
        "temperature": 0.3,
        "max_tokens": 2000
      },
      "position": {"x": 700, "y": 300}
    },
    {
      "id": "parser_critique",
      "type": "Parser",
      "display_name": "Parse Critique JSON",
      "properties": {
        "parser_type": "json",
        "output_type": "Data"
      },
      "position": {"x": 1000, "y": 300}
    },
    {
      "id": "condition_needs_refinement",
      "type": "Condition",
      "display_name": "Check Refinement Need",
      "properties": {
        "data": "",
        "key": "overall_score",
        "validation": "less_than",
        "value": 0.9
      },
      "position": {"x": 1300, "y": 300}
    },
    {
      "id": "chat_output_critique",
      "type": "ChatOutput",
      "display_name": "Critique Result",
      "properties": {},
      "position": {"x": 1600, "y": 300}
    }
  ],
  "edges": [
    {
      "source": "text_input_artifact",
      "target": "prompt_template_critique",
      "target_handle": "artifact"
    },
    {
      "source": "chat_input_problem",
      "target": "prompt_template_critique",
      "target_handle": "original_problem"
    },
    {
      "source": "text_input_focus",
      "target": "prompt_template_critique",
      "target_handle": "critique_focus"
    },
    {
      "source": "prompt_template_critique",
      "target": "language_model_critic"
    },
    {
      "source": "language_model_critic",
      "target": "parser_critique"
    },
    {
      "source": "parser_critique",
      "target": "condition_needs_refinement",
      "target_handle": "data"
    },
    {
      "source": "condition_needs_refinement",
      "source_handle": "true_output",
      "target": "chat_output_critique",
      "target_handle": "input",
      "label": "needs_refinement=true"
    },
    {
      "source": "condition_needs_refinement",
      "source_handle": "false_output",
      "target": "chat_output_critique",
      "target_handle": "input",
      "label": "needs_refinement=false"
    }
  ],
  "flow_inputs": {
    "artifact": {"type": "str", "required": true},
    "original_problem": {"type": "str", "required": true},
    "critique_focus": {"type": "str", "default": "correctness,completeness,efficiency"}
  },
  "flow_outputs": {
    "critique": {"type": "Data"},
    "needs_refinement": {"type": "bool"}
  }
}
```

#### 2.2.2 Example Critique Output

```json
{
  "issues": [
    {
      "description": "No error handling for OAuth provider failures",
      "severity": "critical",
      "suggestion": "Add try/catch with fallback to local auth"
    },
    {
      "description": "Password hashing algorithm not specified",
      "severity": "major",
      "suggestion": "Use bcrypt with 12 rounds minimum"
    },
    {
      "description": "Session timeout not configurable",
      "severity": "minor",
      "suggestion": "Make timeout a config parameter"
    }
  ],
  "overall_score": 0.68,
  "needs_refinement": true,
  "strengths": [
    "OAuth integration plan is comprehensive",
    "GDPR compliance considered early"
  ],
  "weaknesses": [
    "Insufficient error handling",
    "Security details incomplete"
  ]
}
```

---

### 2.3 Self-Critique Loop Pattern (`flows/self_critique_loop_pattern.json`)

**Purpose**: Canonical "Plan → Critique → Refine" iterative improvement pattern

#### 2.3.1 Flow Structure (LangFlow JSON)

```json
{
  "name": "self_critique_loop_pattern",
  "description": "Iterative plan generation, critique, and refinement",
  "version": "0.7.0",
  "components": [
    {
      "id": "chat_input_problem",
      "type": "ChatInput",
      "display_name": "Problem to Solve",
      "position": {"x": 100, "y": 400}
    },
    {
      "id": "text_input_max_iterations",
      "type": "TextInput",
      "display_name": "Max Iterations",
      "properties": {"value": "3"},
      "position": {"x": 100, "y": 550}
    },
    {
      "id": "text_input_threshold",
      "type": "TextInput",
      "display_name": "Quality Threshold",
      "properties": {"value": "0.9"},
      "position": {"x": 100, "y": 700}
    },
    {
      "id": "prompt_template_initial_plan",
      "type": "PromptTemplate",
      "display_name": "Initial Planning",
      "properties": {
        "template": "Generate initial plan for:\n\n{problem}\n\nOutput structured plan as JSON.",
        "variables": {"problem": ""}
      },
      "position": {"x": 400, "y": 300}
    },
    {
      "id": "language_model_planner",
      "type": "LanguageModel",
      "display_name": "Plan Generator",
      "properties": {
        "provider": "anthropic",
        "model": "claude-sonnet-4-5",
        "temperature": 0.5,
        "max_tokens": 2000
      },
      "position": {"x": 700, "y": 300}
    },
    {
      "id": "parser_plan",
      "type": "Parser",
      "display_name": "Parse Plan",
      "properties": {"parser_type": "json", "output_type": "Data"},
      "position": {"x": 1000, "y": 300}
    },
    {
      "id": "loop_refinement",
      "type": "Loop",
      "display_name": "Refinement Iterations",
      "properties": {
        "inputs": "",
        "max_iterations": 3,
        "extract_key": "plan"
      },
      "position": {"x": 1300, "y": 400}
    },
    {
      "id": "prompt_template_critique",
      "type": "PromptTemplate",
      "display_name": "Critique Current Plan",
      "properties": {
        "template": "Critique this plan:\n\n{current_plan}\n\nOriginal problem:\n{problem}\n\nOutput critique as JSON with score.",
        "variables": {"current_plan": "", "problem": ""}
      },
      "position": {"x": 1600, "y": 300}
    },
    {
      "id": "language_model_critic",
      "type": "LanguageModel",
      "display_name": "Critic",
      "properties": {
        "provider": "anthropic",
        "model": "claude-sonnet-4-5",
        "temperature": 0.3,
        "max_tokens": 1500
      },
      "position": {"x": 1900, "y": 300}
    },
    {
      "id": "parser_critique",
      "type": "Parser",
      "display_name": "Parse Critique",
      "properties": {"parser_type": "json", "output_type": "Data"},
      "position": {"x": 2200, "y": 300}
    },
    {
      "id": "condition_quality_check",
      "type": "Condition",
      "display_name": "Quality Threshold Met?",
      "properties": {
        "data": "",
        "key": "overall_score",
        "validation": "greater_than_or_equal",
        "value": 0.9
      },
      "position": {"x": 2500, "y": 400}
    },
    {
      "id": "prompt_template_refine",
      "type": "PromptTemplate",
      "display_name": "Refine Plan",
      "properties": {
        "template": "Refine this plan based on critique:\n\nCurrent plan:\n{current_plan}\n\nCritique:\n{critique}\n\nOutput improved plan as JSON.",
        "variables": {"current_plan": "", "critique": ""}
      },
      "position": {"x": 2800, "y": 600}
    },
    {
      "id": "language_model_refiner",
      "type": "LanguageModel",
      "display_name": "Plan Refiner",
      "properties": {
        "provider": "anthropic",
        "model": "claude-sonnet-4-5",
        "temperature": 0.4,
        "max_tokens": 2000
      },
      "position": {"x": 3100, "y": 600}
    },
    {
      "id": "parser_refined_plan",
      "type": "Parser",
      "display_name": "Parse Refined Plan",
      "properties": {"parser_type": "json", "output_type": "Data"},
      "position": {"x": 3400, "y": 600}
    },
    {
      "id": "data_operations_history",
      "type": "DataOperations",
      "display_name": "Accumulate History",
      "properties": {
        "operation": "append_to_list",
        "list_key": "iteration_history"
      },
      "position": {"x": 1600, "y": 700}
    },
    {
      "id": "chat_output_final",
      "type": "ChatOutput",
      "display_name": "Final Solution",
      "position": {"x": 2800, "y": 200}
    }
  ],
  "edges": [
    {
      "source": "chat_input_problem",
      "target": "prompt_template_initial_plan",
      "target_handle": "problem"
    },
    {
      "source": "prompt_template_initial_plan",
      "target": "language_model_planner"
    },
    {
      "source": "language_model_planner",
      "target": "parser_plan"
    },
    {
      "source": "parser_plan",
      "target": "loop_refinement",
      "target_handle": "inputs"
    },
    {
      "source": "loop_refinement",
      "source_handle": "item_output",
      "target": "prompt_template_critique",
      "target_handle": "current_plan"
    },
    {
      "source": "chat_input_problem",
      "target": "prompt_template_critique",
      "target_handle": "problem"
    },
    {
      "source": "prompt_template_critique",
      "target": "language_model_critic"
    },
    {
      "source": "language_model_critic",
      "target": "parser_critique"
    },
    {
      "source": "parser_critique",
      "target": "condition_quality_check",
      "target_handle": "data"
    },
    {
      "source": "condition_quality_check",
      "source_handle": "true_output",
      "target": "chat_output_final",
      "label": "accept_plan"
    },
    {
      "source": "condition_quality_check",
      "source_handle": "false_output",
      "target": "prompt_template_refine",
      "target_handle": "critique"
    },
    {
      "source": "loop_refinement",
      "source_handle": "item_output",
      "target": "prompt_template_refine",
      "target_handle": "current_plan"
    },
    {
      "source": "prompt_template_refine",
      "target": "language_model_refiner"
    },
    {
      "source": "language_model_refiner",
      "target": "parser_refined_plan"
    },
    {
      "source": "parser_refined_plan",
      "target": "loop_refinement",
      "target_handle": "item_result"
    },
    {
      "source": "parser_critique",
      "target": "data_operations_history",
      "target_handle": "item_to_append"
    },
    {
      "source": "loop_refinement",
      "source_handle": "done_output",
      "target": "chat_output_final"
    }
  ],
  "flow_inputs": {
    "problem": {"type": "str", "required": true},
    "max_iterations": {"type": "int", "default": 3},
    "quality_threshold": {"type": "float", "default": 0.9}
  },
  "flow_outputs": {
    "final_solution": {"type": "Data"},
    "iteration_history": {"type": "List[Data]"},
    "final_critique": {"type": "Data"}
  }
}
```

#### 2.3.2 Execution Flow Diagram

```
Problem Input
    ↓
Generate Initial Plan (LLM)
    ↓
Enter Loop (max 3 iterations):
    ↓
    Critique Current Plan (LLM)
    ↓
    Check Quality Score >= 0.9?
    ├─ YES → Exit loop, return plan ✓
    └─ NO → Continue
        ↓
        Refine Plan Based on Critique (LLM)
        ↓
        Loop back with refined plan
    ↓
Max Iterations Reached → Return best plan
```

---

### 2.4 Deep Reasoning Pattern (`flows/deep_reasoning_pattern.json`)

**Purpose**: Chain-of-thought reasoning with early stopping

#### 2.4.1 Flow Structure Summary

```json
{
  "name": "deep_reasoning_pattern",
  "description": "Extended step-by-step reasoning with confidence-based early stopping",
  "version": "0.7.0",
  "components": [
    {"type": "ChatInput", "id": "problem_input"},
    {"type": "PromptTemplate", "id": "chain_of_thought_template"},
    {"type": "Loop", "id": "reasoning_loop", "max_iterations": 10},
    {"type": "LanguageModel", "id": "reasoning_llm"},
    {"type": "Parser", "id": "parse_reasoning_step"},
    {"type": "Condition", "id": "confidence_check"},
    {"type": "DataOperations", "id": "accumulate_trace"},
    {"type": "LanguageModel", "id": "synthesize_conclusion"},
    {"type": "ChatOutput", "id": "final_output"}
  ],
  "flow_logic": "Loop generates reasoning steps → Check confidence → Exit early if high → Otherwise continue → Synthesize final conclusion"
}
```

**Key Pattern**: Loop component with Condition for early stopping based on confidence threshold.

---

### 2.5 Hypothesis Generation Pattern (`flows/hypothesis_generation_pattern.json`)

**Purpose**: Generate multiple diverse alternative solutions

#### 2.5.1 Flow Structure Summary

```json
{
  "name": "hypothesis_generation_pattern",
  "description": "Generate N diverse hypotheses with rationale",
  "version": "0.7.0",
  "components": [
    {"type": "ChatInput", "id": "problem_input"},
    {"type": "TextInput", "id": "num_hypotheses", "default": "3"},
    {"type": "TextInput", "id": "diversity_factor", "default": "0.7"},
    {"type": "Loop", "id": "hypothesis_loop", "max_iterations": "{num_hypotheses}"},
    {"type": "PromptTemplate", "id": "generate_hypothesis_template"},
    {"type": "LanguageModel", "id": "hypothesis_generator", "temperature": "{diversity_factor}"},
    {"type": "Parser", "id": "parse_hypothesis"},
    {"type": "DataOperations", "id": "accumulate_hypotheses"},
    {"type": "LanguageModel", "id": "suggest_criteria"},
    {"type": "ChatOutput", "id": "hypotheses_output"}
  ],
  "flow_logic": "Loop N times → Each iteration generates unique hypothesis (high temperature for diversity) → Accumulate → Suggest evaluation criteria"
}
```

**Key Insight**: Use higher temperature (diversity_factor) to generate diverse alternatives.

---

## 3. Integration with MADs

### 3.1 Importing Flows via FlowReference

MADs import Imperator flows using LangFlow's **FlowReference** component:

**Example**: Hopper MAD uses self-critique loop for code generation

```json
{
  "name": "hopper_generate_code",
  "description": "Hopper MAD code generation with Imperator self-critique",
  "components": [
    {
      "id": "chat_input_1",
      "type": "ChatInput",
      "display_name": "Code Generation Task"
    },
    {
      "id": "imperator_self_critique",
      "type": "FlowReference",
      "display_name": "Self-Critique Loop (Imperator)",
      "properties": {
        "flow_path": "lib/joshua_imperator/flows/self_critique_loop_pattern.json",
        "inputs_mapping": {
          "problem": "{code_generation_task}",
          "max_iterations": 3,
          "quality_threshold": 0.95
        }
      }
    },
    {
      "id": "chat_output_1",
      "type": "ChatOutput",
      "display_name": "Generated Code"
    }
  ],
  "edges": [
    {
      "source": "chat_input_1",
      "target": "imperator_self_critique",
      "target_handle": "problem"
    },
    {
      "source": "imperator_self_critique",
      "target": "chat_output_1"
    }
  ]
}
```

**Benefits**:
- Reusable reasoning pattern
- Hopper doesn't reimplement self-critique logic
- Updates to Imperator flows propagate to all MADs

---

## 4. Testing Implementation

### 4.1 Test Flow Example (`test_flows/test_planning_pattern.json`)

```json
{
  "name": "test_planning_pattern",
  "description": "Automated test for planning_pattern.json",
  "test_type": "integration",
  "target_flow": "../flows/planning_pattern.json",
  "test_cases": [
    {
      "name": "simple_problem_shallow_plan",
      "inputs": {
        "problem_statement": "Sort a list of numbers",
        "planning_depth": "shallow",
        "context": {}
      },
      "assertions": [
        {
          "type": "json_valid",
          "field": "plan",
          "description": "Plan should be valid JSON"
        },
        {
          "type": "has_key",
          "field": "plan",
          "key": "steps",
          "description": "Plan must have steps array"
        },
        {
          "type": "list_length_range",
          "field": "plan.steps",
          "min": 2,
          "max": 6,
          "description": "Shallow plan should have 2-6 steps"
        },
        {
          "type": "range",
          "field": "plan.confidence",
          "min": 0.0,
          "max": 1.0,
          "description": "Confidence must be 0-1"
        }
      ],
      "expected_latency_ms": 5000
    },
    {
      "name": "complex_problem_deep_plan",
      "inputs": {
        "problem_statement": "Build distributed microservices architecture",
        "planning_depth": "deep",
        "context": {
          "tech_stack": "Kubernetes, gRPC, PostgreSQL",
          "team_size": 5
        }
      },
      "assertions": [
        {
          "type": "list_length_range",
          "field": "plan.steps",
          "min": 10,
          "max": 20,
          "description": "Deep plan should have 10+ steps"
        },
        {
          "type": "has_key",
          "field": "plan",
          "key": "assumptions",
          "description": "Deep plan should identify assumptions"
        }
      ]
    }
  ]
}
```

### 4.2 Integration Test (Python)

```python
# tests/test_imperator_flows.py
import pytest
import json
from pathlib import Path
from joshua_flow_runner import FlowRunner

@pytest.fixture
def flow_runner():
    """Create FlowRunner for Imperator flows"""
    flows_dir = Path(__file__).parent.parent / "flows"
    runner = FlowRunner(
        mad_name="imperator",
        flows_directory=flows_dir
    )
    return runner

@pytest.mark.asyncio
async def test_planning_pattern_execution(flow_runner):
    """Test planning pattern generates valid structured plan"""
    result = await flow_runner.execute_flow(
        "planning_pattern.json",
        {
            "problem_statement": "Implement caching layer",
            "planning_depth": "medium"
        }
    )

    assert "plan" in result
    assert "steps" in result["plan"]
    assert len(result["plan"]["steps"]) >= 3
    assert "confidence" in result["plan"]
    assert 0.0 <= result["plan"]["confidence"] <= 1.0

@pytest.mark.asyncio
async def test_self_critique_loop_convergence(flow_runner):
    """Test self-critique loop improves plan quality"""
    result = await flow_runner.execute_flow(
        "self_critique_loop_pattern.json",
        {
            "problem": "Design REST API",
            "max_iterations": 3,
            "quality_threshold": 0.9
        }
    )

    assert "final_solution" in result
    assert "iteration_history" in result
    assert len(result["iteration_history"]) <= 3

    # Final critique should show improvement
    final_critique = result["final_critique"]
    assert final_critique["overall_score"] >= 0.85

@pytest.mark.asyncio
async def test_deep_reasoning_early_stopping(flow_runner):
    """Test deep reasoning stops early when confidence threshold met"""
    result = await flow_runner.execute_flow(
        "deep_reasoning_pattern.json",
        {
            "problem": "Explain binary search",
            "max_steps": 10,
            "early_stop_confidence": 0.95
        }
    )

    assert "reasoning_trace" in result
    assert "steps_used" in result
    # Should stop before max steps for simple problem
    assert result["steps_used"] < 10
    assert result["confidence"] >= 0.95
```

---

## 5. Deployment

### 5.1 Package Structure

```
lib/joshua_imperator/
├── __init__.py                          # Version, metadata
├── flows/                               # Production flow patterns
│   ├── planning_pattern.json
│   ├── critique_pattern.json
│   ├── refinement_pattern.json
│   ├── self_critique_loop_pattern.json
│   ├── deep_reasoning_pattern.json
│   ├── hypothesis_generation_pattern.json
│   ├── evidence_evaluation_pattern.json
│   ├── verification_pattern.json
│   ├── synthesis_pattern.json
│   └── explanation_pattern.json
├── test_flows/                          # Test flows
│   ├── test_planning_pattern.json
│   ├── test_critique_pattern.json
│   ├── test_self_critique_loop.json
│   └── ...
├── docs/                                # Documentation
│   ├── README.md
│   ├── patterns_guide.md                # When to use each pattern
│   ├── composition_examples.md          # Combining patterns
│   ├── failover_strategies.md           # Degradation approaches
│   └── pattern_catalog.md               # Visual catalog
├── tests/                               # Python integration tests
│   ├── __init__.py
│   ├── test_flow_execution.py
│   ├── test_pattern_equivalence.py
│   └── test_failover.py
├── requirements.txt                     # Dependencies
├── setup.py                             # Package installation
└── pyproject.toml                       # Modern Python packaging
```

### 5.2 requirements.txt

```txt
# Flow Execution
joshua_flow_runner>=0.7.0         # LangFlow flow executor
langflow>=1.5.0                   # LangFlow runtime

# LLM Providers
anthropic>=0.40.0                 # Language Model (Anthropic)

# Data Validation
pydantic>=2.0.0                   # Type safety
pyyaml>=6.0.0                     # Config parsing

# Testing
pytest>=7.0.0
pytest-asyncio>=0.21.0
```

### 5.3 Installation

```bash
# Install from source
cd lib/joshua_imperator
pip install -e .

# Install from PyPI (future)
pip install joshua-imperator>=0.7.0
```

### 5.4 Usage in MAD

```python
# In MAD's requirements.txt
joshua_imperator>=0.7.0

# In MAD's flow definitions, reference Imperator flows
# via FlowReference component (see section 3.1)
```

---

## 6. Performance Characteristics

### 6.1 Expected Latency (Baseline V0.7)

| Flow Pattern | Typical Input | LLM Calls | P50 Latency | P95 Latency |
|--------------|---------------|-----------|-------------|-------------|
| planning | Medium problem | 1 | 3s | 8s |
| critique | Medium artifact | 1 | 2s | 6s |
| refinement | Medium artifact | 1 | 3s | 7s |
| self_critique_loop | 3 iterations | 7 (plan + 3×critique + 3×refine) | 25s | 60s |
| deep_reasoning | 5 steps avg | 6 (5 steps + synthesis) | 15s | 30s |
| hypothesis_generation | 3 hypotheses | 4 (3 hypotheses + criteria) | 12s | 25s |
| evidence_evaluation | 3 options | 4 (3 evals + recommendation) | 10s | 20s |
| verification | Simple solution | 1 | 2s | 5s |
| synthesis | 3 sources | 2 (extract + synthesize) | 5s | 12s |
| explanation | Medium artifact | 2 (explain + examples) | 4s | 10s |

**Notes**:
- Baseline flow-based implementation (overhead from LangFlow flow execution)
- V0.8+ optimized nodes will reduce latency 30-50% for high-usage patterns
- Latency depends on LLM provider response time (Anthropic Claude)

### 6.2 Token Usage Estimates

| Flow Pattern | Avg Input Tokens | Avg Output Tokens | Total Tokens/Call |
|--------------|------------------|-------------------|-------------------|
| planning | 500 | 1200 | 1700 |
| critique | 800 | 600 | 1400 |
| self_critique_loop | 2000 | 3000 | 5000 (cumulative) |
| deep_reasoning | 400 | 2500 | 2900 (cumulative) |

---

## 7. Failover Strategies

### 7.1 Per-Pattern Degradation

Each flow decides how to handle Anthropic unavailability:

**Critical Patterns** (require frontier LLMs):
- `deep_reasoning_pattern` - Fail gracefully, return "Requires frontier LLM"
- `self_critique_loop_pattern` - Fail, too complex for small models

**Degradable Patterns** (can use Ollama):
- `planning_pattern` - Switch to Language Model (Ollama), use simpler prompts
- `critique_pattern` - Degrade to basic validation checks
- `synthesis_pattern` - Use Ollama with reduced context window

**Implementation Example** (planning with failover):

```json
{
  "components": [
    {
      "id": "language_model_primary",
      "type": "LanguageModel",
      "properties": {"provider": "anthropic", "on_error": "return_error"}
    },
    {
      "id": "condition_check_error",
      "type": "Condition",
      "properties": {"key": "error", "validation": "exists"}
    },
    {
      "id": "language_model_fallback",
      "type": "LanguageModel",
      "properties": {
        "provider": "ollama",
        "base_url": "http://sutherland-mad:11434",
        "model": "phi3:mini"
      }
    }
  ],
  "edges": [
    {"source": "language_model_primary", "target": "condition_check_error"},
    {"source": "condition_check_error", "source_handle": "true_output", "target": "language_model_fallback"},
    {"source": "condition_check_error", "source_handle": "false_output", "target": "chat_output"}
  ]
}
```

---

## 8. Validation Against ADR-037

### 8.1 Tier 1: USE (Native Components) ✓

**All flows use native LangFlow components**:
- Language Model (Anthropic, Ollama)
- Prompt Template
- If-Else, Condition
- Loop
- Parser
- Data Operations
- Chat Input/Output, Text Input

**Zero custom nodes in V0.7**.

### 8.2 Tier 1.5: COMPOSE (Flow-First MVPs) ✓

**10 deliberative reasoning patterns** delivered as flows:
- planning, critique, refinement, self-critique loop, deep reasoning, hypothesis generation, evidence evaluation, verification, synthesis, explanation

**Production-ready** in weeks (vs. months for custom nodes).

### 8.3 Tier 2.5: FORK (Future V0.8+)

**When Hamilton data shows need**, fork LangFlow components:
- Fork Loop → `ImperatorRefinementLoop` (optimized for self-critique pattern)
- Fork Language Model → `ImperatorReasoningLLM` (optimized prompts, caching)

**Inherit 90%**, add Joshua-specific optimizations.

---

## 9. Component Evolution Path

### V0.7: Flow-Based MVPs (Current)
- Deploy all 10 patterns as flows
- Hamilton monitoring begins
- Baseline performance

### V0.8: Data-Driven Hardening
- Hamilton identifies: `self_critique_loop_pattern` called 2000×/day, P95 latency 60s
- Hopper receives: `harden_flow` task for self-critique loop
- Hopper metaprograms: `SelfCritiqueLoopNode` custom component
- Result: 40% latency reduction (25s P95)

### V0.9: Hybrid Library
- 3-4 patterns as optimized custom nodes (self-critique, deep reasoning, planning)
- 6-7 patterns remain as flows (flexibility)
- Developers choose: flow (flexible) vs. node (performant)

### V5.0: Full PCP Integration
- Imperator integrates with DTR, LPPM, CET, CRS
- Cognitive fast paths
- Learned prompt optimization

---

## 10. Success Metrics

### 10.1 Deliverable Completeness

- ✅ 10 flow patterns implemented
- ✅ 10 test flows with assertions
- ✅ Integration tests (Python)
- ✅ Documentation (pattern guide, composition examples)
- ✅ Zero custom nodes (validates ADR-037)

### 10.2 Functional Validation

- ✅ All flows execute successfully with valid inputs
- ✅ Graceful error handling on invalid inputs
- ✅ Failover to Ollama works (tested patterns)
- ✅ Pattern equivalence: V0.7 flows ≈ V0.6 imperative code

### 10.3 Adoption Metrics (Target)

- ✅ At least 3 MADs import Imperator flows (Hopper, Turing, Grace)
- ✅ self_critique_loop used by 5+ MADs
- ✅ Hamilton collecting usage data for all patterns

---

## 11. Related Documentation

- **Requirements**: `joshua_imperator_library_requirements_v2.md`
- **ADR-037**: LangFlow Node Sourcing Strategy
- **ADR-032**: Fully Flow-Based Architecture
- **Template MAD**: Reference implementation for flow patterns
- **LangFlow Docs**: https://docs.langflow.org/

---

**Last Updated:** 2025-12-22
**Status:** Ready for Implementation
**Total Estimated Development Time**: 2-3 weeks (flow assembly + testing + docs)
**Compared to Custom Nodes**: 8-12 weeks saved by using native components
