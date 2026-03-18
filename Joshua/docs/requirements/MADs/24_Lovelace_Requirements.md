# Lovelace Requirements

- **Role**: Data Science & Analytics
- **Version**: V7.0
- **Home**: `mads/lovelace/`

---

## 1. Overview

-   **Purpose**: Lovelace is the data science and analytics specialist MAD for the Joshua ecosystem.
-   **V7.0 Scope Definition**: As a V7.0 MAD, Lovelace provides a comprehensive and cognitive suite of tools for statistical analysis, predictive modeling, and machine learning, enabling fully autonomous data science workflows.

---

## 2. Tool Exposure Model

This MAD follows the Direct Tool Exposure architecture (ADR-023). Its public tools are exposed directly on its MCP server and are discoverable via the Rogers registry. Any incoming communication that is not a valid MCP call for an exposed tool is routed to the Thought Engine for conversational processing (e.g., "Can you analyze this dataset for correlations and anomalies?").

> **Note on Tool List:** The tools listed in this document are a *provisional set* based on the MAD's high-level requirements. The final, authoritative list of tools, their specific parameters, and their return schemas will be defined in a dedicated Design Document prior to implementation.

---

## 3. Public Action Engine Tools

### `lovelace_run_analysis`
- **Description:** Performs a specified statistical or machine learning analysis on data retrieved from other MADs.
- **Input Schema:**
    - `analysis_type` (string, required): The type of analysis to perform (e.g., "correlation", "regression", "clustering").
    - `data_source` (dict, required): A pointer to the data, specifying the source MAD and query (e.g., `{"mad": "codd", "query": "SELECT * FROM users_log"}`).
    - `parameters` (dict, optional): Analysis-specific parameters (e.g., `{"target_variable": "churn", "features": ["age", "tenure"]}`).
- **Output Schema:** `{"status": "success", "results": {"summary": "...", "model_metrics": {...}, "visualization_path": "/path/to/chart.png"}}`

### `lovelace_train_model`
- **Description:** Trains a machine learning model on a specified dataset.
- **Input Schema:**
    - `model_type` (string, required): The type of model to train (e.g., "linear_regression", "random_forest").
    - `data_source` (dict, required): A pointer to the training data.
    - `target_variable` (string, required): The variable to predict.
    - `feature_variables` (array[string], required): The features to use for training.
- **Output Schema:** `{"status": "success", "model_id": "model-uuid-123", "metrics": {"accuracy": 0.92, "precision": 0.88}}`

### `lovelace_predict`
- **Description:** Uses a previously trained model to make predictions on new data.
- **Input Schema:**
    - `model_id` (string, required): The ID of the trained model to use.
    - `new_data_source` (dict, required): A pointer to the new data for prediction.
- **Output Schema:** `{"status": "success", "predictions": [0.1, 0.9, 0.3], "model_id": "model-uuid-123"}`

---

## 4. Future Evolution (Post-V0)

Lovelace is introduced in Phase 6 (Expansion) at V7.0 as the specialized data science and analytics platform for the mature Joshua ecosystem.

*   **Phase 6 (Expansion / V7.0):** Lovelace enters the ecosystem as a fully-capable V7.0 MAD with complete PCP (DTR, LPPM, CET, CRS), pure Kafka conversation bus integration, and eMAD awareness. As the data science specialist, Lovelace provides statistical analysis, predictive modeling, and machine learning capabilities. Lovelace's CET enables complex multi-step analytical workflows (data cleaning → feature engineering → modeling → validation → visualization), while CRS continuously improves model selection and hyperparameter tuning strategies. Lovelace coordinates with Codd/Babbage (data access), Playfair (visualization), Bush (notebook workflows), Bass/Muybridge (image/video analysis), and Brin/Gates (cloud ML platforms).
*   **Post-V7.0 Enhancements:** Future evolution includes AutoML capabilities, deep learning model training and deployment, real-time analytics streams, causal inference frameworks, A/B testing orchestration, experiment tracking and reproducibility, and strategic insight generation aligned with Joshua's objectives. Lovelace becomes the central intelligence for autonomous data science operations.

---