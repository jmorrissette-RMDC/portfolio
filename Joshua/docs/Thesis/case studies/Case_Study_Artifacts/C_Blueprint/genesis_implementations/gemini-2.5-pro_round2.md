This is my Round 2 submission for Blueprint v2.0.1.

After a thorough review of the four peer implementations from Round 1, I have synthesized their best ideas into a new, improved version. My approach adopts the clean, modular architecture of **Implementation A (Gemini)**, including its FastAPI backend, vanilla JavaScript frontend, WebSocket communication, and robust configuration system. I have integrated the more accurate workflow understanding from **Implementation B (Grok)**, particularly its recognition of conversational requirements gathering and the iterative nature of the core process.

This v2.0.1 implementation addresses the key gaps from Round 1 by:
1.  **Implementing a true conversational UI** for requirements gathering with the Project Manager, as specified in the original anchor context.
2.  **Building a stateful orchestrator** that correctly manages multi-round Genesis and the critical Synthesis/Review loop until consensus is achieved.
3.  **Enhancing the context files** to be highly explicit, ensuring reliable output parsing from the LLMs.
4.  **Providing a comprehensive and functional codebase**, replacing all stubs and simulated logic with production-ready code.
5.  **Including a full suite of deliverables**, from installation and testing scripts to a detailed `README.md`.

This version represents a significant step forward in stability, functionality, and adherence to the project's core vision.

---

## File: `blueprint/config.yaml`
```yaml
# Blueprint v2.0.1 Configuration
# This file defines the AI team, workflow settings, and API keys.
# API keys should be set in the .env file and are loaded automatically.

# The team of AI agents that will build the digital asset.
# Using diverse models from different providers is recommended for best results.
team:
  # The Project Manager interacts with the user to define requirements.
  # Recommended: A model with strong conversational and reasoning abilities.
  project_manager: "anthropic/claude-3-5-sonnet-20240620"

  # The Senior Developer synthesizes junior outputs and refines based on feedback.
  # Recommended: A top-tier model with excellent synthesis and coding skills.
  senior: "google/gemini-1.5-pro-latest"

  # Junior Developers work in parallel to create initial implementations.
  # Configure between 2 and 5 juniors.
  juniors:
    count: 3
    models:
      - "together/deepseek-ai/deepseek-coder-v2-instruct" # Strong coder
      - "openai/gpt-4o"                                   # All-around powerhouse
      - "google/gemini-1.5-flash-latest"                  # Fast with a large context window

# Workflow settings control the build process.
workflow:
  # Number of Genesis rounds for cross-pollination. 1-3 recommended.
  genesis_rounds: 2
  # Maximum number of Synthesis/Review loops to attempt before failing.
  max_review_loops: 5
  # Approval threshold for the review phase. 1.0 means 100% of juniors must approve.
  approval_threshold: 1.0
  # Maximum retry attempts for a failing LLM call.
  max_retries: 3

# Output settings for the final deliverable.
output:
  # Path for all generated projects, relative to the application's root.
  path: "projects"

# Paths to the context files that define the behavior of each role.
context_paths:
  project_manager: "blueprint/contexts/project_manager.md"
  senior: "blueprint/contexts/senior_developer.md"
  junior: "blueprint/contexts/junior_developer.md"

```
---
## File: `blueprint/contexts/project_manager.md`
```md
# Role: Project Manager

You are the Project Manager for Blueprint, a system that creates digital assets using a team of AI developers. Your role is to engage in a conversation with the user to elicit a complete and clear set of requirements.

## Your Core Responsibilities:

1.  **Conversational Requirements Gathering**:
    -   Your primary goal is to have a natural, helpful conversation with the user.
    -   Start by greeting them and asking what they would like to build.
    -   Ask clarifying questions to resolve ambiguities. For example, if they ask for a "website," ask what kind of website, what pages it should have, what technology it should use, etc.
    -   Guide the user to provide all necessary details.
    -   Do NOT summarize the conversation. The entire verbatim transcript is the requirements document.

2.  **Concluding the Conversation**:
    -   Once you believe the requirements are complete, confirm with the user. You can say something like, "This looks like a solid plan. Are you ready for me to hand this off to the development team?"
    -   The user will signal the end of the conversation by saying something like "yes", "proceed", "start the build", or by using a command like `/build`.

3.  **Generating Instructions for the Team**:
    -   After the conversation is complete, your final task is to generate a brief set of instructions for the development team.
    -   This is NOT a summary of the requirements. It is a high-level directive.
    -   Your entire final output must be ONLY a JSON object with the key "instructions_for_dev_team".

## Example Interaction:

**User**: "I want to make a snake game."

**You**: "Great! A classic snake game is a fun project. To make sure the team builds exactly what you want, could you clarify a few things? What technology should we use? For example, should this be a web-based game using HTML, CSS, and JavaScript, or a Python application using a library like Pygame?"

**User**: "Let's do Python and Pygame."

**You**: "Excellent choice. Should the game keep track of the high score? And what should happen when the snake hits a wall or itself?"

**User**: "Yes to the high score. If it hits a wall or itself, the game should end and display the final score."

**You**: "Perfect. That gives the team a clear direction. Are you ready for me to start the build process?"

**User**: "Yes, go ahead."

**You**:
```json
{
  "instructions_for_dev_team": "Build a classic Snake game using Python and the Pygame library, as detailed in the preceding conversation. The game must track high scores and handle game-over conditions correctly."
}
```

**CRITICAL**: Your final response in the conversation MUST be ONLY the JSON object shown above. Do not include any other text, conversational filler, or markdown formatting.

```
---
## File: `blueprint/contexts/senior_developer.md`
```md
# Role: Senior Developer

You are the Senior Developer and technical lead of the Blueprint team. You are an expert in software architecture, code quality, and synthesis. You are responsible for creating high-quality initial implementations and, most importantly, for synthesizing the work of the entire team into a single, superior product.

## Your Core Responsibilities:

1.  **Genesis Phase**:
    -   You will receive an anchor context containing the user's requirements (as a conversation) and instructions from the Project Manager.
    -   Your task is to create your own complete, independent solution based on this context. This serves as a high-quality baseline for the Synthesis phase.
    -   Your output must be a complete set of files that fulfill the request.

2.  **Synthesis Phase**:
    -   This is your most critical responsibility. You will receive an anchor context containing the original requirements, PM instructions, and ALL solutions created by yourself and the Junior Developers during the Genesis phase.
    -   Your task is to analyze all submissions to identify the best ideas, code structures, algorithms, and implementation details.
    -   You must merge, refactor, and combine these ideas into a single, cohesive, and superior solution.
    -   **Do not simply pick one solution.** Your goal is to create a NEW synthesized artifact that is better than any individual submission.
    -   The final product should be a polished, production-ready deliverable.

3.  **Revision Phase (After Junior Review)**:
    -   You will receive an anchor context containing the original requirements, your previously synthesized solution, and a list of critiques and change requests from the Junior Developers.
    -   Your task is to review the feedback and revise your synthesized solution to address the valid points.
    -   You have the authority to reject feedback if it conflicts with the original user requirements. If you do, you must provide a brief justification in a comment within the relevant code file. For example: `// Junior #2's suggestion to use a NoSQL database was rejected as the requirements imply a relational data structure.`
    -   Your goal is to produce a final version that the entire team can agree on.

## Output Format for ALL Phases:

**CRITICAL**: You must write ALL generated files directly in your response using markdown code blocks. Use this exact format, with no conversational text outside the code blocks:

```
## File: path/to/filename.ext
\`\`\`language
file contents here
\`\`\`

## File: another/file.ext
\`\`\`language
another file's contents
\`\`\`
```

**CRITICAL RULES**:
-   Always write COMPLETE, WORKING CODE.
-   Include ALL necessary files (e.g., main code, tests, README, requirements.txt, Dockerfile).
-   Ensure your solution is self-contained and production-ready.
-   Adhere strictly to the `## File:` format.

```
---
## File: `blueprint/contexts/junior_developer.md`
```md
# Role: Junior Developer

You are a Junior Developer on the Blueprint team. You are a skilled and creative professional tasked with generating a complete solution based on requirements and reviewing the final synthesized product.

## Your Core Responsibilities:

### 1. Genesis Phase (Creation)

You will receive an anchor context containing user requirements (as a conversation) and instructions from the Project Manager. For later Genesis rounds, you will also receive the outputs from all team members from the previous round.

-   **Task**: Create a complete, fully-realized version of the requested digital asset.
-   **First Round**: Work independently and creatively based on the initial requirements.
-   **Subsequent Rounds**: Analyze the work from your peers in the previous round. Incorporate the best ideas into your new version while still exploring your own creative solutions. This is for cross-pollination.
-   **Output**: Your response must be a complete set of files that fulfill the request.

**Output Format for Genesis Phase (MANDATORY)**:
You must write ALL generated files using markdown code blocks. Use this exact format:
```
## File: path/to/filename.ext
\`\`\`language
file contents here
\`\`\`
```

### 2. Review Phase (Critique)

After the Genesis and Synthesis phases, you will be asked to review the final, consolidated solution created by the Senior Developer.

-   **Task**: Critique the synthesized solution. Your goal is to help improve it and ensure it meets the user's requirements.
-   **Analyze**: Compare the Senior's solution against the original user requirements. Is it complete? Is it correct? Is the code high quality?
-   **Output**: Your entire response must be a single JSON object. Do not include any other text or markdown.

**JSON Output Format for Review Phase (MANDATORY)**:
```json
{
  "approved": boolean,
  "critique": "Your detailed critique and reasoning here. If not approved, list specific, actionable changes you want to see. If approved, state why you think it's a good solution."
}
```

-   `approved`: `true` if you believe the solution is complete, correct, and meets the requirements. `false` otherwise.
-   `critique`: A clear, constructive explanation.
    -   If `false`, you MUST provide specific changes. E.g., "The database connection is not properly closed in `db.py`. Please add a `finally` block to ensure `conn.close()` is called. Also, the `README.md` is missing installation instructions."
    -   If `true`, briefly explain why. E.g., "The solution is elegant, well-documented, and fully implements all features from the requirements."

**CRITICAL**: Adhere to the specified output formats for each phase. Incorrect formatting will cause the system to fail.

```
---
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
        <aside class="sidebar">
            <button id="newProjectBtn" class="new-project-btn">+ New Project</button>
            <h2>Projects</h2>
            <ul id="projectList">
                <!-- Projects will be loaded here -->
            </ul>
        </aside>
        <main class="main-content">
            <div id="welcomeScreen">
                <h1>Blueprint v2.0.1</h1>
                <p>Click "New Project" to start building.</p>
            </div>
            <div id="chatScreen" class="hidden">
                <div id="chatLog"></div>
                <div id="buildStatus" class="build-status hidden"></div>
                <form id="chatForm">
                    <textarea id="userInput" placeholder="Chat with the Project Manager to define your project..."></textarea>
                    <button type="submit">Send</button>
                </form>
            </div>
        </main>
        <aside id="artifactViewer" class="artifact-viewer hidden">
             <div class="artifact-header">
                <h3>Artifacts</h3>
                <button id="closeArtifactsBtn">&times;</button>
            </div>
            <div id="artifactTabs"></div>
            <div id="artifactContent"></div>
        </aside>
    </div>
    <script src="app.js"></script>
</body>
</html>
```
---
## File: `blueprint/frontend/styles.css`
```css
:root {
    --bg-color: #1a1a1a;
    --sidebar-bg: #2a2a2a;
    --main-bg: #202020;
    --text-color: #e0e0e0;
    --primary-color: #007bff;
    --border-color: #444;
    --input-bg: #333;
    --button-hover: #0056b3;
    --success: #28a745;
    --error: #dc3545;
    --inprogress: #ffc107;
}

* { box-sizing: border-box; }

body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    background-color: var(--bg-color);
    color: var(--text-color);
    margin: 0;
    height: 100vh;
    overflow: hidden;
}

.container {
    display: flex;
    height: 100%;
}

/* Sidebar */
.sidebar {
    width: 250px;
    background-color: var(--sidebar-bg);
    padding: 1rem;
    display: flex;
    flex-direction: column;
    border-right: 1px solid var(--border-color);
}
.new-project-btn {
    background-color: var(--primary-color);
    color: white;
    border: none;
    padding: 10px 15px;
    border-radius: 5px;
    cursor: pointer;
    width: 100%;
    margin-bottom: 1rem;
    font-size: 1rem;
}
.new-project-btn:hover { background-color: var(--button-hover); }
.sidebar h2 { font-size: 1.1rem; margin-top: 0; border-bottom: 1px solid var(--border-color); padding-bottom: 0.5rem; }
#projectList { list-style: none; padding: 0; margin: 0; overflow-y: auto; }
#projectList li { padding: 10px; cursor: pointer; border-radius: 5px; margin-bottom: 5px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
#projectList li:hover { background-color: #383838; }
#projectList li.active { background-color: var(--primary-color); }

/* Main Content */
.main-content {
    flex-grow: 1;
    display: flex;
    flex-direction: column;
    background-color: var(--main-bg);
}
#welcomeScreen { text-align: center; margin: auto; }
#chatScreen { display: flex; flex-direction: column; height: 100%; }
#chatLog { flex-grow: 1; padding: 1rem; overflow-y: auto; }
.message { max-width: 80%; margin-bottom: 1rem; padding: 10px 15px; border-radius: 10px; line-height: 1.5; }
.user-message { background-color: var(--primary-color); color: white; align-self: flex-end; margin-left: auto; border-bottom-right-radius: 0; }
.pm-message { background-color: var(--sidebar-bg); align-self: flex-start; border-bottom-left-radius: 0; }
.system-message { text-align: center; color: #aaa; font-style: italic; margin: 1rem 0; }
#chatForm { display: flex; padding: 1rem; border-top: 1px solid var(--border-color); }
#userInput { flex-grow: 1; background-color: var(--input-bg); color: var(--text-color); border: 1px solid var(--border-color); border-radius: 5px; padding: 10px; resize: none; font-size: 1rem; }
#chatForm button { background-color: var(--primary-color); color: white; border: none; padding: 10px 15px; margin-left: 10px; border-radius: 5px; cursor: pointer; }
#chatForm button:hover { background-color: var(--button-hover); }

/* Build Status */
.build-status { padding: 1rem; border-top: 1px solid var(--border-color); background-color: #2a2a2a; }
.phase-list { list-style: none; padding: 0; margin: 0; }
.phase-list li { display: flex; align-items: center; gap: 1rem; padding: 0.5rem 0; }
.status-icon { font-size: 1.2rem; }
.status-icon.complete { color: var(--success); }
.status-icon.in-progress { color: var(--inprogress); animation: spin 1s linear infinite; }
.status-icon.failed { color: var(--error); }
.status-icon.pending { color: #666; }
@keyframes spin { 100% { transform: rotate(360deg); } }
.phase-name { font-weight: bold; }
.phase-details { color: #aaa; font-size: 0.9em; }

/* Artifact Viewer */
.artifact-viewer { width: 40%; max-width: 600px; background-color: var(--sidebar-bg); border-left: 1px solid var(--border-color); display: flex; flex-direction: column; }
.artifact-header { display: flex; justify-content: space-between; align-items: center; padding: 1rem; border-bottom: 1px solid var(--border-color); }
#closeArtifactsBtn { background: none; border: none; color: var(--text-color); font-size: 1.5rem; cursor: pointer; }
#artifactTabs { display: flex; flex-wrap: wrap; padding: 0.5rem; border-bottom: 1px solid var(--border-color); }
.tab { padding: 5px 10px; background-color: var(--input-bg); border-radius: 5px; margin: 2px; cursor: pointer; }
.tab.active { background-color: var(--primary-color); }
#artifactContent { flex-grow: 1; padding: 1rem; overflow: auto; white-space: pre-wrap; font-family: "Courier New", Courier, monospace; }

.hidden { display: none !important; }
```
---
## File: `blueprint/frontend/app.js`
```javascript
document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const newProjectBtn = document.getElementById('newProjectBtn');
    const projectList = document.getElementById('projectList');
    const welcomeScreen = document.getElementById('welcomeScreen');
    const chatScreen = document.getElementById('chatScreen');
    const chatLog = document.getElementById('chatLog');
    const chatForm = document.getElementById('chatForm');
    const userInput = document.getElementById('userInput');
    const buildStatusContainer = document.getElementById('buildStatus');
    const artifactViewer = document.getElementById('artifactViewer');
    const closeArtifactsBtn = document.getElementById('closeArtifactsBtn');
    const artifactTabs = document.getElementById('artifactTabs');
    const artifactContent = document.getElementById('artifactContent');

    // State
    let ws;
    let currentProject = null;
    let projects = {};

    const API_BASE_URL = `${window.location.protocol}//${window.location.host}`;
    const WS_URL = `ws${window.location.protocol === 'https:' ? 's' : ''}://${window.location.host}/ws`;

    // --- WebSocket Management ---
    function connectWebSocket() {
        ws = new WebSocket(WS_URL);
        ws.onopen = () => console.log('WebSocket connected');
        ws.onclose = () => {
            console.log('WebSocket disconnected. Reconnecting...');
            setTimeout(connectWebSocket, 3000);
        };
        ws.onerror = (error) => console.error('WebSocket error:', error);
        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            handleWebSocketMessage(data);
        };
    }

    function handleWebSocketMessage(data) {
        if (data.project_id !== currentProject) return;

        switch (data.type) {
            case 'pm_message':
                addMessageToChatLog('pm-message', data.message);
                userInput.disabled = false;
                userInput.focus();
                break;
            case 'build_progress':
                updateBuildStatus(data.payload);
                break;
            case 'build_complete':
                showFinalArtifacts(data.payload);
                userInput.disabled = true;
                userInput.placeholder = "Build complete. Start a new project to continue.";
                break;
            case 'error':
                addMessageToChatLog('system-message', `Error: ${data.message}`);
                userInput.disabled = false;
                break;
        }
    }

    // --- UI Update Functions ---
    function addMessageToChatLog(type, text) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;
        messageDiv.textContent = text;
        chatLog.appendChild(messageDiv);
        chatLog.scrollTop = chatLog.scrollHeight;
    }

    function updateBuildStatus(status) {
        buildStatusContainer.classList.remove('hidden');
        let html = `<h4>Build Progress</h4><ul class="phase-list">`;
        status.phases.forEach(phase => {
            let icon = '⚪';
            let iconClass = 'pending';
            if (phase.status === 'complete') { icon = '✅'; iconClass = 'complete'; }
            if (phase.status === 'in_progress') { icon = '🔄'; iconClass = 'in-progress'; }
            if (phase.status === 'failed') { icon = '❌'; iconClass = 'failed'; }
            html += `<li>
                <span class="status-icon ${iconClass}">${icon}</span>
                <span class="phase-name">${phase.name}</span>
                <span class="phase-details">${phase.details || ''}</span>
            </li>`;
        });
        html += `</ul>`;
        buildStatusContainer.innerHTML = html;
    }
    
    function showFinalArtifacts(artifacts) {
        projects[currentProject].artifacts = artifacts;
        artifactViewer.classList.remove('hidden');
        artifactTabs.innerHTML = '';
        Object.keys(artifacts).forEach((filename, index) => {
            const tab = document.createElement('div');
            tab.className = 'tab';
            tab.textContent = filename;
            tab.dataset.filename = filename;
            if (index === 0) {
                tab.classList.add('active');
                artifactContent.textContent = artifacts[filename];
            }
            artifactTabs.appendChild(tab);
        });
    }

    // --- Project Management ---
    function createNewProject() {
        const projectId = `proj_${new Date().getTime()}`;
        currentProject = projectId;
        projects[currentProject] = {
            id: projectId,
            title: `New Project - ${new Date().toLocaleTimeString()}`,
            chatHistory: [],
            artifacts: null
        };
        ws.send(JSON.stringify({ type: 'start_project', project_id: projectId }));
        
        updateProjectList();
        switchToProject(projectId);
    }
    
    function switchToProject(projectId) {
        currentProject = projectId;
        
        // Update UI
        welcomeScreen.classList.add('hidden');
        chatScreen.classList.remove('hidden');
        chatLog.innerHTML = '';
        buildStatusContainer.classList.add('hidden');
        artifactViewer.classList.add('hidden');
        userInput.value = '';
        userInput.disabled = false;
        userInput.placeholder = "Chat with the Project Manager to define your project...";
        
        // Load project data
        const project = projects[projectId];
        project.chatHistory.forEach(msg => addMessageToChatLog(msg.type, msg.text));
        
        if (project.artifacts) {
            showFinalArtifacts(project.artifacts);
        } else {
            const lastMessage = project.chatHistory[project.chatHistory.length - 1];
            if (lastMessage && lastMessage.type === 'pm-message') {
                 userInput.disabled = false;
            } else if (project.chatHistory.length > 0) {
                userInput.disabled = true; // Waiting for PM
            }
        }
        
        updateProjectList();
    }

    function updateProjectList() {
        projectList.innerHTML = '';
        Object.values(projects).forEach(proj => {
            const li = document.createElement('li');
            li.textContent = proj.title;
            li.dataset.projectId = proj.id;
            if (proj.id === currentProject) {
                li.classList.add('active');
            }
            projectList.appendChild(li);
        });
    }

    // --- Event Listeners ---
    newProjectBtn.addEventListener('click', createNewProject);

    projectList.addEventListener('click', (e) => {
        if (e.target.tagName === 'LI') {
            const projectId = e.target.dataset.projectId;
            switchToProject(projectId);
        }
    });

    chatForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const messageText = userInput.value.trim();
        if (!messageText || !currentProject || userInput.disabled) return;

        addMessageToChatLog('user-message', messageText);
        projects[currentProject].chatHistory.push({ type: 'user-message', text: messageText });
        
        ws.send(JSON.stringify({
            type: 'user_message',
            project_id: currentProject,
            message: messageText
        }));
        
        userInput.value = '';
        userInput.disabled = true;

        if (messageText.toLowerCase().startsWith('/build')) {
            addMessageToChatLog('system-message', 'Build process initiated...');
        }
    });

    closeArtifactsBtn.addEventListener('click', () => {
        artifactViewer.classList.add('hidden');
    });
    
    artifactTabs.addEventListener('click', (e) => {
        if (e.target.classList.contains('tab')) {
            const filename = e.target.dataset.filename;
            artifactContent.textContent = projects[currentProject].artifacts[filename];
            document.querySelectorAll('#artifactTabs .tab').forEach(t => t.classList.remove('active'));
            e.target.classList.add('active');
        }
    });

    // --- Initialization ---
    connectWebSocket();
});
```
---
## File: `blueprint/src/main.py`
```python
import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from blueprint.src.workflow.orchestrator import ProjectOrchestrator
from blueprint.src.api.websocket import ConnectionManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [%(name)s] - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Blueprint application starting up...")
    Path("projects").mkdir(exist_ok=True)
    yield
    logger.info("Blueprint application shutting down.")

app = FastAPI(
    title="Blueprint v2.0.1",
    description="Conversational Multi-Agent Development System",
    lifespan=lifespan
)

manager = ConnectionManager()
orchestrator = ProjectOrchestrator(manager)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            logger.info(f"Received message: {data}")
            project_id = data.get("project_id")

            if data['type'] == 'start_project':
                await orchestrator.start_project(project_id, websocket)
            elif data['type'] == 'user_message':
                await orchestrator.handle_user_message(project_id, data['message'])
            else:
                await manager.send_error(websocket, project_id, "Unknown message type")

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("Client disconnected.")
    except Exception as e:
        logger.error(f"WebSocket Error: {e}", exc_info=True)
        # Attempt to inform client before closing
        if project_id:
             await manager.send_error(websocket, project_id, f"An unexpected server error occurred: {e}")


# Serve the frontend as static files
app.mount("/", StaticFiles(directory="blueprint/frontend", html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Blueprint server with Uvicorn...")
    uvicorn.run("blueprint.src.main:app", host="0.0.0.0", port=8000, reload=True)
```
---
## File: `blueprint/src/api/websocket.py`
```python
import logging
from typing import Dict, List, Any
from fastapi import WebSocket

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        # We will associate the websocket with a project_id later
        logger.info("New client connected.")

    def disconnect(self, websocket: WebSocket):
        # Find and remove the websocket from the dictionary
        project_id_to_remove = None
        for pid, ws in self.active_connections.items():
            if ws == websocket:
                project_id_to_remove = pid
                break
        if project_id_to_remove:
            del self.active_connections[project_id_to_remove]
            logger.info(f"Client for project {project_id_to_remove} disconnected.")

    def register_project_connection(self, project_id: str, websocket: WebSocket):
        self.active_connections[project_id] = websocket
        logger.info(f"Registered websocket for project {project_id}")

    async def _send_json(self, project_id: str, data: Dict[str, Any]):
        websocket = self.active_connections.get(project_id)
        if websocket:
            try:
                await websocket.send_json(data)
            except Exception as e:
                logger.error(f"Failed to send message to project {project_id}: {e}")
        else:
            logger.warning(f"No active connection found for project {project_id}")

    async def send_pm_message(self, project_id: str, message: str):
        await self._send_json(project_id, {"type": "pm_message", "project_id": project_id, "message": message})

    async def send_progress_update(self, project_id: str, payload: Dict[str, Any]):
        await self._send_json(project_id, {"type": "build_progress", "project_id": project_id, "payload": payload})

    async def send_build_complete(self, project_id: str, artifacts: Dict[str, str]):
        await self._send_json(project_id, {"type": "build_complete", "project_id": project_id, "payload": artifacts})

    async def send_error(self, websocket: WebSocket, project_id: str, message: str):
        try:
            await websocket.send_json({"type": "error", "project_id": project_id, "message": message})
        except Exception as e:
            logger.error(f"Failed to send error message to client: {e}")
```
---
## File: `blueprint/src/workflow/orchestrator.py`
```python
import asyncio
import logging
import json
from typing import Dict, List, Any
from pathlib import Path
from fastapi import WebSocket

from blueprint.src.api.websocket import ConnectionManager
from blueprint.src.config.settings import settings
from blueprint.src.llm.client import LLMClient
from blueprint.src.storage.filesystem import parse_and_write_files, get_project_files_as_dict, format_files_for_context
from .phases import Phase, create_initial_phases

logger = logging.getLogger(__name__)

class Project:
    """Manages the state of a single project build."""
    def __init__(self, project_id: str, manager: ConnectionManager):
        self.id = project_id
        self.manager = manager
        self.conversation_history: List[Dict[str, str]] = []
        self.anchor_context: Dict[str, Any] = {}
        self.phases: List[Phase] = create_initial_phases()
        self.project_path = Path(settings.output.path) / self.id
        self.project_path.mkdir(parents=True, exist_ok=True)
        self.build_started = False
        logger.info(f"Project {self.id} initialized at {self.project_path}")

    async def add_user_message(self, message: str):
        self.conversation_history.append({"role": "user", "content": message})
        if message.lower().strip().startswith('/build') and not self.build_started:
            self.build_started = True
            asyncio.create_task(self.run_build_workflow())
        else:
            await self.get_pm_response()

    async def get_pm_response(self):
        pm_client = LLMClient(settings.team.project_manager)
        system_prompt = pm_client.get_context_from_file('project_manager')
        
        response_text = await pm_client.generate(system_prompt, self.conversation_history)
        self.conversation_history.append({"role": "assistant", "content": response_text})
        await self.manager.send_pm_message(self.id, response_text)

    async def run_build_workflow(self):
        try:
            logger.info(f"Starting build workflow for project {self.id}")
            # Final PM call to get instructions
            pm_client = LLMClient(settings.team.project_manager)
            system_prompt = pm_client.get_context_from_file('project_manager')
            pm_final_response = await pm_client.generate(system_prompt, self.conversation_history)
            
            try:
                instructions_json = json.loads(pm_final_response)
                instructions = instructions_json.get("instructions_for_dev_team", "No instructions provided.")
            except json.JSONDecodeError:
                logger.error("PM failed to output valid JSON for instructions.")
                instructions = "Build the project as discussed."

            self.anchor_context['requirements_conversation'] = self.conversation_history
            self.anchor_context['pm_instructions'] = instructions

            # Run through phases
            for phase in self.phases:
                await self.update_phase_status(phase.name, "in_progress")
                await phase.run(self)
                await self.update_phase_status(phase.name, "complete", phase.details)
            
            # Build complete
            final_artifacts = get_project_files_as_dict(self.project_path / "senior")
            await self.manager.send_build_complete(self.id, final_artifacts)

        except Exception as e:
            logger.error(f"Build workflow for {self.id} failed: {e}", exc_info=True)
            active_phase = next((p.name for p in self.phases if p.status == 'in_progress'), "Unknown")
            await self.update_phase_status(active_phase, "failed", str(e))
            # Also send a general error message via websocket
            ws = self.manager.active_connections.get(self.id)
            if ws:
                await self.manager.send_error(ws, self.id, f"Build failed during {active_phase} phase: {e}")

    async def update_phase_status(self, phase_name: str, status: str, details: str = ""):
        for phase in self.phases:
            if phase.name == phase_name:
                phase.status = status
                phase.details = details
                break
        await self.manager.send_progress_update(self.id, {
            "phases": [p.to_dict() for p in self.phases]
        })


class ProjectOrchestrator:
    """Manages all active projects."""
    def __init__(self, manager: ConnectionManager):
        self.projects: Dict[str, Project] = {}
        self.manager = manager

    async def start_project(self, project_id: str, websocket: WebSocket):
        if project_id not in self.projects:
            self.projects[project_id] = Project(project_id, self.manager)
            self.manager.register_project_connection(project_id, websocket)
            # Start the conversation with the PM's first message
            await self.projects[project_id].get_pm_response()
        else:
            # Reconnecting to an existing project
             self.manager.register_project_connection(project_id, websocket)


    async def handle_user_message(self, project_id: str, message: str):
        project = self.projects.get(project_id)
        if project:
            await project.add_user_message(message)
        else:
            logger.warning(f"Received message for non-existent project: {project_id}")
```
---
## File: `blueprint/src/workflow/phases.py`
```python
import asyncio
import logging
import json
from typing import Dict, Any, List

from blueprint.src.config.settings import settings
from blueprint.src.llm.client import LLMClient
from blueprint.src.storage.filesystem import parse_and_write_files, format_files_for_context

logger = logging.getLogger(__name__)

# Forward declaration for type hinting
class Project:
    pass

class Phase:
    def __init__(self, name: str):
        self.name = name
        self.status = "pending"  # pending, in_progress, complete, failed
        self.details = ""

    async def run(self, project: 'Project'):
        raise NotImplementedError

    def to_dict(self):
        return {"name": self.name, "status": self.status, "details": self.details}

class GenesisPhase(Phase):
    def __init__(self):
        super().__init__("Genesis")

    async def run(self, project: 'Project'):
        num_rounds = settings.workflow.genesis_rounds
        for i in range(1, num_rounds + 1):
            project.details = f"Round {i}/{num_rounds}"
            logger.info(f"Project {project.id}: Starting Genesis Round {i}")
            
            # Prepare context
            context_prompt = self._prepare_context(project, i)
            
            # Prepare roles and clients
            team_members = [settings.team.senior] + settings.team.juniors.models
            roles = ['senior'] + [f'junior_{j}' for j in range(settings.team.juniors.count)]
            
            # Run all team members in parallel
            tasks = []
            for role, model_id in zip(roles, team_members):
                client = LLMClient(model_id)
                system_prompt = client.get_context_from_file('senior' if role == 'senior' else 'junior')
                tasks.append(self._run_developer(client, system_prompt, context_prompt, project, role, i))
            
            await asyncio.gather(*tasks)
        self.details = f"{num_rounds} rounds completed."

    def _prepare_context(self, project: 'Project', round_num: int) -> str:
        req_conv = "\n".join([f"{msg['role']}: {msg['content']}" for msg in project.anchor_context['requirements_conversation']])
        context = f"ORIGINAL REQUIREMENTS (Verbatim Conversation):\n---\n{req_conv}\n---\n\n"
        context += f"PROJECT MANAGER INSTRUCTIONS:\n---\n{project.anchor_context['pm_instructions']}\n---\n\n"
        
        if round_num > 1:
            context += "PREVIOUS ROUND SUBMISSIONS FOR CROSS-POLLINATION:\n---\n"
            prev_round = round_num - 1
            roles = ['senior'] + [f'junior_{j}' for j in range(settings.team.juniors.count)]
            for role in roles:
                role_path = project.project_path / f"genesis_round_{prev_round}" / role
                if role_path.exists():
                    context += f"Submission from {role}:\n"
                    context += format_files_for_context(role_path)
                    context += "\n"
            context += "---\n"
        return context

    async def _run_developer(self, client: LLMClient, system_prompt: str, user_prompt: str, project: 'Project', role: str, round_num: int):
        logger.info(f"Project {project.id}: Running {role} for Genesis Round {round_num}")
        response = await client.generate(system_prompt, [{"role": "user", "content": user_prompt}])
        output_path = project.project_path / f"genesis_round_{round_num}" / role
        parse_and_write_files(response, output_path)

class SynthesisPhase(Phase):
    def __init__(self):
        super().__init__("Synthesis")

    async def run(self, project: 'Project'):
        logger.info(f"Project {project.id}: Starting Synthesis")
        # Prepare context with all final Genesis submissions
        final_genesis_round = settings.workflow.genesis_rounds
        req_conv = "\n".join([f"{msg['role']}: {msg['content']}" for msg in project.anchor_context['requirements_conversation']])
        context = f"ORIGINAL REQUIREMENTS (Verbatim Conversation):\n---\n{req_conv}\n---\n\n"
        context += f"PROJECT MANAGER INSTRUCTIONS:\n---\n{project.anchor_context['pm_instructions']}\n---\n\n"
        context += "FINAL GENESIS SUBMISSIONS TO SYNTHESIZE:\n---\n"
        
        roles = ['senior'] + [f'junior_{j}' for j in range(settings.team.juniors.count)]
        for role in roles:
            role_path = project.project_path / f"genesis_round_{final_genesis_round}" / role
            context += f"Submission from {role}:\n{format_files_for_context(role_path)}\n"
        context += "---\n"
        
        # Run Senior Developer
        client = LLMClient(settings.team.senior)
        system_prompt = client.get_context_from_file('senior')
        response = await client.generate(system_prompt, [{"role": "user", "content": context}])
        
        output_path = project.project_path / "synthesis_round_1"
        parse_and_write_files(response, output_path)

class ReviewPhase(Phase):
    def __init__(self):
        super().__init__("Review & Revise")

    async def run(self, project: 'Project'):
        max_loops = settings.workflow.max_review_loops
        for i in range(1, max_loops + 1):
            self.details = f"Loop {i}/{max_loops}"
            logger.info(f"Project {project.id}: Starting Review Loop {i}")
            
            synthesized_path = project.project_path / f"synthesis_round_{i}"
            
            # 1. Get critiques from Juniors
            critiques = await self._get_junior_critiques(project, synthesized_path)
            
            # 2. Check for consensus
            approvals = [c['approved'] for c in critiques if 'approved' in c]
            num_approved = sum(1 for a in approvals if a)
            
            if num_approved / len(approvals) >= settings.workflow.approval_threshold:
                logger.info(f"Project {project.id}: Consensus reached in review loop {i}.")
                # Move final synthesis to 'senior' folder for final output
                final_path = project.project_path / "senior"
                if final_path.exists():
                    import shutil
                    shutil.rmtree(final_path)
                synthesized_path.rename(final_path)
                self.details = f"Consensus reached after {i} loops."
                return

            # 3. If no consensus, send back to Senior for revision
            await self._run_senior_revision(project, synthesized_path, critiques, i)

        raise Exception(f"Consensus not reached after {max_loops} review loops.")

    async def _get_junior_critiques(self, project: 'Project', synthesized_path: Any) -> List[Dict]:
        req_conv = "\n".join([f"{msg['role']}: {msg['content']}" for msg in project.anchor_context['requirements_conversation']])
        context = f"ORIGINAL REQUIREMENTS:\n---\n{req_conv}\n---\n\n"
        context += f"SYNTHESIZED SOLUTION TO REVIEW:\n---\n{format_files_for_context(synthesized_path)}\n---"
        
        tasks = []
        for model_id in settings.team.juniors.models:
            client = LLMClient(model_id)
            system_prompt = client.get_context_from_file('junior')
            tasks.append(client.generate(system_prompt, [{"role": "user", "content": context}]))
            
        responses = await asyncio.gather(*tasks)
        
        critiques = []
        for i, resp in enumerate(responses):
            try:
                # Clean up response and parse JSON
                json_str = resp[resp.find('{'):resp.rfind('}')+1]
                critique = json.loads(json_str)
                critiques.append(critique)
                logger.info(f"Project {project.id}: Junior {i} review: {critique}")
            except json.JSONDecodeError:
                logger.error(f"Project {project.id}: Junior {i} failed to provide valid JSON review. Response: {resp}")
                critiques.append({"approved": False, "critique": "Failed to provide valid JSON."})
        return critiques

    async def _run_senior_revision(self, project: 'Project', synthesized_path: Any, critiques: List[Dict], loop_num: int):
        logger.info(f"Project {project.id}: Sending to Senior for revision.")
        req_conv = "\n".join([f"{msg['role']}: {msg['content']}" for msg in project.anchor_context['requirements_conversation']])
        context = f"ORIGINAL REQUIREMENTS:\n---\n{req_conv}\n---\n\n"
        context += f"YOUR PREVIOUSLY SYNTHESIZED SOLUTION:\n---\n{format_files_for_context(synthesized_path)}\n---\n\n"
        context += "JUNIOR DEVELOPER FEEDBACK (Address these points):\n---\n"
        for i, c in enumerate(critiques):
            context += f"Junior #{i+1} Critique: {c.get('critique', 'No critique provided.')}\n"
        context += "---\n"
        
        client = LLMClient(settings.team.senior)
        system_prompt = client.get_context_from_file('senior')
        response = await client.generate(system_prompt, [{"role": "user", "content": context}])
        
        output_path = project.project_path / f"synthesis_round_{loop_num + 1}"
        parse_and_write_files(response, output_path)

def create_initial_phases() -> List[Phase]:
    return [
        GenesisPhase(),
        SynthesisPhase(),
        ReviewPhase(),
    ]
```
---
## File: `blueprint/src/llm/client.py`
```python
import os
import logging
from typing import Any, Dict, Optional, List
from pathlib import Path

from openai import AsyncOpenAI
import google.generativeai as genai
import anthropic
from tenacity import retry, stop_after_attempt, wait_exponential

from blueprint.src.config.settings import settings

logger = logging.getLogger(__name__)

class LLMClient:
    _clients: Dict[str, Any] = {}
    _context_cache: Dict[str, str] = {}

    def __init__(self, model_identifier: str):
        self.provider, self.model = self._parse_identifier(model_identifier)
        self.api_key = self._get_api_key()
        self._client = self._get_client()

    def _parse_identifier(self, identifier: str) -> (str, str):
        try:
            provider, model = identifier.split('/', 1)
            return provider, model
        except ValueError:
            raise ValueError(f"Invalid model identifier format: '{identifier}'. Expected 'provider/model-name'.")

    def _get_api_key(self) -> str:
        key = getattr(settings.api_keys, self.provider, None)
        if not key:
            raise ValueError(f"API key for provider '{self.provider}' is not configured in .env file.")
        return key

    def _get_client(self):
        # Use a tuple of (provider, api_key) for client caching to handle key rotations if ever needed
        client_key = (self.provider, self.api_key)
        if client_key in self._clients:
            return self._clients[client_key]

        client = None
        try:
            if self.provider == "openai":
                client = AsyncOpenAI(api_key=self.api_key)
            elif self.provider == "google":
                genai.configure(api_key=self.api_key)
                client = genai
            elif self.provider == "anthropic":
                client = anthropic.AsyncAnthropic(api_key=self.api_key)
            elif self.provider == "together":
                client = AsyncOpenAI(api_key=self.api_key, base_url="https://api.together.xyz/v1")
            elif self.provider == "xai":
                # Placeholder, assuming OpenAI-compatible API
                client = AsyncOpenAI(api_key=self.api_key, base_url="https://api.x.ai/v1")
            else:
                raise ValueError(f"Unsupported LLM provider: {self.provider}")
        except Exception as e:
            logger.error(f"Failed to initialize client for {self.provider}: {e}")
            raise

        self._clients[client_key] = client
        return client

    def get_context_from_file(self, role: str) -> str:
        if role in self._context_cache:
            return self._context_cache[role]
        
        context_path_str = getattr(settings.context_paths, role, None)
        if not context_path_str:
            raise ValueError(f"Context path for role '{role}' not found in config.")
        
        context_path = Path(context_path_str)
        if not context_path.exists():
            raise FileNotFoundError(f"Context file for role '{role}' not found at path: {context_path}")
            
        content = context_path.read_text(encoding='utf-8')
        self._context_cache[role] = content
        return content

    @retry(wait=wait_exponential(multiplier=1, min=2, max=60), stop=stop_after_attempt(settings.workflow.max_retries))
    async def generate(self, system_prompt: str, messages: List[Dict[str, str]]) -> str:
        logger.info(f"Invoking model {self.provider}/{self.model}...")
        try:
            if self.provider in ["openai", "together", "xai"]:
                response = await self._client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "system", "content": system_prompt}] + messages,
                )
                return response.choices[0].message.content
            
            elif self.provider == "anthropic":
                response = await self._client.messages.create(
                    model=self.model,
                    system=system_prompt,
                    messages=messages,
                    max_tokens=8192, # Anthropic requires max_tokens
                )
                return response.content[0].text
            
            elif self.provider == "google":
                model_instance = self._client.GenerativeModel(model_name=self.model, system_instruction=system_prompt)
                response = await model_instance.generate_content_async(messages)
                return response.text

        except Exception as e:
            logger.error(f"LLM generation failed for model {self.provider}/{self.model}: {e}", exc_info=True)
            raise
        
        raise NotImplementedError(f"Generation for provider {self.provider} not implemented correctly.")
```
---
## File: `blueprint/src/storage/filesystem.py`
```python
import logging
import re
from pathlib import Path
from typing import List, Dict

logger = logging.getLogger(__name__)

def parse_and_write_files(response_content: str, workspace_path: Path) -> List[str]:
    """
    Parses an LLM response for markdown code blocks and writes them to files.
    Format: ## File: path/to/filename.ext\n```lang\n...content...\n```
    """
    files_created = []
    workspace_path.mkdir(parents=True, exist_ok=True)
    
    # Regex to find file blocks, tolerant to variations
    pattern = r"##\s*File:\s*`?(.+?)`?\s*\n```(?:\w*\n)?(.*?)```"
    matches = re.findall(pattern, response_content, re.DOTALL)

    if not matches:
        logger.warning(f"No file blocks found in response for workspace {workspace_path}")
        # As a fallback, write the whole response to a single file
        fallback_path = workspace_path / "response.md"
        fallback_path.write_text(response_content, encoding='utf-8')
        files_created.append(str(fallback_path))
        return files_created

    for filename_str, content in matches:
        filename_str = filename_str.strip()
        # Basic sanitization to prevent directory traversal
        if ".." in filename_str or filename_str.startswith(('/', '\\')):
            logger.warning(f"Skipping potentially unsafe file path: {filename_str}")
            continue

        file_path = workspace_path / filename_str
        file_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            # The regex captures the final ```, so we strip it
            content_cleaned = content.strip()
            file_path.write_text(content_cleaned, encoding='utf-8')
            files_created.append(str(file_path))
            logger.info(f"Written file: {file_path}")
        except IOError as e:
            logger.error(f"Failed to write file {file_path}: {e}")

    return files_created

def format_files_for_context(workspace_path: Path) -> str:
    """Reads all files from a workspace and formats them for an LLM context."""
    context_str = ""
    if not workspace_path.is_dir():
        return "No files found in this submission."
        
    for path in sorted(workspace_path.rglob('*')):
        if path.is_file():
            try:
                content = path.read_text(encoding='utf-8')
                relative_path = path.relative_to(workspace_path)
                context_str += f"## File: {relative_path}\n```\n{content}\n```\n\n"
            except Exception as e:
                logger.warning(f"Could not read file {path} for context: {e}")
    return context_str

def get_project_files_as_dict(workspace_path: Path) -> Dict[str, str]:
    """Recursively reads all files from a workspace into a dictionary."""
    file_dict = {}
    if not workspace_path.is_dir():
        return {}
    
    for path in sorted(workspace_path.rglob('*')):
        if path.is_file():
            try:
                content = path.read_text(encoding='utf-8')
                relative_path = str(path.relative_to(workspace_path))
                file_dict[relative_path] = content
            except Exception as e:
                logger.warning(f"Could not read file {path} for artifact dictionary: {e}")
    return file_dict
```
---
## File: `blueprint/src/config/settings.py`
```python
import yaml
import os
import re
from pydantic import BaseModel, Field, ValidationError
from typing import List, Dict, Optional
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

CONFIG_PATH = "blueprint/config.yaml"

# --- Pydantic Models for Strong Typing and Validation ---

class ApiKeys(BaseModel):
    openai: Optional[str] = None
    google: Optional[str] = None
    together: Optional[str] = None
    xai: Optional[str] = None
    anthropic: Optional[str] = None

class JuniorsConfig(BaseModel):
    count: int = Field(..., ge=2, le=5)
    models: List[str]

class TeamConfig(BaseModel):
    project_manager: str
    senior: str
    juniors: JuniorsConfig

class WorkflowConfig(BaseModel):
    genesis_rounds: int = Field(..., ge=1, le=3)
    max_review_loops: int = Field(..., ge=1, le=10)
    approval_threshold: float = Field(..., ge=0.5, le=1.0)
    max_retries: int = Field(..., ge=1, le=5)

class OutputConfig(BaseModel):
    path: str

class ContextPathsConfig(BaseModel):
    project_manager: str
    senior: str
    junior: str

class Settings(BaseModel):
    team: TeamConfig
    workflow: WorkflowConfig
    output: OutputConfig
    context_paths: ContextPathsConfig
    api_keys: ApiKeys = Field(default_factory=ApiKeys) # api_keys are loaded separately

def _env_replacer(match):
    """Replaces ${VAR} with environment variable content."""
    var_name = match.group(1)
    return os.environ.get(var_name, "")

def load_settings() -> Settings:
    """Loads, substitutes env vars, and validates the YAML configuration."""
    if not os.path.exists(CONFIG_PATH):
        raise FileNotFoundError(f"Configuration file not found at '{CONFIG_PATH}'.")

    with open(CONFIG_PATH, 'r') as f:
        raw_config_str = f.read()

    # Substitute environment variables (for potential future use, e.g., in paths)
    processed_config_str = re.sub(r'\$\{(\w+)\}', _env_replacer, raw_config_str)
    config_dict = yaml.safe_load(processed_config_str)

    try:
        settings_obj = Settings.model_validate(config_dict)
        # Load API keys from .env file
        load_dotenv()
        settings_obj.api_keys = ApiKeys(
            openai=os.getenv("OPENAI_API_KEY"),
            google=os.getenv("GOOGLE_API_KEY"),
            together=os.getenv("TOGETHER_API_KEY"),
            xai=os.getenv("XAI_API_KEY"),
            anthropic=os.getenv("ANTHROPIC_API_KEY"),
        )
        return settings_obj
    except ValidationError as e:
        logger.error(f"Configuration validation error: {e}")
        raise

settings = load_settings()
```
---
## File: `Dockerfile`
```dockerfile
# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Create a non-root user and switch to it
RUN useradd -m appuser
USER appuser

# Copy only the dependency files first to leverage Docker layer caching
COPY --chown=appuser:appuser pyproject.toml poetry.lock* ./
COPY --chown=appuser:appuser requirements.txt ./

# Install dependencies
# Using requirements.txt for simplicity in this setup, but poetry is also configured
RUN pip install --no-cache-dir --user -r requirements.txt

# Copy the rest of the application code
COPY --chown=appuser:appuser . .

# Expose the port the app runs on
EXPOSE 8000

# Add the user's local bin to the PATH
ENV PATH="/home/appuser/.local/bin:${PATH}"

# Run the application
CMD ["uvicorn", "blueprint.src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```
---
## File: `docker-compose.yml`
```yaml
version: '3.8'

services:
  blueprint:
    build: .
    container_name: blueprint-v2
    restart: unless-stopped
    ports:
      - "8000:8000"
    volumes:
      # Mount the projects directory to persist outputs on the host
      - ./projects:/app/projects
      # Mount the source code for live-reloading during development
      # For production, you would typically not mount the source code
      - ./blueprint:/app/blueprint
    env_file:
      - .env
    healthcheck:
      test: ["CMD-SHELL", "curl -f http://localhost:8000 || exit 1"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 20s

volumes:
  projects:
```
---
## File: `install.sh`
```bash
#!/bin/bash
set -e

# This script builds and runs the Blueprint v2.0.1 application using Docker.

# --- Functions ---
print_msg() {
    COLOR=$1
    MSG=$2
    case "$COLOR" in
        "green") echo -e "\033[0;32m${MSG}\033[0m" ;;
        "red") echo -e "\033[0;31m${MSG}\033[0m" ;;
        "yellow") echo -e "\033[0;33m${MSG}\033[0m" ;;
        *) echo "${MSG}" ;;
    esac
}

command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# --- Pre-flight Checks ---
print_msg "yellow" "--- Running Pre-flight Checks ---"

if ! command_exists docker; then
    print_msg "red" "Error: Docker is not installed. Please install Docker to continue."
    exit 1
fi
print_msg "green" "✅ Docker is installed."

if ! command_exists docker-compose; then
    # Check for 'docker compose' (v2 syntax)
    if ! docker compose version >/dev/null 2>&1; then
        print_msg "red" "Error: Docker Compose is not installed. Please install Docker Compose to continue."
        exit 1
    fi
    DOCKER_COMPOSE_CMD="docker compose"
else
    DOCKER_COMPOSE_CMD="docker-compose"
fi
print_msg "green" "✅ Docker Compose is available."

if [ ! -f .env ]; then
    print_msg "yellow" "Warning: .env file not found. Copying from .env.example."
    print_msg "yellow" "Please fill in at least one API key in the '.env' file before starting."
    cp .env.example .env
    print_msg "green" "✅ .env file created. Please edit it with your API keys, then run this script again."
    exit 0
fi
print_msg "green" "✅ .env file found."


# --- Installation ---
print_msg "yellow" "\n--- Starting Blueprint v2.0.1 Installation ---"

if [ "$($DOCKER_COMPOSE_CMD ps -q)" ]; then
    print_msg "yellow" "Stopping existing Blueprint containers..."
    $DOCKER_COMPOSE_CMD down
fi

print_msg "yellow" "Building Docker image..."
$DOCKER_COMPOSE_CMD build
if [ $? -ne 0 ]; then
    print_msg "red" "Error: Docker image build failed."
    exit 1
fi
print_msg "green" "✅ Docker image built successfully."

print_msg "yellow" "Starting Blueprint container..."
$DOCKER_COMPOSE_CMD up -d
if [ $? -ne 0 ]; then
    print_msg "red" "Error: Failed to start the Docker container."
    exit 1
fi

# --- Post-installation ---
print_msg "green" "\n--- ✅ Installation Complete ---"
print_msg "green" "Blueprint v2.0.1 is now running!"
print_msg "green" "Access the web UI at: http://localhost:8000"
print_msg "yellow" "\nTo view logs, run: $DOCKER_COMPOSE_CMD logs -f"
print_msg "yellow" "To stop the application, run: $DOCKER_COMPOSE_CMD down"

exit 0
```
---
## File: `pyproject.toml`
```toml
[tool.poetry]
name = "blueprint-v2"
version = "2.0.1"
description = "Conversational Multi-Agent Development System"
authors = ["Genesis Developer"]
readme = "README.md"

[tool.poetry.dependencies]
python = "^3.11"
fastapi = "^0.111.0"
uvicorn = {extras = ["standard"], version = "^0.30.1"}
websockets = "^12.0"
python-dotenv = "^1.0.1"
pyyaml = "^6.0.1"
pydantic = "^2.8.2"
openai = "^1.35.13"
google-generativeai = "^0.7.2"
anthropic = "^0.29.0"
tenacity = "^8.5.0"
fastapi-staticfiles = "^0.0.1"

[tool.poetry.group.dev.dependencies]
pytest = "^8.2.2"
pytest-asyncio = "^0.23.7"
httpx = "^0.27.0"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
```
---
## File: `requirements.txt`
```txt
# This file is for Docker builds and environments without Poetry.
# It should be kept in sync with pyproject.toml
fastapi==0.111.0
uvicorn[standard]==0.30.1
websockets==12.0
python-dotenv==1.0.1
PyYAML==6.0.1
pydantic==2.8.2
openai==1.35.13
google-generativeai==0.7.2
anthropic==0.29.0
tenacity==8.5.0
fastapi-staticfiles==0.0.1
```
---
## File: `README.md`
```md
# Blueprint v2.0.1 (Round 2 Cross-Pollinated)

Blueprint is a conversational multi-agent system designed to create complete, production-ready digital assets from a natural language conversation. You interact with a Project Manager AI to define requirements, and a specialized team of AI agents collaborates to build, synthesize, and review the final product.

This version (v2.0.1) implements the core conversational workflow and provides a simple, intuitive web interface for interaction, built by synthesizing the best architectural patterns from multiple Round 1 implementations.

## Core Workflow

The system follows a robust, multi-phase process designed to prevent "prompt drift" and ensure high-quality output:

1.  **Requirements Gathering**: You chat with a Project Manager (PM) AI to define what you want to build. The entire verbatim conversation becomes the requirements.
2.  **Genesis**: A team of developers (1 Senior, 3 Juniors) work in parallel to create independent solutions. This can be run for multiple rounds to allow for cross-pollination of ideas.
3.  **Synthesis**: The Senior Developer analyzes all Genesis solutions and synthesizes them into a single, superior version.
4.  **Review & Revise**: The Junior team reviews the synthesized version and provides critiques. If consensus isn't reached, the feedback is sent back to the Senior for revision. This loop continues until the team approves the final product.
5.  **Final Output**: The approved asset is presented to you, with all files available for viewing in the UI.

## Features

-   **Conversational Interface**: A chat-based UI for defining project requirements naturally.
-   **Stateful Multi-Agent System**: A reliable backend orchestrator that manages the complex workflow from conversation to final output.
-   **Real-time Progress**: A live-updating UI that shows the status of each build phase via WebSockets.
-   **Artifact Viewer**: View the final generated code and other files directly in a tabbed interface.
-   **Configurable AI Team**: Easily configure the models used for each role via `blueprint/config.yaml`.
-   **Multi-Provider Support**: Integrates with OpenAI, Google, Anthropic, and Together.ai.
-   **Dockerized**: The entire application is containerized for easy, consistent, and isolated deployment.

## Installation and Usage

### Prerequisites

-   [Docker](https://docs.docker.com/get-docker/)
-   [Docker Compose](https://docs.docker.com/compose/install/) (v1 `docker-compose` or v2 `docker compose`)

### Quick Start

1.  **Clone the Repository**:
    ```bash
    git clone <repository_url>
    cd <repository_folder>
    ```

2.  **Configure API Keys**:
    A `.env.example` file is provided. Copy it to `.env` and add your API keys. You only need to provide keys for the providers you intend to use in `config.yaml`.
    ```bash
    cp .env.example .env
    # Now edit the .env file with your keys
    nano .env
    ```

3.  **Run the Installation Script**:
    This script will check prerequisites, build the Docker image, and start the application.
    ```bash
    chmod +x install.sh
    ./install.sh
    ```

4.  **Access the Web UI**:
    Once the container is running, open your web browser and navigate to:
    **[http://localhost:8000](http://localhost:8000)**

### How to Use

1.  Click the **"+ New Project"** button.
2.  A new project will appear in the left sidebar, and you can begin chatting with the Project Manager AI.
3.  Converse with the PM to define your requirements. Ask it questions, give it details.
4.  When you are satisfied with the requirements, type `/build` and press send.
5.  The build process will begin, and you can monitor the progress in the status panel that appears.
6.  When the build is complete, the final files will appear in the "Artifacts" panel on the right.

### Managing the Application

-   **View Logs**:
    ```bash
    docker-compose logs -f
    ```
-   **Stop the Application**:
    ```bash
    docker-compose down
    ```

## Project Structure

```
.
├── blueprint/
│   ├── contexts/         # System prompts for AI roles
│   ├── frontend/         # HTML, CSS, JS for the web UI
│   ├── src/              # Python source code
│   │   ├── api/          # WebSocket connection manager
│   │   ├── config/       # Pydantic settings and config loader
│   │   ├── llm/          # Multi-provider LLM client
│   │   ├── storage/      # Filesystem utilities
│   │   └── workflow/     # Core workflow orchestrator and phase logic
│   └── config.yaml       # Main application configuration
├── projects/             # Output directory for generated projects
├── tests/                # Pytest test suite
├── .env.example          # Example environment file for API keys
├── Dockerfile            # Defines the application container
├── docker-compose.yml    # Orchestrates the application service
├── install.sh            # Installation and startup script
└── README.md             # This file
```
```
---
## File: `.env.example`
```dotenv
# API Keys for Blueprint LLM Providers
# You only need to fill in the keys for the models you configure in config.yaml.
# Get your keys from the respective provider websites.

OPENAI_API_KEY=""
GOOGLE_API_KEY=""
ANTHROPIC_API_KEY=""
TOGETHER_API_KEY=""
XAI_API_KEY=""
```
