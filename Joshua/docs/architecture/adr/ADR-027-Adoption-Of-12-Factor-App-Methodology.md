# ADR-027: Adoption of the 12-Factor App Methodology

**Status:** Proposed
**Date:** 2025-12-18
**Deciders:** System Architect

## Context and Problem Statement

The Joshua project is a complex, distributed system composed of many containerized services (MADs). To ensure scalability, resilience, and maintainability as the ecosystem grows, we need a common set of architectural principles to guide the development and deployment of these services. Without a formal methodology, we risk developing inconsistent, tightly-coupled components that are difficult to manage, scale, and debug.

## Decision

The Joshua project will officially adopt the **12-Factor App methodology** as a core set of design principles for all MADs and supporting services. All future development and architectural reviews will use these factors as a guiding framework.

This decision includes recognizing and formally documenting three well-reasoned, strategic deviations from a strict interpretation of the methodology, which are tailored to the unique requirements of our multi-agent system.

### Acknowledged Strategic Deviations

Our architecture knowingly diverges from a strict interpretation in the following areas for specific, strategic benefits:

1.  **Factor 6 (Processes): Deliberate State Isolation.**
    *   While most MADs are designed to be stateless, we explicitly isolate state into specialist "data manager" MADs (`Horace`, `Codd`, `Babbage`). This allows the rest of the ecosystem to adhere to the stateless principle while providing robust, centralized state management as a service.

2.  **Factor 10 (Dev/Prod Parity): Pragmatic Parity Exception.**
    *   We deliberately break parity for the code source. Development environments use hot-mounted code for rapid iteration, while production environments use immutable images with baked-in code for stability and reproducibility. This is a conscious trade-off to optimize for developer velocity and production safety.

3.  **Factor 11 (Logs): Logs as a First-Class Data Stream.**
    *   The V1+ target architecture elevates logs beyond simple `stdout` streams. By publishing logs to the Kafka conversation bus, they become a real-time, queryable source of operational intelligence for other MADs (`Hamilton`, `McNamara`), which is a more powerful and data-centric approach to observability.

## Consequences

*   **Positive:**
    *   Provides a clear, industry-standard framework for building robust, scalable services.
    *   Establishes a shared vocabulary for architectural design and review.
    *   New MADs will be developed with a higher degree of consistency and quality.
    *   Simplifies onboarding for new developers (human or AI).
*   **Action Item:** All future MAD design documents and code reviews must assess for alignment with the 12-Factor principles and our documented deviations. Existing MADs should be audited and refactored towards compliance over time.
