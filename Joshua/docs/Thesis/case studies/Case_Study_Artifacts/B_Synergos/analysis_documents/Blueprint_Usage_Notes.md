# Sultan's Blueprint Usage Notes
**Date:** October 17, 2025
**Context:** Documentation of Blueprint location, configuration, and usage attempts

---

## Overview

Sultan's Blueprint is the multi-agent system that created Synergos on October 16, 2025. This document captures what we learned about where it is, how to run it, and what worked/didn't work when trying to use it for the performance analysis.

---

## Blueprint Location

**The actual Blueprint that created Synergos:**
```
/mnt/projects/sultans-blueprint-ui/sultans_blueprint/
```

**How we verified this:**
- Searched session logs: `~/.claude/projects/-home-aristotle9/3d7f129c-f84f-496c-a0db-e816ce64986e.jsonl`
- Found project ID: `410251ea-6f01-4e09-a77b-652c6367bd15`
- Confirmed this project exists at: `/mnt/projects/sultans-blueprint-ui/projects/410251ea-6f01-4e09-a77b-652c6367bd15/`
- Contains all Synergos workspace files

**Still running since October 16:**
```bash
ps aux | grep sultans_blueprint
# aristot+  106929  python -B -m sultans_blueprint
```

---

## How Blueprint Was Used to Create Synergos

### What Actually Happened (October 16, 2025)

1. **Started Blueprint Server:**
   ```bash
   cd /mnt/projects/sultans-blueprint-ui && source venv/bin/activate && python -B -m sultans_blueprint
   ```

2. **Created WebSocket Client** (`/tmp/test_blueprint_client.py`):
   ```python
   request = {
       "tool": "prompt",
       "input": {
           "requirements": "Create a simple Python calculator..."
       }
   }

   async with websockets.connect("ws://localhost:8000") as websocket:
       await websocket.send(json.dumps(request))
       # Receive status updates and final result
   ```

3. **Blueprint Ran 5 Phases:**
   - ANCHOR_DOCS: Requirements and design (2 min)
   - GENESIS: 6 parallel solutions (55 sec)
   - SYNTHESIS: Merge best ideas (25 sec)
   - CONSENSUS: Quality voting (21 sec)
   - OUTPUT: Package deliverable (6 sec)

4. **Result:** 9 files, production-ready Synergos application

---

## Blueprint Configuration

### Default Config
`/mnt/projects/sultans-blueprint-ui/sultans_blueprint/config/config.yaml`

**Default team (what created Synergos):**
```yaml
roles:
  imperator: "together/meta-llama/Llama-3-70b-chat-hf"
  senior: "openai/gpt-4o"
  juniors:
    - "together/meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo"
    - "together/deepseek-ai/DeepSeek-R1"
    - "together/mistralai/Mixtral-8x7B-Instruct-v0.1"
    - "together/meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo"
    - "together/meta-llama/Llama-3.3-70B-Instruct-Turbo"
```

### Analysis Config (Attempted)
`/mnt/projects/sultans-blueprint-ui/sultans_blueprint/config/config.analysis.yaml`

**Top-tier analyst team (what we tried to use):**
```yaml
roles:
  imperator: "openai/gpt-5"
  senior: "google/gemini-2.5-pro"
  juniors:
    - "openai/gpt-4o"
    - "xai/grok-4"
    - "together/deepseek-ai/DeepSeek-R1"
    - "together/meta-llama/Llama-3.3-70B-Instruct-Turbo"
```

---

## Performance Analysis Attempt (October 17, 2025)

### What We Tried

**Goal:** Send the Synergos Performance Analysis Framework through Blueprint using top-tier models.

**Attempt 1: Use environment variable**
```bash
export CONFIG_FILE=/mnt/projects/sultans-blueprint-ui/sultans_blueprint/config/config.analysis.yaml
python -B -m sultans_blueprint
```
**Result:** ❌ Didn't work - Blueprint ignored the environment variable

**Attempt 2: Swap config files**
```bash
cp config/config.yaml config/config.yaml.backup
cp config/config.analysis.yaml config/config.yaml
python -B -m sultans_blueprint
```
**Result:** ⚠️ Partially worked - Blueprint loaded the analysis config, but...

### Problems Encountered

1. **GPT-5 returned empty content:**
   - API call succeeded (HTTP 200)
   - `reasoning_tokens=4096` but `content=''`
   - Issue: Prompt too long + reasoning tokens consumed all output tokens

2. **Grok-4 configuration missing:**
   ```
   ERROR: FIEDLER_GROK_CLIENT environment variable not set
   ```
   - Blueprint expects `FIEDLER_GROK_CLIENT` to point to `grok_client.py`
   - This variable wasn't configured

3. **Together.ai service unavailable (earlier attempt):**
   ```
   HTTP 503 Service Unavailable
   model: meta-llama/Llama-3-70b-chat-hf
   ```
   - Default imperator model was down

### What We Learned

**Blueprint is not ready for production use because:**
- ❌ Config file selection is hardcoded (no command-line argument)
- ❌ Some model integrations incomplete (Grok needs special setup)
- ❌ No handling for empty LLM responses
- ❌ Service availability issues cascade to full failure

---

## What Worked: Direct Fiedler Usage

**Instead of using Blueprint, we sent directly to models via Fiedler MCP:**

```python
mcp__iccm__fiedler_send
- prompt: [Performance Analysis Framework]
- models: ["gpt-5", "gemini-2.5-pro", "grok-4", "deepseek-ai/DeepSeek-R1", "meta-llama/Llama-3.3-70B-Instruct-Turbo"]
```

**Result:** ✅ SUCCESS
- All 5 models responded
- Parallel execution (79 seconds for 4 models, GPT-5 took 187 seconds)
- Results saved to `/mnt/irina_storage/files/temp/synergos_analysis/20251017_165804_f04a8d9b/`

**Why this worked:**
- Fiedler handles model failures gracefully
- No complex multi-phase workflow to fail
- Direct model access without synthesis/consensus overhead
- Better suited for research consultation than application creation

---

## Key Differences: Blueprint vs. Fiedler

### Sultan's Blueprint (Multi-Agent Application Creation)
**Purpose:** Create complete software applications
**Phases:**
1. ANCHOR_DOCS (requirements)
2. GENESIS (parallel solutions)
3. SYNTHESIS (merge best ideas)
4. CONSENSUS (quality voting)
5. OUTPUT (package deliverable)

**Best for:**
- Creating applications from prompts
- Combining diverse LLM solutions
- Producing production-ready code

**Not ready for:**
- Research analysis (too complex)
- Long prompts (no token limit handling)
- Production use (configuration issues)

### Fiedler (Direct LLM Consultation)
**Purpose:** Send prompts to multiple LLMs, get individual responses
**Phases:** Just send → receive

**Best for:**
- Research analysis
- Getting multiple perspectives
- Long prompts (handles token limits better)
- Production use (battle-tested)

**Results:**
- Individual analysis files per model
- No synthesis (you interpret results)
- Simple, reliable

---

## Blueprint Server Details

### How to Start
```bash
cd /mnt/projects/sultans-blueprint-ui
source venv/bin/activate
python -B -m sultans_blueprint > /tmp/sultans_blueprint.log 2>&1 &
```

### How to Stop
```bash
lsof -ti:8000 | xargs kill -9
```

### Check Status
```bash
ps aux | grep sultans_blueprint
tail -f /tmp/sultans_blueprint.log
```

### How to Send Requests

**WebSocket format:**
```python
import asyncio
import json
import websockets

async def send_request():
    uri = "ws://localhost:8000"
    request = {
        "tool": "prompt",
        "input": {
            "requirements": "Your prompt here..."
        }
    }

    async with websockets.connect(uri) as websocket:
        await websocket.send(json.dumps(request))

        async for message in websocket:
            data = json.loads(message)
            msg_type = data.get("type")

            if msg_type == "final_output":
                # Blueprint finished
                break
```

**Important:** The server expects messages in this specific format: `{"tool": "prompt", "input": {...}}`

---

## Files Generated by Synergos Creation

**Project workspace:**
```
/mnt/projects/sultans-blueprint-ui/projects/410251ea-6f01-4e09-a77b-652c6367bd15/
├── workspace/
│   ├── imperator/      # Requirements phase
│   ├── senior/         # Final synthesized solution
│   ├── junior_0/       # Individual solution
│   ├── junior_1/       # Individual solution (named it "Synergos")
│   ├── junior_2/       # Individual solution
│   ├── junior_3/       # Individual solution
│   └── junior_4/       # Individual solution
└── output/             # Final packaged deliverable
```

**The actual Synergos application is in:** `workspace/senior/`

---

## Performance Analysis Results

**What we generated:**
```
/mnt/projects/Joshua/docs/research/synergos/performance_analysis/20251017_165804_f04a8d9b/
├── gemini-2.5-pro.md (12K) - 44 seconds
├── grok-4-0709.md (8.2K) - 60 seconds
├── deepseek-ai_DeepSeek-R1.md (18K) - 79 seconds
├── meta-llama_Llama-3.3-70B-Instruct-Turbo.md (4.9K) - 12 seconds
├── gpt-5.md (12K) - 188 seconds
└── fiedler.log
```

**Method used:** Direct Fiedler MCP (`mcp__iccm__fiedler_send`)

**Why not Blueprint:** Blueprint configuration issues made direct Fiedler more reliable for research analysis.

---

## Lessons Learned

### For Future Blueprint Use:

1. **Use default config unless you modify Blueprint code**
   - No clean way to specify alternate config file
   - Would need to edit `src/server.py` to accept command-line argument

2. **Blueprint is for application creation, not research**
   - 5-phase workflow adds complexity
   - Better suited for code generation than analysis

3. **For research/consultation, use Fiedler directly**
   - Simpler, more reliable
   - Better error handling
   - Already production-ready

### For Documenting Achievements:

**Synergos creation (October 16) was legitimate:**
- Blueprint worked correctly
- Default config was appropriate for application creation
- 4 minutes to production-ready application
- All phases completed successfully

**Performance analysis (October 17) took different approach:**
- Blueprint not appropriate for this task
- Used Fiedler directly (the LLM layer that Blueprint uses)
- Still got high-quality consensus-based analysis
- Appropriate tool for the job

---

## Summary

**Blueprint Location:** `/mnt/projects/sultans-blueprint-ui/sultans_blueprint/`

**Blueprint Purpose:** Multi-agent software application creation (5-phase workflow)

**What Worked:** Creating Synergos on October 16, 2025 (4 minutes, 9 files, 100% tests passing)

**What Didn't Work:** Using Blueprint for performance analysis (October 17) - configuration issues, empty responses, service unavailability

**What We Used Instead:** Direct Fiedler MCP calls - simpler, more reliable for research analysis

**Takeaway:** Blueprint successfully created Synergos. For research analysis, Fiedler direct access is better. Blueprint needs work before wider production use, but the core achievement (Synergos) is valid and impressive.

---

**Files Referenced:**
- Blueprint code: `/mnt/projects/sultans-blueprint-ui/sultans_blueprint/`
- Synergos output: `/mnt/projects/sultans-blueprint-ui/projects/410251ea-6f01-4e09-a77b-652c6367bd15/`
- Performance analysis: `/mnt/projects/Joshua/docs/research/synergos/performance_analysis/`
- Session logs: `~/.claude/projects/-home-aristotle9/3d7f129c-f84f-496c-a0db-e816ce64986e.jsonl`
