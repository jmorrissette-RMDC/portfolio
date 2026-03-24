# TEST PLAN: Alexandria

**MAD Group:** alexandria
**Version:** 1.0
**Date:** 2026-03-08
**Host:** irina (192.168.1.110)
**Status:** Draft — awaiting execution

---

## 1. Environment Setup

- [ ] All 5 Alexandria containers are `(healthy)`:
  ```bash
  docker ps --filter "label=mad.logical_actor=alexandria" --format "table {{.Names}}\t{{.Status}}"
  ```
- [ ] PyPI proxy accessible: `curl -s http://192.168.1.110:3141/root/pypi/+simple/ | head -3`
- [ ] NPM proxy accessible: `curl -s http://192.168.1.110:4873/-/ping`
- [ ] Docker registry accessible: `curl -s http://192.168.1.110:5000/v2/`
- [ ] MCP health: `curl -s http://[alexandria-langgraph]:8000/health` from within alexandria-net

---

## 2. Core Proxy Function Tests (90% of the plan)

These tests prove Alexandria does what it exists to do: transparently cache external
dependencies so builds are fast and offline-capable. Every test follows the same pattern:

1. **Cold** — request something not yet in cache; verify Alexandria fetches it from the
   upstream registry over HTTPS
2. **Warm** — request the same thing again; verify it is served from local cache with
   no internet round-trip
3. **Offline** — block the upstream / confirm internet not needed for cached items

---

### 2.1 PyPI Proxy (Devpi → https://pypi.org)

**Purpose:** Verify `pip install` transparently caches Python packages.

#### TC-PYPI-01: Cold cache miss — simple package

- **Pre-condition:** `requests` package not in devpi cache (or use a package that
  definitely isn't, e.g., `cowsay==6.1`)
- **Action:**
  ```bash
  docker run --rm python:3.12-slim pip install \
    --index-url http://192.168.1.110:3141/root/pypi/+simple/ \
    --trusted-host 192.168.1.110 \
    cowsay==6.1 -v 2>&1 | grep -E "Downloading|Looking"
  ```
- **Expected:** `Downloading http://192.168.1.110:3141/...cowsay...` — served via
  Alexandria (which fetched it from PyPI over HTTPS in the background)
- **Verify cache populated:**
  ```bash
  curl -s http://192.168.1.110:3141/root/pypi/+simple/cowsay/ | grep href | head -5
  ```
  Expected: package links present

#### TC-PYPI-02: Warm cache hit — same package, no internet

- **Pre-condition:** TC-PYPI-01 completed; cowsay now in cache
- **Action:** Same pip install command as TC-PYPI-01
- **Expected:** `Downloading http://192.168.1.110:3141/...` — served from local cache
- **Verify no upstream fetch:** Check devpi logs — no outbound request to pypi.org
  ```bash
  docker logs alexandria-devpi --since 10s 2>&1 | grep -i "pypi.org\|upstream\|miss"
  ```

#### TC-PYPI-03: Large package (numpy or pandas wheel)

- **Purpose:** Verify large binary wheels (50-200MB) cache correctly
- **Action:**
  ```bash
  docker run --rm python:3.12-slim pip install \
    --index-url http://192.168.1.110:3141/root/pypi/+simple/ \
    --trusted-host 192.168.1.110 \
    numpy==2.2.3 -v 2>&1 | tail -5
  ```
- **Expected:** Successful install; wheel downloaded via Alexandria

#### TC-PYPI-04: Package with dependencies (full dependency tree)

- **Purpose:** Verify devpi caches transitive dependencies, not just the top-level package
- **Action:**
  ```bash
  docker run --rm python:3.12-slim pip install \
    --index-url http://192.168.1.110:3141/root/pypi/+simple/ \
    --trusted-host 192.168.1.110 \
    fastapi==0.115.0 -v 2>&1 | grep "Downloading" | wc -l
  ```
- **Expected:** Multiple packages downloaded (fastapi has ~10 dependencies)
- **Verify all cached:**
  ```bash
  curl -s http://192.168.1.110:3141/root/pypi/+simple/starlette/ | grep -c href
  curl -s http://192.168.1.110:3141/root/pypi/+simple/pydantic/ | grep -c href
  ```

#### TC-PYPI-05: Offline capability — cached packages available without internet

- **Purpose:** The definitive test. Cached packages must be serveable when upstream is unreachable.
- **Pre-condition:** cowsay and numpy cached from TC-PYPI-01 and TC-PYPI-03
- **Action:** Install from cache in a container with no network route to the internet:
  ```bash
  docker run --rm --network joshua26_alexandria-net python:3.12-slim pip install \
    --index-url http://alexandria-devpi:3141/root/pypi/+simple/ \
    --trusted-host alexandria-devpi \
    --no-index \
    cowsay==6.1 -v 2>&1 | tail -5
  ```
  Note: `--no-index` forces pip to only use the specified index (not fall back to PyPI).
  The container is on `alexandria-net`, which has no public internet route.
- **Expected:** `Successfully installed cowsay-6.1` — served entirely from local cache

#### TC-PYPI-06: Concurrent installs

- **Purpose:** Multiple containers installing simultaneously (realistic CI scenario)
- **Action:** Launch 3 parallel pip installs:
  ```bash
  for pkg in httpx==0.28.1 rich==13.9.4 typer==0.15.1; do
    docker run --rm python:3.12-slim pip install \
      --index-url http://192.168.1.110:3141/root/pypi/+simple/ \
      --trusted-host 192.168.1.110 $pkg &
  done
  wait
  echo "All parallel installs complete"
  ```
- **Expected:** All three succeed without errors or corruption

#### TC-PYPI-07: Cache persistence across devpi restart

- **Purpose:** Verify cached packages survive a container restart
- **Pre-condition:** cowsay cached from TC-PYPI-01
- **Action:**
  ```bash
  # Restart devpi
  docker restart alexandria-devpi
  # Wait for healthy
  sleep 30 && docker inspect alexandria-devpi --format '{{.State.Health.Status}}'
  # Verify cache still there
  curl -s http://192.168.1.110:3141/root/pypi/+simple/cowsay/ | grep -c href
  ```
- **Expected:** Health = healthy; cowsay package links still present after restart

---

### 2.2 NPM Proxy (Verdaccio → https://registry.npmjs.org)

**Purpose:** Verify `npm install` transparently caches Node.js packages.

#### TC-NPM-01: Cold cache miss — simple package

- **Pre-condition:** `is-odd` package not in verdaccio cache
- **Action:**
  ```bash
  docker run --rm node:20-slim sh -c \
    'mkdir /tmp/t && cd /tmp/t && npm init -y && \
     npm install --registry http://192.168.1.110:4873 is-odd --verbose 2>&1 | \
     grep -E "GET|http" | head -10'
  ```
- **Expected:** Requests going to `http://192.168.1.110:4873` (not npmjs.org directly)
- **Verify cache populated:**
  ```bash
  ls /mnt/storage/packages/npm/is-odd/ 2>/dev/null || \
    ssh aristotle9@192.168.1.110 "ls /mnt/storage/packages/npm/ | grep is-odd"
  ```

#### TC-NPM-02: Warm cache hit — same package

- **Pre-condition:** TC-NPM-01 completed
- **Action:** Same npm install command
- **Expected:** Install succeeds; faster (served from local cache)

#### TC-NPM-03: Scoped package (@org/package)

- **Purpose:** Scoped packages are what the ecosystem actually uses (MCP SDK, etc.)
- **Action:**
  ```bash
  docker run --rm node:20-slim sh -c \
    'mkdir /tmp/t && cd /tmp/t && npm init -y && \
     npm install --registry http://192.168.1.110:4873 \
     @modelcontextprotocol/sdk --verbose 2>&1 | tail -5'
  ```
- **Expected:** `added N packages` — success; scoped package cached

#### TC-NPM-04: Multiple packages (realistic MAD build)

- **Purpose:** Simulate a real MAD gateway build (Node.js packages the ecosystem uses)
- **Action:**
  ```bash
  docker run --rm node:20-slim sh -c \
    'mkdir /tmp/t && cd /tmp/t && npm init -y && \
     npm install --registry http://192.168.1.110:4873 \
     express ws uuid && npm list --depth=0'
  ```
- **Expected:** All packages installed; transitive dependencies cached

#### TC-NPM-05: Offline capability — cached packages available without internet

- **Pre-condition:** is-odd and express cached from earlier tests
- **Action:**
  ```bash
  docker run --rm --network joshua26_alexandria-net node:20-slim sh -c \
    'mkdir /tmp/t && cd /tmp/t && npm init -y && \
     npm install --registry http://alexandria-verdaccio:4873 \
     --prefer-offline is-odd 2>&1 | tail -3'
  ```
- **Expected:** `added N packages` — no internet required

#### TC-NPM-06: Cache persistence across verdaccio restart

- **Pre-condition:** is-odd cached from TC-NPM-01
- **Action:**
  ```bash
  docker restart alexandria-verdaccio
  sleep 20 && docker inspect alexandria-verdaccio --format '{{.State.Health.Status}}'
  # Verify package still serveable
  docker run --rm node:20-slim sh -c \
    'mkdir /tmp/t && cd /tmp/t && npm init -y && \
     npm install --registry http://192.168.1.110:4873 is-odd 2>&1 | tail -3'
  ```
- **Expected:** Healthy; is-odd installs from cache

---

### 2.3 Docker Registry (Nineveh → irina:5000)

**Purpose:** Verify Docker images can be pushed to and pulled from the local registry.

#### TC-REG-01: Push image to registry

- **Action:**
  ```bash
  ssh aristotle9@192.168.1.110 "
    docker pull alpine:3.21 && \
    docker tag alpine:3.21 irina:5000/test/alpine:3.21 && \
    docker push irina:5000/test/alpine:3.21
  "
  ```
- **Expected:** `Pushed` — image layers uploaded to registry

#### TC-REG-02: Pull image from registry — same host

- **Action:**
  ```bash
  ssh aristotle9@192.168.1.110 "
    docker rmi irina:5000/test/alpine:3.21 && \
    docker pull irina:5000/test/alpine:3.21 && \
    echo 'Pull successful'
  "
  ```
- **Expected:** `Pull complete` — image served from `irina:5000`

#### TC-REG-03: Pull image from registry — different host (cross-host)

- **Purpose:** The real use case — m5 pulls an image that was built on irina
- **Action:**
  ```bash
  ssh aristotle9@192.168.1.120 "
    docker pull irina:5000/test/alpine:3.21 && \
    echo 'Cross-host pull successful'
  "
  ```
- **Expected:** `Pull complete` — image retrieved from local registry, not Docker Hub

#### TC-REG-04: Push real MAD image and pull on another host

- **Purpose:** Simulate actual CI/CD workflow — build image on irina, deploy on m5
- **Action:**
  ```bash
  # Build and push from irina
  ssh aristotle9@192.168.1.110 "
    docker build -t irina:5000/joshua26-alexandria:test \
      -f /mnt/storage/projects/Joshua26/mads/alexandria/alexandria/Dockerfile \
      /mnt/storage/projects/Joshua26 && \
    docker push irina:5000/joshua26-alexandria:test
  "
  # Pull and verify on m5
  ssh aristotle9@192.168.1.120 "
    docker pull irina:5000/joshua26-alexandria:test && \
    docker inspect irina:5000/joshua26-alexandria:test --format '{{.Id}}' | head -c 20
  "
  ```
- **Expected:** Same image ID on both hosts — served from `irina:5000`

#### TC-REG-05: Image persists across registry restart

- **Pre-condition:** test/alpine pushed in TC-REG-01
- **Action:**
  ```bash
  ssh aristotle9@192.168.1.110 "
    docker restart alexandria-registry && \
    sleep 15 && \
    docker inspect alexandria-registry --format '{{.State.Health.Status}}' && \
    docker pull irina:5000/test/alpine:3.21 && \
    echo 'Image survived restart'
  "
  ```
- **Expected:** Healthy; image pulls successfully after restart

#### TC-REG-06: Registry tag listing and deletion

- **Action:**
  ```bash
  # List tags via registry API
  curl -s http://192.168.1.110:5000/v2/test/alpine/tags/list
  # Push a deletable tag
  ssh aristotle9@192.168.1.110 "
    docker tag alpine:3.21 irina:5000/test/alpine:deleteme && \
    docker push irina:5000/test/alpine:deleteme
  "
  # Verify via MCP tool
  # (see Section 3 — alex_registry_delete_tag)
  ```
- **Expected:** Tag appears in listing; deletion via MCP tool succeeds

---

## 3. MCP Management Interface Tests (10% of the plan)

These tests verify the management tools report accurate state — i.e., they reflect
reality established by the core proxy tests above. Run these AFTER Section 2.

All MCP tool invocations use JSON-RPC 2.0 sessionless POST to port 9229 from within
a container on `joshua-net`:

```bash
docker run --rm --network joshua-net curlimages/curl -s -X POST \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"TOOL","arguments":ARGS},"id":"1"}' \
  http://alexandria:9229/mcp
```

---

#### TC-MCP-01: alex_cache_status — reflects real cache state

- **Pre-condition:** Packages warmed by Section 2 tests
- **Arguments:** `{}`
- **Expected:** `pypi.package_count > 0`, `npm.package_count > 0`, `docker.repository_count > 0`
- **State verification:** Counts match what's actually in `/mnt/storage/packages/pypi/` and `/mnt/storage/packages/npm/`

#### TC-MCP-02: alex_warm_pypi — actually warms the cache

- **Arguments:** `{"requirements": "boto3==1.35.0\nsix==1.16.0"}`
- **Expected:** `warmed: ["boto3", "six"]`, `failed: []`
- **State verification:**
  ```bash
  curl -s http://192.168.1.110:3141/root/pypi/+simple/boto3/ | grep -c href
  ```
  Expected: package links present after tool call

#### TC-MCP-03: alex_warm_npm — actually warms the cache

- **Arguments:** `{"package_json": "{\"dependencies\":{\"chalk\":\"5.3.0\"}}"}`
- **Expected:** `warmed: ["chalk"]`, `failed: []`
- **State verification:**
  ```bash
  ssh aristotle9@192.168.1.110 "ls /mnt/storage/packages/npm/ | grep chalk"
  ```

#### TC-MCP-04: alex_list_packages — lists what's actually cached

- **Arguments (pypi):** `{"cache": "pypi", "search": "cowsay"}`
- **Expected:** cowsay appears in results (cached in TC-PYPI-01)
- **Arguments (npm):** `{"cache": "npm", "search": "is-odd"}`
- **Expected:** is-odd appears in results (cached in TC-NPM-01)

#### TC-MCP-05: alex_registry_list_images

- **Arguments:** `{}`
- **Expected:** `repositories` contains `test/alpine` (pushed in TC-REG-01)

#### TC-MCP-06: alex_registry_list_tags

- **Arguments:** `{"image": "test/alpine"}`
- **Expected:** tags list contains `3.21` and `deleteme`

#### TC-MCP-07: alex_registry_delete_tag — deletes non-latest; blocks latest

- **Block latest:**
  - Arguments: `{"image": "test/alpine", "tag": "latest"}`
  - Expected: error `Cannot delete the 'latest' tag`
- **Delete non-latest:**
  - Arguments: `{"image": "test/alpine", "tag": "deleteme"}`
  - Expected: `success: true`
  - **State verification:** `curl -s http://192.168.1.110:5000/v2/test/alpine/tags/list` — `deleteme` no longer present

#### TC-MCP-08: metrics_get — returns valid Prometheus text

- **Arguments:** `{}`
- **Expected:** Response contains `mcp_requests_total` counter with `mad="alexandria"` labels
- **Verify format:** Text is valid Prometheus exposition format

#### TC-MCP-09: alex_imperator_chat — handles a multi-step cache operation

- **Arguments:** `{"message": "What is the current status of all three caches and how many packages are cached in total?"}`
- **Expected:** Coherent response describing pypi, npm, and docker cache status with counts
- **Note:** This invokes the LLM via Sutherland — requires Sutherland to be healthy

---

## 4. Infrastructure Tests

#### TC-INF-01: Health endpoint aggregation

```bash
docker exec alexandria-langgraph python -c "
import urllib.request, json
r = urllib.request.urlopen('http://localhost:8000/health')
data = json.loads(r.read())
print(data)
assert data['status'] == 'healthy'
assert data['devpi'] == 'ok'
assert data['verdaccio'] == 'ok'
assert data['registry'] == 'ok'
print('PASS')
"
```

#### TC-INF-02: Network isolation — backing services not reachable from joshua-net

```bash
# This should FAIL (connection refused) — backing services are on alexandria-net only
docker run --rm --network joshua-net curlimages/curl -s --connect-timeout 3 \
  http://alexandria-devpi:3141/ && echo "FAIL: devpi reachable from joshua-net" \
  || echo "PASS: devpi correctly isolated"
```

#### TC-INF-03: MCP port not host-exposed (9229 not on host)

```bash
ssh aristotle9@192.168.1.110 "curl -s --connect-timeout 2 http://localhost:9229/health \
  && echo FAIL || echo 'PASS: port 9229 not host-exposed'"
```

#### TC-INF-04: Prometheus metrics format valid

```bash
docker exec alexandria-langgraph python -c "
import urllib.request
r = urllib.request.urlopen('http://localhost:8000/metrics')
text = r.read().decode()
assert 'mcp_requests_total' in text
assert 'alexandria' in text
print('PASS:', len(text), 'bytes of metrics')
"
```

#### TC-INF-05: Log format is structured JSON

```bash
ssh aristotle9@192.168.1.110 "docker logs alexandria-langgraph --tail 5 2>&1 | \
  python3 -c 'import sys,json; [json.loads(l) for l in sys.stdin if l.strip()]; print(\"PASS: all log lines are valid JSON\")'"
```

---

## 5. Overall Verification Checklist

- [ ] TC-PYPI-01 through TC-PYPI-07 all pass
- [ ] TC-NPM-01 through TC-NPM-06 all pass
- [ ] TC-REG-01 through TC-REG-06 all pass
- [ ] TC-MCP-01 through TC-MCP-09 all pass
- [ ] TC-INF-01 through TC-INF-05 all pass
- [ ] No unexpected errors in `docker logs` for any container
- [ ] All 5 containers remain `(healthy)` throughout testing
- [ ] Cache data persists at `/mnt/storage/packages/` and `/mnt/storage/images/alexandria-registry/`

---

## 6. Test Results Log

See `mads/alexandria/tests/TEST-RESULTS.md`

---

*Version: 1.0 | Created: 2026-03-08*
