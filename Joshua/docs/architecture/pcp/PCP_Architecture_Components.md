# PCP Architecture Components - Bullet Format

**Version**: 1.0
**Purpose**: Consolidated view of all PCP tier component structures in bullet format
**Source**: Extracted from tier-specific design documents

---

## Tier 1: Decision Tree Router (DTR)

### DTR Instance Components

- **Feature Extractor**
  - Message structure analysis
  - Syntax pattern detection
  - Content marker identification
  - Complexity metrics

- **Decision Tree Classifier**
  - Hoeffding tree for online learning
  - Max depth: 10-15 levels
  - Split criteria: Information gain
  - Leaf nodes: Classification + confidence

- **Router**
  - Classification → Routing decision
  - Confidence threshold enforcement
  - Escalation path determination
  - Execution coordination

- **Learning System**
  - Outcome observation
  - Tree refinement
  - Split point adjustment
  - Performance tracking

---

## Tier 2: Learned Prose-to-Process Mapper (LPPM)

### LPPM Instance Components

- **Conversational Pattern Encoder**
  - Tokenization and embedding
  - Conversation structure encoding
  - Intent classification

- **Pattern Recognition Network**
  - Neural network (LSTM/Transformer)
  - Trained on V1 Imperator orchestrations
  - Outputs: Process ID + Confidence
  - Unknown patterns → Escalate

- **Process Template Library**
  - Learned process templates from V1
  - Multi-step workflow definitions
  - Decision point specifications
  - MAD interaction patterns

- **Orchestration Engine**
  - Execute deterministic steps
  - Coordinate multi-MAD interactions
  - Escalate decision points to Imperator
  - Integrate strategic guidance

- **Learning System**
  - Observe Imperator orchestrations
  - Extract process patterns
  - Generalize templates
  - Refine recognition network

---

## Tier 3: Context Engineering Transformer (CET)

### CET Instance Components

- **Task Classifier**
  - Analyze escalated message
  - Classify task type (code gen, planning, debug, etc.)
  - Identify required reasoning capabilities

- **Context Source Identifier**
  - Recent conversation (always included)
  - Historical conversations (RAG retrieval)
  - Authoritative documents (domain knowledge)
  - Real-time data (system state, metrics)
  - Cross-domain analogies (transfer learning)

- **Multi-Head Attention Network**
  - Self-attention over task type
  - Cross-attention: task × sources
  - Learn which sources to emphasize
  - Learn token allocation per source

- **Content Selector & Ranker**
  - Select specific content from each source
  - Rank by relevance to task
  - Apply domain-specific LoRA adapters

- **Context Assembler**
  - Allocate token budget per source
  - Apply compression where needed
  - Structure for optimal LLM understanding
  - Include meta-information (source attribution)

- **Learning System**
  - Observe Imperator reasoning outcomes
  - Learn attention patterns for task types
  - Refine token allocation strategies
  - Discover effective compression techniques

---

## Tier 4: Imperator (LLM Reasoning)

### Imperator Instance Components

- **Context Receiver**
  - V1-V3: Generic conversation context
  - V4+: CET-optimized context
  - Recent conversation history
  - MAD capabilities and state

- **LLM Selector**
  - Primary LLM for MAD domain
  - Task-specific model selection
  - Consulting team provisioning (via Fiedler)

- **Reasoning Engine**
  - Construct LLM prompt with context
  - Invoke LLM via Fiedler
  - Parse and interpret response
  - Iterative refinement if needed

- **Action Coordinator**
  - Translate reasoning to action sequences
  - Coordinate Action Engine execution
  - Orchestrate multi-MAD workflows
  - Handle execution feedback

- **Conversation Logger**
  - Record all reasoning to Rogers (conversation bus)
  - Structure for future learning (V2-V4)
  - Include decision rationale
  - Tag with outcome for training data

---

## Tier 5: Cognitive Recommendation System (CRS)

### CRS Instance Components

- **Decision Observer**
  - Monitor DTR routing decisions
  - Monitor LPPM workflow selections
  - Monitor CET context assemblies
  - Monitor Imperator reasoning paths

- **Operational History Database**
  - Store all past decisions and outcomes
  - Index by decision type, context, results
  - Enable fast pattern matching and retrieval
  - Track decision-outcome correlations

- **Pattern Matcher**
  - Compare current decision to history
  - Identify anomalies and deviations
  - Find similar past situations
  - Assess decision consistency

- **Anomaly Detector**
  - Statistical deviation analysis
  - Pattern inconsistency detection
  - Confidence assessment
  - Risk evaluation

- **Recommendation Generator**
  - Decision validation messages
  - Alternative approach suggestions
  - Capability gap identifications
  - Consultation requests

- **Learning System**
  - Track recommendation outcomes
  - Refine thresholds based on value
  - Reduce false positives over time
  - Adapt to context patterns

---

## Data Flow Between Components

### Sequential Flow (Tiers 1-4)

1. **Message Input** → DTR Feature Extractor
2. **DTR Classification** → Router Decision
3. **If Escalate** → LPPM Pattern Encoder
4. **LPPM Recognition** → Process Template Match
5. **If Escalate** → CET Task Classifier
6. **CET Assembly** → Context optimization
7. **Always Escalate** → Imperator Context Receiver
8. **Imperator Reasoning** → Action Coordinator
9. **Action Execution** → Response
10. **All Steps** → Conversation Logger

### Parallel Observation (Tier 5)

- **CRS Observes All Tiers** (non-blocking, async)
  - DTR decisions → Pattern Matcher
  - LPPM orchestrations → Anomaly Detector
  - CET assemblies → Pattern Matcher
  - Imperator reasoning → Anomaly Detector
  - All observations → Recommendation Generator
  - Recommendations → Delivered to Imperator (advisory only)

---

## Component Integration Patterns

### V1 Integration (Current)
- **Active**: Imperator (all components)
- **Inactive**: DTR, LPPM, CET, CRS
- **Data Collection**: All Imperator components log to conversation bus

### V2 Integration (Planned)
- **Active**: LPPM (all components) + Imperator
- **Inactive**: DTR, CET, CRS
- **Learning**: LPPM learns from V1 conversation history

### V3 Integration (Planned)
- **Active**: DTR (all components) + LPPM + Imperator
- **Inactive**: CET, CRS
- **Learning**: DTR learns from V1-V2 conversation history

### V4 Integration (Planned)
- **Active**: DTR + LPPM + CET (all components) + Imperator
- **Inactive**: CRS
- **Learning**: CET learns from V1-V3 reasoning outcomes

### V5 Integration (Planned)
- **Active**: All tiers (DTR + LPPM + CET + Imperator + CRS)
- **Learning**: CRS learns from all tier decisions and outcomes
- **Metacognition**: CRS provides reflective validation

---

## Component Communication Protocols

### Intra-Tier Communication
- Components within a tier communicate via direct method calls
- Data passed as structured objects (typed interfaces)
- Synchronous execution within tier

### Inter-Tier Communication
- Tiers communicate via escalation interfaces
- Asynchronous where possible (CRS observation)
- Structured escalation requests with full context

### External Communication
- **To Conversation Bus (Rogers)**: All tiers log via Conversation Logger
- **To Action Engine**: Imperator coordinates execution
- **To Fiedler**: Imperator requests LLM access
- **From User/MADs**: Messages enter via DTR (or Imperator in V1)

---

## Component Dependencies

### DTR Dependencies
- **Data**: V1-V2 conversation history for training
- **Runtime**: Trained decision tree model
- **External**: Action Engine (for deterministic execution)

### LPPM Dependencies
- **Data**: V1 conversation history with Imperator orchestrations
- **Runtime**: Trained neural network, process template library
- **External**: Action Engine, CET (for escalation)

### CET Dependencies
- **Data**: V1-V3 conversation history with outcomes
- **Runtime**: Trained transformer network, domain LoRA adapters
- **Sources**: Conversation bus, document store, real-time metrics
- **External**: Imperator (always escalates to)

### Imperator Dependencies
- **Runtime**: LLM access via Fiedler
- **Context**: CET-assembled context (V4+) or generic (V1-V3)
- **External**: Action Engine, Fiedler, Rogers

### CRS Dependencies
- **Data**: Operational history database (all past decisions)
- **Runtime**: Pattern matching algorithms, anomaly detectors
- **External**: All tiers (observes decisions), Imperator (delivers recommendations)

---

## Shared Infrastructure

### All Tiers Share

- **Conversation Bus (Rogers)**: All tiers log operations for learning and audit
- **MongoDB (Dewey)**: All tiers store and retrieve data
- **File Storage (Horace)**: All tiers access persistent files
- **Configuration**: All tiers read MAD-specific configuration

### Tier-Specific Infrastructure

- **DTR**: In-memory decision tree, minimal storage
- **LPPM**: Neural network inference, process template database
- **CET**: Transformer inference, RAG retrieval system, document indexes
- **Imperator**: LLM API access, prompt construction system
- **CRS**: Operational history database, pattern matching indexes

---

**Navigation**: [← Index](./PCP_00_Index.md) | [Overview](./PCP_Overview.md)
