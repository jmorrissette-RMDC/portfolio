# Hopper V1 Architecture Synthesis Prompt

**Date:** 2025-10-13
**Pathfinder:** Hopper (1 of 2 MADs)
**Version:** V1 - Conversational (Imperator)
**Iteration:** 1

---

## Mission

Create comprehensive V1 architecture and requirements for **Hopper - The Software Engineer MAD**.

---

## Context Documents

You have access to the complete anchor package:
- ANCHOR_OVERVIEW.md - System vision, V1-V4 definitions
- SYSTEM_DIAGRAM.md - V4 end-state architecture
- NON_FUNCTIONAL_REQUIREMENTS.md - Performance, security, logging
- MAD_ROSTER.md - All 13 MADs with descriptions
- V1_PHASE1_BASELINE.md - Rogers + Dewey proven baseline
- ARCHITECTURE_GUIDELINES.md - How to write requirements
- REVIEW_CRITERIA.md - What reviewers check

---

## Hopper Overview (from MAD_ROSTER.md)

**Purpose:** To coordinate and execute autonomous software development tasks.

**Primary Responsibilities:**
- Write, debug, and test code in various languages
- Interact with version control systems (e.g., Git)
- Read and understand existing codebases
- Execute build and test scripts
- Can manage teams of eMADs for larger development projects

**Key Capabilities/Tools:**
- Code generation and analysis tools
- Terminal access for running commands
- Version control integration

**Lifecycle:** Can be Persistent (for oversight) or Ephemeral (for specific coding tasks)

**Key Dependencies:** Rogers, Horace (file system), Turing (secrets), Fiedler (consulting LLMs)

---

## V1 Requirements

For V1, Hopper must have:

1. **Imperator Integration:**
   - Dedicated LLM for software engineering reasoning
   - Understands programming languages, patterns, architectures
   - Can reason about code quality, testing, debugging

2. **Conversation Bus Integration:**
   - Joins conversations via Rogers
   - Receives coding requests from users (via Grace) or other MADs
   - Can initiate conversations with Horace (files), Turing (secrets), Fiedler (consultants)

3. **Core Software Engineering Tools:**
   - Code generation (write_code)
   - File operations via Horace (read_code, save_code)
   - Command execution (run_command, run_tests)
   - Git operations (git_commit, git_push, git_status)
   - Code analysis (analyze_codebase, find_bugs)

4. **Consulting LLM Integration:**
   - Request code reviews from Fiedler
   - Request language specialists for specific tasks
   - Request test generation assistance

5. **Logging as Conversations:**
   - All actions logged to #logs-hopper-v1
   - Uses joshua_logger

---

## Required Output Format

Follow the Standardized MAD Architecture Template from ARCHITECTURE_GUIDELINES.md:

```markdown
# Hopper V1 Requirements

## 1. Overview
- Purpose and Role
- New in this Version (N/A for V1)

## 2. Thinking Engine
- Imperator Configuration (V1+)
- Consulting LLM Usage Patterns

## 3. Action Engine
- MCP Server Capabilities
- Tools Exposed (use YAML format)
- External System Integrations
- Internal Operations

## 4. Interfaces
- Conversation Participation Patterns
- Dependencies on Other MADs
- Data Contracts (YAML/JSON)

## 5. Data Management
- Data Ownership
- Storage Requirements
- Conversation Patterns

## 6. Deployment
- Container Requirements
- Configuration
- Monitoring/Health Checks

## 7. Testing Strategy
- Unit Test Coverage
- Integration Test Scenarios

## 8. Example Workflows
- 2-3 concrete examples with conversational messages
```

---

## Quality Requirements

- **Deployable:** A senior engineer can implement from this document without clarification
- **Unambiguous:** All interfaces, tools, and behaviors explicitly defined
- **Complete:** All dependencies listed, all tools specified in YAML
- **Concrete:** Include 2-3 detailed example workflows
- **Compliant:** Adheres to NON_FUNCTIONAL_REQUIREMENTS.md

---

## Synthesis Instructions

1. Read all anchor package documents
2. Understand Hopper's role in the ecosystem
3. Design V1 architecture with Imperator as the core intelligence
4. Define all tools in YAML format
5. Show how Hopper interacts with Rogers, Horace, Turing, Fiedler
6. Provide concrete examples of coding workflows

**Execute synthesis now.**
