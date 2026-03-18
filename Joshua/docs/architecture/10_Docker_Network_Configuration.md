# 10. Docker Network Configuration

**Version:** 1.0
**Status:** Active - Phase 1 Foundation
**Last Updated:** 2025-12-18
**Owner:** System Architect
**Document:** `/docs/architecture/10_Docker_Network_Configuration.md`

---

## Overview

This document defines the Docker network topology for the Joshua ecosystem. The network architecture implements environment segregation using isolated Docker bridge networks to separate development, testing, and production MAD deployments.

**Related:**
- Phase 1 Foundation Build Plan - Step 1: Define Docker Networks
- Multi-homed Relay Model (Sam MCP Gateway)
- ADR-025: Environment-Specific Storage and Promotion Model

---

## Network Architecture

### Environment Segregation

Three isolated Docker bridge networks provide environment separation:

| Network Name | Driver | Subnet | Gateway | Purpose |
|--------------|--------|---------|---------|---------|
| `dev_network` | bridge | 172.27.0.0/16 | 172.27.0.1 | Development environment |
| `test_network` | bridge | 172.28.0.0/16 | 172.28.0.1 | Testing environment |
| `prod_network` | bridge | 172.30.0.0/16 | 172.30.0.1 | Production environment |

### Network Properties

**Driver:** Bridge (Docker default for single-host deployments)
**Scope:** Local (single Docker host)
**IPv4 Address Space:** /16 subnet provides 65,534 usable addresses per environment
**Isolation:** Complete network-level separation between environments

---

## Multi-Homed Relay Model

The Sam (MCP Gateway) container implements a multi-homed pattern:

**Sam Connectivity:**
- Connects to `dev_network` (for dev MADs)
- Connects to `test_network` (for test MADs)
- Connects to `prod_network` (for production MADs)
- Maps port to physical host network (e.g., 192.168.1.x) for external client access

**Environment Detection:**
- Sam detects source network of incoming connections
- Maps network to environment label: `dev_network` → "dev", `test_network` → "test", `prod_network` → "prod"
- Routes MCP tool calls based on source environment

**Deprecated:**
- `gateway_network` concept (replaced by multi-homed relay model)

---

## Network Creation Commands

Networks were created using Docker CLI:

```bash
# Create development network
docker network create --driver bridge dev_network

# Create testing network
docker network create --driver bridge test_network

# Create production network
docker network create --driver bridge prod_network
```

---

## Verification

Verify networks exist and configuration:

```bash
# List networks
docker network ls | grep -E "dev_network|test_network|prod_network"

# Inspect network details
docker network inspect dev_network test_network prod_network
```

Expected output:
```
dev_network: 172.27.0.0/16 (Gateway: 172.27.0.1)
test_network: 172.28.0.0/16 (Gateway: 172.28.0.1)
prod_network: 172.30.0.0/16 (Gateway: 172.30.0.1)
```

---

## MAD Network Assignment

MADs are assigned to networks based on their deployment environment:

**Development Environment (`dev_network`):**
- Development versions of all MADs
- Experimental features
- Rapid iteration

**Test Environment (`test_network`):**
- Integration testing
- Deming CI/CD validation
- Pre-production verification

**Production Environment (`prod_network`):**
- Stable, validated MAD versions
- Production workloads
- V0.10 Federation Ready MADs

---

## Docker Compose Integration

Network isolation works in conjunction with storage isolation (see ADR-025). Each environment has its own network AND its own storage.

**Example docker-compose.dev.yml:**
```yaml
services:
  hopper-dev:
    image: hopper:latest
    container_name: hopper-dev
    volumes:
      - /mnt/projects/Joshua:/mnt/projects/Joshua:ro  # Dev: hot-mount code
      - /mnt/irina_storage/dev/files:/mnt/irina_storage/files:rw  # Dev: isolated storage
    networks:
      - dev_network
    environment:
      - ENVIRONMENT=dev

networks:
  dev_network:
    external: true
```

**Example docker-compose.prod.yml:**
```yaml
services:
  hopper-prod:
    image: hopper:v1.2.3  # Prod: immutable tagged image with code baked in
    container_name: hopper-prod
    volumes:
      # Prod: NO code mount (code is in image)
      - /mnt/irina_storage/prod/files:/mnt/irina_storage/files:rw  # Prod: isolated storage
    networks:
      - prod_network
    environment:
      - ENVIRONMENT=prod

networks:
  prod_network:
    external: true
```

**Key Points:**
- Network isolation (dev_network, test_network, prod_network) prevents cross-environment communication
- Storage isolation (/dev/files, /test/files, /prod/files) prevents data corruption
- Only dev hot-mounts code; test/prod use immutable images

---

## Security Considerations

**Network Isolation:**
- MADs in different environments cannot communicate directly
- Only Sam (multi-homed) bridges environments
- Prevents dev code from affecting production

**Subnet Separation:**
- Non-overlapping subnets prevent routing conflicts
- Standard Docker bridge networking security applies

**Future:**
- Consider firewall rules for additional security
- Implement network policies if migrating to Kubernetes

---

## Migration Notes

**From Legacy Networks:**
- Previous implementations used `iccm_network`, `joshua-net`, etc.
- New MAD deployments should use environment-specific networks
- Legacy networks can be deprecated after full migration

**To Overlay Networks (Future):**
- If deploying across multiple Docker hosts in the future
- Initialize Docker Swarm: `docker swarm init`
- Recreate networks with `--driver overlay`
- Current bridge networks sufficient for single-host deployment

---

## Phase 1 Completion

**Step 1: Define Docker Networks - COMPLETE**

✅ Networks created and verified
✅ Configuration documented
✅ Ready for Step 2: Deploy Sam (MCP Gateway)

**Next Step:** Build and deploy Sam to V0.7 standard (multi-homed relay)
