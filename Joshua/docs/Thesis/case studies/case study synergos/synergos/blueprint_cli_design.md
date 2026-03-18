# Sultan's Blueprint CLI Design

## Vision
A command-line interface that makes it trivial to use Sultan's Blueprint to build software, including using Blueprint to build its own next version.

## Current State
- Blueprint runs as MCP WebSocket server
- Requires client connection to submit requests
- No direct CLI interface
- Configuration in YAML files

## Proposed CLI

### Basic Usage
```bash
# Simple request (interactive)
blueprint build "Create a REST API for task management"

# From request file
blueprint build -f request.yaml

# With custom config
blueprint build -f request.yaml -c custom_config.yaml

# Watch and monitor
blueprint build -f request.yaml --watch

# Use specific models
blueprint build -f request.yaml --imperator gpt-4o --senior gemini-2.5-pro
```

### Request File Format (YAML)
```yaml
# request.yaml
prompt: |
  Create a REST API for task management with the following features:
  - CRUD operations for tasks
  - SQLite backend
  - FastAPI framework
  - Complete with tests and documentation

files:
  - path/to/context/file1.md
  - path/to/context/file2.py

config:
  genesis_rounds: 1
  consensus_thresholds:
    technical: 0.8
    subjective: 0.7

output:
  directory: ./output/task-api
  format: zip  # or 'directory'
```

### Command Structure

```bash
blueprint [command] [options]

Commands:
  build       Build a new application
  config      Manage configuration
  models      List/test available models
  status      Check Blueprint status
  history     View past builds
  version     Show version info

Build Options:
  -f, --file FILE           Request file (YAML/JSON)
  -c, --config FILE        Custom config file
  -o, --output DIR         Output directory
  --imperator MODEL        Override Imperator model
  --senior MODEL           Override Senior model
  --juniors MODEL,MODEL    Override Junior models
  --watch                  Monitor progress
  --no-zip                 Output as directory not ZIP
  --verbose               Show detailed logs

Config Commands:
  blueprint config show              Show current config
  blueprint config set KEY VALUE     Set config value
  blueprint config models            List available models
  blueprint config test              Test all models

Models Commands:
  blueprint models list              List all available models
  blueprint models test [MODEL]      Test specific model(s)
  blueprint models refresh           Refresh model list

Status Commands:
  blueprint status                   Show server status
  blueprint status [PROJECT_ID]      Show specific project

History Commands:
  blueprint history                  List recent builds
  blueprint history [PROJECT_ID]     Show build details
```

## Implementation Plan

### Phase 1: Core CLI (MVP)
```python
# blueprint_cli.py
import click
import yaml
import asyncio
from pathlib import Path

@click.group()
def cli():
    """Sultan's Blueprint - Autonomous Multi-Agent Software Development"""
    pass

@cli.command()
@click.argument('prompt', required=False)
@click.option('-f', '--file', 'request_file', help='Request file (YAML/JSON)')
@click.option('-o', '--output', help='Output directory')
@click.option('--watch', is_flag=True, help='Monitor progress')
def build(prompt, request_file, output, watch):
    """Build a new application"""
    if not prompt and not request_file:
        click.echo("Error: Provide either a prompt or request file")
        return

    # Load request
    if request_file:
        config = load_request(request_file)
    else:
        config = {'prompt': prompt}

    # Execute build
    result = execute_build(config, output, watch)

    click.echo(f"✓ Build complete: {result['output_path']}")

@cli.command()
def status():
    """Check Blueprint status"""
    # Check if server is running
    # Show active projects
    pass

@cli.command()
@click.option('--format', type=click.Choice(['yaml', 'json']), default='yaml')
def config(format):
    """Show current configuration"""
    # Load and display config
    pass

if __name__ == '__main__':
    cli()
```

### Phase 2: WebSocket Client
```python
# websocket_client.py
import asyncio
import websockets
import json

class BlueprintClient:
    def __init__(self, url="ws://localhost:8000"):
        self.url = url
        self.ws = None

    async def connect(self):
        self.ws = await websockets.connect(self.url)

    async def build(self, prompt, files=None, watch=False):
        request = {
            "type": "build",
            "prompt": prompt,
            "files": files or []
        }

        await self.ws.send(json.dumps(request))

        if watch:
            async for message in self.ws:
                data = json.loads(message)
                yield data
        else:
            response = await self.ws.recv()
            return json.loads(response)

    async def close(self):
        await self.ws.close()
```

### Phase 3: Enhanced Features
- Progress indicators with rich/tqdm
- Interactive mode for selecting models
- Template library (common app types)
- Build history with search
- Diff viewer for iterations

## Self-Hosting Use Case

### Building Blueprint v2 with Blueprint v1

**Request file: `blueprint_v2_request.yaml`**
```yaml
prompt: |
  Create Sultan's Blueprint v2 with the following improvements:

  1. Enhanced CLI with rich terminal output
  2. Better error handling and recovery
  3. Streaming progress updates
  4. Model selection optimization
  5. Cost tracking and reporting
  6. Build caching for faster iterations

  Architecture:
  - Maintain 5-phase workflow
  - Keep Fiedler integration
  - Add CLI layer
  - Improve observability

  Quality requirements:
  - 100% test coverage
  - Type hints throughout
  - Comprehensive documentation
  - Example projects included

files:
  - /mnt/projects/sultans-blueprint-ui/README.md
  - /mnt/projects/sultans-blueprint-ui/sultans_blueprint/src/**/*.py
  - /mnt/projects/Joshua/docs/research/blueprint_and_the_calculator.md

config:
  genesis_rounds: 2  # More rounds for complex project
  consensus_thresholds:
    technical: 0.9   # Higher bar for quality
    subjective: 0.8

  models:
    imperator: openai/gpt-4o
    senior: google/gemini-2.5-pro
    juniors:
      - together/deepseek-ai/DeepSeek-R1
      - openai/gpt-4o
      - google/gemini-2.5-pro
      - xai/grok-4
      - together/meta-llama/Llama-3.3-70B-Instruct-Turbo

output:
  directory: /mnt/projects/sultans-blueprint-v2
  format: directory
  include_docs: true
  include_tests: true
```

**Execute:**
```bash
blueprint build -f blueprint_v2_request.yaml --watch
```

## Benefits

1. **Accessibility**: Simple command instead of MCP client
2. **Automation**: Script builds, CI/CD integration
3. **Iteration**: Easy to refine and rebuild
4. **Self-Improvement**: Blueprint builds Blueprint
5. **Standardization**: Request files = reproducible builds

## File Structure
```
sultans-blueprint-ui/
├── blueprint_cli/
│   ├── __init__.py
│   ├── cli.py              # Main CLI entry point
│   ├── client.py           # WebSocket client
│   ├── request.py          # Request file handling
│   ├── display.py          # Rich terminal UI
│   └── templates/          # Request templates
│       ├── web_app.yaml
│       ├── rest_api.yaml
│       ├── cli_tool.yaml
│       └── library.yaml
├── pyproject.toml          # Add CLI entry point
└── README_CLI.md           # CLI documentation
```

## Installation
```bash
# Install with CLI
pip install -e ".[cli]"

# Or
pip install sultans-blueprint[cli]

# Verify
blueprint --version
```

## Next Steps
1. Implement basic CLI (build command)
2. Add WebSocket client
3. Test with simple request
4. Add progress monitoring
5. Use Blueprint to build Blueprint v2

This will enable the bootstrapping loop - Blueprint building its own improvements!