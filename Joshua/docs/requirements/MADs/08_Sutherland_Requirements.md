# Sutherland Requirements

- **Role**: GPU Management
- **Version**: V0.10
- **Home**: `mads/sutherland/`

---

## 1. Overview

-   **Purpose**: `Sutherland` is the expert MAD for the governance, orchestration, and monitoring of the Joshua AI Compute Cluster, which comprises all distributed GPU resources.
-   **V0.10 Scope Definition**: Sutherland acts as a federated "Local Warden." An instance of Sutherland runs on every GPU-enabled host, managing local GPU resources, and providing intelligent placement recommendations to other MADs. It does not run workloads itself but manages leases and a queue for stateful tasks.

---

## 2. Tool Exposure Model

This MAD follows the Direct Tool Exposure architecture (ADR-023). Its public tools are exposed directly on its MCP server and are discoverable via the Rogers registry. Any incoming communication that is not a valid MCP call for an exposed tool is routed to the Thought Engine for conversational processing (e.g., "What is the current status of the GPU cluster?").

> **Note on Tool List:** The tools listed in this document are a *provisional set* based on the MAD's high-level requirements. The final, authoritative list of tools, their specific parameters, and their return schemas will be defined in a dedicated Design Document prior to implementation.

---

## 3. Public Action Engine Tools

### `sutherland_recommend_placement`
- **Description:** Analyzes the global state of the GPU cluster and recommends the optimal host and GPU for a new workload. This is typically called by an orchestrator MAD like `Moses` or `Hopper`.
- **Input Schema:**
    - `requirements` (dict, required): The hardware requirements for the workload (e.g., `{"vram_min_mb": 16000, "cuda_cores_min": 4096}`).
    - `placement_preference` (string, optional, default: 'least_utilized'): The desired placement strategy ('least_utilized', 'most_utilized').
- **Output Schema:** `{"status": "success", "recommendation": {"host_id": "host-m5", "gpu_device_ids": [0], "reasoning": "..."}}`

### `sutherland_request_gpu_lease`
- **Description:** Requests an exclusive, stateful lease on a GPU for a long-running task (e.g., video rendering). The request will be either granted immediately or queued.
- **Input Schema:**
    - `requirements` (dict, required): The hardware requirements for the lease.
    - `duration_minutes` (integer, required): The requested duration of the lease.
    - `priority` (integer, optional, default: 5): The priority of the request (1-10, 10 is highest).
- **Output Schema (Granted):** `{"status": "granted", "lease_id": "uuid-1234", "host_id": "host-m5", "gpu_device_ids": [0]}`
- **Output Schema (Queued):** `{"status": "queued", "request_id": "uuid-5678", "estimated_wait_seconds": 120}`

### `sutherland_release_gpu_lease`
- **Description:** Releases an active GPU lease, making the resource available for other tasks.
- **Input Schema:**
    - `lease_id` (string, required): The ID of the lease to release.
- **Output Schema:** `{"status": "success", "message": "Lease released."}`

### `sutherland_get_lease_status`
- **Description:** Polls the status of a queued lease request.
- **Input Schema:**
    - `request_id` (string, required): The ID of the queued request.
- **Output Schema:** `{"status": "pending", "position_in_queue": 3, "estimated_wait_seconds": 90}`

### `sutherland_load_model`
- **Description:** Instructs the local Sutherland instance to load a specified model into its inference server (e.g., Triton).
- **Input Schema:**
    - `model_name` (string, required): The name of the model to load.
    - `gpu_device_ids` (array[integer], required): The local GPU device IDs to load the model onto.
- **Output Schema:** `{"status": "success", "endpoint": "http://localhost:8000/v2/models/...", "message": "Model loaded."}`

---

## 4. Future Evolution (Post-V0)

Sutherland's role as the GPU management platform remains focused on efficient resource allocation and scheduling throughout the ecosystem's evolution.

*   **Phase 1 (Foundation / V0.10):** Sutherland is hardened and quality-gated for flawless Direct Communication, becoming the reliable GPU management platform for the V0.10 Core Fleet. All GPU-dependent MADs (Henson, Muybridge, Bass, potential future ML/AI MADs) depend on Sutherland for GPU resource allocation.
*   **Phase 2 (Conversation / V1.0):** Sutherland is re-platformed to communicate exclusively via the Rogers Conversation Bus (pure Kafka), using `Joshua_Communicator` for all inter-MAD communication. GPU lease requests, grants, and releases flow through the durable conversation log, enabling complete GPU utilization history reconstruction and analysis.
*   **Phase 5 (Autonomy / V7.0):** Sutherland integrates with Joshua MAD's strategic orchestration, receiving top-down directives for system-wide GPU allocation policies, constitutional constraints on resource usage priorities, and strategic optimization of GPU resources based on ecosystem-wide objectives.

---