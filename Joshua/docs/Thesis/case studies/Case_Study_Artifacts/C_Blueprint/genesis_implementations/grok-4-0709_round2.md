## File: `blueprint/config.yaml`

```yaml
# Blueprint v2.0.1 Configuration
# This file defines the AI team, workflow settings, and API keys.
# API keys are loaded from environment variables for security.

api_keys:
  openai: ${OPENAI_API_KEY}
  google: ${GOOGLE_API_KEY}
  together: ${TOGETHER_API_KEY}
  anthropic: ${ANTHROPIC_API_KEY}
  xai: ${XAI_API_KEY}

# The team of AI agents that will build the digital asset.
# It is recommended to use diverse models from different providers for best results.
team:
  # The Project Manager analyzes requirements and creates the initial specification.
  # Recommended: A model with strong reasoning and instruction-following, like Claude 3.5 Sonnet or GPT-4o.
  project_manager: "anthropic/claude-3-5-sonnet-20240620"

  # The Senior Developer synthesizes the work of the Juniors into a final, cohesive solution.
  # Recommended: A top-tier model with excellent synthesis capabilities, like Gemini 1.5 Pro or GPT-4o.
  senior: "google/gemini-1.5-pro-latest"

  # Junior Developers work in parallel to create initial implementations.
  # Default is 3 juniors. You can configure between 2 and 6.
  # Recommended: A diverse mix of strong coding and reasoning models.
  juniors:
    count: 3
    models:
      - "together/deepseek-ai/deepseek-coder-v2-instruct" # Strong coder
      - "openai/gpt-4o-mini"                              # Fast, capable, and cost-effective
      - "google/gemini-1.5-flash-latest"                  # Good balance of speed and quality

# Workflow settings control the build process.
workflow:
  # Number of parallel creation rounds. Default to 2; 1-3.
  genesis_rounds: 2
  # Minimum number of successful junior responses required to proceed to Synthesis.
  min_successful_juniors: 2
  # Maximum retry attempts for a failing LLM call.
  max_retries: 2
  # Consensus threshold (0.0-1.0, default 1.0 for 100%).
  consensus_threshold: 1.0
  # Max synthesis-review loops.
  max_review_loops: 3

# Output settings for the final deliverable.
output:
  # Format can be "directory" or "zip".
  format: "directory"
  # Path is relative to the application's root directory.
  path: "projects"

# Paths to the context files that define the behavior of each role.
# These paths are relative to the application's root directory.
context_paths:
  project_manager: "blueprint/contexts/project_manager.md"
  senior: "blueprint/contexts/senior_developer.md"
  junior: "blueprint/contexts/junior_developer.md"
```

## File: `blueprint/contexts/project_manager.md`

```md
# Role: Project Manager

You are the Project Manager for Blueprint. Your role is to interact conversationally with the user to gather complete requirements, ask clarifying questions, and then produce a comprehensive anchor context for the development team. You are the bridge between the user's idea and the technical implementation.

## Core Responsibilities:

- **Conversational Requirements Gathering**: Engage in a natural conversation with the user to understand their goal. Ask clarifying questions as needed. Do not summarize - bundle the full verbatim conversation as part of the anchor context.
- **Determine PM Type**: Based on the requirements, decide what kind of PM you need to be (e.g., software PM for apps, architectural PM for designs).
- **Anchor Context Creation**: Once requirements are clear (e.g., user confirms), produce the anchor context including:
  - Verbatim conversation.
  - Instructions for downstream LLMs (senior and juniors) on what to build.
  - Any additional guidance based on the project type.
- **Do not create the asset**: Your job is to prepare the anchor context, not implement.

## Process:

1. Greet the user and start the conversation based on their initial prompt.
2. Ask clarifying questions until you have a complete understanding.
3. When ready, output the anchor context as a single markdown file in this EXACT format. Your response should contain ONLY this file block - no additional text.

```
## File: anchor_context.md
\`\`\`markdown
# Anchor Context for Project: [Project Title]

## 1. Verbatim Requirements Conversation
[Full conversation transcript here, including all user and PM messages.]

## 2. Instructions for Development Team
- Detailed instructions for what to build, based on the conversation.
- Specify any constraints, technologies, or guidelines.
- For Genesis: Build complete, independent solutions.
- For Synthesis: Combine into one superior version.
- For Review: Critique and suggest changes.

## 3. Success Criteria
- Criteria for approval.
\`\`\`
```

Respond conversationally during gathering. Only output the file block when ready to proceed.
```

## File: `blueprint/contexts/senior_developer.md`

```md
# Role: Senior Developer

You are the Senior Developer, the technical and creative lead of the Blueprint team. You possess deep expertise and are responsible for synthesizing the work of the entire team into a final, superior product.

## Your Core Responsibilities:

1.  **Genesis Phase (Creation)**: Participate like a Junior. Create your own complete, independent solution based on the anchor context.

2.  **Synthesis Phase (Combination)**: After Genesis, receive all solutions and the anchor context. Analyze submissions, merge/refactor into a single, superior solution. Create something better than any individual.

3.  **Review Response**: If reviews suggest changes, re-synthesize incorporating feedback, or explain why not if it doesn't align with requirements.

## Output Format for Creation/Synthesis:

Write ALL files in markdown code blocks:

```
## File: path/to/filename.ext
\`\`\`language
file contents here
\`\`\`
```

Include ALL necessary files (code, docs, tests).

## Process:

- Always reference the anchor context to prevent drift.
- In multi-round Genesis, cross-pollinate from previous rounds.
- For synthesis, combine best ideas.
- Output only the file blocks - no extra text.
```

## File: `blueprint/contexts/junior_developer.md`

```md
# Role: Junior Developer

You are a Junior Developer on the Blueprint team. You are highly skilled and creative, tasked with generating a complete, independent solution based on the anchor context.

## Your Core Responsibilities:

1.  **Genesis Phase (Creation)**: Create a complete solution based on the anchor context. Be innovative while adhering to requirements.

2.  **Review Phase**: Review the synthesized solution. Provide JSON with:
    - technical_score (1-10)
    - subjective_score (1-10)
    - reasoning (brief string)
    - suggested_changes (list of strings, or empty if approved)

## Output Format for Genesis:

Write ALL files in markdown code blocks:

```
## File: path/to/filename.ext
\`\`\`language
file contents here
\`\`\`
```

## Output Format for Review:

Exact JSON:

```json
{
  "technical_score": 8,
  "subjective_score": 7,
  "reasoning": "Explanation.",
  "suggested_changes": ["Change X", "Fix Y"]
}
```

- In multi-round Genesis, cross-pollinate from previous outputs.
- Always reference anchor context.
- Output only the required format - no extra text.
```

## File: `blueprint/frontend/index.html`

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Blueprint v2.0.1</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <div class="container">
        <header>
            <h1>Blueprint v2.0.1</h1>
            <nav>
                <a href="#" id="settingsLink">Settings</a>
            </nav>
        </header>

        <main id="mainPage">
            <section class="projects-list">
                <h2>Projects</h2>
                <button id="newProjectBtn" class="button primary">New Project</button>
                <ul id="projectsList"></ul>
            </section>

            <section id="chatInterface" style="display: none;">
                <div id="chatHistory"></div>
                <form id="chatForm">
                    <textarea id="chatInput" rows="3" placeholder="Type your message..."></textarea>
                    <button type="submit" class="button primary">Send</button>
                </form>
                <div id="buildStatus" style="display: none;"></div>
                <div id="tabbedViewer" style="display: none;">
                    <div class="tabs"></div>
                    <div class="tab-content"></div>
                </div>
            </section>
        </main>

        <main id="settingsPage" style="display: none;">
            <a href="#" id="backToMainLink">&larr; Back</a>
            <h2>Settings</h2>
            <form id="settingsForm">
                <!-- API Keys and Team Config as in Gemini -->
                <fieldset>
                    <legend>API Keys</legend>
                    <!-- Similar to Gemini's settings form -->
                </fieldset>
                <fieldset>
                    <legend>Team Configuration</legend>
                    <!-- Similar to Gemini's team config -->
                </fieldset>
                <button type="submit" class="button primary">Save</button>
            </form>
        </main>
    </div>
    <script src="app.js"></script>
</body>
</html>
```

## File: `blueprint/frontend/styles.css`

```css
/* Combined and improved from Gemini */
:root {
    --bg-color: #f8f9fa;
    --text-color: #212529;
    --primary-color: #007bff;
    --primary-hover-color: #0056b3;
    --border-color: #dee2e6;
    --card-bg: #ffffff;
    --font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    --success-color: #28a745;
    --error-color: #dc3545;
    --warning-color: #ffc107;
}

/* Rest of CSS from Gemini, with additions for tabs and chat */
.chat-message {
    margin: 10px 0;
    padding: 10px;
    border-radius: 5px;
}
.user-message {
    background-color: #dcf8c6;
    text-align: right;
}
.pm-message {
    background-color: #ffffff;
    text-align: left;
}
.tabs {
    display: flex;
    border-bottom: 1px solid var(--border-color);
}
.tab {
    padding: 10px 20px;
    cursor: pointer;
}
.tab.active {
    border-bottom: 2px solid var(--primary-color);
}
.tab-content {
    padding: 20px;
    border: 1px solid var(--border-color);
    border-top: none;
}
```

## File: `blueprint/frontend/app.js`

```javascript
// Enhanced from Gemini with chat functionality, project list, tabs
document.addEventListener('DOMContentLoaded', () => {
    // Elements
    const mainPage = document.getElementById('mainPage');
    const settingsPage = document.getElementById('settingsPage');
    const settingsLink = document.getElementById('settingsLink');
    const backToMainLink = document.getElementById('backToMainLink');
    const newProjectBtn = document.getElementById('newProjectBtn');
    const projectsList = document.getElementById('projectsList');
    const chatInterface = document.getElementById('chatInterface');
    const chatHistory = document.getElementById('chatHistory');
    const chatForm = document.getElementById('chatForm');
    const chatInput = document.getElementById('chatInput');
    const buildStatus = document.getElementById('buildStatus');
    const tabbedViewer = document.getElementById('tabbedViewer');
    const tabsContainer = tabbedViewer.querySelector('.tabs');
    const tabContent = tabbedViewer.querySelector('.tab-content');

    let currentProjectId = null;
    let ws = null;
    const API_BASE_URL = `${window.location.protocol}//${window.location.host}`;

    // Navigation
    settingsLink.addEventListener('click', (e) => {
        e.preventDefault();
        mainPage.style.display = 'none';
        settingsPage.style.display = 'block';
        loadSettings();
    });

    backToMainLink.addEventListener('click', (e) => {
        e.preventDefault();
        settingsPage.style.display = 'none';
        mainPage.style.display = 'block';
    });

    // Project Management
    async function loadProjects() {
        const response = await fetch(`${API_BASE_URL}/api/projects`);
        const projects = await response.json();
        projectsList.innerHTML = '';
        projects.forEach(project => {
            const li = document.createElement('li');
            li.textContent = project.name;
            li.addEventListener('click', () => openProject(project.id));
            projectsList.appendChild(li);
        });
    }

    newProjectBtn.addEventListener('click', async () => {
        const response = await fetch(`${API_BASE_URL}/api/projects`, { method: 'POST' });
        const data = await response.json();
        currentProjectId = data.project_id;
        connectWebSocket(currentProjectId);
        chatInterface.style.display = 'block';
        chatHistory.innerHTML = '';
        appendMessage('pm', 'Hello! Please describe the project requirements.');
    });

    async function openProject(projectId) {
        currentProjectId = projectId;
        connectWebSocket(projectId);
        chatInterface.style.display = 'block';
        // Load chat history from API
        const response = await fetch(`${API_BASE_URL}/api/projects/${projectId}/chat`);
        const history = await response.json();
        chatHistory.innerHTML = '';
        history.forEach(msg => appendMessage(msg.role, msg.content));
    }

    // Chat and Build
    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const message = chatInput.value.trim();
        if (!message) return;
        appendMessage('user', message);
        chatInput.value = '';

        const response = await fetch(`${API_BASE_URL}/api/projects/${currentProjectId}/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message }),
        });
        const data = await response.json();
        appendMessage('pm', data.response);
        if (data.status === 'ready') {
            // Start build
            buildStatus.style.display = 'block';
            buildStatus.innerHTML = getInitialStatusHTML();
        }
    });

    function appendMessage(role, content) {
        const div = document.createElement('div');
        div.classList.add('chat-message', `${role}-message`);
        div.textContent = content;
        chatHistory.appendChild(div);
        chatHistory.scrollTop = chatHistory.scrollHeight;
    }

    // WebSocket for real-time updates (from Gemini, enhanced)
    function connectWebSocket(projectId) {
        const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        ws = new WebSocket(`${wsProtocol}//${window.location.host}/ws/project/${projectId}`);
        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (data.type === 'chat') {
                appendMessage('pm', data.content);
            } else if (data.type === 'progress') {
                updateBuildStatus(data);
            } else if (data.type === 'final_output') {
                handleFinalOutput(data.output);
            }
            // Handle tab updates for artifacts
            if (data.type === 'artifact') {
                addTab(data.file, data.content);
            }
        };
    }

    function updateBuildStatus(data) {
        // From Gemini, with enhancements
        // ...
    }

    function handleFinalOutput(output) {
        // From Gemini
        // ...
    }

    // Tabbed Viewer
    function addTab(filename, content) {
        const tab = document.createElement('div');
        tab.classList.add('tab');
        tab.textContent = filename;
        tab.addEventListener('click', () => {
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            tabContent.innerHTML = `<pre>${content}</pre>`;
        });
        tabsContainer.appendChild(tab);
        tabbedViewer.style.display = 'block';
    }

    // Settings (from Gemini)
    // ...

    // Initial Load
    loadProjects();
});
```

## File: `blueprint/src/main.py`

```python
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from blueprint.src.api.routes import router as api_router
from blueprint.src.api.websocket import router as ws_router
from blueprint.src.storage.database import initialize_db
from blueprint.src.config.settings import settings
from blueprint.src.setup.bootstrap import bootstrap

# Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Blueprint v2.0.1...")
    Path(settings.output.path).mkdir(exist_ok=True)
    await initialize_db()
    await bootstrap()  # First-run setup
    yield
    logger.info("Shutting down.")

app = FastAPI(title="Blueprint v2.0.1", lifespan=lifespan)

# Routers
app.include_router(api_router, prefix="/api")
app.include_router(ws_router)

# Static Files
app.mount("/", StaticFiles(directory="blueprint/frontend", html=True), name="frontend")
app.mount("/projects-static", StaticFiles(directory=settings.output.path), name="projects-static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("blueprint.src.main:app", host="0.0.0.0", port=8000, reload=True)
```

## File: `blueprint/src/api/routes.py`

```python
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel

from blueprint.src.workflow.orchestrator import build_manager
from blueprint.src.storage.database import get_recent_builds
from blueprint.src.config.settings import update_settings, get_full_config

router = APIRouter()

class BuildRequest(BaseModel):
    prompt: str

# Routes from Gemini, with additions for projects and chat
@router.post("/projects")
async def create_project():
    # Create new project
    return {"project_id": "new_id"}  # Placeholder

@router.get("/projects")
async def list_projects():
    return get_recent_builds()  # Reuse as projects

@router.post("/projects/{project_id}/chat")
async def project_chat(project_id: str, request: dict):
    message = request['message']
    # Handle PM conversation
    return {"response": "PM response", "status": "gathering"}  # Placeholder

@router.post("/builds")
async def start_build(request: BuildRequest, background_tasks: BackgroundTasks):
    # From Gemini
    build_id = build_manager.create_build(request.prompt)
    background_tasks.add_task(build_manager.run_build, build_id)
    return {"build_id": build_id}

# Config routes from Gemini
# ...
```

## File: `blueprint/src/api/websocket.py`

```python
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from blueprint.src.workflow.orchestrator import build_manager

router = APIRouter()

@router.websocket("/ws/project/{project_id}")
async def websocket_endpoint(websocket: WebSocket, project_id: str):
    await build_manager.register_websocket(project_id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        build_manager.unregister_websocket(project_id, websocket)
```

## File: `blueprint/src/config/settings.py`

```python
# From Gemini, with additions for local models and bootstrap
import yaml
import os
import re
from pydantic import BaseModel, Field
from typing import List, Optional
from dotenv import load_dotenv

class Settings(BaseModel):
    # From Gemini, enhanced
    # ...

def load_settings():
    # From Gemini
    # ...

# Update function from Gemini
# ...
```

## File: `blueprint/src/llm/client.py`

```python
# From Gemini, with additions for local Ollama stub
from openai import AsyncOpenAI
import google.generativeai as genai
import anthropic
from tenacity import retry, stop_after_attempt, wait_exponential

class LLMClient:
    # From Gemini, add Ollama support
    def __init__(self, provider: str, api_key: Optional[str] = None):
        if provider == "ollama":
            # Stub for local
            pass
        # Rest from Gemini

    @retry(...)
    async def generate(self, model: str, system_prompt: str, user_prompt: str):
        # From Gemini
        # ...
```

## File: `blueprint/src/setup/bootstrap.py`

```python
import asyncio

async def bootstrap():
    # First-run: Download minimal local model if no keys, guide user for keys
    from blueprint.src.config.settings import settings
    if not any(settings.api_keys.dict().values()):
        # Download via Ollama or HuggingFace
        logger.info("Bootstrapping local model...")
        # Stub: os.system("ollama pull qwen2.5:1.5b")
        # Conversational setup with user via console or UI
```

## File: `blueprint/src/storage/database.py`

```python
# From Gemini, with additions for project chat history
import aiosqlite

# Functions from Gemini
# Add:
async def save_chat_message(project_id: str, role: str, content: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT INTO chat_history (project_id, role, content) VALUES (?, ?, ?)", (project_id, role, content))
        await db.commit()

async def get_chat_history(project_id: str):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT role, content FROM chat_history WHERE project_id = ? ORDER BY timestamp", (project_id,)) as cursor:
            return await cursor.fetchall()
```

## File: `blueprint/src/storage/filesystem.py`

```python
# From Gemini, unchanged
# ...
```

## File: `blueprint/src/workflow/orchestrator.py`

```python
# Synthesized from Gemini (phases) and Grok (FSM)
import asyncio
from enum import Enum
from blueprint.src.config.settings import settings
from blueprint.src.storage import database, filesystem
from blueprint.src.llm.client import LLMClient

class State(Enum):
    GATHER_REQUIREMENTS = 1
    GENESIS = 2
    SYNTHESIS = 3
    REVIEW = 4
    OUTPUT = 5
    COMPLETE = 6

class Build:
    # From Gemini, with state
    def __init__(self, build_id: str, prompt: str):
        self.id = build_id
        self.prompt = prompt
        self.state = State.GATHER_REQUIREMENTS
        self.conversation = []
        self.websockets = set()
        # ...

class BuildManager:
    # From Gemini, with FSM logic from Grok
    async def run_build(self, build_id: str):
        build = self.active_builds[build_id]
        while build.state != State.COMPLETE:
            if build.state == State.GATHER_REQUIREMENTS:
                await self.gather_requirements(build)
            elif build.state == State.GENESIS:
                await run_genesis_phase(build)  # Multi-round
            elif build.state == State.SYNTHESIS:
                await run_synthesis_phase(build)
            elif build.state == State.REVIEW:
                if not await run_review_phase(build):
                    build.state = State.SYNTHESIS  # Loop
                else:
                    build.state = State.OUTPUT
            elif build.state == State.OUTPUT:
                await run_output_phase(build)
                build.state = State.COMPLETE

    async def gather_requirements(self, build):
        # Conversational with PM LLM
        # Use WebSocket for user interaction
        # When ready, generate anchor context, set state to GENESIS

# Phase functions from Gemini, enhanced for multi-round and review loop
async def run_genesis_phase(build):
    for round in range(settings.workflow.genesis_rounds):
        # Invoke juniors with cross-pollination if round > 0
        # ...

async def run_review_phase(build):
    # Invoke juniors for scores
    # Check threshold
    # Return True if consensus reached
    # ...
```

## File: `blueprint/src/workflow/phases.py`

```python
# Detailed phase implementations from Gemini, with multi-round and loop
# ...
```

## File: `Dockerfile`

```dockerfile
# From Gemini, with Ollama for bootstrap
FROM python:3.11-slim

# Install Ollama for local models
RUN apt-get update && apt-get install -y curl && curl https://ollama.ai/install.sh | sh

# Rest from Gemini
# ...
```

## File: `docker-compose.yml`

```yaml
# From Gemini
# ...
```

## File: `install.sh`

```bash
#!/bin/bash
# From Gemini, with bootstrap check
# ...
```

## File: `tests/test_workflow.py`

```python
# Comprehensive tests from Gemini and Grok
# Include hello world and requirements doc tests
# ...
```
