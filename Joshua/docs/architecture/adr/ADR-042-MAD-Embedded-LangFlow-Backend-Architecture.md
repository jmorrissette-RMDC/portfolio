# ADR-042: MAD Embedded LangFlow Backend Architecture

**Status:** Proposed

**Context:**

In V0.7, MADs implement their logic using LangFlow flows stored as `.json` files. Developers need the ability to:
1. **Execute** flows that use Agent components (conversational agents with memory)
2. **Visualize** flows during development and debugging
3. **Edit** flows interactively in dev environments
4. **Monitor** flow execution state

Initial explorations considered a centralized "Flow Controller" architecture where:
- Individual MADs would run headless (no LangFlow backend)
- A central backend (hosted by Hopper) would aggregate and visualize all flows
- Execution events would be published to a central database

**Research findings revealed this architecture is not feasible:**

1. **Agent Components Require Backend**:
   - LangFlow's `run_flow_from_json()` (headless execution) fails with Agent components
   - Error: `sqlite3.OperationalError: no such table: message`
   - Agents require chat history database which only exists when backend is running
   - 100% of MAD flows use Agent components

2. **No External Event Injection**:
   - LangFlow backend only tracks flows it directly executes in its own process
   - No API to inject execution events from external processes
   - Cannot visualize flows running in remote containers

3. **Backend IS the Executor**:
   - FastAPI backend receives flow execution requests
   - Backend directly instantiates Flow object in its Python process
   - Backend has in-memory access to execution state
   - Events generated during execution, not read from external source

**Decision:**

Every MAD will run its own embedded LangFlow backend server. There will be no centralized "Flow Controller" hub.

## Architecture

### Each Persistent MAD Container Includes:

1. **LangFlow Backend Server** (FastAPI/uvicorn on port 7860)
   - Full backend process (not headless)
   - Serves both API and UI
   - Manages flow execution in its own process

2. **LangFlow Database** (PostgreSQL or SQLite)
   - Stores Agent chat history and conversation memory
   - Flow metadata and execution logs
   - Per-MAD choice of database engine

3. **Flow Storage** (`flows/` directory)
   - `.json` flow definitions
   - Loaded and executed by LangFlow backend
   - Versioned in git with MAD code

4. **LangFlow UI** (React frontend)
   - Visual flow editor
   - Playground for testing flows
   - Real-time execution monitoring

### Per-MAD Access Pattern

**Development Workflow**:
- Developer wants to work on Horace flows
- Browse to `http://horace-dev:7860`
- Full LangFlow IDE loads
- Edit flows visually, test in playground, monitor executions

**Production Monitoring**:
- Operator wants to view Fiedler production flows
- Browse to `http://fiedler-prod:7860`
- Read-only view (enforced by environment-specific permissions)
- See flow definitions, cannot edit

### Environment-Specific Configuration

Each MAD container sets `JOSHUA_ENVIRONMENT` variable:
- **dev**: LangFlow UI fully interactive (read/write)
- **test**: LangFlow UI read-only (future: server-side enforcement)
- **prod**: LangFlow UI read-only (future: server-side enforcement)

### Resource Footprint

**Per Persistent MAD**:
- **LangFlow Backend**: ~250-500MB RAM
- **Database** (PostgreSQL): ~50-100MB RAM
- **Total**: ~300-600MB RAM per MAD

**System-Wide** (40 persistent MADs):
- **Total RAM**: 12-24GB across all MADs
- **Distribution**: Spread across multiple servers (per ADR-016, ADR-018)
- **Acceptable**: Modern servers have 64-256GB RAM

### Ephemeral MADs (eMADs) - Special Case

**Problem**: eMADs could spawn 100s-1000s of instances
- 500MB × 1000 eMADs = 500GB RAM overhead = NOT acceptable

**Solution**: eMADs share central LangFlow backend(s)
- Kaiser spawns lightweight eMAD containers (no embedded backend)
- eMADs connect to shared LangFlow backend pool for execution
- Central backends manage ephemeral flow executions
- Details in future ADR (eMAD architecture)

## Integration with Observability (ADR-043)

While each MAD has its own backend, **centralized observability** is achieved through external monitoring platforms:

**All MADs configured with environment variables**:
```bash
LANGFUSE_PUBLIC_KEY=xxx
LANGFUSE_SECRET_KEY=xxx
LANGFUSE_HOST=https://langfuse.joshua.internal
```

**Execution traces automatically pushed to Langfuse/LangSmith**:
- Node executions, data flow, LLM calls
- Prompts, responses, errors, timing, costs
- All MADs visible in one dashboard

**Hamilton MAD provides unified interface**:
- Reads from Langfuse/LangSmith APIs
- Exposes MCP tools for system-wide flow observability
- See ADR-043 for details

## Migration Path (V0.7 → V1.0)

**V0.7 (Current)**:
- Each MAD: Embedded LangFlow backend
- Direct access: `http://mad-name:7860`
- No bus integration

**V1.0 (Rogers Conversation Bus)**:
- Same: Each MAD still runs LangFlow backend
- Same: Direct access still works
- New: Flow execution events also published to Kafka
- New: Babbage consumes flow events for permanent logging
- Unchanged: LangFlow execution model (backend-centric)

The embedded backend architecture is **stable across V0→V1 migration**.

## Alternatives Considered

### Alternative A: Centralized Flow Controller
- **Idea**: Hopper hosts single LangFlow backend, all MADs run headless
- **Rejected**:
  - Headless execution fails with Agent components
  - LangFlow cannot visualize external executions
  - Would require forking LangFlow

### Alternative B: Custom Flow Execution Engine
- **Idea**: Build custom executor + visualization, use LangFlow only for design
- **Rejected**:
  - Significant engineering effort
  - Lose LangFlow's mature component ecosystem
  - Maintenance burden for custom executor

### Alternative C: Shared Backend Pool for Persistent MADs
- **Idea**: Multiple MADs share one LangFlow backend instance
- **Rejected**:
  - Tight coupling between MADs
  - Failure cascades across MADs
  - Database isolation issues
  - Violates cellular monolith principle

**Consequences:**

**Positive:**
- **Works with Agent Components**: Each backend provides database for Agents
- **Self-Contained MADs**: Each MAD is independent, can develop/test/debug in isolation
- **No Custom Development**: Uses LangFlow as-is, no forking required
- **Familiar UX**: Developers use standard LangFlow IDE
- **Simple Deployment**: Each MAD is a complete unit (code + backend + database)
- **Cellular Monolith Alignment**: Each MAD is independently deployable and operable

**Negative:**
- **Resource Overhead**: 300-600MB RAM per MAD (vs ~50-100MB pure headless)
- **Distributed UI**: No single pane of glass for all flows (must browse to each MAD)
- **Image Size**: LangFlow adds ~1.5-2GB to each MAD Docker image
- **Startup Time**: 2-5 seconds backend initialization on container start
- **Backend Maintenance**: Must keep LangFlow updated across all MAD images

**Risks & Mitigations:**

1. **Risk**: LangFlow version conflicts across MADs
   - **Mitigation**: Pin LangFlow version in base image, update systematically

2. **Risk**: Database overhead (40 PostgreSQL instances)
   - **Mitigation**: Use SQLite for dev/test, PostgreSQL only for prod MADs

3. **Risk**: Port conflicts on same host
   - **Mitigation**: Moses maps MAD ports uniquely (7860 internal → unique external)

4. **Risk**: LangFlow security vulnerabilities
   - **Mitigation**: Network isolation, authentication required, McNamara security scans

**Related ADRs:**
- **ADR-032**: Fully Flow-Based Architecture (establishes flows as implementation standard)
- **ADR-025**: Environment-Specific Storage and Promotion Model (defines dev/test/prod)
- **ADR-043**: Hamilton Flow Observability Integration (centralized monitoring)
- **ADR-016**: Joshua MAD Orchestrator (persistent MAD deployment)
- **ADR-018**: Moses Container Orchestrator (container placement and networking)

**Implementation Notes:**

### MAD Dockerfile Template
```dockerfile
FROM langflow/langflow:latest

# Install MAD-specific Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy MAD code and flows
COPY . /app/mad_name/

# Set environment variables
ENV JOSHUA_ENVIRONMENT=${ENVIRONMENT}
ENV LANGFUSE_PUBLIC_KEY=${LANGFUSE_PUBLIC_KEY}
ENV LANGFUSE_SECRET_KEY=${LANGFUSE_SECRET_KEY}

# Expose LangFlow port
EXPOSE 7860

# Start LangFlow backend
CMD ["langflow", "run", "--host", "0.0.0.0", "--port", "7860"]
```

### Database Configuration
**dev/test**: SQLite (simpler, lower overhead)
```bash
LANGFLOW_DATABASE_URL=sqlite:///./langflow.db
```

**prod**: PostgreSQL (better for concurrent access)
```bash
LANGFLOW_DATABASE_URL=postgresql://user:pass@postgres:5432/mad_name
```

### Network Access
- **Internal**: MADs access each other via Docker network DNS
- **External Dev**: Developers access via mapped ports (e.g., `localhost:8001` → `horace-dev:7860`)
- **External Prod**: Grace or Cerf proxy to specific MAD backends (authenticated)

---

**Status**: Proposed
**Next Steps**:
1. Build proof-of-concept Horace MAD with embedded LangFlow backend
2. Test Agent component execution and database requirements
3. Validate resource overhead measurements
4. Write ADR-043 (Hamilton observability integration)

**Last Updated**: 2025-12-23

---

## Appendix: Decision Process

This appendix captures the key conversation and research that led to this architectural decision. The original proposal was significantly different, and understanding the evolution is critical for future architectural decisions.

### Initial Proposal: Centralized Flow Controller

**Original Concept** (discussed with Gemini AI):
- Individual MADs would run **headless** (no LangFlow backend)
- Events would be published to external database (originally MongoDB, later clarified as database-agnostic)
- **Hopper would host a central LangFlow backend** (the "Flow Controller")
- This central backend would read events from the database and visualize all MAD flows
- Benefits: Lightweight MADs (~50-100MB each), single UI for all flows

**Quote from conversation:**
> "Every MAD Runs a Server: To enable live inspection, every MAD container in every environment will run the standard LangFlow backend server."

**User correction:**
> "stop talking about 'inspection', you are just making shit up. There is no 'inspection', its just read vs read/write. When I open a doc in read only there is no magical state called inspection. The UI can connect to all flows in all environments. Write is only available in Dev"

**Clarified concept:**
- Central UI can connect to any MAD's flows
- Environment-based permissions: dev = read/write, test/prod = read-only
- Write permissions enforced server-side via `JOSHUA_ENVIRONMENT` variable

### Critical Discovery #1: LangFlow Backend Cannot Read External Events

**Research finding:**
> "LangFlow backend CANNOT read execution events from external sources. Backend only tracks flows it directly executes in its own process. No API to inject execution events from external processes."

**Key question from user:**
> "Backend only tracks flows it directly executes in its own process - Why? How does it read its own processes?"

**Answer:**
The LangFlow backend **IS** the executor:
1. Backend receives flow execution request
2. Backend directly instantiates Flow object in its Python process
3. Backend has direct in-memory access to execution state
4. Events are generated during execution, not read from external source
5. No external event injection mechanism exists

**User realization:**
> "so, no matter what you do, the backend has to exist because without it there is nothing that executes the flows?"

**Response:**
> "NO - the backend does NOT have to exist to execute flows! Headless execution WITHOUT backend:
> ```python
> from langflow.load import load_flow_from_json
> flow = load_flow_from_json("planning_flow.json")
> result = flow(inputs={"query": "..."})
> ```"

### Critical Discovery #2: Agent Components Require Backend

**Research finding:**
> "HOWEVER - Critical Limitation:
> - Simple flows (just LLM calls, data processing): ✅ Work headlessly
> - Flows with Agent components: ❌ FAIL headlessly
>   - Agents need chat history database
>   - Error: `sqlite3.OperationalError: no such table: message`
>   - Requires database backend to run"

**User confirmation:**
> "the answer is 100% yes [MAD flows use Agent components]"

### Critical Realization: Original Architecture is Infeasible

**If 100% of MAD flows use Agent components:**
1. MADs CANNOT run pure headless (`run_flow_from_json` will crash)
2. Each MAD MUST have database (for Agent chat history)
3. Each MAD MUST have LangFlow backend process (to access database)
4. This means ~250-500MB RAM per MAD (the overhead we tried to avoid)
5. Each MAD backend only tracks its own flows
6. No way to centralize visualization in one LangFlow backend

**The original centralized Flow Controller architecture was completely broken.**

### The Pivot: Accept the Overhead

**User decision:**
> "the path is pretty clear. MVP dont have to be ideal, accepting the overhead is the only option, then seek optimization at a later date. This isn't really a problem for MADs. If we have 40 mads that would be at most 20GB. We've got a bunch of servers to locate them on and 20GB is not really that much."

**Simplified architecture emerges:**
- Every persistent MAD gets its own LangFlow backend
- Want to view/edit Horace flows? Browse to `horace-dev:7860`
- Want to view Fiedler flows? Browse to `fiedler-dev:7860`
- No centralized "Flow Controller" hub
- No event database
- Each MAD is self-contained

**User:**
> "The problem is the eMADs. But they could operate off of a central backend. This also means that we dont have to build any hybrid infrastructure for Hopper. Every mad gets a head, so if you want to play with the flows, just go there."

### Database Discussion

**User clarification:**
> "there is a database though. and how do those external monitoring tools work?"

**Clarification:**
- Yes, each LangFlow backend needs a database
- Purpose: Agent chat history (conversations, memory)
- Options: PostgreSQL or SQLite
- This is NOT the event store from original proposal
- This is just LangFlow's standard database requirement

### External Monitoring Tools Discovery

**How Langfuse/LangSmith work:**
1. Setup via environment variables in each MAD container
2. During execution, LangFlow **pushes** trace data to external platform
3. Centralized viewing in Langfuse/LangSmith web UI
4. Separate from LangFlow visual flow editor

**User realization:**
> "yes it does [give centralized view]. One would imagine that is part of the monitoring MAD"

**Exactly right:**
> "Hamilton MAD as Central Observability Hub would manage Langfuse/LangSmith configuration, provide unified dashboard, expose tools for flow execution monitoring."

### Key Lessons Learned

**Why the original architecture failed:**
1. **Assumption**: LangFlow backend can visualize flows it didn't execute
   - **Reality**: Backend must BE the executor to track execution

2. **Assumption**: Headless execution works for all flows
   - **Reality**: Agent components require database, which requires backend

3. **Assumption**: Centralization requires central backend
   - **Reality**: Centralization achieved via external observability platform

**Why the final architecture works:**
1. **Embraces LangFlow's architecture** instead of fighting it
2. **Accepts resource overhead** as acceptable tradeoff (20GB across 40 MADs)
3. **Uses external tools correctly** (Langfuse for centralized observability)
4. **Keeps MADs self-contained** (cellular monolith principle)
5. **Defers optimization** (eMADs will share backends, future optimization possible)

### MongoDB Clarification

**Important note from conversation:**
> "Mongo is not a requirements. it doesnt matter what this shit is stored in. I wish that was not part of your research because it obscure the key points."

The database technology (MongoDB, PostgreSQL, SQLite) was **never the architectural constraint**. The fundamental issue was that LangFlow backend cannot read external execution events **regardless of storage technology**. The backend must execute the flows itself.

This clarification prevented getting stuck on database technology debates and focused on the core architectural incompatibility.

---

**Conclusion:**

This architecture evolved through discovery, not initial design. The research into LangFlow's actual capabilities was critical to understanding why the elegant centralized solution wouldn't work and why the "every MAD gets a backend" solution, despite appearing inelegant, is actually the only feasible path given:
1. LangFlow's execution model (backend-centric)
2. Agent components' database requirements
3. The need for self-contained, independently operable MADs

Future optimizations (eMAD backend sharing, custom flow executors) can be explored once the basic architecture is proven in production.
