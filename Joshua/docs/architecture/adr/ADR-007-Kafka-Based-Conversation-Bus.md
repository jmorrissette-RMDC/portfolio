## ℹ️ Status: Amended ℹ️

This decision has been amended and clarified by **[ADR-022: Rogers as Bus Controller and Service Registry](./ADR-022-Rogers-As-Registry.md)**.

*Please read the new ADR for the complete, up-to-date context regarding Rogers' specific role.*

---

# ADR-007 (v2): Adopt a Pure Kafka Architecture for the V1.0 Rogers Bus

**Status:** Superseded by v2, Accepted
**Original ADR Status:** Obsolete

**Context:**
The V1.0 "Great Migration" is a foundational architectural shift for Joshua, moving all MADs from direct V0 MCP calls to a centralized conversation bus. A robust and scalable architecture for this bus is critical. It must serve as both a high-performance, real-time communication fabric and as the system's permanent, immutable "collective memory" to enable long-term learning (Event Sourcing). The original version of this ADR proposed a hybrid Kafka/Redis architecture to solve for durability and speed separately. However, a deeper technical analysis of Kafka's capabilities and the system's actual latency requirements revealed that a simpler, more robust architecture is possible.

**Decision:**
The V1.0 Rogers Conversation Bus will be implemented using a **pure Apache Kafka architecture.** The hybrid Kafka/Redis model is rejected to reduce operational complexity and unify the data model.

1.  **Core Architecture (The "Durable Fast Lane"):**
    *   **Technology:** Apache Kafka will serve as the **single, unified bus** for both real-time messaging and durable logging.
    *   **Mechanism:** Kafka's native use of the operating system's **page cache** will provide the "fast lane" for real-time messaging. Hot data (recently produced or consumed messages) will be served directly from the broker's memory, providing low-millisecond latency competitive with in-memory systems. All data is simultaneously and transparently persisted to disk, providing the "durable log" without needing a separate system.

2.  **Rogers MAD (The "Bus Controller"):**
    *   **Function:** Rogers is the application-layer controller that MADs interact with. Its primary role is to manage the **Kafka topics** that represent conversations and mailboxes.
    *   **Workflow:** When a MAD sends a message, it produces directly to a Kafka topic. Rogers' role is to handle the control plane: creating topics for new conversations (`rogers_create_conversation`) and managing the service registry that maps MAD capabilities to specific Kafka topics.

3.  **CQRS for Memory (`Babbage`):**
    *   The **Command Query Responsibility Segregation (CQRS)** pattern is maintained and clarified. The Kafka log is the "Write Side." The **Babbage MAD** is the primary, durable consumer of the Kafka log, building optimized "Read Models" (e.g., in MongoDB) for efficient historical querying and deep analysis.

**Consequences:**

*   **Positive:**
    *   **Drastic Architectural Simplification:** Reduces the number of complex distributed systems to manage from two to one, significantly lowering operational overhead, potential points of failure, and maintenance burden.
    *   **Sufficient Performance with Less Complexity:** Achieves "fast lane" low-millisecond latency for real-time messaging via Kafka's page cache, which is more than adequate for V1.0's needs where downstream LLM calls are the primary bottleneck. We avoid the complexity of Redis for a negligible performance gain.
    *   **Guaranteed Data Consistency:** Eliminates the possibility of race conditions or data divergence between separate real-time and durable layers. There is a single source of truth: the Kafka log.
    *   **Robustness and Resilience:** Leverages Kafka's mature, battle-tested architecture for both speed and durability. Features like consumer groups and message retention provide excellent temporal decoupling and fault tolerance out-of-the-box.
    *   **True Event Sourcing:** This is the textbook implementation of Event Sourcing, providing a perfect, immutable, and replayable log of all system events for learning and auditing.

*   **Negative:**
    *   **Higher Burden on Kafka Tuning:** The performance of the "fast lane" is dependent on correctly provisioning the Kafka brokers with sufficient RAM for the OS page cache to hold the active set of conversations. This requires more careful tuning and monitoring of Kafka itself. This is an acceptable trade-off.

*   **Neutral:**
    *   This decision formalizes a simpler, more robust, and more maintainable V1.0 bus architecture that still meets all core project requirements for speed and durability.

---
---

## Appendix A: Detailed Architectural Analysis and Rationale (v2)

### A.1. Original Hybrid Model and Its Flaws

The original ADR proposed a hybrid Kafka/Redis architecture. The rationale was to use the "best tool for the job"—Redis for speed and Kafka for durability. However, this introduced significant complexity: managing two distributed systems, ensuring data consistency between them, and building client logic to handle both.

### A.2. The Power of Kafka's Page Cache: A "Durable Fast Lane"

The key technical insight that enables this simplified architecture is a deep understanding of how Kafka works. Kafka is not merely a "disk-based" system. It is designed to be a **log whose performance is dictated by main memory.**

*   **Serving Reads from Memory:** A Kafka broker aggressively uses the host operating system's page cache. When consumers are reading "hot" data (messages that were recently written), they are almost always reading directly from RAM. This memory-to-memory transfer is extremely fast, with latencies in the **low single-digit milliseconds.**
*   **The V1.0 Context:** For the Joshua V1.0 system, the primary performance bottleneck is not the messaging bus; it is the multi-second response time of an Imperator's LLM call. The difference between a sub-millisecond Redis latency and a 2-5 millisecond Kafka latency is **architecturally insignificant**. The operational simplicity of a single system far outweighs the negligible performance gain of a hybrid approach.

By leveraging Kafka's page cache, we get a "Durable Fast Lane" in one system: the speed of in-memory reads for real-time collaboration and the absolute guarantee of disk-based durability for long-term learning.

### A.3. How This Simplifies the Ecosystem

*   **Rogers' Role:** Rogers is simplified. It is no longer an active message router in the data path. It becomes a **control plane** manager, responsible for creating topics and managing metadata, which is a much cleaner and more robust role.
*   **MAD Client (`Joshua_Communicator`):** The client library becomes a standard Kafka producer/consumer. This is a well-understood, battle-tested pattern with excellent library support.
*   **Babbage's Role:** Babbage's role as the "Read Model" builder in a CQRS pattern becomes much clearer. It is simply a long-term, resilient consumer of the Kafka log, completely decoupled from the real-time message flow.

This decision results in a V1.0 architecture that is simpler, more robust, and easier to operate, while still providing the foundational capabilities of speed and durability required for Joshua's evolution.

### A.4. Use Case Illustration: Onboarding a New MAD and Imperator Memory

To fully validate the pure-Kafka architecture, let's illustrate how it functions for two critical use cases: adding a new MAD and enabling the Imperator's "recent memory" for context.

#### A.4.1 Use Case: Onboarding the `Muybridge` MAD (Video Processing)

Let's assume we are in Phase 6 (Expansion) and we want to add the `Muybridge` MAD (video processing) to our mature, V7.0 ecosystem.

**Architectural State:**
*   The system is running on a pure-Kafka conversation bus.
*   The `Joshua` MAD is the active strategic leader (ADR-016).
*   The `Moses` MAD is the container orchestrator (ADR-018).
*   All other core MADs are operational.

**Step 1: The Strategic Decision (Human -> `Hopper` -> `Joshua`)**

1.  **Human User:** Expresses a need for a new capability (e.g., "We need video processing for our new project.").
2.  **`Hopper`'s Initiative:** The `Hopper` MAD (Autonomous Development Manager) receives this need. Its Imperator (Thought Engine) initiates a project to build the `Muybridge` MAD. `Hopper` then engages the human user conversationally to gather detailed requirements and generate a build plan. It creates the initial code for `Muybridge`, including its `Dockerfile` and a deployment manifest that specifies its resource needs (e.g., `gpu_required: true`). This code is placed in a known location in a Git repository that `Joshua` can access.
3.  **Request to `Joshua` for Approval:** Before commencing the formal build and deployment, `Hopper` submits a formal request to the `Joshua` MAD (Strategic Leader) for strategic permission:
    `joshua_request_mad_build_permission(name='Muybridge', manifest_path='/path/to/muybridge/manifest.json', build_plan={...})`
4.  **`Joshua`'s Deliberation:** `Joshua`'s Imperator (its Thought Engine) analyzes this strategic request. It checks the system's constitution, verifies that the new capability doesn't conflict with existing MADs, and confirms it aligns with the overall system roadmap. **`Joshua` grants permission to build, but does not execute the build itself.**
5.  **Approval:** `Joshua` approves the *build and future deployment* of `Muybridge`.

**Step 2: Service Discovery & Topic Creation (`Rogers` MAD)**

This is where the Kafka-centric design becomes crucial. For `Muybridge` to communicate, it needs dedicated Kafka topics.

1.  **`Joshua` informs `Rogers`:** `Joshua` sends a request to the `Rogers` MAD (the "Bus Controller"): `rogers_register_participant(participant_id='Muybridge')`.
2.  **`Rogers`' Action:** The `Rogers` MAD, as the manager of the bus, performs the necessary setup within Kafka:
    *   **Creates a "Mailbox" Topic:** It creates a dedicated, persistent Kafka topic named `mad.muybridge.inbox`. This is `Muybridge`'s primary, durable mailbox where other MADs can send it direct requests.
    *   **Registers in Service Registry:** `Rogers` updates its internal service registry, mapping the capability "video processing" to the `Muybridge` participant and its inbox topic. This registry is how other MADs will discover `Muybridge`.

At this point, the *communication infrastructure* for `Muybridge` exists on the bus, even though the MAD itself is not yet running.

**Step 3: Deployment (`Joshua` -> `Moses` -> Sutherland)**

1.  **`Joshua` delegates to `Moses`:** `Joshua`, having approved the deployment, now delegates the "how" to the container orchestrator, `Moses`.
    `moses_deploy_persistent_mad(mad_name='Muybridge', manifest={...})`
2.  **`Moses`'s Placement Logic:** `Moses`'s Imperator receives the request. It sees the `gpu_required: true` constraint in the manifest. To satisfy this, it internally consults with the `Sutherland` MAD (the GPU expert): `sutherland_recommend_placement(requirements={'gpu': true})`.
3.  **`Sutherland`'s Recommendation:** A `Sutherland` instance provides an optimal host recommendation (e.g., "Host-3 has a free GPU").
4.  **`Moses` Executes Deployment:** `Moses` issues a command to the *local `Moses` instance* on Host-3 to pull the `Muybridge` image and run the container.

**Step 4: The `Muybridge` MAD Comes Online**

1.  **Container Starts:** The `Muybridge` container starts on Host-3.
2.  **Connects to the Bus:** Its first action is to initialize its `Joshua_Communicator`. Using its configuration, it establishes a connection to the Kafka brokers.
3.  **Starts its "Consumer Group":** The `Joshua_Communicator` within `Muybridge` starts a Kafka consumer. This consumer subscribes to its dedicated inbox topic (`mad.muybridge.inbox`) and joins a unique consumer group (e.g., `cg-muybridge`). This makes it the exclusive reader of its "mailbox." It also subscribes to any broadcast topics it needs to listen to (e.g., `system.broadcasts`).

`Muybridge` is now fully online and part of the ecosystem.

**Step 5: A MAD uses the New Capability (`Hopper` -> `Muybridge`)**

1.  **`Hopper` needs a video transcribed:** `Hopper`'s Thought Engine decides it needs this new capability.
2.  **Service Discovery via `Rogers`:** `Hopper` doesn't know where `Muybridge` is. It asks `Rogers`: `rogers_find_capability(capability='video_transcription')`.
3.  **`Rogers` Responds:** `Rogers` checks its registry and replies: `{'participant_id': 'Muybridge', 'inbox_topic': 'mad.muybridge.inbox'}`.
4.  **`Hopper` Sends a Request:** `Hopper` now knows the "address." It becomes a **producer** to the `mad.muybridge.inbox` topic. It constructs a request message and publishes it to that Kafka topic.
    *   **Message Key:** `correlation_id` (for the response)
    *   **Message Value:** `{ "action": "muybridge_transcribe", "payload": {...} }`
    *   **Reply-To Header:** `Hopper` adds a header to the message specifying its *own* inbox topic (`mad.hopper.inbox`) where it expects the reply.
5.  **`Muybridge` Processes the Request:** As the **consumer** of its own inbox topic, `Muybridge` receives the message from `Hopper`. It processes the video transcription.
6.  **`Muybridge` Sends the Response:** `Muybridge` becomes a **producer**. It reads the `Reply-To` header from the original message and publishes the response to `Hopper`'s inbox topic (`mad.hopper.inbox`), using the same `correlation_id` as the message key.
7.  **`Hopper` Receives the Response:** `Hopper`'s consumer receives the response message, its `Joshua_Communicator` matches the `correlation_id`, and the asynchronous request is completed.

**Analysis of the Pure-Kafka Model in this Use Case:**

*   **Does it provide a "Fast Lane"?** Yes. When `Hopper` publishes to the `mad.muybridge.inbox` topic, if `Muybridge` is an active consumer, Kafka will likely serve the message directly from the page cache. The latency is in the low milliseconds—plenty fast for this asynchronous, conversational interaction.
*   **Does it provide a "Durable Log"?** Yes, perfectly. The request from `Hopper` and the response from `Muybridge` are both permanently appended to their respective Kafka topics. The entire interaction is captured, ordered, and replayable, providing perfect training data for the learning system.
*   **Is it Simple?** Architecturally, yes. There's one messaging system. The concepts are standard Kafka patterns: topics, producers, consumers, and consumer groups. `Rogers` acts as the "control plane" (creating topics), and the MADs are the "data plane" (producing/consuming messages).
*   **Is it Resilient?** Yes. If the `Muybridge` MAD is down when `Hopper` sends the request, the message simply sits in the `mad.muybridge.inbox` topic (Kafka retains it). When `Muybridge` comes back online, it will immediately consume the message and process it. This provides excellent temporal decoupling and resilience.

#### A.4.2 Use Case: Imperator's "Recent Memory" for Context

How does an Imperator use the bus as recent memory for context? It gets to the heart of how the pure-Kafka bus architecture directly enables the cognitive functions of the Imperator.

**Kafka Concepts at Play:**

To understand this, we need two key Kafka concepts:

1.  **Topics:** A topic is like a log file or a channel. In our architecture, **every conversation has its own dedicated topic**. For example, a project run by `Hopper` might take place in a topic named `conv.hopper.proj-alpha-123`.
2.  **Consumer Offsets:** Each consumer (a MAD listening to a topic) keeps track of its position in the log with a pointer called an "offset." It knows the last message it read. Crucially, a consumer can **rewind its offset** to re-read older messages.

**Scenario 1: Re-joining an Ongoing Conversation (Asynchronous Memory)**

Imagine a `Hopper` MAD that is working on a long-running project. It has been conversing with `Starret` and `Fiedler` in the `conv.hopper.proj-alpha-123` topic. `Hopper` then has to restart due to an update. How does its Imperator regain the "recent memory" of that conversation?

1.  **MAD Restarts:** The `Hopper` container restarts. Its `Joshua_Communicator` reconnects to Kafka.
2.  **Imperator Needs Context:** Before taking its next action, `Hopper`'s Imperator needs to know what was last discussed.
3.  **Client Connects as a Consumer:** The `Joshua_Communicator` starts a Kafka consumer and subscribes to the `conv.hopper.proj-alpha-123` topic.
4.  **Rewinding the Offset for Context:** Instead of just starting from the newest message, the client tells the consumer to **seek to an earlier offset**. It can ask for:
    *   The last `N` messages (e.g., `seek_to_offset(end - 50)`).
    *   All messages from the last `T` minutes (e.g., `seek_by_timestamp(now - 15_minutes)`).
5.  **Fast "Catch-Up" Consumption:** The client then consumes the messages from that earlier point up to the present. Because these messages are almost certainly still in the broker's **page cache (in memory)**, this is an extremely fast operation. `Hopper` can "re-read" the last 100 messages in a few milliseconds.
6.  **Imperator's Context is Built:** The content of these messages is fed into the Imperator's context window (e.g., LangChain's `ConversationBufferMemory`).

**Result:** The Imperator's "short-term memory" is now fully populated with the recent history of the conversation, exactly as if it had been running the whole time. The Kafka topic *is* the memory.

**Scenario 2: Awaiting a Response (Synchronous-Style Memory)**

This is the request/response pattern we discussed. A MAD's Imperator needs to maintain the immediate context of "I just asked a question, and I'm waiting for the answer."

1.  **`Hopper` asks `Horace` a Question:** `Hopper`'s Imperator decides it needs to write a file.
2.  **`Hopper` Produces to `Horace`'s Inbox:** It sends a message to the `mad.horace.inbox` topic with a unique `correlation_id` (e.g., `corr-xyz`) and a `reply-to` header pointing to its own inbox, `mad.hopper.inbox`.
3.  **`Hopper`'s Client Awaits a Response:** The `Joshua_Communicator` now does something specific. It starts a temporary, highly-focused Kafka consumer.
    *   **Subscribes to its own inbox:** `mad.hopper.inbox`.
    *   **Starts consuming from the latest offset.**
    *   **Filters for the `correlation_id`:** It inspects each incoming message, looking for one that has the `correlation_id` of `corr-xyz`.
4.  **`Horace` Responds:** `Horace` processes the request and sends a response message to the `mad.hopper.inbox` topic, making sure to include the `correlation_id` `corr-xyz`.
5.  **`Hopper`'s Client Receives the Match:** The temporary consumer sees the message with the matching ID. The `await` call in `Hopper`'s code that was waiting for the response now completes, and the response message is returned. The temporary consumer is then stopped.

**Synthesis: The Bus as the Source of All Context**

In both scenarios, the Kafka bus is not just a transport layer; it is the **externalized, queryable memory of the entire system.**

*   **Short-Term / Recent Memory:** Achieved by consuming the last N messages from a conversation topic. This is fast because the data is in the broker's page cache.
*   **Long-Term / Historical Memory:** Achieved by rewinding the offset much further back or by querying `Babbage`, which builds optimized "Read Models" (indexes) of the entire Kafka log for very deep, complex searches.

This architecture means the Imperator itself doesn't need to store a large amount of state in its own memory. Its memory is the bus. When it needs context, it simply reads it from the relevant topic on the bus, which is a fast and scalable operation. This keeps the MADs themselves lightweight and resilient to restarts.
