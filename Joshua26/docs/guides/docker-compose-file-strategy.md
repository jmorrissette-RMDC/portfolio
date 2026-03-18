# Docker Compose File Strategy

**Date:** 2026-01-31
**Purpose:** Document the correct usage of docker-compose files in Joshua26

---

## File Hierarchy

### Primary Deployment Files (Production)

**Master Compose:**
- `docker-compose.yml` - Defines ALL deployed services

**Per-Host Overrides:**
- `docker-compose.irina.yml` - Irina (storage leader)
- `docker-compose.m5.yml` - M5 (compute/GPU)
- `docker-compose.hymie.yml` - Hymie (desktop automation)

### Local Development Files (Testing Only)

**pMAD-Specific Compose Files:**
- `mads/[mad-name]/docker-compose.yml` - For local development/testing only

---

## Production Deployment

### Correct Usage

**Always use TWO files when deploying:**

```bash
# On Irina:
docker compose -f docker-compose.yml -f docker-compose.irina.yml up -d

# On M5:
docker compose -f docker-compose.yml -f docker-compose.m5.yml up -d

# On Hymie:
docker compose -f docker-compose.yml -f docker-compose.hymie.yml up -d
```

### Using COMPOSE_FILE Environment Variable (Recommended)

Set this in your shell profile on each host:

```bash
# On Irina (~/.bashrc or ~/.zshrc):
export COMPOSE_FILE=docker-compose.yml:docker-compose.irina.yml

# On M5:
export COMPOSE_FILE=docker-compose.yml:docker-compose.m5.yml

# On Hymie:
export COMPOSE_FILE=docker-compose.yml:docker-compose.hymie.yml
```

Then you can simply run:
```bash
docker compose up -d
```

### ❌ WRONG - Do Not Do This

```bash
# This will try to start ALL services on the current host!
docker compose up -d

# This will ignore host-specific configuration!
docker compose -f docker-compose.yml up -d
```

---

## How Override Files Work

### Profiles Mechanism

The override files use Docker Compose profiles to disable services that shouldn't run on that host:

**Example from docker-compose.irina.yml:**
```yaml
services:
  rogers:
    profiles: ["m5-only"]  # Disables rogers on Irina
```

**Service runs if:**
- It's not listed in the override file (enabled by default)
- It's listed but has no profile (enabled explicitly)

**Service is disabled if:**
- It has a profile that doesn't match the current deployment

### Profile Categories

- `["irina-only"]` - Only runs on Irina
- `["m5-only"]` - Only runs on M5
- `["hymie-only"]` - Only runs on Hymie

---

## Service Distribution

### Irina (Storage Leader)
```
starret, henson, brin, alexandria
```

### M5 (Compute/GPU)
```
rogers, sutherland, malory
```

### Hymie (Desktop Automation)
```
hymie
```

---

## Local Development Files

### Purpose

MAD-specific compose files in `mads/[mad-name]/docker-compose.yml` are for:
- Local development and testing
- Quick iteration without affecting production
- Reference/documentation

### Status Markers

**Deployed MADs (in production):**
```yaml
# DEPRECATED: This file is kept for reference/testing only
# The active production configuration is in /mnt/storage/projects/Joshua26/docker-compose.yml
# All changes should be made to the master docker-compose.yml
```

**In-Design MADs (not yet deployed):**
```yaml
# NOTE: This file is for local development/testing only
# When ready for production, this service must be added to the master docker-compose.yml
# and registry.yml before deployment
```

### ⚠️ Important Rules

1. **Never use MAD-specific compose files for production**
2. **All production changes go in master docker-compose.yml**
3. **Before deploying a new MAD:**
   - Add it to `docker-compose.yml`
   - Add it to `registry.yml`
   - Add appropriate profile disables to override files
4. **After deployment:**
   - Mark the MAD's local compose file as deprecated

---

## Adding a New Service

### Checklist

1. ✅ **Create the MAD code** in `mads/[mad-name]/`
2. ✅ **Create local compose file** for development (`mads/[mad-name]/docker-compose.yml`)
3. ✅ **Test locally** using the local compose file
4. ✅ **Add to registry.yml** with UID, GID, port, host assignment
5. ✅ **Add to docker-compose.yml** master file
6. ✅ **Update override files**:
   - Add profile disables to hosts where it shouldn't run
   - Update comment listing services that run on each host
7. ✅ **Deploy** using the two-file pattern
8. ✅ **Mark local compose as deprecated**

---

## Troubleshooting

### Problem: Service running on wrong host

**Cause:** Override file not used, or profiles not set correctly

**Fix:**
1. Check override file has correct profile for that service
2. Ensure you're using `-f docker-compose.yml -f docker-compose.[host].yml`
3. Stop the service on the wrong host
4. Redeploy on correct host with both files

### Problem: Service not starting

**Cause:** Profile might be disabling it incorrectly

**Fix:**
1. Check override file - service might have wrong profile
2. Verify service is supposed to run on that host
3. Check registry.yml for correct host assignment

### Problem: Changes not taking effect

**Cause:** Using MAD-specific compose file instead of master

**Fix:**
1. Make changes in master `docker-compose.yml`
2. Redeploy using two-file pattern
3. Mark MAD-specific file as deprecated

---

## Best Practices

1. **Always use COMPOSE_FILE environment variable** on production hosts
2. **Keep registry.yml and docker-compose.yml in sync**
3. **Never commit secrets** to compose files (use env_file or /storage/credentials/)
4. **Test locally first** using MAD-specific compose files
5. **Document exceptions** (like hymie's special device/permission requirements)
6. **Review override files** when adding new services to avoid conflicts

---

## Files to Keep in Sync

When adding/removing/changing services, update ALL of these:

1. `registry.yml` - Service definition with UID/GID/port/host
2. `docker-compose.yml` - Service container definition
3. `docker-compose.irina.yml` - Profile disables for Irina
4. `docker-compose.m5.yml` - Profile disables for M5
5. `docker-compose.hymie.yml` - Profile disables for Hymie
6. `docs/audits/MAD-inventory-audit-FINAL-2026-01-31.md` - Update inventory

---

## Related Documents

- [MAD Inventory Audit](../audits/MAD-inventory-audit-FINAL-2026-01-31.md)
- [Remote Docker Access via SSH](./remote-docker-access-via-ssh.md)
- [ADR-045 MAD Template Standard](../ADRs/ADR-045-mad-template-standard.md)
