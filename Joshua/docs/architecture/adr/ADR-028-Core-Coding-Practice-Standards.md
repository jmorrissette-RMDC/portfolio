# ADR-028: Core Coding Practice Standards

**Status:** Proposed
**Date:** 2025-12-18
**Deciders:** System Architect

## Context and Problem Statement

To ensure the long-term maintainability, readability, and quality of the Joshua codebase, a set of explicit and enforceable coding practice standards is required. Without such standards, individual MADs and shared libraries may develop inconsistently, leading to increased technical debt, difficulty in collaboration (human-AI and AI-AI), and a higher risk of bugs.

## Decision

The Joshua project will adopt the following core coding practice standards. These standards are mandatory for all new code and will serve as guidelines for refactoring existing code.

### 1. Code Style & Linting

*   **Principle:** All Python code must adhere to a single, automated style.
*   **Standard:**
    *   **Formatting:** `black` is the official, non-negotiable code formatter.
    *   **Linting:** `ruff` is the official linter, configured to enforce a strict set of quality, style, and security rules.

### 2. Naming Conventions

*   **Principle:** Use clear, descriptive, and consistent names for all code elements.
*   **Standard:**
    *   **Modules/Packages:** `snake_case` (e.g., `joshua_communicator`).
    *   **Classes:** `PascalCase` (e.g., `ThoughtEngine`).
    *   **Functions, Methods, Variables:** `snake_case` (e.g., `route_message`).
    *   **Constants:** `UPPER_SNAKE_CASE` (e.g., `DEFAULT_PORT = 8000`).

### 3. Error Handling & Logging

*   **Principle:** Errors should be explicit and logs should be structured and informative.
*   **Standard:**
    *   **Exceptions:** Use specific, custom exceptions where appropriate (e.g., `ToolError`, `ConfigurationError`) instead of catching generic `Exception` where possible.
    *   **Logging:** All logging **must** be performed through the `Joshua_Communicator`'s integrated logger. Logs must be structured (e.g., JSON) and provide sufficient context for debugging and analysis.

### 4. Testing Philosophy

*   **Principle:** Code without tests is considered incomplete and cannot be deployed.
*   **Standard:**
    *   **Framework:** `pytest` is the official testing framework.
    *   **Requirement:** Every public function or method exposed by a MAD's Action Engine **must** have corresponding unit tests. Tests must cover successful execution paths, expected error conditions, and edge cases.

### 5. Docstrings and Type Hinting

*   **Principle:** Code should be self-documenting and statically analyzable.
*   **Standard:**
    *   **Type Hinting:** All function signatures and variable declarations **must** include modern Python type hints. This is non-negotiable.
    *   **Docstrings:** Every public module, class, and function **must** have a docstring explaining its purpose, arguments, and return value (e.g., adhering to Google Style or reStructuredText format).

### 6. Security Best Practices

*   **Principle:** Security is a foundational requirement, not an afterthought.
*   **Standard:**
    *   **No Hardcoded Secrets:** Credentials, API keys, and other sensitive information **must never** be stored directly in the codebase or committed to version control.
    *   **Secrets Management (Temporary Exception):** Until the `Turing` MAD (specialist for secrets management) is fully built and integrated, secrets will be managed via **environment variables**. This interim solution aligns with the 12-Factor App methodology (Factor 3: Config) as a temporary measure.
    *   **Input Sanitization:** All data originating from external sources or other MADs must be treated as untrusted and undergo proper validation and sanitization before processing.

### 7. Git Workflow

*   **Principle:** The `main` branch must always be stable, deployable, and reflect the highest quality code.
*   **Standard:**
    *   **Feature Branches:** All new development (features, bugfixes, refactoring) **must** be conducted on separate feature branches.
    *   **Pull Requests (PRs):** Changes are merged into `main` exclusively via Pull Requests.
    *   **Code Reviews:** Every PR **must** undergo a code review and receive approval from at least one other team member. Automated Continuous Integration (CI) checks (linting, formatting, testing, type checking) **must** pass before a PR can be merged.

## Consequences

*   **Positive:**
    *   Increases code quality, readability, and consistency across the entire codebase.
    *   Facilitates easier collaboration and understanding for both human and AI developers.
    *   Reduces the likelihood of introducing bugs and simplifies debugging.
    *   Provides a clear framework for automated quality checks within CI pipelines.
*   **Action Item:** All development teams (human and AI) must familiarize themselves with these standards. Automated checks will be integrated into the CI process to enforce compliance. The exception for `Turing` will be tracked and removed once `Turing` is operational.
