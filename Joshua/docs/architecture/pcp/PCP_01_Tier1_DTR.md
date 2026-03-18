# Tier 1: Decision Tree Router (DTR)

**Version**: 1.0
**Status**: Design Phase (V2 Planned)
**Implementation Target**: V2

---

## Table of Contents

1. [Overview](#overview)
2. [Design Principles](#design-principles)
3. [Architecture](#architecture)
4. [Feature Extraction](#feature-extraction)
5. [Classification Algorithm](#classification-algorithm)
6. [Routing Logic](#routing-logic)
7. [Learning Mechanism](#learning-mechanism)
8. [Integration](#integration)
9. [Performance Specifications](#performance-specifications)
10. [Implementation Guide](#implementation-guide)

---

## Overview

### Purpose

The Decision Tree Router (DTR) provides **reflexive routing** in microseconds for deterministic operations. Like spinal reflexes that bypass the brain for immediate response, DTR bypasses expensive LLM processing for operations following learned patterns.

### Position in PCP

**Tier 1** - First filter in the cognitive cascade:
- Receives all incoming messages
- Routes deterministic operations directly to Action Engine
- Escalates uncertain/novel operations to LPPM (Tier 2)

### Key Characteristics

**Latency**: 10-100 microseconds per classification
**Throughput**: 10,000-100,000 classifications/second
**Resource**: Minimal CPU, negligible memory, no GPU
**Cost**: Effectively free (amortized infrastructure only)
**Accuracy Target**: 95%+ for deterministic classifications

---

## Design Principles

### 1. Reflexive Speed

DTR must operate at reflexive timescales—microseconds, not milliseconds. This requires:
- Shallow decision tree (max depth 10-15)
- Minimal feature computation
- In-memory operation (no I/O during classification)
- Compiled decision paths

### 2. Conservative Escalation

**False negatives** (escalate when could handle) are acceptable.
**False positives** (route deterministically when should escalate) cause failures.

DTR errs on the side of escalation—better to occasionally send deterministic operations to LPPM than to mis-route semantic operations deterministically.

### 3. Incremental Learning

DTR learns online from streaming operations:
- No batch retraining required
- Hoeffding tree or similar online learning algorithm
- Continuous refinement as patterns emerge
- Graceful adaptation to changing message patterns

### 4. Domain Specialization

Each MAD has its own DTR instance trained on domain-specific messages:
- Dewey DTR learns database query patterns
- Horace DTR learns file operation patterns
- Fiedler DTR learns LLM request patterns

Shared algorithm, separate training data, domain-specific behavior.

---

## Architecture

### Component Structure

```
┌─────────────────────────────────────────────────────────────┐
│                       DTR Instance                           │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │            Feature Extractor                          │  │
│  │  - Message structure analysis                         │  │
│  │  - Syntax pattern detection                           │  │
│  │  - Content marker identification                      │  │
│  │  - Complexity metrics                                 │  │
│  └──────────────┬───────────────────────────────────────┘  │
│                 ↓                                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         Decision Tree Classifier                      │  │
│  │  - Hoeffding tree for online learning                 │  │
│  │  - Max depth: 10-15 levels                            │  │
│  │  - Split criteria: Information gain                   │  │
│  │  - Leaf nodes: Classification + confidence            │  │
│  └──────────────┬───────────────────────────────────────┘  │
│                 ↓                                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Router                                   │  │
│  │  - Classification → Routing decision                  │  │
│  │  - Confidence threshold enforcement                   │  │
│  │  - Escalation path determination                      │  │
│  │  - Execution coordination                             │  │
│  └──────────────┬───────────────────────────────────────┘  │
│                 ↓                                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │           Learning System                             │  │
│  │  - Outcome observation                                │  │
│  │  - Tree refinement                                    │  │
│  │  - Split point adjustment                             │  │
│  │  - Performance tracking                               │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

```
Message Input
    ↓
Feature Extraction (< 10 μs)
    ↓
Decision Tree Traversal (< 50 μs)
    ↓
Routing Decision + Confidence
    ↓
    ├─ Deterministic (high confidence)
    │      → Execute via Action Engine
    │      → Record outcome for learning
    │
    ├─ Fixed Data (high confidence)
    │      → Process via data handlers
    │      → Record outcome for learning
    │
    └─ Uncertain / Novel (low confidence)
           → Escalate to LPPM (Tier 2)
           → Record pattern for future learning
```

---

## Feature Extraction

### Input Features

DTR analyzes message characteristics without semantic processing:

**1. Structural Features** (5-10 features)
- Message format: JSON, plain text, mixed, command-like
- Length: Character count, token estimate
- Nesting depth: For structured formats
- Field count: Number of distinct elements

**2. Syntax Features** (10-15 features)
- Keyword presence: EXECUTE, QUERY, STORE, FETCH, etc.
- Command prefix: Starts with deterministic trigger
- Delimiter patterns: Specific punctuation indicating structure
- Case patterns: ALL_CAPS_COMMANDS vs natural prose
- Symbol density: Ratio of symbols to alphanumeric

**3. Content Markers** (5-10 features)
- Operation tokens: Specific verbs indicating deterministic actions
- Entity references: File paths, database names, identifiers
- Parameter structures: Key-value pairs, argument lists
- Question indicators: ? mark, question words
- Imperative vs declarative: Command vs description

**4. Context Features** (5 features)
- Source participant: Which MAD sent the message
- Conversation state: Turn number, recent message types
- Timestamp: Time of day (some operations time-dependent)
- Recent routing history: What DTR routed in last N messages

**Total**: 25-40 features (keep minimal for speed)

### Feature Computation

**Implementation**:
```python
class DTRFeatureExtractor:
    """Extract features from messages for DTR classification"""

    def extract(self, message: Message) -> FeatureVector:
        """
        Extract features in < 10 microseconds

        Returns: Fixed-size float vector (25-40 dimensions)
        """
        features = []

        # Structural features (pre-computed when possible)
        features.extend(self._structural_features(message))

        # Syntax features (regex-based, fast)
        features.extend(self._syntax_features(message))

        # Content markers (keyword matching)
        features.extend(self._content_markers(message))

        # Context features (from conversation state)
        features.extend(self._context_features(message))

        return np.array(features, dtype=np.float32)

    def _structural_features(self, message: Message) -> List[float]:
        return [
            float(len(message.content)),  # Length
            float(self._is_json(message)),  # Is JSON
            float(self._nesting_depth(message)),  # Nesting
            float(self._field_count(message)),  # Fields
        ]

    def _syntax_features(self, message: Message) -> List[float]:
        content = message.content
        return [
            float(bool(re.search(r'^(EXECUTE|QUERY|STORE|FETCH)', content))),
            float(bool(re.search(r'[A-Z_]{5,}', content))),  # ALL_CAPS pattern
            float(content.count(':') / max(len(content), 1)),  # Colon density
            float(content.count('{') / max(len(content), 1)),  # Brace density
            # ... additional syntax features
        ]

    def _content_markers(self, message: Message) -> List[float]:
        content_lower = message.content.lower()
        return [
            float('execute' in content_lower),
            float('query' in content_lower),
            float('retrieve' in content_lower),
            float('store' in content_lower),
            float('?' in message.content),  # Question
            # ... additional content markers
        ]

    def _context_features(self, message: Message) -> List[float]:
        return [
            float(hash(message.sender) % 100) / 100.0,  # Sender encoding
            float(message.turn_number),
            float(self._time_of_day_bucket()),
        ]
```

---

## Classification Algorithm

### Hoeffding Tree (Online Learning)

**Algorithm**: Very Fast Decision Tree (VFDT) / Hoeffding Tree

**Characteristics**:
- Online learning from streaming data
- No batch retraining required
- Logarithmic classification time: O(log n) in tree depth
- Sub-linear training time per example
- Theoretical guarantees on convergence

**Why Hoeffding Tree**:
- Handles streaming message data naturally
- Adapts to changing patterns without retraining
- Fast classification (microseconds)
- Well-studied algorithm with robust implementations

### Tree Structure

**Split Criteria**: Information Gain

**Leaf Nodes**: Store classification + confidence
```python
class LeafNode:
    classification: Classification  # DETERMINISTIC, FIXED_DATA, ESCALATE
    confidence: float  # 0.0 to 1.0
    sample_count: int  # Training examples reaching this leaf
    class_distribution: Dict[Classification, int]  # For confidence calc
```

**Internal Nodes**: Store split condition
```python
class InternalNode:
    feature_index: int  # Which feature to split on
    threshold: float  # Split value
    left_child: Node  # feature <= threshold
    right_child: Node  # feature > threshold
```

**Max Depth**: 10-15 levels (limits worst-case latency)

**Pruning**: Conservative—prefer shallow, high-confidence paths

### Classification Confidence

**Confidence Calculation**:
```
confidence = max(class_distribution) / sum(class_distribution)
```

**Thresholds**:
- confidence ≥ 0.90: High confidence, route deterministically
- confidence ≥ 0.70: Medium confidence, route with monitoring
- confidence < 0.70: Low confidence, escalate to LPPM

**Uncertainty Handling**: When in doubt, escalate.

---

## Routing Logic

### Classification Categories

**1. DETERMINISTIC**: Commands with fixed execution paths
- Examples: `EXECUTE_TEST suite_name`, `QUERY_STATUS`, `GET_FILE path`
- Action: Execute directly via Action Engine
- No semantic processing required

**2. FIXED_DATA**: Structured data requiring processing
- Examples: JSON objects, schema definitions, configuration data
- Action: Process via domain-specific data handlers
- Validation and transformation without reasoning

**3. PROCESS**: Patterns matching learned workflows
- Examples: "Run development cycle", "Generate report"
- Action: Escalate to LPPM (Tier 2) for process orchestration
- LPPM has learned workflow for this pattern

**4. PROSE**: Natural language requiring semantic understanding
- Examples: Novel questions, creative requests, complex reasoning
- Action: Escalate to LPPM → CET → Imperator (Tiers 2-4)
- Full LLM reasoning required

### Routing Decision Tree

```
Classify Message
    ↓
    ├─ Classification: DETERMINISTIC + Confidence ≥ 0.90
    │      → Route to Action Engine
    │      → Execute deterministically
    │      → Record outcome
    │
    ├─ Classification: FIXED_DATA + Confidence ≥ 0.90
    │      → Route to Data Handler
    │      → Process structure
    │      → Record outcome
    │
    ├─ Classification: PROCESS + Confidence ≥ 0.70
    │      → Escalate to LPPM (Tier 2)
    │      → LPPM orchestrates workflow
    │      → Record pattern
    │
    └─ Classification: PROSE or Low Confidence
           → Escalate to LPPM (Tier 2)
           → LPPM → CET → Imperator as needed
           → Record for learning
```

### Escalation Paths

**To LPPM (Tier 2)**:
- All PROCESS classifications
- All PROSE classifications
- Low confidence DETERMINISTIC/FIXED_DATA

**Direct to Action Engine**:
- Only high-confidence DETERMINISTIC
- Well-established patterns with proven success

**To Data Handlers**:
- Only high-confidence FIXED_DATA
- Structural processing without reasoning

---

## Learning Mechanism

### Online Learning Process

```
1. DTR classifies message → routes accordingly

2. Execution happens (Action Engine or escalation)

3. Outcome observed:
   - Success: Routing was correct
   - Failure: Routing was incorrect
   - Escalation required: Classification was conservative

4. DTR updates:
   - Correct routing: Reinforce decision path
   - Incorrect routing: Weaken decision path
   - Escalation: Analyze if future similar messages could route directly

5. Tree refinement:
   - Adjust split points based on new examples
   - Grow tree if necessary (within max depth)
   - Prune low-confidence branches
```

### Training Examples

**Format**:
```python
@dataclass
class TrainingExample:
    features: np.ndarray  # Feature vector (25-40 dimensions)
    classification: Classification  # DETERMINISTIC, FIXED_DATA, PROCESS, PROSE
    outcome: Outcome  # SUCCESS, FAILURE, ESCALATED
    timestamp: datetime
    message_id: str  # For traceability
```

**Sources**:
- **V1 Conversation History**: Observe Imperator routing decisions
- **V2 Online**: Real-time DTR routing outcomes
- **V3 LPPM Patterns**: Observe LPPM escalation vs handling

**Collection**:
- Every message processed by Thought Engine generates training example
- Stored in conversation bus (Rogers via Dewey)
- Retrievable for DTR training across MAD restarts

### Incremental Training

**Algorithm**: Hoeffding Tree update
```python
def update_tree(self, example: TrainingExample):
    """
    Update DTR with new training example

    Time complexity: O(log n) in tree depth
    """
    # 1. Find leaf node for this example
    leaf = self._traverse_to_leaf(example.features)

    # 2. Update class distribution at leaf
    leaf.class_distribution[example.classification] += 1
    leaf.sample_count += 1

    # 3. Check if leaf should split
    if self._should_split(leaf):
        # Compute information gain for each feature
        best_feature, best_threshold = self._find_best_split(leaf)

        # Split leaf into internal node with two children
        self._split_leaf(leaf, best_feature, best_threshold)

    # 4. Update confidence scores
    leaf.confidence = max(leaf.class_distribution.values()) / leaf.sample_count
```

**Hoeffding Bound**: Determines when to split based on information gain with statistical confidence

### Adaptation to Drift

**Pattern Drift Detection**:
- Monitor classification accuracy over time windows
- If accuracy drops > 10% over 1000 messages, trigger adaptation
- Increase learning rate temporarily
- Re-evaluate split points

**Graceful Degradation**:
- If DTR accuracy degrades, increase escalation threshold
- Route conservatively until patterns restabilize
- Better to escalate unnecessarily than to mis-route

---

## Integration

### MAD Integration

**Location**: Within Thought Engine, first component executed

**Initialization**:
```typescript
class ThoughtEngine {
    private dtr: DecisionTreeRouter;
    private lppm: LearnedProseToProcessMapper;
    private cet: ContextEngineeringTransformer;
    private imperator: Imperator;

    constructor(config: ThoughtEngineConfig) {
        // DTR initialized first
        this.dtr = new DecisionTreeRouter({
            madName: config.madName,
            featureExtractor: new DTRFeatureExtractor(),
            maxDepth: 15,
            confidenceThreshold: 0.90,
        });

        // Other tiers...
    }

    async processMessage(message: Message): Promise<Response> {
        // DTR attempts reflexive routing first
        const dtrResult = await this.dtr.classify(message);

        if (dtrResult.shouldRoute) {
            // High confidence deterministic routing
            return await this.actionEngine.execute(dtrResult.action);
        } else {
            // Escalate to LPPM (Tier 2)
            return await this.lppm.process(message);
        }
    }
}
```

### Training Data Pipeline

**V1 → V3 Transition**:
1. V1 conversation history contains all Imperator routing decisions
2. Extract training examples: message → classification → outcome
3. Pre-train DTR on V1 historical data before V3 deployment
4. Continue online learning in V3 from real-time outcomes

**Training Extraction**:
```python
def extract_dtr_training_data(
    conversation_history: List[Message],
    mad_name: str
) -> List[TrainingExample]:
    """
    Extract DTR training examples from V1 conversation history

    Args:
        conversation_history: V1 messages processed by Imperator
        mad_name: MAD to extract data for

    Returns:
        List of training examples for DTR
    """
    examples = []

    for message in conversation_history:
        if message.recipient != mad_name:
            continue  # Not for this MAD

        # Extract features
        features = feature_extractor.extract(message)

        # Determine classification from Imperator's handling
        classification = infer_classification(message)

        # Determine outcome from execution result
        outcome = infer_outcome(message)

        examples.append(TrainingExample(
            features=features,
            classification=classification,
            outcome=outcome,
            timestamp=message.timestamp,
            message_id=message.id
        ))

    return examples
```

### Cross-MAD Learning

**Shared**: Algorithm implementation (Hoeffding tree code)

**Separate**: Training data and trained models
- Each MAD trains on its domain-specific message patterns
- Dewey DTR learns database patterns
- Horace DTR learns file patterns
- Fiedler DTR learns LLM request patterns

**Potential Future**: Transfer learning for abstract patterns
- Research question: Can abstract routing principles transfer?
- Example: "Execute X" pattern might transfer across domains
- Not implemented in V3, potential V4+ enhancement

---

## Performance Specifications

### Latency Targets

**Classification**: 10-100 microseconds (0.01-0.1 ms)
- Feature extraction: < 10 μs
- Tree traversal: < 50 μs
- Routing decision: < 10 μs
- Total: < 100 μs worst case

**Throughput**: 10,000-100,000 classifications/second
- Single-threaded: 10,000 ops/sec
- Multi-threaded (per MAD): 100,000 ops/sec

**Memory**: < 10 MB per DTR instance
- Tree structure: ~1-5 MB
- Feature extractor: ~1 MB
- Training buffer: ~2-5 MB

**CPU**: < 1% utilization at steady state
- Minimal computation per classification
- Negligible training overhead online

### Accuracy Targets

**Overall Accuracy**: 95%+
- Measured as: Correct routing decisions / Total classifications

**False Positive Rate**: < 1%
- False positives: Route deterministically when should escalate
- Most costly errors (cause failures)

**False Negative Rate**: < 10%
- False negatives: Escalate when could route deterministically
- Less costly (slight inefficiency)

**Confidence Calibration**: ±5%
- Reported confidence should match actual accuracy
- confidence=0.95 → 95% actual accuracy

### Scalability

**Message Volume**:
- Designed for 10K-100K messages/day per MAD
- Tested up to 1M messages/day

**Training Data**:
- Efficient online learning, no batch retraining
- Tree grows logarithmically with training examples

**Concurrent Operations**:
- Stateless classification (threadable)
- Lock-free tree traversal (read-only)
- Batched tree updates (minimize contention)

---

## Implementation Guide

### Phase 1: Feature Extraction (Week 1-2)

**Tasks**:
1. Implement `DTRFeatureExtractor` class
2. Define feature vector schema (25-40 dimensions)
3. Optimize extraction for < 10 μs latency
4. Unit test feature extraction

**Deliverables**:
- `dtr_feature_extractor.py`
- Feature extraction tests
- Benchmark: < 10 μs average

### Phase 2: Decision Tree (Week 3-5)

**Tasks**:
1. Implement Hoeffding tree algorithm
2. Support online learning with streaming data
3. Enforce max depth and confidence thresholds
4. Unit test tree operations

**Deliverables**:
- `hoeffding_tree.py`
- Tree algorithm tests
- Benchmark: < 50 μs traversal

**Library Option**: Consider using existing Hoeffding tree implementation (e.g., `river` Python library) if performance adequate

### Phase 3: Router Integration (Week 6-7)

**Tasks**:
1. Implement `DecisionTreeRouter` class
2. Integrate with Thought Engine message flow
3. Add routing logic and escalation paths
4. Integration tests with Action Engine

**Deliverables**:
- `decision_tree_router.ts` (Node.js MAD runtime)
- Python training module calls from TypeScript
- Integration tests

### Phase 4: Training Pipeline (Week 8-9)

**Tasks**:
1. Implement training data extraction from V1 history
2. Pre-training process for V3 deployment
3. Online learning integration
4. Training data management

**Deliverables**:
- `dtr_training_pipeline.py`
- V1 data extraction scripts
- Training orchestration

### Phase 5: Validation & Tuning (Week 10-12)

**Tasks**:
1. Validate DTR accuracy on V1 held-out data
2. Tune confidence thresholds
3. Performance benchmarking
4. Production readiness review

**Deliverables**:
- Validation report
- Performance benchmarks
- Production deployment plan

### Technology Stack

**Classification Engine**: Python 3.11+
- `numpy` for feature vectors
- `river` for Hoeffding tree (or custom implementation)
- `msgpack` for serialization

**MAD Integration**: TypeScript/Node.js
- Python child process or FFI for DTR calls
- IPC for feature passing and classification results
- Async/await for non-blocking classification

**Training Infrastructure**: Python
- `pandas` for training data management
- `joblib` for model persistence
- Integration with Rogers/Dewey for data retrieval

### Testing Strategy

**Unit Tests**:
- Feature extraction correctness and speed
- Decision tree algorithm correctness
- Online learning convergence
- Edge cases (empty messages, malformed data)

**Integration Tests**:
- DTR → Action Engine routing
- DTR → LPPM escalation
- End-to-end message flow

**Performance Tests**:
- Latency benchmarks (99th percentile < 100 μs)
- Throughput tests (10K+ ops/sec)
- Memory profiling

**Accuracy Tests**:
- Accuracy on V1 held-out data
- Confidence calibration
- False positive/negative rates

---

## Future Enhancements (V4+)

### Pattern Transfer Learning

**Concept**: Transfer abstract routing patterns across MAD domains

**Example**: "EXECUTE X" pattern learned by Dewey might transfer to Horace

**Research**: Investigate meta-learning for cross-domain transfer

### Multi-Tier Lookahead

**Concept**: DTR predicts full routing path (DTR → LPPM → Imperator)

**Benefit**: Pre-fetch context early, reduce latency

**Complexity**: Requires coordination with LPPM and CET

### Ensemble Classification

**Concept**: Multiple decision trees voting on classification

**Benefit**: Higher accuracy, better confidence estimates

**Cost**: Increased latency (still sub-millisecond)

### Constitutional Constraints

**Concept**: Hard-coded routing rules for safety/compliance

**Example**: "Never route financial operations deterministically"

**Integration**: Pre-filter before DTR classification

---

## References

- Domingos, P., & Hulten, G. (2000). Mining High-Speed Data Streams. KDD 2000
- Bifet, A., & Gavaldà, R. (2009). Adaptive Learning from Evolving Data Streams
- Paper 04: Progressive Cognitive Pipeline (Tier 1 section)
- Paper 02: System Evolution (V3 Implementation)

---

**Navigation**: [← Overview](./PCP_Overview.md) | [Index](./PCP_00_Index.md) | [Tier 2 LPPM →](./PCP_02_Tier2_LPPM.md)
