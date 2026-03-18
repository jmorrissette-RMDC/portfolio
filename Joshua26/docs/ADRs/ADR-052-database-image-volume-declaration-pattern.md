# ADR-052: Storage Pattern for Official Database Images with VOLUME Declarations

**Status:** Accepted
**Date:** 2026-02-19
**Deciders:** System Architect
**Related:** ADR-039 (Two-Volume Mounting Policy), ADR-045 (MAD Template Standard)

## Context

Several official Docker database images declare `VOLUME` paths in their Dockerfiles:

| Image | Declared VOLUMEs |
|-------|-----------------|
| `postgres` | `/var/lib/postgresql/data` |
| `neo4j` | `/data`, `/logs` |
| `redis` | `/data` |

When Docker encounters a `VOLUME` directive in an image, it creates an **anonymous volume** at that path unless the host explicitly provides a mount at that exact location.

Anonymous volumes:
- Are not tracked by the two-volume policy (ADR-039)
- Cannot be referenced by name for backup or inspection
- Accumulate as orphaned volumes over time (one per container recreation)
- Violate REQ-000 §3.1 (two-volume mounting policy)

The standard ADR-039 approach of mounting `workspace:/workspace` and pointing the application at a path inside `/workspace` does NOT suppress anonymous volume creation for `VOLUME`-declared paths — Docker still creates the anonymous volume at the declared path regardless of where the application is configured to store its data.

The only way to suppress anonymous volume creation is to provide an explicit mount (bind mount or named volume) **at the exact declared VOLUME path**.

## Decision

All containers using official images that declare `VOLUME` paths **must** suppress anonymous volume creation by providing an explicit bind mount at each declared VOLUME path, pointing to the appropriate host location.

The host location follows REQ-000 §3.7 (database data in workspace, backups in storage):

```yaml
# postgres
volumes:
  - storage:/storage
  - /mnt/nvme/workspace/[mad]/databases/postgres/data:/var/lib/postgresql/data

# neo4j
volumes:
  - storage:/storage
  - /mnt/nvme/workspace/[mad]/databases/neo4j/data:/data
  - /mnt/nvme/workspace/[mad]/databases/neo4j/logs:/logs

# redis
volumes:
  - storage:/storage
  - /mnt/nvme/workspace/[mad]/databases/redis/data:/data
```

This pattern:
- Suppresses anonymous volume creation (Docker sees an existing mount at each declared VOLUME path)
- Keeps data on the local NVMe SSD (fast I/O for database operations, per ADR-039)
- Makes data paths explicit and inspectable on the host
- Does NOT use the `workspace` named volume for database data directories (the bind mount goes directly to the NVMe path that the workspace volume maps to)

## Consequences

- Containers using this pattern deviate from ADR-039 two-volume policy
- This deviation requires a formal exception registered in REQ-000-exception-registry per REQ-000 §8.1
- Registered exceptions: EX-POSTGRES-001, EX-NEO4J-001, EX-REDIS-001
- The bind mount paths must be created on the host before first deployment
- Post-deploy permissions: `chown -R 999:999 <data-path>` for postgres; image-appropriate ownership for neo4j and redis
- The `_template` postgres container serves as the canonical reference implementation of this pattern
- All new containers using images with declared VOLUMEs must follow this pattern and register a new exception

## Identifying Affected Images

Before deploying any official image as a backing service, verify whether it declares VOLUMEs:

```bash
docker inspect <image> --format='{{.Config.Volumes}}'
```

If the output is non-empty, this ADR applies and a bind mount + exception registration is required.
