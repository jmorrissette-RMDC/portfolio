# Tier 4: Imperator (LLM Reasoning)

**Version**: 1.0
**Status**: V1 Implementation (Current Focus)
**Implementation Target**: V1

---

## Table of Contents

1. [Overview](#overview)
2. [Design Principles](#design-principles)
3. [Architecture](#architecture)
4. [LLM Selection Strategy](#llm-selection-strategy)
5. [Reasoning Patterns](#reasoning-patterns)
6. [Consulting Teams](#consulting-teams)
7. [Context Integration](#context-integration)
8. [Action Coordination](#action-coordination)
9. [Learning Integration](#learning-integration)
10. [Performance Specifications](#performance-specifications)
11. [Implementation Guide](#implementation-guide)

---

## Overview

### Purpose

The Imperator represents the PCP's deliberative tier—full LLM reasoning capability for situations requiring genuine semantic understanding, creative problem-solving, and strategic thinking. After progressive filtering through DTR, LPPM, and CET (V3-V4), only operations genuinely requiring expensive intelligence reach the Imperator.

### Position in PCP

**Tier 4** - Deliberative reasoning tier:
- Receives escalations from CET (Tier 3) with optimized context
- Receives direct inputs in V1 (before DTR/LPPM/CET exist)
- Performs full semantic reasoning
- Coordinates Action Engine for execution
- Records all decisions in conversation bus for learning

### Key Characteristics

**Latency**: 1-10 seconds per inference
**Throughput**: Limited by LLM API rate limits
**Resource**: GPU-intensive on LLM provider infrastructure
**Cost**: Substantial per inference (varies by model)
**Capability**: Full semantic understanding and creative reasoning

---

## Design Principles

### 1. Full Semantic Capability

The Imperator is not constrained—it has access to:
- Full LLM reasoning capability
- Complete semantic understanding
- Creative problem-solving
- Strategic planning and coordination
- Complex multi-step orchestration

When operations reach the Imperator, no capability shortcuts are taken.

### 2. Flexible LLM Usage

The Imperator is not a single LLM but an **interface to the LLM ecosystem**:

**Primary Reasoning**: Each MAD has a preferred LLM for routine reasoning
- Dewey: Claude Sonnet for structured database reasoning
- Hopper: GPT-4 for code generation
- McNamara: Gemini for security analysis

**Consulting Teams**: When primary reasoning insufficient, request specialist LLMs
- **Verification**: Additional LLMs validate critical decisions
- **Specialization**: Domain-expert LLMs provide specific knowledge
- **Consensus**: Multiple LLMs reason about complex problems

**Model Selection**: Dynamic based on task requirements, not fixed

### 3. Context-Optimized Reasoning

In V4+, the Imperator receives CET-optimized context:
- Purpose-specific context assembly
- Optimal token allocation per source
- Task-appropriate structuring
- Higher success rate with fewer iterations

In V1-V3, the Imperator receives generic context but still operates effectively.

### 4. Conversation-Based Learning

Everything the Imperator does is recorded in the conversation bus:
- Reasoning processes
- Decision outcomes
- Multi-MAD orchestrations
- Strategic guidance

This creates the learning corpus for V2-V4 optimization (DTR, LPPM, CET).

---

## Architecture

### Component Structure

```
┌─────────────────────────────────────────────────────────────┐
│                    Imperator Instance                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         Context Receiver                              │  │
│  │  - V1-V3: Generic conversation context               │  │
│  │  - V4+: CET-optimized context                         │  │
│  │  - Recent conversation history                        │  │
│  │  - MAD capabilities and state                         │  │
│  └──────────────┬───────────────────────────────────────┘  │
│                 ↓                                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         LLM Selector                                  │  │
│  │  - Primary LLM for MAD domain                         │  │
│  │  - Task-specific model selection                      │  │
│  │  - Query Fiedler for model recommendations (advisory) │  │
│  └──────────────┬───────────────────────────────────────┘  │
│                 ↓                                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         Reasoning Engine                              │  │
│  │  - Construct LLM prompt with context                  │  │
│  │  - Invoke LLM via library nodes (direct access)       │  │
│  │  - Parse and interpret response                       │  │
│  │  - Iterative refinement if needed                     │  │
│  └──────────────┬───────────────────────────────────────┘  │
│                 ↓                                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │        Action Coordinator                             │  │
│  │  - Translate reasoning to action sequences            │  │
│  │  - Coordinate Action Engine execution                 │  │
│  │  - Orchestrate multi-MAD workflows                    │  │
│  │  - Handle execution feedback                          │  │
│  └──────────────┬───────────────────────────────────────┘  │
│                 ↓                                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │        Conversation Logger                            │  │
│  │  - Record all reasoning to Rogers (conversation bus)  │  │
│  │  - Structure for future learning (V2-V4)              │  │
│  │  - Include decision rationale                         │  │
│  │  - Tag with outcome for training data                 │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

```
Message + Context (from CET or direct)
    ↓
Context Integration
    ↓
LLM Selection
    │
    ├─ Primary LLM (routine reasoning)
    └─ Consulting Team (complex/critical reasoning)
    ↓
Reasoning Process
    │
    ├─ Construct prompt
    ├─ Invoke LLM (direct via library nodes - per ADR-035)
    ├─ Parse response
    └─ Iterative refinement if needed
    ↓
Action Planning
    │
    ├─ Translate reasoning to actions
    ├─ Identify MADs involved
    └─ Sequence action steps
    ↓
Action Coordination
    │
    ├─ Execute via Action Engine
    ├─ Orchestrate multi-MAD workflows
    └─ Monitor execution
    ↓
Response Generation
    ↓
Conversation Logging (to Rogers)
    ↓
Response to User/MAD
```

---

## LLM Selection Strategy

### Primary LLM Configuration

Each MAD configures a preferred primary LLM:

```typescript
interface ImperatorConfig {
    primaryLLM: {
        provider: string;      // "anthropic", "openai", "google"
        model: string;         // "claude-sonnet-4", "gpt-4", "gemini-2.0-flash"
        temperature: number;   // Default temperature
        maxTokens: number;     // Max response tokens
    };

    fallbackLLMs: Array<{
        provider: string;
        model: string;
        useWhen: string;      // "primary_unavailable" | "primary_failed"
    }>;
}
```

**Example Configurations**:

**Dewey** (Data Management):
```typescript
{
    primaryLLM: {
        provider: "anthropic",
        model: "claude-sonnet-4",  // Excellent structured reasoning
        temperature: 0.1,           // Low temp for consistency
        maxTokens: 4096
    }
}
```

**Hopper** (Code Generation):
```typescript
{
    primaryLLM: {
        provider: "openai",
        model: "gpt-4-turbo",     // Strong code generation
        temperature: 0.3,          // Some creativity for code
        maxTokens: 8192
    }
}
```

**McNamara** (Security):
```typescript
{
    primaryLLM: {
        provider: "google",
        model: "gemini-2.0-flash-thinking-exp",  // Deep analysis
        temperature: 0.0,          // Maximum consistency
        maxTokens: 8192
    }
}
```

### Dynamic Model Selection

For specific task types, override primary LLM:

```typescript
class LLMSelector {
    selectForTask(
        task: TaskClassification,
        primaryConfig: ImperatorConfig
    ): LLMConfig {
        // Task-specific overrides
        if (task.requiresExtendedContext && task.contextSize > 100000) {
            // Use Gemini 2.0 for large context
            return {
                provider: "google",
                model: "gemini-2.0-flash",
                maxTokens: 8192
            };
        }

        if (task.type === TaskType.CODE_GENERATION && task.complexity === "high") {
            // Use best code model
            return {
                provider: "openai",
                model: "gpt-4-turbo",
                maxTokens: 8192
            };
        }

        if (task.requiresDeepReasoning) {
            // Use thinking models
            return {
                provider: "openai",
                model: "o1",
                maxTokens: 4096
            };
        }

        // Default to primary
        return primaryConfig.primaryLLM;
    }
}
```

---

## Reasoning Patterns

### Reasoning Types

**Novel Problem Solving**: Situations not matching learned patterns
- Example: "Design authentication for quantum computing environment"
- Requires: Creative synthesis, domain transfer, strategic thinking

**Strategic Planning**: High-level coordination and architecture
- Example: "Plan development roadmap balancing features and technical debt"
- Requires: Goal reasoning, constraint satisfaction, tradeoff analysis

**Complex Diagnosis**: Multi-factor failure analysis
- Example: "System degrades only under specific load patterns"
- Requires: Hypothesis generation, evidence correlation, root cause analysis

**Creative Synthesis**: Novel solutions requiring innovation
- Example: "Architect real-time collaboration with offline support"
- Requires: Cross-domain analogies, constraint relaxation, novel approaches

### Reasoning Process

```typescript
class ImperatorReasoning {
    async reason(
        message: Message,
        context: AssembledContext
    ): Promise<ReasoningResult> {
        // 1. Analyze task
        const analysis = await this.analyzeTask(message, context);

        // 2. Select LLM
        const llmConfig = this.llmSelector.selectForTask(analysis);

        // 3. Construct prompt
        const prompt = this.promptBuilder.build({
            task: message,
            context: context,
            madCapabilities: this.madCapabilities,
            reasoningGoal: analysis.goal
        });

        // 4. Invoke LLM
        let response = await this.invokeLLM(llmConfig, prompt);

        // 5. Validate reasoning
        if (!this.isReasoningComplete(response)) {
            // Iterative refinement
            response = await this.refineReasoning(response, context);
        }

        // 6. Parse and structure
        const structured = this.parseReasoning(response);

        return {
            reasoning: structured,
            confidence: this.assessConfidence(response),
            actions: this.extractActions(structured),
            requiresConsulting: this.needsValidation(structured)
        };
    }

    private async refineReasoning(
        initial: LLMResponse,
        context: AssembledContext
    ): Promise<LLMResponse> {
        // Identify gaps or uncertainties
        const gaps = this.identifyGaps(initial);

        // Construct follow-up prompt
        const refinementPrompt = this.promptBuilder.buildRefinement({
            initialReasoning: initial,
            gaps: gaps,
            context: context
        });

        // Invoke LLM again
        return await this.invokeLLM(this.currentLLM, refinementPrompt);
    }
}
```

---

## Consulting Teams

### When to Use Consulting Teams

**Verification**: Critical decisions requiring validation
- Example: Database schema migration affecting all services
- Action: Request verification LLM to review decision

**Specialization**: Domain expertise beyond primary LLM
- Example: Complex security vulnerability analysis
- Action: Request security-specialist LLM consultation

**Consensus**: Complex problems with multiple valid approaches
- Example: Architecture decision with significant tradeoffs
- Action: Request multiple LLMs, synthesize consensus

**Uncertainty**: Primary LLM expresses low confidence
- Example: Novel problem outside training distribution
- Action: Request diverse perspectives for robustness

### Consulting Team Coordination

```typescript
class ConsultingTeamCoordinator {
    async requestConsulting(
        task: ReasoningTask,
        primaryReasoning: ReasoningResult,
        consultingType: ConsultingType
    ): Promise<ConsultingResult> {

        // Define consulting team composition
        const team = this.composeTeam(consultingType);

        // Prepare consultation request
        const consultRequest = {
            task: task,
            primaryReasoning: primaryReasoning,
            consultingGoal: this.defineGoal(consultingType),
            independentAnalysis: true  // Don't share each other's responses
        };

        // Execute consultations in parallel
        const consultations = await Promise.all(
            team.map(llmConfig =>
                this.consultSingleLLM(llmConfig, consultRequest)
            )
        );

        // Synthesize consultation results
        return this.synthesizeConsultations({
            primary: primaryReasoning,
            consultations: consultations,
            type: consultingType
        });
    }

    private composeTeam(type: ConsultingType): LLMConfig[] {
        switch (type) {
            case ConsultingType.VERIFICATION:
                // 1-2 different models for verification
                return [
                    { provider: "anthropic", model: "claude-sonnet-4" },
                    { provider: "openai", model: "gpt-4" }
                ];

            case ConsultingType.SPECIALIZATION:
                // Domain-specific expert models
                return this.selectDomainExperts();

            case ConsultingType.CONSENSUS:
                // 3-5 diverse models for consensus
                return [
                    { provider: "anthropic", model: "claude-sonnet-4" },
                    { provider: "openai", model: "gpt-4" },
                    { provider: "google", model: "gemini-2.0-flash" },
                    { provider: "x-ai", model: "grok-2" }
                ];

            case ConsultingType.UNCERTAINTY:
                // Diverse perspectives
                return this.selectDiverseModels();
        }
    }

    private async synthesizeConsultations(
        data: ConsultationData
    ): Promise<ConsultingResult> {
        // Identify agreements and disagreements
        const agreements = this.findAgreements(data.consultations);
        const disagreements = this.findDisagreements(data.consultations);

        // If strong consensus, adopt consensus view
        if (agreements.strength > 0.8) {
            return {
                decision: agreements.consensusView,
                confidence: agreements.strength,
                reasoning: "Strong consensus among consultations"
            };
        }

        // If significant disagreement, escalate to human
        if (disagreements.severity > 0.5) {
            return {
                decision: null,
                confidence: 0.0,
                reasoning: "Significant disagreement requires human judgment",
                requiresHumanReview: true,
                perspectives: data.consultations
            };
        }

        // Otherwise, synthesize nuanced view
        return this.synthesizeNuancedView(data);
    }
}
```

---

## Context Integration

### V1-V3: Generic Context

In V1-V3 (before CET), Imperator receives generic context:

```typescript
interface GenericContext {
    recentConversation: Message[];  // Last N messages
    madState: MADState;              // Current MAD capabilities
    conversationMetadata: {
        conversationId: string;
        participants: string[];
        startTime: Date;
    };
}
```

**Limitations**:
- No purpose-specific assembly
- No optimal token allocation
- No compression or structuring
- Context may miss critical information

**Still Effective**: LLMs reason successfully with generic context, just less efficiently

### V4+: CET-Optimized Context

In V4+, Imperator receives CET-optimized context:

```typescript
interface OptimizedContext {
    taskType: TaskType;

    sources: {
        recentConversation: StructuredContent;
        relevantHistory: StructuredContent;      // RAG retrieval
        authoritativeDocs: StructuredContent;    // Domain knowledge
        realTimeData: StructuredContent;         // System state
        crossDomainAnalogies?: StructuredContent; // Transfer learning
    };

    tokenAllocation: {
        [sourceName: string]: number;  // Tokens per source
    };

    assembly Strategy: string;  // How context was assembled

    metadata: {
        cetVersion: string;
        attentionWeights: number[];
        confidenceInAssembly: number;
    };
}
```

**Improvements**:
- Purpose-specific for task type
- Optimal source selection and allocation
- Compressed while preserving critical info
- Structured for LLM understanding

**Effectiveness**: 2-3x improvement in first-attempt success

---

## Action Coordination

### Translating Reasoning to Actions

```typescript
class ActionCoordinator {
    async coordinateActions(
        reasoning: ReasoningResult,
        context: Context
    ): Promise<ExecutionResult> {
        // 1. Extract action plan from reasoning
        const actionPlan = this.extractActionPlan(reasoning);

        // 2. Identify involved MADs
        const involvedMADs = this.identifyMADs(actionPlan);

        // 3. Sequence actions (handle dependencies)
        const sequence = this.sequenceActions(actionPlan);

        // 4. Execute action sequence
        const results = [];
        for (const action of sequence) {
            const result = await this.executeAction(action);
            results.push(result);

            // Check for failures
            if (!result.success) {
                // Failure handling
                const recovery = await this.handleFailure(action, result);
                if (!recovery.recovered) {
                    return {
                        success: false,
                        partialResults: results,
                        failedAction: action,
                        error: result.error
                    };
                }
            }
        }

        return {
            success: true,
            results: results,
            reasoning: reasoning
        };
    }

    private async executeAction(
        action: PlannedAction
    ): Promise<ActionResult> {
        // Route to appropriate MAD's Action Engine
        if (action.targetMAD === this.madName) {
            // Local execution
            return await this.actionEngine.execute(action);
        } else {
            // Remote execution via conversation bus
            return await this.sendActionToMAD(action.targetMAD, action);
        }
    }

    private async handleFailure(
        action: PlannedAction,
        failure: ActionResult
    ): Promise<RecoveryResult> {
        // Re-invoke Imperator for failure diagnosis and recovery
        const diagnosis = await this.imperator.reason({
            task: "diagnose action failure",
            failedAction: action,
            failure: failure,
            context: this.context
        });

        // Execute recovery strategy if provided
        if (diagnosis.recoveryStrategy) {
            return await this.executeRecovery(diagnosis.recoveryStrategy);
        }

        return { recovered: false, reason: "No recovery strategy" };
    }
}
```

### Multi-MAD Orchestration

```typescript
class MultiMADOrchestrator {
    async orchestrateWorkflow(
        workflow: WorkflowPlan,
        participants: string[]
    ): Promise<OrchestrationResult> {
        const results = new Map<string, any>();

        // Execute workflow steps
        for (const step of workflow.steps) {
            // Determine which MAD handles this step
            const assignedMAD = this.assignStep(step, participants);

            // Send task to MAD
            const message = this.buildTaskMessage(step, results);
            const response = await this.sendToMAD(assignedMAD, message);

            // Store result for subsequent steps
            results.set(step.id, response);

            // Check for decision points
            if (step.requiresDecision) {
                // Imperator provides strategic guidance
                const guidance = await this.provideGuidance(step, response);
                this.updateWorkflow(workflow, guidance);
            }
        }

        return {
            success: true,
            stepResults: results,
            finalOutcome: this.synthesizeFinalOutcome(results)
        };
    }
}
```

---

## Learning Integration

### Recording for Future Learning

Everything the Imperator does is recorded in the conversation bus for V2-V4 learning:

```typescript
class ConversationLogger {
    async logReasoningEpisode(
        message: Message,
        context: Context,
        reasoning: ReasoningResult,
        actions: ActionPlan,
        outcome: ExecutionResult
    ): Promise<void> {
        // Create structured log entry
        const episode = {
            type: "imperator_reasoning",
            timestamp: new Date(),
            conversationId: context.conversationId,
            madName: this.madName,

            // Input
            trigger: message,
            contextProvided: context,
            taskClassification: reasoning.taskType,

            // Reasoning process
            llmUsed: reasoning.llmConfig,
            promptConstruction: reasoning.prompt,
            rawResponse: reasoning.rawLLMResponse,
            parsedReasoning: reasoning.structured,
            confidence: reasoning.confidence,

            // Actions
            actionPlan: actions,
            involvedMADs: actions.participants,

            // Outcome
            executionResults: outcome,
            success: outcome.success,
            duration: outcome.duration,

            // Metadata for learning
            tags: {
                taskType: reasoning.taskType,
                complexity: this.assessComplexity(reasoning),
                novelty: this.assessNovelty(message, context),
                useForTraining: true
            }
        };

        // Store in conversation bus (Rogers → Dewey)
        await this.rogers.storeMessage(episode);

        // Index for retrieval
        await this.indexForRetrieval(episode);
    }
}
```

### Training Data Generation

```typescript
// V3: LPPM learns process patterns from these episodes
interface LPPMTrainingData {
    processPattern: string;         // What workflow was orchestrated
    steps: ProcessStep[];           // Sequence of actions
    madInteractions: Interaction[]; // How MADs coordinated
    decisionPoints: DecisionPoint[]; // When Imperator provided guidance
    outcome: Outcome;               // Success/failure
}

// V2: DTR learns routing patterns
interface DTRTrainingData {
    messageFeatures: FeatureVector;  // Extracted features
    routingDecision: RoutingClass;   // How it was classified
    escalated: boolean;              // Did it need Imperator?
    outcome: Outcome;                // Was routing correct?
}

// V4: CET learns context optimization
interface CETTrainingData {
    taskType: TaskType;
    sourcesAvailable: ContextSource[];
    sourcesUsed: ContextSource[];
    tokenAllocations: Map<string, number>;
    reasoningSuccess: boolean;
    iterationsRequired: number;
    outcomeQuality: number;
}
```

---

## Performance Specifications

### Latency Characteristics

**Single Inference**: 1-10 seconds
- Model-dependent: Fast models ~1-2s, deep reasoning models ~5-10s
- Context-dependent: Larger context → longer latency
- Load-dependent: API rate limits affect response time

**With Iteration**: 5-30 seconds
- Initial reasoning: 2-5s
- Refinement iteration: 2-5s each
- Typical: 1-2 iterations for complex tasks

**With Consulting**: 10-60 seconds
- Primary reasoning: 2-5s
- Parallel consultations: 5-10s
- Synthesis: 2-5s

### Throughput Characteristics

**Rate Limits**: Provider-dependent
- Anthropic Claude: Tier-based (e.g., 50 requests/min)
- OpenAI GPT-4: Tier-based (e.g., 5000 requests/min)
- Google Gemini: Tier-based (e.g., 10 requests/min free, 360/min paid)

**Practical Limits**: 10-100 inferences/minute per MAD
- Depends on provider tier and model
- Can parallelize across multiple API keys
- Consulting teams count as multiple requests

### Effectiveness Metrics

**First-Attempt Success**:
- V1-V3 (generic context): ~65%
- V4+ (CET-optimized): ~82%

**Iteration Count**:
- Simple tasks: 1 inference
- Moderate tasks: 1-2 iterations
- Complex tasks: 2-4 iterations

**Consulting Rate**:
- V1-V3: ~5% of tasks require consulting
- V4+: ~2-3% (CET improves context, fewer uncertainties)

---

## Implementation Guide

### V1 Implementation (Current)

**Priority**: Get all MADs operational with functional Imperator

**Tasks**:
1. Implement Imperator base class
2. Integrate library nodes for direct LLM access (ADR-035)
3. Build prompt construction system
4. Add Action Engine coordination
5. Implement conversation logging

**Per-MAD Customization**:
- Configure primary LLM for domain
- Define MAD-specific capabilities
- Set up domain context sources

### Prompt Engineering

```typescript
class PromptBuilder {
    buildPrompt(config: PromptConfig): string {
        return `
You are the Thought Engine for ${config.madName}, a specialized component in the Joshua ecosystem.

Your role: ${config.madRole}

Capabilities available to you:
${this.formatCapabilities(config.madCapabilities)}

Current task:
${config.task}

Context:
${this.formatContext(config.context)}

Instructions:
- Analyze the task thoroughly
- Consider available capabilities
- Plan a sequence of actions using Action Engine
- If coordinating with other MADs, specify interactions clearly
- Provide reasoning for your decisions

Response format:
{
  "analysis": "Your analysis of the task",
  "reasoning": "Your reasoning process",
  "actionPlan": [
    {
      "action": "action_name",
      "parameters": {...},
      "rationale": "why this action"
    }
  ],
  "confidence": 0.0-1.0,
  "alternativeApproaches": ["if applicable"]
}
`;
    }
}
```

### Testing Strategy

**Unit Tests**:
- Prompt construction correctness
- LLM response parsing
- Action extraction logic
- Conversation logging

**Integration Tests**:
- Imperator → Direct LLM access via library nodes
- Imperator → Action Engine coordination
- Multi-MAD orchestration
- Failure handling and recovery

**Validation Tests**:
- Reasoning quality on sample tasks
- Action plan correctness
- Orchestration effectiveness
- Learning data quality

---

## References

- Yao, S., et al. (2023). ReAct: Synergizing Reasoning and Acting in Language Models. ICLR 2023
- Wei, J., et al. (2022). Chain-of-Thought Prompting Elicits Reasoning in Large Language Models. NeurIPS 2022
- Paper 04: Progressive Cognitive Pipeline (Tier 4 section)
- MAD Architecture v1.3: Thought Engine specifications

---

**Navigation**: [← Tier 3 CET](./PCP_03_Tier3_CET.md) | [Index](./PCP_00_Index.md) | [Tier 5 CRS →](./PCP_05_Tier5_CRS.md)
