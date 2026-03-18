# `joshua_imperator` Library Requirements V2

- **Role**: Core Deliberative Reasoning Component (PCP Tier 4)
- **Version**: 0.7
- **Home**: `lib/joshua_imperator/`
- **ADR References**: ADR-031 (Modular PCP), ADR-032 (Flow-Based Architecture), **ADR-037 (LangFlow Node Sourcing Strategy)**

---

## Implementation Strategy Update (2025-12-22)

**This document reflects the ADR-037 strategy: Use → Compose → Fork → Build**

**Key Architectural Shift:**
- **V0.7 Baseline**: Implement Imperator capabilities as **LangFlow flows** using native components (Language Model, If-Else, Loop, MCP Tools, etc.)
- **V0.8+ Evolution**: Based on Hamilton monitoring data, harden frequently-used flows into custom nodes via Hopper metaprogramming
- **Component Evolution**: Accept flow-based MVPs, monitor performance, harden only when data justifies it

**Why This Approach:**
1. **Native LangFlow components** already provide: LLM access, conditionals, loops, data operations, MCP integration
2. **Zero custom development** needed for baseline deliberative reasoning
3. **Faster delivery**: Flows assembled in hours/days vs. weeks of custom node development
4. **Data-driven hardening**: Hamilton monitors which flows are bottlenecks → Hopper optimizes those
5. **Validates architecture**: Proves deliberative reasoning works with native components before building custom ones

**Previous Document Status:**
- The original `joshua_imperator_library_requirements.md` specified 12 custom nodes to build
- **Most are now flow patterns** using native LangFlow Language Model components
- **A few may become custom nodes** if data shows they're performance-critical or highly reused

**See ADR-037** for complete sourcing hierarchy and Component Evolution Lifecycle.

---

## 1. Overview

### 1.1 Purpose

The `joshua_imperator` library provides **core deliberative reasoning capabilities** for the Joshua ecosystem. It represents Tier 4 of the Progressive Cognitive Pipeline (PCP) - deep, multi-step reasoning for complex problems.

**Architectural Approach (V0.7):**
- Deliver capabilities as **reusable LangFlow flows** (not custom nodes initially)
- Use native LangFlow components (Language Model, If-Else, Loop, Prompt Template, etc.)
- Accept flow-based MVPs, harden to nodes only when Hamilton monitoring justifies it

### 1.2 Scope

**In Scope (V0.7):**
- Reference flow patterns demonstrating deliberative reasoning capabilities
- Flow implementations for: planning, critique, refinement, hypothesis generation, verification
- Integration with native LangFlow components (Language Model, MCP Tools, etc.)
- Documentation of reasoning patterns and when to use them

**Out of Scope (V0.7):**
- Custom node implementations (defer to V0.8+ based on performance data)
- Direct LLM API integration (use native Language Model components instead)
- Optimized performance (accept flow overhead, optimize in V0.8+ if needed)

---

## 2. Architectural Principles

### 2.1 Flow-First Strategy (ADR-037 Tier 1.5: COMPOSE)

1. **Flows Before Nodes**: All deliberative reasoning patterns start as `.json` flows
2. **Native Components**: Use LangFlow's Language Model, If-Else, Loop, MCP Tools, etc.
3. **Hamilton Monitoring**: Track flow usage, latency, reusability
4. **Data-Driven Hardening**: Hopper converts high-value flows to optimized nodes only when justified

### 2.2 Composition Patterns

Imperator flows compose native LangFlow components:
- **Language Model** (Anthropic) - Primary reasoning
- **Language Model** (Ollama) - Failover via Sutherland
- **Prompt Template** - Inject reasoning instructions
- **If-Else / Condition** - Decision branching
- **Loop** - Iterative refinement
- **MCP Tools** - Call other MADs (e.g., Fiedler for model recommendations)
- **Data Operations** - Aggregate results

### 2.3 Stateless Flows

- Flows are stateless (all state explicitly passed via inputs)
- No hidden state between flow invocations
- External state management delegated to CET (future)

### 2.4 Intellectual Capital Preservation

Previous Imperator reasoning patterns (Plan → Critique → Refine) preserved as:
- Reference flow patterns (`imperator_self_critique_pattern.json`)
- Comprehensive documentation explaining rationale
- Test flows validating behavior

---

## 3. Core Deliberative Reasoning Patterns

Instead of custom nodes, Imperator provides **reference flow patterns** implementing deliberative reasoning.

### 3.1 Planning Pattern (`flows/planning_pattern.json`)

**Purpose**: Generate structured plan for complex problem

**Flow Structure**:
```
Chat Input (problem_statement)
    ↓
Prompt Template (planning_instructions + problem)
    ↓
Language Model (Anthropic) → Generate plan with steps, dependencies, success criteria
    ↓
Parser → Structure as JSON
    ↓
Chat Output (structured_plan)
```

**Native Components Used**:
- Chat Input, Prompt Template, Language Model, Parser, Chat Output

**Inputs**:
- `problem_statement` (str): Problem to plan
- `planning_depth` (enum: "shallow", "medium", "deep"): Detail level
- `context` (dict, optional): Constraints, prior attempts

**Outputs**:
- `plan` (dict): Structured plan with steps, dependencies, criteria
- `confidence` (float): Plan quality estimate

**Failover**: If Anthropic unavailable, use Language Model (Ollama) via Sutherland

---

### 3.2 Critique Pattern (`flows/critique_pattern.json`)

**Purpose**: Critically evaluate plan, solution, or artifact

**Flow Structure**:
```
Chat Input (artifact, original_problem)
    ↓
Prompt Template (critique_instructions + artifact + problem)
    ↓
Language Model (Anthropic) → Identify issues, severity, suggestions
    ↓
Parser → Structure critique as JSON
    ↓
Condition → Check if refinement needed (critique_score < threshold)
    ↓
Chat Output (structured_critique, needs_refinement)
```

**Native Components Used**:
- Chat Input, Prompt Template, Language Model, Parser, Condition, Chat Output

**Inputs**:
- `artifact` (str | dict): Item to critique
- `original_problem` (str): Context for relevance checking
- `critique_focus` (list[str], optional): Aspects to evaluate

**Outputs**:
- `critique` (dict): Structured critique with issues, severity
- `needs_refinement` (bool): Whether artifact requires work
- `suggestions` (list[str]): Improvement recommendations

---

### 3.3 Refinement Pattern (`flows/refinement_pattern.json`)

**Purpose**: Improve artifact based on critique feedback

**Flow Structure**:
```
Chat Input (original_artifact, critique)
    ↓
Prompt Template (refinement_instructions + artifact + critique)
    ↓
Language Model (Anthropic) → Apply critique feedback, improve artifact
    ↓
Parser → Structure refined artifact
    ↓
Data Operations → Track changes made
    ↓
Chat Output (refined_artifact, changes_made)
```

**Native Components Used**:
- Chat Input, Prompt Template, Language Model, Parser, Data Operations, Chat Output

**Inputs**:
- `original_artifact` (str | dict): Artifact to refine
- `critique` (dict): Critique feedback
- `refinement_strategy` (enum: "incremental", "rewrite", "targeted")

**Outputs**:
- `refined_artifact` (str | dict): Improved version
- `changes_made` (list[str]): Description of changes
- `addresses_critique` (bool): Whether all points addressed

---

### 3.4 Self-Critique Loop Pattern (`flows/self_critique_loop_pattern.json`)

**Purpose**: Canonical "Plan → Critique → Refine" iterative improvement pattern

**Flow Structure**:
```
Chat Input (problem)
    ↓
Prompt Template (planning) → Language Model → Parser → plan_v1
    ↓
Loop (max_iterations=3):
    ├─ Item: current_plan
    ├─ Prompt Template (critique) → Language Model → critique
    ├─ Condition (critique_score >= threshold?)
    │   ├─ True → Exit loop (plan accepted)
    │   └─ False → Continue
    ├─ Prompt Template (refinement) → Language Model → refined_plan
    └─ Return refined_plan to loop
    ↓
Data Operations (aggregate iteration history)
    ↓
Chat Output (final_plan, iteration_history, final_critique)
```

**Native Components Used**:
- Chat Input, Prompt Template, Language Model, Loop, Condition, Parser, Data Operations, Chat Output

**Inputs**:
- `problem` (str): Problem to solve
- `max_iterations` (int, default: 3): Refinement cycles limit
- `quality_threshold` (float, default: 0.9): Acceptance criteria

**Outputs**:
- `final_solution` (str | dict): Refined solution after iterations
- `iteration_history` (list[dict]): Log of all cycles
- `final_critique` (dict): Final quality assessment

**Notes**:
- Demonstrates Loop component for iterative refinement
- Condition component for early stopping
- Preserves canonical Imperator self-critique pattern

---

### 3.5 Deep Reasoning Pattern (`flows/deep_reasoning_pattern.json`)

**Purpose**: Extended chain-of-thought reasoning for complex problems

**Flow Structure**:
```
Chat Input (problem)
    ↓
Prompt Template (chain_of_thought_instructions)
    ↓
Loop (max_steps=10):
    ├─ Item: current_reasoning_state
    ├─ Language Model → Next reasoning step
    ├─ Data Operations → Append to reasoning_trace
    ├─ Condition (confidence >= early_stop_threshold?)
    │   ├─ True → Exit loop
    │   └─ False → Continue
    └─ Return updated state
    ↓
Language Model (final_synthesis) → Generate conclusion from trace
    ↓
Chat Output (reasoning_trace, conclusion, confidence)
```

**Native Components Used**:
- Chat Input, Prompt Template, Language Model, Loop, Condition, Data Operations, Chat Output

**Inputs**:
- `problem` (str): Complex problem requiring deep analysis
- `max_steps` (int, default: 10): Maximum reasoning steps
- `early_stop_confidence` (float, default: 0.95): Confidence for early termination

**Outputs**:
- `reasoning_trace` (list[dict]): Step-by-step reasoning chain
- `conclusion` (str): Final answer
- `confidence` (float): Confidence in conclusion
- `steps_used` (int): Actual steps taken

---

### 3.6 Hypothesis Generation Pattern (`flows/hypothesis_generation_pattern.json`)

**Purpose**: Generate multiple alternative explanations/solutions

**Flow Structure**:
```
Chat Input (problem, num_hypotheses)
    ↓
Loop (iterations=num_hypotheses):
    ├─ Prompt Template (generate_hypothesis + diversity_factor)
    ├─ Language Model → Generate hypothesis with rationale
    ├─ Data Operations → Add to hypothesis list
    └─ Continue
    ↓
Language Model (generate_evaluation_criteria) → Suggest criteria for evaluation
    ↓
Chat Output (hypotheses, evaluation_criteria)
```

**Native Components Used**:
- Chat Input, Prompt Template, Language Model, Loop, Data Operations, Chat Output

**Inputs**:
- `problem` (str): Problem to generate hypotheses for
- `num_hypotheses` (int, default: 3): Number of alternatives
- `diversity_factor` (float, default: 0.7): How different they should be

**Outputs**:
- `hypotheses` (list[dict]): Hypotheses with rationale
- `evaluation_criteria` (list[str]): Suggested evaluation criteria

---

### 3.7 Evidence Evaluation Pattern (`flows/evidence_evaluation_pattern.json`)

**Purpose**: Systematically evaluate evidence for/against options

**Flow Structure**:
```
Chat Input (options, evidence, evaluation_criteria)
    ↓
Loop (iterate over options):
    ├─ Item: current_option
    ├─ Prompt Template (evaluate_option + evidence + criteria)
    ├─ Language Model → Generate pros/cons, score against criteria
    ├─ Parser → Structure evaluation
    └─ Return evaluation
    ↓
Data Operations (aggregate all evaluations)
    ↓
Language Model (make_recommendation) → Select best option with justification
    ↓
Chat Output (evaluations, recommendation, confidence)
```

**Native Components Used**:
- Chat Input, Prompt Template, Language Model, Loop, Parser, Data Operations, Chat Output

**Inputs**:
- `options` (list[dict]): Options to evaluate
- `evidence` (list[str] | dict): Available evidence
- `evaluation_criteria` (list[str]): Criteria to check

**Outputs**:
- `evaluations` (list[dict]): Each option with pros/cons, scores
- `recommendation` (dict): Best option with justification
- `confidence` (float): Confidence in recommendation

---

### 3.8 Verification Pattern (`flows/verification_pattern.json`)

**Purpose**: Check if proposed solution actually solves problem

**Flow Structure**:
```
Chat Input (original_problem, proposed_solution)
    ↓
Prompt Template (verification_instructions)
    ↓
Language Model → Test solution against requirements, identify gaps
    ↓
Parser → Structure verification results
    ↓
Condition (is_valid == True?)
    ├─ True → Output solution
    └─ False → Connect to refinement_pattern.json (via MCP Tools)
    ↓
Chat Output (is_valid, verification_report, gaps)
```

**Native Components Used**:
- Chat Input, Prompt Template, Language Model, Parser, Condition, MCP Tools, Chat Output

**Inputs**:
- `original_problem` (str): Problem being solved
- `proposed_solution` (str | dict): Solution to verify
- `verification_criteria` (list[str], optional): Specific checks

**Outputs**:
- `is_valid` (bool): Whether solution addresses problem
- `verification_report` (dict): Detailed check results
- `gaps` (list[str]): Missing aspects or failure modes

---

### 3.9 Synthesis Pattern (`flows/synthesis_pattern.json`)

**Purpose**: Combine multiple information sources into coherent conclusions

**Flow Structure**:
```
Chat Input (information_sources, synthesis_goal)
    ↓
Loop (iterate over sources):
    ├─ Language Model → Extract key points from each source
    └─ Data Operations → Accumulate key points
    ↓
Language Model (synthesize) → Integrate all key points
    ↓
Language Model (identify_conflicts) → Find unresolved contradictions
    ↓
Chat Output (synthesis, key_insights, unresolved_conflicts)
```

**Native Components Used**:
- Chat Input, Prompt Template, Language Model, Loop, Data Operations, Chat Output

**Inputs**:
- `information_sources` (list[str] | list[dict]): Multiple inputs
- `synthesis_goal` (str): Summary, integration, or reconciliation

**Outputs**:
- `synthesis` (str | dict): Integrated conclusion
- `key_insights` (list[str]): Main takeaways
- `unresolved_conflicts` (list[str], optional): Contradictions

---

### 3.10 Explanation Pattern (`flows/explanation_pattern.json`)

**Purpose**: Generate human-understandable explanations

**Flow Structure**:
```
Chat Input (artifact, audience, explanation_style)
    ↓
Prompt Template (explanation_instructions + audience + style)
    ↓
Language Model → Generate explanation adapted to audience
    ↓
Language Model (extract_key_points) → Summarize main points
    ↓
Condition (style == "analogical"?)
    ├─ True → Language Model (generate_examples) → Create analogies
    └─ False → Skip
    ↓
Chat Output (explanation, key_points, supporting_examples)
```

**Native Components Used**:
- Chat Input, Prompt Template, Language Model, Condition, Chat Output

**Inputs**:
- `artifact` (str | dict): Item to explain
- `audience` (enum: "technical", "general", "expert")
- `explanation_style` (enum: "step-by-step", "analogical", "causal")

**Outputs**:
- `explanation` (str): Human-readable explanation
- `key_points` (list[str]): Main points
- `supporting_examples` (list[str], optional): Analogies

---

## 4. LLM Access Architecture

### 4.1 Primary Path: Native Language Model Component

All flows use LangFlow's **native Language Model component**:

```json
{
  "component": "Language Model",
  "provider": "anthropic",
  "model": "claude-sonnet-4-5",
  "temperature": 0.7,
  "max_tokens": 2000
}
```

**No custom LLM nodes required**. Language Model component handles:
- Provider selection (Anthropic, OpenAI, Google, Ollama)
- API key management
- Error handling
- Response streaming (optional)

### 4.2 Failover: Language Model (Ollama) via Sutherland

When Anthropic unavailable, flows use Ollama provider:

```json
{
  "component": "Language Model",
  "provider": "ollama",
  "model": "phi3:mini",
  "base_url": "http://sutherland-mad:11434"
}
```

**Failover Strategy**: Each flow decides degradation behavior:
- **Deep reasoning flows**: May fail gracefully (require frontier LLMs)
- **Simple flows**: Degrade to Ollama with simplified prompts
- **Critical flows**: Queue for when Anthropic returns

**Implementation**: Use Condition component to check for Language Model errors, route to Ollama on failure.

### 4.3 No Fiedler MCP Calls (V0.7)

- **V0.7**: Direct Language Model component usage (Anthropic, Ollama)
- **V1.0+**: May add Fiedler consultation via MCP Tools for model recommendations
- **Rationale**: Simpler architecture for baseline, add orchestration layer later

---

## 5. Flow File Structure

```
lib/joshua_imperator/
├── __init__.py                          # Library metadata, version
├── flows/                               # Reference flow patterns
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
├── test_flows/                          # Test flows with known inputs/outputs
│   ├── test_planning_pattern.json
│   ├── test_self_critique_loop.json
│   └── ...
├── docs/                                # Documentation
│   ├── README.md
│   ├── patterns_guide.md                # When to use which pattern
│   ├── composition_examples.md          # Combining patterns
│   └── failover_strategies.md           # Degradation approaches
├── tests/                               # Python integration tests
│   ├── test_flow_execution.py
│   └── test_pattern_equivalence.py
└── requirements.txt                     # Dependencies
```

---

## 6. Integration with MADs

### 6.1 Usage in MAD Flows

MADs import Imperator flows as reusable subflows:

**Example**: Hopper MAD uses `self_critique_loop_pattern.json` for code generation:

```json
{
  "name": "hopper_generate_code",
  "components": [
    {
      "id": "chat_input_1",
      "type": "ChatInput"
    },
    {
      "id": "imperator_self_critique",
      "type": "FlowReference",
      "properties": {
        "flow_path": "lib/joshua_imperator/flows/self_critique_loop_pattern.json",
        "inputs_mapping": {
          "problem": "{code_generation_task}"
        }
      }
    },
    {
      "id": "chat_output_1",
      "type": "ChatOutput"
    }
  ]
}
```

### 6.2 Flow Reusability

Imperator flows are **general-purpose reasoning patterns**:
- Any MAD can import and use them
- Flows are parameterized via inputs (no hardcoded logic)
- MADs customize behavior via Prompt Templates passed as inputs

---

## 7. Component Evolution (Future)

### 7.1 Hamilton Monitoring (V0.8)

Hamilton MAD tracks Imperator flow usage:
- **Execution frequency**: Which flows are called most often?
- **Latency**: P50, P95, P99 for each flow
- **Reusability**: How many MADs use each flow?
- **Error rates**: Which flows fail most often?

### 7.2 Hardening Triggers (V0.8+)

Hopper converts flow to optimized custom node when:
1. **Performance bottleneck**: Flow in top 10% latency
2. **High reusability**: Used by 5+ MADs
3. **Strategic abstraction**: Core Joshua reasoning pattern

**Example**: If `self_critique_loop_pattern.json` shows:
- 1000+ calls/day across 8 MADs
- P95 latency 12s (Loop overhead significant)
- Error rate <1%

→ Hopper metaprograms `SelfCritiqueLoopNode` custom component
→ Optimized Python implementation (no Loop overhead)
→ Deploy to joshua_imperator v0.8.1
→ MADs update flow references to use new node

### 7.3 Evolution Lifecycle

```
Stage 1: Flow-First MVP
  └─ deploy self_critique_loop_pattern.json
      ↓ (Hamilton monitors)
Stage 2: Data Collection
  └─ 2 weeks of production usage data
      ↓ (High usage detected)
Stage 3: Hardening Decision
  └─ Hopper receives harden_flow task
      ↓ (Metaprogramming)
Stage 4: Optimized Node
  └─ Deploy SelfCritiqueLoopNode v0.8.1
      ↓ (Gradual rollout)
Stage 5: Migration
  └─ MADs update to use optimized node
```

---

## 8. Functional Requirements

### 8.1 Flow Implementation

- **LangFlow JSON Format**: All patterns as valid `.json` flow definitions
- **Native Components Only**: Use Language Model, If-Else, Loop, Condition, Prompt Template, MCP Tools, Data Operations, Parser, Chat Input/Output
- **Parameterized Inputs**: Flows accept inputs via Chat Input / Text Input components
- **Structured Outputs**: Use Parser to structure outputs as JSON
- **Self-Documenting**: Flow names, component display names clearly indicate purpose

### 8.2 Testing

- **Test Flows**: Each pattern has corresponding test flow with known inputs/expected outputs
- **Integration Tests**: Python tests execute flows via joshua_flow_runner
- **Equivalence Testing**: Compare V0.7 flow behavior to previous V0.6 imperative implementation
- **Error Handling**: Test failover paths (Anthropic unavailable → Ollama)

### 8.3 Documentation

- **Pattern Guide**: When to use each flow, input/output specifications
- **Composition Examples**: How to combine patterns for complex tasks
- **Failover Strategies**: How each pattern degrades when LLMs unavailable
- **Reference Architecture**: How flows integrate with MAD architecture

---

## 9. Non-Functional Requirements

### 9.1 Performance

- **Simple Patterns** (planning, critique, refinement): < 30s for typical inputs
- **Iterative Patterns** (self-critique loop, deep reasoning): < 3 minutes with max iterations
- **Token Efficiency**: Prompt templates concise, avoid unnecessary verbosity

**Baseline Acceptance**: V0.7 flows may be slower than optimized nodes - acceptable as MVP.

### 9.2 Observability

- **Flow Logging**: Use LangFlow's built-in logging for component execution
- **Hamilton Integration**: Log flow invocations for monitoring (future)
- **Error Tracking**: Capture Language Model errors, failover events

### 9.3 Testability

- **Unit-Level**: Test individual flow patterns with mocked LLM responses
- **Integration-Level**: Test flows end-to-end with real Language Model calls
- **Regression**: Test equivalence to previous V0.6 Imperator behavior

---

## 10. Dependencies

```txt
# requirements.txt
joshua_flow_runner>=0.7.0         # Flow execution engine
langflow>=1.5.0                   # LangFlow runtime
anthropic>=0.40.0                 # For Language Model (Anthropic)
pydantic>=2.0.0                   # Data validation
pyyaml>=6.0.0                     # Config parsing
```

**No custom dependencies** - all reasoning via native LangFlow components.

---

## 11. Deliverables

1. **Flow Library**: 10 reference flow patterns (`.json` files)
2. **Test Flows**: Test flows for each pattern with assertions
3. **Documentation**: Pattern guide, composition examples, failover strategies
4. **Integration Tests**: Python tests validating flow execution
5. **Design Document**: Detailed design covering flow structures (separate document)

---

## 12. Success Criteria

The `joshua_imperator` library (V0.7 flow-based implementation) is successful when:

1. **All 10 patterns implemented** as working LangFlow flows
2. **Zero custom nodes required** (validates ADR-037 "Use" tier)
3. **Test coverage**: All flows pass integration tests
4. **Pattern equivalence**: V0.7 flows produce equivalent results to V0.6 imperative code
5. **Documentation complete**: Developers can use patterns without asking questions
6. **Reusable**: At least 3 MADs successfully import and use Imperator flows
7. **Failover works**: Flows gracefully degrade to Ollama when Anthropic unavailable

---

## 13. Version Evolution Roadmap

### V0.7 (Current): Flow-Based MVPs
- All patterns as `.json` flows
- Native LangFlow components only
- Baseline performance (accept flow overhead)
- Hamilton monitoring begins

### V0.8: Data-Driven Hardening
- Hamilton identifies high-value flows
- Hopper converts top 3 flows to optimized custom nodes
- MADs migrate to nodes for performance-critical paths
- Flows remain available for flexibility

### V0.9: Full Node Library
- All patterns available as both flows and nodes
- Developers choose based on needs (flexibility vs. performance)
- Cross-MAD reasoning patterns
- LPPM integration for learned prompts

### V5.0: Full PCP Integration
- Imperator integrates with all PCP tiers (DTR, LPPM, CET, CRS)
- Cognitive fast paths
- 80-90% cost reduction

---

## 14. Relationship to Other PCP Components

- **DTR (joshua_dtr)**: Triage determines when Imperator reasoning needed
- **LPPM (joshua_lppm)**: Provides learned prompt patterns for Imperator flows
- **CET (joshua_cet)**: Manages working memory Imperator flows read/write
- **CRS (joshua_crs)**: Post-execution reflection on Imperator outcomes

**V0.7 Note**: Only Imperator active, others deferred to V5.0.

---

## 15. Migration from V0.6 Imperative Code

### Previous Architecture (V0.6)

```python
# Old imperative Imperator
class Imperator:
    def self_critique_loop(self, problem):
        plan = self.generate_plan(problem)
        for i in range(3):
            critique = self.critique_plan(plan)
            if critique.score >= 0.9:
                return plan
            plan = self.refine_plan(plan, critique)
        return plan
```

### New Architecture (V0.7)

```json
// self_critique_loop_pattern.json flow
{
  "components": [
    {"type": "ChatInput", "id": "problem_input"},
    {"type": "PromptTemplate", "id": "planning_prompt"},
    {"type": "LanguageModel", "id": "planner"},
    {"type": "Loop", "id": "refinement_loop", "max_iterations": 3},
    {"type": "ChatOutput", "id": "final_plan"}
  ]
}
```

**Benefits of Flow Approach**:
- **Visual**: See reasoning pattern in LangFlow UI
- **Testable**: Test flow with known inputs
- **Flexible**: Modify flow without code changes
- **Monitorable**: Hamilton tracks every component
- **Optimizable**: Hopper can metaprogram improvements

---

## 16. Open Questions

1. **Streaming**: Should flows support streaming LLM outputs for long-running operations?
2. **Caching**: Should identical flow inputs use cached LLM responses? (Language Model component may support this natively)
3. **Abort Mechanisms**: How to interrupt long-running flows? (LangFlow timeout configuration?)
4. **Progressive Output**: Should iterative flows provide intermediate results during Loop execution?
5. **Flow Versioning**: How do MADs track which Imperator flow version they're using?

---

## Appendix A: Comparison to Custom Node Approach

### Original Requirements (Pre-ADR-037)

Specified **12 custom nodes**:
- PlanNode, CritiqueNode, RefineNode, DeepReasoningNode, SelfCritiqueLoopNode, HypothesisGenerationNode, EvidenceEvaluationNode, DecisionNode, SynthesisNode, VerificationNode, ExplanationNode, ChatSessionNode

**Estimated Effort**: 8-12 weeks of development

### Flow-Based Approach (ADR-037)

Implements **10 flow patterns**:
- All using native LangFlow components
- Zero custom development
- Equivalent functionality

**Actual Effort**: 2-3 weeks (flow assembly + testing)

### Cost Savings

- **Development**: ~10 weeks saved
- **Maintenance**: No custom code to maintain (LangFlow community maintains components)
- **Evolution**: Hamilton monitors → Hopper hardens only high-value flows → minimal custom code

**Validates ADR-037 Strategy**: Use native components first, build custom only when data justifies.

---

**Last Updated:** 2025-12-22
**Status:** Ready for Implementation (V0.7 Flow-Based Approach)
**Supersedes:** `joshua_imperator_library_requirements.md` (custom node approach)
