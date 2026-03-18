# HLD: State 3 pMAD — AE/TE Separation

**Version:** 2.0 **Date:** 2026-03-13 **Status:** Active **Related Documents:** HLD-MAD-container-composition.md, mads/kaiser/docs/REQ-kaiser.md, a1-conversationally-cognizant-ai-systems.md

---

## The Problem with State 2

State 2 is the correct architecture for a pMAD's *structure*: nginx gateway, LangGraph StateGraph,
Imperator pattern, observability built in. It solved the fragility of State 1 (custom gateway
code, procedural logic outside the graph) and validated the research premise that agents can
reason about and modify systems expressed as StateGraphs.

But State 2 has a coupling that limits the ecosystem's agility: **the Thought Engine (TE) and
Action Engine (AE) are developed and deployed as a single unit.** The AE — the pMAD's complete
infrastructure (containers, gateway, connection pools, observability) — makes action possible.
The TE — the Imperator and its cognitive apparatus (PCP, inference, conversation-as-state) —
provides intelligence. In State 2 the code for both lives together, so any change to either
requires rebuilding and redeploying the whole. When a StateGraph node changes, the whole container
rebuilds. When a new flow is added, a new image is built and the container restarts. The
development cycle is: change code → rebuild image → push → redeploy → restart. For the AE this
is acceptable — infrastructure is stable. For the TE it is a bottleneck.

The TE changes constantly. The AE almost never does.

---

## The State 3 Pattern

State 3 separates the two concerns completely by making both the AE and the TE dynamically
loadable StateGraph packages.

A State 3 pMAD's container is reduced to an irreducible **bootstrap kernel**: a Python runtime,
a web server, connection pool management, and a single baked-in tool —
`install_stategraph(package_name)`. The kernel discovers installed packages via Python's
`setuptools` entry_points mechanism and knows how to handle them based on what kind of package
they are. This is the one piece that cannot be dynamically loaded — it is the loader.

Everything else — both AE and TE — is published to Alexandria (the internal PyPI cache) as
versioned Python packages and installed into the running container at runtime.

There are two kinds of StateGraph packages, distinguished by their entry_points group:

**AE StateGraph** — infrastructure wiring: how containers connect, how MCP tools are routed to
handlers, message flow in and out of the system, peer proxy configuration, Executor-driven
processes. AE packages register under the pMAD's AE entry_points group. The bootstrap wires
them into the web server's routing table, making their MCP tools available on joshua-net.

**TE StateGraph** — cognitive logic: the Imperator, PCP, inference flows, domain reasoning. TE
packages register under the pMAD's TE entry_points group. The bootstrap makes them available
for internal invocation by the AE when cognitive work is needed. The AE calls into the TE, not
the other way around — the web server routes nothing directly to the TE.

```
Bootstrap kernel (container — irreducible core)
    ├── Python runtime
    ├── web server
    ├── connection pool management
    ├── install_stategraph() tool
    └── entry_points scanner (discovers AE and TE packages)

AE StateGraph (Alexandria package)
    ├── MCP tool handler implementations
    ├── Infrastructure wiring and message routing
    └── Executor-driven processes

TE StateGraph (Alexandria package)
    ├── Imperator and cognitive apparatus
    ├── PCP and inference flows
    └── Domain reasoning logic
```

The AE's containers may also include sidecars — small purpose-built containers that adapt
standard images for use within the pMAD (e.g. wrapping a CLI-only tool with an API, or mounting
Docker access for container management). Sidecars carry whatever privileges or system-level
dependencies their job requires, keeping the kernel generic and unprivileged. The AE StateGraph
knows how to talk to its sidecars; the kernel does not. See HLD-MAD-container-composition for
container composition patterns.

The container ships with nothing but the kernel. What makes it *this particular pMAD* — its
tools, its wiring, its intelligence — all comes from Alexandria packages.

---

## What This Means for the MAD Pattern

The AE/TE separation has a profound consequence for the MAD pattern itself. Once the TE is
portable — a library that can be installed into any compatible AE — it no longer needs to be
bundled with its own infrastructure. An autonomous cognitive actor (a TE with its own Imperator)
that has no infrastructure domain to be concerned about can instead have a subject matter domain
and be hosted on a generic pMAD's AE.

This gives rise to two concrete forms of the MAD:

**pMAD (Persistent MAD)** — owns its own AE and its own TE. Has a system domain: the
infrastructure it manages is part of its concern. Always running. The AE provides the body —
containers, gateway, databases, observability — and the TE provides the intelligence that
operates over that domain.

**eMAD (Ephemeral MAD)** — has no AE of its own. It *is* only a TE, installed as a library into
a host pMAD's AE. Has a subject matter domain: engineering, publishing, analysis — whatever
the eMAD is built for. Between invocations it does not exist. This is what the concept papers
mean by "no body" — not an abstraction but a literal truth.

The Imperator within an eMAD has its own Identity and Purpose — it is a fully autonomous
cognitive agent. Intent emerges at runtime as the Imperator's Purpose meets current
circumstances. The eMAD relies on the host pMAD's AE for all infrastructure capabilities, but
its cognition is its own.

**MAD** remains the umbrella term for the pattern itself — an autonomous actor that is
simultaneously server and client, governed by shared domain intelligence. pMADs and eMADs are
the two forms that pattern takes.

eMADs are maximally portable: the same eMAD library can be installed into any pMAD that
implements the host contract. Different hosts, different infrastructure, same TE — no changes
to the library itself.

---

## The Host Contract

The AE defines a **host contract**: a stable API that TE packages depend on. The contract
specifies what the AE provides — peer proxy base URL, connection pools, logging configuration,
observability hooks. TE packages are written against the contract, not against a specific
container.

This decouples the evolution of the AE from the evolution of the TE. A new container version
that still satisfies the host contract requires no changes to any installed TE packages. A new
TE package that conforms to the contract can be installed into any compatible AE.

The host contract is the interface between AE and TE. Each pMAD that adopts State 3 defines its
own host contract, specific to its domain and the capabilities its AE provides.

---

## Dynamic StateGraph Loading via Alexandria

Both AE and TE packages are standard Python packages, published to Alexandria with semantic
versioning.

Discovery uses Python's `setuptools` entry_points. Each State 3 pMAD defines two entry_points
groups — one for AE packages and one for TE packages. The bootstrap kernel scans both groups,
wires AE packages into the routing table, and makes TE packages available for internal
invocation. No code changes to the kernel are required when new packages are installed.

```toml
# Example: AE package entry_points
[project.entry-points."kaiser.ae"]
core_tools = "kaiser_ae.register:build_graph"

# Example: TE package entry_points
[project.entry-points."kaiser.te"]
hopper = "hopper_emad.register:build_graph"
```

The entry_points group tells the bootstrap what kind of package it is — AE or TE — and the
bootstrap handles each appropriately.

**Adding new capability to a running pMAD:**
1. Develop the StateGraph package locally (AE or TE)
2. Publish to Alexandria
3. Call `install_stategraph("[package-name]")`
4. The bootstrap rescans entry_points — new capability is live

No container rebuild. No restart. No downtime. In-flight requests complete on the old handlers;
new requests get the new ones. Python's reference counting handles the transition.

**Expanding a pMAD's infrastructure:** When a new container is added to a pMAD (e.g. a new
database, a media processing service), the AE StateGraph package is updated to wire in the new
container and expose any new MCP tools. Publish the updated AE package, call
`install_stategraph`, and the pMAD's AE now includes the new capability. If the TE needs to
use the new tools, its package is updated and installed the same way. Both evolve independently
without touching the container kernel.

---

## The CI/CD Split

State 3 produces independent delivery tracks for each concern:

| Track | Trigger | Cadence | Downtime |
|---|---|---|---|
| **Kernel (container)** | Python runtime upgrade, web framework change, bootstrap fix | Very rare | Brief restart |
| **AE (package)** | New MCP tool, infrastructure wiring change, new container integration | Varies by domain | Zero |
| **TE (package)** | Imperator logic, PCP change, domain reasoning update | Frequent | Zero |

The TE track is as fast as any Python development workflow — teams (or agents) can iterate on
intelligence at full speed without any infrastructure ceremony.

The AE track depends on the pMAD's domain. Core infrastructure pMADs — the context broker, the
inference broker, observability — reach AE stability quickly. Their containers are largely
prebuilt images (postgres, redis, nginx) wired together via LangGraph; custom container builds
are rare, reserved for capabilities where no standard image exists. For these pMADs the AE track
approaches zero. But capability-oriented pMADs — media generation, desktop automation, and
other domains where new tools continually emerge — will actively grow their AEs by adding new
containers as new capabilities become available. The AE is not universally stable; it depends
on how settled the pMAD's domain is.

The kernel track approaches zero almost immediately — the bootstrap kernel is minimal and
generic.

In all cases, each track evolves independently. That is the core value of the separation.

---

## Implementation Example: Kaiser and Hopper

The first State 3 implementation in Joshua26 is **Kaiser**, a pMAD purpose-built for hosting
eMADs. Kaiser is an oddity in the ecosystem: it has its own TE and Imperator with a system
domain (eMAD hosting infrastructure), but also hosts eMADs that each bring their own TE and
named Imperator with their own subject matter domains. Many TEs run within Kaiser's pMAD,
all supported by Kaiser's AE — Kaiser's own TE plus every hosted eMAD's. No other pMAD will
exhibit this pattern unless another eMAD host is built; Kaiser's express purpose is eMAD
hosting.

Kaiser's AE provides:
- `/v1/chat/completions` — OpenAI-compatible endpoint for conversational eMAD dispatch.
  The `model` field identifies the eMAD by name. Supports streaming, multimodal content,
  and the ecosystem `conversation_id` extension for Rogers session continuity
  (see HLD-conversational-core §5.2, §5.5).
- MCP management tools: `kaiser_list_emads()`, `kaiser_install_emad(package_name)`,
  `kaiser_create_emad()`, `kaiser_update_emad()`, `kaiser_delete_emad()`,
  `kaiser_imperator_chat()`, `metrics_get()`
- Peer proxy to other MADs in the ecosystem — shared by all installed eMADs
- Asyncio concurrent execution — multiple eMAD StateGraphs run concurrently in one process

The following example shows how an eMAD registers its TE against Kaiser's entry_points group:

```toml
# pyproject.toml of an eMAD TE package
[project.entry-points."kaiser.te"]
hopper = "hopper_emad.register:build_graph"
```

In this example, `hopper` is an engineering eMAD (the Engineering Department). When Kaiser's
bootstrap scans entry_points, it discovers `hopper` as a TE package and makes it available via
the `/v1/chat/completions` endpoint. The eMAD's TE package (`hopper-emad`) provides the complete SDLC StateGraph —
Imperator, agents, orchestrators, Quorum engines — requiring no infrastructure beyond what
Kaiser's AE provides.

**Why no queue for the initial implementation:** eMAD StateGraphs are almost entirely I/O bound.
All inference is delegated to Sutherland; all state to Rogers. Python's asyncio event loop
handles concurrent invocations natively. A Redis-backed worker pool becomes appropriate only
when workers need to be distributed across multiple physical hosts — a scaling ceiling not yet
reached.

---

## Scaling

Because eMADs are libraries, scaling a host pMAD horizontally means running multiple instances
(on different hosts) with the same eMAD libraries installed. The instances share no state — all
conversation state lives in Rogers, all model state in Sutherland. Any instance can handle any
eMAD invocation.

Adding a new pMAD to the ecosystem does not require restarting existing pMADs. Existing pMADs
discover new peers via the peer proxy when they first need them. The ecosystem is additive —
new capability appears without disrupting running services.

---

## The General Case: All MADs Become State 3

Kaiser demonstrates the pattern for eMAD hosting, but the same principle applies to every MAD.
Rogers' context assembly logic, Sutherland's alias routing, Henson's conversation management —
all of these are StateGraphs that currently require container rebuilds whenever they change.

As MADs adopt State 3, their containers reduce to the bootstrap kernel. Their AE and TE
StateGraphs move to Alexandria packages. At that point, every pMAD in the ecosystem is
dynamically composable — its identity, tools, wiring, and intelligence all delivered as packages,
with the container itself interchangeable.

The endpoint of this trajectory: **the kernel is infrastructure, everything else travels via
Alexandria.** Adding new capability to the ecosystem means publishing a package, not rebuilding
a container. The Metacognitive Architect commissions new eMADs, builds libraries, publishes them
to Alexandria, installs them into a host, and wires them into Henson — entirely via MCP tool
calls, with no human touching a container.

---

## Prior Art

This pattern is well-established in software infrastructure:

- **OSGi / Apache Karaf** — Java standard for hot-deploying bundles into a running JVM. Used in
  Eclipse IDE, WildFly application server. The direct enterprise Java equivalent.
- **Stevedore (OpenStack)** — Python library built on `setuptools` entry_points for exactly this
  pattern. OpenStack runs at production scale on dynamic plugin loading. The technical mechanism
  Joshua26 uses is identical.
- **Kafka Connect** — Connectors installed as plugins into a running Connect cluster without
  restart. Same pattern for data infrastructure.
- **Envoy xDS API** — Envoy proxy reconfigures routes, clusters, listeners dynamically via control
  plane API. No restarts. The infrastructure equivalent of what State 3 does for StateGraphs.
- **Erlang/OTP hot code loading** — The gold standard. Erlang replaces running module code without
  stopping the system. WhatsApp and telecom switches run on this principle.

State 3 is the application of the microkernel / plugin architecture to LangGraph MADs. The
technical mechanism (Python entry_points, `importlib`, Alexandria as registry) is the Stevedore
pattern applied to a LangGraph ecosystem.

---

## Summary

| | State 2 | State 3 |
|---|---|---|
| **Container** | AE + TE in one image | Bootstrap kernel only |
| **AE** | In container image | In Alexandria package |
| **TE** | In container image | In Alexandria package |
| **AE or TE change** | Rebuild + restart | Publish + `install_stategraph()` |
| **New capability** | New container or image rebuild | Package publish + install |
| **Downtime on update** | Brief restart | Zero |
| **Development cadence** | Container cycle | Normal Python |
| **Scaling** | Container replicas | Package replicas (same library, multiple hosts) |
| **First implementation** | All current pMADs | Kaiser |
