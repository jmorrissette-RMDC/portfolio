# ADR-037: Local Package Caching For Docker Builds

Status: Accepted
Date: 2026-01-01
Updated: 2026-01-15
Deciders: System Architect

## Context and Problem Statement

When building Docker containers, the standard approach downloads packages from remote registries (PyPI, npm, etc.) during every rebuild. This creates several problems:

1. Slow Rebuilds: Every docker build re-downloads hundreds of megabytes of packages
2. Network Dependency: Builds fail without internet access or when registries are unreachable
3. Non-Deterministic Builds: Package versions can change between builds
4. Bandwidth Waste: Repeatedly downloading the same large packages wastes bandwidth and time

## Decision

All containerized services in the Joshua ecosystem will adopt a local package caching pattern that stores pre-downloaded packages in the repository for offline, reproducible, fast Docker builds.

### Implementation Pattern

**Python Services:**

1. Directory Structure:
   - packages/ directory for pre-downloaded .whl and .tar.gz files
   - packages/.gitignore to exclude package files from git
   - requirements.txt for Python dependencies
   - Dockerfile that uses local packages

2. Package Download (One-Time Setup):
   ```bash
   pip download -q -r requirements.txt -d packages/
   ```

3. Dockerfile Pattern:
   ```dockerfile
   COPY packages/ /tmp/packages/
   COPY requirements.txt /tmp/requirements.txt
   RUN pip install --find-links=/tmp/packages/ --prefer-binary -r /tmp/requirements.txt
   ```

4. Adding New Dependencies:
   - Add package to requirements.txt
   - Run: `pip download -q <package-name> -d packages/`
   - Rebuild container

**Node.js Services:**

1. Directory Structure:
   - packages/ directory for pre-downloaded .tgz files
   - packages/.gitignore to exclude package files from git
   - package.json for npm dependencies
   - Dockerfile that uses local packages

2. Package Download (One-Time Setup):
   ```bash
   npm pack <package-name> --pack-destination packages/
   # Or for all dependencies:
   npm ci && cp -r node_modules packages/node_modules
   ```

3. Dockerfile Pattern:
   ```dockerfile
   COPY packages/ /tmp/packages/
   COPY package.json package-lock.json /tmp/
   RUN npm ci --cache /tmp/packages/ --prefer-offline
   ```

4. Adding New Dependencies:
   - Add package to package.json
   - Run: `npm pack <package-name> --pack-destination packages/`
   - Rebuild container

### Key Mechanisms

**Python:**
- `pip download`: Downloads wheels without installing them
- `--find-links=/tmp/packages/`: Tells pip to look in local directory first
- `--prefer-binary`: Prefers pre-built wheels over source distributions
- PyPI Fallback: If a package isn't in local cache, pip falls back to PyPI

**Node.js:**
- `npm pack`: Creates .tgz archives of packages
- `--cache /tmp/packages/`: Use local cache directory
- `--prefer-offline`: Use cached packages before fetching from npm
- npm Fallback: If a package isn't in local cache, npm falls back to registry

**System Packages (apt/apk):**

1. Directory Structure:
   - packages/apt/ directory for pre-downloaded .deb files
   - packages/.gitignore to exclude package files from git
   - Dockerfile that uses local packages

2. Package Download (One-Time Setup):
   ```bash
   # Download specific packages
   apt-get download package-name another-package
   mv *.deb packages/apt/

   # Or use a download script (see malory/packages/download-packages.sh)
   ```

3. Dockerfile Pattern:
   ```dockerfile
   COPY mads/<service>/packages/apt/*.deb /tmp/apt-cache/
   RUN apt-get update && \
       (dpkg -i /tmp/apt-cache/*.deb 2>/dev/null || \
        apt-get install -y --no-install-recommends package-name) && \
       rm -rf /var/lib/apt/lists/* /tmp/apt-cache
   ```

**Docker Base Images:**

1. Directory Structure:
   - packages/docker/ directory for saved base images
   - packages/.gitignore to exclude .tar files from git

2. Image Download (One-Time Setup):
   ```bash
   # Pull and save base image
   docker pull node:20.11.0-slim
   docker save node:20.11.0-slim -o packages/docker/node-20.11.0-slim.tar
   ```

3. Build Pattern:
   ```bash
   # Before docker build, load cached image
   docker load -i packages/docker/node-20.11.0-slim.tar
   docker build -f Dockerfile .
   ```

4. Dockerfile (no changes needed):
   ```dockerfile
   FROM node:20.11.0-slim  # Will use locally cached image
   ```

**Runtime Binaries (Playwright, etc.):**

1. Directory Structure:
   - packages/playwright/ directory for browser binaries
   - packages/.gitignore to exclude binaries from git

2. Binary Download (One-Time Setup):
   ```bash
   # Download Playwright browsers
   npx playwright install chromium
   # Copy from cache to packages
   cp -r ~/.cache/ms-playwright packages/playwright/
   ```

3. Dockerfile Pattern:
   ```dockerfile
   # Copy cached browsers
   COPY --chown=$USER_NAME:$USER_GID mads/<service>/packages/playwright/ /home/$USER_NAME/.cache/ms-playwright/

   # Playwright will use cached browsers instead of downloading
   RUN npx playwright install chromium --dry-run || true
   ```

## Consequences

### Positive
- Fast Rebuilds: Seconds instead of minutes
- Offline Capability: No internet needed for rebuilds
- Reproducible Builds: Exact wheel files ensure identical builds
- Bandwidth Savings: Download once, rebuild many times
- Developer Velocity: Faster iteration cycles

### Negative
- Initial Setup Cost: Requires running pip download before first build
- Disk Space: Local packages/ directory can be several gigabytes
- Manual Dependency Updates: Adding dependencies requires explicit pip download step

## Examples

This pattern is currently implemented in:

**Python Packages:**
1. langflow: Langflow control layer with 4.5GB of cached packages

**System Packages (apt):**
1. malory: Playwright dependencies cached in packages/apt/
2. henson: System libraries cached in packages/apt/

**Node.js Packages:**
- (To be implemented in all Node.js MADs including joshua/mcp-wrapper)

**Docker Base Images:**
- (To be implemented - cache commonly used base images)

**Runtime Binaries:**
- (To be implemented for malory - cache Playwright browsers)

## Related Decisions
- ADR-027: 12-Factor App Methodology
- ADR-028: Core Coding Practice Standards
