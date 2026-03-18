# ADR-042: Centralized Flow Controller for MAD Flow Management

**Status:** Proposed (Draft - Pending LangFlow Architecture Validation)

**Context:**

In V0.7, MADs implement their logic using LangFlow flows stored as `.json` files. Developers need the ability to:
1. **Visualize** flows across all MADs and environments (dev, test, prod)
2. **Monitor** live execution state of any flow
3. **Debug** historical flow executions (replay capability)
4. **Edit** flows interactively in dev environments only

The challenge is providing this centralized capability while:
- Keeping individual MAD containers lightweight (headless)
- Enforcing environment-specific write permissions
- Enabling perfect historical reconstruction of any execution
- Maintaining a clean V0→V1 migration path (WebSocket/MCP → Kafka bus)

**Decision:**

We will implement a **Centralized Flow Controller** architecture with the following components:

## 1. Component Architecture

### Hopper: The Flow Controller Hub
- **Runs the LangFlow Backend Server**: Hopper is the ONLY MAD that runs the full LangFlow backend (FastAPI/uvicorn)
- **Hosts Flow Controller UI**: Custom web interface for flow visualization and management
- **Centralized Monitoring**: Aggregates and visualizes flows from ALL MADs across ALL environments

### All Other MADs: Headless Execution
- **Run Joshua_Flow_Runner Only**: Pure execution engines with no web server
- **Lightweight**: Minimal resource footprint (~50-100MB RAM vs ~250-500MB with backend)
- **Event Publishers**: Emit execution events via Joshua_Communicator

## 2. Data Storage Architecture (MongoDB)

### `flows` Collection: Immutable Flow Versions
```
{
  "_id": "sha256_hash_of_flow_json",
  "mad_name": "horace-dev",
  "flow_name": "planning_flow",
  "timestamp": "2025-12-23T...",
  "structure": { ... complete flow.json ... }
}
```

**Purpose**: Content-addressable storage of flow versions
- **Deduplication**: Production flow executed 1M times = 1 document
- **Hash Stability**: Same flow content = same hash = same document
- **Version Tracking**: Every unique edit creates new hash/document

### `flow_executions` Collection: Execution Event Log
```
{
  "_id": "execution_uuid_123",
  "flow_hash": "sha256_hash_of_flow_json",  // Foreign key to flows._id
  "mad_name": "horace-dev",
  "flow_name": "planning_flow",
  "start_time": "2025-12-23T12:00:00Z",
  "status": "completed",
  "events": [
    { "event_type": "node_started", "node_id": "A", "timestamp": "...", "data": {...} },
    { "event_type": "node_finished", "node_id": "A", "timestamp": "...", "output": {...} },
    ...
  ]
}
```

**Purpose**: Lightweight execution records with relational reference
- **Scalable**: Millions of executions without data duplication
- **Fast Queries**: Indexed on `_id` (execution_id) and `flow_hash`

## 3. Flow Execution & Event Publishing

### Execution Workflow (Any MAD):

1. **FlowRunner Loads Flow**:
   - Reads `flows/planning_flow.json` from filesystem
   - Calculates SHA256 hash of JSON content
   - Upserts to `flows` collection (idempotent)

2. **Execution Starts**:
   - Creates execution document in `flow_executions` with `flow_hash` reference
   - Generates unique `execution_id`

3. **During Execution**:
   - FlowRunner executes nodes via LangFlow's Flow object
   - Generates events: `node_started`, `node_finished`, `error`, etc.
   - Calls `Joshua_Communicator.publish_event(event_data)`

4. **Event Publishing** (Environment-Agnostic):
   ```python
   # Same API call in all MADs, all environments
   communicator.publish_event({
       "execution_id": "uuid_123",
       "event_type": "node_finished",
       "node_id": "A",
       "output": {...}
   })
   ```

### Joshua_Communicator Implementation:

**V0.7 (Current - No Kafka Bus)**:
- Writes directly to MongoDB `flow_executions` collection
- Appends events to execution document's `events` array
- Direct database client embedded in library

**V1.0 (Future - Kafka Bus)**:
- Publishes events to Kafka topic `system.flow_events`
- Same `publish_event()` API, different implementation
- Zero changes to MAD code

## 4. Flow Controller Operations

### Viewing Flows (Live or Historical)

**User Action**: Select MAD + flow in Flow Controller UI

**Backend Process** (Hopper's LangFlow backend):
1. Query `flow_executions` for requested `execution_id`
2. Retrieve `flow_hash` from execution document
3. Query `flows` collection using `flow_hash` as key
4. Combine:
   - Flow structure (from `flows`)
   - Execution events (from `flow_executions`)
5. Stream to UI via WebSocket

**UI Rendering**:
- Renders visual graph from flow structure
- Overlays execution state from events:
  - Highlights active nodes (green)
  - Shows completed nodes (grey)
  - Displays errors (red)
  - Shows data flowing between nodes

### Editing Flows (dev Only)

**Environment-Based Write Control**:
- **dev**: Edit button enabled in UI
- **test/prod**: Edit button disabled/hidden (visual enforcement)

**Edit Workflow** (dev environment only):

1. **User edits flow** in Flow Controller UI, clicks "Save"
2. **Flow Controller backend** (Hopper):
   - Validates updated flow JSON
   - Makes MCP tool call: `horace_dev_hot_reload_flow(flow_name, flow_json)`
3. **Target dev MAD** (e.g., horace-dev):
   - Receives MCP call via its Action Engine
   - Writes updated JSON to `flows/planning_flow.json`
   - Calls `FlowRunner.reload_flow(flow_name)`
   - FlowRunner reloads flow into memory
4. **Next Execution**:
   - New SHA256 hash calculated
   - New version document created in `flows` collection
   - New executions reference new hash

**Server-Side Protection** (Future Enhancement):
- Modify LangFlow backend to check `JOSHUA_ENVIRONMENT` variable
- Reject write operations if not `dev` (403 Forbidden)
- Defense-in-depth: UI + server enforcement

## 5. Replay Debugging Capability

**"Roll Back the Clock" Feature**:

Because every execution stores:
1. Exact flow version (via content-addressable hash)
2. Complete event stream (all node executions, data, errors)

The Flow Controller can perfectly reconstruct ANY historical execution:

**Use Case**: Debug production failure from 2 weeks ago
1. Developer selects failed execution from history
2. Flow Controller retrieves:
   - Exact flow structure that ran (might be 5 versions old)
   - Complete event stream from that execution
3. UI renders step-by-step visualization:
   - Exact data that passed between nodes
   - Where failure occurred
   - Full error context
4. Developer sees EXACTLY what happened without reproduction

## 6. V0→V1 Migration Path

The architecture is designed for zero-touch migration:

**What Changes in V1.0**:
- `Joshua_Communicator.publish_event()` implementation only
- Events go to Kafka instead of MongoDB
- Babbage MAD consumes Kafka and writes to MongoDB (same schema)

**What Stays the Same**:
- MAD code (calls same API)
- Flow Controller (reads same MongoDB schema)
- UI/UX (identical user experience)
- Data model (same collections, same structure)

## 7. Resource Efficiency

**V0.7 MAD Resource Footprint**:
- **Headless (horace, starret, etc.)**: ~50-100MB RAM
- **Hopper (with LangFlow backend)**: ~250-500MB RAM

**Comparison to "Headed Everywhere" Alternative**:
- 10 MADs headed: 2.5-5GB RAM total
- 9 headless + 1 headed: 0.7-1.4GB RAM total
- **Savings**: ~75% reduction in memory overhead

**Scalability**:
- Adding new MADs adds ~75MB RAM (headless)
- Not ~400MB RAM (headed)
- Moses can pack more MADs per host

**Consequences:**

**Positive:**
- **Centralized UX**: Single UI for all flows across all MADs and environments
- **Lightweight MADs**: Headless execution keeps containers resource-efficient
- **Perfect Historical Debugging**: Exact flow version + complete event log = flawless replay
- **Scalable Data Model**: Content-addressable deduplication prevents bloat
- **Clean V0→V1 Migration**: Communicator abstraction enables seamless transition
- **Environment Safety**: Dev-only editing prevents accidental prod modifications
- **Observability**: Universal view into all flow executions system-wide

**Negative:**
- **MongoDB Dependency (V0.7)**: Requires shared MongoDB instance accessible to all MADs
- **Single Point of Failure (UI)**: If Hopper is down, flow visualization is unavailable (flows still execute)
- **Network Overhead (V0.7)**: Every event = MongoDB write (vs. batched Kafka in V1)
- **Storage Growth**: `flow_executions` collection grows with every run (requires retention policy)
- **LangFlow Backend Modification Risk**: Future LangFlow updates may break our integration

**Risks & Mitigations:**

1. **Risk**: LangFlow backend may not support reading external execution data
   - **Mitigation**: Research LangFlow architecture before implementation (see "Open Questions")

2. **Risk**: MongoDB write latency impacts flow execution performance
   - **Mitigation**: Async event publishing, connection pooling, bulk writes

3. **Risk**: Infinite storage growth in `flow_executions`
   - **Mitigation**: Implement TTL-based retention (e.g., 90 days for dev, 365 for prod)

**Related ADRs:**
- **ADR-032**: Fully Flow-Based Architecture (establishes flows as implementation standard)
- **ADR-025**: Environment-Specific Storage and Promotion Model (defines dev/test/prod)
- **ADR-021**: Unified Joshua_Communicator (abstraction layer for event publishing)

**Open Questions (Requiring Research):**

1. **Can LangFlow's backend read execution state from external MongoDB?**
   - Or must it only track flows it directly executes?

2. **How does LangFlow's Flow object emit execution events?**
   - Are there hooks/callbacks we can intercept?

3. **Can we inject external events into LangFlow's backend for visualization?**
   - Or must we build a custom visualization layer?

4. **What's the API for headless flow execution in LangFlow?**
   - `Flow.run()` method signature, event handling, etc.

**Next Steps:**

1. **Research LangFlow Architecture** (BLOCKING):
   - Study backend server internals
   - Understand headless execution API
   - Validate external data integration feasibility

2. **If Feasible**:
   - Build Joshua_Flow_Runner prototype
   - Implement MongoDB event publishing in Joshua_Communicator
   - Create proof-of-concept Flow Controller UI

3. **If Not Feasible**:
   - Design alternative architecture (possibly custom flow visualization)
   - Re-evaluate LangFlow as flow execution engine

---

**Status**: Draft pending LangFlow architecture validation
**Last Updated**: 2025-12-23
