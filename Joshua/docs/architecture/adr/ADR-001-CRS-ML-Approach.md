# ADR-001: Adopt Pattern-Matching and Anomaly Detection for the CRS

**Status:** Accepted

**Context:**
The Cognitive Recommendation System (CRS) for Joshua is envisioned as a "Netflix for actions," providing proactive recommendations to the Imperator. The core architectural question was whether to implement this using traditional recommender system algorithms (e.g., Collaborative Filtering, Matrix Factorization) or a different set of machine learning techniques.

A traditional recommender system is designed to solve the "matrix completion" problem, predicting a user's rating for an item based on a sparse `user-item` rating matrix. Joshua's operational data, however, is not a user-item matrix. It is a rich, chronological log of `(context, decision, outcome)` events stored on the conversation bus. The goal is not to predict a rating for a decision, but to assess if a proposed decision is optimal within a given context and to recommend a better course of action if it is not. This represents a different class of ML problem.

**Decision:**
We will **not** use traditional Collaborative Filtering or Matrix Factorization algorithms as the primary mechanism for the CRS.

Instead, the CRS will be implemented as a hybrid ML system composed of the following capabilities, which are better suited to Joshua's data structure:

1.  **Semantic Search / Vector Similarity:** To find similar historical `contexts` from the operational event log. This allows the CRS to reason based on precedent.
2.  **Anomaly Detection / Outlier Detection:** To identify when a proposed `decision` deviates significantly from a history of successful decisions made in similar contexts. This is the core of "proactive critique."
3.  **Classification / Generative Models:** To recommend a better `decision` based on the most frequent successful outcomes found in the historical data for a given context.

**Consequences:**

*   **Positive:**
    *   **Correct Tool for the Job:** This approach aligns the ML algorithms with the actual structure of the data (event logs) and the problem to be solved (contextual decision validation).
    *   **Richer Recommendations:** It enables a more sophisticated set of recommendations beyond simple "ratings," including identifying missing steps, flagging deviations from best practice, and suggesting alternative plans.
    *   **Architectural Alignment:** This model fits perfectly with the proposed V5 LangGraph implementation, where each of these ML techniques can be encapsulated as a modular node in the parallel "observer" graph.
    *   **Leverages Existing Architecture:** It can reuse the RAG and vector search infrastructure already being developed for the CET.

*   **Negative:**
    *   **No Single Off-the-Shelf Library:** We cannot use a single, turn-key recommender system library. The CRS will require the integration of several distinct ML components.
    *   **Increased Implementation Complexity:** The initial implementation is more complex than simply plugging in a standard collaborative filtering model.

*   **Neutral:**
    *   This decision solidifies the CRS's architectural role as a *cognitive validator* and *process optimizer*, distinct from a simple content recommendation engine.

---
---

## Appendix A: Detailed Rationale & Inspirations for the CRS ML Approach

### A.1. The "Netflix for Actions" Analogy

The guiding vision for the CRS is to be a "Netflix for actions." Just as Netflix uses a user's viewing history to recommend the next movie, the CRS uses the entire system's operational history to recommend the next action or course correction.

-   **Netflix:** Analyzes `(user, movie, rating)` data to predict what a user will like.
-   **Joshua CRS:** Analyzes `(context, decision, outcome)` data to predict what decision will lead to a successful outcome.

This analogy is powerful but also highlights a critical technical distinction that drives this ADR.

### A.2. Data Structure: Why Collaborative Filtering is the Wrong Tool

The core reason for rejecting traditional recommender algorithms is a fundamental mismatch in the data's structure and the problem's nature.

-   **Traditional CRS Data (e.g., Netflix):** The data is a large, sparse **`user-item` matrix**. The problem is **matrix completion**—filling in the missing ratings. Algorithms like **Collaborative Filtering** (finding similar users) and **Matrix Factorization** are specifically optimized to decompose this matrix and predict missing values.

-   **Joshua's CRS Data:** The data is a **log of structured events**. Each event is a `(context, decision, outcome)` triplet.
    -   `context`: A high-dimensional object including conversation history, system state, and the user's request.
    -   `decision`: A complex, structured plan or action, not a simple "item" from a fixed catalog.
    -   `outcome`: A measure of success.

The problem is not to predict a "rating" for a decision. It is to **classify a proposed decision as optimal or anomalous** within a given context, and if anomalous, **recommend a better decision** based on historical precedent. This is a problem of pattern matching, anomaly detection, and classification, not matrix completion.

### A.3. The Right ML Toolkit for the Job

Because the problem is different, we must use a different, more appropriate set of ML tools. The CRS's intelligence will emerge from the combination of three distinct techniques:

1.  **Finding Similar Situations (Context Matching) -> Semantic Search:** The first step is to answer, "Have we been in a situation like this before?" This is a semantic search problem. We will use **vector embeddings** of the `context` portion of our event logs, stored in a vector database, to find the nearest historical neighbors to the current situation. This is the same underlying technology as RAG.

2.  **Identifying Bad Patterns (Anomaly Detection) -> Outlier Detection:** The next step is to answer, "Is the proposed plan weird compared to what worked in the past?" For a given context, we can retrieve all historical decisions. Successful decisions will form a "cluster" of good patterns. If the new proposed decision falls far outside this cluster, it is an anomaly. We will use algorithms like **Isolation Forests** or **statistical deviation analysis** for this.

3.  **Recommending a Better Action -> Classification/Generation:** Finally, if a plan is flagged as anomalous, we must suggest an alternative. We can do this in two ways:
    *   **Classification:** Look at all the successful historical decisions for this context and recommend the most frequent one. This is a simple classification task.
    *   **Generation:** For more complex plans, we can use a small, fast LLM. We provide it with the context, the flawed plan, and a few examples of historically successful plans, and ask it to generate a corrected version.

This hybrid toolkit is far more powerful and appropriate for Joshua's data than a single, monolithic collaborative filtering model.
