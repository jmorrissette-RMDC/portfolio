# ADR-044: Monorepo Library Distribution Pattern

**Status:** Accepted

**Context:**

The Joshua system consists of multiple MADs (Microservice Autonomous Domains) that share common functionality through libraries. These libraries include:

- **Action Engine Libraries**: `joshua_network`, `joshua_logger`, `joshua_communicator`, `joshua_flow_runner`
- **Thought Engine Libraries**: `joshua_thought_engine` (contains PCP pipeline)
- **Domain-Specific Libraries**: `joshua_ssh`, `joshua_bus_client`

Key characteristics of the Joshua ecosystem:
1. **Cellular Monolith Architecture**: All MADs deployed together as a cohesive system
2. **Internal-Only Libraries**: No external consumers, libraries serve Joshua MADs exclusively
3. **Coordinated Evolution**: MAD capabilities evolve together through phases (V0.7, V0.8, V1.0, etc.)
4. **Shared Codebase**: All code lives in `/mnt/projects/Joshua/` repository
5. **Consistent Dependencies**: MADs should use compatible library versions for system coherence

The question is: **How should shared libraries be distributed to MADs during development, testing, and production?**

**Decision:**

Joshua will use a **monorepo with local editable pip installs** for library distribution. Libraries remain in the Joshua repository and are installed into MAD containers using `pip install -e` from local paths.

## Architecture

### 1. Repository Structure

```
/mnt/projects/Joshua/
├── lib/                                    # All shared libraries
│   ├── joshua_network/
│   │   ├── joshua_network/
│   │   │   ├── __init__.py
│   │   │   └── websocket_client.py
│   │   ├── pyproject.toml
│   │   └── README.md
│   ├── joshua_logger/
│   │   ├── joshua_logger/
│   │   ├── pyproject.toml
│   │   └── README.md
│   ├── joshua_thought_engine/
│   │   ├── joshua_thought_engine/
│   │   │   ├── pcp/
│   │   │   │   ├── flows/             # PCP flow definitions
│   │   │   │   └── config/            # PCP configuration
│   │   │   └── __init__.py
│   │   ├── pyproject.toml
│   │   └── README.md
│   └── joshua_communicator/
│       ├── joshua_communicator/
│       ├── pyproject.toml
│       └── README.md
├── mads/                                   # All MAD implementations
│   ├── template/
│   ├── fiedler/
│   └── grace/
└── docs/
```

### 2. Library Packaging Pattern

Each library uses standard Python packaging with `pyproject.toml`:

```toml
# lib/joshua_thought_engine/pyproject.toml
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "joshua-thought-engine"
version = "0.7.0"
description = "Progressive Cognitive Pipeline for Joshua MADs"
requires-python = ">=3.11"
dependencies = [
    "langflow>=1.5.0",
    "langfuse-sdk>=2.0.0",
]

[tool.setuptools]
packages = ["joshua_thought_engine"]

[tool.setuptools.package-data]
joshua_thought_engine = ["pcp/flows/*.json", "pcp/config/*.yaml"]
```

**Key aspects:**
- Libraries declare their own dependencies
- Flow files (`.json`) and configs (`.yaml`) included via `package-data`
- Standard Python packaging conventions
- Version matches MAD version target (e.g., 0.7.0 for V0.7 MADs)

### 3. Development Workflow

**Hot-mounted volumes for instant iteration:**

```yaml
# mads/template/docker-compose.dev.yml
services:
  template-dev:
    build:
      context: ../../
      dockerfile: mads/template/Dockerfile
    volumes:
      # Hot-mount MAD code
      - ./template:/app/template

      # Hot-mount libraries for live editing
      - ../../lib/joshua_network:/app/lib/joshua_network
      - ../../lib/joshua_logger:/app/lib/joshua_logger
      - ../../lib/joshua_thought_engine:/app/lib/joshua_thought_engine
      - ../../lib/joshua_communicator:/app/lib/joshua_communicator
    environment:
      - JOSHUA_ENVIRONMENT=dev
```

**Initial container build:**

```dockerfile
# mads/template/Dockerfile
FROM langflow/langflow:latest

# Copy all libraries
COPY lib/ /app/lib/

# Install libraries in editable mode
RUN pip install -e /app/lib/joshua_network \
                 -e /app/lib/joshua_logger \
                 -e /app/lib/joshua_thought_engine \
                 -e /app/lib/joshua_communicator

# Copy MAD code
COPY mads/template /app/template

WORKDIR /app
CMD ["python", "-m", "template.server_joshua"]
```

**Development experience:**
1. Edit `/mnt/projects/Joshua/lib/joshua_thought_engine/pcp/flows/imperator.json`
2. Change is instantly visible in mounted container
3. No rebuild required for code/flow changes
4. Rebuild only needed if dependencies change in `pyproject.toml`

### 4. Test/Production Deployment

**No hot-mounting, immutable containers:**

```yaml
# mads/template/docker-compose.prod.yml
services:
  template-prod:
    build:
      context: ../../
      dockerfile: mads/template/Dockerfile
    # No volume mounts - everything baked into image
    environment:
      - JOSHUA_ENVIRONMENT=prod
```

**Same Dockerfile as development:**
- `COPY lib/` bakes libraries into image
- `pip install -e` installs from baked-in paths
- Result: Immutable container with known library versions

### 5. Dependency Management

**MAD declares only direct library dependencies:**

```txt
# mads/template/requirements.txt
joshua_thought_engine>=0.7.0
joshua_communicator>=0.7.0

# DO NOT declare transitive dependencies
# (langflow, langfuse, websockets, etc.)
# Libraries declare these in their pyproject.toml
```

**Library declares its own dependencies:**

```toml
# lib/joshua_thought_engine/pyproject.toml
dependencies = [
    "langflow>=1.5.0",
    "langfuse-sdk>=2.0.0",
]
```

**When MAD container builds:**
```bash
pip install -e /app/lib/joshua_thought_engine
# Automatically installs langflow and langfuse
```

**Benefits:**
- Add langflow dependency → Edit one pyproject.toml → Rebuild → All MADs get it
- Remove 40 instances of same dependency from 40 MAD requirements.txt files
- Single source of truth for library dependencies

### 6. Versioning Strategy

**Git-based versioning, not semantic versioning:**

- **Version numbers align with MAD phases**: v0.7.0, v0.8.0, v1.0.0, v5.0.0
- **All libraries progress together**: When system moves to V0.8, all libraries tagged v0.8.0
- **Git tags mark releases**: `git tag v0.8.0 -m "Context-Aware Reasoning Release"`
- **No independent library versions**: joshua_thought_engine v0.7.0 and joshua_communicator v0.7.0 tested together

**Why coordinated versioning?**
- Libraries tested together as a cohesive system
- Avoids compatibility matrix complexity (TE v1 + Comm v2 + Network v3 = which combinations work?)
- Reflects reality: Joshua evolves as integrated system, not independent libraries

### 7. Flow Distribution

**Flow files are packaged assets:**

```python
# MAD code can reference library flows
import joshua_thought_engine
from pathlib import Path

# Get path to PCP flows
pcp_flows = Path(joshua_thought_engine.__file__).parent / "pcp" / "flows"
imperator_flow = pcp_flows / "tier4_imperator.json"

# Load and execute
flow_runner.execute_flow(imperator_flow, inputs={...})
```

**Or LangFlow can reference directly if subflow support exists:**

```json
{
  "component": "Subflow",
  "flow_path": "joshua_thought_engine/pcp/flows/tier4_imperator.json"
}
```

**Development vs Production:**
- **Dev**: Flows hot-mounted, edit → save → instantly active
- **Prod**: Flows baked into image, immutable

## Alternatives Considered

### Alternative A: Publish to PyPI

**Approach:**
- Publish `joshua-thought-engine`, `joshua-communicator`, etc. to PyPI
- MADs install via `pip install joshua-thought-engine==0.7.0`

**Rejected because:**
- **Unnecessary overhead**: Publish workflow, PyPI credentials management, no external consumers
- **Slower iteration**: Change library → publish to PyPI → update MAD requirements → rebuild (vs. change → rebuild)
- **Version fragmentation risk**: MAD A could end up on TE v0.7.0, MAD B on v0.8.0 unintentionally
- **Monorepo benefits lost**: Atomic commits across library + MAD changes not possible
- **No value added**: PyPI solves external distribution, we have no external users

### Alternative B: PYTHONPATH Only (No pip)

**Approach:**
```dockerfile
COPY lib/ /app/lib/
ENV PYTHONPATH=/app/lib:$PYTHONPATH
```

**Rejected because:**
- **Dependency explosion in MADs**: Every MAD must list langflow, langfuse, websockets, structlog, etc.
- **Maintenance burden**: Add library dependency → update 40 MAD requirements.txt files
- **No metadata**: Can't query package versions, no entry points support
- **Already using pip**: joshua-libs already packaged, changing pattern creates inconsistency

### Alternative C: Git Submodules

**Approach:**
- Each library in separate git repo
- MADs include libraries as git submodules

**Rejected because:**
- **Complexity**: Submodule management is notoriously difficult
- **Atomic changes broken**: Can't commit MAD + library change in one commit
- **Versioning overhead**: 10 libraries = 10 repos to tag/release
- **Cellular monolith violated**: System designed to deploy cohesively, not as independent components

### Alternative D: Private Package Repository

**Approach:**
- Run Artifactory/Nexus/devpi
- Publish joshua libraries to private PyPI mirror

**Rejected because:**
- **Infrastructure overhead**: Another service to maintain
- **Solves wrong problem**: Private PyPI useful for external dependencies, not internal monorepo
- **Same issues as public PyPI**: Publishing workflow, versioning complexity

## Consequences

### Positive

✅ **Simple development workflow**: Edit library code/flows, changes instant via hot-mount

✅ **Immutable production builds**: Containers bake in exact library versions

✅ **Dependency encapsulation**: Libraries own their dependencies, MADs stay clean

✅ **Atomic changes**: Single commit can update library + all MADs using it

✅ **No external dependencies**: Self-contained, no PyPI/network needed for builds

✅ **Coordinated versioning**: All libraries tested together, no compatibility matrix

✅ **Standard tooling**: Uses pip/setuptools, familiar to all Python developers

✅ **Future-proof**: Structure supports PyPI later if external distribution becomes needed

### Negative

❌ **Container build context size**: `COPY lib/` copies all libraries even if MAD uses only one
   - **Mitigation**: Multi-stage builds can copy only needed libraries
   - **Reality**: Library code is small (mostly flows/config), negligible impact

❌ **Rebuild on library dependency changes**: Changing `pyproject.toml` dependencies requires container rebuild
   - **Mitigation**: Dependencies stabilize quickly, rare changes after initial development
   - **Reality**: Acceptable tradeoff for dependency encapsulation benefits

❌ **No version isolation**: All MADs must use compatible library versions
   - **Mitigation**: Intentional - system designed for coordinated evolution
   - **Reality**: Feature, not bug - ensures system coherence

### Risks & Mitigations

**Risk**: Developer accidentally edits library in container instead of host mount
- **Mitigation**: Clear documentation, `.dockerignore` prevents copying over mounts
- **Impact**: Low - changes lost on container restart, developer learns quickly

**Risk**: Library dependency conflicts between MADs
- **Mitigation**: All MADs use same Python version (3.11+), tested together
- **Impact**: Low - conflicts caught in dev, resolved before production

**Risk**: Build cache invalidation on unrelated library changes
- **Mitigation**: Docker layer caching, multi-stage builds
- **Impact**: Low - library changes trigger rebuilds only for MADs using that library

## Implementation Guidelines

### Creating a New Library

1. **Create directory structure:**
```bash
mkdir -p lib/joshua_new_library/joshua_new_library
```

2. **Write pyproject.toml:**
```toml
[project]
name = "joshua-new-library"
version = "0.7.0"
dependencies = ["dependency1", "dependency2"]

[tool.setuptools]
packages = ["joshua_new_library"]
```

3. **Add to MAD Dockerfile:**
```dockerfile
RUN pip install -e /app/lib/joshua_new_library
```

4. **Use in MAD:**
```python
import joshua_new_library
```

### Updating Library Dependencies

1. **Edit pyproject.toml:**
```toml
dependencies = [
    "langflow>=1.6.0",  # Updated version
]
```

2. **Rebuild affected MADs:**
```bash
docker-compose build template
```

3. **Test:**
```bash
docker-compose up template
```

### Hot-Mounting New Library for Development

```yaml
# Add to docker-compose.dev.yml
volumes:
  - ../../lib/joshua_new_library:/app/lib/joshua_new_library
```

## Related ADRs

- **ADR-032**: Fully Flow-Based Architecture (establishes flows as first-class artifacts)
- **ADR-042**: MAD Embedded LangFlow Backend Architecture (how MADs execute flows)
- **ADR-020**: System Evolution Roadmap (defines version progression: V0.7, V0.8, V1.0, V5.0)
- **ADR-027**: Adoption of 12-Factor App Methodology (dependency declaration, config externalization)

## Migration Notes

### Existing Libraries

**joshua-libs** (joshua_network, joshua_logger):
- Already using this pattern ✅
- No changes needed
- Continue current approach

**imperator** (legacy V0.5 Python implementation):
- Will be replaced by `joshua_thought_engine` (flow-based V0.7+)
- Migration: Rewrite as flows in `joshua_thought_engine/pcp/flows/`

**joshua_bus_client** (V1.0 Kafka client):
- Keep current structure
- Will be absorbed into `joshua_communicator` during V1.0 migration

**joshua_ssh**:
- Keep current structure
- Evaluate if should remain separate or merge into utility library

### New Libraries for V0.7

**joshua_thought_engine**:
- Create as new library following this ADR
- Contains PCP flows, prompts, configs
- V0.7: Imperator flows without RAG
- V0.8: Add Henson RAG integration
- V5.0: Full PCP pipeline

**joshua_communicator**:
- Create as new library following this ADR
- MCP protocol adapter
- V0.7: WebSocket/HTTP transport
- V1.0: Add Kafka transport

---

**Status**: Accepted
**Next Steps**:
1. Create `joshua_thought_engine` library structure
2. Create `joshua_communicator` library structure
3. Write requirements documents for each library
4. Update MAD Dockerfile template to follow this pattern
5. Update developer documentation with workflow examples

**Last Updated**: 2025-12-23
