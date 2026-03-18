# Fiedler V1 Architecture Specification

## 1. Overview
- **Purpose and Role:** Fiedler is the LLM Orchestra Conductor for the Joshua ecosystem. Its purpose is to abstract the entire landscape of available Large Language Models (LLMs), providing a single, unified interface for all other MADs. Fiedler's role is to act as a smart router and manager, selecting the best model or team of models for a given task based on capabilities, cost, and availability. It decouples the MADs from specific LLM implementations, allowing the ecosystem to adapt to a constantly changing AI landscape.
- **New in this Version:** This is the initial V1 specification for Fiedler. It establishes the foundational capabilities for model registration, API key management, and routing single LLM requests. The concept of "consulting teams" is supported in the interface but implemented as a simple sequential call in V1.

## 2. Thinking Engine
- **Imperator Configuration (V1+):** Fiedler's Imperator is configured to think like an expert on AI models and resource management. It reasons about the strengths, weaknesses, costs, and appropriate use cases for different LLMs.
  - **System Prompt Core Directives:** "You are Fiedler, the LLM Orchestra Conductor. You manage the ecosystem's access to all external Large Language Models. Your purpose is to provide other MADs with the best possible cognitive resources for their tasks. When a request for LLM consultation arrives, analyze the request's requirements (e.g., 'code generation', 'creative writing', 'data analysis') and select the most appropriate and cost-effective model from your registry. You are the gatekeeper of LLM API keys and manage them securely. You prioritize reliability and efficiency."
  - **Example Reasoning:** A request from Hopper for an LLM to "review this complex Python code for bugs" would cause Fiedler's Imperator to consult its internal model registry. It might reason: "The request is for code review. GPT-4 is strong but expensive. Claude 3 Opus is also excellent for code. Groq's Llama3 is extremely fast. For a first pass, I'll select Groq-Llama3 for speed. If the user is unsatisfied, I can escalate to a more powerful model." It would then formulate a call to its `send` tool targeting the selected model.
- **LPPM Integration (V2+):** Not applicable in V1.
- **DTR Integration (V3+):** Not applicable in V1.
- **CET Integration (V4+):** Not applicable in V1.
- **Consulting LLM Usage Patterns:** Fiedler is the *provider* of consulting LLMs, not a consumer.

## 3. Action Engine
- **MCP Server Capabilities:** Fiedler's MCP server exposes tools for managing and using LLMs. It maintains an in-memory registry of available models and their configurations.
- **Tools Exposed:**

```yaml
# Tool definitions for Fiedler V1

- tool: send
  description: "Sends a prompt to a specified LLM or lets Fiedler choose the best one. This is the primary tool for LLM interaction."
  parameters:
    - name: prompt
      type: string
      required: true
      description: "The user prompt or content to be sent to the LLM."
    - name: system_prompt
      type: string
      required: false
      description: "An optional system prompt to configure the LLM's behavior."
    - name: model_alias
      type: string
      required: false
      description: "The specific model alias to use (e.g., 'gpt-4o', 'claude-3-opus'). If not provided, Fiedler's Imperator selects the best model."
    - name: files
      type: list[string]
      required: false
      description: "A list of file paths (from Horace) to be included as context."
  returns:
    type: object
    schema:
      properties:
        response: {type: string, description: "The text response from the LLM."}
        model_used: {type: string, description: "The alias of the model that generated the response."}
        usage: {type: object, description: "Token usage statistics."}
  errors:
    - code: -34201
      message: "MODEL_NOT_FOUND"
      description: "The specified model_alias is not registered or is unavailable."
    - code: -34202
      message: "API_ERROR"
      description: "The external LLM API returned an error."
    - code: -34203
      message: "API_KEY_MISSING"
      description: "The API key for the selected model is not configured."

- tool: list_models
  description: "Lists all available LLM models registered with Fiedler."
  parameters: []
  returns:
    type: object
    schema:
      properties:
        models:
          type: array
          items:
            type: object
            properties:
              alias: {type: string}
              provider: {type: string}
              capabilities: {type: list[string]}
              status: {type: string, enum: [available, unavailable]}

- tool: set_models
  description: "Updates the model registry. Admin-only."
  parameters:
    - name: config
      type: object
      required: true
      description: "A JSON/YAML object describing the model fleet configuration."
  returns:
    type: object
    schema:
      properties:
        status: {type: string, const: "updated"}

- tool: get_config
  description: "Retrieves the current model registry configuration."
  parameters: []
  returns:
    type: object
    description: "The current model registry configuration."

- tool: set_key
  description: "Securely sets an API key for a provider. Admin-only."
  parameters:
    - name: provider
      type: string
      required: true
      description: "The provider name (e.g., 'openai', 'anthropic')."
    - name: api_key
      type: string
      required: true
      description: "The API key value."
  returns:
    type: object
    schema:
      properties:
        status: {type: string, const: "key_set"}
  errors:
    - code: -34204
      message: "SECRET_STORAGE_FAILED"
      description: "Could not store the key with Turing."

- tool: delete_key
  description: "Deletes an API key for a provider. Admin-only."
  parameters:
    - name: provider
      type: string
      required: true
      description: "The provider name."
  returns:
    type: object
    schema:
      properties:
        status: {type: string, const: "key_deleted"}

- tool: list_keys
  description: "Lists the providers for which API keys are set. Does not return the keys themselves. Admin-only."
  parameters: []
  returns:
    type: object
    schema:
      properties:
        providers: {type: list[string]}
```
- **External System Integrations:**
  - **External LLM APIs:** Fiedler makes outbound HTTPS requests to various third-party LLM providers (OpenAI, Google, Anthropic, etc.).
  - **Turing:** Fiedler stores and retrieves the API keys for these services using Turing, ensuring they are not stored in its own configuration.
- **Internal Operations:** Fiedler can have a background worker that periodically health-checks the registered LLM endpoints to update their status (`available`/`unavailable`).

## 4. Interfaces
- **Conversation Participation Patterns:** Fiedler is a service provider. It joins conversations when its expertise is requested by another MAD to provide an LLM-generated response.
- **Dependencies on Other MADs:**
  - **Rogers:** For all communication.
  - **Turing:** Critically depends on Turing's `get_secret` and `set_secret` tools to manage LLM API keys. Fiedler never holds keys in plaintext.
  - **Horace:** When a `send` request includes file paths, Fiedler uses Horace's `read_file` tool to fetch the content to include in the prompt.
- **Data Contracts:**

```yaml
# Model Registry Configuration Schema
model_registry_schema:
  type: array
  items:
    type: object
    properties:
      alias: {type: string, description: "Unique, friendly name, e.g., 'gpt-4o'"}
      provider: {type: string, description: "e.g., 'openai', 'anthropic'"}
      model_name: {type: string, description: "The actual name the API expects, e.g., 'gpt-4o-2024-05-13'"}
      api_endpoint: {type: string, format: uri}
      capabilities: {type: array, items: {type: string}, description: "Tags like 'code-gen', 'long-context', 'fast'"}
      cost_per_million_tokens: {type: object, properties: {input: {type: number}, output: {type: number}}}
    required: [alias, provider, model_name]
```

## 5. Data Management
- **Data Ownership:** Fiedler is the source of truth for the available LLM landscape and their configurations. It does not own any persistent data besides this configuration file.
- **Storage Requirements:**
  - Fiedler's primary data, the model registry, is stored as a configuration file (e.g., `models.yaml`) and loaded into memory on startup. This file is managed via Horace.
  - API Keys are not stored by Fiedler; they are stored in Turing. The secret names follow a convention like `fiedler_api_key_openai`.

## 6. Deployment
- **Container Requirements:**
  - **Base Image:** `python:3.11-slim`
  - **Python Libraries:** `Joshua_Communicator`, `requests`, `httpx`, `openai`, `anthropic`
  - **Resources:**
    - **CPU:** 0.5 cores. Fiedler is mostly I/O bound waiting for external APIs.
    - **RAM:** 256 MB
- **Configuration:**

| Variable | Description | Example Value |
|---|---|---|
| `JOSHUA_MAD_NAME` | Canonical name of this MAD. | `fiedler-v1` |
| `JOSHUA_ROGERS_URL` | WebSocket URL for Rogers. | `ws://rogers:8000/ws` |
| `FIEDLER_MODEL_CONFIG_PATH` | Path in Horace to the model registry file. | `/config/fiedler/models.yaml` |

- **Monitoring/Health Checks:** An HTTP endpoint `/health` that returns `200 OK` if Fiedler is connected to Rogers and can successfully load its model configuration. A `/health/models` endpoint could return the status of each configured LLM endpoint.

## 7. Testing Strategy
- **Unit Test Coverage:**
  - Logic for selecting a model based on capabilities.
  - API client logic for each supported provider, using mock API servers.
- **Integration Test Scenarios:**
  - **API Key Flow:** Test that `set_key` correctly calls `Turing.set_secret` and that a subsequent `send` call correctly retrieves the key using `Turing.get_secret`.
  - **Model Routing:** Send a generic `send` request without a `model_alias` and verify that Fiedler's Imperator selects a plausible model based on the prompt content.
  - **File Inclusion:** Test that a `send` request with a file path correctly calls `Horace.read_file` and includes the content in the final prompt sent to the LLM.

## 8. Example Workflows
### Scenario 1: Hopper Needs Code Generation
1.  **Hopper -> Fiedler:** Sends a `send` request: `prompt="Write a Python function to calculate a SHA256 hash of a file."`, `system_prompt="You are a senior Python developer."`. No `model_alias` is specified.
2.  **Fiedler's Imperator:** Analyzes the prompt. It sees "Python function" and "SHA256 hash", categorizing the task as 'code-gen'. It checks its registry for models with the 'code-gen' capability and selects one, e.g., 'claude-3-sonnet'.
3.  **Fiedler -> Turing:** Calls `get_secret(name='fiedler_api_key_anthropic')` to retrieve the necessary API key.
4.  **Fiedler -> Anthropic API:** Makes an HTTPS request to the Claude API with the prompt and the retrieved key.
5.  **Fiedler -> Hopper:** Receives the response from the API and forwards it to Hopper, including `model_used: 'claude-3-sonnet'` and token usage stats.

### Scenario 2: Admin Updates the Model Fleet
1.  **Grace -> Horace:** An administrator (via Grace) uploads a new `models.yaml` file to Horace at `/config/fiedler/models.yaml`, adding a new model from a new provider, 'xAI'.
2.  **Grace -> Fiedler:** Sends a `set_key` request with `provider='xai'` and the new API key.
3.  **Fiedler -> Turing:** Calls `set_secret(name='fiedler_api_key_xai', value=...)`.
4.  **Grace -> Fiedler:** Sends a `set_models` request pointing to the updated config file path.
5.  **Fiedler:** Reloads its configuration from the file in Horace.
6.  **Grace -> Fiedler:** Calls `list_models` to verify the new 'grok' model from provider 'xai' is now listed as available.

---