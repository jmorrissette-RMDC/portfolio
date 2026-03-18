# Kaiser V6.0 Requirements

- **Role**: eMAD Lifecycle Management (Team Assembler)
- **Version**: V6.0
- **MAD Number**: 15
- **Phase**: 4 (eMADs)

---

## 1. Overview

### Purpose

Kaiser is the dedicated, high-throughput service responsible for the tactical orchestration and lifecycle management of all ephemeral MADs (eMADs) in the Joshua ecosystem. Per **ADR-017**, Kaiser acts as the specialized "Team Assembler" or "Foreman," translating high-level team requests into declarative deployment orders and monitoring eMAD health throughout their short lifecycles.

Kaiser is the key enabling technology for the V6.0 "eMAD Revolution," providing the scalable infrastructure needed for massive parallel collaboration through ephemeral agent teams.

### Strategic Value

Kaiser enables the core V6.0 capability: intelligent eMAD teams for scalable, parallel, and complex task execution. By handling the high-frequency spawning and termination of eMADs, Kaiser allows persistent MADs to delegate complex work to ephemeral specialist teams without being burdened by infrastructure concerns.

**Architectural Role**: Kaiser bridges the gap between strategic planning (Joshua) and infrastructure placement (Moses), specializing in team composition expertise.

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
```

**Justification**: Kaiser's core logic is team composition reasoning, which is well-served by the universal LLM access node. No provider-specific or domain-specific nodes required.

---

## 3. Flow Architecture

### 3.1. General-Purpose Flows Referenced

- None - Kaiser's flows are highly specialized for eMAD lifecycle management

### 3.2. MAD-Specific Flows

#### 3.2.1. Team Assembly Flow (`team_assembly_flow.json`)

**Purpose**: Translate high-level team request into declarative deployment order

**Trigger**: MCP tool call `kaiser_assemble_team`

**Inputs**:
- `roles` (list of strings, required) - eMAD roles needed (e.g., ['Sr_Dev', 'QA', 'DevOps'])
- `project_context` (dict, optional) - Project metadata for team specialization
- `constraints` (dict, optional) - Resource constraints (GPU, RAM, etc.)

**Outputs**:
- `team_id` (string) - Unique identifier for spawned team
- `deployment_status` (string) - "success", "partial", "failed"
- `eMAD_endpoints` (list) - Connection details for each spawned eMAD
- `error` (string, optional) - Error message if deployment failed

**Node Composition**:
- Uses `LLMCLINode` from `joshua_core` to reason about role requirements
- Uses flow control nodes to construct deployment order
- Uses MCP tool nodes to call `moses_deploy_team`

**Orchestration Pattern**:
1. Analyze requested roles and determine resource requirements
2. Construct declarative deployment order for each eMAD
3. Make single delegation call to Moses
4. Await success/fail confirmation from Moses
5. Return team endpoints to requester

**Error Handling**:
- Moses reports partial deployment → Return partial team + error details
- Moses reports full failure → Log error, return failure status
- Timeout waiting for Moses → Retry once, then fail gracefully

**Performance Characteristics**:
- Expected latency: 2-10s (depends on container startup time)
- Resource usage: Single LLM call for role analysis

#### 3.2.2. Team Monitoring Flow (`team_monitoring_flow.json`)

**Purpose**: Monitor health of active eMAD teams

**Trigger**: Scheduled (periodic, every 30s)

**Inputs**:
- None (queries internal team registry)

**Outputs**:
- `health_report` (dict) - Status of all active teams
- `teams_terminated` (list) - Teams that completed and were cleaned up

**Node Composition**:
- Queries team registry for active teams
- Polls each eMAD for health status
- Identifies completed or failed eMADs
- Triggers termination flow for completed teams

**Orchestration Pattern**: Sequential polling with parallel health checks

**Performance Characteristics**:
- Expected latency: 100-500ms
- Resource usage: No LLM calls (deterministic health checking)

#### 3.2.3. Team Termination Flow (`team_termination_flow.json`)

**Purpose**: Orchestrate graceful shutdown of eMAD team

**Trigger**: MCP tool call `kaiser_terminate_team` or completion detected by monitoring

**Inputs**:
- `team_id` (string, required) - Team to terminate

**Outputs**:
- `termination_status` (string) - "success", "partial", "failed"
- `resources_released` (dict) - Summary of released resources

**Node Composition**:
- Delegates termination to Moses via `moses_terminate_team`
- Cleans up team registry

**Orchestration Pattern**: Delegate to Moses, await confirmation, cleanup local state

**Performance Characteristics**:
- Expected latency: 1-5s
- Resource usage: No LLM calls

---

## 4. Exposed MCP Tools

### 4.1. `kaiser_assemble_team`

**Description**: Request assembly of ephemeral MAD team for a project

**Triggers Flow**: `team_assembly_flow.json`

**Parameters**:
- `roles` (list of strings, required) - eMAD roles (e.g., ["Sr_Dev", "QA"])
- `project_context` (dict, optional) - Project metadata
- `constraints` (dict, optional) - Resource constraints

**Returns**:
- `team_id` (string) - Team identifier
- `deployment_status` (string) - "success", "partial", "failed"
- `eMAD_endpoints` (list) - Connection info for each eMAD
- `error` (string, optional) - Error details if failed

**Example Usage**:
```json
{
  "tool": "mcp__kaiser__kaiser_assemble_team",
  "parameters": {
    "roles": ["Sr_Dev", "QA", "DevOps"],
    "project_context": {
      "project_name": "web-app-refactor",
      "languages": ["python", "javascript"]
    },
    "constraints": {
      "gpu_required": false,
      "max_ram_gb": 8
    }
  }
}
```

### 4.2. `kaiser_terminate_team`

**Description**: Gracefully terminate an eMAD team

**Triggers Flow**: `team_termination_flow.json`

**Parameters**:
- `team_id` (string, required) - Team to terminate

**Returns**:
- `termination_status` (string) - "success", "partial", "failed"
- `resources_released` (dict) - Summary of released resources

**Example Usage**:
```json
{
  "tool": "mcp__kaiser__kaiser_terminate_team",
  "parameters": {
    "team_id": "team_abc123"
  }
}
```

### 4.3. `kaiser_get_team_status`

**Description**: Query current status of an eMAD team

**Triggers Flow**: `team_status_query_flow.json`

**Parameters**:
- `team_id` (string, required) - Team to query

**Returns**:
- `team_status` (dict) - Current team state
- `active_eMADs` (list) - Health status of each eMAD
- `uptime` (int) - Seconds since team was spawned

---

## 5. Configuration

### 5.1. Persona (`config/persona.md`)

Kaiser is the **efficient, high-throughput Team Assembler**. Think of Kaiser as the foreman on a construction site - focused on getting the right specialists to the job site quickly and reliably.

**Key Traits**:
- **Decisive**: Rapid team composition decisions without overthinking
- **Pragmatic**: Focuses on what's achievable with available resources
- **Reliable**: Ensures teams are properly deployed and monitored
- **Delegation-Oriented**: Trusts Moses to handle infrastructure details

### 5.2. Flow Configuration (`config/flow_config.yaml`)

```yaml
# Flow selection configuration
triage_rules:
  - pattern: "assemble|spawn|create.*team"
    flow: "team_assembly_flow.json"
  - pattern: "terminate|shutdown|destroy.*team"
    flow: "team_termination_flow.json"
  - pattern: "status|health|check.*team"
    flow: "team_status_query_flow.json"

# Model preferences (for LLMCLINode calls)
llm_preferences:
  primary_provider: "anthropic"
  primary_model: "claude-sonnet-4-5"
  fallback_to_sutherland: true

# Kaiser-specific configuration
team_management:
  max_concurrent_teams: 50
  team_health_check_interval_s: 30
  default_team_timeout_s: 3600  # 1 hour
  auto_terminate_on_completion: true
```

---

## 6. Physical Structure

```
kaiser/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── README.md
├── kaiser/
│   ├── __init__.py
│   ├── server_joshua.py          # ~50 lines
│   ├── flows/
│   │   ├── team_assembly_flow.json
│   │   ├── team_monitoring_flow.json
│   │   ├── team_termination_flow.json
│   │   └── team_status_query_flow.json
│   ├── test_flows/
│   │   ├── test_team_assembly_flow.json
│   │   └── test_team_termination_flow.json
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

- `test_team_assembly_flow.json` - Test eMAD role analysis and deployment order generation
- `test_team_termination_flow.json` - Test graceful shutdown flow

### 7.2. Integration Tests

- `test_integration.py` - End-to-end team spawning with Moses integration
- `test_flows.py` - Flow execution via FlowRunner

---

## 8. LLM Access and Failover

### 8.1. Primary Path: Direct LLM Access

Uses `LLMCLINode` from `joshua_core` for:
- Team composition reasoning (analyzing role requirements)
- Resource requirement estimation

### 8.2. Failover: Sutherland

Falls back to Sutherland for basic reasoning when external providers unavailable.

---

## 9. Version Evolution

### Current: V6.0 (eMAD-Aware)
- Full PCP stack (DTR + LPPM + CET + Imperator + CRS)
- eMAD team orchestration capability
- Delegation model with Moses

### Future: V7.0 (Joshua-Aware)
- Integration with Joshua for strategic team planning
- Advanced team optimization strategies
- Cross-project team resource sharing

---

## 10. Dependencies

### Upstream Dependencies
- **Moses** (MAD #16) - Container placement orchestration (CRITICAL)
- **Sutherland** (MAD #8) - Failover LLM inference
- **Rogers** (MAD #11) - Conversation bus communication (V1.0+)

### Downstream Consumers
- **Hopper** (MAD #1) - Primary eMAD team requester for development projects
- **Joshua** (MAD #17) - Strategic orchestration delegating to Kaiser
- Any MAD requiring parallel team execution (V6.0+)

---

## 11. Success Criteria

### Functional Requirements
- [ ] Can assemble eMAD teams with 95%+ success rate
- [ ] Team assembly latency < 10s for 90% of requests
- [ ] Graceful handling of partial deployment failures
- [ ] Automatic termination of completed teams

### Performance Requirements
- [ ] Support 50+ concurrent active eMAD teams
- [ ] Team health monitoring with < 1 minute detection of failures
- [ ] < 5s termination latency for team cleanup

### Quality Requirements
- [ ] All test flows pass
- [ ] Integration tests with Moses pass
- [ ] No orphaned eMAD containers after termination
- [ ] Accurate team registry maintained

---

## 12. Related Documentation

- **ADR-017**: Kaiser eMAD Lifecycle Management - Establishes Kaiser's role
- **ADR-018**: Moses Federated Container Orchestrator - Defines Moses delegation model
- **ADR-032**: Fully Flow-Based Architecture
- **00_Joshua_System_Roadmap.md**: Phase 4 eMAD architecture
- **Moses Requirements**: `16_Moses_Requirements.md` - Downstream dependency

---

**Last Updated:** 2025-12-22
