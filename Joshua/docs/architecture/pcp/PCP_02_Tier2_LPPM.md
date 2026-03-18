# Tier 2: Learned Prose-to-Process Mapper (LPPM)

**Version**: 1.0
**Status**: Design Phase (V3 Planned)
**Implementation Target**: V3

---

## Table of Contents

1. [Overview](#overview)
2. [Design Principles](#design-principles)
3. [Architecture](#architecture)
4. [Pattern Recognition](#pattern-recognition)
5. [Process Templates](#process-templates)
6. [Knowledge Distillation](#knowledge-distillation)
7. [Orchestration Engine](#orchestration-engine)
8. [Escalation Logic](#escalation-logic)
9. [Learning Mechanism](#learning-mechanism)
10. [Integration](#integration)
11. [Performance Specifications](#performance-specifications)
12. [Implementation Guide](#implementation-guide)

---

## Overview

### Purpose

The Learned Prose-to-Process Mapper (LPPM) provides **process orchestration** in milliseconds for learned multi-step workflows. Like learned motor patterns that execute automatically after training (walking, typing), LPPM orchestrates complex processes observed repeatedly in conversations without requiring creative reasoning.

### Position in PCP

**Tier 2** - Second filter in the cognitive cascade:
- Receives escalations from DTR (Tier 1) and direct inputs
- Recognizes learned process patterns in conversational requests
- Orchestrates deterministic workflows autonomously
- Escalates novel elements or strategic decisions to Imperator via CET

### Key Characteristics

**Latency**: 50-500 milliseconds per orchestration
**Throughput**: 100-1,000 orchestrations/second per MAD
**Resource**: Moderate CPU, modest GPU for neural inference, moderate memory
**Cost**: Significantly cheaper than full LLM inference
**Success Rate**: 85%+ for learned processes

---

## Design Principles

### 1. Knowledge Distillation

LPPM learns by observing how the **Imperator** solves problems through conversation:
- Watch Imperator orchestrate multi-MAD workflows
- Identify recurring patterns in orchestration strategies
- Distill expensive symbolic reasoning into efficient procedural execution
- Convert "how the Imperator does it" into "automatic execution template"

This is knowledge distillation from teacher (Imperator) to student (LPPM).

### 2. Process, Not Prose

LPPM operates on **process patterns**, not natural language semantics:
- Input: "Start development cycle for authentication feature"
- Recognition: Development cycle pattern (requirements → implement → test → validate)
- Output: Multi-step orchestration plan

LPPM doesn't understand language deeply; it recognizes conversation patterns that map to processes.

### 3. Hybrid Orchestration

LPPM doesn't choose between full autonomy and full escalation:
- Orchestrate deterministic steps autonomously
- Escalate specific decision points requiring reasoning
- Imperator provides strategic guidance
- LPPM continues with guidance integrated

Example: LPPM orchestrates development cycle, encounters "Must support legacy API" → escalates compatibility question → Imperator provides strategy → LPPM continues with strategy

### 4. Domain Specialization

Each MAD's LPPM learns domain-specific process patterns:
- Dewey LPPM: Database migration workflows, query optimization processes
- Hopper LPPM: Development cycles, code generation workflows
- McNamara LPPM: Incident response processes, threat analysis workflows

Shared algorithm, domain-specific training, specialized behavior.

---

## Architecture

### Component Structure

```
┌─────────────────────────────────────────────────────────────┐
│                      LPPM Instance                           │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         Conversational Pattern Encoder                │  │
│  │  - Tokenization and embedding                         │  │
│  │  - Conversation structure encoding                    │  │
│  │  - Intent classification                              │  │
│  └──────────────┬───────────────────────────────────────┘  │
│                 ↓                                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │          Pattern Recognition Network                  │  │
│  │  - Neural network (LSTM/Transformer)                  │  │
│  │  - Trained on V1 Imperator orchestrations             │  │
│  │  - Outputs: Process ID + Confidence                   │  │
│  │  - Unknown patterns → Escalate                        │  │
│  └──────────────┬───────────────────────────────────────┘  │
│                 ↓                                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │           Process Template Library                    │  │
│  │  - Learned process templates from V1                  │  │
│  │  - Multi-step workflow definitions                    │  │
│  │  - Decision point specifications                      │  │
│  │  - MAD interaction patterns                           │  │
│  └──────────────┬───────────────────────────────────────┘  │
│                 ↓                                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │          Orchestration Engine                         │  │
│  │  - Execute deterministic steps                        │  │
│  │  - Coordinate multi-MAD interactions                  │  │
│  │  - Escalate decision points to Imperator              │  │
│  │  - Integrate strategic guidance                       │  │
│  └──────────────┬───────────────────────────────────────┘  │
│                 ↓                                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │          Learning System                              │  │
│  │  - Observe Imperator orchestrations                   │  │
│  │  - Extract process patterns                           │  │
│  │  - Generalize templates                               │  │
│  │  - Refine recognition network                         │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

```
Message Input (from DTR or direct)
    ↓
Conversational Pattern Encoding (< 50 ms)
    ↓
Pattern Recognition Neural Network (< 200 ms)
    ↓
Match to Process Template? + Confidence
    ↓
    ├─ Known Process (confidence ≥ 0.70)
    │      ↓
    │  Generate Orchestration Plan
    │      ↓
    │  Execute Deterministic Steps
    │      ↓
    │  Decision Point?
    │      ├─ No → Continue execution
    │      └─ Yes → Escalate to Imperator (CET → Tier 4)
    │             ↓
    │         Receive Strategic Guidance
    │             ↓
    │         Continue with Guidance
    │
    └─ Unknown / Novel (confidence < 0.70)
           → Escalate entirely to CET → Imperator (Tiers 3-4)
           → Observe outcome for future learning
```

---

## Pattern Recognition

### Neural Network Architecture

**Model Type**: Bidirectional LSTM or Transformer Encoder

**Input**: Conversational message + context
- Tokenized message text
- Conversation history (last N messages)
- Participant identities
- Turn structure

**Output**: Process pattern classification + confidence
- Process ID: Which learned template matches
- Confidence: 0.0-1.0 matching score
- Parameters: Extracted entities (feature name, file path, etc.)

**Architecture**:
```
Input: Tokenized conversation (512 tokens max)
    ↓
Embedding Layer (768 dimensions)
    ↓
Bidirectional LSTM (2 layers, 512 hidden units)
  or
Transformer Encoder (6 layers, 8 heads)
    ↓
Attention Pooling
    ↓
Classification Head → Process ID + Confidence
    ↓
Parameter Extraction Head → Named entities/arguments
```

### Training Data Format

```python
@dataclass
class ProcessTrainingExample:
    """Training example for LPPM pattern recognition"""

    # Input
    message: str  # Conversational trigger message
    context: List[str]  # Recent conversation history
    participants: List[str]  # Involved MADs

    # Output (from V1 Imperator observation)
    process_id: str  # Which process was executed
    process_steps: List[ProcessStep]  # Actual steps taken
    mad_interactions: List[MADInteraction]  # MAD coordination
    decision_points: List[DecisionPoint]  # Strategic escalations
    outcome: Outcome  # SUCCESS, PARTIAL_SUCCESS, FAILURE

    # Metadata
    timestamp: datetime
    conversation_id: str
    imperator_model: str  # Which LLM orchestrated
```

**Collection Source**: V1 conversation history where Imperator orchestrated workflows

### Pattern Recognition Process

```python
class LPPMPatternRecognizer:
    """Recognize learned process patterns from conversational input"""

    def __init__(self, model: NeuralNetwork, templates: ProcessLibrary):
        self.model = model
        self.templates = templates

    def recognize(
        self,
        message: Message,
        context: ConversationContext
    ) -> RecognitionResult:
        """
        Recognize process pattern in < 200 ms

        Returns: Process template + confidence + parameters
        """
        # 1. Encode conversational input
        encoding = self._encode_conversation(message, context)

        # 2. Neural network classification
        logits = self.model.forward(encoding)
        process_id = torch.argmax(logits).item()
        confidence = torch.softmax(logits, dim=-1)[process_id].item()

        # 3. Extract parameters
        parameters = self._extract_parameters(message, process_id)

        # 4. Retrieve template
        if confidence >= 0.70:
            template = self.templates.get(process_id)
            return RecognitionResult(
                matched=True,
                template=template,
                confidence=confidence,
                parameters=parameters
            )
        else:
            return RecognitionResult(
                matched=False,
                confidence=confidence,
                reason="Low confidence - novel pattern"
            )

    def _encode_conversation(
        self,
        message: Message,
        context: ConversationContext
    ) -> torch.Tensor:
        """Encode message + context for neural network"""
        # Tokenize message
        message_tokens = self.tokenizer.encode(message.content)

        # Tokenize recent context (last 5 messages)
        context_tokens = []
        for prev_message in context.recent[-5:]:
            context_tokens.extend(self.tokenizer.encode(prev_message.content))

        # Combine and pad/truncate to 512 tokens
        all_tokens = context_tokens + message_tokens
        all_tokens = all_tokens[-512:]  # Keep most recent

        # Convert to tensor
        return torch.tensor(all_tokens, dtype=torch.long)

    def _extract_parameters(
        self,
        message: Message,
        process_id: str
    ) -> Dict[str, Any]:
        """Extract process-specific parameters from message"""
        template = self.templates.get(process_id)

        parameters = {}
        for param_spec in template.parameters:
            # Use regex or NER to extract
            value = self._extract_entity(message.content, param_spec)
            if value:
                parameters[param_spec.name] = value

        return parameters
```

---

## Process Templates

### Template Structure

```python
@dataclass
class ProcessTemplate:
    """Learned process workflow template"""

    id: str  # Unique process identifier
    name: str  # Human-readable name
    description: str  # What this process does

    # Pattern matching
    trigger_patterns: List[str]  # Conversation patterns that trigger
    required_parameters: List[ParameterSpec]  # Entities to extract

    # Workflow steps
    steps: List[ProcessStep]  # Ordered execution steps
    decision_points: List[DecisionPoint]  # When to escalate to Imperator

    # MAD coordination
    involved_mads: List[str]  # Which MADs participate
    interaction_patterns: List[InteractionPattern]  # How they coordinate

    # Metadata
    learned_from_conversations: List[str]  # Training sources
    success_rate: float  # Historical performance
    avg_execution_time: float  # Typical duration
```

### Example: Development Cycle Template

```python
development_cycle_template = ProcessTemplate(
    id="dev_cycle_001",
    name="Standard Development Cycle",
    description="Requirements → Implementation → Testing → Validation workflow",

    trigger_patterns=[
        "start development cycle for {feature}",
        "implement {feature}",
        "develop {feature} with requirements {requirements}"
    ],

    required_parameters=[
        ParameterSpec(name="feature", type="string", required=True),
        ParameterSpec(name="requirements", type="text", required=False),
    ],

    steps=[
        ProcessStep(
            id="requirements_analysis",
            action="analyze_requirements",
            mad="Hopper",
            deterministic=False,  # May need Imperator guidance
        ),
        ProcessStep(
            id="implementation",
            action="generate_code",
            mad="Hopper",
            deterministic=True,  # Can execute automatically
            depends_on=["requirements_analysis"]
        ),
        ProcessStep(
            id="validation",
            action="review_code",
            mad="Starret",
            deterministic=True,
            depends_on=["implementation"]
        ),
        ProcessStep(
            id="testing",
            action="run_tests",
            mad="Hopper",
            deterministic=True,
            depends_on=["implementation"]
        ),
    ],

    decision_points=[
        DecisionPoint(
            after_step="requirements_analysis",
            condition="requirements_unclear or requirements_novel",
            escalate_to="Imperator",
            question="How should we interpret these requirements?"
        ),
        DecisionPoint(
            after_step="validation",
            condition="validation_failed",
            escalate_to="Imperator",
            question="How should we address validation concerns?"
        ),
    ],

    involved_mads=["Hopper", "Starret", "Dewey"],
    interaction_patterns=[
        InteractionPattern(
            from_mad="Hopper",
            to_mad="Starret",
            message_type="validation_request",
            timing="after_implementation"
        ),
    ],

    learned_from_conversations=[
        "conv_20250915_dev_auth",
        "conv_20250918_dev_api",
        # ... 15 more examples
    ],
    success_rate=0.87,
    avg_execution_time=180.0  # seconds
)
```

### Template Library Management

```python
class ProcessTemplateLibrary:
    """Manage learned process templates"""

    def __init__(self):
        self.templates: Dict[str, ProcessTemplate] = {}
        self.pattern_index: Dict[str, List[str]] = {}  # pattern → template IDs

    def add_template(self, template: ProcessTemplate):
        """Add newly learned template to library"""
        self.templates[template.id] = template

        # Index trigger patterns for fast lookup
        for pattern in template.trigger_patterns:
            if pattern not in self.pattern_index:
                self.pattern_index[pattern] = []
            self.pattern_index[pattern].append(template.id)

    def get(self, process_id: str) -> Optional[ProcessTemplate]:
        """Retrieve template by ID"""
        return self.templates.get(process_id)

    def search_by_pattern(self, message: str) -> List[ProcessTemplate]:
        """Find templates matching message pattern"""
        matches = []
        for pattern, template_ids in self.pattern_index.items():
            if self._pattern_matches(pattern, message):
                matches.extend([self.templates[tid] for tid in template_ids])
        return matches

    def update_success_rate(self, process_id: str, outcome: Outcome):
        """Update template performance metrics after execution"""
        template = self.templates[process_id]
        # Exponential moving average
        alpha = 0.1
        success = 1.0 if outcome == Outcome.SUCCESS else 0.0
        template.success_rate = (
            alpha * success + (1 - alpha) * template.success_rate
        )
```

---

## Knowledge Distillation

### Learning from Imperator Orchestrations

**Source**: V1 conversation history where Imperator orchestrated workflows

**Process**:
1. **Identify Orchestration Episodes**: Conversations where Imperator coordinated multiple MADs
2. **Extract Workflow Structure**: Sequence of MAD interactions, decision points, outcomes
3. **Generalize Patterns**: Find common structures across similar orchestrations
4. **Create Templates**: Distill generalizable process templates
5. **Train Recognition Network**: Learn to map conversational triggers to templates

### Pattern Extraction Algorithm

```python
def extract_process_patterns(
    conversations: List[Conversation],
    min_similarity: float = 0.75
) -> List[ProcessTemplate]:
    """
    Extract process templates from V1 Imperator orchestrations

    Args:
        conversations: V1 conversation history
        min_similarity: Minimum similarity to cluster as same pattern

    Returns:
        List of learned process templates
    """
    # 1. Identify orchestration episodes
    orchestrations = []
    for conv in conversations:
        if is_orchestration_episode(conv):
            orchestrations.append(extract_orchestration_structure(conv))

    # 2. Cluster similar orchestrations
    clusters = cluster_orchestrations(orchestrations, min_similarity)

    # 3. Generate template for each cluster
    templates = []
    for cluster in clusters:
        template = generalize_cluster_to_template(cluster)
        templates.append(template)

    return templates


def extract_orchestration_structure(conv: Conversation) -> OrchestrationEpisode:
    """Extract workflow structure from conversation"""
    episode = OrchestrationEpisode()

    # Identify participants
    episode.participants = set(msg.sender for msg in conv.messages)

    # Extract step sequence
    for msg in conv.messages:
        if is_action_message(msg):
            step = ProcessStep(
                action=extract_action(msg),
                mad=msg.sender,
                deterministic=was_deterministic(msg)
            )
            episode.steps.append(step)

    # Identify decision points
    for msg in conv.messages:
        if is_decision_point(msg):  # Imperator deliberation
            decision = DecisionPoint(
                question=extract_question(msg),
                resolution=extract_resolution(msg)
            )
            episode.decision_points.append(decision)

    # Extract outcome
    episode.outcome = determine_outcome(conv)

    return episode


def cluster_orchestrations(
    orchestrations: List[OrchestrationEpisode],
    min_similarity: float
) -> List[List[OrchestrationEpisode]]:
    """Cluster similar orchestrations using structure similarity"""
    # Use edit distance on step sequences
    similarity_matrix = compute_similarity_matrix(orchestrations)

    # Hierarchical clustering
    clusters = agglomerative_clustering(
        similarity_matrix,
        threshold=min_similarity
    )

    return clusters


def generalize_cluster_to_template(
    cluster: List[OrchestrationEpisode]
) -> ProcessTemplate:
    """Create process template from cluster of similar orchestrations"""
    # Find common structure
    common_steps = extract_common_steps(cluster)
    common_decision_points = extract_common_decision_points(cluster)
    common_mads = extract_common_mads(cluster)

    # Extract trigger patterns from initiating messages
    trigger_patterns = extract_trigger_patterns(cluster)

    # Build template
    template = ProcessTemplate(
        id=generate_template_id(),
        name=infer_template_name(cluster),
        description=infer_description(cluster),
        trigger_patterns=trigger_patterns,
        steps=common_steps,
        decision_points=common_decision_points,
        involved_mads=common_mads,
        learned_from_conversations=[ep.conversation_id for ep in cluster],
        success_rate=compute_success_rate(cluster),
        avg_execution_time=compute_avg_time(cluster)
    )

    return template
```

### Neural Network Training

**Objective**: Learn to map conversational triggers → process templates

**Training Data**: Pairs of (conversation trigger, process template ID)

**Training Process**:
```python
def train_lppm_recognition_network(
    templates: List[ProcessTemplate],
    conversations: List[Conversation]
) -> NeuralNetwork:
    """
    Train LPPM pattern recognition network

    Args:
        templates: Extracted process templates
        conversations: V1 conversation history

    Returns:
        Trained neural network
    """
    # 1. Create training examples
    training_examples = []
    for conv in conversations:
        # Find which template this conversation matches
        matching_template = find_matching_template(conv, templates)
        if matching_template:
            example = ProcessTrainingExample(
                message=conv.trigger_message.content,
                context=[msg.content for msg in conv.context],
                participants=[msg.sender for msg in conv.messages],
                process_id=matching_template.id,
                # ... other fields
            )
            training_examples.append(example)

    # 2. Initialize model
    model = LPPMNetwork(
        vocab_size=tokenizer.vocab_size,
        embedding_dim=768,
        hidden_dim=512,
        num_layers=2,
        num_processes=len(templates),
    )

    # 3. Train with cross-entropy loss
    optimizer = Adam(model.parameters(), lr=1e-4)
    for epoch in range(num_epochs):
        for batch in DataLoader(training_examples, batch_size=32):
            # Forward pass
            logits = model(batch.encoded_input)
            loss = cross_entropy_loss(logits, batch.process_id)

            # Backward pass
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

    return model
```

---

## Orchestration Engine

### Execution Process

```python
class LPPMOrchestrationEngine:
    """Execute learned process workflows"""

    async def orchestrate(
        self,
        template: ProcessTemplate,
        parameters: Dict[str, Any],
        context: ConversationContext
    ) -> OrchestrationResult:
        """
        Orchestrate multi-step workflow from template

        Returns: Outcome + results from each step
        """
        result = OrchestrationResult(template_id=template.id)

        # Execute steps in sequence
        for step in template.steps:
            # Check dependencies
            if not self._dependencies_satisfied(step, result):
                continue  # Skip or wait

            # Execute step
            if step.deterministic:
                # Execute autonomously
                step_result = await self._execute_deterministic_step(
                    step, parameters, context
                )
            else:
                # May require Imperator guidance
                step_result = await self._execute_guided_step(
                    step, parameters, context
                )

            result.step_results[step.id] = step_result

            # Check for decision points after this step
            decision_point = self._find_decision_point_after(step, template)
            if decision_point and self._should_escalate(decision_point, step_result):
                # Escalate to Imperator for strategic guidance
                guidance = await self._escalate_for_guidance(
                    decision_point, step_result, context
                )

                # Integrate guidance into remaining workflow
                self._integrate_guidance(template, guidance)

        return result

    async def _execute_deterministic_step(
        self,
        step: ProcessStep,
        parameters: Dict[str, Any],
        context: ConversationContext
    ) -> StepResult:
        """Execute step autonomously via Action Engine"""
        # Construct action message
        action_message = self._build_action_message(step, parameters)

        # Send to appropriate MAD's Action Engine
        response = await self.action_engine.execute(
            mad=step.mad,
            action=step.action,
            parameters=action_message
        )

        return StepResult(
            success=response.success,
            data=response.data,
            execution_time=response.execution_time
        )

    async def _escalate_for_guidance(
        self,
        decision_point: DecisionPoint,
        step_result: StepResult,
        context: ConversationContext
    ) -> StrategicGuidance:
        """Escalate decision point to Imperator (via CET)"""
        # Construct escalation message
        escalation = {
            "question": decision_point.question,
            "context": {
                "template": template.name,
                "current_step": step.id,
                "step_result": step_result.summary(),
            },
            "options": decision_point.options,
        }

        # Route to CET → Imperator (Tiers 3-4)
        guidance = await self.imperator.provide_guidance(escalation, context)

        return guidance

    def _integrate_guidance(
        self,
        template: ProcessTemplate,
        guidance: StrategicGuidance
    ):
        """Integrate Imperator's strategic guidance into workflow"""
        # Modify remaining steps based on guidance
        for modification in guidance.modifications:
            if modification.type == "ADD_STEP":
                template.steps.insert(modification.position, modification.step)
            elif modification.type == "MODIFY_STEP":
                step = template.steps[modification.step_index]
                step.parameters.update(modification.parameters)
            elif modification.type == "SKIP_STEP":
                template.steps[modification.step_index].skip = True
```

---

## Escalation Logic

### When to Escalate

**Novel Elements**:
- Process pattern recognized but contains novel parameters
- Example: Development cycle for "quantum computing feature" (unfamiliar domain)
- Action: Execute standard structure, escalate novel domain questions

**Decision Points**:
- Pre-defined points in template requiring strategic judgment
- Example: "Requirements unclear" in development cycle
- Action: Escalate specific question, continue with guidance

**Execution Failures**:
- Step fails unexpectedly during orchestration
- Example: Code generation produces syntax errors repeatedly
- Action: Escalate failure diagnosis, adjust strategy

**Confidence Thresholds**:
- Step result confidence below threshold
- Example: Validation step returns "uncertain" result
- Action: Escalate for human-like judgment

### Escalation Format

```python
@dataclass
class EscalationRequest:
    """Request for Imperator strategic guidance during LPPM orchestration"""

    # Context
    template_id: str  # Which process is being orchestrated
    current_step: str  # Where we are in the process
    execution_state: Dict[str, Any]  # Results so far

    # Question
    decision_point: DecisionPoint  # What requires guidance
    question: str  # Specific question for Imperator
    options: Optional[List[str]]  # Possible approaches (if known)

    # Urgency
    blocking: bool  # Does workflow halt until guidance received?
    timeout: Optional[float]  # How long to wait for response

@dataclass
class StrategicGuidance:
    """Imperator's strategic guidance for LPPM to continue orchestration"""

    # Decision
    decision: str  # Answer to the question
    rationale: str  # Why this approach

    # Workflow modifications
    modifications: List[WorkflowModification]  # How to adjust process

    # Confidence
    confidence: float  # Imperator's confidence in guidance
    alternatives: List[str]  # Other approaches considered
```

---

(Continuing in next message due to length...)
