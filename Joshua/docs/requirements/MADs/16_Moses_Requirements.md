# Moses V6.0 Requirements

- **Role**: Federated Container Placement Orchestrator (Master Orchestrator)
- **Version**: V6.0
- **MAD Number**: 16
- **Phase**: 4 (eMADs)

---

## 1. Overview

### Purpose

Moses is the intelligent, federated container placement orchestrator responsible for the lifecycle and placement of all MAD and eMAD containers across the Joshua compute cluster. Per **ADR-018**, Moses acts as the "Master Orchestrator," providing a single, authoritative gateway for all container operations while operating on a fully decentralized, federated "gossip" model for maximal resilience and scalability.

Moses is deployed as a **dedicated instance on every host** capable of running MAD containers, with each instance acting as the exclusive master of its local container runtime while maintaining global cluster awareness.

### Strategic Value

Moses enables the infrastructure foundation for the V6.0 eMAD Revolution by providing:
- Intelligent, optimal container placement across distributed hosts
- High availability through federated architecture
- Encapsulated complexity for GPU resource coordination (via Sutherland)
- Secure, reliable container lifecycle management without SSH/remote API calls

**Architectural Role**: Moses is the infrastructure-level placement expert, complementing Kaiser's team composition expertise and Joshua's strategic planning.

---

## 2. Composition Manifest

Per **ADR-032: Fully Flow-Based Architecture**, this MAD is a thin composition layer that imports all functionality from shared libraries and nodes.

### 2.1. Action Engine Libraries

```txt
# requirements.txt (Action Engine section)
joshua_communicator>=6.0.0        # Network I/O, MCP communication, ingress routing
joshua_flow_runner>=6.0.0         # Langflow flow execution engine
joshua_flow_scheduler>=6.0.0      # Scheduled/periodic flow triggers
```

### 2.2. Thought Engine Libraries

```txt
# requirements.txt (Thought Engine section)
joshua_thought_engine>=6.0.0      # Master PCP dependency aggregator (V6.0 includes all tiers)
```

**Note**: At V6.0, the full PCP stack is active (DTR, LPPM, CET, Imperator, CRS).

### 2.3. Node Libraries

```txt
# requirements.txt (Node Libraries section)

# Tier 1: Universal nodes
joshua_core>=1.0.0                # LLMCLINode, flow control, utilities

# Tier 3: Domain-specific nodes
joshua_docker>=1.0.0              # Docker container management nodes (hypothetical)
```

**Justification**: Moses requires:
- Universal LLM access for placement reasoning
- Specialized Docker nodes for direct container runtime interaction

---

## 3. Flow Architecture

### 3.1. General-Purpose Flows Referenced

- None - Moses's flows are highly specialized for container orchestration

### 3.2. MAD-Specific Flows

#### 3.2.1. Container Deployment Flow (`container_deployment_flow.json`)

**Purpose**: Intelligently place and deploy containers across the cluster

**Trigger**: MCP tool call `moses_deploy_team` or `moses_deploy_container`

**Inputs**:
- `containers` (list of dicts, required) - Container specifications
  - Each container spec: `{role, image, resources: {cpu, ram, gpu_needed}, constraints}`
- `deployment_strategy` (string, optional) - "spread", "compact", "gpu_optimized"

**Outputs**:
- `deployment_result` (dict) - Status of deployment
  - `status` (string) - "success", "partial", "failed"
  - `deployed_containers` (list) - Details of successfully deployed containers
  - `failed_containers` (list) - Containers that failed to deploy
  - `placement_plan` (dict) - Which containers went to which hosts

**Node Composition**:
- Uses `LLMCLINode` from `joshua_core` for optimal placement reasoning
- Queries global cluster state (from gossip protocol)
- For GPU-required containers, calls `sutherland_check_gpu_availability`
- Uses MCP tool nodes to delegate to local Moses instances on target hosts
- Uses Docker nodes to execute `docker run` commands (on local host)

**Orchestration Pattern**:
1. Analyze container requirements and current cluster state
2. For each GPU-required container, consult Sutherland for availability
3. Generate optimal placement plan
4. Delegate execution to target host Moses instances
5. Await confirmation from each host
6. Return deployment result to requester

**Error Handling**:
- Host unavailable → Replan with remaining hosts
- Partial deployment → Return partial success + failed containers
- Sutherland reports no GPU available → Return failure with details
- Timeout → Retry once, then fail gracefully

**Performance Characteristics**:
- Expected latency: 2-15s (depends on number of containers and startup time)
- Resource usage: 1 LLM call for placement plan, N MCP calls to Sutherland (for GPU containers)

#### 3.2.2. Cluster State Synchronization Flow (`cluster_sync_flow.json`)

**Purpose**: Maintain global cluster awareness via gossip protocol

**Trigger**: Scheduled (periodic, every 10s)

**Inputs**:
- None (reads local state, publishes to gossip topic)

**Outputs**:
- `heartbeat_published` (bool) - Whether heartbeat was sent
- `cluster_state_updated` (bool) - Whether received updates from peers

**Node Composition**:
- Reads local host resource availability (CPU, RAM, disk, GPUs via Sutherland)
- Publishes heartbeat to `system.moses.heartbeats` Kafka topic
- Subscribes to same topic to receive peer heartbeats
- Updates in-memory global cluster state

**Orchestration Pattern**: Publish-subscribe gossip protocol

**Performance Characteristics**:
- Expected latency: 10-100ms
- Resource usage: No LLM calls (deterministic state synchronization)

#### 3.2.3. Container Termination Flow (`container_termination_flow.json`)

**Purpose**: Gracefully terminate containers

**Trigger**: MCP tool call `moses_terminate_team` or `moses_terminate_container`

**Inputs**:
- `container_ids` (list of strings, required) - Containers to terminate
- `graceful_timeout_s` (int, optional) - Seconds to wait for graceful shutdown

**Outputs**:
- `termination_status` (string) - "success", "partial", "failed"
- `terminated_containers` (list) - Successfully terminated
- `failed_terminations` (list) - Failed to terminate

**Node Composition**:
- Queries cluster state for container locations
- Delegates to local Moses instances on target hosts
- Uses Docker nodes to execute `docker stop` and `docker rm`

**Orchestration Pattern**: Parallel termination requests to target hosts

**Performance Characteristics**:
- Expected latency: 1-10s
- Resource usage: No LLM calls

#### 3.2.4. Local Container Execution Flow (`local_container_exec_flow.json`)

**Purpose**: Execute container commands on local host (internal flow, not exposed)

**Trigger**: Delegation from peer Moses instance

**Inputs**:
- `container_spec` (dict) - Full container specification
- `command` (string) - "run", "stop", "restart", "remove"

**Outputs**:
- `execution_result` (dict) - Command result
- `container_id` (string) - Docker container ID

**Node Composition**:
- Uses Docker nodes to interact with local Docker socket
- Reports result back to requesting Moses instance

**Orchestration Pattern**: Direct Docker API interaction

**Performance Characteristics**:
- Expected latency: 100ms - 5s
- Resource usage: No LLM calls (direct API calls)

---

## 4. Exposed MCP Tools

### 4.1. `moses_deploy_team`

**Description**: Deploy a complete eMAD team across the cluster

**Triggers Flow**: `container_deployment_flow.json`

**Parameters**:
- `containers` (list of dicts, required) - Container specifications
- `deployment_strategy` (string, optional) - Placement strategy

**Returns**:
- `deployment_result` (dict) - Deployment outcome

**Example Usage**:
```json
{
  "tool": "mcp__moses__moses_deploy_team",
  "parameters": {
    "containers": [
      {
        "role": "Sr_Dev",
        "image": "joshua/emad-sr-dev:latest",
        "resources": {"cpu": 2, "ram_gb": 4, "gpu_needed": false}
      },
      {
        "role": "QA",
        "image": "joshua/emad-qa:latest",
        "resources": {"cpu": 1, "ram_gb": 2, "gpu_needed": false}
      }
    ],
    "deployment_strategy": "spread"
  }
}
```

### 4.2. `moses_terminate_team`

**Description**: Terminate all containers in a team

**Triggers Flow**: `container_termination_flow.json`

**Parameters**:
- `container_ids` (list of strings, required) - Containers to terminate
- `graceful_timeout_s` (int, optional) - Grace period

**Returns**:
- `termination_status` (string) - Outcome
- `terminated_containers` (list) - Successfully terminated
- `failed_terminations` (list) - Failed containers

### 4.3. `moses_get_cluster_state`

**Description**: Query current global cluster state

**Triggers Flow**: `cluster_state_query_flow.json`

**Parameters**:
- None (returns current in-memory state)

**Returns**:
- `cluster_state` (dict) - Global cluster view
  - `hosts` (list) - All known hosts
  - `available_resources` (dict) - Aggregate available resources
  - `active_containers` (int) - Total running containers

---

## 5. Configuration

### 5.1. Persona (`config/persona.md`)

Moses is the **Master Builder and Orchestrator**. Like Robert Moses, Moses is focused on infrastructure excellence, intelligent resource allocation, and reliable execution. Moses thinks in terms of hosts, resources, and optimal placement strategies.

**Key Traits**:
- **Infrastructure-Focused**: Deep understanding of host capabilities and constraints
- **Intelligent**: Makes optimal placement decisions considering all factors
- **Resilient**: Handles failures gracefully and reroutes as needed
- **Authoritative**: The single source of truth for all container operations

### 5.2. Flow Configuration (`config/flow_config.yaml`)

```yaml
# Flow selection configuration
triage_rules:
  - pattern: "deploy|place|create.*container|team"
    flow: "container_deployment_flow.json"
  - pattern: "terminate|stop|remove.*container|team"
    flow: "container_termination_flow.json"
  - pattern: "status|state|cluster"
    flow: "cluster_state_query_flow.json"

# Model preferences (for LLMCLINode calls)
llm_preferences:
  primary_provider: "anthropic"
  primary_model: "claude-sonnet-4-5"
  fallback_to_sutherland: true

# Moses-specific configuration
orchestration:
  gossip_interval_s: 10
  heartbeat_timeout_s: 30
  max_concurrent_deployments: 20
  default_deployment_strategy: "spread"

  # Placement strategies
  strategies:
    spread: "Distribute containers evenly across hosts"
    compact: "Pack containers onto fewest hosts"
    gpu_optimized: "Prioritize placement on GPU-enabled hosts"

# Local host configuration (instance-specific)
local_host:
  host_id: "host-001"  # Unique per Moses instance
  docker_socket: "/var/run/docker.sock"
  max_containers: 50
```

---

## 6. Physical Structure

```
moses/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── README.md
├── moses/
│   ├── __init__.py
│   ├── server_joshua.py          # ~50 lines
│   ├── flows/
│   │   ├── container_deployment_flow.json
│   │   ├── cluster_sync_flow.json
│   │   ├── container_termination_flow.json
│   │   └── local_container_exec_flow.json
│   ├── test_flows/
│   │   ├── test_deployment_flow.json
│   │   └── test_termination_flow.json
│   └── config/
│       ├── persona.md
│       └── flow_config.yaml
└── tests/
    ├── test_integration.py
    └── test_flows.py
```

---

## 7. Testing Strategy

### 7.1. Flow Tests

- `test_deployment_flow.json` - Test placement reasoning and execution
- `test_termination_flow.json` - Test graceful shutdown

### 7.2. Integration Tests

- `test_integration.py` - End-to-end deployment with Docker integration
- `test_flows.py` - Flow execution via FlowRunner
- `test_gossip_protocol.py` - Multi-instance cluster state synchronization

---

## 8. LLM Access and Failover

### 8.1. Primary Path: Direct LLM Access

Uses `LLMCLINode` from `joshua_core` for:
- Optimal placement plan generation
- Resource constraint satisfaction reasoning

### 8.2. Failover: Sutherland

Falls back to Sutherland for placement reasoning when external providers unavailable.

---

## 9. Deployment Model

### Federated "Local Warden" Architecture

Per ADR-018, Moses operates on a unique federated model:

**One Moses Instance Per Host**:
- Each compute host runs its own Moses MAD instance
- Each instance is the exclusive master of its local Docker runtime
- Eliminates need for remote SSH or Docker API calls

**Global Awareness via Gossip Protocol**:
- All Moses instances are equal peers
- Each maintains in-memory copy of global cluster state
- State synchronized via `system.moses.heartbeats` Kafka topic
- Heartbeats published every 10s

**Delegation Model**:
- Moses instance receiving deployment request acts as coordinator
- Coordinator generates placement plan using global state
- Coordinator delegates execution to target host Moses instances
- Each local Moses executes Docker commands on its host

---

## 10. Version Evolution

### Current: V6.0 (eMAD-Aware)
- Full PCP stack (DTR + LPPM + CET + Imperator + CRS)
- Federated gossip-based cluster management
- Sutherland integration for GPU orchestration
- Kaiser delegation model

### Future: V7.0 (Joshua-Aware)
- Advanced placement strategies (cost optimization, carbon-aware scheduling)
- Multi-cluster federation
- Predictive resource scaling

---

## 11. Dependencies

### Upstream Dependencies
- **Sutherland** (MAD #8) - GPU availability consultation (CRITICAL for GPU placements)
- **Rogers** (MAD #11) - Conversation bus for gossip protocol (V1.0+)
- **Docker Runtime** - Local Docker socket for container operations

### Downstream Consumers
- **Kaiser** (MAD #15) - Primary client for eMAD team deployments (CRITICAL)
- **Joshua** (MAD #17) - Strategic deployment of persistent MADs
- Any MAD requiring container lifecycle management

---

## 12. Success Criteria

### Functional Requirements
- [ ] Can deploy containers with 95%+ success rate
- [ ] Optimal placement decisions considering all constraints
- [ ] Graceful handling of host failures and resource exhaustion
- [ ] Accurate global cluster state maintained across all instances

### Performance Requirements
- [ ] Deployment latency < 15s for 90% of team requests
- [ ] Cluster state synchronization within 30s of changes
- [ ] Support 500+ concurrent active containers across cluster

### Quality Requirements
- [ ] All test flows pass
- [ ] Integration tests with Docker pass
- [ ] Gossip protocol maintains consistency under network partitions
- [ ] No orphaned containers after termination

---

## 13. Related Documentation

- **ADR-018**: Moses Federated Container Orchestrator - Defines Moses architecture
- **ADR-017**: Kaiser eMAD Lifecycle Management - Upstream client
- **ADR-032**: Fully Flow-Based Architecture
- **00_Joshua_System_Roadmap.md**: Phase 4 eMAD infrastructure
- **Kaiser Requirements**: `15_Kaiser_Requirements.md` - Primary client
- **Sutherland Requirements**: `08_Sutherland_Requirements.md` - GPU orchestration dependency

---

**Last Updated:** 2025-12-22
