**Reviewer:** Codex
**Gate:** 1
**MAD:** alexandria
**Date:** 2026-03-03

- **Gate 1: FAILED** — Core architecture/registry alignment issues with REQ-000 must be resolved before implementation.
- **Blockers:**
  1) **Registry allocations missing for Alexandria components.** REQ-018/019/022 specify UIDs (2017, 2018, 2024) and ports, but there are no `registry.yml` entries for alexandria/delphi/pergamum/nineveh. This violates REQ-000 §2.2 (service account creation), §6.3 (registry entry), and §7.6 (host affinity). Add explicit entries (including host, port, UID/GID, MCP endpoints where applicable).
  2) **Network model conflicts with REQ-000 §7.4.1.** REQ-018/019 declare “Host-Bound Infrastructure” and explicitly avoid `joshua-net`, but REQ-000 requires each MAD gateway to attach to `joshua-net` and a private `[mad]-net`, with internal containers on `[mad]-net` only. If Alexandria components are exempt, the exemption must be formally documented in REQ-000-exception-registry before implementation. Otherwise, redesign to comply with the gateway/private-net pattern.
  3) **Nineveh uses Swarm placement constraints in compose.** REQ-022 shows `deploy.placement.constraints` in the compose snippet. REQ-000 §7.6 requires host affinity via per-host override profiles (not Swarm constraints). Update the design to align with the override/profile strategy.
  4) **Nineveh identity is non-compliant.** REQ-022 specifies GID 2000 (joshua-services) but REQ-000 §2.3 mandates GID 2001 (administrators) for all services. Update the REQ to GID 2001.
  5) **MCP tool exposure is undefined/contradictory.** REQ-018/019 define MCP tools using `mad-core-py` and SAM registration, but the architecture only shows a host-bound Devpi/Verdaccio container with no MCP gateway container, no MCP port, and no networking plan for MCP access. The design must define the gateway container, ports, and networks (or explicitly remove MCP tools and justify). This is a requirements conflict with REQ-000 §4 (MCP transport) and §6.5 (tool documentation).

- **Observations:**
  1) **Credential path conventions conflict with REQ-000.** REQ-018/019/022 use `/storage/credentials/api-keys/...` while REQ-000 §3.5 expects `/storage/credentials/<service>/<credential-file>`. Align the path pattern or document the deviation explicitly.
  2) **Offline build strategy for Devpi/Verdaccio images is underspecified.** The base image options use `pip install` / `npm install -g` without detailing cached package usage per REQ-000 §1.1/1.2/1.3. The design should specify how these images build offline (local cache location, Dockerfile steps).
  3) **Nineveh port exposure is internally inconsistent.** REQ-022 lists ports as “joshua-net only,” but the compose snippet maps `5000:5000` (host-bound). Clarify intended exposure and ensure it matches the chosen network model.
  4) **Performance targets likely optimistic.** The >500 MB/s LAN transfer targets for package registries and Docker registry may exceed real-world throughput depending on disks and NICs. Consider stating these as aspirational or define measurement methodology.

- **Recommendations:**
  1) **Document the “Host-Bound Infrastructure” pattern explicitly.** If Alexandria components are intentionally outside the standard MAD network model, add a formal exception in REQ-000-exception-registry or update REQ-000 to describe this class of service.
  2) **Define a clear container list per component.** For each of Delphi/Pergamum/Nineveh, explicitly list containers, MCP gateway (if any), ports, and networks. This will reduce implementation ambiguity and align with REQ-000 §6.4.
  3) **Pin base images and dependencies.** Replace `python:3.11-slim` / `node:20-slim` with pinned versions (or digests) and specify exact package versions to satisfy REQ-000 §1.4/1.7.
  4) **Add explicit tool schemas in the REQs.** Tool names are listed but schemas are not; include input/output schemas and error cases to comply with REQ-000 §4.6 and to make implementation unambiguous.
