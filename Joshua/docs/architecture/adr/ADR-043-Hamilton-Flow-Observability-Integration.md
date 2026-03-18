# ADR-043: Hamilton Flow Observability Integration with Langfuse

**Status:** Proposed

**Context:**

Per ADR-042, each MAD runs its own embedded LangFlow backend for flow execution. This architecture provides:
- ✅ Self-contained MAD development and debugging
- ✅ Support for Agent components (conversational memory)
- ✅ Standard LangFlow IDE per MAD

**However, it creates an observability challenge:**
- **Distributed UI**: To view Horace flows, browse to `horace-dev:7860`
- **Distributed UI**: To view Fiedler flows, browse to `fiedler-prod:7860`
- **No system-wide view**: Cannot see all flow executions across all MADs in one place
- **Manual correlation**: Difficult to trace multi-MAD workflows

**Operational requirements:**
1. **System-wide observability**: See all flow executions across all 40 MADs
2. **Historical replay**: Debug production failures by replaying exact execution trace
3. **Performance monitoring**: Track flow execution times, LLM costs, error rates
4. **Multi-MAD tracing**: Follow a user request as it flows through multiple MADs
5. **Alerting**: Detect and respond to flow failures automatically

**External observability platforms solve this problem:**
- **Langfuse**: Open-source LLM observability platform
- **LangSmith**: Commercial platform by LangChain
- **LangWatch**: Alternative observability solution

These platforms integrate with LangFlow via LangChain's callback system, automatically capturing execution traces from all MADs and centralizing them in one dashboard.

**Decision:**

Hamilton MAD (System Monitoring & Observability) will integrate with **Langfuse** to provide centralized flow observability across the entire Joshua ecosystem.

## Architecture

### Component Integration

```
┌─────────────────────────────────────────────────────────────┐
│                    All MAD Containers                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Horace-dev   │  │ Fiedler-prod │  │ Starret-test │ ...  │
│  │              │  │              │  │              │      │
│  │ LangFlow     │  │ LangFlow     │  │ LangFlow     │      │
│  │ Backend      │  │ Backend      │  │ Backend      │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
│         │                 │                 │               │
│         └─────────────────┴─────────────────┘               │
│                           │ Traces (via LangChain callbacks)│
└───────────────────────────┼─────────────────────────────────┘
                            ▼
                  ┌──────────────────────┐
                  │   Langfuse Platform  │
                  │   (Self-Hosted)      │
                  │                      │
                  │ - Trace Storage      │
                  │ - Web Dashboard      │
                  │ - REST API           │
                  └──────────┬───────────┘
                            ▲ │
                    Queries │ │ Reads
                            │ ▼
                  ┌──────────────────────┐
                  │   Hamilton MAD       │
                  │                      │
                  │ - Langfuse Client    │
                  │ - MCP Tools          │
                  │ - Alerting Logic     │
                  └──────────────────────┘
                            │
                            │ MCP Tools
                            ▼
                  ┌──────────────────────┐
                  │   Operators/MADs     │
                  │   (via Claude Code)  │
                  └──────────────────────┘
```

### Langfuse Integration Per MAD

**Environment Variables** (set in all MAD containers):
```bash
# Enable Langfuse tracing
LANGFUSE_PUBLIC_KEY=pk_xxx
LANGFUSE_SECRET_KEY=sk_xxx
LANGFUSE_HOST=https://langfuse.joshua.internal

# Tag traces with MAD identity
LANGFUSE_TAGS=mad:horace,env:dev,version:0.7
```

**Automatic Trace Capture**:
- LangFlow detects Langfuse environment variables on startup
- Automatically enables LangChain callback integration
- Every flow execution generates trace:
  - **Trace**: Top-level execution record (unique ID, start/end time, status)
  - **Spans**: Each node execution (node type, inputs, outputs, duration)
  - **Events**: LLM calls, tool invocations, errors
  - **Metadata**: MAD name, flow name, environment, user context

**Push-Based Model**:
- MADs **push** traces to Langfuse in real-time during execution
- No polling, no batch processing
- Events streamed as they occur
- Network failure resilient (traces buffered, retried)

### Hamilton MAD Responsibilities

Hamilton acts as the **centralized observability interface** for the Joshua ecosystem.

#### 1. Langfuse Client Integration

**Python SDK**:
```python
from langfuse import Langfuse

langfuse = Langfuse(
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
    secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
    host=os.getenv("LANGFUSE_HOST")
)
```

**Read-Only Access**:
- Hamilton reads from Langfuse (does not write traces)
- Queries for system-wide flow execution data
- Exposes data via MCP tools to operators

#### 2. MCP Tools for Flow Observability

**View Recent Executions**:
```python
hamilton_get_recent_flow_executions(
    mad_name: Optional[str] = None,
    flow_name: Optional[str] = None,
    environment: Optional[str] = None,
    limit: int = 20
) -> List[TraceMetadata]
```
- Lists recent flow executions across all MADs
- Filters by MAD, flow, environment
- Returns trace IDs, timestamps, status, duration

**Replay Execution**:
```python
hamilton_replay_flow_execution(
    trace_id: str
) -> DetailedTrace
```
- Retrieves complete trace for specific execution
- Returns:
  - Full flow structure (what ran)
  - Step-by-step node executions
  - Inputs/outputs for each node
  - LLM prompts and responses
  - Errors with stack traces
  - Timing breakdown

**Get Flow Performance Metrics**:
```python
hamilton_get_flow_performance(
    mad_name: str,
    flow_name: str,
    time_range: str = "24h"
) -> PerformanceMetrics
```
- Aggregates metrics across multiple executions:
  - Average/P50/P95/P99 execution time
  - Success rate (% of executions without errors)
  - Total LLM cost
  - Most common error types
  - Throughput (executions per hour)

**Search Flow Executions**:
```python
hamilton_search_flow_executions(
    query: str,
    filters: Dict[str, Any]
) -> List[TraceMetadata]
```
- Full-text search across traces
- Find executions by input data, output, error message
- Filter by tags, metadata, time range

**Multi-MAD Trace Correlation**:
```python
hamilton_trace_user_request(
    request_id: str
) -> DistributedTrace
```
- Follows a user request across multiple MADs
- Returns chronological trace of all MAD invocations
- Shows data flow between MADs
- Identifies bottlenecks in multi-MAD workflows

#### 3. Alerting and Anomaly Detection

**Failure Detection**:
- Hamilton polls Langfuse for recent failures (every 1 minute)
- Detects:
  - Flow execution errors
  - Timeout failures
  - LLM API errors
  - Performance degradation (P95 latency spike)

**Alert Actions**:
- Publish alert to Rogers conversation bus (V1.0)
- Log to Hamilton's monitoring database
- Expose via `hamilton_get_active_alerts()` MCP tool
- Operators query Hamilton for system health

**Example Alert**:
```json
{
  "alert_id": "alert_123",
  "severity": "critical",
  "mad_name": "horace-prod",
  "flow_name": "code_generation",
  "error_type": "LLMTimeout",
  "count": 5,
  "time_window": "5 minutes",
  "first_occurrence": "2025-12-23T14:30:00Z",
  "last_occurrence": "2025-12-23T14:35:00Z",
  "trace_ids": ["trace_1", "trace_2", "trace_3", "trace_4", "trace_5"]
}
```

### Langfuse Deployment

**Self-Hosted Installation**:
- Langfuse runs as Docker container on Joshua infrastructure
- PostgreSQL database for trace storage
- Redis for caching and session management
- Nginx reverse proxy for HTTPS

**Network Access**:
- **Internal**: All MADs access via `https://langfuse.joshua.internal`
- **External**: Developers access web dashboard for manual exploration
- **Hamilton**: Queries via REST API from within ecosystem

**Data Retention**:
- **dev**: 30 days (high volume, less critical)
- **test**: 90 days (validation traces)
- **prod**: 365 days (compliance, audit trail)

### Observability Workflow Examples

#### Example 1: Debug Production Failure

**Scenario**: Horace production flow failed, user reported incomplete code generation

**Workflow**:
1. Operator asks Claude Code: *"Show me recent Horace failures"*
2. Claude Code calls: `hamilton_get_recent_flow_executions(mad_name="horace-prod", status="failed")`
3. Hamilton queries Langfuse, returns list of failed traces
4. Operator: *"Replay trace trace_xyz"*
5. Claude Code calls: `hamilton_replay_flow_execution(trace_id="trace_xyz")`
6. Hamilton returns complete execution trace:
   - Input prompt
   - Each node's execution
   - **Error at "syntax_validation" node**: Timeout calling external linter
   - Root cause identified
7. Operator fixes timeout configuration

#### Example 2: Monitor Multi-MAD Workflow

**Scenario**: User request flows through Hopper → Fiedler → Horace → Starret

**Workflow**:
1. User submits request to Hopper with `request_id=req_123`
2. Each MAD tags traces with `request_id=req_123`
3. Operator asks: *"Trace request req_123"*
4. Claude Code calls: `hamilton_trace_user_request(request_id="req_123")`
5. Hamilton queries Langfuse for all traces with `request_id=req_123`
6. Returns chronological distributed trace:
   - Hopper: 200ms (plan generation)
   - Fiedler: 5000ms (LLM call) ← **BOTTLENECK**
   - Horace: 300ms (file write)
   - Starret: 800ms (git commit)
7. Operator identifies Fiedler LLM call as performance bottleneck

#### Example 3: Monitor System Health

**Scenario**: Operator checks overall system health

**Workflow**:
1. Operator asks: *"How are flows performing today?"*
2. Claude Code calls:
   - `hamilton_get_active_alerts()` → Returns 2 active alerts (Fiedler high latency)
   - `hamilton_get_flow_performance(mad_name="horace-prod", time_range="24h")` → 95% success rate, P95 latency 2.3s
3. Hamilton aggregates data from Langfuse
4. Operator sees system is healthy except for Fiedler performance issue
5. Drills into Fiedler metrics to investigate

## Migration Path (V0.7 → V1.0)

**V0.7 (Current)**:
- MADs push traces to Langfuse
- Hamilton queries Langfuse directly
- Observability via Hamilton MCP tools

**V1.0 (Rogers Conversation Bus)**:
- Same: MADs still push traces to Langfuse (unchanged)
- Same: Hamilton still queries Langfuse
- New: Hamilton also consumes flow event topic from Kafka (for real-time alerting)
- New: Babbage stores flow events in CQRS read models (duplicate of Langfuse data)

The Langfuse integration is **stable across V0→V1 migration**.

## Alternatives Considered

### Alternative A: Custom Event Store (MongoDB)
- **Idea**: MADs write execution events to MongoDB, Hamilton reads
- **Rejected**:
  - LangFlow doesn't support external event injection (per ADR-042 research)
  - Would require custom event capture code in each MAD
  - Duplicate effort building what Langfuse provides

### Alternative B: LangSmith (Commercial)
- **Idea**: Use LangChain's commercial platform instead of Langfuse
- **Rejected**:
  - Vendor lock-in
  - Cost at scale (40 MADs × high execution volume)
  - Less control over data retention

### Alternative C: No Centralized Observability
- **Idea**: Operators browse to each MAD's LangFlow UI individually
- **Rejected**:
  - Poor UX (must know which MAD to check)
  - Cannot correlate multi-MAD workflows
  - No system-wide alerting
  - No historical replay across MADs

**Consequences:**

**Positive:**
- **Centralized Visibility**: Single dashboard for all 40 MADs
- **Zero MAD Code Changes**: LangFlow automatically sends traces (just env vars)
- **Historical Replay**: Perfect debugging of production failures
- **Multi-MAD Tracing**: Follow requests across distributed workflows
- **Open Source**: Langfuse is self-hosted, no vendor lock-in
- **Mature Integration**: LangFlow natively supports Langfuse
- **Operator-Friendly**: Hamilton MCP tools integrate with Claude Code workflows

**Negative:**
- **External Dependency**: Langfuse must be available for observability
- **Storage Overhead**: Trace data grows with execution volume (retention policies required)
- **Network Overhead**: Every flow execution pushes data to Langfuse
- **Langfuse Learning Curve**: Operators must understand Langfuse data model
- **Dual UI**: LangFlow UI (per-MAD editing) + Langfuse UI (system-wide monitoring)

**Risks & Mitigations:**

1. **Risk**: Langfuse platform failure causes trace loss
   - **Mitigation**: Traces buffered in MADs, retried on failure
   - **Mitigation**: Langfuse deployed with high availability (replicas, backups)

2. **Risk**: Trace data leaks sensitive information
   - **Mitigation**: Langfuse access restricted to authenticated operators
   - **Mitigation**: PII scrubbing in traces (future enhancement)

3. **Risk**: High trace volume overwhelms Langfuse
   - **Mitigation**: Sampling (trace 100% in dev, 10% in prod)
   - **Mitigation**: Retention policies (auto-delete old traces)

4. **Risk**: LangFlow updates break Langfuse integration
   - **Mitigation**: Pin LangFlow version, test upgrades in dev first

**Related ADRs:**
- **ADR-042**: MAD Embedded LangFlow Backend Architecture (each MAD runs backend)
- **ADR-016**: Joshua MAD Orchestrator (Hamilton as monitoring MAD)
- **ADR-007**: Kafka-Based Conversation Bus (V1.0 event integration)

**Implementation Notes:**

### Langfuse Docker Deployment
```yaml
version: '3.8'
services:
  langfuse:
    image: langfuse/langfuse:latest
    environment:
      DATABASE_URL: postgresql://langfuse:password@postgres:5432/langfuse
      REDIS_URL: redis://redis:6379
      NEXTAUTH_URL: https://langfuse.joshua.internal
      NEXTAUTH_SECRET: <secret>
    ports:
      - "3000:3000"
    depends_on:
      - postgres
      - redis

  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: langfuse
      POSTGRES_USER: langfuse
      POSTGRES_PASSWORD: password
    volumes:
      - langfuse-db:/var/lib/postgresql/data

  redis:
    image: redis:7
    volumes:
      - langfuse-redis:/data
```

### Hamilton MCP Tool Example
```python
@mcp_tool
def hamilton_get_recent_flow_executions(
    mad_name: Optional[str] = None,
    flow_name: Optional[str] = None,
    environment: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 20
) -> List[Dict[str, Any]]:
    """
    Get recent flow executions across all MADs.

    Args:
        mad_name: Filter by MAD name (e.g., "horace-dev")
        flow_name: Filter by flow name (e.g., "code_generation")
        environment: Filter by environment (dev/test/prod)
        status: Filter by status (success/error/timeout)
        limit: Maximum number of results (default 20)

    Returns:
        List of trace metadata dictionaries
    """
    # Build Langfuse query
    query_params = {
        "limit": limit,
        "orderBy": "timestamp",
        "order": "desc"
    }

    # Apply filters
    if mad_name:
        query_params["tags"] = f"mad:{mad_name}"
    if environment:
        query_params["tags"] = f"env:{environment}"
    if status:
        query_params["status"] = status

    # Query Langfuse API
    traces = langfuse.get_traces(**query_params)

    # Format for display
    return [
        {
            "trace_id": trace.id,
            "mad_name": trace.tags.get("mad"),
            "flow_name": trace.name,
            "status": trace.status,
            "duration_ms": trace.duration,
            "start_time": trace.timestamp.isoformat(),
            "error": trace.output.get("error") if trace.status == "error" else None
        }
        for trace in traces
    ]
```

---

**Status**: Proposed
**Next Steps**:
1. Deploy self-hosted Langfuse instance on Joshua infrastructure
2. Configure Horace-dev with Langfuse environment variables (proof-of-concept)
3. Test trace capture and visualization
4. Implement Hamilton MCP tools for observability
5. Validate multi-MAD trace correlation

**Last Updated**: 2025-12-23

---

## Appendix: Decision Process

This appendix captures the conversation that led to recognizing the need for centralized observability and how Hamilton emerged as the natural integration point.

### The Distributed UI Problem

After establishing that each MAD would run its own LangFlow backend (ADR-042), a new challenge emerged:

**The architecture creates distributed UI:**
- Want to view Horace flows? → Browse to `horace-dev:7860`
- Want to view Fiedler flows? → Browse to `fiedler-prod:7860`
- Want to view Starret flows? → Browse to `starret-test:7860`

**Operational challenges:**
- No system-wide view of flow executions
- Cannot see all flows across all 40 MADs in one place
- Manual correlation required to trace multi-MAD workflows
- Must know which MAD to check for debugging

### Discovery of External Observability Platforms

**During LangFlow architecture research, external monitoring tools were discovered:**

From the research findings:
> "Observability Integrations (Potential Workaround):
> - LangFlow integrates with external observability platforms: **Langfuse, LangSmith, LangWatch**
> - These integrations use **LangChain's callback system** to capture execution traces
> - Setup via environment variables (e.g., `LANGSMITH_TRACING=true`)
> - Traces are automatically sent to the external platform during execution"

**Key characteristics:**
- **Push-based integration**: LangFlow pushes to external system (not pull-based)
- **Automatic capture**: Just set environment variables, traces flow automatically
- **No code changes**: Works with LangFlow as-is
- **Centralized dashboard**: All MAD traces in one place

### Database Discussion Clarification

**User asked about databases:**
> "there is a database though. and how do those external monitoring tools work?"

**Important distinction emerged:**
1. **LangFlow's database**: Required for Agent chat history (per-MAD)
   - Purpose: Conversational memory
   - Not for event storage/observability
   - Just LangFlow's standard requirement

2. **External observability database**: Langfuse's PostgreSQL
   - Purpose: Trace storage across all MADs
   - Centralized, system-wide
   - Separate from LangFlow databases

**This clarification prevented confusion between:**
- Runtime databases (per MAD, for Agents)
- Observability databases (centralized, for monitoring)

### Hamilton as Natural Integration Point

**User realization:**
> "yes it does [give centralized view]. One would imagine that is part of the monitoring MAD"

**This was the breakthrough insight:** Hamilton MAD (System Monitoring & Observability) is the perfect place to integrate observability tooling.

**Why Hamilton?**
1. **Mandate**: Hamilton's role is system-wide monitoring
2. **Operator interface**: Provides MCP tools for operational tasks
3. **Abstraction layer**: Hides Langfuse complexity from operators
4. **Aggregation point**: Combines multiple observability sources
5. **Alerting logic**: Detects failures, performance issues

**Architecture emerges:**
```
All MADs → Push traces → Langfuse
                            ↓
Hamilton → Read from Langfuse → Expose MCP tools
                                      ↓
Operators → Query Hamilton → Get system-wide observability
```

### Environment Variables vs. Direct Integration

**Original thought**: Should MADs write events directly to some database?

**Better approach discovered**: Use LangFlow's built-in Langfuse integration
- Set environment variables in MAD containers
- LangFlow automatically handles trace pushing
- No custom code in MADs
- No changes to flow execution logic

**Conversation example:**
> "If the execution events are being reported and stored, that presents an interesting capability that you could roll back the clock and see everything that happened at any time right?"

Response:
> "Yes, absolutely. That is a critical and powerful side-effect of this architecture. By having Hopper (or a data-manager MAD it calls, like Babbage) persist every reported flow event, we are creating a perfect, immutable audit log."

**But then the realization:**
> "so you dont want the events sent to hopper, you want them sent to an event store. In v0 the bus would transport them, but in v0 youd just write them directly. The change in the joshua communicator from v0 to v1 would handle the swap"

**This led to understanding**: Don't need custom event publishing code. Langfuse integration handles this automatically.

### The "Replay Debugging" Capability

**User insight about replay:**
> "if the execution events are being reported and stored, that presents an interesting capability that you could roll back the clock and see everything that happened at any time right?"

**This crystallized a key requirement:**
- Historical replay of any flow execution
- See exact inputs, outputs, errors
- Debug production failures weeks later
- No reproduction needed

**Langfuse provides this automatically:**
- Stores every trace with unique ID
- Full execution history (all nodes, all data)
- Query by execution ID
- Visualize step-by-step execution

### Multi-MAD Tracing Discussion

**Challenge identified**: How to trace requests across multiple MADs?

**Example scenario:**
User request flows: Hopper → Fiedler → Horace → Starret

**Solution**: Tag traces with shared `request_id`
```python
# Each MAD tags its trace
LANGFUSE_TAGS=mad:hopper,request_id:req_123
```

**Hamilton tool:**
```python
hamilton_trace_user_request(request_id="req_123")
```

Returns chronological distributed trace across all MADs.

### Why NOT Custom Event Store

**Original proposal included**: Custom event store (MongoDB/PostgreSQL) with MADs writing events

**Rejected because:**
1. **Duplicate effort**: Langfuse already provides this
2. **Maintenance burden**: Would need to maintain custom integration
3. **Lost features**: Langfuse UI, query capabilities, visualization
4. **Code changes**: Would require modifying every MAD
5. **LangFlow incompatibility**: Headless execution can't inject events (per ADR-042 research)

**Key quote:**
> "Mongo is not a requirements. it doesnt matter what this shit is stored in."

The database technology doesn't matter. What matters is:
- Automatic trace capture (Langfuse provides)
- Centralized visibility (Langfuse provides)
- No MAD code changes (Langfuse provides)

### V0 → V1 Migration Consideration

**Important architectural decision**: This observability architecture must work in both V0 and V1

**V0 (no Kafka bus):**
- MADs push traces directly to Langfuse
- Hamilton queries Langfuse
- Works immediately

**V1 (with Kafka bus):**
- MADs still push traces to Langfuse (unchanged!)
- Optionally: Flow events also published to Kafka
- Babbage consumes Kafka, writes to database
- Hamilton can query both Langfuse AND Babbage

**Key insight**: Langfuse integration is **V0/V1 agnostic**
- Same environment variables
- Same trace capture
- Same Hamilton tools
- Migration doesn't break observability

### Self-Hosted vs. Commercial

**Choice: Langfuse (open-source) over LangSmith (commercial)**

**Reasons:**
1. **Self-hosted**: Full control over data retention
2. **No vendor lock-in**: Can switch if needed
3. **Cost**: No per-trace fees at scale (40 MADs × high volume)
4. **Customization**: Can modify if needed
5. **Data sovereignty**: Traces stay on Joshua infrastructure

**Alternative B considered (LangSmith):**
- Mature, polished
- LangChain's official platform
- But: Commercial, cost at scale, vendor lock-in

### Hamilton MCP Tools Design

**Key realization**: Operators interact via Claude Code, which calls MCP tools

**Design principle**: Hamilton tools should feel natural in conversation

**Example workflow:**
```
Operator: "Show me recent Horace failures"
Claude Code: hamilton_get_recent_flow_executions(mad_name="horace-prod", status="failed")
Hamilton: [Returns list from Langfuse]

Operator: "Replay trace trace_xyz"
Claude Code: hamilton_replay_flow_execution(trace_id="trace_xyz")
Hamilton: [Returns complete execution trace]
```

**Tools designed for:**
- Natural language queries
- Progressive disclosure (list → detail)
- Multi-MAD correlation
- Alerting and health checks

### Key Lessons Learned

**1. Don't rebuild what exists**
- Langfuse/LangSmith already solve observability
- Building custom event store = duplicate effort
- Use mature tools correctly

**2. Centralization ≠ Central Execution**
- Distributed backends (per ADR-042)
- Centralized observability (this ADR)
- Different concerns, different solutions

**3. Hamilton as Interface Layer**
- Don't expose Langfuse directly to operators
- Hamilton provides Joshua-specific abstractions
- MCP tools integrate with Claude Code workflows

**4. Environment Variables > Code**
- Simple configuration
- No MAD modifications
- Works with LangFlow as-is

**5. V0/V1 Stability**
- Observability works before the bus exists
- Same observability after bus migration
- Stable across architectural evolution

---

**Conclusion:**

This ADR emerged from recognizing that distributed backends (ADR-042) don't preclude centralized observability. External monitoring platforms like Langfuse provide exactly the capabilities needed:
- Automatic trace capture (no code changes)
- Centralized visibility (single dashboard)
- Historical replay (debugging capability)
- Multi-MAD correlation (distributed tracing)

Hamilton's role as the interface layer was a natural fit, providing Joshua-specific observability tools that integrate seamlessly with Claude Code workflows. The result is a clean separation: LangFlow handles execution, Langfuse handles observability, Hamilton provides the operator interface.
