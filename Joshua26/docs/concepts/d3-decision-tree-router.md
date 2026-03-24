# Concept: The Decision Tree Router (DTR)

**Status:** Concept **Date:** 2026-03-04
**Maturity:** Designed, Not Yet Built

***

## Author

**J. Morrissette**

***

## What is a Decision Tree Router?

A Decision Tree Router (DTR) is a fast, non-LLM routing component that sits at the entry point of a processing pipeline. Its purpose is to classify incoming requests and route them to the appropriate handler — bypassing expensive LLM invocation entirely for requests that match learned, high-confidence patterns.

The defining characteristic of a DTR is that it operates at reflexive timescales — microseconds, not milliseconds — and it learns. Unlike a static rule file, a DTR trains continuously from the outcomes of the requests it processes. Over time it becomes faster and more accurate at recognizing the patterns it has seen before, while remaining conservative about novel or ambiguous cases.

***

## The Core Problem It Solves

In a system where agents or pipelines receive high-volume, repeated requests, a naive implementation invokes an LLM for every request regardless of complexity. This is expensive, slow, and unnecessary: the vast majority of requests in any established system are routine, follow known patterns, and do not require reasoning to handle correctly.

The DTR solves this by acting as a learned first filter. It does not replace LLM reasoning — it protects it. Novel, ambiguous, or sensitive requests are escalated to the appropriate agent for deliberate handling. Routine, well-understood requests are dispatched immediately without engaging the LLM at all.

***

## How It Works

### Feature Extraction

The DTR extracts a compact feature vector from each incoming request. For structured requests (where the inputs are discrete typed fields), this is trivial and near-instantaneous by comparison to an LLM call. For less structured inputs, features may include structural characteristics, keyword presence, content markers, and context signals from the conversation or request history.

The feature vector is kept small (typically 25–40 dimensions) to keep extraction time below 10 microseconds.

### Classification

The extracted feature vector is passed through a decision tree classifier — specifically a Hoeffding tree (also called a Very Fast Decision Tree). The Hoeffding tree supports online learning: it updates continuously from streaming data without requiring batch retraining. This makes it ideal for a system that must adapt to changing patterns at runtime.

The tree produces a classification and a confidence score. Three outcomes are possible:

-   **ALLOW** — the request is a known safe, routine pattern; proceed directly to execution
-   **DENY** — the request matches a known violation pattern; reject immediately
-   **DEFER** — confidence is insufficient; escalate to the responsible agent for deliberate handling

### Confidence Thresholds

Routing decisions are only made deterministically when confidence exceeds a configured threshold (typically 0.90 for ALLOW/DENY). Below this threshold, the DTR defers regardless of the nominal classification. This is intentional: the cost of an incorrect deterministic routing decision is always higher than the cost of an unnecessary escalation.

**False negatives** (escalating when the DTR could have handled it) are acceptable. **False positives** (routing deterministically when the agent should have decided) are not.

### Constitutional Constraints

Before the DTR, a set of hard-coded constitutional constraints acts as an unconditional pre-filter. These are rules that must never be learned away — absolute denials or absolute allows that exist outside the scope of learned behavior. They execute before feature extraction and cannot be overridden by the DTR's classification.

Examples: a hard deny on operations affecting system-critical paths; a hard allow on a known safe internal health check.

### Online Learning

After every request is handled, the DTR observes the outcome and updates its tree accordingly. Correct routing reinforces the decision path. Incorrect routing weakens it. Escalated requests that the agent approved are noted as potential candidates for future fast-path routing.

This feedback loop means the DTR gets progressively faster as patterns stabilize, while remaining able to adapt if patterns shift (drift detection can trigger a temporary increase in the escalation rate to recalibrate).

***

## Performance Design Targets

These are design targets derived from the theoretical characteristics of Hoeffding trees at the described feature vector size. They have not been measured in a Joshua implementation — the DTR has not been built. Actual performance will depend on hardware, feature vector dimensionality, and tree depth at deployment time.

-   **Classification latency**: 10–100 microseconds (design target)
-   **Throughput**: 10,000–100,000 classifications per second (design target)
-   **Memory footprint**: \< 10 MB per instance (design target)
-   **CPU utilisation**: \< 1% at steady state (design target)
-   **No GPU required**

***

## Domain Specialisation

Each DTR instance is trained on the request patterns of its specific domain. The algorithm is shared; the training data and trained model are not. A DTR trained on filesystem access patterns will not behave the same as one trained on database query patterns, even though both use the same Hoeffding tree implementation.

This means a DTR instance should be co-located with the pipeline it serves and trained from that pipeline's operational history.

***

## Relationship to the Agents It Protects

The DTR does not make policy decisions — it routes. The agent it defers to remains the authority. The DTR's role is to spare that agent from processing requests that do not require its reasoning. If a DTR is misconfigured or encounters a pattern it has not seen, the fallback is always escalation to the agent: no harm is done.

This means the correctness of the system does not depend on the DTR. It depends on the agent. The DTR is a performance and efficiency optimization, not a correctness component.

***

## When to Use a DTR

A DTR is appropriate when:

-   A pipeline receives high volumes of requests
-   A significant proportion of those requests are repetitive and follow recognizable patterns
-   The cost of invoking the deliberate handler (LLM agent) for every request is prohibitive
-   Incorrect routing decisions can be caught and corrected by the system (i.e., failures are observable)

A DTR is not appropriate when:

-   Request volume is low and LLM invocation cost is acceptable
-   Requests are predominantly novel and do not exhibit stable patterns
-   The stakes of an incorrect deterministic decision are catastrophic and unrecoverable

***

## Relationship to Other Concepts

-   **Intent-Based Filesystem Management** (`d7-intent-based-filesystem-management.md`) — a domain where the DTR serves as the fast-path routing layer before a policy enforcement agent
