# ADR-002: Define a Hybrid "Common DNA" for v0 MAD Evolution

---
**⚠️ LEGACY ARCHITECTURE - SUPERSEDED**

This ADR describes the V0.1-V0.10 "code-first" MAD architecture using LangChain AgentExecutor and imperative Python. This approach has been superseded by ADR-032 (Fully Flow-Based Architecture) for all V0.7+ MADs.

**Status:** Superseded
**Superseded by:** ADR-032
**Applies to:** Legacy V0.1-V0.6 MADs only

---

**Status (Historical):** Accepted

**Context:**
As the Joshua ecosystem evolves, a standardized architectural DNA is required for all Multipurpose Agentic Duos (MADs) to ensure coherence within the "Cellular Monolith" design. The goal is to define a robust and pragmatic implementation path for a MAD's V0 progression (from V0.1 to V0.10). The key decision was whether to build all components from scratch, adopt a single external framework wholesale (like LangChain), or synthesize a hybrid approach. A pure native build would be slow and reinvent many wheels. A wholesale adoption would risk sacrificing Joshua's unique architectural principles (like the PCP and the conversation bus) to a foreign framework's idioms.

**Decision:**
We will adopt a hybrid, "best-of-breed" approach for the V0 MAD's "Common DNA." This strategy integrates patterns and components from mature agentic frameworks into the specific layers of the Joshua architecture where they fit best, preserving Joshua's unique macro-architecture while accelerating development.

The V0 evolutionary path is defined as follows:

1.  **V0.1 (Foundation):** A **Joshua-native Action Engine** with pure Python tools. No frameworks are integrated at this stage.

2.  **V0.5 (Reasoning):** The **Thought Engine (Imperator)** is introduced. Its reasoning loop is engineered using a combination of:
    *   **LangChain `AgentExecutor`:** As the foundational "thought-action-observation" loop.
    *   **AutoGPT Self-Critique Pattern:** An explicit, prompt-driven criticism step is added to the loop for in-the-moment self-correction before an action is taken.
    *   **Memory:** The Imperator's memory is limited to its static `persona.md`, the immediate conversation history (e.g., `ConversationBufferMemory`), and a simple agent scratchpad. It does not perform broad RAG at this stage.

3.  **V0.7 (Modernization):** The **Action Engine** is systematically refactored to fully leverage modern, standardized components from frameworks like LangChain and Haystack. This includes replacing raw API calls with robust integrations, and adopting standard document loaders, text splitters, and other utility components.

4.  **V0.8 (Context):** The **Thought Engine** is upgraded with "Fast RAG" capabilities. This is a hybrid implementation:
    *   **Plumbing (LangChain/Haystack):** The underlying in-memory vector stores (for Persona/Rules and Recent Conversation) are implemented using components from these frameworks.
    *   **Strategy (Joshua Native):** The logic for managing and intelligently querying these stores is Joshua-native, representing an early, simplified version of the V4 CET's strategic context assembly.

5.  **V0.10 (Federation):** A fully mature MAD that has completed the V0.8 progression. The focus is on hardening, comprehensive testing (via the `Demming` MAD), and ensuring flawless communication with other V0.10 MADs. The Thought Engine (TE) within each MAD interacts with its own Action Engine (AE) via direct, in-memory MCP calls, ensuring efficient execution while maintaining decoupling. All external communication with other MADs continues to be handled via the `Joshua_Communicator`.

**Consequences:**

*   **Positive:**
    *   **Accelerated Development:** We avoid reinventing solved problems by using battle-tested components for things like agent loops and data parsing.
    *   **Architectural Integrity:** Joshua's core principles (PCP, Cellular Monolith, Conversation Bus) are preserved as the guiding macro-architecture. We are plugging components *into* Joshua, not replacing it.
    *   **Clarity and Modularity:** Provides a clear, version-by-version blueprint for how a MAD gains capabilities, making the system's evolution predictable and manageable. This includes a clear distinction: Thought Engines make direct, in-memory MCP calls to their local Action Engine for efficiency, while using the `Joshua_Communicator` exclusively for external communication to other MADs.
    *   **Best-of-Breed:** Allows us to select the single best pattern for each architectural need (e.g., AutoGPT's critique, LangChain's execution loop, Haystack's RAG components).

*   **Negative:**
    *   **Dependency Management:** Creates a dependency on several external frameworks, which will require monitoring and maintenance as they evolve.
    *   **Integration Complexity:** Requires careful engineering to ensure the "seams" between Joshua-native logic and external framework components are clean and well-defined.

*   **Neutral:**
    *   This decision formally codifies the MAD implementation strategy, providing a clear standard for all current and future MAD development.
---
---

## Appendix A: Detailed Rationale for the V0 Evolutionary Path

This appendix captures the detailed reasoning behind the version-by-version adoption of framework patterns for the V0 MAD.

### A.1. Overall Philosophy: "Buy the Plumbing, Build the Strategy"

The core philosophy is to use external frameworks for commoditized, low-level "plumbing" while keeping the high-level "strategic" logic that makes Joshua unique as a native implementation. We buy what is standard and build what is novel.

-   **Plumbing (Frameworks):** Agent loops, document loaders, vector store integrations, API wrappers. These are solved problems with mature open-source solutions.
-   **Strategy (Joshua Native):** The PCP's cognitive cascade, the CET's context orchestration, the LPPM's learning mechanism, and the conversation bus protocols. These are Joshua's core innovations.

### A.2. Version-Specific Rationale

**V0.1 (Foundation):**
*   **Decision:** No framework integration.
*   **Rationale:** The initial focus must be on defining the MAD's core domain logic and exposing it correctly via the native MCP server. Introducing external frameworks at this stage would add unnecessary complexity and obscure the core function of the MAD. The goal is to first build a working tool, then make it smart.

**V0.5 (Reasoning):**
*   **Decision:** Implement the Imperator using LangChain's `AgentExecutor` and AutoGPT's self-critique pattern.
*   **Rationale:** The `AgentExecutor` is a mature, industry-standard implementation of the ReAct (Reason+Act) agent loop. Building this from scratch would be a significant reinvention of the wheel. The AutoGPT self-critique pattern is a powerful, low-cost enhancement that adds a layer of reflection and error-correction to the basic loop. Combining these two gives us a robust, best-of-breed reasoning engine with minimal custom engineering. Memory at this stage is intentionally simple (conversation history and persona), as the focus is on establishing the core reasoning capability, not advanced knowledge retrieval.

**V0.7 (Modernization):**
*   **Decision:** Systematically refactor the Action Engine to use LangChain/Haystack components.
*   **Rationale:** This version marks a deliberate shift from ad-hoc tools to a professionally engineered toolkit. By V0.7, a MAD has proven its core value, and the investment in refactoring is justified. Using LangChain's document loaders and API integrations provides immediate access to a vast ecosystem of pre-built connectors, drastically reducing the effort needed to interact with diverse data sources and services. This makes the MAD more capable and resilient.

**V0.8 (Context):**
*   **Decision:** Implement Fast RAG using LangChain/Haystack for plumbing and Joshua-native logic for strategy.
*   **Rationale:** This is a key example of the "Buy the Plumbing, Build the Strategy" principle. The low-level task of creating and querying an in-memory vector store is perfectly handled by components from LangChain or Haystack (e.g., `FAISS` integration). However, the *strategic* logic of *when* to query this memory, *how* to manage the TTL cache for conversations, and *how* to assemble the results into the Imperator's prompt is a precursor to the CET and is unique to Joshua's cognitive architecture. This hybrid approach gives us a fast implementation path without sacrificing our unique architectural vision.

**V0.10 (Federation):**
*   **Decision:** No new framework integrations.
*   **Rationale:** This stage is about stabilization, not new features. The focus is on ensuring the hybrid architecture built up through V0.8 is robust, thoroughly tested, and ready for the major architectural shift of the V1.0 Rogers Bus migration. Introducing new components at this stage would add unacceptable risk.
