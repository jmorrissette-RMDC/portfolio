# ADR-025: Adopt Environment-Specific Storage and Promotion Model

**Status:** Accepted

**Context:**
The current Joshua architecture defines a three-network segregation for `dev`, `test`, and `prod` environments (`10_Docker_Network_Configuration.md`). However, the deployment and containerization standards (`07_Deployment_And_Containerization.md`) specify a single, shared host path for both data (`/mnt/irina_storage/files`) and code (`/mnt/projects/Joshua`) for all MAD containers, regardless of their environment. This creates a direct conflict where network-isolated environments would still share the same underlying file system, leading to data corruption, testing instability, and an insecure promotion path. This ADR resolves this architectural inconsistency.

**Decision:**
We will formally adopt a robust, multi-environment architecture that enforces strict isolation at the storage level and formalizes the code promotion model, aligning with industry best practices for enterprise-grade software development.

1.  **Environment-Specific Storage Architecture:** The single shared storage model is deprecated. We will implement an isolated storage structure for each environment:
    *   `/mnt/irina_storage/dev/`: For development data.
    *   `/mnt/irina_storage/test/`: For testing data.
    *   `/mnt/irina_storage/prod/`: For production data.
    Each environment's MADs will mount only their corresponding storage directory. For example, a `dev` MAD will mount `/mnt/irina_storage/dev/files:/mnt/irina_storage/files:rw`.

2.  **Bidirectional Data Flow Model:**
    *   **Structure/Schema/Code flows UP:** `dev` → `test` → `prod`.
    *   **Data flows DOWN:** A sanitized, representative copy of production data will be periodically replicated to the `test` environment to ensure realistic testing. The `dev` environment will use synthetic or developer-specific data.

3.  **Hybrid Code Deployment and Promotion Model:** The universal "hot-mounting" strategy is deprecated in favor of a hybrid model.
    *   **Development (`dev`):** Will continue to use a read-only "hot-mount" of the project source code (`/mnt/projects/Joshua:/mnt/projects/Joshua:ro`) to enable rapid iteration without container rebuilds.
    *   **Testing & Production (`test`, `prod`):** Will use immutable Docker images where the code is **COPIED** into the image at build time from a specific, version-controlled Git tag or commit. These containers will **not** mount the host's source code directory.

4.  **Environment Variable Pattern for Storage Paths (12-Factor App Compliance):** To ensure code portability across environments without modification, all MAD code must reference storage paths via environment variables rather than hardcoded paths.
    *   **Standard Environment Variable:** `STORAGE_ROOT` - The base path for all MAD file I/O operations.
    *   **Default Value:** `/mnt/irina_storage/files` - The standardized container-internal path.
    *   **Code Pattern:** MADs must use `os.getenv("STORAGE_ROOT", "/mnt/irina_storage/files")` when accessing storage.
    *   **Docker Configuration:** Each environment's Docker Compose file sets `STORAGE_ROOT` via the `environment` section (though the default typically remains unchanged, this allows override for testing or alternative deployments).

    **Rationale:** This pattern follows the [12-Factor App](https://12factor.net/config) methodology where configuration is separated from code. The same MAD code can run across dev/test/prod without modification, with Docker controlling the actual storage location via volume mounts. This also enables local testing with alternative storage paths (e.g., `STORAGE_ROOT=/tmp/test_storage`).

**Consequences:**

*   **Positive:**
    *   **True Environment Isolation:** Prevents `dev` instability from affecting `test` or `prod` data.
    *   **Realistic Testing:** Allows the `test` environment to validate new code and schema changes against production-scale data patterns.
    *   **Immutable Production Artifacts:** Creates secure, reliable, and reproducible production deployments, as the code is baked into the image.
    *   **Architectural Clarity:** Resolves a major inconsistency and aligns the project with standard, robust MLOps and DevOps practices.

*   **Negative:**
    *   **Increased Build Complexity:** Requires a formal image build and tagging process for promoting code to `test` and `prod`, moving beyond simple `docker-compose up`.
    *   **Configuration Management:** Requires more sophisticated Docker Compose files (e.g., using overrides or separate files per environment) to manage the different volume mounts.

**Supersedes:**
This ADR explicitly supersedes the following sections in `07_Deployment_And_Containerization.md`:
*   The "Standard Mount Policy".
*   The "Dockerfile Pattern for Hot-Mounting" (which now only applies to the `dev` environment).

This ADR also provides the necessary context for implementing `10_Docker_Network_Configuration.md`, linking the network isolation to the newly defined storage isolation.

---
## Appendix A: Example Docker Compose Implementation

This illustrates how the new model would be implemented in `docker-compose` files.

**`docker-compose.yml` (Base for all environments):**
```yaml
services:
  hopper:
    # Build details defined here
    image: hopper:latest # Tag will be overridden in test/prod
    networks:
      # Network will be defined in override files
```

**`docker-compose.dev.yml` (Development Override):**
```yaml
services:
  hopper:
    container_name: hopper-dev
    environment:
      - STORAGE_ROOT=/mnt/irina_storage/files  # Standard container path (12-factor config)
    volumes:
      - /mnt/projects/Joshua:/mnt/projects/Joshua:ro # Hot-mount code
      - /mnt/irina_storage/dev/files:/mnt/irina_storage/files:rw # Dev data (host path specific to dev)
    networks:
      - dev_network
networks:
  dev_network:
    external: true
```

**`docker-compose.prod.yml` (Production Override):**
```yaml
services:
  hopper:
    image: hopper:v1.2.3 # Specific, immutable image tag
    container_name: hopper-prod
    environment:
      - STORAGE_ROOT=/mnt/irina_storage/files  # Standard container path (12-factor config)
    volumes:
      # NO code mount
      - /mnt/irina_storage/prod/files:/mnt/irina_storage/files:rw # Prod data (host path specific to prod)
    networks:
      - prod_network
networks:
  prod_network:
    external: true
```

## Appendix B: Code Pattern Example

**Template MAD Tool Implementation:**
```python
# mads/template_mad/template_mad/action_engine/tools.py
import os
from datetime import datetime

async def template_hello_world(message: str) -> dict:
    """Writes a message to a file to verify core functionality."""
    # Use environment variable for storage path (12-factor pattern)
    storage_root = os.getenv("STORAGE_ROOT", "/mnt/irina_storage/files")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = os.path.join(storage_root, f"template_mad_hello_{timestamp}.txt")

    try:
        with open(file_path, "w") as f:
            f.write(f"Hello from template_mad! Your message was: '{message}'")

        return {
            "status": "success",
            "message": f"Wrote to {file_path}"
        }
    except Exception as e:
        raise e
```

**Benefits of this pattern:**
- ✅ Same code works across dev/test/prod environments
- ✅ No code changes needed when promoting between environments
- ✅ Testable with local storage paths (e.g., `STORAGE_ROOT=/tmp/test`)
- ✅ Follows 12-factor app methodology
- ✅ Docker Compose controls actual storage location via volume mounts
