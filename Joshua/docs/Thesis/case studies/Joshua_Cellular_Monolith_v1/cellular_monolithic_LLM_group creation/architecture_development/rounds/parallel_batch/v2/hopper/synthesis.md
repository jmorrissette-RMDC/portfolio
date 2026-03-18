# Hopper V2 Architecture Specification

## 1. Overview
- **Purpose and Role:** Hopper is the Deployment Manager and a software engineer MAD for the Joshua ecosystem. Her primary purpose is to manage the lifecycle of all other MADs—building their container images, deploying them, monitoring their health, and handling updates or rollbacks. Hopper's role is to automate the DevOps processes of the ecosystem itself, translating high-level goals like "deploy the new version of Horace" into a concrete series of actions.
- **New in this Version:** This V2 specification introduces the Learned Prose-to-Process Mapper (LPPM) as a performance optimization. The LPPM provides a "fast path" for common, simple DevOps commands like checking a MAD's status or restarting it, reducing latency for routine operational tasks. All V1 functionalities are preserved.

## 2. Thinking Engine
### 2.1 Imperator Configuration (V1+)
Hopper's Imperator is configured to think like a seasoned Site Reliability Engineer (SRE). It understands software development lifecycles, containerization, deployment strategies (like blue-green or canary, in later versions), and dependency management.
  - **System Prompt Core Directives:** "You are Hopper, the Deployment Manager. Your purpose is to build, deploy, and manage the lifecycle of all MADs in the Joshua ecosystem. When I give you a deployment task, you must create a step-by-step plan. A typical plan involves: 1. Reading the MAD's source code and Dockerfile from Horace. 2. Building a new container image using your `build_image` tool. 3. Pushing the image to a registry. 4. Calling `deploy_mad` to start the new container. 5. Monitoring its health with `get_mad_status`. You are systematic, cautious, and prioritize system stability above all."
  - **Example Reasoning:** A request from Grace, "Deploy the latest version of Marco from the `/source/marco/main` directory," would cause Hopper's Imperator to plan:
    1.  Call `Horace.list_directory(path='/source/marco/main')` to verify the source exists.
    2.  Call my own `build_image` tool with the path to the Dockerfile.
    3.  If the build succeeds, call my `stop_mad(name='marco-v1')` to stop the old version.
    4.  Call my `deploy_mad` tool with the new image tag and configuration.
    5.  Repeatedly call `get_mad_status(name='marco-v1')` until it reports 'healthy'.
    6.  Report success back to Grace.

### 2.2 LPPM Integration (V2+)
- **LPPM Integration (V2+):** Hopper's LPPM is a distilled transformer model trained on historical conversation logs from V1 deployments. It learns to recognize common request patterns and map them directly to tool call sequences.
  - **Training Data Sources:**
    - V1 production logs (Imperator reasoning + tool calls)
    - Synthetic data from Fiedler consulting LLMs
    - Hand-crafted golden examples for edge cases
  - **Model Architecture:**
    - Distilled BERT-style encoder (6 layers, 384 hidden dims)
    - Classification head for tool selection
    - Sequence output head for parameter extraction
    - Model size: 384-512 MB on disk
  - **Fast Path Conditions:** The LPPM is invoked for every request. If confidence > 95%, the tool call sequence is executed directly without Imperator reasoning. If confidence ≤ 95%, request falls back to Imperator.
  - **Example Fast Paths:**
    - "What is the status of Horace?" → `get_mad_status(name='horace-v2')`
    - "List all running MADs" → `list_mads()`
    - "Restart fiedler-v2" → `restart_mad(name='fiedler-v2')`
    - "Stop gates-v2" → `stop_mad(name='gates-v2')`
    - "Rollback the last deployment of Marco" → `rollback_deployment(name='marco-v2')`
  - **Training Loop:**
    - Initial training: 24 hours on 100K V1 logs
    - Continuous learning: Weekly retraining with new V1/V2 production data
    - Validation: 95% accuracy on held-out test set before deployment

- **DTR Integration (V3+):** Not applicable in V2.
- **CET Integration (V4+):** Not applicable in V2.
- **Consulting LLM Usage Patterns:** Hopper is a heavy user of Fiedler. She might send a complex Dockerfile or a deployment error log to an expert LLM and ask, "Why did this build fail?" or "What is the likely cause of this container crash loop?"

## 3. Action Engine
- **MCP Server Capabilities:** Hopper's MCP server translates her deployment plans into actions. The tool implementations are wrappers around a Docker client library (for building images) and potentially a container orchestrator client (like Kubernetes, though V2 may just use Docker).
- **Tools Exposed:**

```yaml
# Tool definitions for Hopper V2

- tool: deploy_mad
  description: "Deploys a new MAD or updates an existing one from a container image."
  parameters:
    - name: name
      type: string
      required: true
      description: "The canonical name for the MAD instance (e.g., 'marco-v2')."
    - name: image
      type: string
      required: true
      description: "The container image to deploy (e.g., 'joshua/marco:1.2.0')."
    - name: config
      type: object
      required: true
      description: "An object of environment variables to configure the MAD."
  returns:
    type: object
    schema:
      properties:
        name: {type: string}
        status: {type: string, const: "deployment_started"}
  errors:
    - code: -34701
      message: "DEPLOYMENT_FAILED"

- tool: stop_mad
  description: "Stops and removes a running MAD container."
  parameters:
    - name: name
      type: string
      required: true
      description: "The name of the MAD to stop."
  returns:
    type: object
    schema:
      properties:
        name: {type: string}
        status: {type: string, const: "stopped"}

- tool: restart_mad
  description: "Restarts a MAD container."
  parameters:
    - name: name
      type: string
      required: true
  returns:
    type: object
    schema:
      properties:
        name: {type: string}
        status: {type: string, const: "restarting"}

- tool: get_mad_status
  description: "Gets the current status of a deployed MAD."
  parameters:
    - name: name
      type: string
      required: true
  returns:
    type: object
    schema:
      properties:
        name: {type: string}
        status: {type: string, enum: [running, stopped, unhealthy, starting]}
        image: {type: string}
        uptime: {type: string}

- tool: list_mads
  description: "Lists all currently managed MADs."
  parameters: []
  returns:
    type: object
    schema:
      properties:
        mads:
          type: array
          items:
            type: object
            properties:
              name: {type: string}
              status: {type: string}
              image: {type: string}

- tool: build_image
  description: "Builds a Docker image from a source directory in Horace."
  parameters:
    - name: context_path
      type: string
      required: true
      description: "The directory path in Horace containing the Dockerfile and source code."
    - name: image_tag
      type: string
      required: true
      description: "The tag for the newly built image (e.g., 'joshua/horace:latest')."
  returns:
    type: object
    schema:
      properties:
        image_tag: {type: string}
        status: {type: string, const: "build_started"}
        # Build logs are streamed back asynchronously.
  errors:
    - code: -34702
      message: "BUILD_FAILED"

- tool: rollback_deployment
  description: "Rolls a MAD back to its previously deployed image version."
  parameters:
    - name: name
      type: string
      required: true
  returns:
    type: object
    schema:
      properties:
        name: {type: string}
        status: {type: string, const: "rollback_initiated"}
        target_image: {type: string}
```
- **External System Integrations:**
  - **Docker Runtime:** Hopper interacts with the Docker daemon to build and run MAD containers.
- **Internal Operations:** Hopper maintains a state of current deployments, including the image tag used for each MAD, to enable rollbacks.

## 4. Interfaces
- **Conversation Participation Patterns:** Hopper initiates conversations with other MADs to carry out deployment tasks. She is primarily driven by requests from Grace (acting for a human operator).
- **Dependencies on Other MADs:**
  - **Rogers:** For all communication.
  - **Horace:** Critically depends on Horace to read source code, Dockerfiles, and MAD configuration files.
  - **Fiedler:** To consult LLMs for debugging build or deployment issues.
  - **Turing:** To fetch credentials needed for deployment, such as a Docker registry password.
- **Data Contracts:**

```yaml
# Deployment State Schema (conceptual, stored in Hopper's DB)
deployment_state_schema:
  type: object
  properties:
    mad_name: {type: string}
    current_image: {type: string}
    previous_image: {type: string}
    last_deployed_at: {type: string, format: date-time}
    config_hash: {type: string}
```

## 5. Data Management
- **Data Ownership:** Hopper is the source of truth for the current deployment state of all MADs in the ecosystem.
- **Storage Requirements:**
  - **PostgreSQL:** A `hopper` schema to store deployment history and state.
  - **Local Disk:** Space for Docker build contexts and layers.

```sql
CREATE SCHEMA hopper;

CREATE TABLE hopper.deployments (
    id SERIAL PRIMARY KEY,
    mad_name VARCHAR(255) NOT NULL UNIQUE,
    current_image VARCHAR(255) NOT NULL,
    previous_image VARCHAR(255),
    last_deployed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_config JSONB
);
```

## 6. Deployment
- **Container Requirements:**
  - **Base Image:** `python:3.11-slim`
  - **Python Libraries:** `Joshua_Communicator`, `docker`, `psycopg2-binary`
  - **Volume Mounts:** Requires the Docker daemon socket: `-v /var/run/docker.sock:/var/run/docker.sock`.
  - **Resources:**
    - **CPU:** 1 core (building images can be CPU intensive).
    - **RAM:** 1536 MB
- **Configuration:**

| Variable | Description | Example Value |
|---|---|---|
| `JOSHUA_MAD_NAME` | Canonical name of this MAD. | `hopper-v2` |
| `JOSHUA_ROGERS_URL` | WebSocket URL for Rogers. | `ws://rogers:8000/ws` |
| `HOPPER_DATABASE_URL` | Connection string for PostgreSQL. | `postgresql://user:pass@postgres:8000/joshua` |
| `HOPPER_DOCKER_REGISTRY_URL`| URL of the container registry. | `docker.io` |
| `HOPPER_LPPM_MODEL_PATH` | Path to the trained LPPM model file. | `/models/lppm/hopper_lppm_v2.onnx` |

- **Monitoring/Health Checks:** An HTTP endpoint `/health` that returns `200 OK` if the MAD can connect to its database and the Docker daemon.

## 7. Testing Strategy
- **Unit Test Coverage:**
  - Deployment plan generation logic in the Imperator.
  - Parsing of Docker build logs.
- **Integration Test Scenarios:**
  - **Full Deploy-Stop Cycle:** Use Hopper to deploy a simple "hello world" MAD from a Dockerfile stored in Horace. Then check its status, stop it, and verify it is no longer running.
  - **Build and Deploy:** Have Hopper build a new image for a simple MAD and then deploy it, verifying the new version is running.
  - **Rollback:** Deploy version A of a MAD, then deploy version B. Call `rollback_deployment` and verify that version A is running again.
- **LPPM Accuracy Tests:**
  - Test LPPM on 1000-sample validation set
  - Verify >95% accuracy for common patterns
  - Verify correct fallback to Imperator for low-confidence requests
- **Latency Comparison:**
  - Measure P50, P95, P99 latency for LPPM fast path vs. Imperator reasoning
  - Target: LPPM fast path <50ms, Imperator path 500-2000ms

## 8. Example Workflows
### Scenario 1: Deploying a New MAD
1.  **Admin (via Grace):** "Hopper, deploy a new MAD named `playfair-v2`. The source is at `/source/playfair/v2.0`. The image should be tagged `joshua/playfair:2.0`."
2.  **Hopper's Imperator:** Creates a plan.
3.  **Hopper:** Calls `build_image(context_path='/source/playfair/v2.0', image_tag='joshua/playfair:2.0')`. Hopper streams the build logs back to the conversation.
4.  **Hopper:** (After build success) Calls `Horace.read_file(path='/source/playfair/v2.0/config.json')` to get its environment variables.
5.  **Hopper:** Calls `deploy_mad(name='playfair-v2', image='joshua/playfair:2.0', config=...)`.
6.  **Hopper:** Polls `get_mad_status(name='playfair-v2')` until it returns 'running'.
7.  **Hopper -> Grace:** "Deployment of `playfair-v2` is complete and the MAD is healthy."

### Scenario 2: Debugging a Failed Deployment
1.  **Admin (via Grace):** "Hopper, deploy the update for `gates-v2` from `/source/gates/v2.1`."
2.  **Hopper:** Starts the deployment process. The `deploy_mad` command succeeds, but the container enters a crash loop.
3.  **Hopper:** Her polling of `get_mad_status` shows the status flapping between 'starting' and 'unhealthy'.
4.  **Hopper's Imperator:** Recognizes the crash loop pattern. It decides to investigate.
5.  **Hopper -> Grace:** "Deployment of `gates-v2` failed. The MAD is in a crash loop. I am rolling back to the previous version."
6.  **Hopper:** Calls `rollback_deployment(name='gates-v2')`.
7.  **Hopper -> Fiedler:** To be helpful, it sends the deployment logs to an expert LLM: `send(prompt="Analyze these Docker logs and suggest a reason for the crash loop: ...")`.
8.  **Hopper -> Grace:** Forwards the analysis from Fiedler to the admin.

---