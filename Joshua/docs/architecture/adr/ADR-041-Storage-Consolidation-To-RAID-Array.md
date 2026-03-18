# ADR-041: Storage Consolidation to RAID Array

**Status:** Accepted
**Date:** 2025-12-22
**Deciders:** System Architect, Infrastructure Team
**Related ADRs:** ADR-025 (Environment-Specific Storage)

## Context

The Joshua infrastructure was using a fragmented storage architecture with data split across multiple locations:

1. **ZFS Pool for irina_storage:**
   - 100GB pool stored as a file (`/mnt/storage/zfs/irina-pool.img`) on ext4
   - 79GB used (78% capacity)
   - No snapshots enabled (defeating primary ZFS benefit)
   - Minimal compression (1.05x ratio with lz4)
   - Double filesystem overhead (ZFS on top of ext4)

2. **Root Disk for projects:**
   - `/mnt/projects` on 914GB root disk (`/dev/sdf2`)
   - 2.5GB used
   - Single disk (no redundancy)

3. **Available RAID Array:**
   - 44TB ext4 RAID (`/dev/md0`) at `/mnt/storage`
   - Only 154GB used (0.3% capacity)
   - Underutilized while critical data was constrained

### Problems Identified

**Storage Constraints:**
- irina_storage limited to 100GB despite 44TB available
- Running out of space for MAD operations
- Projects on single disk without RAID protection

**ZFS Overhead Without Benefits:**
- No snapshots configured (user expectation mismatch)
- Minimal compression gains
- File-on-ext4 implementation adds complexity
- Performance overhead from double filesystem layer

**Data Protection:**
- Gitwatch provides per-file versioning for projects
- ZFS snapshots were never enabled
- Projects on root disk lack hardware redundancy

**User Expectation Mismatch:**
- User expected ZFS to "automatically keep X versions"
- Reality: ZFS requires explicit snapshot configuration
- Snapshots are time-based (whole filesystem), not per-file versioning

## Decision

**Consolidate all storage onto the 44TB RAID array using ext4 with bind mounts.**

### Implementation Strategy

1. **Migrate to ext4 on RAID:**
   - Move all ZFS datasets to `/mnt/storage/irina_storage/` (ext4)
   - Move `/mnt/projects` to `/mnt/storage/projects/` (ext4)
   - Eliminate ZFS pool entirely

2. **Use bind mounts for transparency:**
   - Bind mount `/mnt/storage/irina_storage` → `/mnt/irina_storage`
   - Bind mount `/mnt/storage/projects` → `/mnt/projects`
   - Keep NFS export paths unchanged
   - Zero client-side configuration changes required

3. **Preserve ADR-025 compliance:**
   - Maintain `/mnt/irina_storage/{dev,test,prod}/` structure
   - STORAGE_ROOT environment variable pattern unchanged
   - Resource-Manager pattern (Horace/Codd/Babbage) unaffected

### Migration Process Executed

**Phase 1: Preparation (No Downtime)**
- Created ext4 directory structure on RAID
- Backed up all data to `/mnt/storage/backup/` (15.6GB)
- Documented current state

**Phase 2: Migration (30-60 min downtime)**
- Stopped containers on client (192.168.1.200): horace, qdrant, gitwatch
- Copied ZFS datasets to ext4: files (83GB), metadata, postgres
- Copied other directories: archive (21GB), qemu, dev, test, prod
- Copied projects: 2.5GB
- Unmounted ZFS datasets
- Created bind mounts in `/etc/fstab`
- Mounted bind mounts
- Remounted NFS on client
- Restarted all containers

**Phase 3: Verification**
- All services operational
- NFS mounts show 44TB available (vs 97GB before)
- File access working correctly
- Containers functioning normally

## Consequences

### Positive

**Massive Storage Increase:**
- irina_storage: 100GB → 44TB (440x increase)
- projects: Root disk → RAID (55x increase + redundancy)
- Total: ~82GB used, 42TB available for growth

**Improved Reliability:**
- Projects now on RAID array (hardware redundancy)
- All data on same reliable storage infrastructure
- Gitwatch continues providing version control for projects

**Reduced Complexity:**
- Eliminated ZFS overhead and complexity
- Single filesystem type (ext4) across all storage
- No double filesystem layer
- Simpler backup and management strategy

**Zero Client Impact:**
- Bind mounts kept NFS paths unchanged
- No container configuration changes
- No application code changes
- STORAGE_ROOT environment variable pattern preserved
- ADR-025 multi-environment architecture intact

**Better Performance:**
- Direct ext4 access vs ZFS-on-file-on-ext4
- No compression overhead
- Reduced I/O layers

### Negative

**Loss of ZFS Features:**
- No copy-on-write semantics
- No built-in checksumming
- No snapshot capability (though it was never enabled anyway)

**Mitigation:**
- Gitwatch provides per-file versioning for projects (auto-save branch)
- RAID provides hardware redundancy
- Backups retained for 7 days as safety net
- ZFS pool preserved for 7 days for rollback capability

### Neutral

**Migration Complexity:**
- Required coordinated downtime across server and client
- 30-60 minute service interruption
- But: Clean rollback plan available using preserved ZFS pool

## Implementation Details

### Server Configuration (192.168.1.210)

**Bind Mounts in `/etc/fstab`:**
```
/mnt/storage/irina_storage /mnt/irina_storage none bind 0 0
/mnt/storage/projects /mnt/projects none bind 0 0
```

**Directory Structure:**
```
/mnt/storage/              (44TB RAID array, ext4)
├── irina_storage/
│   ├── files/            (83GB - MAD working files)
│   ├── horace_metadata/  (metadata)
│   ├── postgres/         (database)
│   ├── dev/              (development environment)
│   ├── test/             (test environment)
│   ├── prod/             (production environment)
│   ├── archive/          (21GB - archived data)
│   ├── qdrant/           (vector database)
│   └── qemu/             (virtual machines)
├── projects/
│   ├── Joshua/           (main git repo, gitwatch protected)
│   ├── Blueprint/
│   └── rmdev-pro/
└── backup/               (migration backups, temporary)
    ├── files/
    ├── projects/
    └── qdrant/
```

**NFS Exports (unchanged):**
- `/mnt/irina_storage` → 192.168.1.0/24
- `/mnt/projects` → 192.168.1.0/24

### Client Configuration (192.168.1.200)

**NFS Mounts (unchanged in `/etc/fstab`):**
```
192.168.1.210:/mnt/irina_storage /mnt/irina_storage nfs defaults 0 0
192.168.1.210:/mnt/projects /mnt/projects nfs defaults 0 0
```

**Container Mounts (unchanged):**
- Horace: `/mnt/irina_storage/files`
- Qdrant: `/mnt/irina_storage/qdrant/storage`
- Gitwatch: `/mnt/projects/Joshua`

### Preserved Data Protection

**Gitwatch Auto-Save:**
- Monitors `/mnt/projects/Joshua`
- Auto-commits to `auto-save` branch every 2 seconds
- Provides per-file version history
- Continues functioning unchanged post-migration

**RAID Array:**
- Hardware redundancy for all data
- 44TB capacity for growth
- ext4 filesystem reliability

### Cleanup After 7 Days

```bash
# After verification period (7 days minimum)
sudo zpool destroy irina
sudo rm /mnt/storage/zfs/irina-pool.img
sudo rm -rf /mnt/irina_storage.old
sudo rm -rf /mnt/projects.old
sudo rm -rf /mnt/storage/backup/
```

## Lessons Learned

1. **User Expectations vs Reality:**
   - ZFS snapshots are not automatic - require explicit configuration
   - Time-based snapshots ≠ per-file versioning
   - Important to clarify storage capabilities upfront

2. **Right Tool for the Job:**
   - Gitwatch provides better per-file versioning than ZFS snapshots for code
   - ZFS overhead not justified without using its features
   - Simpler is often better

3. **Bind Mounts for Transparency:**
   - Bind mounts enable storage migration with zero client changes
   - NFS exports can remain stable while backend changes
   - Critical for minimizing disruption

4. **Migration Planning:**
   - Comprehensive backups before major storage changes
   - Clear rollback plan essential
   - Verification checklist prevents oversights

## Related Documentation

- ADR-025: Environment-Specific Storage Architecture
- File_System_Architecture.md: Complete filesystem documentation
- Gitwatch configuration: `/home/aristotle9/gitwatch-docker/`

## References

- Migration execution log: 2025-12-22
- ZFS pool status before migration: 99.5GB total, 78.6GB used
- RAID array: /dev/md0, 44TB ext4
- Downtime: 30-60 minutes
- Containers affected: horace-mcp, qdrant-joshua, gitwatch-joshua
