# PCP Integration and Data Flow

**Version**: 1.0
**Status**: Design Phase
**Target**: Complete system integration across V1-V5

---

## Table of Contents

1. [Overview](#overview)
2. [Tier Integration Patterns](#tier-integration-patterns)
3. [Data Flow Architecture](#data-flow-architecture)
4. [Escalation Mechanisms](#escalation-mechanisms)
5. [Conversation Bus Integration](#conversation-bus-integration)
6. [Cross-Tier Learning](#cross-tier-learning)
7. [Error Handling](#error-handling)
8. [Performance Optimization](#performance-optimization)

---

## Overview

The Progressive Cognitive Pipeline integrates five tiers into a cohesive system where operations flow through progressive cognitive levels. This document details how tiers integrate, data flows between components, and the system operates as a unified whole.

### Integration Modes

**Sequential Cascade (Tiers 1-4)**:
- Operations flow through tiers in sequence
- Each tier attempts to handle or escalates to next
- Lower tiers handle routine, upper tiers handle novel

**Parallel Observer (Tier 5)**:
- CRS observes all tier decisions in parallel
- Provides advisory recommendations without blocking
- Operates alongside execution tiers

---

## Tier Integration Patterns

### V1: Imperator Only

```typescript
// V1: Single-tier architecture
class ThoughtEngineV1 {
    private imperator: Imperator;
    private actionEngine: ActionEngine;

    async processMessage(message: Message): Promise<Response> {
        // All decisions go to Imperator
        const reasoning = await this.imperator.reason(message);
        const response = await this.actionEngine.execute(reasoning.actions);

        // Record everything for V2+ learning
        await this.recordToConversationBus(message, reasoning, response);

        return response;
    }
}
```

### V2: DTR + Imperator

```typescript
// V2: Two-tier architecture
class ThoughtEngineV2 {
    private dtr: DecisionTreeRouter;
    private imperator: Imperator;
    private actionEngine: ActionEngine;

    async processMessage(message: Message): Promise<Response> {
        // DTR attempts reflexive routing
        const dtrResult = await this.dtr.classify(message);

        if (dtrResult.shouldRoute) {
            // Execute deterministically
            const response = await this.actionEngine.execute(dtrResult.action);
            await this.recordToConversationBus(message, dtrResult, response);
            return response;
        }

        // Escalate to Imperator
        const reasoning = await this.imperator.reason(message);
        const response = await this.actionEngine.execute(reasoning.actions);
        await this.recordToConversationBus(message, reasoning, response);
        return response;
    }
}
```

### V3: DTR + LPPM + Imperator

```typescript
// V3: Three-tier architecture
class ThoughtEngineV3 {
    private dtr: DecisionTreeRouter;
    private lppm: LearnedProseToProcessMapper;
    private imperator: Imperator;
    private actionEngine: ActionEngine;

    async processMessage(message: Message): Promise<Response> {
        // DTR attempts reflexive routing
        const dtrResult = await this.dtr.classify(message);

        if (dtrResult.shouldRoute) {
            // Execute deterministically
            const response = await this.actionEngine.execute(dtrResult.action);
            await this.recordToConversationBus(message, dtrResult, response);
            return response;
        }

        // LPPM attempts process orchestration
        const lppmResult = await this.lppm.recognize(message);

        if (lppmResult.canOrchestrate) {
            const response = await this.lppm.orchestrate(lppmResult.workflow);
            await this.recordToConversationBus(message, lppmResult, response);
            return response;
        }

        // Escalate to Imperator
        const reasoning = await this.imperator.reason(message);
        const response = await this.actionEngine.execute(reasoning.actions);
        await this.recordToConversationBus(message, reasoning, response);
        return response;
    }
}
```

### V4: Complete PCP (DTR + LPPM + CET + Imperator)

```typescript
// V4: Four-tier cascade architecture
class ThoughtEngineV4 {
    private dtr: DecisionTreeRouter;
    private lppm: LearnedProseToProcessMapper;
    private cet: ContextEngineeringTransformer;
    private imperator: Imperator;
    private actionEngine: ActionEngine;

    async processMessage(message: Message): Promise<Response> {
        // Tier 1: DTR reflexive routing
        const dtrResult = await this.dtr.classify(message);

        if (dtrResult.shouldRoute) {
            const response = await this.actionEngine.execute(dtrResult.action);
            await this.recordToConversationBus(message, dtrResult, response);
            return response;
        }

        // Tier 2: LPPM process orchestration
        const lppmResult = await this.lppm.recognize(message);

        if (lppmResult.canOrchestrate) {
            const response = await this.lppm.orchestrate(lppmResult.workflow);
            await this.recordToConversationBus(message, lppmResult, response);
            return response;
        }

        // Tier 3: CET context optimization
        const optimizedContext = await this.cet.assembleContext(
            message,
            this.conversationContext
        );

        // Tier 4: Imperator reasoning with optimized context
        const reasoning = await this.imperator.reason(message, optimizedContext);
        const response = await this.actionEngine.execute(reasoning.actions);
        await this.recordToConversationBus(message, reasoning, response);
        return response;
    }
}
```

### V5: Complete PCP + CRS

```typescript
// V5: Full five-tier architecture with metacognitive validation
class ThoughtEngineV5 {
    private dtr: DecisionTreeRouter;
    private lppm: LearnedProseToProcessMapper;
    private cet: ContextEngineeringTransformer;
    private imperator: Imperator;
    private crs: CognitiveRecommendationSystem;  // NEW
    private actionEngine: ActionEngine;

    async processMessage(message: Message): Promise<Response> {
        // Tiers 1-4: Sequential cascade (same as V4)
        const dtrResult = await this.dtr.classify(message);

        if (dtrResult.shouldRoute) {
            // CRS observes DTR decision (async, non-blocking)
            this.crs.observeDecision('DTR', dtrResult, message);

            const response = await this.actionEngine.execute(dtrResult.action);
            await this.recordToConversationBus(message, dtrResult, response);
            return response;
        }

        const lppmResult = await this.lppm.recognize(message);

        if (lppmResult.canOrchestrate) {
            // CRS observes LPPM decision
            this.crs.observeDecision('LPPM', lppmResult, message);

            const response = await this.lppm.orchestrate(lppmResult.workflow);
            await this.recordToConversationBus(message, lppmResult, response);
            return response;
        }

        const optimizedContext = await this.cet.assembleContext(
            message,
            this.conversationContext
        );

        // CRS observes CET context assembly
        this.crs.observeDecision('CET', optimizedContext, message);

        const reasoning = await this.imperator.reason(message, optimizedContext);

        // CRS observes Imperator reasoning
        this.crs.observeDecision('IMPERATOR', reasoning, message);

        const response = await this.actionEngine.execute(reasoning.actions);
        await this.recordToConversationBus(message, reasoning, response);
        return response;
    }
}
```

---

## Data Flow Architecture

### Message Flow Diagram

```
User/MAD Message
    ↓
Rogers (Conversation Bus)
    ↓
MAD Receives Message
    ↓
Thought Engine Entry Point
    ↓
┌─────────────────────────────────────────────┐
│ Tier 1: DTR (microseconds)                  │
│   ↓ Deterministic → Action Engine → Response│
│   ↓ Escalate ↓                              │
├─────────────────────────────────────────────┤
│ Tier 2: LPPM (milliseconds)                 │
│   ↓ Process → Orchestrate → Response        │
│   ↓ Novel/Escalate ↓                        │
├─────────────────────────────────────────────┤
│ Tier 3: CET (hundreds of ms)                │
│   ↓ Optimize Context ↓                      │
│   ↓ Always Escalate ↓                       │
├─────────────────────────────────────────────┤
│ Tier 4: Imperator (seconds)                 │
│   → Reason → Action Engine → Response       │
└─────────────────────────────────────────────┘
    ↓
Response via Rogers
    ↓
User/MAD

// Parallel Observer
Tier 5: CRS (observes all tiers, provides advisory recommendations)
```

### Data Structures

```typescript
interface Message {
    id: string;
    conversationId: string;
    sender: string;
    recipient: string;
    content: string;
    timestamp: Date;
    metadata: Record<string, any>;
}

interface TierResult {
    tier: 'DTR' | 'LPPM' | 'CET' | 'IMPERATOR';
    handled: boolean;
    escalate: boolean;
    result?: any;
    duration: number;
    confidence?: number;
}

interface ConversationContext {
    recentMessages: Message[];
    participants: string[];
    madCapabilities: MADCapabilities;
    conversationHistory: ConversationHistory;
}

interface Response {
    success: boolean;
    data: any;
    tier: string;
    duration: number;
    reasoning?: ImperatorReasoning;
    metadata: Record<string, any>;
}
```

---

## Escalation Mechanisms

### Escalation Triggers

**DTR → LPPM**:
- Low confidence classification (< 0.90)
- Novel pattern not matching training data
- Process pattern detected (requires orchestration)
- Semantic reasoning required

**LPPM → CET → Imperator**:
- Novel process element encountered
- Decision point requiring strategic judgment
- Workflow execution failure
- Unknown pattern (confidence < 0.70)

**CET → Imperator**:
- Always (CET is optimization layer)
- CET never makes execution decisions
- Provides optimized context to Imperator

**Imperator → Consulting Team**:
- Low confidence in reasoning
- Critical decision requiring validation
- Novel problem requiring diverse perspectives
- Explicit uncertainty signals

### Escalation Data

```typescript
interface EscalationRequest {
    fromTier: PCP Tier;
    toTier: PCP Tier;
    reason: EscalationReason;
    originalMessage: Message;
    tierResult: TierResult;
    context: ConversationContext;
    urgency: 'low' | 'medium' | 'high';
}

enum EscalationReason {
    LOW_CONFIDENCE = 'low_confidence',
    NOVEL_PATTERN = 'novel_pattern',
    DECISION_POINT = 'decision_point',
    EXECUTION_FAILURE = 'execution_failure',
    COMPLEXITY_THRESHOLD = 'complexity_threshold'
}
```

---

## Conversation Bus Integration

### Recording Operations

Every tier operation is recorded to the conversation bus:

```typescript
class ConversationRecorder {
    async recordTierOperation(
        tier: PCP Tier,
        message: Message,
        result: TierResult,
        response: Response
    ): Promise<void> {
        const record = {
            type: 'tier_operation',
            tier: tier,
            timestamp: new Date(),
            conversationId: message.conversationId,
            madName: this.madName,

            // Input
            message: message,
            context: this.captureContext(),

            // Processing
            tierResult: result,
            duration: result.duration,
            escalated: result.escalate,

            // Output
            response: response,
            success: response.success,

            // Metadata for learning
            tags: {
                tier: tier,
                handled: result.handled,
                confidence: result.confidence,
                useForTraining: true
            }
        };

        await this.rogers.storeMessage(record);
    }
}
```

### Learning Data Pipeline

```typescript
class LearningDataExtractor {
    // Extract DTR training data from V1-V2 conversation history
    async extractDTRTrainingData(
        conversationHistory: Conversation[],
        madName: string
    ): Promise<DTRTrainingExample[]> {
        const examples = [];

        for (const conv of conversationHistory) {
            for (const msg of conv.messages) {
                if (msg.recipient === madName) {
                    // Extract features
                    const features = this.extractFeatures(msg);

                    // Determine classification from how it was handled
                    const classification = this.inferClassification(msg, conv);

                    // Determine outcome
                    const outcome = this.inferOutcome(msg, conv);

                    examples.push({
                        features,
                        classification,
                        outcome,
                        messageId: msg.id
                    });
                }
            }
        }

        return examples;
    }

    // Extract LPPM training data from V1 conversation history
    async extractLPPMTrainingData(
        conversationHistory: Conversation[],
        madName: string
    ): Promise<LPPMTrainingExample[]> {
        // Identify orchestration episodes where Imperator coordinated workflows
        const orchestrations = this.identifyOrchestrations(
            conversationHistory,
            madName
        );

        // Extract process patterns
        return this.extractProcessPatterns(orchestrations);
    }

    // Extract CET training data from V1-V3 conversation history
    async extractCETTrainingData(
        conversationHistory: Conversation[],
        madName: string
    ): Promise<CETTrainingExample[]> {
        const examples = [];

        for (const conv of conversationHistory) {
            // Find Imperator reasoning episodes
            const reasoningEpisodes = this.identifyReasoningEpisodes(conv, madName);

            for (const episode of reasoningEpisodes) {
                // Extract task classification
                const task = this.classifyTaskRetrosp ectively(episode);

                // Identify context that was available
                const availableContext = this.identifyAvailableContext(episode);

                // Determine what context was used
                const usedContext = this.extractUsedContext(episode);

                // Measure outcome quality
                const outcome = this.evaluateOutcome(episode);

                examples.push({
                    taskClassification: task,
                    availableContext,
                    usedContext,
                    outcomeQuality: outcome.quality,
                    iterationsRequired: outcome.iterations
                });
            }
        }

        return examples;
    }
}
```

---

## Cross-Tier Learning

### Downward Optimization

**Pattern**: Imperator → LPPM → DTR

When the Imperator repeatedly handles a pattern, it should cascade down:

```typescript
class DownwardOptimizer {
    async detectOptimizationOpportunities(): Promise<OptimizationOpportunity[]> {
        // Find repeated Imperator operations
        const repeatedPatterns = await this.findRepeatedImperatorPatterns();

        const opportunities = [];

        for (const pattern of repeatedPatterns) {
            if (pattern.frequency > 10 && pattern.stability > 0.85) {
                // Stable pattern repeated 10+ times → Candidate for LPPM
                opportunities.push({
                    tier: 'LPPM',
                    pattern: pattern,
                    benefit: 'Reduce latency from seconds to milliseconds',
                    action: 'Add to LPPM training queue'
                });
            }

            if (pattern.frequency > 50 && pattern.deterministic > 0.95) {
                // Highly deterministic, frequent pattern → Candidate for DTR
                opportunities.push({
                    tier: 'DTR',
                    pattern: pattern,
                    benefit: 'Reduce latency from milliseconds to microseconds',
                    action: 'Add to DTR training data'
                });
            }
        }

        return opportunities;
    }
}
```

### Upward Escalation

When lower tiers consistently fail or escalate, patterns need re-learning:

```typescript
class EscalationAnalyzer {
    async detectRelearningNeeds(): Promise<RelearningNeed[]> {
        // Find patterns where DTR/LPPM consistently fail or escalate
        const failurePatterns = await this.findFailurePatterns();

        const needs = [];

        for (const pattern of failurePatterns) {
            if (pattern.failureRate > 0.20) {
                // 20%+ failure rate → Pattern drift, needs retraining
                needs.push({
                    tier: pattern.tier,
                    pattern: pattern,
                    issue: 'Pattern drift detected',
                    action: 'Retrain on recent data',
                    priority: 'high'
                });
            }
        }

        return needs;
    }
}
```

---

## Error Handling

### Graceful Degradation

```typescript
class GracefulDegradation {
    async handleTierFailure(
        tier: PCPTier,
        error: Error,
        message: Message
    ): Promise<Response> {
        // Log failure
        await this.logFailure(tier, error, message);

        // Escalate to next tier
        switch (tier) {
            case 'DTR':
                // DTR failed → Skip to LPPM
                return await this.lppm.process(message);

            case 'LPPM':
                // LPPM failed → Skip to Imperator
                return await this.imperator.reason(message);

            case 'CET':
                // CET failed → Imperator with generic context
                const genericContext = this.buildGenericContext();
                return await this.imperator.reason(message, genericContext);

            case 'IMPERATOR':
                // Imperator failed → Retry with different LLM or escalate to human
                return await this.handleImperatorFailure(message, error);

            default:
                throw new Error(`Unknown tier failure: ${tier}`);
        }
    }

    async handleImperatorFailure(
        message: Message,
        error: Error
    ): Promise<Response> {
        // Try fallback LLM
        try {
            return await this.imperator.reasonWithFallback(message);
        } catch (fallbackError) {
            // All LLMs failed → Escalate to human
            return {
                success: false,
                requiresHumanIntervention: true,
                error: 'All reasoning tiers failed',
                originalError: error,
                fallbackError: fallbackError
            };
        }
    }
}
```

---

## Performance Optimization

### Parallel Processing

Where possible, execute operations in parallel:

```typescript
class ParallelOptimizations {
    async processWithParallelism(message: Message): Promise<Response> {
        // When Imperator reasoning is needed, start context assembly early
        if (await this.shouldEscalateToImperator(message)) {
            // Start context assembly in parallel with final tier attempts
            const contextPromise = this.cet.assembleContext(message);

            // Try lower tiers while context assembles
            const lowerTierResult = await this.tryLowerTiers(message);

            if (lowerTierResult.handled) {
                // Lower tier handled it, cancel context assembly if possible
                return lowerTierResult.response;
            }

            // Wait for context, then use Imperator
            const context = await contextPromise;
            return await this.imperator.reason(message, context);
        }

        // Standard sequential processing
        return await this.processSequentially(message);
    }
}
```

### Caching

```typescript
class CachingOptimizations {
    async processWithCaching(message: Message): Promise<Response> {
        // Cache recent DTR classifications
        const cacheKey = this.computeDTRCacheKey(message);
        const cached = await this.cache.get(`dtr:${cacheKey}`);

        if (cached && this.isCacheValid(cached)) {
            return cached.response;
        }

        // Normal processing with cache population
        const response = await this.process(message);

        // Cache successful deterministic routes
        if (response.tier === 'DTR' && response.success) {
            await this.cache.set(`dtr:${cacheKey}`, response, ttl: 3600);
        }

        return response;
    }
}
```

---

## References

- Paper 04: Progressive Cognitive Pipeline
- Paper 02: System Evolution and Current State
- MAD Architecture v1.3

---

**Navigation**: [← Tier 5 CRS](./PCP_05_Tier5_CRS.md) | [Index](./PCP_00_Index.md) | [Learning →](./PCP_07_Learning.md)
