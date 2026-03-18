# Alexandria — Supply Chain Wall

Alexandria is the unified external dependency cache for the Joshua26 ecosystem. It provides transparent caching for PyPI packages, NPM packages, and Docker images, enabling fast offline-capable builds across all MADs.

**Host:** irina (192.168.1.110)
**MCP port:** 9229 (joshua-net)
**Cache proxy ports:** 3141 (PyPI), 4873 (NPM), 5000 (Docker registry) — host-bound

## Container Group

| Container | Image | Role |
|-----------|-------|------|
| `alexandria` | nginx:alpine | Gateway — MCP + cache proxy ingress |
| `alexandria-langgraph` | python:3.12-slim | LangGraph + Imperator + metrics |
| `alexandria-devpi` | python:3.12-slim | Devpi PyPI cache |
| `alexandria-verdaccio` | verdaccio/verdaccio | Verdaccio NPM cache |
| `alexandria-registry` | registry:2 | Docker Registry 2.0 |

## MCP Tools

| Tool | Description |
|------|-------------|
| `alex_cache_status` | Aggregate status for all three caches |
| `alex_warm_pypi` | Pre-warm PyPI cache from requirements.txt |
| `alex_warm_npm` | Pre-warm NPM cache from package.json |
| `alex_list_packages` | List cached packages (pypi or npm) |
| `alex_registry_list_images` | List stored Docker images |
| `alex_registry_list_tags` | List tags for a Docker image |
| `alex_registry_get_image_info` | Get image metadata |
| `alex_registry_delete_tag` | Delete an image tag (not latest) |
| `alex_registry_storage_stats` | Docker registry storage usage |
| `alex_imperator_chat` | Multi-step cache operations via Imperator |
| `metrics_get` | Prometheus metrics |

## Client Configuration

After deployment, configure clients on all hosts:

**Python base images:**
```dockerfile
ENV PIP_INDEX_URL=http://irina:3141/root/pypi/+simple/
ENV PIP_TRUSTED_HOST=irina
```

**Node.js base images:**
```dockerfile
ENV NPM_CONFIG_REGISTRY=http://irina:4873
```

**Docker daemon (`/etc/docker/daemon.json`) on irina, m5, hymie:**
```json
{ "insecure-registries": ["irina:5000"] }
```

**CI/CD image push:**
```bash
docker tag my-image:latest irina:5000/my-image:latest
docker push irina:5000/my-image:latest
```

## First-Time Deployment

1. Run `mads/alexandria/alexandria-devpi/packages/download-packages.sh` on irina
2. Run `mads/alexandria/alexandria-langgraph/packages/download-packages.sh` on irina
3. Commit the downloaded wheels to the repository
4. Create workspace config files on irina:
   ```bash
   mkdir -p /workspace/alexandria/config/verdaccio
   mkdir -p /workspace/alexandria/config/registry
   cp mads/alexandria/config-templates/verdaccio/config.yaml /workspace/alexandria/config/verdaccio/
   cp mads/alexandria/config-templates/registry/config.yml /workspace/alexandria/config/registry/
   ```
5. Deploy: `py -3.12 scripts/deployment/deploy.py alexandria`

## Requirements

- **REQ:** `mads/alexandria/docs/REQ-alexandria.md`
- **Exceptions:** EX-ALEXANDRIA-001 through EX-ALEXANDRIA-007 in `docs/requirements/REQ-000-exception-registry.md`
