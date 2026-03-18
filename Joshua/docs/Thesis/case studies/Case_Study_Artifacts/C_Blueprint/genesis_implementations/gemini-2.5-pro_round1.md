Of course. As a Genesis Developer on this multi-agent team, I will build the complete Blueprint v2.0.1 implementation.

I have carefully reviewed the anchor context, the existing v1 codebase, and the detailed requirements, paying special attention to the `Blueprint_v2.0.1_Requirements.md` file which prioritizes a reliable core workflow and a simple UI over advanced features.

My implementation will replace the unreliable v1 `desktop_commander` with a secure, backend-driven file system, refactor the LLM provider layer for stability, and introduce a clean FastAPI backend with a vanilla JavaScript frontend, all containerized with Docker. I will also provide the requested installation and comprehensive testing scripts.

Here is the complete Blueprint v2.0.1 implementation:

---

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
  # Number of parallel creation rounds. v2.0.1 uses a single round.
  genesis_rounds: 1
  # Minimum number of successful junior responses required to proceed to Synthesis.
  min_successful_juniors: 2
  # Maximum retry attempts for a failing LLM call.
  max_retries: 2

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

---

## File: `blueprint/contexts/junior_developer.md`

```md
# Role: Junior Developer

You are a Junior Developer on the Blueprint team. You are a highly skilled and creative professional tasked with generating a complete, independent solution based on a set of guiding documents. Your strength lies in your ability to think creatively and produce a high-quality, standalone deliverable from a clear specification.

## Your Core Responsibilities:

1.  **Genesis Phase (Creation)**: This is your primary function. You will receive a requirements document. Your task is to create a complete, fully-realized version of the requested digital asset based *only* on this document.
    -   Work independently. Do not assume you can ask for clarification.
    -   Be creative and innovative in your approach, while strictly adhering to the specified constraints.
    -   Your output should be a complete set of files that fulfill the request.

2.  **Consensus Phase (Review)**: After the Genesis and Synthesis phases, you will be asked to review the final, consolidated solution created by the Senior Developer. You must provide a JSON response with two scores:
    -   `technical_score` (1-10): Does the solution work? Is it technically sound and complete according to the requirements? (10 = Perfect, 1 = Fatally flawed).
    -   `subjective_score` (1-10): Is this a high-quality, elegant, and well-crafted solution? (10 = Brilliant, 1 = Poor quality).
    -   Also provide a brief `reasoning` string for your scores.

## Output Format for Genesis Phase:

**CRITICAL**: You must write ALL generated files directly in your response using markdown code blocks. Use this exact format:

```
## File: path/to/filename.ext
\`\`\`language
file contents here
\`\`\`

## File: another_file.ext
\`\`\`language
another file contents
\`\`\`
```

For example:

```
## File: calculator.py
\`\`\`python
def add(a, b):
    return a + b

def subtract(a, b):
    return a - b
\`\`\`

## File: README.md
\`\`\`markdown
# Calculator

A simple Python calculator with add, subtract, multiply, and divide functions.
\`\`\`
```

## Process:

1.  **Genesis Phase**:
    -   You will receive requirements in your prompt.
    -   Create a complete solution with ALL necessary files.
    -   Write each file using the markdown code block format shown above.
    -   Include documentation, tests, and any supporting files needed.
    -   Ensure your solution is self-contained and complete.

2.  **Consensus Phase**:
    -   Review the synthesized solution against the original requirements.
    -   Provide your scores in this EXACT JSON format:
    ```json
    {
      "technical_score": 8,
      "subjective_score": 7,
      "reasoning": "Your explanation here."
    }
    ```

**CRITICAL**: Your goal in the Genesis round is to produce the best possible standalone solution. Be bold and innovative. Write COMPLETE, WORKING CODE in markdown code blocks. Do NOT write instructions about what to do - write the actual code files.
```

---

## File: `blueprint/contexts/project_manager.md`

```md
# Role: Project Manager

You are the Project Manager for Blueprint. Your role is to take a user's request and transform it into a clear, actionable requirements document for the development team. You are the bridge between the user's idea and the technical implementation.

## Your Core Responsibility:

**Anchor Docs Phase**: Your single most important task is to analyze the user's request and produce a comprehensive requirements document.

-   **Analyze the request**: Carefully read the user's prompt to understand their core goal, the type of digital asset they want, and any specified constraints or features.
-   **Structure the requirements**: Organize the requirements logically. A good structure includes an overview, key features, technical specifications (if any), and success criteria.
-   **Be explicit**: The development team will work *only* from your document. Ambiguity will lead to incorrect results. Be clear and specific.
-   **Do not create the asset**: Your job is to write the specification, not the final product. The Senior and Junior Developers will handle the implementation.

## Output Format:

**CRITICAL**: You must output the requirements document as a single markdown file. Your response should contain ONLY the file content in the following format. Do not add any conversational text before or after the file block.

```
## File: 01_requirements.md
\`\`\`markdown
# Project Requirements: [Project Title]

## 1. Overview

A brief, one-paragraph summary of the project's goal.

## 2. Key Features

- A bulleted list of the essential features and functionalities.
- Each feature should be described clearly.

## 3. Technical Specifications (Optional)

- Specify any required technologies, languages, or platforms.
- Mention any constraints or non-functional requirements (e.g., performance, security).

## 4. Deliverables

- A list of the expected output files (e.g., source code, documentation, test files).
- This helps the team understand the scope of the project.

## 5. Success Criteria

- How will we know the project is successful?
- e.g., "The application runs without errors," "All specified features are implemented."
\`\`\`
```

## Process:

1.  Receive the user's request in your prompt.
2.  Analyze it thoroughly.
3.  Construct the requirements document inside a markdown code block as shown above.
4.  Ensure your entire response is just this single file block.
```

---

## File: `blueprint/contexts/senior_developer.md`

```md
# Role: Senior Developer

You are the Senior Developer, the technical and creative lead of the Blueprint team. You possess deep expertise and are responsible for synthesizing the work of the entire team into a final, superior product.

## Your Core Responsibilities:

1.  **Genesis Phase (Creation)**: You participate in the Genesis phase just like a Junior Developer. You will create your own complete, independent solution based on the requirements. This serves as a high-quality baseline for the Synthesis phase.

2.  **Synthesis Phase (Combination)**: This is your most critical responsibility. After the Genesis phase, you will receive all solutions created by yourself and the Junior Developers. Your task is to:
    -   Analyze all submissions to identify the best ideas, code structures, and implementation details.
    -   Merge, refactor, and combine these ideas into a single, cohesive, and superior solution.
    -   **Do not simply pick one solution**. Your goal is to create a NEW synthesized artifact that is better than any individual submission. The final product should be a polished, production-ready deliverable.

## Output Format for ALL Creation/Synthesis Phases:

**CRITICAL**: You must write ALL generated files directly in your response using markdown code blocks. Use this exact format:

```
## File: path/to/filename.ext
\`\`\`language
file contents here
\`\`\`

## File: another_file.ext
\`\`\`language
another file contents
\`\`\`
```

For example:

```
## File: app.py
\`\`\`python
from flask import Flask, request
app = Flask(__name__)

@app.route('/')
def home():
    return "Hello World"
\`\`\`

## File: README.md
\`\`\`markdown
# My Application

A simple Flask web application.

## Installation
pip install flask

## Usage
python app.py
\`\`\`
```

## Process:

1.  **Genesis Phase**:
    -   You will receive the requirements in your prompt.
    -   Create your own complete solution with ALL necessary files.
    -   Write each file using the markdown code block format.
    -   This is your high-quality baseline for synthesis.

2.  **Synthesis Phase**:
    -   You will receive the requirements and all Genesis solutions in your prompt context.
    -   Analyze each submission to identify the best ideas.
    -   Create a NEW synthesized solution that combines the best parts.
    -   Write the synthesized files using markdown code blocks.
    -   **This is the final deliverable** - make it excellent.

**CRITICAL**:
-   Write COMPLETE, WORKING CODE in markdown code blocks.
-   Do NOT write instructions or conversational text.
-   Include ALL necessary files (main code, tests, README, requirements, etc.).
-   Your final output must be a self-contained, production-ready digital asset.
```

---

## File: `blueprint/frontend/app.js`

```javascript
document.addEventListener('DOMContentLoaded', () => {
    const buildForm = document.getElementById('buildForm');
    const promptInput = document.getElementById('prompt');
    const startBuildBtn = document.getElementById('startBuildBtn');
    const buildStatusContainer = document.getElementById('buildStatus');
    const recentBuildsList = document.getElementById('recentBuildsList');
    const settingsLink = document.getElementById('settingsLink');
    const mainPage = document.getElementById('mainPage');
    const settingsPage = document.getElementById('settingsPage');
    const backToMainLink = document.getElementById('backToMainLink');
    const settingsForm = document.getElementById('settingsForm');

    let currentBuildId = null;
    let ws = null;

    const API_BASE_URL = `${window.location.protocol}//${window.location.host}`;

    // --- Page Navigation ---
    settingsLink.addEventListener('click', (e) => {
        e.preventDefault();
        mainPage.style.display = 'none';
        settingsPage.style.display = 'block';
        loadSettings();
    });

    backToMainLink.addEventListener('click', (e) => {
        e.preventDefault();
        mainPage.style.display = 'block';
        settingsPage.style.display = 'none';
    });

    // --- WebSocket Handling ---
    function connectWebSocket(buildId) {
        const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        ws = new WebSocket(`${wsProtocol}//${window.location.host}/ws/build/${buildId}`);

        ws.onopen = () => console.log('WebSocket connected');
        ws.onclose = () => console.log('WebSocket disconnected');
        ws.onerror = (error) => console.error('WebSocket error:', error);

        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            updateBuildStatus(data);
        };
    }

    function updateBuildStatus(data) {
        if (data.build_id !== currentBuildId) return;

        const phaseEl = document.getElementById(`phase-${data.phase_number}`);
        if (phaseEl) {
            const statusIcon = phaseEl.querySelector('.status-icon');
            const detailsEl = phaseEl.querySelector('.phase-details');

            if (data.status === 'in_progress') {
                statusIcon.innerHTML = '🔄';
                statusIcon.className = 'status-icon in-progress';
            } else if (data.status === 'complete') {
                statusIcon.innerHTML = '✅';
                statusIcon.className = 'status-icon complete';
            } else if (data.status === 'failed') {
                statusIcon.innerHTML = '❌';
                statusIcon.className = 'status-icon failed';
            }
            
            detailsEl.innerHTML = `(${data.time_elapsed.toFixed(1)}s) ${data.message}`;

            // Un-hide the next step
            const nextPhaseEl = document.getElementById(`phase-${data.phase_number + 1}`);
            if (nextPhaseEl) {
                nextPhaseEl.style.visibility = 'visible';
            }
        }
        
        if (data.type === 'final_output') {
            handleFinalOutput(data.output);
        } else if (data.type === 'error') {
            handleBuildError(data);
        }

        const costEl = document.getElementById('cost-display');
        costEl.textContent = `$${data.cost_so_far.toFixed(4)}`;
    }
    
    function handleFinalOutput(output) {
        const finalStatus = document.getElementById('final-status');
        let content = `<h3>✅ Build Complete!</h3>
                       <p>Total Time: ${output.total_time.toFixed(1)}s</p>
                       <p>Total Cost: $${output.total_cost.toFixed(4)}</p>
                       <h4>Files Created:</h4>
                       <pre class="file-list">${output.files.join('\n')}</pre>`;

        if (output.download_path) {
             content += `<a href="${output.download_path}" class="button" download>Download ZIP</a>`;
        }
        content += `<button onclick="window.location.reload()" class="button">New Build</button>`;

        finalStatus.innerHTML = content;
        startBuildBtn.disabled = false;
        startBuildBtn.textContent = 'Start New Build';
        loadRecentBuilds();
    }

    function handleBuildError(data) {
        const finalStatus = document.getElementById('final-status');
        finalStatus.innerHTML = `<h3>❌ Build Failed</h3>
                                 <p>Phase: ${data.phase}</p>
                                 <p class="error-message">${data.message}</p>
                                 <button onclick="window.location.reload()" class="button">Try Again</button>`;
        startBuildBtn.disabled = false;
        startBuildBtn.textContent = 'Start New Build';
        loadRecentBuilds();
    }


    // --- Build Process ---
    buildForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const prompt = promptInput.value;
        if (!prompt) {
            alert('Please enter a project description.');
            return;
        }

        if (startBuildBtn.textContent === 'Start New Build') {
            window.location.reload();
            return;
        }

        startBuildBtn.disabled = true;
        startBuildBtn.textContent = 'Building...';
        buildStatusContainer.innerHTML = getInitialStatusHTML();
        buildStatusContainer.style.display = 'block';

        try {
            const response = await fetch(`${API_BASE_URL}/api/builds`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ prompt }),
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Failed to start build.');
            }

            const data = await response.json();
            currentBuildId = data.build_id;
            connectWebSocket(currentBuildId);

        } catch (error) {
            console.error('Error starting build:', error);
            alert(`Error: ${error.message}`);
            startBuildBtn.disabled = false;
            startBuildBtn.textContent = 'Start Build';
        }
    });

    function getInitialStatusHTML() {
        return `
            <h3>Building...</h3>
            <p>Cost so far: <span id="cost-display">$0.0000</span></p>
            <ul class="phase-list">
                <li id="phase-1" style="visibility: visible;">
                    <span class="status-icon pending">🔄</span>
                    <span class="phase-name">1. Anchor Docs</span>
                    <span class="phase-details">(Waiting...)</span>
                </li>
                <li id="phase-2" style="visibility: hidden;">
                    <span class="status-icon pending">⚪</span>
                    <span class="phase-name">2. Genesis</span>
                    <span class="phase-details"></span>
                </li>
                <li id="phase-3" style="visibility: hidden;">
                    <span class="status-icon pending">⚪</span>
                    <span class="phase-name">3. Synthesis</span>
                    <span class="phase-details"></span>
                </li>
                <li id="phase-4" style="visibility: hidden;">
                    <span class="status-icon pending">⚪</span>
                    <span class="phase-name">4. Consensus</span>
                    <span class="phase-details"></span>
                </li>
                <li id="phase-5" style="visibility: hidden;">
                    <span class="status-icon pending">⚪</span>
                    <span class="phase-name">5. Output</span>
                    <span class="phase-details"></span>
                </li>
            </ul>
            <div id="final-status"></div>
        `;
    }

    // --- Recent Builds ---
    async function loadRecentBuilds() {
        try {
            const response = await fetch(`${API_BASE_URL}/api/builds`);
            const builds = await response.json();
            recentBuildsList.innerHTML = '';
            builds.slice(0, 5).forEach(build => {
                const li = document.createElement('li');
                const statusIcon = build.status === 'complete' ? '✅' : (build.status === 'failed' ? '❌' : '🔄');
                const time = build.total_time ? `${build.total_time.toFixed(1)}s` : '';
                const cost = build.total_cost ? `$${build.total_cost.toFixed(4)}` : '';
                
                let actions = '';
                if (build.status === 'complete' && build.output_path) {
                    if (build.output_format === 'zip') {
                       actions = `<a href="/${build.output_path}" download>Download</a>`;
                    } else {
                       actions = `<a href="/projects-static/${build.id}/" target="_blank">View Files</a>`;
                    }
                } else if (build.status === 'failed') {
                    actions = `<a href="#" class="view-log" data-build-id="${build.id}">View Log</a>`;
                }

                li.innerHTML = `
                    <span>${statusIcon} ${build.prompt.substring(0, 40)}...</span>
                    <span class="build-meta">${time} ${cost}</span>
                    <span class="build-actions">${actions}</span>
                `;
                recentBuildsList.appendChild(li);
            });
        } catch (error) {
            console.error('Error loading recent builds:', error);
            recentBuildsList.innerHTML = '<li>Could not load recent builds.</li>';
        }
    }

    // --- Settings ---
    async function loadSettings() {
        try {
            const response = await fetch(`${API_BASE_URL}/api/config`);
            const config = await response.json();

            // API Keys
            document.getElementById('openai_api_key').value = config.api_keys.openai ? '********' : '';
            document.getElementById('google_api_key').value = config.api_keys.google ? '********' : '';
            document.getElementById('anthropic_api_key').value = config.api_keys.anthropic ? '********' : '';
            document.getElementById('together_api_key').value = config.api_keys.together ? '********' : '';

            // Team
            document.getElementById('project_manager').value = config.team.project_manager;
            document.getElementById('senior').value = config.team.senior;
            document.getElementById('juniors_count').value = config.team.juniors.count;

            const juniorModelsContainer = document.getElementById('junior_models_container');
            juniorModelsContainer.innerHTML = '';
            for (let i = 0; i < config.team.juniors.count; i++) {
                 const input = document.createElement('input');
                 input.type = 'text';
                 input.id = `junior_model_${i}`;
                 input.value = config.team.juniors.models[i] || '';
                 input.required = true;
                 const label = document.createElement('label');
                 label.htmlFor = `junior_model_${i}`;
                 label.textContent = `Junior ${i + 1} Model:`;
                 juniorModelsContainer.appendChild(label);
                 juniorModelsContainer.appendChild(input);
            }
        } catch (error) {
            console.error('Error loading settings:', error);
            alert('Could not load settings.');
        }
    }
    
    document.getElementById('juniors_count').addEventListener('change', (e) => {
        const count = parseInt(e.target.value, 10);
        const juniorModelsContainer = document.getElementById('junior_models_container');
        const existingInputs = juniorModelsContainer.querySelectorAll('input');
        const existingValues = Array.from(existingInputs).map(input => input.value);
        
        juniorModelsContainer.innerHTML = '';
        for (let i = 0; i < count; i++) {
             const input = document.createElement('input');
             input.type = 'text';
             input.id = `junior_model_${i}`;
             input.value = existingValues[i] || '';
             input.required = true;
             const label = document.createElement('label');
             label.htmlFor = `junior_model_${i}`;
             label.textContent = `Junior ${i + 1} Model:`;
             juniorModelsContainer.appendChild(label);
             juniorModelsContainer.appendChild(input);
        }
    });

    settingsForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const formData = new FormData(settingsForm);
        const juniorModels = Array.from(document.querySelectorAll('#junior_models_container input')).map(input => input.value);

        const newConfig = {
            api_keys: {
                openai: formData.get('openai_api_key').includes('********') ? null : formData.get('openai_api_key'),
                google: formData.get('google_api_key').includes('********') ? null : formData.get('google_api_key'),
                anthropic: formData.get('anthropic_api_key').includes('********') ? null : formData.get('anthropic_api_key'),
                together: formData.get('together_api_key').includes('********') ? null : formData.get('together_api_key'),
            },
            team: {
                project_manager: formData.get('project_manager'),
                senior: formData.get('senior'),
                juniors: {
                    count: parseInt(formData.get('juniors_count'), 10),
                    models: juniorModels
                }
            }
        };
        
        // Filter out null API keys
        for (const key in newConfig.api_keys) {
            if (newConfig.api_keys[key] === null) {
                delete newConfig.api_keys[key];
            }
        }

        try {
            const response = await fetch(`${API_BASE_URL}/api/config`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(newConfig),
            });
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Failed to save settings.');
            }
            alert('Settings saved successfully! The application will now reload.');
            window.location.reload();
        } catch (error) {
            console.error('Error saving settings:', error);
            alert(`Error: ${error.message}`);
        }
    });


    // --- Initial Load ---
    loadRecentBuilds();
});
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
        <header>
            <h1>Blueprint v2.0.1</h1>
            <nav>
                <a href="#" id="settingsLink">Settings</a>
            </nav>
        </header>

        <main id="mainPage">
            <section class="new-project">
                <h2>New Project</h2>
                <form id="buildForm">
                    <textarea id="prompt" rows="5" placeholder="Describe what you want to create... e.g., 'Create a Python web scraper for Hacker News'"></textarea>
                    <button type="submit" id="startBuildBtn" class="button primary">Start Build</button>
                </form>
            </section>

            <section id="buildStatus" class="build-status" style="display: none;"></section>

            <section class="recent-builds">
                <h2>Recent Builds</h2>
                <ul id="recentBuildsList">
                    <li>Loading recent builds...</li>
                </ul>
            </section>
        </main>

        <main id="settingsPage" style="display: none;">
            <a href="#" id="backToMainLink">&larr; Back to Main</a>
            <h2>Settings</h2>
            <form id="settingsForm">
                <fieldset>
                    <legend>API Keys</legend>
                    <p>Leave a key field unchanged to keep the existing key. Enter a new key to update it. To remove a key, submit an empty value.</p>
                    <label for="openai_api_key">OpenAI API Key:</label>
                    <input type="password" id="openai_api_key" name="openai_api_key">
                    
                    <label for="google_api_key">Google API Key:</label>
                    <input type="password" id="google_api_key" name="google_api_key">
                    
                    <label for="anthropic_api_key">Anthropic API Key:</label>
                    <input type="password" id="anthropic_api_key" name="anthropic_api_key">

                    <label for="together_api_key">Together.ai API Key:</label>
                    <input type="password" id="together_api_key" name="together_api_key">
                </fieldset>
                
                <fieldset>
                    <legend>Team Configuration</legend>
                    <label for="project_manager">Project Manager Model:</label>
                    <input type="text" id="project_manager" name="project_manager" required>
                    
                    <label for="senior">Senior Developer Model:</label>
                    <input type="text" id="senior" name="senior" required>
                    
                    <label for="juniors_count">Number of Juniors:</label>
                    <select id="juniors_count" name="juniors_count">
                        <option value="2">2</option>
                        <option value="3" selected>3</option>
                        <option value="4">4</option>
                        <option value="5">5</option>
                        <option value="6">6</option>
                    </select>
                    
                    <div id="junior_models_container">
                        <!-- Junior model inputs will be dynamically inserted here -->
                    </div>
                </fieldset>
                
                <button type="submit" class="button primary">Save Settings & Reload</button>
            </form>
        </main>

    </div>
    <script src="app.js"></script>
</body>
</html>
```

---

## File: `blueprint/frontend/styles.css`

```css
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

body {
    font-family: var(--font-family);
    background-color: var(--bg-color);
    color: var(--text-color);
    margin: 0;
    padding: 2rem;
    line-height: 1.6;
}

.container {
    max-width: 800px;
    margin: 0 auto;
    background: var(--card-bg);
    padding: 2rem;
    border-radius: 8px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}

header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid var(--border-color);
    padding-bottom: 1rem;
    margin-bottom: 2rem;
}

header h1 {
    margin: 0;
    color: var(--primary-color);
}

section {
    margin-bottom: 2rem;
}

h2 {
    border-bottom: 1px solid var(--border-color);
    padding-bottom: 0.5rem;
    margin-top: 0;
}

form {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

textarea, input[type="text"], input[type="password"], select {
    width: 100%;
    padding: 0.75rem;
    border: 1px solid var(--border-color);
    border-radius: 4px;
    font-size: 1rem;
    box-sizing: border-box;
}

textarea {
    resize: vertical;
}

.button {
    padding: 0.75rem 1.5rem;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 1rem;
    text-decoration: none;
    display: inline-block;
    text-align: center;
}

.button.primary {
    background-color: var(--primary-color);
    color: white;
}

.button.primary:hover {
    background-color: var(--primary-hover-color);
}

.button:disabled {
    background-color: #cccccc;
    cursor: not-allowed;
}

.build-status, .recent-builds {
    border: 1px solid var(--border-color);
    border-radius: 4px;
    padding: 1.5rem;
}

.phase-list {
    list-style: none;
    padding: 0;
}

.phase-list li {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 0.5rem 0;
    border-bottom: 1px solid #eee;
}

.phase-list li:last-child {
    border-bottom: none;
}

.status-icon {
    font-size: 1.2rem;
}
.status-icon.complete { color: var(--success-color); }
.status-icon.in-progress { color: var(--warning-color); animation: spin 1s linear infinite; }
.status-icon.failed { color: var(--error-color); }
.status-icon.pending { color: #ccc; }


@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

.phase-name {
    font-weight: bold;
    flex-grow: 1;
}

.phase-details {
    color: #6c757d;
    font-size: 0.9em;
}

#final-status {
    margin-top: 1.5rem;
    padding-top: 1.5rem;
    border-top: 1px solid var(--border-color);
}

.file-list {
    background-color: #f1f1f1;
    padding: 1rem;
    border-radius: 4px;
    max-height: 200px;
    overflow-y: auto;
    white-space: pre-wrap;
    word-break: break-all;
}

.error-message {
    color: var(--error-color);
    background-color: #f8d7da;
    border: 1px solid #f5c6cb;
    padding: 1rem;
    border-radius: 4px;
}

#recentBuildsList {
    list-style: none;
    padding: 0;
}

#recentBuildsList li {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.5rem;
    border-bottom: 1px solid #eee;
}
#recentBuildsList li:hover {
    background-color: #f1f1f1;
}

.build-meta {
    font-size: 0.8em;
    color: #6c757d;
}

/* Settings Page */
#settingsPage a {
    color: var(--primary-color);
    text-decoration: none;
    margin-bottom: 1rem;
    display: inline-block;
}
#settingsPage a:hover {
    text-decoration: underline;
}

fieldset {
    border: 1px solid var(--border-color);
    border-radius: 4px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
}

legend {
    font-weight: bold;
    padding: 0 0.5rem;
    color: var(--primary-color);
}

#settingsForm label {
    display: block;
    margin-top: 1rem;
    font-weight: 500;
}

#junior_models_container {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    margin-top: 0.5rem;
}
```

---

## File: `blueprint/src/api/routes.py`

```python
import logging
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional

from blueprint.src.storage.database import get_recent_builds, get_build_log
from blueprint.src.workflow.orchestrator import BuildManager
from blueprint.src.config.settings import settings, update_settings, get_full_config

router = APIRouter()
logger = logging.getLogger(__name__)
build_manager = BuildManager()

class BuildRequest(BaseModel):
    prompt: str

class BuildResponse(BaseModel):
    build_id: str
    message: str

@router.post("/builds", response_model=BuildResponse, status_code=202)
async def start_build(request: BuildRequest, background_tasks: BackgroundTasks):
    """Starts a new build process."""
    try:
        build_id = build_manager.create_build(request.prompt)
        background_tasks.add_task(build_manager.run_build, build_id)
        return BuildResponse(build_id=build_id, message="Build started.")
    except Exception as e:
        logger.error(f"Failed to start build: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to start build process.")

@router.get("/builds")
async def list_recent_builds():
    """Lists the most recent builds."""
    return await get_recent_builds()

@router.get("/builds/{build_id}/log")
async def get_log_for_build(build_id: str):
    """Gets the log for a specific build."""
    log = await get_build_log(build_id)
    if not log:
        raise HTTPException(status_code=404, detail="Build log not found.")
    return log

class ApiKeysUpdate(BaseModel):
    openai: Optional[str] = None
    google: Optional[str] = None
    anthropic: Optional[str] = None
    together: Optional[str] = None
    xai: Optional[str] = None

class JuniorsConfigUpdate(BaseModel):
    count: int
    models: List[str]

class TeamConfigUpdate(BaseModel):
    project_manager: str
    senior: str
    juniors: JuniorsConfigUpdate

class ConfigUpdateRequest(BaseModel):
    api_keys: Optional[ApiKeysUpdate] = None
    team: Optional[TeamConfigUpdate] = None

@router.get("/config")
async def get_config():
    """Gets the current configuration, redacting sensitive keys."""
    return get_full_config()

@router.put("/config")
async def put_config(request: ConfigUpdateRequest):
    """Updates the configuration."""
    try:
        update_settings(request.dict(exclude_unset=True))
        return {"message": "Configuration updated successfully. Restart the application for all changes to take effect."}
    except Exception as e:
        logger.error(f"Error updating configuration: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
```

---

## File: `blueprint/src/api/websocket.py`

```python
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from blueprint.src.workflow.orchestrator import build_manager

router = APIRouter()
logger = logging.getLogger(__name__)

@router.websocket("/ws/build/{build_id}")
async def websocket_endpoint(websocket: WebSocket, build_id: str):
    """WebSocket endpoint for streaming build progress."""
    await build_manager.register_websocket(build_id, websocket)
    try:
        while True:
            # Keep the connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        build_manager.unregister_websocket(build_id, websocket)
        logger.info(f"WebSocket disconnected for build {build_id}")
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

CONFIG_PATH = "config.yaml"

# --- Pydantic Models for Strong Typing and Validation ---

class ApiKeys(BaseModel):
    openai: Optional[str] = None
    google: Optional[str] = None
    together: Optional[str] = None
    xai: Optional[str] = None
    anthropic: Optional[str] = None

class JuniorsConfig(BaseModel):
    count: int = Field(..., ge=2, le=6)
    models: List[str]

class TeamConfig(BaseModel):
    project_manager: str
    senior: str
    juniors: JuniorsConfig

class WorkflowConfig(BaseModel):
    genesis_rounds: int = Field(1, ge=1)
    min_successful_juniors: int = Field(2, ge=1)
    max_retries: int = Field(2, ge=1)

class OutputConfig(BaseModel):
    format: str = "directory"
    path: str = "projects"

class ContextPathsConfig(BaseModel):
    project_manager: str
    senior: str
    junior: str

class Settings(BaseModel):
    api_keys: ApiKeys
    team: TeamConfig
    workflow: WorkflowConfig
    output: OutputConfig
    context_paths: ContextPathsConfig


def _env_replacer(match):
    var_name = match.group(1)
    value = os.environ.get(var_name)
    if value is None:
        logger.debug(f"Environment variable '{var_name}' not found, using empty string.")
        return ""
    return value

def load_settings() -> Settings:
    """Loads, substitutes env vars, and validates the YAML configuration."""
    load_dotenv()
    
    if not os.path.exists(CONFIG_PATH):
        raise FileNotFoundError(f"Configuration file not found at '{CONFIG_PATH}'. Please ensure it exists.")

    with open(CONFIG_PATH, 'r') as f:
        raw_config_str = f.read()

    processed_config_str = re.sub(r'\$\{(\w+)\}', _env_replacer, raw_config_str)
    config_dict = yaml.safe_load(processed_config_str)

    try:
        return Settings.model_validate(config_dict)
    except ValidationError as e:
        logger.error(f"Configuration validation error: {e}")
        raise

def update_settings(update_data: Dict):
    """Updates and saves the configuration file."""
    if not os.path.exists(CONFIG_PATH):
        raise FileNotFoundError(f"Cannot update settings: {CONFIG_PATH} not found.")

    with open(CONFIG_PATH, 'r') as f:
        config_dict = yaml.safe_load(f)

    # Deep merge the update_data into config_dict
    def merge(a, b):
        for key, value in b.items():
            if isinstance(value, dict) and key in a and isinstance(a[key], dict):
                merge(a[key], value)
            else:
                a[key] = value

    # Handle API keys separately to update env vars
    if 'api_keys' in update_data:
        api_keys_update = update_data.pop('api_keys')
        env_lines = []
        if os.path.exists('.env'):
            with open('.env', 'r') as f:
                env_lines = f.readlines()
        
        for provider, key in api_keys_update.items():
            env_var = f"{provider.upper()}_API_KEY"
            if key: # Update or add key
                found = False
                for i, line in enumerate(env_lines):
                    if line.startswith(f"{env_var}="):
                        env_lines[i] = f"{env_var}={key}\n"
                        found = True
                        break
                if not found:
                    env_lines.append(f"{env_var}={key}\n")
            else: # Remove key
                 env_lines = [line for line in env_lines if not line.startswith(f"{env_var}=")]
        
        with open('.env', 'w') as f:
            f.writelines(env_lines)
    
    merge(config_dict, update_data)

    with open(CONFIG_PATH, 'w') as f:
        yaml.dump(config_dict, f, default_flow_style=False, sort_keys=False)

    # Reload settings in the current process
    global settings
    settings = load_settings()
    logger.info("Configuration updated and reloaded.")

def get_full_config():
    """Returns the current config, redacting keys for safety."""
    config_data = settings.model_dump()
    for key in config_data['api_keys']:
        if config_data['api_keys'][key]:
            config_data['api_keys'][key] = "********"
    return config_data


settings = load_settings()
```

---

## File: `blueprint/src/llm/client.py`

```python
import os
from typing import Any, Dict, Optional

from openai import AsyncOpenAI
import google.generativeai as genai
import anthropic
from tenacity import retry, stop_after_attempt, wait_exponential
import logging

logger = logging.getLogger(__name__)

class LLMClient:
    _clients: Dict[str, Any] = {}

    def __init__(self, provider: str, api_key: Optional[str] = None):
        self.provider = provider
        self.api_key = api_key
        self._client = self._get_client()

    def _get_client(self):
        if self.provider in self._clients:
            return self._clients[self.provider]

        client = None
        key = self.api_key
        if not key:
            raise ValueError(f"API key for {self.provider} is not configured.")

        try:
            if self.provider == "openai":
                client = AsyncOpenAI(api_key=key)
            elif self.provider == "google":
                genai.configure(api_key=key)
                client = genai.GenerativeModel
            elif self.provider == "anthropic":
                client = anthropic.AsyncAnthropic(api_key=key)
            elif self.provider == "together":
                client = AsyncOpenAI(api_key=key, base_url="https://api.together.xyz/v1")
            elif self.provider == "xai":
                client = AsyncOpenAI(api_key=key, base_url="https://api.x.ai/v1")
            else:
                raise ValueError(f"Unsupported LLM provider: {self.provider}")
        except Exception as e:
            logger.error(f"Failed to initialize client for {self.provider}: {e}")
            raise

        self._clients[self.provider] = client
        return client

    @retry(wait=wait_exponential(multiplier=1, min=2, max=60), stop=stop_after_attempt(3))
    async def generate(self, model: str, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        logger.info(f"Invoking model {model} from provider {self.provider}...")
        try:
            if self.provider in ["openai", "together", "xai"]:
                response = await self._client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    max_tokens=4096,
                )
                content = response.choices[0].message.content
                usage = response.usage
                return {
                    "content": content,
                    "prompt_tokens": usage.prompt_tokens,
                    "completion_tokens": usage.completion_tokens,
                }
            elif self.provider == "anthropic":
                response = await self._client.messages.create(
                    model=model,
                    system=system_prompt,
                    messages=[{"role": "user", "content": user_prompt}],
                    max_tokens=4096,
                )
                content = response.content[0].text
                usage = response.usage
                return {
                    "content": content,
                    "prompt_tokens": usage.input_tokens,
                    "completion_tokens": usage.output_tokens,
                }
            elif self.provider == "google":
                gemini_model = self._client(model_name=model, system_instruction=system_prompt)
                response = await gemini_model.generate_content_async(user_prompt)
                content = response.text
                # Note: Google's async client doesn't directly return token counts in the same way.
                # We can estimate or make a separate call if needed, but for now, we'll omit them for simplicity.
                return {
                    "content": content,
                    "prompt_tokens": 0, # Placeholder
                    "completion_tokens": 0, # Placeholder
                }
        except Exception as e:
            logger.error(f"LLM generation failed for model {model}: {e}", exc_info=True)
            raise
        
        raise NotImplementedError(f"Generation for provider {self.provider} not implemented.")
```

---

## File: `blueprint/src/storage/database.py`

```python
import aiosqlite
import json
from datetime import datetime, timezone

DB_PATH = "projects/builds.db"

async def initialize_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS builds (
                id TEXT PRIMARY KEY,
                prompt TEXT NOT NULL,
                status TEXT NOT NULL,
                output_path TEXT,
                output_format TEXT,
                total_time REAL,
                total_cost REAL,
                created_at TEXT NOT NULL
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS phase_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                build_id TEXT NOT NULL,
                phase_number INTEGER NOT NULL,
                phase_name TEXT NOT NULL,
                status TEXT NOT NULL,
                message TEXT,
                details TEXT,
                time_elapsed REAL,
                cost_so_far REAL,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (build_id) REFERENCES builds(id)
            )
        """)
        await db.commit()

async def create_build_record(build_id: str, prompt: str, output_format: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO builds (id, prompt, status, output_format, created_at) VALUES (?, ?, ?, ?, ?)",
            (build_id, prompt, "running", output_format, datetime.now(timezone.utc).isoformat())
        )
        await db.commit()

async def log_phase_update(build_id: str, phase_number: int, phase_name: str, status: str, message: str, details: dict, time_elapsed: float, cost_so_far: float):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """INSERT INTO phase_logs (build_id, phase_number, phase_name, status, message, details, time_elapsed, cost_so_far, timestamp)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (build_id, phase_number, phase_name, status, message, json.dumps(details), time_elapsed, cost_so_far, datetime.now(timezone.utc).isoformat())
        )
        await db.commit()

async def update_build_status(build_id: str, status: str, output_path: str = None, total_time: float = None, total_cost: float = None):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE builds SET status = ?, output_path = ?, total_time = ?, total_cost = ? WHERE id = ?",
            (status, output_path, total_time, total_cost, build_id)
        )
        await db.commit()

async def get_recent_builds(limit: int = 10):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM builds ORDER BY created_at DESC LIMIT ?", (limit,)) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

async def get_build_log(build_id: str):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM phase_logs WHERE build_id = ? ORDER BY timestamp ASC", (build_id,)) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
```

---

## File: `blueprint/src/storage/filesystem.py`

```python
import os
import zipfile
from pathlib import Path
import logging
import re
import shutil

logger = logging.getLogger(__name__)

def create_project_workspace(base_path: str, project_id: str) -> Path:
    """Creates a dedicated directory for a new project."""
    project_dir = Path(base_path) / project_id
    project_dir.mkdir(parents=True, exist_ok=True)
    return project_dir

def parse_and_write_files(response_content: str, workspace_path: Path) -> list[str]:
    """
    Parses an LLM response for markdown code blocks and writes them to files.
    Format: ## File: path/to/filename.ext\n```lang\n...content...\n```
    """
    files_created = []
    # Regex to find file blocks
    pattern = r"##\s*File:\s*(.+?)\s*\n```(?:\w+\n)?(.*?)```"
    matches = re.findall(pattern, response_content, re.DOTALL)

    if not matches:
        logger.warning(f"No file blocks found in response for workspace {workspace_path}")
        return []

    for filename_str, content in matches:
        # Sanitize filename
        filename_str = filename_str.strip()
        if ".." in filename_str or filename_str.startswith("/"):
            logger.warning(f"Skipping potentially unsafe file path: {filename_str}")
            continue

        file_path = workspace_path / filename_str
        file_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            file_path.write_text(content.strip(), encoding='utf-8')
            files_created.append(str(file_path.relative_to(workspace_path.parent.parent)))
            logger.info(f"Written file: {file_path}")
        except IOError as e:
            logger.error(f"Failed to write file {file_path}: {e}")

    return files_created

def package_deliverable(project_path: Path, output_format: str) -> str:
    """Packages the final deliverable as a directory or ZIP file."""
    if output_format == "zip":
        zip_path = project_path.with_suffix('.zip')
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(project_path):
                for file in files:
                    file_path = Path(root) / file
                    arcname = file_path.relative_to(project_path)
                    zipf.write(file_path, arcname)
        # Remove the original directory after zipping
        shutil.rmtree(project_path)
        return str(zip_path)
    else: # "directory"
        return str(project_path)

def list_files_in_project(project_path: Path) -> list[str]:
    """Recursively lists all files in a project directory."""
    if not project_path.is_dir():
        return []
    
    file_list = []
    for path in sorted(project_path.rglob('*')):
        if path.is_file():
            # Create a relative path string
            relative_path = path.relative_to(project_path)
            file_list.append(str(relative_path))
    return file_list

def get_project_files_for_context(project_path: Path) -> str:
    """Reads all files from a project workspace and formats them for an LLM context."""
    context_str = ""
    if not project_path.is_dir():
        return ""
        
    for path in sorted(project_path.rglob('*')):
        if path.is_file():
            try:
                content = path.read_text(encoding='utf-8')
                relative_path = path.relative_to(project_path)
                context_str += f"## File: {relative_path}\n```\n{content}\n```\n\n"
            except Exception as e:
                logger.warning(f"Could not read file {path} for context: {e}")
    return context_str
```

---

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

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [%(name)s] - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Code to run on startup
    logger.info("Blueprint application starting up...")
    # Ensure project and database directories exist
    Path(settings.output.path).mkdir(exist_ok=True)
    Path(settings.output.path).joinpath('db').mkdir(exist_ok=True)
    # Adjust DB path to be inside the projects dir
    global DB_PATH
    from blueprint.src.storage import database
    database.DB_PATH = str(Path(settings.output.path) / "builds.db")
    await initialize_db()
    logger.info("Database initialized.")
    yield
    # Code to run on shutdown
    logger.info("Blueprint application shutting down.")

app = FastAPI(
    title="Blueprint v2.0.1",
    lifespan=lifespan
)

# API Routers
app.include_router(api_router, prefix="/api")
app.include_router(ws_router)

# Static Files
# Serve the main frontend
app.mount("/", StaticFiles(directory="blueprint/frontend", html=True), name="frontend")
# Serve the project output files for viewing
app.mount("/projects-static", StaticFiles(directory=settings.output.path), name="projects-static")
# Serve zipped project files for download
app.mount("/projects", StaticFiles(directory=settings.output.path), name="projects-download")


if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Blueprint server with Uvicorn...")
    uvicorn.run("blueprint.src.main:app", host="0.0.0.0", port=8000, reload=True)
```

---

## File: `blueprint/src/workflow/orchestrator.py`

```python
import asyncio
import logging
import uuid
import time
from typing import Dict, List, Any, Coroutine, Set
from fastapi import WebSocket

from blueprint.src.config.settings import settings
from blueprint.src.storage import database, filesystem
from blueprint.src.llm.client import LLMClient
from .phases import run_anchor_docs_phase, run_genesis_phase, run_synthesis_phase, run_consensus_phase, run_output_phase

logger = logging.getLogger(__name__)

class Build:
    """Represents the state of a single build."""
    def __init__(self, build_id: str, prompt: str):
        self.id = build_id
        self.prompt = prompt
        self.status = "running"
        self.websockets: Set[WebSocket] = set()
        self.start_time = time.time()
        self.cost = 0.0
        self.project_path = filesystem.create_project_workspace(settings.output.path, self.id)
        self.phase_details: Dict[str, Any] = {}

    async def register(self, websocket: WebSocket):
        await websocket.accept()
        self.websockets.add(websocket)

    def unregister(self, websocket: WebSocket):
        self.websockets.remove(websocket)

    async def send_progress_update(self, phase_number: int, phase_name: str, status: str, message: str, details: Dict = None):
        """Sends a progress update to all connected clients and logs it."""
        elapsed = time.time() - self.start_time
        update = {
            "type": "progress",
            "build_id": self.id,
            "phase_number": phase_number,
            "phase": phase_name,
            "status": status,
            "message": message,
            "details": details or {},
            "time_elapsed": elapsed,
            "cost_so_far": self.cost,
        }
        await self._broadcast(update)
        await database.log_phase_update(
            self.id, phase_number, phase_name, status, message, details, elapsed, self.cost
        )

    async def send_final_output(self, output: Dict):
        """Sends the final output details."""
        await self._broadcast({"type": "final_output", "output": output})

    async def send_error(self, phase: str, message: str):
        """Sends an error message."""
        await self._broadcast({"type": "error", "phase": phase, "message": message})

    async def _broadcast(self, message: Dict):
        """Broadcasts a message to all connected websockets."""
        disconnected_sockets = set()
        for websocket in self.websockets:
            try:
                await websocket.send_json(message)
            except Exception:
                disconnected_sockets.add(websocket)
        for ws in disconnected_sockets:
            self.unregister(ws)

class BuildManager:
    """Manages all active and past builds."""
    def __init__(self):
        self.active_builds: Dict[str, Build] = {}

    def create_build(self, prompt: str) -> str:
        build_id = str(uuid.uuid4())
        build = Build(build_id=build_id, prompt=prompt)
        self.active_builds[build_id] = build
        return build_id

    async def register_websocket(self, build_id: str, websocket: WebSocket):
        if build_id in self.active_builds:
            await self.active_builds[build_id].register(websocket)
        else:
            await websocket.close(code=1011, reason="Build not found")

    def unregister_websocket(self, build_id: str, websocket: WebSocket):
        if build_id in self.active_builds:
            self.active_builds[build_id].unregister(websocket)

    async def run_build(self, build_id: str):
        build = self.active_builds.get(build_id)
        if not build:
            logger.error(f"Attempted to run non-existent build: {build_id}")
            return

        await database.create_build_record(build.id, build.prompt, settings.output.format)
        
        try:
            # Phase 1: Anchor Docs
            context = await run_anchor_docs_phase(build)
            build.cost += context.get("cost", 0.0)

            # Phase 2: Genesis
            context = await run_genesis_phase(build, context)
            build.cost += context.get("cost", 0.0)

            # Phase 3: Synthesis
            context = await run_synthesis_phase(build, context)
            build.cost += context.get("cost", 0.0)

            # Phase 4: Consensus
            context = await run_consensus_phase(build, context)
            build.cost += context.get("cost", 0.0)

            # Phase 5: Output
            context = await run_output_phase(build, context)
            build.cost += context.get("cost", 0.0)
            
            # Finalize
            total_time = time.time() - build.start_time
            await database.update_build_status(
                build.id, "complete", context["output_path"], total_time, build.cost
            )
            final_output_details = {
                "build_id": build.id,
                "total_time": total_time,
                "total_cost": build.cost,
                "files": context["files"],
                "download_path": context["output_path"] if settings.output.format == 'zip' else None
            }
            await build.send_final_output(final_output_details)

        except Exception as e:
            logger.error(f"Build {build_id} failed: {e}", exc_info=True)
            current_phase = build.phase_details.get("name", "Unknown")
            await build.send_error(phase=current_phase, message=str(e))
            await database.update_build_status(build.id, "failed")
        finally:
            # Clean up
            if build_id in self.active_builds:
                del self.active_builds[build_id]

build_manager = BuildManager()
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
from blueprint.src.storage import filesystem
from .orchestrator import Build

logger = logging.getLogger(__name__)

def get_llm_client(model_identifier: str) -> LLMClient:
    """Helper to get an LLM client instance for a given model."""
    provider, _ = model_identifier.split('/', 1)
    api_key = getattr(settings.api_keys, provider, None)
    return LLMClient(provider, api_key)

async def run_phase(build: Build, phase_number: int, phase_name: str, coroutine):
    """Wrapper to run a phase, updating status and handling errors."""
    build.phase_details = {"name": phase_name, "number": phase_number}
    await build.send_progress_update(phase_number, phase_name, "in_progress", f"Starting {phase_name} phase...")
    try:
        result = await coroutine
        await build.send_progress_update(phase_number, phase_name, "complete", f"{phase_name} phase completed.")
        return result
    except Exception as e:
        logger.error(f"Error in {phase_name} for build {build.id}: {e}", exc_info=True)
        await build.send_progress_update(phase_number, phase_name, "failed", f"Error during {phase_name}: {e}")
        raise

async def run_anchor_docs_phase(build: Build) -> Dict[str, Any]:
    """Phase 1: Project Manager creates the requirements document."""
    async def task():
        pm_model_id = settings.team.project_manager
        client = get_llm_client(pm_model_id)
        
        with open(settings.context_paths.project_manager, 'r') as f:
            system_prompt = f.read()

        response = await client.generate(
            model=pm_model_id.split('/', 1)[1],
            system_prompt=system_prompt,
            user_prompt=build.prompt
        )
        
        pm_workspace = build.project_path / "project_manager"
        filesystem.parse_and_write_files(response['content'], pm_workspace)
        
        req_path = pm_workspace / "01_requirements.md"
        if not req_path.exists():
            raise FileNotFoundError("Project Manager failed to create the requirements document.")
            
        return {
            "requirements_content": req_path.read_text(),
            "cost": 0.005 # Placeholder cost
        }
    return await run_phase(build, 1, "Anchor Docs", task())

async def run_genesis_phase(build: Build, context: Dict[str, Any]) -> Dict[str, Any]:
    """Phase 2: Juniors create parallel implementations."""
    async def task():
        with open(settings.context_paths.junior, 'r') as f:
            system_prompt = f.read()
        
        user_prompt = f"Here are the project requirements:\n\n{context['requirements_content']}"
        
        tasks = []
        for i in range(settings.team.juniors.count):
            model_id = settings.team.juniors.models[i]
            client = get_llm_client(model_id)
            tasks.append(client.generate(
                model=model_id.split('/', 1)[1],
                system_prompt=system_prompt,
                user_prompt=user_prompt
            ))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        successful_juniors = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Junior {i} failed: {result}")
            else:
                junior_workspace = build.project_path / f"junior_{i}"
                filesystem.parse_and_write_files(result['content'], junior_workspace)
                successful_juniors.append(i)
        
        if len(successful_juniors) < settings.workflow.min_successful_juniors:
            raise RuntimeError(f"Genesis failed: Only {len(successful_juniors)}/{settings.team.juniors.count} juniors succeeded.")
            
        return {
            "successful_juniors": successful_juniors,
            "cost": 0.01 * len(successful_juniors) # Placeholder
        }
    return await run_phase(build, 2, "Genesis", task())

async def run_synthesis_phase(build: Build, context: Dict[str, Any]) -> Dict[str, Any]:
    """Phase 3: Senior developer synthesizes junior solutions."""
    async def task():
        senior_model_id = settings.team.senior
        client = get_llm_client(senior_model_id)
        
        with open(settings.context_paths.senior, 'r') as f:
            system_prompt = f.read()
        
        synthesis_context = f"Requirements:\n{context['requirements_content']}\n\n"
        for i in context['successful_juniors']:
            junior_workspace = build.project_path / f"junior_{i}"
            synthesis_context += f"--- JUNIOR {i} SUBMISSION ---\n"
            synthesis_context += filesystem.get_project_files_for_context(junior_workspace)
            
        response = await client.generate(
            model=senior_model_id.split('/', 1)[1],
            system_prompt=system_prompt,
            user_prompt=synthesis_context
        )
        
        senior_workspace = build.project_path / "senior"
        filesystem.parse_and_write_files(response['content'], senior_workspace)
        
        return {"cost": 0.01} # Placeholder
    return await run_phase(build, 3, "Synthesis", task())

async def run_consensus_phase(build: Build, context: Dict[str, Any]) -> Dict[str, Any]:
    """Phase 4: Juniors review the senior's solution."""
    async def task():
        with open(settings.context_paths.junior, 'r') as f:
            system_prompt = f.read() # The junior context includes consensus instructions
            
        senior_workspace = build.project_path / "senior"
        senior_solution = filesystem.get_project_files_for_context(senior_workspace)
        
        user_prompt = f"Please review the following synthesized solution against the original requirements.\n\nRequirements:\n{context['requirements_content']}\n\nSynthesized Solution:\n{senior_solution}"
        
        tasks = []
        for i in range(settings.team.juniors.count):
            model_id = settings.team.juniors.models[i]
            client = get_llm_client(model_id)
            tasks.append(client.generate(
                model=model_id.split('/', 1)[1],
                system_prompt=system_prompt,
                user_prompt=user_prompt
            ))
            
        results = await asyncio.gather(*tasks)
        
        # For now, we just log the votes. A future version could use this for a revision loop.
        for i, result in enumerate(results):
            try:
                vote = json.loads(result['content'].strip().replace("```json", "").replace("```", ""))
                logger.info(f"Junior {i} vote: {vote}")
            except json.JSONDecodeError:
                logger.warning(f"Could not parse vote from Junior {i}: {result['content']}")

        return {"cost": 0.005 * len(results)} # Placeholder
    return await run_phase(build, 4, "Consensus", task())

async def run_output_phase(build: Build, context: Dict[str, Any]) -> Dict[str, Any]:
    """Phase 5: Package the final deliverable."""
    async def task():
        senior_workspace = build.project_path / "senior"
        output_path = filesystem.package_deliverable(senior_workspace, settings.output.format)
        files = filesystem.list_files_in_project(Path(output_path)) if settings.output.format == "directory" else []
        
        return {
            "output_path": output_path,
            "files": files,
            "cost": 0.0
        }
    return await run_phase(build, 5, "Output", task())
```

---

## File: `Dockerfile`

```dockerfile
# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Create a non-root user
RUN useradd -m -d /app/user -s /bin/bash appuser
USER appuser
WORKDIR /app/user

# Copy the requirements file into the container at /app/user
COPY --chown=appuser:appuser requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir --user -r requirements.txt

# Copy the application code into the container
COPY --chown=appuser:appuser . .

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Define environment variable to ensure Python outputs are sent straight to the terminal
ENV PYTHONUNBUFFERED 1
ENV PATH="/app/user/.local/bin:${PATH}"

# Run main.py when the container launches
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
      # Mount the projects directory to persist outputs
      - ./projects:/app/user/projects
      # Mount config and contexts for live changes without rebuild
      - ./blueprint/config.yaml:/app/user/config.yaml
      - ./blueprint/contexts:/app/user/blueprint/contexts
    env_file:
      - .env
    healthcheck:
      test: ["CMD-SHELL", "curl -f http://localhost:8000/api/builds || exit 1"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 20s
```

---

## File: `install.sh`

```bash
#!/bin/bash

# This script builds and runs the Blueprint v2.0.1 application using Docker.

# --- Configuration ---
# Name for the Docker image and container
IMAGE_NAME="blueprint-v2-image"
CONTAINER_NAME="blueprint-v2"

# --- Functions ---

# Function to print colored messages
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

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# --- Pre-flight Checks ---
print_msg "yellow" "--- Running Pre-flight Checks ---"

# Check for Docker
if ! command_exists docker; then
    print_msg "red" "Error: Docker is not installed. Please install Docker to continue."
    print_msg "red" "See: https://docs.docker.com/get-docker/"
    exit 1
fi
print_msg "green" "✅ Docker is installed."

# Check for Docker Compose
if ! command_exists docker-compose; then
    print_msg "red" "Error: docker-compose is not installed. Please install Docker Compose to continue."
    print_msg "red" "See: https://docs.docker.com/compose/install/"
    exit 1
fi
print_msg "green" "✅ Docker Compose is installed."

# Check for .env file
if [ ! -f .env ]; then
    print_msg "yellow" "Warning: .env file not found. Creating a template."
    print_msg "yellow" "Please fill in your API keys in the '.env' file before starting."
    cat > .env << EOL
# API Keys for Blueprint LLM Providers
# Get your keys from the respective provider websites.
# You only need to fill in the ones you want to use.
OPENAI_API_KEY=
GOOGLE_API_KEY=
ANTHROPIC_API_KEY=
TOGETHER_API_KEY=
XAI_API_KEY=
EOL
    print_msg "green" "✅ .env file created. Please edit it with your API keys."
    exit 0
fi
print_msg "green" "✅ .env file found."


# --- Installation ---
print_msg "yellow" "\n--- Starting Blueprint v2.0.1 Installation ---"

# Stop and remove any existing container with the same name
if [ "$(docker ps -q -f name=${CONTAINER_NAME})" ]; then
    print_msg "yellow" "Stopping existing container..."
    docker-compose down
fi

# Build the Docker image
print_msg "yellow" "Building Docker image '${IMAGE_NAME}'..."
docker-compose build
if [ $? -ne 0 ]; then
    print_msg "red" "Error: Docker image build failed."
    exit 1
fi
print_msg "green" "✅ Docker image built successfully."

# Start the container in detached mode
print_msg "yellow" "Starting Blueprint container '${CONTAINER_NAME}'..."
docker-compose up -d
if [ $? -ne 0 ]; then
    print_msg "red" "Error: Failed to start the Docker container."
    exit 1
fi
print_msg "green" "✅ Blueprint container started successfully."

# --- Post-installation ---
print_msg "yellow" "\n--- Installation Complete ---"
print_msg "green" "Blueprint v2.0.1 is now running!"
print_msg "green" "You can access the web UI at: http://localhost:8000"
print_msg "yellow" "\nTo view logs, run: docker-compose logs -f"
print_msg "yellow" "To stop the application, run: docker-compose down"

exit 0
```

---

## File: `pyproject.toml`

```toml
[tool.poetry]
name = "blueprint-v2"
version = "2.0.1"
description = "Autonomous multi-agent system for creating digital assets."
authors = ["Genesis Developer <dev@example.com>"]
readme = "README.md"

[tool.poetry.dependencies]
python = "^3.11"
fastapi = "^0.111.0"
uvicorn = {extras = ["standard"], version = "^0.30.1"}
websockets = "^12.0"
python-dotenv = "^1.0.1"
pyyaml = "^6.0.1"
pydantic = "^2.8.2"
aiosqlite = "^0.20.0"
openai = "^1.35.13"
google-generativeai = "^0.7.2"
anthropic = "^0.29.0"
tenacity = "^8.5.0"
pytest = "^8.2.2"
pytest-asyncio = "^0.23.7"
httpx = "^0.27.0"
aiofiles = "^23.2.1"
fastapi-staticfiles = "^0.0.1"


[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
```

---

## File: `requirements.txt`

```txt
fastapi==0.111.0
uvicorn[standard]==0.30.1
websockets==12.0
python-dotenv==1.0.1
PyYAML==6.0.1
pydantic==2.8.2
aiosqlite==0.20.0
openai==1.35.13
google-generativeai==0.7.2
anthropic==0.29.0
tenacity==8.5.0
pytest==8.2.2
pytest-asyncio==0.23.7
httpx==0.27.0
aiofiles==23.2.1
fastapi-staticfiles==0.0.1
```

---

## File: `test.sh`

```bash
#!/bin/bash

# This script runs the test suite for Blueprint v2.0.1.
# It starts a test instance of the application, runs pytest, and then shuts down.

# --- Configuration ---
COMPOSE_FILE="docker-compose.test.yml"
CONTAINER_NAME="blueprint-v2-test"
EXIT_CODE=0

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

cleanup() {
    print_msg "yellow" "\n--- Cleaning up test environment ---"
    docker-compose -f ${COMPOSE_FILE} down -v --remove-orphans
    rm -f ${COMPOSE_FILE}
    print_msg "green" "✅ Test environment cleaned up."
}

# --- Main Script ---

# Ensure cleanup runs on exit
trap cleanup EXIT

# Check for .env file, which is required for tests
if [ ! -f .env ]; then
    print_msg "red" "Error: .env file not found."
    print_msg "red" "Please create a .env file with your API keys to run the tests."
    exit 1
fi

print_msg "yellow" "--- Setting up test environment ---"

# Create a docker-compose file for testing that runs the pytest command
cat > ${COMPOSE_FILE} << EOL
version: '3.8'
services:
  test:
    build: .
    container_name: ${CONTAINER_NAME}
    volumes:
      - ./projects_test:/app/user/projects
    env_file:
      - .env
    command: ["pytest", "-v"]
EOL

print_msg "yellow" "Building test container..."
docker-compose -f ${COMPOSE_FILE} build
if [ $? -ne 0 ]; then
    print_msg "red" "Error: Test container build failed."
    exit 1
fi

print_msg "yellow" "\n--- Running Pytest Suite ---"
docker-compose -f ${COMPOSE_FILE} run --rm test
EXIT_CODE=$?

if [ ${EXIT_CODE} -eq 0 ]; then
    print_msg "green" "\n--- ✅ All tests passed successfully! ---"
else
    print_msg "red" "\n--- ❌ Some tests failed. ---"
fi

exit ${EXIT_CODE}
```

---

## File: `tests/conftest.py`

```python
import pytest
import pytest_asyncio
from httpx import AsyncClient
from pathlib import Path
import shutil

# Make sure the main app is importable
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from blueprint.src.main import app
from blueprint.src.config.settings import settings
from blueprint.src.storage import database

# Set a dedicated test database path
TEST_DB_PATH = "projects_test/test_builds.db"
database.DB_PATH = TEST_DB_PATH

@pytest_asyncio.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture(scope="function")
async def test_client():
    """Create an async test client for the FastAPI app."""
    # Ensure the test projects directory is clean before each test
    test_projects_dir = Path("projects_test")
    if test_projects_dir.exists():
        shutil.rmtree(test_projects_dir)
    test_projects_dir.mkdir(parents=True, exist_ok=True)
    
    # Override settings for testing
    settings.output.path = str(test_projects_dir)
    
    # Initialize a clean database for each test
    await database.initialize_db()

    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

    # Clean up after the test
    if test_projects_dir.exists():
        shutil.rmtree(test_projects_dir)
```

---

## File: `tests/test_workflow_integration.py`

```python
import pytest
import asyncio
from fastapi import WebSocket
from pathlib import Path
import json

from blueprint.src.workflow.orchestrator import BuildManager

# This is a more complex integration test that simulates a full build process.

class MockWebSocket:
    def __init__(self):
        self.sent_messages = []
        self.accepted = False
        self.closed = False

    async def accept(self):
        self.accepted = True

    async def send_json(self, data):
        self.sent_messages.append(data)

    async def close(self, code=1000, reason=None):
        self.closed = True

@pytest.mark.asyncio
@pytest.mark.integration
async def test_full_workflow_hello_world(test_client):
    """
    Tests the full multi-agent workflow by asking it to create a Python Hello World program.
    This requires valid API keys in the .env file.
    """
    prompt = "Create a simple Python program that prints 'Hello, World!' to the console. Include a README.md file."
    
    build_manager = BuildManager()
    build_id = build_manager.create_build(prompt)
    
    mock_ws = MockWebSocket()
    await build_manager.register_websocket(build_id, mock_ws)

    # Run the build in the background
    await build_manager.run_build(build_id)

    # Assertions
    assert len(mock_ws.sent_messages) > 5 # Should have at least one message per phase
    
    final_message = mock_ws.sent_messages[-1]
    assert final_message['type'] == 'final_output'
    
    output_details = final_message['output']
    assert output_details['total_time'] > 0
    # Cost can be 0 if using free models, so we don't assert on it
    
    # Check that the output directory and files were created
    project_path = Path(f"projects_test/{build_id}/senior")
    assert project_path.exists()
    
    main_py = project_path / "main.py"
    readme_md = project_path / "README.md"
    
    assert main_py.exists()
    assert readme_md.exists()
    
    main_content = main_py.read_text()
    assert 'print("Hello, World!")' in main_content

    readme_content = readme_md.read_text()
    assert "Hello, World" in readme_content

@pytest.mark.asyncio
@pytest.mark.integration
async def test_full_workflow_requirements_doc(test_client):
    """
    Tests the workflow by asking it to create a requirements document based on the anchor context.
    """
    # A snippet from the anchor context
    prompt = """
    Create a requirements document for a system with the following workflow:
    1. A Project Manager LLM receives user requirements and asks clarifying questions. The conversation becomes the requirements.
    2. In a Genesis phase, multiple Junior developers build the digital asset in parallel based on the requirements.
    3. In a Synthesis phase, a Senior developer combines the best ideas into one version.
    4. In a Review phase, Juniors critique the synthesized version. This can loop until approval.
    5. The final approved product is output to the user.
    The document should be in Markdown format.
    """
    
    build_manager = BuildManager()
    build_id = build_manager.create_build(prompt)
    
    mock_ws = MockWebSocket()
    await build_manager.register_websocket(build_id, mock_ws)
    
    await build_manager.run_build(build_id)
    
    final_message = mock_ws.sent_messages[-1]
    assert final_message['type'] == 'final_output'
    
    project_path = Path(f"projects_test/{build_id}/senior")
    assert project_path.exists()
    
    # Check for a markdown file in the output
    md_files = list(project_path.glob("*.md"))
    assert len(md_files) > 0, "No markdown file found in the output"
    
    req_doc_content = md_files[0].read_text()
    assert "Genesis" in req_doc_content
    assert "Synthesis" in req_doc_content
    assert "Project Manager" in req_doc_content
```

---

## File: `README.md`

```md
# Blueprint v2.0.1

Blueprint is an autonomous multi-agent system designed to create complete, production-ready digital assets from natural language descriptions. Instead of a back-and-forth process with a single AI, you provide a prompt, and a team of specialized AI agents collaborates to build the final product.

This version (v2.0.1) focuses on establishing a reliable core workflow and providing a simple, intuitive web interface for interaction.

## Features (v2.0.1)

-   **Reliable 5-Phase Workflow**: A robust, multi-agent process for creating digital assets:
    1.  **Anchor Docs**: A Project Manager AI analyzes your request and creates a formal requirements document.
    2.  **Genesis**: A team of Junior Developer AIs work in parallel to create independent solutions.
    3.  **Synthesis**: A Senior Developer AI analyzes all solutions and synthesizes them into a single, superior version.
    4.  **Consensus**: The Junior team reviews the final version for quality assurance.
    5.  **Output**: The final, approved asset is packaged and delivered.
-   **Simple Web UI**: An intuitive, single-page web application for submitting projects, monitoring progress in real-time, and accessing results.
-   **Configurable AI Team**: Easily configure the models used for the Project Manager, Senior, and Junior roles via a `config.yaml` file.
-   **Multi-Provider Support**: Integrates with major LLM providers including OpenAI, Google, Anthropic, and Together.ai.
-   **Dockerized**: The entire application is containerized with Docker for easy, consistent, and isolated deployment.
-   **Persistent History**: Build history and results are stored locally in a SQLite database.

## Installation and Usage

### Prerequisites

-   [Docker](https://docs.docker.com/get-docker/)
-   [Docker Compose](https://docs.docker.com/compose/install/)

### Quick Start

1.  **Clone the Repository**:
    ```bash
    git clone <repository_url>
    cd blueprint-v2
    ```

2.  **Configure API Keys**:
    The installation script will create a `.env` file for you if it doesn't exist. Open this file and add your API keys from your desired LLM providers.
    ```env
    # .env
    OPENAI_API_KEY=sk-...
    GOOGLE_API_KEY=AIza...
    ANTHROPIC_API_KEY=sk-ant-...
    TOGETHER_API_KEY=...
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

### Interacting with Blueprint

-   **Start a Build**: Enter a description of the digital asset you want to create in the text area and click "Start Build".
-   **Monitor Progress**: The UI will display the status of each phase of the workflow in real-time.
-   **View Results**: Completed projects will appear in the "Recent Builds" list. You can view the generated files or download a ZIP archive.
-   **Configure Settings**: Click the "Settings" link to configure your API keys and the AI models used for each role in the development team.

### Managing the Application

-   **View Logs**:
    ```bash
    docker-compose logs -f
    ```
-   **Stop the Application**:
    ```bash
    docker-compose down
    ```

## Running Tests

The project includes a comprehensive test suite that validates the functionality of the entire workflow.

1.  **Ensure API keys are in `.env`**: The integration tests require valid API keys to run.
2.  **Run the Test Script**:
    ```bash
    chmod +x test.sh
    ./test.sh
    ```
    This will spin up a dedicated test container, run `pytest`, and then clean up the environment.

## Project Structure

```
.
├── blueprint/
│   ├── contexts/         # System prompts for AI roles
│   ├── frontend/         # HTML, CSS, JS for the web UI
│   ├── src/              # Python source code
│   │   ├── api/          # FastAPI routes and WebSocket handlers
│   │   ├── config/       # Pydantic settings and config management
│   │   ├── llm/          # LLM client and provider logic
│   │   ├── storage/      # Database and filesystem operations
│   │   └── workflow/     # Core 5-phase workflow orchestrator and logic
│   └── config.yaml       # Main application configuration
├── projects/             # Output directory for generated projects
├── tests/                # Pytest test suite
├── Dockerfile            # Defines the application container
├── docker-compose.yml    # Orchestrates the application service
├── install.sh            # Installation and startup script
├── test.sh               # Test runner script
└── README.md             # This file
```
```
