# PCP API Specifications

**Version**: 1.0
**Status**: Implementation Design
**Related**: [Overview](./PCP_Overview.md), [Integration](./PCP_06_Integration.md)

---

## Table of Contents

1. [Overview](#overview)
2. [Core Message Protocol](#core-message-protocol)
3. [Tier-Specific APIs](#tier-specific-apis)
4. [Inter-Tier Communication](#inter-tier-communication)
5. [External Integration APIs](#external-integration-apis)
6. [Error Handling](#error-handling)
7. [API Versioning](#api-versioning)
8. [Integration Examples](#integration-examples)

---

## Overview

This document specifies the complete API surface for the PCP system, including interfaces between tiers, external integration points, and message protocols. All APIs are designed for backward compatibility and graceful version migration.

### API Design Principles

**1. Strongly Typed Interfaces**
- All messages have defined schemas
- Runtime validation of message structure
- Type safety in implementation languages
- Clear error messages for violations

**2. Backward Compatibility**
- Additive changes only (new fields, not removed)
- Version negotiation for breaking changes
- Deprecated features maintained for migration period
- Clear deprecation timeline

**3. Async-First**
- All tier operations are async
- Non-blocking escalation
- Streaming support where applicable
- Graceful timeout handling

**4. Observable by Default**
- All API calls logged
- Trace IDs propagated
- Metrics automatically collected
- Debug mode available

---

## Core Message Protocol

### Message Base Schema

```typescript
/**
 * Base message structure for all PCP communication
 */
interface Message {
  // Identification
  id: string;  // UUID v4
  conversationId: string;  // Links messages in conversation
  parentMessageId?: string;  // For threaded conversations
  traceId: string;  // Distributed tracing ID

  // Content
  content: string;  // Primary message content
  contentType: 'text' | 'markdown' | 'code' | 'json';
  attachments?: Attachment[];  // Files, images, etc.

  // Context
  sender: MessageSender;  // Who sent this message
  recipient?: MessageRecipient;  // Specific recipient (optional)
  timestamp: number;  // Unix timestamp (ms)
  metadata: Record<string, any>;  // Extensible metadata

  // PCP-specific
  tier?: TierName;  // Which tier is processing
  escalatedFrom?: TierName;  // If escalated, from which tier
  confidence?: number;  // Confidence score (0-1)
  requiresResponse: boolean;  // Expect response?
}

interface MessageSender {
  type: 'user' | 'mad' | 'tier';
  id: string;  // User ID or MAD name or tier name
  name?: string;  // Display name
}

interface MessageRecipient {
  type: 'user' | 'mad' | 'tier' | 'broadcast';
  id?: string;  // Specific recipient ID (if not broadcast)
}

interface Attachment {
  id: string;
  type: 'file' | 'image' | 'code' | 'link';
  filename?: string;
  url?: string;
  content?: string;  // Inline content
  metadata: Record<string, any>;
}

type TierName = 'dtr' | 'lppm' | 'cet' | 'imperator' | 'crs';
```

### Response Schema

```typescript
/**
 * Standard response from PCP tier
 */
interface Response {
  // Identification
  id: string;  // Response UUID
  requestId: string;  // Original message ID
  conversationId: string;
  traceId: string;

  // Status
  status: ResponseStatus;
  tier: TierName;  // Which tier generated response
  processingTime: number;  // Milliseconds

  // Content
  content: string;  // Response content
  contentType: 'text' | 'markdown' | 'code' | 'json';
  attachments?: Attachment[];

  // Execution details
  actions?: Action[];  // Actions taken
  escalated?: boolean;  // Was this escalated?
  escalatedTo?: TierName;  // Which tier handled it

  // Metadata
  timestamp: number;
  metadata: Record<string, any>;

  // Error handling
  error?: ErrorDetails;
}

type ResponseStatus =
  | 'success'
  | 'partial_success'
  | 'escalated'
  | 'error'
  | 'timeout';

interface Action {
  type: string;  // Action type identifier
  target: string;  // What the action operates on
  parameters: Record<string, any>;
  result?: any;  // Action result (if available)
  duration?: number;  // Execution time (ms)
}

interface ErrorDetails {
  code: string;  // Error code
  message: string;  // Human-readable message
  tier: TierName;  // Where error occurred
  retryable: boolean;  // Can this be retried?
  metadata?: Record<string, any>;
}
```

---

## Tier-Specific APIs

### DTR API

```typescript
/**
 * Decision Tree Router API
 */
interface DTRAPI {
  /**
   * Classify message and route to appropriate handler
   */
  classify(request: DTRClassificationRequest): Promise<DTRClassificationResponse>;

  /**
   * Report outcome for online learning
   */
  reportOutcome(outcome: DTROutcome): Promise<void>;

  /**
   * Get current DTR statistics
   */
  getStatistics(): Promise<DTRStatistics>;
}

interface DTRClassificationRequest {
  message: Message;
  features?: FeatureVector;  // Pre-computed features (optional)
}

interface DTRClassificationResponse {
  // Classification result
  action: DTRAction;
  confidence: number;  // 0-1
  alternativeActions?: Array<{action: DTRAction; confidence: number}>;

  // Execution path
  shouldEscalate: boolean;
  escalateTo?: 'lppm' | 'imperator';

  // Metadata
  features: FeatureVector;  // Features used for classification
  treeNode?: string;  // Which tree node made decision
  processingTime: number;  // Microseconds
}

interface DTRAction {
  type: 'execute' | 'escalate' | 'route';
  target?: string;  // If routing, where to
  parameters?: Record<string, any>;
}

interface DTROutcome {
  requestId: string;
  action: DTRAction;
  success: boolean;
  actualAction?: DTRAction;  // What should have been done
  executionTime: number;
}

interface DTRStatistics {
  totalClassifications: number;
  accuracy: number;  // 0-1
  escalationRate: number;  // 0-1
  averageLatency: number;  // Microseconds
  treeDepth: number;
  treeNodes: number;
  lastTraining: number;  // Timestamp
}

type FeatureVector = number[];  // Fixed-length array
```

---

### LPPM API

```typescript
/**
 * Learned Prose-to-Process Mapper API
 */
interface LPPMAPI {
  /**
   * Recognize process pattern in message
   */
  recognizePattern(request: LPPMRecognitionRequest): Promise<LPPMRecognitionResponse>;

  /**
   * Execute process template
   */
  executeTemplate(request: LPPMExecutionRequest): Promise<LPPMExecutionResponse>;

  /**
   * Get available templates
   */
  listTemplates(filter?: TemplateFilter): Promise<ProcessTemplate[]>;

  /**
   * Add new template (for learning)
   */
  addTemplate(template: ProcessTemplate): Promise<void>;
}

interface LPPMRecognitionRequest {
  message: Message;
  candidateTemplates?: string[];  // Specific templates to consider (optional)
}

interface LPPMRecognitionResponse {
  // Recognition result
  template?: ProcessTemplate;
  confidence: number;  // 0-1
  alternativeTemplates?: Array<{template: ProcessTemplate; confidence: number}>;

  // Execution decision
  shouldExecute: boolean;
  shouldEscalate: boolean;
  escalationReason?: string;

  // Metadata
  recognitionTime: number;  // Milliseconds
}

interface LPPMExecutionRequest {
  message: Message;
  template: ProcessTemplate;
  parameters?: Record<string, any>;  // Template parameter values
}

interface LPPMExecutionResponse extends Response {
  // Execution details
  template: ProcessTemplate;
  stepsExecuted: number;
  stepsTotal: number;
  currentStep?: number;  // If paused for decision

  // Decision points
  requiresDecision?: boolean;
  decisionContext?: DecisionContext;

  // Performance
  executionTime: number;  // Milliseconds
}

interface ProcessTemplate {
  id: string;
  name: string;
  description: string;
  version: string;

  // Template structure
  steps: TemplateStep[];
  parameters: TemplateParameter[];
  decisionPoints: DecisionPoint[];

  // Metadata
  usage: number;  // How many times used
  successRate: number;  // 0-1
  averageExecutionTime: number;  // Milliseconds
  createdAt: number;
  updatedAt: number;
}

interface TemplateStep {
  id: string;
  name: string;
  action: Action;
  dependsOn: string[];  // Step IDs that must complete first
  retryable: boolean;
  timeout?: number;  // Milliseconds
}

interface TemplateParameter {
  name: string;
  type: 'string' | 'number' | 'boolean' | 'object';
  required: boolean;
  default?: any;
  validation?: string;  // Regex or JSON schema
}

interface DecisionPoint {
  id: string;
  step: string;  // Step ID where decision needed
  question: string;
  options: string[];
  escalateToImperator: boolean;
}

interface DecisionContext {
  decisionPoint: DecisionPoint;
  currentState: Record<string, any>;
  relevantHistory: Message[];
}

interface TemplateFilter {
  namePattern?: string;
  minSuccessRate?: number;
  minUsage?: number;
  tags?: string[];
}
```

---

### CET API

```typescript
/**
 * Context Engineering Transformer API
 */
interface CETAPI {
  /**
   * Assemble optimized context for task
   */
  assembleContext(request: CETAssemblyRequest): Promise<CETAssemblyResponse>;

  /**
   * Classify task type
   */
  classifyTask(message: Message): Promise<TaskClassification>;

  /**
   * Get available context sources
   */
  listContextSources(): Promise<ContextSource[]>;

  /**
   * Report reasoning outcome (for learning)
   */
  reportOutcome(outcome: CETOutcome): Promise<void>;
}

interface CETAssemblyRequest {
  message: Message;
  taskType?: TaskType;  // Pre-classified task type (optional)
  maxContextTokens?: number;  // Budget constraint
  sources?: string[];  // Specific sources to use (optional)
}

interface CETAssemblyResponse {
  // Assembled context
  context: AssembledContext;

  // Assembly details
  taskType: TaskType;
  sourcesUsed: ContextSourceUsage[];
  totalTokens: number;
  assemblyTime: number;  // Milliseconds

  // Quality metrics
  relevanceScore: number;  // 0-1 (estimated)
  coverageScore: number;  // 0-1 (how much of request covered)
}

interface AssembledContext {
  // Context sections
  recentConversation: string;  // Recent conversation history
  historicalContext?: string;  // RAG-retrieved relevant history
  authoritativeDocs?: string;  // Domain knowledge
  realTimeData?: string;  // System state, metrics
  analogies?: string;  // Cross-domain analogies

  // Metadata
  structure: ContextStructure;  // How context is organized
  sourceAttribution: Record<string, string[]>;  // Which sources contributed what
  tokenCount: number;
}

interface ContextStructure {
  sections: Array<{
    name: string;
    tokens: number;
    relevance: number;
  }>;
  compression: string;  // What compression applied
}

interface TaskType {
  primary: string;  // Main task type (e.g., 'code_generation')
  secondary?: string[];  // Additional characteristics
  complexity: 'simple' | 'medium' | 'complex';
  domain?: string;  // Specific domain (e.g., 'python', 'database')
  requiredSources: ContextSourceType[];  // Which sources needed
}

interface TaskClassification {
  taskType: TaskType;
  confidence: number;  // 0-1
  classificationTime: number;  // Milliseconds
}

interface ContextSource {
  id: string;
  type: ContextSourceType;
  name: string;
  available: boolean;
  averageLatency: number;  // Milliseconds
  tokenCost: number;  // Average tokens contributed
}

type ContextSourceType =
  | 'conversation_history'
  | 'rag_retrieval'
  | 'authoritative_docs'
  | 'real_time_data'
  | 'analogies';

interface ContextSourceUsage {
  source: ContextSource;
  tokensUsed: number;
  relevance: number;  // 0-1
  retrievalTime: number;  // Milliseconds
}

interface CETOutcome {
  requestId: string;
  context: AssembledContext;
  reasoningSuccess: boolean;
  reasoningQuality: number;  // 0-1
  contextEffectiveness: number;  // 0-1
}
```

---

### Imperator API

```typescript
/**
 * Imperator (LLM Reasoning) API
 */
interface ImperatorAPI {
  /**
   * Reason about message and generate response
   */
  reason(request: ImperatorReasoningRequest): Promise<ImperatorReasoningResponse>;

  /**
   * Continue reasoning with user decision
   */
  continueWithDecision(
    request: ImperatorContinuationRequest
  ): Promise<ImperatorReasoningResponse>;

  /**
   * Get available LLM models
   */
  listModels(): Promise<LLMModel[]>;

  /**
   * Request consulting team
   */
  requestConsultingTeam(
    request: ConsultingTeamRequest
  ): Promise<ConsultingTeamResponse>;
}

interface ImperatorReasoningRequest {
  message: Message;
  context?: AssembledContext;  // From CET (optional)
  modelPreference?: string;  // Specific LLM model
  consultingTeam?: boolean;  // Use multiple models for consensus
}

interface ImperatorReasoningResponse extends Response {
  // Reasoning details
  reasoning: ReasoningTrace;
  model: LLMModel;
  tokens: TokenUsage;

  // Actions
  actions: Action[];
  actionsExecuted: boolean;

  // Decision requests
  needsUserDecision?: boolean;
  decisionContext?: DecisionContext;

  // Performance
  reasoningTime: number;  // Milliseconds
  llmTime: number;  // Time waiting for LLM API
}

interface ReasoningTrace {
  thoughts: string[];  // Chain of thought
  assumptions: string[];  // Assumptions made
  alternatives: string[];  // Alternatives considered
  selected: string;  // Selected approach
  confidence: number;  // 0-1
}

interface LLMModel {
  id: string;
  name: string;
  provider: string;  // 'openai', 'anthropic', etc.
  contextWindow: number;  // Max tokens
  capabilities: string[];  // 'code', 'reasoning', etc.
  costPerToken: number;
  averageLatency: number;  // Milliseconds
}

interface TokenUsage {
  prompt: number;
  completion: number;
  total: number;
  cost: number;  // USD
}

interface ImperatorContinuationRequest {
  conversationId: string;
  previousResponseId: string;
  decision: UserDecision;
}

interface UserDecision {
  decisionPointId: string;
  selected: string;  // Selected option
  rationale?: string;  // Why user chose this
}

interface ConsultingTeamRequest {
  message: Message;
  context?: AssembledContext;
  models: string[];  // Which models to consult
  votingStrategy: 'majority' | 'consensus' | 'best_confidence';
}

interface ConsultingTeamResponse {
  // Individual model responses
  responses: Array<{
    model: LLMModel;
    response: ImperatorReasoningResponse;
    vote: string;  // Model's recommendation
  }>;

  // Consensus
  consensus: ImperatorReasoningResponse;
  agreement: number;  // 0-1 (how much models agreed)
  totalTime: number;  // Milliseconds
  totalCost: number;  // USD
}
```

---

### CRS API

```typescript
/**
 * Cognitive Recommendation System API
 */
interface CRSAPI {
  /**
   * Observe tier decision (non-blocking)
   */
  observeDecision(observation: CRSObservation): Promise<void>;

  /**
   * Validate decision and generate recommendations
   */
  validateDecision(
    request: CRSValidationRequest
  ): Promise<CRSValidationResponse>;

  /**
   * Report recommendation outcome
   */
  reportRecommendationOutcome(outcome: RecommendationOutcome): Promise<void>;

  /**
   * Get CRS statistics
   */
  getStatistics(): Promise<CRSStatistics>;
}

interface CRSObservation {
  tier: TierName;
  decision: any;  // Tier-specific decision
  message: Message;
  timestamp: number;
}

interface CRSValidationRequest {
  tier: TierName;
  decision: any;
  message: Message;
  urgency: 'low' | 'medium' | 'high';  // How fast response needed
}

interface CRSValidationResponse {
  // Validation result
  validated: boolean;
  issues: ValidationIssue[];
  recommendations: Recommendation[];

  // Processing
  validationTime: number;  // Milliseconds
  confidence: number;  // 0-1 (in recommendations)
}

interface ValidationIssue {
  type: 'inconsistency' | 'anomaly' | 'capability_gap' | 'risk';
  severity: 'low' | 'medium' | 'high' | 'critical';
  description: string;
  evidence: any[];  // Supporting evidence
}

interface Recommendation {
  type: 'alternative_approach' | 'consultation' | 'escalation' | 'validation';
  description: string;
  rationale: string;
  expectedImprovement: string;
  cost: 'low' | 'medium' | 'high';  // Cost of following recommendation
}

interface RecommendationOutcome {
  recommendationId: string;
  accepted: boolean;
  followed: boolean;  // If accepted, was it actually followed?
  improvementRealized: number;  // 0-1
  feedback?: string;
}

interface CRSStatistics {
  totalObservations: number;
  validationsPerformed: number;
  recommendationsMade: number;
  recommendationsAccepted: number;
  averageImprovementWhenFollowed: number;  // 0-1
  falsePositiveRate: number;  // 0-1
}
```

---

## Inter-Tier Communication

### Escalation Protocol

```typescript
/**
 * Standard escalation interface between tiers
 */
interface EscalationRequest {
  // Origin
  fromTier: TierName;
  toTier: TierName;
  reason: EscalationReason;

  // Message
  message: Message;
  priorDecisions?: PriorDecision[];  // What lower tiers tried

  // Context
  confidence: number;  // Why escalating (low confidence)
  attemptedActions?: Action[];  // What was tried
  constraints?: Record<string, any>;  // Any constraints to observe

  // Metadata
  escalationTime: number;
  traceId: string;
}

interface EscalationReason {
  code: string;
  description: string;
  category: 'low_confidence' | 'unknown_pattern' | 'decision_required' | 'error';
}

interface PriorDecision {
  tier: TierName;
  decision: any;
  confidence: number;
  timestamp: number;
}

interface EscalationResponse extends Response {
  // Handling
  handledBy: TierName;
  furtherEscalated: boolean;
  escalatedTo?: TierName;

  // Feedback for learning
  shouldHaveEscalated: boolean;
  correctTier: TierName;  // Which tier should have handled
}
```

### Conversation Bus Protocol

```typescript
/**
 * Rogers conversation bus protocol
 */
interface ConversationBusAPI {
  /**
   * Connect to conversation bus
   */
  connect(config: ConnectionConfig): Promise<Connection>;

  /**
   * Send message to conversation
   */
  sendMessage(message: Message): Promise<void>;

  /**
   * Subscribe to conversation
   */
  subscribe(
    conversationId: string,
    callback: (message: Message) => void
  ): Promise<Subscription>;

  /**
   * Query conversation history
   */
  queryHistory(query: HistoryQuery): Promise<Message[]>;

  /**
   * Store tier decision for learning
   */
  storeDecision(decision: TierDecision): Promise<void>;
}

interface ConnectionConfig {
  url: string;  // WebSocket URL
  auth?: AuthToken;
  mad: string;  // MAD name
  tier?: TierName;  // Tier name (if applicable)
}

interface Connection {
  id: string;
  status: 'connected' | 'disconnected' | 'error';
  latency: number;  // Milliseconds
  disconnect(): Promise<void>;
}

interface Subscription {
  id: string;
  conversationId: string;
  unsubscribe(): Promise<void>;
}

interface HistoryQuery {
  conversationId?: string;
  timeRange?: TimeRange;
  tiers?: TierName[];
  limit?: number;
  offset?: number;
}

interface TimeRange {
  start: number;  // Unix timestamp
  end: number;
}

interface TierDecision {
  tier: TierName;
  message: Message;
  decision: any;
  outcome: any;
  timestamp: number;
  metadata: Record<string, any>;
}
```

---

## External Integration APIs

### MAD Public API

```typescript
/**
 * Public API for MAD interaction
 */
interface MADAPI {
  /**
   * Send message to MAD
   */
  sendMessage(request: MADMessageRequest): Promise<MADMessageResponse>;

  /**
   * Get MAD capabilities
   */
  getCapabilities(): Promise<MADCapabilities>;

  /**
   * Get MAD status
   */
  getStatus(): Promise<MADStatus>;

  /**
   * Execute specific tool/action
   */
  executeTool(request: ToolExecutionRequest): Promise<ToolExecutionResponse>;
}

interface MADMessageRequest {
  message: Message;
  streamResponse?: boolean;  // Stream response in chunks
  timeout?: number;  // Milliseconds
}

interface MADMessageResponse extends Response {
  mad: string;  // MAD name
  pipelineUsed: TierName[];  // Which tiers processed
  totalTime: number;
}

interface MADCapabilities {
  mad: string;
  domain: string;  // MAD's domain
  tools: Tool[];  // Available tools
  thoughtEngine: {
    version: string;
    tiers: TierName[];  // Which tiers active
  };
  actionEngine: {
    version: string;
    actions: string[];  // Supported actions
  };
}

interface Tool {
  name: string;
  description: string;
  parameters: ToolParameter[];
  timeout: number;  // Milliseconds
}

interface ToolParameter {
  name: string;
  type: string;
  required: boolean;
  description: string;
}

interface MADStatus {
  mad: string;
  healthy: boolean;
  thoughtEngine: {
    status: 'healthy' | 'degraded' | 'error';
    activeTiers: TierName[];
    metrics: Record<string, number>;
  };
  actionEngine: {
    status: 'healthy' | 'degraded' | 'error';
    metrics: Record<string, number>;
  };
}

interface ToolExecutionRequest {
  tool: string;
  parameters: Record<string, any>;
  timeout?: number;
}

interface ToolExecutionResponse {
  tool: string;
  result: any;
  duration: number;  // Milliseconds
  success: boolean;
  error?: ErrorDetails;
}
```

### REST API

```typescript
/**
 * REST API for external integrations
 */

// POST /api/v1/messages
interface SendMessageEndpoint {
  request: {
    mad: string;
    message: {
      content: string;
      contentType?: string;
      attachments?: Attachment[];
      metadata?: Record<string, any>;
    };
    options?: {
      streamResponse?: boolean;
      timeout?: number;
    };
  };

  response: MADMessageResponse;
}

// GET /api/v1/mads
interface ListMADsEndpoint {
  response: {
    mads: Array<{
      name: string;
      domain: string;
      status: 'healthy' | 'degraded' | 'error';
      capabilities: MADCapabilities;
    }>;
  };
}

// GET /api/v1/conversations/{conversationId}
interface GetConversationEndpoint {
  params: {
    conversationId: string;
  };
  query?: {
    limit?: number;
    offset?: number;
  };

  response: {
    conversationId: string;
    messages: Message[];
    totalMessages: number;
  };
}

// GET /api/v1/metrics
interface GetMetricsEndpoint {
  query?: {
    tier?: TierName;
    timeRange?: string;  // ISO 8601 duration
  };

  response: {
    metrics: Record<string, number>;
    timestamp: number;
  };
}
```

---

## Error Handling

### Standard Error Codes

```typescript
/**
 * PCP error codes
 */
enum PCPErrorCode {
  // Request errors (4xx equivalent)
  INVALID_MESSAGE = 'PCP_400_INVALID_MESSAGE',
  UNAUTHORIZED = 'PCP_401_UNAUTHORIZED',
  RATE_LIMITED = 'PCP_429_RATE_LIMITED',
  MESSAGE_TOO_LARGE = 'PCP_413_MESSAGE_TOO_LARGE',

  // Tier errors (5xx equivalent)
  TIER_UNAVAILABLE = 'PCP_503_TIER_UNAVAILABLE',
  TIER_TIMEOUT = 'PCP_504_TIER_TIMEOUT',
  TIER_ERROR = 'PCP_500_TIER_ERROR',

  // Escalation errors
  ESCALATION_FAILED = 'PCP_500_ESCALATION_FAILED',
  NO_TIER_CAN_HANDLE = 'PCP_500_NO_TIER_CAN_HANDLE',

  // Learning errors
  INSUFFICIENT_TRAINING_DATA = 'PCP_500_INSUFFICIENT_TRAINING_DATA',
  MODEL_NOT_READY = 'PCP_503_MODEL_NOT_READY',

  // Resource errors
  LLM_API_ERROR = 'PCP_502_LLM_API_ERROR',
  DATABASE_ERROR = 'PCP_500_DATABASE_ERROR',
  CONVERSATION_BUS_ERROR = 'PCP_500_CONVERSATION_BUS_ERROR',
}

interface PCPError extends Error {
  code: PCPErrorCode;
  tier?: TierName;
  requestId?: string;
  retryable: boolean;
  retryAfter?: number;  // Milliseconds
  metadata?: Record<string, any>;
}
```

### Error Handling Strategy

```typescript
/**
 * Standard error handler for PCP operations
 */
class PCPErrorHandler {
  async handleError(
    error: PCPError,
    request: any,
    tier: TierName
  ): Promise<Response> {
    // Log error
    await this.logError(error, request, tier);

    // Determine retry strategy
    if (error.retryable && this.shouldRetry(error, request)) {
      return await this.retryRequest(request, tier);
    }

    // Determine escalation
    if (this.shouldEscalate(error, tier)) {
      return await this.escalateRequest(request, tier);
    }

    // Return error response
    return this.buildErrorResponse(error, request);
  }

  shouldRetry(error: PCPError, request: any): boolean {
    // Don't retry if already retried
    if (request.retryCount >= MAX_RETRIES) {
      return false;
    }

    // Retry on transient errors
    return [
      PCPErrorCode.TIER_TIMEOUT,
      PCPErrorCode.TIER_UNAVAILABLE,
      PCPErrorCode.LLM_API_ERROR
    ].includes(error.code);
  }

  shouldEscalate(error: PCPError, tier: TierName): boolean {
    // Escalate if tier can't handle
    if (error.code === PCPErrorCode.NO_TIER_CAN_HANDLE) {
      return tier !== 'imperator';  // Imperator is last resort
    }

    // Escalate on model errors
    if (error.code === PCPErrorCode.MODEL_NOT_READY) {
      return true;
    }

    return false;
  }
}
```

---

## API Versioning

### Version Strategy

```typescript
/**
 * API versioning and compatibility
 */
interface APIVersion {
  major: number;  // Breaking changes
  minor: number;  // New features, backward compatible
  patch: number;  // Bug fixes
}

const CURRENT_VERSION: APIVersion = {
  major: 1,
  minor: 0,
  patch: 0
};

interface VersionedAPI {
  version: APIVersion;
  deprecations?: Deprecation[];
  compatibleWith: APIVersion[];  // Versions this API can communicate with
}

interface Deprecation {
  field: string;
  deprecatedIn: APIVersion;
  removedIn: APIVersion;
  replacement?: string;
  migration: string;  // Migration guide
}

/**
 * Version negotiation for inter-tier communication
 */
class VersionNegotiator {
  negotiateVersion(
    clientVersion: APIVersion,
    serverVersions: APIVersion[]
  ): APIVersion | null {
    // Find highest compatible version
    const compatible = serverVersions.filter(v =>
      this.isCompatible(clientVersion, v)
    );

    if (compatible.length === 0) {
      return null;  // No compatible version
    }

    // Return highest version
    return compatible.reduce((max, v) =>
      this.compareVersions(v, max) > 0 ? v : max
    );
  }

  isCompatible(v1: APIVersion, v2: APIVersion): boolean {
    // Same major version = compatible
    return v1.major === v2.major;
  }

  compareVersions(v1: APIVersion, v2: APIVersion): number {
    if (v1.major !== v2.major) return v1.major - v2.major;
    if (v1.minor !== v2.minor) return v1.minor - v2.minor;
    return v1.patch - v2.patch;
  }
}
```

### Breaking Change Protocol

```typescript
/**
 * How to handle breaking changes in API
 */
interface BreakingChangeProtocol {
  // 1. Announce deprecation
  announce: {
    version: APIVersion;  // When announced
    fields: string[];  // What's being deprecated
    timeline: string;  // When it will be removed
    migration: string;  // How to migrate
  };

  // 2. Support both old and new for transition period
  transitionPeriod: {
    duration: string;  // How long both supported
    warnings: boolean;  // Emit warnings for old usage
  };

  // 3. Remove deprecated features
  removal: {
    version: APIVersion;  // When removed
    errorMessage: string;  // What to show users
  };
}

// Example: Deprecating a field
const EXAMPLE_DEPRECATION: BreakingChangeProtocol = {
  announce: {
    version: { major: 1, minor: 1, patch: 0 },
    fields: ['Message.userId'],
    timeline: 'v2.0.0',
    migration: 'Use Message.sender.id instead'
  },
  transitionPeriod: {
    duration: '6 months',
    warnings: true  // Log warning when userId used
  },
  removal: {
    version: { major: 2, minor: 0, patch: 0 },
    errorMessage: 'Message.userId removed, use Message.sender.id'
  }
};
```

---

## Integration Examples

### Example 1: Send Message to MAD (REST)

```typescript
// Using REST API
async function sendMessageToMAD(
  madName: string,
  content: string
): Promise<Response> {
  const response = await fetch('https://api.joshua.ai/v1/messages', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${API_KEY}`
    },
    body: JSON.stringify({
      mad: madName,
      message: {
        content: content,
        contentType: 'text'
      }
    })
  });

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${await response.text()}`);
  }

  return await response.json();
}

// Usage
const response = await sendMessageToMAD(
  'coding-assistant',
  'Write a function to sort an array'
);
console.log(response.content);
```

### Example 2: Connect to Conversation Bus (WebSocket)

```typescript
// Using WebSocket for conversation bus
import { WebSocket } from 'ws';

async function connectToConversationBus(
  madName: string,
  conversationId: string
): Promise<WebSocket> {
  const ws = new WebSocket('wss://rogers.joshua.ai/v1/conversations');

  // Wait for connection
  await new Promise((resolve, reject) => {
    ws.on('open', resolve);
    ws.on('error', reject);
  });

  // Authenticate
  ws.send(JSON.stringify({
    type: 'auth',
    token: API_KEY,
    mad: madName
  }));

  // Join conversation
  ws.send(JSON.stringify({
    type: 'subscribe',
    conversationId: conversationId
  }));

  // Handle messages
  ws.on('message', (data) => {
    const message = JSON.parse(data.toString());
    console.log('Received message:', message);
  });

  return ws;
}

// Usage
const ws = await connectToConversationBus('coding-assistant', 'conv-123');

// Send message
ws.send(JSON.stringify({
  type: 'message',
  content: 'Hello from external client',
  contentType: 'text'
}));
```

### Example 3: Implement Custom Tier (TypeScript)

```typescript
// Implementing a custom tier
class CustomTier {
  async process(message: Message): Promise<Response> {
    // 1. Extract features
    const features = await this.extractFeatures(message);

    // 2. Make decision
    const decision = await this.makeDecision(features);

    // 3. Check if should escalate
    if (decision.confidence < CONFIDENCE_THRESHOLD) {
      return await this.escalate(message, 'imperator');
    }

    // 4. Execute decision
    const result = await this.execute(decision);

    // 5. Log for learning
    await this.logDecision(message, decision, result);

    // 6. Return response
    return {
      id: generateUUID(),
      requestId: message.id,
      conversationId: message.conversationId,
      traceId: message.traceId,
      status: 'success',
      tier: 'custom',
      content: result.content,
      contentType: 'text',
      actions: result.actions,
      processingTime: Date.now() - startTime,
      timestamp: Date.now(),
      metadata: {}
    };
  }

  async escalate(message: Message, toTier: TierName): Promise<Response> {
    const escalationRequest: EscalationRequest = {
      fromTier: 'custom',
      toTier: toTier,
      reason: {
        code: 'low_confidence',
        description: 'Confidence below threshold',
        category: 'low_confidence'
      },
      message: message,
      confidence: 0.5,
      escalationTime: Date.now(),
      traceId: message.traceId
    };

    return await this.nextTier.process(escalationRequest);
  }
}
```

### Example 4: Query PCP Metrics (Python)

```python
# Query PCP performance metrics
import requests
from datetime import datetime, timedelta

def get_pcp_metrics(tier=None, hours_ago=24):
    """
    Get PCP metrics for analysis
    """
    url = 'https://api.joshua.ai/v1/metrics'

    params = {
        'timeRange': f'PT{hours_ago}H'  # ISO 8601 duration
    }

    if tier:
        params['tier'] = tier

    response = requests.get(
        url,
        params=params,
        headers={'Authorization': f'Bearer {API_KEY}'}
    )

    response.raise_for_status()
    return response.json()

# Usage
metrics = get_pcp_metrics(tier='dtr', hours_ago=24)

print(f"DTR Latency (p99): {metrics['dtr.latency.p99']}ms")
print(f"DTR Escalation Rate: {metrics['dtr.escalation_rate'] * 100}%")
print(f"DTR Accuracy: {metrics['dtr.accuracy'] * 100}%")
```

---

**Navigation**: [← Performance](./PCP_09_Performance.md) | [Index](./PCP_00_Index.md)
