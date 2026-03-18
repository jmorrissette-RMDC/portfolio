# **High-Level Design: Vannevar Workspace (State 2)**

**Document ID:** HLD-020

**MAD ID:** vannevar

**Version:** 1.0

**Status:** Active

**Primary Host:** irina (192.168.1.110)

**Registry Port:** 6342 (MCP/UI)

## **1. System Overview**

Vannevar is a State 2 compliant MAD designed for high-bandwidth multi-agent orchestration. It follows a strict functional decomposition: OTS (Off-the-shelf) Infrastructure for the boundary, Graph-Native Logic for orchestration, and Specialized Backing Services for execution.

## **2. Container Composition (State 2)**

Following the State 2 mandate, the MAD is composed of seven specialized containers. All programmatic logic is centralized in the LangGraph container.

| **Container Name**     | **Role**           | **Technology**          | **Network**               |
|------------------------|--------------------|-------------------------|---------------------------|
| **vannevar**           | Gateway / Boundary | nginx:alpine (OTS)      | joshua-net + vannevar-net |
| **vannevar-langgraph** | Brain / Logic      | Python 3.11 / LangGraph | vannevar-net only         |
| **vannevar-amux**      | Hands / Utility    | Node.js (node-pty)      | vannevar-net only         |
| **vannevar-claude**    | Agent CLI          | Claude Code             | vannevar-net only         |
| **vannevar-gemini**    | Agent CLI          | Gemini CLI              | vannevar-net only         |
| **vannevar-codex**     | Agent CLI          | Codex CLI               | vannevar-net only         |
| **vannevar-postgres**  | Database           | postgres:16-alpine      | vannevar-net only         |

## **3. Communication Architecture (ADR-053)**

### **3.1 Inbound Traffic (Ingress)**

-   **Dashboard UI:** Static React assets served directly by the vannevar (Nginx) container.
-   **Logic Routing:** Nginx proxies /mcp (Tool/REST calls) to the vannevar-langgraph container.
-   **Terminal Streaming:** Nginx proxies /ws (WebSockets) directly to vannevar-amux to ensure low-latency terminal throughput.

### **3.2 Outbound Traffic (Egress Proxy)**

The vannevar-langgraph container is network-isolated. To call peer MADs (e.g., Sutherland), it uses the Nginx egress proxy:

-   **Path:** http://vannevar:6342/proxy/[peer-name]/mcp
-   Nginx resolves the peer on joshua-net and forwards the request.

### **3.3 Internal Orchestration**

The "Brain" (vannevar-langgraph) sends orchestration commands (spawn, kill, resize) to vannevar-amux via the private vannevar-net. vannevar-amux manages the PTY instances of the isolated CLI containers.

## **4. Storage Architecture (ADR-039 / ADR-046)**

| **Volume**    | **Path**            | **Purpose**                                             |
|---------------|---------------------|---------------------------------------------------------|
| **storage**   | /storage            | Global credentials, shared project assets, and backups. |
| **workspace** | /workspace/vannevar | Session metadata, PTY sockets, and database files.      |

**Database Placement:** Per ADR-046, PostgreSQL data files are stored in /workspace/vannevar/databases/postgres/data for local I/O performance on the irina host.

## **5. Build and Compliance (REQ-000)**

-   **Package Caching (ADR-037):** All custom-built components (-langgraph, -amux) utilize local packages/ directories containing all required wheels/tarballs for offline-ready builds.
-   **Identity:** All containers run as UID 2030 and GID 2001 (administrators).
-   **Security:** umask 000 is enforced via a start.sh wrapper script to ensure shared file accessibility across the group.
-   **Apgar Compatibility:** vannevar-langgraph exposes /metrics and /metrics_get nodes within the StateGraph.
