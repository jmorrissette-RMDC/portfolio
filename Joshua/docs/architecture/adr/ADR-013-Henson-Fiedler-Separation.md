## ⚠️ Status: Superseded ⚠️

This decision has been superseded by **[ADR-021: Unified Joshua_Communicator](./ADR-021-Unified-Communicator.md)** and **[ADR-023: Direct Tool Exposure](./ADR-023-Direct-Tool-Exposure.md)**. The roles of Fiedler (LLM Gateway) and Henson (Context Engineer) are still separate, but the interaction model described herein is obsolete.

**⚠️ ADDITIONAL ARCHITECTURAL UPDATE (2025-12-21):**
This ADR describes the data flow as "Calling MAD -> Henson (CET) -> Fiedler -> Calling MAD" where Fiedler executes LLM calls. This execution model has been **superseded by ADR-035: Direct Access AI Model Nodes**.

**Current Architecture (per ADR-035):**
- MADs use `joshua_ai_access` library nodes to access LLMs **directly** (no Fiedler gateway)
- Fiedler provides **recommendations** via Master Model Index (advisor, not executor)
- The separation principle (Henson for context, Fiedler for LLM expertise) remains valid

See ADR-034 and ADR-035 for the complete architectural pivot.

*Do not use this document for new designs. It is kept for historical context only.*

---

# ADR-013: Maintain Henson and Fiedler as Separate, Specialized MADs

**Status:** Accepted (Superseded by ADR-021/ADR-023/ADR-035)

**Context:**
The V4.0 architecture introduces a "triangular" data flow for complex, context-dependent LLM calls: `Calling MAD -> Henson (CET) -> Fiedler -> Calling MAD`. This flow, while efficient, raises the architectural question of whether the capabilities of Henson (Context Engineering) and Fiedler (LLM Provisioning) should be merged into a single, unified "LLM Services" MAD. A merger could, on the surface, simplify the data flow by removing one network hop. This ADR evaluates that possibility and formalizes the decision.

**Decision:**
Henson and Fiedler will be maintained as **separate, distinct, and highly specialized MADs.** Merging their capabilities is rejected as an architectural anti-pattern. Fiedler's domain is the *external LLM landscape*, and Henson's domain is the *internal Joshua knowledge landscape*. This separation is a deliberate and critical architectural choice.

-   **Fiedler's Role:** To act as the system's expert on LLM providers, models, and APIs. Its core function is to provide reliable, resilient access to external LLMs. It is the system's "ambassador to the world of LLMs."
-   **Henson's Role:** To act as the system's "Context Engineer." Its core function is to host the Context Engineering Transformer (CET) and transform raw, multi-source internal context into optimized prompts for the Imperator. It is the system's "chief intelligence analyst."

**Consequences:**

*   **Positive:**
    *   **Clear Separation of Concerns:** Enforces a clean architectural boundary between inward-facing knowledge synthesis (Henson) and outward-facing API access (Fiedler).
    *   **Enables Independent Horizontal Scalability:** Allows Fiedler (I/O-bound, low resource) and Henson (compute-bound, high GPU resource) to be scaled independently, leading to massive cost and performance optimizations.
    *   **Enhances System Resilience and Graceful Degradation:** The separation creates a natural "firewall" that allows the system to function in a degraded mode if one of the MADs fails. A Henson failure allows for suboptimal, direct-to-Fiedler calls. A Fiedler failure allows Henson to intelligently queue requests.
    *   **Promotes Architectural Flexibility and Decoupling:** Allows the CET and LLM provider layers to evolve and be replaced independently. For example, a future non-LLM reasoning engine could use Henson for context without needing Fiedler at all.

*   **Negative:**
    *   **Increased Network Hops:** The triangular data flow for CET-enhanced calls involves an additional network hop compared to a merged model. This is deemed an insignificant cost given the immense benefits in scalability, resilience, and architectural clarity.

*   **Neutral:**
    *   This decision solidifies the "Cellular Monolith" design principle, emphasizing the value of highly specialized, single-responsibility agents collaborating over a shared bus.

---
---

## Appendix A: Detailed Architectural Rationale

This appendix captures the three primary arguments for maintaining Henson and Fiedler as separate MADs.

### A.1. Fundamentally Different Domains of Expertise

The most important reason for separation is that Henson and Fiedler operate in fundamentally different and unrelated domains.

-   **Fiedler's Expertise is Outward-Facing:** It is the system's expert on the external world of LLM APIs. Its knowledge base includes model capabilities, provider rate limits, API key management, and transport-level error handling. Its primary task is to execute a perfectly formed prompt against an external service reliably.
-   **Henson's Expertise is Inward-Facing:** It is the system's expert on Joshua's own internal "collective memory." Its knowledge base is the vast corpus of conversations, documents, and data stored within Babbage, Horace, and Codd. Its primary task is to navigate this internal landscape and synthesize raw data into strategically valuable context.

Merging these two would create a single MAD with a hopelessly broad and conflicted domain, violating the core principle of specialized, single-responsibility agents.

### A.2. Independent Horizontal Scalability

Henson and Fiedler have dramatically different performance profiles and resource requirements. Merging them would create an inefficient, monolithic scaling unit.

-   **Fiedler is a Lightweight, I/O-Bound Proxy:** Its job is to manage network calls. It requires minimal CPU and memory, and zero GPU. It can be scaled out cheaply on CPU-only instances to handle a massive number of concurrent network connections.
-   **Henson is a Heavyweight, Compute-Bound Engine:** Its job is to run the CET, a large transformer model. It is compute-intensive and requires significant, expensive GPU resources.

By keeping them separate, we can **right-size the resources for each function independently**:
-   Deploy a small, highly available cluster of cheap, CPU-based Fiedler instances.
-   Deploy a separate, auto-scaling cluster of expensive, GPU-powered Henson instances that can scale up and down based on the demand for context engineering.

This separation allows for a far more cost-effective and performant deployment than a merged model, where we would be forced to pay for expensive GPUs just to handle simple network proxy tasks.

### A.3. Graceful Degradation and System Resilience

The separation creates a natural "firewall" between internal knowledge processing and external API access, which enables more sophisticated and graceful failure handling.

-   **Scenario 1: Henson Fails.** The system loses its advanced context engineering capability. However, it does not lose the ability to reason. A calling MAD's PCP can detect the failure of `henson_assemble_context` and fall back to a "degraded mode": constructing a simpler, naive prompt using only local context and sending it directly to Fiedler. The system's intelligence is reduced, but it remains functional.

-   **Scenario 2: Fiedler Fails.** The system loses its connection to external LLMs. However, it does not lose its ability to prepare for reasoning. Henson can detect that its call to `fiedler_send` has failed. Instead of immediately failing the entire request, Henson's Thought Engine can make an intelligent decision to **queue the optimized prompt** in a persistent, internal queue. It can then inform the original requester that the task is queued and will be completed when the LLM provider is available again. This makes the system resilient to transient LLM outages and prevents the loss of valuable, already-computed context.

These two distinct, manageable failure modes are a direct and powerful benefit of the architectural separation. A single, merged MAD would have a single, catastrophic failure mode, bringing down both context engineering and LLM access simultaneously.
