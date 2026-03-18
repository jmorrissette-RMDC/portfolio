# ADR-003: Adopt a Hybrid Transformer + LoRA Architecture for V4 CET

**Status:** Accepted

**Context:**
The Context Engineering Transformer (CET) for Joshua's V4.0 is designed to optimize the context provided to the Imperator. An initial architectural discussion focused on whether the CET would primarily function as a rule-based orchestrator of RAG (Retrieval-Augmented Generation) components, or as a machine learning model itself. It was clarified that the CET's core principle is to act as a transformer model that "learns context as a language," performing a generative transformation on raw context to produce an optimized input for the Imperator. This raised the question of how to achieve both universal context optimization principles and domain-specific specialization efficiently across all MADs.

**Decision:**
The V4.0 Context Engineering Transformer (CET) will be implemented as a **hybrid Transformer + LoRA (Low-Rank Adaptation) architecture.**

Specifically:
1.  **Shared Base CET Transformer Model:** A single, large, and powerful transformer model will be developed and hosted (likely within the `Henson` MAD). This base model will be trained on the universal principles of "optimal context language"—learning how to structure, synthesize, condense, prioritize, and reformat raw, multi-source information into a highly effective input for an LLM, irrespective of domain. This forms the core intelligence of context optimization.
2.  **Domain-Specific LoRA Adapters:** Each MAD or domain requiring specialized context optimization will have its own small, efficient LoRA adapter. These adapters will be fine-tuned specifically on domain-relevant context optimization tasks.
3.  **Dynamic Specialization at Inference:** At runtime, when a MAD requests context from the CET, the CET service will dynamically load its base model with the requesting MAD's specific LoRA adapter. The LoRA will act as a "tuning knob" that guides the base model's attention and generative capabilities, ensuring the context is optimally transformed for that MAD's domain-specific needs without requiring full model retraining.

**Consequences:**

*   **Positive:**
    *   **Maximal Efficiency:** A single large model handles universal context principles, while small LoRAs provide cost-effective domain specialization. This avoids retraining a massive model for every domain.
    *   **Unified Learning:** The base CET model can continuously improve its universal context-engineering skills from the aggregated experience of all MADs.
    *   **Domain-Specific Excellence:** LoRAs ensure that context is perfectly tailored to each MAD's unique domain, capturing nuances in required information structure and emphasis.
    *   **Architectural Coherence:** Reinforces the "Cellular Monolith" by having a shared, central cognitive component that is specialized at the edges.
    *   **Leverages Frameworks:** The CET uses the underlying RAG components (e.g., from LangChain/Haystack within data MADs) as its raw information sources for the transformation process, without reinventing the plumbing.

*   **Negative:**
    *   **Initial Training Complexity:** Training the large base CET transformer model and managing its LoRA adapters is a significant machine learning engineering effort.
    *   **Hosting Requirements:** A central, GPU-accelerated service (Henson MAD) is required to host the base CET model and manage LoRA loading.

*   **Neutral:**
    *   This decision firmly establishes the CET as a learning, generative ML model, a distinct cognitive tier within the PCP, and a core Joshua innovation.
---
---

## Appendix A: Detailed Rationale & Inspirations for the CET Architecture

### A.1. The CET as a "Contextual Sub-Brain"

The core clarification driving this ADR is that the CET is not a simple, rule-based orchestrator of RAG tools. It is a **transformer model in its own right**—a specialized "sub-brain" whose sole purpose is to shape information for the main Imperator LLM.

-   **Analogy: The Expert Research Assistant:** The RAG "plumbing" in data MADs (Babbage, Horace) acts like a librarian that can fetch every relevant book. The CET acts as the expert research assistant who reads all the books, synthesizes the key arguments, highlights the most critical paragraphs, and hands the decision-maker a perfect one-page briefing. The CET's output is not a collection of raw documents; it's a new, generative artifact specifically engineered for the task.

-   **ML Function:** The CET performs a learned, generative `(raw_context, task) -> optimized_context` transformation. It learns to restructure, synthesize, translate, prioritize, and prune raw information into a dense, coherent, and highly effective prompt for the Imperator.

### A.2. The "Universal Grammar of Context"

The decision to use a **single, shared base CET model** is predicated on the insight that "good context" has universal properties, much like language has a universal grammar. This shared base model is an expert in these properties, independent of the domain. These universal skills include:

-   **Optimal Structuring:** Learning the best ways to format information (e.g., using Markdown, providing examples first, placing instructions at the end).
-   **Synthesis:** Learning to combine disparate pieces of information into a cohesive whole.
-   **Summarization & Pruning:** Learning to identify and remove redundant or low-value information without losing critical details.
-   **Prioritization:** Learning to rank information by relevance so the most important context appears first.

By centralizing this expertise in one model, all MADs in the ecosystem can benefit from continuous improvements to these core skills without needing individual retraining.

### A.3. LoRA Adapters as "Domain-Specific Lenses"

The LoRA adapters are the key to achieving domain specialization without the massive cost of training a separate CET model for each MAD. The LoRA acts as a small, efficient "lens" or "tuning knob" that dynamically adapts the powerful base CET model at inference time.

-   **Function as a Specializer:** A MAD's LoRA is fine-tuned only on examples from its specific domain. Hopper's LoRA learns what optimal context looks like for *code generation*, while McNamara's LoRA learns what it looks like for *security analysis*.
-   **Function as an Attention Guide:** The LoRA effectively guides the base model's attention. When Hopper's LoRA is active, it tells the base model to "pay more attention to syntax, function signatures, and code examples" and "pay less attention to narrative flow." This allows the base model to apply its universal context-structuring skills in a way that is highly specialized for the immediate task.

The hybrid architecture is therefore a perfect synthesis: the **base model** provides the general "how-to" of context engineering, and the **LoRA adapter** provides the specific "what-for" of the domain. This provides both the power of a large, general model and the precision of a small, specialized one.
