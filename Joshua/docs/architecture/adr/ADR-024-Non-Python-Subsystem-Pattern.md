# ADR-024: Non-Python Subsystem Pattern for MAD Implementation

**Status:** Accepted

**📝 Note on Flow-Based Architecture (2025-12-22):**
This three-layer pattern is **architecture-agnostic** and applies equally to code-first and flow-based MAD implementations. In flow-based architecture (ADR-032), Layer 3 (the Python bridge) is typically packaged as a LangFlow-compatible node library that wraps the subprocess. The core principle remains: Python provides the MCP interface and wraps non-Python components, regardless of whether composition happens via imperative Action Engine code or visual flows.

**Context:**

Joshua's standard architecture requires all MCP servers (MADs) to be implemented in Python using the joshua_network framework. This ensures consistency, standardization, and access to mature cognitive frameworks (LangChain, Haystack, etc.) across the entire ecosystem.

However, some domain-specific tasks are best implemented in non-Python languages where specialized libraries or performance characteristics are critical:
- **Node.js + Playwright**: Web browser automation with superior ecosystem (Malory MAD)
- **Rust**: High-performance computation or systems-level operations
- **Go**: Concurrent network services or cloud-native infrastructure
- **Specialized tools**: Language-specific libraries with no Python equivalent

The challenge: how do we leverage best-of-breed implementations in non-Python languages while maintaining architectural homogeneity and framework standards across the entire ecosystem?

**Decision:**

MADs requiring non-Python components will adopt a **three-layer pattern** that keeps the Python + joshua_network framework as the authoritative MCP interface:

1. **Layer 1 - MCP Server Wrapper (Python + joshua_network):**
   - The MAD is implemented entirely in Python using the joshua_network framework
   - Defines and exposes all tools via standard MCP (Model Context Protocol)
   - Tool schemas (name, description, inputSchema) are defined in Python
   - All Thought Engine logic and cognitive processing stays in Python
   - Manages client communication (relay, other MADs)
   - Validates all inputs and outputs against MCP specifications

2. **Layer 2 - Subprocess Component (Non-Python Implementation):**
   - Runs as an isolated subprocess, sidecar, or external service
   - Implements specialized domain functionality (e.g., Playwright for browser automation)
   - Communicates with Layer 1 via well-defined IPC (stdin/stdout, WebSocket, HTTP, gRPC)
   - Has no direct MCP protocol access
   - Can be replaced without affecting the MCP interface
   - Failures are isolated and managed by the Python wrapper

3. **Layer 3 - Action Engine Integration (Python):**
   - Tool handlers in the Action Engine invoke subprocess operations
   - Transform subprocess results into MCP-compliant responses
   - Handle all error cases, retries, timeouts, and state management
   - Maintain consistency with MAD's Thought Engine decisions
   - Provide clean abstraction between cognitive layer and specialized component

**Consequences:**

*   **Positive:**
    *   **Framework Compliance:** All MADs remain consistent joshua_network implementations visible to the relay as standard MCP servers
    *   **Best-of-Breed:** Enables use of specialized libraries (Playwright, Rust performance, Go concurrency) without architectural compromise
    *   **Isolation:** Non-Python components are isolated from cognitive architecture, reducing risk and complexity
    *   **Replaceability:** Non-Python component can be swapped without affecting MCP interface or Thought Engine
    *   **Standardization:** Provides formal pattern for handling non-Python requirements across all future MADs
    *   **Tool Discovery:** Relay sees unified MCP interface from Python layer; subprocess details are implementation details

*   **Negative:**
    *   **IPC Complexity:** Requires designing and maintaining inter-process communication protocols between Python and non-Python components
    *   **Debugging:** Cross-language debugging requires additional tooling and expertise
    *   **Performance Overhead:** IPC adds latency compared to pure Python implementations
    *   **Dependency Management:** Creates external dependencies in non-Python languages requiring monitoring and maintenance

*   **Neutral:**
    *   Establishes formal standard for all MADs requiring non-Python implementations
    *   Provides clear decision framework: Python-first by default, non-Python only when justified by unique requirements

**Example: Malory v0.7 (Web Browser Automation)**

Malory implements this pattern across all three layers:

1. **MCP Server (Python + joshua_network):** Defines 21 browser tools (navigate, click, fill_form, etc.) with proper MCP schemas
2. **Subprocess (Node.js + Playwright):** Runs Playwright MCP subprocess for actual browser automation via Playwright API
3. **Action Engine (Python):** Tool handlers transform MCP calls into Playwright subprocess invocations, manage browser contexts, handle failures

Result: The relay sees Malory as a standard Python MCP server with 21 tools. The Node.js subprocess is an invisible implementation detail.

---

## Related Decisions

*   **ADR-002:** V0 MAD DNA - hybrid "best-of-breed" approach philosophy
*   **ADR-020:** System Evolution Roadmap - Malory scheduled for Phase 1 Foundation
