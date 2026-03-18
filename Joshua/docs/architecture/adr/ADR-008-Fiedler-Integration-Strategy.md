# ADR-008: Adopt a "Framework First" Strategy for Fiedler's LLM Integrations

**Status:** Accepted (Superseded by ADR-034/ADR-035 for execution model)

**⚠️ ARCHITECTURAL UPDATE (2025-12-21):**
This ADR describes Fiedler's original role as a **central LLM gateway** that executes LLM calls on behalf of MADs. This execution model has been **superseded by ADR-035: Direct Access AI Model Nodes**.

**Current Architecture (per ADR-035):**
- MADs use `joshua_ai_access` library nodes **directly** (no proxy/gateway)
- Fiedler is now an **orchestrator and advisor** (Master Model Index, recommendations)
- The framework integration strategy described here remains valid for Fiedler's internal operations

See ADR-034 and ADR-035 for the complete architectural pivot.

**Context:**
Fiedler, as Joshua's central LLM gateway, must interact with a diverse and rapidly evolving landscape of Large Language Model APIs. A key architectural decision for its V0.7 Modernization is how to implement its Action Engine to be both maintainable and highly capable. A purely custom, native SDK-based approach for every provider would be an immense and unsustainable engineering burden. Conversely, relying on a single, unified abstraction layer risks providing only lowest-common-denominator functionality and blocking access to critical, provider-specific features. This risk was previously validated by project experiences where the `litellm` abstraction failed to support essential multimodal capabilities for Gemini.

**Decision:**
Fiedler's Action Engine will adopt a **"Framework First, Native SDK by Exception"** strategy for integrating with LLM providers.

1.  **Default Standard: LangChain Integration:** The default and required method for integrating any LLM provider will be to use the official **LangChain community integration**. This is the baseline and is expected to cover the vast majority of use cases, maximizing our leverage of the open-source ecosystem.

2.  **Exception Protocol: The "Native Escape Hatch":** A custom, native SDK-based client will only be developed for a specific provider if a critical need is proven and documented. The strict criteria for an exception are:
    *   **Unsupported Critical Feature:** A feature essential for a core Joshua workflow (e.g., advanced multimodal inputs) is available in the provider's native SDK but is missing, incomplete, or unstable in the LangChain integration.
    *   **Verifiable Performance Bottleneck:** There is a measurable, significant, and unacceptable performance degradation for a core workflow when using the LangChain integration compared to the native SDK.

3.  **Native Clients as Technical Debt:** Any custom native client is to be considered a temporary solution and a form of technical debt. Its existence must be tracked, and a corresponding issue should be opened with the LangChain project to request the missing feature or report the performance issue.

4.  **Deprecation Goal:** The explicit goal for any native client is its own deprecation. Once the official LangChain integration achieves parity for the feature or performance that prompted the exception, Fiedler's architecture must be refactored to remove the custom client and revert to the standard LangChain integration.

**Consequences:**

*   **Positive:**
    *   **Maximizes Leverage of Open Source:** Aligns our development with the mature LangChain ecosystem, drastically reducing our maintenance burden for the "long tail" of LLM providers.
    *   **Provides an Escape Hatch for Innovation:** Does not block Joshua from using cutting-edge, provider-specific features when they are critical, ensuring we are never limited by a framework's release cycle.
    *   **Creates a Clear, High Bar for Custom Code:** Prevents the proliferation of custom clients by establishing a formal justification process.
    *   **Promotes Community Contribution:** Our default path when encountering a limitation is to contribute back to the open-source project, which benefits the entire community.

*   **Negative:**
    *   **Potential for Short-Term Complexity:** In the rare case an exception is needed, Fiedler's internal logic will have to manage both the standard LangChain client and a custom native client until the official integration is updated.

*   **Neutral:**
    *   This decision establishes a pragmatic, scalable, and future-proof policy for managing Fiedler's most critical function: communicating with a diverse and rapidly evolving set of LLM providers.

---
---

## Appendix A: Detailed Architectural Rationale and Evolution of Thought

### A.1. The "Leaky Abstraction" Problem

The primary driver for this decision is to avoid the "leaky abstraction" problem, which is particularly acute in the rapidly changing LLM space. A unified abstraction layer must, by definition, generalize features. This can lead to failure modes where the abstraction either only supports lowest-common-denominator features or provides incomplete/brittle support for advanced features. The project's direct negative experience with `litellm`'s failure to handle Gemini's multimodal capabilities served as a powerful validation of this risk. A core MAD like Fiedler cannot be architecturally dependent on a third-party's speed to correctly implement mission-critical features.

### A.2. Evolution of the Architectural Decision

The discussion leading to this ADR explored two competing philosophies:

1.  **Initial Proposal: "Native SDK for Strategic, Framework for Commodity":** This initial idea proposed identifying a few "strategic" providers (e.g., Google, OpenAI) and building native SDK integrations for them from the start, while using a framework like LangChain for all others. The rationale was to guarantee deep capability for the most important models.

2.  **Critique of Initial Proposal:** It was correctly pointed out that this approach makes several premature assumptions. It assumes we can predict which providers will remain "strategic" and puts the initial engineering burden on us to build and maintain custom clients, even if the framework's integration is perfectly adequate. It violates the principle of not reinventing the wheel.

3.  **Final Proposal: "Framework First, Native SDK by Exception":** The final, superior decision reverses the default. It establishes the community standard (LangChain) as the default and treats custom, native code as a managed exception. This is a much more scalable and pragmatic engineering philosophy.

### A.3. The Role of LangChain: Breadth and a High-Quality Baseline

This policy relies on the maturity of the LangChain ecosystem. Unlike more minimalistic tools, LangChain generally aims for comprehensive support of provider features. By defaulting to LangChain, we assume its integrations are "good enough" for the vast majority of cases. This allows us to focus our engineering efforts only on the true exceptions where the abstraction is demonstrably insufficient for a critical need. LangChain provides the **breadth** of coverage.

### A.4. The Role of the Native SDK: The "Escape Hatch" for Depth

The "escape hatch" is a critical component of this strategy. It is our architectural safety valve. It ensures that Joshua's progress is never blocked by a limitation in a third-party framework. By having a formal process for justifying and implementing a native SDK client, we give ourselves the ability to go for **depth** of capability when—and only when—it is absolutely necessary. The explicit framing of these native clients as "technical debt" ensures that we always have a long-term goal of returning to the community standard, thus preventing a gradual slide into a fully custom, unmaintainable system.
