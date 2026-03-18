# Deployment and Containerization Architecture

**Version**: 1.0 (Unified)
**Status:** Authoritative

---

## 1. Overview

The Joshua ecosystem is designed for containerized deployment using Docker. Each Multipurpose Agentic Duo (MAD) is packaged as a separate Docker image and runs in its own container, providing process isolation, simplified dependency management, and independent updates. This document defines the standards for containerization, networking, and deployment orchestration across both V0 (Direct Communication) and V1+ (Conversation Bus) architectural phases.

## 2. Containerization Standards

### 2.1. One MAD Per Container

Each MAD is packaged as a Docker container, ensuring a clear boundary of responsibility and resource allocation. This allows for independent lifecycle management and updates for each component.

### 2.2. Standard Mount Policy

> **⚠️ DEPRECATED:** This section describes the legacy single-environment mount policy. For multi-environment deployments (dev/test/prod), see **ADR-025: Environment-Specific Storage and Promotion Model** which supersedes this section.

**Legacy Policy (Single Environment Only):**

Every MAD container in a single-environment deployment adheres to a standard two-mount policy for code and data:

1.  **Code Mount (Read-Only):** A read-only bind mount of the entire `Joshua` project directory (`/mnt/projects/Joshua`).
    ```yaml
    volumes:
      - /mnt/projects/Joshua:/mnt/projects/Joshua:ro
    ```
    *   **Purpose:** Enables "hot-mounting" of source code for rapid development (live code updates without container rebuilds) and provides shared access to common libraries (e.g., `Joshua_Communicator`) located in `/lib`.

2.  **Data Mount (Read-Write):** A read-write bind mount for all runtime data (`/mnt/irina_storage/files`).
    ```yaml
    volumes:
      - /mnt/irina_storage/files:/mnt/irina_storage/files:rw
    ```
    *   **Purpose:** Provides a shared, persistent file system for all MADs, managed by `Horace` (V1+). This is typically NFS-backed for multi-host access.

**For Multi-Environment Deployments:**

See **ADR-025** for the environment-specific storage architecture where:
- Dev environment hot-mounts code and uses `/mnt/irina_storage/dev/files`
- Test/Prod environments have code copied into images and use `/mnt/irina_storage/test/files` or `/mnt/irina_storage/prod/files`

### 2.3. Dockerfile Pattern for Hot-Mounting

> **⚠️ NOTE:** This pattern applies to **development environments only**. For test/prod environments, see ADR-025 which specifies code should be COPIED into images for immutability.

`Dockerfile`s for development MADs should be optimized for hot-mounted code. This means they should **not** `COPY` the MAD's source code into the image (except for dependency files like `requirements.txt`). Instead, they should install dependencies and set the `PYTHONPATH` to use the code from the read-only mount.

**Example Python Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install MAD-specific dependencies
COPY mads/<mad-name>/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt && \
    rm /tmp/requirements.txt

# Set PYTHONPATH to include shared libs and MAD code from the mount
ENV PYTHONPATH=/mnt/projects/Joshua/lib:/mnt/projects/Joshua/mads/<mad-name>

# Expose the standard internal port for the MCP server
EXPOSE 8000

# Run the application (using hot-mounted code)
CMD ["python", "-u", "-m", "<mad-name>.server_joshua"]
```

## 3. Networking Architecture

The networking model evolves from a simple bridge network for V0 single-host deployment to a more robust internal network for V1+ multi-host deployments. A consistent internal port standard is maintained across all versions.

### 3.1. Standard Internal Port

**All MAD MCP servers MUST listen on the standard internal port `8000`**. This simplifies MAD configuration, prevents port conflicts within the Docker network, and promotes a consistent architecture.

### 3.2. V0 Networking: Docker Bridge Network

In V0, MADs operate on a single **Docker Bridge Network** (e.g., `iccm_network`).

*   **Internal Communication:** All MADs are attached to this network and communicate using their Docker service name and the standard internal port (e.g., `ws://fiedler:8000`). Docker's built-in DNS handles service discovery.
*   **External Access:** Only the **`Sam` (MCP Gateway)** (e.g., `sam-gateway`) will have a port mapped to the host machine for external programmatic access. `Grace` will also have a port mapped for its web UI.

```mermaid
graph TD
    subgraph "Docker Host (Pharaoh - 192.168.1.200)"
        subgraph "Docker Bridge Network (iccm_network)"
            Sam_Gateway[sam-gateway<br/>(`Sam` MCP Gateway:8000)]
            Fiedler[fiedler-mcp:8000]
            Horace[horace-mcp:8000]
            Marco[marco-mcp:8000]

            Sam_Gateway -.->|"ws://fiedler:8000"| Fiedler
            Sam_Gateway -.->|"ws://horace:8000"| Horace
            Fiedler -.->|"ws://horace:8000"| Horace
        end
        ExternalClient[External Client<br/>(e.g., Claude Code)] -- "Connects to Host Port 9000" --> Sam_Gateway
    end
```

### 3.3. V1+ Networking: Docker Overlay Networks (Conversation Bus)

In V1+, MADs typically deploy on **Docker Swarm Overlay Networks** (e.g., `joshua-net`), facilitating multi-host deployments and integrating with the `Rogers` Conversation Bus.

*   **Internal Communication:** All V1+ MADs are attached to the `joshua-net` overlay network. They communicate via the `Rogers` Conversation Bus, which itself listens on `8000` internally (e.g., `ws://rogers:8000`).
*   **External Access:** Only the **`Sam` MAD** (as the V1+ MCP Gateway) will map a single port to the host for external programmatic access (e.g., `9001:8000`). `Grace` will continue to map a port for its web UI.

```mermaid
graph TD
    subgraph "Docker Host (e.g., Irina - 192.168.1.210)"
        HostPort9001[Host Port 9001] -- "Maps to" --> Sam_Container[sam:8000]
        
        subgraph "Docker Overlay Network (joshua-net)"
            Sam_Container -- "ws://rogers:8000" --> Rogers_Container[rogers:8000]
            Fiedler_Container[fiedler:8000] -- "ws://rogers:8000" --> Rogers_Container
            Horace_Container[horace:8000] -- "ws://rogers:8000" --> Rogers_Container
            # ... Other MADs ...
        end
    end
    ExternalClient[External Client] -- "Connects to Host Port 9001" --> HostPort9001
```

## 4. Deployment Orchestration

### 4.1. Docker Compose for V0/V1

For V0 and V1.0 phases, deployment is managed via a single **`docker-compose.yml`** file. This provides a simple, declarative way to define and run the entire multi-container application on a single host.

*   **Service Definition:** Each MAD has a service entry, specifying its Dockerfile context, image, container name, and network attachment.
*   **Port Mapping:** Only specific entry-point services (`Gates` in V0, `Sam` and `Grace` in V1+) will have their ports mapped to the host machine for external access.
*   **Volumes:** Named volumes are used for persistent data stores (`codd_data`, `babbage_data`, `turing_vault`) and bind mounts for shared file systems (`irina_storage`).

**Example `docker-compose.yml` (V0 or V1 simplified):**
```yaml
version: '3.8'

services:
  my_mad:
    build:
      context: ../../
      dockerfile: mads/my_mad/Dockerfile
    image: my_mad:latest
    container_name: my_mad
    restart: unless-stopped
    volumes:
      - /mnt/projects/Joshua:/mnt/projects/Joshua:ro
      - /mnt/irina_storage/files:/mnt/irina_storage/files:rw
    environment:
      - PYTHONDONTWRITEBYTECODE=1
      - PYTHONUNBUFFERED=1
      - MAD_PORT=8000 # Standard internal port
      # ... other MAD-specific variables
    # Only expose ports for entry-point services like Sam/Relay or Grace
    # ports: 
    #   - "9001:8000" # Example for Sam/Relay
    networks:
      - joshua-net
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 5s

networks:
  joshua-net:
    external: true # Or define as internal for single-host
```

### 4.2. Development vs. Production Strategies

*   **Development:** Relies on **hot-mounted code** (read-only bind mounts) for live code updates without container rebuilds.
*   **Production (Future):** Will transition to **copying code at build time** into self-contained images for greater immutability and portability.

### 4.3. SSH Backdoor Architecture

Every MAD container **must** provide an SSH backdoor for operational debugging and emergency access. This is a critical debugging tool when the main communication channels are unavailable.

*   **Requirement:** Each MAD Dockerfile installs an SSH server, configured for key-based authentication (no passwords).
*   **Port Mapping:** SSH ports are mapped uniquely to the host for each MAD (e.g., `2201:22` for `Rogers`).
*   **Auditing:** SSH access attempts are logged locally and, when the bus is operational, broadcast as audit events for `McNamara`.

## 5. Constraints and Limitations

### V0 Specific Limitations

-   **Single Host Deployment:** The bridge network limits V0 to single Docker host deployments.
-   **Manual Service Discovery:** Peer MAD URLs must be manually configured via environment variables (e.g., `FIEDLER_URL=ws://fiedler:8000`).

### V1+ Specific Limitations

-   **Single Host Deployment (V1.0):** While using overlay networks, early V1.0 still largely relies on Docker Compose for single-host orchestration.
-   **No Automated Health Checks/Recovery:** V1.0 relies on Docker Compose's basic `restart` policies. Advanced automated health checks, restarts on failure, or rolling updates are out of scope.
-   **Configuration Management:** Secrets and critical configuration are passed via environment variables, which is not ideal for production security.

## 6. Future Considerations

*   **Kubernetes Deployment:** Future versions will likely leverage Kubernetes for multi-host orchestration, enabling high availability, automated scaling, and advanced operational features.
*   **Service Mesh:** A service mesh (e.g., Istio) could provide deeper control over traffic management, security policies, and observability within the Docker network.
*   **Secrets Management Integration:** Integration with dedicated secrets management tools (e.g., HashiCorp Vault) will enhance security beyond environment variables.