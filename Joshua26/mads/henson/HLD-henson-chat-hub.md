# HLD: Joshua26 Human Interaction Layer

**Version:** 1.0
**Date:** 2026-02-24
**Status:** Draft
**Author:** Aristotle9

---

## Executive Summary
This architecture decouples the human chat experience (Henson) from memory (Rogers) and compute (Sutherland/Fiedler). It establishes Henson as the "Universal Switchboard," hosting UIs and routing conversational input through a Shared Imperator Graph configured dynamically by Persona definitions.

## The Unified Architecture

```text
Human User
    │
    ▼ (Web UI / Chat Client)
┌────────────────────────────────────────────────────────┐
│ HENSON (The Human Hub)                                 │
│ - Hosts UIs (Nginx)                                    │
│ - Stores Persona Configs (Postgres)                    │
│ - Runs Shared Imperator Graph (LangGraph)              │
└──────┬────────────────────┬────────────────────┬───────┘
       │                    │                    │
       ▼                    ▼                    ▼
┌──────────────┐    ┌──────────────┐     ┌──────────────┐
│ ROGERS       │    │ FIEDLER      │     │ OTHER MADs   │
│ (Memory)     │    │ (LLM Router) │     │ (Tools)      │
│              │    │              │     │              │
│ - Custom     │    │ - Aliases    │     │ - Brin       │
│   Assemblies │    │ - Multi-LoRA │     │ - Malory     │
│ - Mem0 KG    │    │ - API Auth   │     │ - Starret    │
└──────────────┘    └──────┬───────┘     └──────────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │ SUTHERLAND   │
                    │ (Compute)    │
                    │ - Ray Serve  │
                    │ - TP vLLM    │
                    └──────────────┘
```

*   **Henson (The Hub):** Hosts UIs via Nginx, stores Persona configurations in Postgres, and runs the Shared Imperator LangGraph.
*   **Rogers (Memory):** Provides infinite conversation storage and custom context assemblies (CAG, RAG-KG).
*   **Fiedler (Routing):** Acts as the LLM traffic cop, resolving aliases to specific models or LoRAs without knowing about the underlying hardware.
*   **Sutherland (Compute):** The physical infrastructure provider (e.g., Ray Serve, TP vLLM) that executes the models Fiedler points to, and queues background jobs.

---

## The Shared Imperator Pattern
Henson instantiates a shared cognitive Python library (the "Imperator") for every turn. 
- If talking to **Gunner**, Henson injects Gunner's prompt and tools into the graph.
- If talking to **Grace**, Henson injects Grace's prompt and requests her specific CAG-heavy context from Rogers.
- If talking to **Fiedler directly**, Henson acts as a pass-through to Fiedler's own instance of the Imperator graph.

---

## Sovereign Alignment (Brain/Voice Split)
To ensure personal companions do not presume corporate morality and to bypass safety filters on prose generation:
1. **The Brain (Orchestrator):** High-tier commercial models (via Fiedler) handle abstract planning and tool logic. They receive the dense Rogers context.
2. **The Voice (Speaker):** The abstract plan is sent to a fast, sovereign local model (via Sutherland/Ray) which generates the final human-facing prose using Tensor Parallelism and dynamic LoRA swapping for low-latency emotional connection.

---

## Implementation Phasing Strategy

### Phase 1: The Switchboard (Current Target)
*   **Goal:** Establish the physical infrastructure, UX, and baseline human-to-MAD routing.
*   **Interaction Model:** Strictly **Human-to-Imperator**.
*   **Execution:** Simple LangGraph, single-model calls, generic Rogers context.
*   **Compute:** Uses existing legacy backend (GPUStack/Cloud).

### Phase 2: The Cognitive Upgrade
*   **Goal:** Introduce sovereign alignment and basic tool agency.
*   **Execution:** Implement **Brain/Voice split** for personas.
*   **Compute:** Rework **Sutherland** (Ray/vLLM) and **Fiedler** (Routing/Aliases).
*   **Context:** Still utilizing generic Rogers context flows, but extracting better long-term facts.
*   **Tools:** Initial agentic tools (Web, Git, Calendar).

### Phase 3: The Autonomous Swarm
*   **Goal:** True multi-agent autonomy, deep contextual personalization, and swarm behavior.
*   **Interaction Model:** **MAD-to-MAD conversation** enabled.
*   **Context:** Henson begins requesting **Custom Context Assemblies** from Rogers (CAG for Grace, RAG-KG for Gunner).
*   **Behavior:** Proactive thinking loops and dynamic capability building (Henson Host Imperator creating new Guest Personas).
