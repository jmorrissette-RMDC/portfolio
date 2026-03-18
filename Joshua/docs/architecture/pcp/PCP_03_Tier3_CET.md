# Tier 3: Context Engineering Transformer (CET)

**Version**: 1.0
**Status**: Design Phase (V4 Planned)
**Implementation Target**: V4 (2026 Q3)

---

## Table of Contents

1. [Overview](#overview)
2. [Design Principles](#design-principles)
3. [Architecture](#architecture)
4. [Task Classification](#task-classification)
5. [Context Source Selection](#context-source-selection)
6. [Attention Mechanisms](#attention-mechanisms)
7. [Context Assembly](#context-assembly)
8. [Learning Mechanism](#learning-mechanism)
9. [Integration](#integration)
10. [Performance Specifications](#performance-specifications)
11. [Implementation Guide](#implementation-guide)

---

## Overview

### Purpose

The Context Engineering Transformer (CET) provides **context optimization** for LLM efficiency. CET recognizes that context is the fundamental carrier of thought—it determines what the LLM can reason about and how effectively it performs. Rather than treating context as a constraint ("fill N tokens with recent conversation"), CET engineers optimal context for specific reasoning tasks.

### Position in PCP

**Tier 3** - Optimization layer before Imperator:
- Receives escalations from LPPM (Tier 2) requiring Imperator reasoning
- Analyzes task requirements
- Assembles optimal context from multiple sources
- Always escalates to Imperator (Tier 4) with optimized context

**Note**: CET is not a decision point—it's an optimization layer. All inputs to CET proceed to Imperator, but with purpose-engineered context that improves reasoning effectiveness.

### Key Characteristics

**Latency**: 100-500 milliseconds per context assembly
**Throughput**: 100-1,000 assemblies/second per MAD
**Resource**: Moderate GPU for transformer inference, significant memory for context sources
**Cost**: Cheaper than LLM inference, more expensive than LPPM
**Effectiveness Impact**: 2-3x improvement in Imperator first-attempt success rate

---

## Design Principles

### 1. Context as Carrier of Thought

Context is not merely input—it is the **fundamental carrier of thought**. The context provided to an LLM literally determines:
- What the LLM can reason about
- What knowledge is accessible
- What patterns are recognizable
- How effectively reasoning proceeds

Poor context → Poor reasoning, regardless of LLM capability
Optimal context → Optimal reasoning within LLM capability

**Critical: Optimal context is not minimal context.**

CET's goal is the **"rightest" context**, not the smallest:
- **Expand context** when critical reasoning dependencies are missing (definitions, schemas, procedures)
- **Reduce context** when noise drowns out signal
- **Enrich context** when raw data needs meta-instructions or formatting for effective reasoning
- **Compress context** only when token budget requires it

Success is measured by Imperator correctness, not token count. A 10,000-token context that produces the right answer is superior to a 1,000-token context that fails.

### 2. Purpose-Specific Assembly

Context requirements differ dramatically by task type:

**Code Generation**: Needs relevant examples, API docs, similar implementations
**Strategic Planning**: Needs goals, constraints, historical decisions, outcome patterns
**Debugging**: Needs error logs, recent changes, similar failure patterns, system state
**Creative Synthesis**: Needs diverse examples, analogies, different perspectives

CET assembles context specifically for the task at hand, not generically.

### 3. Multi-Source Optimization

Optimal context synthesizes from multiple sources:
- **Recent conversation**: Immediate context and ongoing thread
- **Historical retrieval**: Relevant past conversations and decisions (RAG)
- **Authoritative documents**: Technical documentation, specifications, policies
- **Real-time data**: Current system state, resource availability, metrics
- **Cross-domain analogies**: Related patterns from different domains

CET learns which source combinations enable successful reasoning for each task type.

### 4. Learned Context Shaping

CET learns optimal context assembly through outcome feedback:
- Observe which context assemblies led to successful Imperator reasoning
- Learn attention patterns over sources and content
- Discover token allocation strategies per source type
- **Learn necessary contextual wrappers**: Discover when raw data needs meta-instructions, definitions, or procedural context to prevent Imperator hallucinations or errors
- **Learn enrichment patterns**: Identify when adding standard operating procedures, safety checklists, or domain context improves reasoning (even if it increases token count)
- **Learn format transformations**: Discover when converting data formats (e.g., CSV → Markdown tables, logs → structured summaries) improves LLM reasoning performance
- Master compression techniques that preserve critical information (applied only when token budget requires reduction)

The system continuously improves context engineering through experience, optimizing for **Imperator correctness first**, token efficiency second.

---

## Architecture

### Component Structure

```
┌─────────────────────────────────────────────────────────────┐
│                      CET Instance                            │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         Task Classifier                               │  │
│  │  - Analyze escalated message                          │  │
│  │  - Classify task type (code gen, planning, debug...)  │  │
│  │  - Identify required reasoning capabilities           │  │
│  └──────────────┬───────────────────────────────────────┘  │
│                 ↓                                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │      Context Source Identifier                        │  │
│  │  - Recent conversation (always included)              │  │
│  │  - Historical conversations (RAG retrieval)           │  │
│  │  - Authoritative documents (domain knowledge)         │  │
│  │  - Real-time data (system state, metrics)             │  │
│  │  - Cross-domain analogies (transfer learning)         │  │
│  └──────────────┬───────────────────────────────────────┘  │
│                 ↓                                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │        Multi-Head Attention Network                   │  │
│  │  - Self-attention over task type                      │  │
│  │  - Cross-attention: task × sources                    │  │
│  │  - Learn which sources to emphasize                   │  │
│  │  - Learn token allocation per source                  │  │
│  └──────────────┬───────────────────────────────────────┘  │
│                 ↓                                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         Content Selector & Ranker                     │  │
│  │  - Select specific content from each source           │  │
│  │  - Rank by relevance to task                          │  │
│  │  - Apply domain-specific LoRA adapters                │  │
│  └──────────────┬───────────────────────────────────────┘  │
│                 ↓                                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │          Context Assembler                            │  │
│  │  - Allocate token budget per source                   │  │
│  │  - Enrich content: Add wrappers, definitions, SOPs    │  │
│  │  - Transform formats: Optimize for LLM reasoning      │  │
│  │  - Compress content: Reduce only when budget requires │  │
│  │  - Structure for optimal LLM understanding            │  │
│  │  - Include meta-information (source attribution)      │  │
│  └──────────────┬───────────────────────────────────────┘  │
│                 ↓                                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │           Learning System                             │  │
│  │  - Observe Imperator reasoning outcomes               │  │
│  │  - Learn attention patterns for task types            │  │
│  │  - Refine token allocation strategies                 │  │
│  │  - Learn enrichment patterns: When to add context     │  │
│  │  - Learn format transformations for better reasoning  │  │
│  │  - Learn compression: When budget requires reduction  │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

```
Escalated Message (from LPPM)
    ↓
Task Classification (< 50 ms)
    │
    ├─ Task Type: CODE_GENERATION
    ├─ Task Type: STRATEGIC_PLANNING
    ├─ Task Type: DEBUGGING
    ├─ Task Type: CREATIVE_SYNTHESIS
    └─ Task Type: GENERAL_REASONING
    ↓
Identify Context Sources (< 100 ms)
    │
    ├─ Recent Conversation (always)
    ├─ Historical Conversations (RAG)
    ├─ Authoritative Docs (if applicable)
    ├─ Real-time Data (system state)
    └─ Cross-domain Analogies (if beneficial)
    ↓
Attention-Based Selection (< 200 ms)
    │
    ├─ Self-attention: Task requirements
    ├─ Cross-attention: Task × Sources
    └─ Output: Source priorities + token allocations
    ↓
Content Selection & Ranking (< 100 ms)
    │
    ├─ Retrieve specific content from each source
    ├─ Rank by relevance
    └─ Select top-k items per source
    ↓
Context Assembly (< 50 ms)
    │
    ├─ Allocate tokens per source
    ├─ Enrich content: Add wrappers, definitions, SOPs
    ├─ Transform formats: Optimize for LLM reasoning
    ├─ Compress content: Reduce only when budget requires
    ├─ Structure for task type
    └─ Add meta-information
    ↓
Optimized Context → Imperator (Tier 4)
```

---

## Task Classification

### Task Types

**CODE_GENERATION**: Generate, modify, or refactor code
- Context needs: Relevant code examples, API documentation, similar implementations, coding standards

**STRATEGIC_PLANNING**: High-level planning and architecture
- Context needs: Goals, constraints, historical decisions, outcome patterns, architectural principles

**DEBUGGING**: Diagnose and fix errors
- Context needs: Error logs, recent changes, similar failure patterns, system state, relevant code

**CREATIVE_SYNTHESIS**: Novel problem-solving requiring synthesis
- Context needs: Diverse examples, analogies from different domains, different perspectives

**DATA_ANALYSIS**: Analyze and interpret data
- Context needs: Data schemas, similar analyses, statistical context, domain knowledge

**GENERAL_REASONING**: Default for uncategorized tasks
- Context needs: Broad context from multiple sources

### Classification Model

```python
class CETTaskClassifier:
    """Classify escalated tasks for purpose-specific context assembly"""

    def __init__(self, model: TransformerModel):
        self.model = model

    def classify(self, message: Message, context: ConversationContext) -> TaskType:
        """
        Classify task type in < 50 ms

        Returns: Task type + confidence + reasoning requirements
        """
        # Encode message + context
        encoding = self._encode_task(message, context)

        # Classifier head
        logits = self.model.task_classifier(encoding)
        task_type = TaskType(torch.argmax(logits).item())
        confidence = torch.softmax(logits, dim=-1).max().item()

        # Reasoning requirements
        requirements = self._identify_reasoning_requirements(
            task_type, message, context
        )

        return TaskClassification(
            task_type=task_type,
            confidence=confidence,
            requirements=requirements
        )

    def _identify_reasoning_requirements(
        self,
        task_type: TaskType,
        message: Message,
        context: ConversationContext
    ) -> ReasoningRequirements:
        """Identify what reasoning capabilities are needed"""
        requirements = ReasoningRequirements()

        # Task-specific analysis
        if task_type == TaskType.CODE_GENERATION:
            requirements.needs_examples = True
            requirements.needs_api_docs = self._mentions_apis(message)
            requirements.needs_standards = True

        elif task_type == TaskType.DEBUGGING:
            requirements.needs_error_context = True
            requirements.needs_recent_changes = True
            requirements.needs_similar_failures = True

        # ... other task types

        return requirements
```

---

## Context Source Selection

### Available Context Sources

**1. Recent Conversation** (always included)
```python
@dataclass
class RecentConversationSource:
    """Recent messages from current conversation"""
    messages: List[Message]  # Last N messages
    max_tokens: int = 2000  # Default allocation
    priority: float = 1.0  # Always highest priority
```

**2. Historical Conversations** (RAG retrieval)
```python
@dataclass
class HistoricalConversationSource:
    """Relevant past conversations via semantic search"""
    query: str  # Derived from current task
    top_k: int = 5  # Number of conversations to retrieve
    max_tokens_per_conv: int = 500
    embedding_model: str = "text-embedding-3-large"
```

**3. Authoritative Documents** (domain knowledge)
```python
@dataclass
class AuthoritativeDocumentSource:
    """Technical docs, specs, policies"""
    document_types: List[str]  # e.g., ["API_DOCS", "ARCHITECTURE"]
    query: str  # Derived from task
    top_k: int = 3
    max_tokens_per_doc: int = 1000
```

**4. Real-Time Data** (current system state)
```python
@dataclass
class RealTimeDataSource:
    """Current system metrics, logs, state"""
    data_types: List[str]  # e.g., ["METRICS", "LOGS", "STATE"]
    time_window: timedelta  # How recent
    max_tokens: int = 500
```

**5. Cross-Domain Analogies** (transfer learning)
```python
@dataclass
class CrossDomainAnalogySource:
    """Patterns from different domains that might transfer"""
    source_domains: List[str]  # Which domains to search
    similarity_threshold: float = 0.75
    max_analogies: int = 2
    max_tokens_per_analogy: int = 300
```

### Source Selection Logic

```python
class CETSourceSelector:
    """Select which context sources to use for a task"""

    def select_sources(
        self,
        task_classification: TaskClassification,
        available_sources: Dict[str, ContextSource]
    ) -> List[SelectedSource]:
        """
        Determine which sources to use and their priorities

        Returns: Ordered list of sources with token allocations
        """
        selected = []

        # Recent conversation always included
        selected.append(SelectedSource(
            source=available_sources["recent_conversation"],
            priority=1.0,
            token_allocation=2000
        ))

        # Task-specific source selection
        if task_classification.task_type == TaskType.CODE_GENERATION:
            # Prioritize examples and API docs
            if "code_examples" in available_sources:
                selected.append(SelectedSource(
                    source=available_sources["code_examples"],
                    priority=0.9,
                    token_allocation=1500
                ))
            if "api_docs" in available_sources:
                selected.append(SelectedSource(
                    source=available_sources["api_docs"],
                    priority=0.85,
                    token_allocation=1000
                ))

        elif task_classification.task_type == TaskType.DEBUGGING:
            # Prioritize error context and recent changes
            selected.append(SelectedSource(
                source=available_sources["error_logs"],
                priority=0.95,
                token_allocation=1000
            ))
            selected.append(SelectedSource(
                source=available_sources["recent_changes"],
                priority=0.90,
                token_allocation=800
            ))
            selected.append(SelectedSource(
                source=available_sources["similar_failures"],
                priority=0.85,
                token_allocation=1000
            ))

        # ... other task types

        # Historical conversations (RAG) for all tasks
        selected.append(SelectedSource(
            source=available_sources["historical_conversations"],
            priority=0.70,
            token_allocation=1500
        ))

        return selected
```

---

## Attention Mechanisms

### Multi-Head Attention Architecture

**Purpose**: Learn which context sources and content items to emphasize for each task type

**Architecture**:
```
Task Encoding (from classifier)
    ↓
Self-Attention over Task Features
    ↓
Available Sources (encoded)
    ↓
Cross-Attention: Task × Sources
    ↓
    ├─ Head 1: Recent conversation relevance
    ├─ Head 2: Historical pattern matching
    ├─ Head 3: Document relevance
    ├─ Head 4: Data importance
    └─ Head 8: Cross-domain transfer potential
    ↓
Attention Weights → Source Priorities
```

### Implementation

```python
class CETAttentionNetwork(nn.Module):
    """Multi-head attention for context source selection"""

    def __init__(
        self,
        d_model: int = 768,
        num_heads: int = 8,
        dropout: float = 0.1
    ):
        super().__init__()

        self.task_encoder = TransformerEncoder(
            d_model=d_model,
            nhead=num_heads,
            num_layers=2
        )

        self.source_encoder = TransformerEncoder(
            d_model=d_model,
            nhead=num_heads,
            num_layers=2
        )

        self.cross_attention = nn.MultiheadAttention(
            embed_dim=d_model,
            num_heads=num_heads,
            dropout=dropout
        )

        self.priority_head = nn.Linear(d_model, 1)
        self.token_allocation_head = nn.Linear(d_model, 1)

    def forward(
        self,
        task_encoding: torch.Tensor,
        source_encodings: torch.Tensor
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Compute attention over sources for task

        Args:
            task_encoding: [1, d_model] - encoded task
            source_encodings: [num_sources, d_model] - encoded sources

        Returns:
            priorities: [num_sources] - source priorities (0-1)
            token_allocations: [num_sources] - tokens per source
        """
        # Self-attention over task
        task_features = self.task_encoder(task_encoding.unsqueeze(0))

        # Self-attention over sources
        source_features = self.source_encoder(source_encodings.unsqueeze(1))

        # Cross-attention: task attends to sources
        attended_sources, attention_weights = self.cross_attention(
            query=task_features,
            key=source_features,
            value=source_features
        )

        # Compute priorities (which sources to emphasize)
        priorities = torch.sigmoid(
            self.priority_head(attended_sources.squeeze(0))
        ).squeeze(-1)

        # Compute token allocations (how many tokens per source)
        token_allocations = torch.relu(
            self.token_allocation_head(attended_sources.squeeze(0))
        ).squeeze(-1)

        # Normalize token allocations to total budget
        total_budget = 8000  # tokens available for context
        token_allocations = (
            token_allocations / token_allocations.sum() * total_budget
        )

        return priorities, token_allocations
```

### Domain-Specific LoRA Adapters

**Purpose**: Specialize attention patterns for MAD domains without full model retraining

**Architecture**: Low-Rank Adaptation (LoRA) layers for domain-specific tuning

```python
class CETWithLoRA(nn.Module):
    """CET with domain-specific LoRA adapters"""

    def __init__(
        self,
        base_model: CETAttentionNetwork,
        domains: List[str],
        lora_rank: int = 16
    ):
        super().__init__()

        self.base_model = base_model

        # LoRA adapters per domain
        self.domain_adapters = nn.ModuleDict({
            domain: LoRAAdapter(
                base_dim=768,
                rank=lora_rank
            )
            for domain in domains
        })

    def forward(
        self,
        task_encoding: torch.Tensor,
        source_encodings: torch.Tensor,
        domain: str
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """Forward with domain-specific adaptation"""

        # Base model forward
        priorities, token_allocations = self.base_model(
            task_encoding, source_encodings
        )

        # Apply domain-specific LoRA
        if domain in self.domain_adapters:
            adapter = self.domain_adapters[domain]
            priorities = priorities + adapter(priorities)
            token_allocations = token_allocations + adapter(token_allocations)

        return priorities, token_allocations
```

---

## Context Assembly

### Assembly Process

```python
class CETContextAssembler:
    """Assemble optimized context from selected sources"""

    def assemble(
        self,
        task: TaskClassification,
        sources: List[SelectedSource],
        total_budget: int = 8000
    ) -> AssembledContext:
        """
        Assemble context optimized for task

        Returns: Structured context ready for Imperator
        """
        context = AssembledContext(task_type=task.task_type)

        # Allocate tokens per source (from attention mechanism)
        allocations = self._compute_allocations(sources, total_budget)

        # Retrieve and process each source
        for source, allocation in zip(sources, allocations):
            content = self._retrieve_source_content(source, allocation)

            # Enrich content: Add wrappers, definitions, procedures if needed
            content = self._enrich_content(content, task)

            # Apply compression if budget exceeded
            if len(content.tokens) > allocation:
                content = self._compress_content(content, allocation, task)

            # Structure for task type
            structured = self._structure_for_task(content, task.task_type)

            context.add_source(source.name, structured)

        # Add meta-information
        context.add_metadata({
            "task_type": task.task_type.value,
            "source_count": len(sources),
            "total_tokens": sum(allocations),
            "assembly_strategy": "attention_optimized"
        })

        return context

    def _enrich_content(
        self,
        content: SourceContent,
        task: TaskClassification
    ) -> SourceContent:
        """
        Enrich content with necessary wrappers, definitions, and context

        The goal is the "rightest" context, not the smallest. Sometimes adding
        information improves Imperator reasoning even if it increases token count.
        """
        enriched = content.copy()

        # Task-specific enrichment patterns learned from outcomes
        if task.task_type == TaskType.CODE_GENERATION:
            # Add coding standards and best practices if missing
            if not self._has_style_guide(content):
                enriched = self._add_coding_standards(enriched, task)

            # Add API documentation context if API calls detected
            if self._contains_api_calls(content):
                enriched = self._add_api_context(enriched, task)

        elif task.task_type == TaskType.DEBUGGING:
            # Add system state context if error logs present
            if self._has_error_logs(content):
                enriched = self._add_system_state_context(enriched)

            # Add safety procedures for production systems
            if self._is_production_system(task):
                enriched = self._add_rollback_procedures(enriched)

        elif task.task_type == TaskType.STRATEGIC_PLANNING:
            # Add constraints and goals if not explicitly stated
            enriched = self._add_planning_constraints(enriched, task)

            # Add historical decision context
            enriched = self._add_decision_history(enriched, task)

        # Format transformations: Convert to LLM-optimal formats
        enriched = self._transform_format_for_reasoning(enriched, task)

        return enriched

    def _compress_content(
        self,
        content: SourceContent,
        target_tokens: int,
        task: TaskClassification
    ) -> SourceContent:
        """
        Compress content while preserving critical information

        Applied ONLY when token budget requires reduction. Compression is a
        secondary optimization after enrichment, not a primary goal.
        """

        # Task-specific compression strategies
        if task.task_type == TaskType.CODE_GENERATION:
            # Preserve code structure, compress comments
            return self._compress_code(content, target_tokens)

        elif task.task_type == TaskType.DEBUGGING:
            # Preserve error messages and stack traces, compress context
            return self._compress_debug_info(content, target_tokens)

        else:
            # Generic abstractive summarization
            return self._generic_compress(content, target_tokens)

    def _structure_for_task(
        self,
        content: SourceContent,
        task_type: TaskType
    ) -> StructuredContent:
        """Structure content optimally for task type"""

        if task_type == TaskType.CODE_GENERATION:
            return StructuredContent(
                sections=[
                    Section(title="Relevant Examples", content=content.examples),
                    Section(title="API Documentation", content=content.docs),
                    Section(title="Recent Context", content=content.conversation)
                ]
            )

        elif task_type == TaskType.STRATEGIC_PLANNING:
            return StructuredContent(
                sections=[
                    Section(title="Goals & Constraints", content=content.goals),
                    Section(title="Historical Decisions", content=content.history),
                    Section(title="Outcome Patterns", content=content.outcomes)
                ]
            )

        # ... other task types

        return StructuredContent(sections=[
            Section(title="Context", content=content.all)
        ])
```

### Context Parallelism

**Purpose**: Enable multiple file/module processing in single LLM context

**Technique**: Lay out 15+ interdependent modules in single large-context session

```python
class ParallelContextAssembler:
    """Assemble context for parallel processing of multiple items"""

    def assemble_parallel(
        self,
        items: List[ProcessingItem],
        context_window: int = 200000  # e.g., Gemini 2.0
    ) -> ParallelContext:
        """
        Assemble multiple items for simultaneous processing

        Example: 15 interdependent code modules for simultaneous development
        """
        context = ParallelContext()

        # Calculate token budget per item
        tokens_per_item = context_window // len(items)

        # Assemble each item with cross-references
        for i, item in enumerate(items):
            item_context = self._assemble_item(item, tokens_per_item)

            # Add cross-references to other items
            item_context.add_cross_references([
                CrossReference(
                    target_item=j,
                    relationship=self._analyze_relationship(items[i], items[j])
                )
                for j in range(len(items)) if i != j
            ])

            context.add_item(item_context)

        # Add global coordination instructions
        context.set_coordination_strategy(
            "Process all items simultaneously, maintaining consistency"
        )

        return context
```

---

## Learning Mechanism

### Outcome-Based Learning

**Training Signal**: Imperator reasoning outcomes with CET-assembled context

```python
@dataclass
class CETTrainingExample:
    """Training example for CET optimization"""

    # Input
    task_classification: TaskClassification
    available_sources: List[ContextSource]
    source_contents: Dict[str, Any]  # Actual retrieved content

    # CET Decision
    selected_sources: List[SelectedSource]
    attention_weights: torch.Tensor
    token_allocations: List[int]
    assembled_context: AssembledContext

    # Outcome
    imperator_success: bool  # Did Imperator solve task successfully?
    iterations_required: int  # How many back-and-forths?
    imperator_confidence: float  # Confidence in solution
    outcome_quality: float  # Validated quality (0-1)

    # Metadata
    timestamp: datetime
    conversation_id: str
    mad_name: str
```

### Training Process

```python
def train_cet_from_outcomes(
    training_examples: List[CETTrainingExample]
) -> CETAttentionNetwork:
    """
    Train CET to optimize context assembly based on Imperator outcomes

    Args:
        training_examples: V1-V3 history with CET assemblies + outcomes

    Returns:
        Trained CET network
    """
    model = CETAttentionNetwork()
    optimizer = Adam(model.parameters(), lr=1e-4)

    for epoch in range(num_epochs):
        for batch in DataLoader(training_examples, batch_size=16):

            # Forward: Predict attention weights and token allocations
            pred_priorities, pred_allocations = model(
                batch.task_encoding,
                batch.source_encodings
            )

            # Compute loss based on outcomes
            loss = compute_outcome_based_loss(
                predicted_priorities=pred_priorities,
                predicted_allocations=pred_allocations,
                actual_priorities=batch.attention_weights,
                outcomes=batch.outcome_quality  # Weight by quality
            )

            # Backward
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

    return model


def compute_outcome_based_loss(
    predicted_priorities: torch.Tensor,
    predicted_allocations: torch.Tensor,
    actual_priorities: torch.Tensor,
    outcomes: torch.Tensor
) -> torch.Tensor:
    """
    Loss function weighted by Imperator outcome quality

    Good outcomes → Reinforce these priorities/allocations
    Bad outcomes → Discourage these priorities/allocations
    """
    # Priority loss (weighted by outcomes)
    priority_loss = F.mse_loss(
        predicted_priorities,
        actual_priorities,
        reduction='none'
    )
    priority_loss = (priority_loss * (1.0 - outcomes)).mean()

    # Token allocation loss (weighted by outcomes)
    allocation_loss = F.mse_loss(
        predicted_allocations,
        actual_allocations,
        reduction='none'
    )
    allocation_loss = (allocation_loss * (1.0 - outcomes)).mean()

    return priority_loss + allocation_loss
```

---

## Integration

### MAD Integration

```typescript
class ThoughtEngine {
    private dtr: DecisionTreeRouter;
    private lppm: LearnedProseToProcessMapper;
    private cet: ContextEngineeringTransformer;
    private imperator: Imperator;

    async processMessage(message: Message): Promise<Response> {
        // DTR attempts reflexive routing (Tier 1)
        const dtrResult = await this.dtr.classify(message);
        if (dtrResult.shouldRoute) {
            return await this.actionEngine.execute(dtrResult.action);
        }

        // LPPM attempts process orchestration (Tier 2)
        const lppmResult = await this.lppm.process(message);
        if (lppmResult.canOrchestrate) {
            return await this.lppm.orchestrate(lppmResult.template);
        }

        // CET optimizes context for Imperator (Tier 3)
        const optimizedContext = await this.cet.assembleContext(
            message,
            this.conversationContext
        );

        // Imperator performs reasoning (Tier 4)
        return await this.imperator.reason(message, optimizedContext);
    }
}
```

### Training Data Pipeline

```python
def extract_cet_training_data(
    conversations: List[Conversation],
    mad_name: str
) -> List[CETTrainingExample]:
    """
    Extract CET training data from V1-V3 conversation history

    Args:
        conversations: History where Imperator reasoned
        mad_name: MAD to extract data for

    Returns:
        Training examples for CET
    """
    examples = []

    for conv in conversations:
        # Find Imperator reasoning episodes
        reasoning_episodes = identify_imperator_episodes(conv, mad_name)

        for episode in reasoning_episodes:
            # Extract task classification
            task = classify_task_retrospectively(episode)

            # Identify what context was available
            available_sources = identify_available_sources(episode)

            # Determine what context was actually used
            used_context = extract_used_context(episode)

            # Measure outcome quality
            outcome = evaluate_outcome_quality(episode)

            examples.append(CETTrainingExample(
                task_classification=task,
                available_sources=available_sources,
                assembled_context=used_context,
                imperator_success=outcome.success,
                outcome_quality=outcome.quality,
                # ... other fields
            ))

    return examples
```

---

## Performance Specifications

### Latency Targets

**Context Assembly**: 100-500 milliseconds total
- Task classification: < 50 ms
- Source selection: < 100 ms
- Attention computation: < 200 ms
- Content retrieval: < 100 ms
- Assembly & structuring: < 50 ms

**Throughput**: 100-1,000 assemblies/second
- Limited by transformer inference speed
- GPU-accelerated for production deployment

### Memory Requirements

**Model Size**: 200-500 MB
- Transformer network: ~300 MB
- Domain-specific LoRA adapters: ~50 MB per domain
- Total with 3 domains: ~450 MB

**Runtime Memory**: 2-4 GB per MAD
- Model in GPU memory: ~500 MB
- Context sources cache: ~1-2 GB
- Working memory: ~1 GB

### Effectiveness Metrics

**PRIMARY GOAL: Imperator Correctness**

**First-Attempt Success Rate**: 2-3x improvement
- Without CET: ~65% Imperator success on first attempt
- With CET: ~82-85% Imperator success on first attempt
- Measurement: Correctness of Imperator output, not token count

**Iteration Reduction**: 40-60% fewer back-and-forth cycles
- Optimal context enables complete reasoning on first attempt
- Reduces wasted Imperator calls (cost savings)

**SECONDARY GOAL: Operational Efficiency**

**Signal-to-Noise Optimization**: Improved context quality
- Eliminate irrelevant information that confuses reasoning
- Add missing dependencies (definitions, schemas, procedures)
- Transform formats for better LLM comprehension
- Success measured by Imperator correctness, not token reduction

**Cost Efficiency**: Reduced Imperator API costs
- Better context → fewer retries → lower total cost
- Token reduction is beneficial when it maintains correctness
- Token expansion is acceptable when it improves correctness

---

## Model Selection and Deployment Strategy

### Selected Model: Yi-34B-200K

**Decision Date**: 2025-12-02
**Status**: Experimental Validation Phase

#### Model Rationale

The Yi-34B-200K by 01.AI was selected as the foundational model for CET implementation based on the following criteria:

**1. Native 200,000-Token Context Window**
- Fundamental architectural requirement for CET's design principle: "Context is the carrier of thought"
- Enables processing of massive input (hundreds of pages of text) for context optimization
- Most alternative models (Llama 3, Qwen) limited to 8k-32k tokens
- Yi-34B-200K trained from scratch with extended context capabilities

**2. Optimal Size for Local Deployment**
- 34 billion parameters: Mid-size (smaller than 70B models, larger than 7B)
- 4-bit quantized footprint: ~23GB VRAM (fits on single Tesla P40/V100)
- Excellent balance between capability and deployability on available hardware
- Fine-tuning potential via QLoRA without requiring massive computational resources

**3. Architecture Quality**
- Transformer-based with proven extended context techniques
- Multi-lingual training data corpus
- Strong general language understanding across NLP tasks
- Fine-tunable for specialized CET tasks (tool use, function calling)

#### Hardware Inventory and Deployment Options

**Available Hardware**:
- 3x Tesla P40 GPUs (24GB VRAM each)
- 1x Tesla V100 GPU (32GB VRAM)
- Total raw compute: 104GB VRAM

**Deployment Strategy - Experimental Approach**

Rather than committing to a single configuration before validation, we will test multiple deployment patterns using existing hardware to inform optimal production architecture:

##### Option A: 8 Parallel Instances (Parallelism-First)
```
3x P40 + 1x V100 configured for 4 independent Yi-34B-200K instances
(one instance per GPU, running subsets of 4 total)

Configuration:
  - 3x P40: 1 instance per card (23GB used, 1GB free)
  - 1x V100: 1 instance (23GB used, 9GB free)

Strengths:
  • Maximum parallelism: 4 simultaneous independent CET requests
  • Each MAD gets dedicated GPU inference
  • No contention between contexts

Weaknesses:
  • Tight VRAM margins on P40s (minimal headroom)
  • Older P40 architecture → slower inference
  • Cannot batch multiple requests on same GPU
```

##### Option B: Single Coordinated Instance (Quality-First)
```
All 3x P40s + 1x V100 configured as single distributed Yi-34B-200K instance
(192GB total VRAM for single model instance)

Configuration:
  - Model + KV cache: ~23GB per P40 instance
  - Batch processing: Remaining 9GB+ per GPU for request batching

Strengths:
  • Massive VRAM headroom (~30GB+ free across all GPUs)
  • Can run higher-bit quantization (6-bit/8-bit vs 4-bit) → better quality
  • Larger batch sizes for throughput
  • More stable operation

Weaknesses:
  • Single model bottleneck (sequential processing flow)
  • Requires sophisticated distributed inference orchestration
  • Slower per-request latency compared to parallel
```

##### Option C: Hybrid (Recommended for Initial Testing)
```
2x P40 for parallel independent instances + 1x P40 + V100 for coordinated higher-quality instance

Configuration:
  - 2x P40: Independent instances (parallelism)
  - 1x P40 + V100: Distributed 8-bit instance (quality)

Reasoning:
  • Test both parallelism and quality approaches simultaneously
  • Parallelism: Fast response to independent requests
  • Quality: Better context engineering for complex escalations
  • Hybrid load-balancing based on request type

Cost Analysis:
  • P40: ~$160/unit → 3x = $480
  • V100: ~$900/unit → 1x = $900
  • Total current: $1,380

  • Parallelism setup: add 5x P40s (~$800) for 8-instance cluster
  • Quality setup: add 3-4x V100s (~$3,600) for distributed instances
  • Hybrid: add 2-3x P40s (~$320-480) for balanced approach
```

#### Experimental Validation Plan

**Phase 1: Baseline Measurement (Week 1)**
- Deploy Option A (4 parallel instances)
- Measure: Context assembly latency, throughput, quality
- Collect: Actual token usage patterns per task type

**Phase 2: Quality Testing (Week 2)**
- Deploy Option B (single coordinated with 8-bit quantization)
- Compare: Assembly quality vs Option A
- Measure: Difference in Imperator success rate

**Phase 3: Hybrid Configuration (Week 3)**
- Deploy Option C (2 parallel + 1 coordinated)
- Test: Load-balancing algorithm
- Measure: Cost-efficiency vs performance trade-off

**Decision Criteria**:
- Context assembly latency: Target < 500ms
- Throughput: Target 100-1,000 assemblies/second
- Quality metric: Imperator first-attempt success rate improvement
- Cost per request: Optimize for budget constraints

#### Success Metrics

**If Parallelism Wins**:
- Scale to 8x P40 cluster (~$1,280 investment)
- Optimize for independent MAD serving
- Focus on request queuing and load distribution

**If Quality Wins**:
- Scale to 4x V100 cluster (~$3,600 investment)
- Optimize for batch processing and distributed inference
- Focus on complex context engineering tasks

**If Hybrid Wins**:
- Scale to 2x P40 parallel + 4x V100 coordinated
- Implement smart routing: simple requests → parallel, complex → quality
- Focus on load-prediction and request classification

#### Next Steps

1. **Finalize deployment platform** (llama.cpp with multi-GPU support via CUDA)
2. **Set up monitoring** (latency, throughput, quality metrics)
3. **Begin Phase 1 testing** with current hardware
4. **Document findings** to inform hardware procurement strategy

---

## Training Strategy: Cloud Fine-Tuning and LoRA Considerations

### The LoRA Latency Trade-Off

Low-Rank Adaptation (LoRA) is a powerful technique for efficient model customization, but it introduces a measurable inference latency cost:

**How LoRA Works**:
- LoRA "freezes" the original model weights and trains two smaller "adapter" matrices (A and B)
- During inference, the input passes through both the original frozen weights AND the LoRA adapter weights
- Results are combined, adding an extra computational step to every token generation

**Latency Impact**:
- Each token generation requires two matrix multiplications instead of one
- This adds overhead to inference speed compared to running the base model alone
- Cumulative effect is noticeable over long context sequences

**Eliminating LoRA Latency**:
- LoRA adapter weights can be **merged** into the base model weights before deployment
- Produces a new, single-weight artifact with no adapter overhead
- Final inference speed matches the base model's speed with no performance penalty
- Enables fast, stable deployment on local P40 hardware

### Recommended Strategy: Cloud-Train, Local-Infer

Rather than accept LoRA latency for base model training, employ a hybrid workflow:

#### Phase 1: Cloud-Based Full Fine-Tuning

**Cloud Instance Rental**:
- Rent powerful GPU server (e.g., 8x NVIDIA A100 80GB or A40 48GB)
- Duration: 1 day to 24 hours total (not weeks)
- Cost: $300-$700 per training run

**Training Process**:
1. Prepare curated dataset (10,000 high-quality examples recommended)
   - Each example: "raw context" → "optimized context output"
   - Higher quality beats larger quantity for specialized tasks
2. Perform full fine-tune (updates all 34B parameters)
   - Setup and data prep: 1-2 hours
   - Actual training (2 epochs): 4-24 hours depending on instance tier
   - Quantization to GGUF: 1 hour
3. Download final quantized model (~23GB GGUF file)
4. Terminate cloud instance (cost complete)

**Estimated Timeline**:
- A100 Cluster (8x 80GB): Full process in ~8-10 hours, $300-400
- A40 Cluster (8x 48GB): Full process in ~18-24 hours, $400-700

**Key Factor**: Dataset size and hyperparameter tuning are the main variables. A focused dataset with ~10,000 examples is sufficient for a specialized Context Engineering task.

#### Phase 2: Local Deployment

Deploy the cloud-trained, fully fine-tuned model on P40 cluster:
- Single GGUF artifact (no base + adapter complexity)
- Maximum inference speed on local hardware
- Zero LoRA latency overhead
- Stable, production-ready deployment

#### Phase 3: Optional Domain-Specific LoRA Adaptation

After establishing the fully fine-tuned base CET model, use LoRAs for granular domain customization:

**Strategy**:
- Base CET model: Fully fine-tuned via cloud training (foundational quality)
- Domain LoRAs: Locally trained adapters for specific use cases
  - Example: "code-review-context" LoRA
  - Example: "architecture-documentation" LoRA
  - Example: "bug-investigation" LoRA

**Benefits**:
1. Foundational quality embedded across all parameters (base model)
2. Rapid, cost-free domain adaptation via LoRAs (local training)
3. Flexible deployment: merge LoRAs into base for critical paths (no latency)
4. Experimentation speed: iterate on domain LoRAs without retraining base

### Cost-Effectiveness Analysis

**One-Time Investment**:
- Cloud fine-tuning: $300-700 (one-time)
- Local hardware already owned: 3x P40 + 1x V100

**Continuous Cost**:
- Inference on local P40s: electricity only (~$500-1000/year)
- No per-request API costs
- No rental fees

**Payoff Timeline**:
- ROI achieved in first month compared to API-based inference
- Subsequent cost is near-zero (electricity only)
- Specialized, domain-optimized model locked-in for future use

### Implementation Recommendation

**Immediate Path**:
1. Complete Phase 1 deployment testing (Option A/B/C validation)
2. Identify optimal deployment pattern
3. Prepare training dataset (collect 5,000-10,000 curated context examples)
4. Execute cloud fine-tuning run during Phase 2 (Week 4-6)
5. Switch production to cloud-trained model for Phase 3 (Week 7+)
6. Iterate with domain LoRAs as patterns emerge

This approach maximizes local inference performance while making strategic use of cloud resources for training.

---

## Implementation Guide

### Phase 1: Task Classification (Week 1-3)

**Tasks**:
1. Design task taxonomy (CODE_GEN, DEBUGGING, etc.)
2. Implement task classifier model
3. Train on V1-V3 conversation history
4. Validate classification accuracy

**Deliverables**:
- Task classifier implementation
- Training pipeline
- Validation report (>85% accuracy)

### Phase 2: Source Selection (Week 4-6)

**Tasks**:
1. Define context source interfaces
2. Implement RAG retrieval for historical conversations
3. Build document search for authoritative sources
4. Integrate real-time data sources

**Deliverables**:
- Source selector implementation
- RAG integration
- Source availability APIs

### Phase 3: Attention Network (Week 7-10)

**Tasks**:
1. Implement multi-head attention architecture
2. Add domain-specific LoRA adapters
3. Train on V1-V3 outcome data
4. Benchmark attention computation latency

**Deliverables**:
- Attention network implementation
- LoRA adapter system
- Trained models per MAD domain

### Phase 4: Context Assembly (Week 11-13)

**Tasks**:
1. Implement context assembly logic
2. Add compression strategies per task type
3. Build context structuring system
4. Support context parallelism

**Deliverables**:
- Context assembler implementation
- Compression algorithms
- Parallel context support

### Phase 5: Integration & Validation (Week 14-16)

**Tasks**:
1. Integrate CET with Thought Engine
2. A/B test with vs without CET
3. Measure effectiveness improvements
4. Production deployment

**Deliverables**:
- Production-ready CET integration
- Performance benchmarks
- Effectiveness validation report

### Technology Stack

**Core Model**: Python 3.11+ with PyTorch 2.0+
- Transformer architecture for attention
- LoRA for domain adaptation
- GPU acceleration (CUDA/ROCm)

**MAD Integration**: TypeScript/Node.js
- Python child process for CET inference
- IPC for context passing
- Async/await for non-blocking assembly

**Context Sources**:
- MongoDB + vector embeddings (RAG)
- Redis cache for recent context
- File system for authoritative documents

---

## Future Enhancements (V5+)

### Predictive Context Assembly

**Concept**: Predict likely escalations and pre-fetch context

**Benefit**: Reduce CET latency through predictive assembly

### Collaborative Context Assembly

**Concept**: Multiple MADs contribute to shared context

**Example**: Development cycle involves Hopper + Starret + Dewey contexts

### Adaptive Compression

**Concept**: Learn task-specific compression that preserves critical info

**Research**: Neural compression models trained on reasoning outcomes

### Context Caching

**Concept**: Cache assembled contexts for similar tasks

**Benefit**: Sub-millisecond retrieval for repeated patterns

---

## References

- Vaswani, A., et al. (2017). Attention Is All You Need. NeurIPS 2017
- Lewis, P., et al. (2020). Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks. NeurIPS 2020
- Hu, E., et al. (2021). LoRA: Low-Rank Adaptation of Large Language Models. ICLR 2022
- Paper 04: Progressive Cognitive Pipeline (Tier 3 section)

---

**Navigation**: [← Tier 2 LPPM](./PCP_02_Tier2_LPPM.md) | [Index](./PCP_00_Index.md) | [Tier 4 Imperator →](./PCP_04_Tier4_Imperator.md)
