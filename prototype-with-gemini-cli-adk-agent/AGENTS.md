# AI Coding Assistant Context

This document provides context for AI coding assistants (Claude Code, Gemini CLI, GitHub Copilot, Cursor, etc.) to understand the ADK Python project and assist with development.

## Project Overview

The Agent Development Kit (ADK) is an open-source, code-first Python toolkit for building, evaluating, and deploying sophisticated AI agents with flexibility and control. While optimized for Gemini and the Google ecosystem, ADK is model-agnostic, deployment-agnostic, and is built for compatibility with other frameworks. ADK was designed to make agent development feel more like software development, to make it easier for developers to create, deploy, and orchestrate agentic architectures that range from simple tasks to complex workflows.

### Key Components

- **Agent** - Blueprint defining identity, instructions, and tools (`LlmAgent`, `LoopAgent`, `ParallelAgent`, `SequentialAgent`, etc.)
- **Runner** - Execution engine that orchestrates the "Reason-Act" loop, manages LLM calls, executes tools, and handles multi-agent coordination
- **Tool** - Functions/capabilities agents can call (Python functions, OpenAPI specs, MCP tools, Google API tools)
- **Session** - Conversation state management (in-memory, Vertex AI, Spanner-backed)
- **Memory** - Long-term recall across sessions

## Project Architecture

Please refer to [ADK Project Overview and Architecture](https://github.com/google/adk-python/blob/main/contributing/adk_project_overview_and_architecture.md) for details.


### Test Structure

```
tests/
├── unittests/       # 2600+ unit tests across 236+ files
│   ├── agents/
│   ├── tools/
│   ├── models/
│   ├── evaluation/
│   ├── a2a/
│   └── ...
└── integration/     # Integration tests
```



### Agent Structure Convention (Required)

**All agent directories must follow this structure:**
```
my_agent/
├── __init__.py      # MUST contain: from . import agent
└── agent.py         # MUST define: root_agent = Agent(...) OR app = App(...)
```

**Choose one pattern based on your needs:**

**Option 1 - Simple Agent (for basic agents without plugins):**
```python
from google.adk.agents import Agent
from google.adk.tools import google_search

root_agent = Agent(
    name="search_assistant",
    model="gemini-2.5-flash",
    instruction="You are a helpful assistant.",
    description="An assistant that can search the web.",
    tools=[google_search]
)
```

**Option 2 - App Pattern (when you need plugins, event compaction, custom configuration):**
```python
from google.adk import Agent
from google.adk.apps import App
from google.adk.plugins import ContextFilterPlugin

root_agent = Agent(
    name="my_agent",
    model="gemini-2.5-flash",
    instruction="You are a helpful assistant.",
    tools=[...],
)

app = App(
    name="my_app",
    root_agent=root_agent,
    plugins=[
        ContextFilterPlugin(num_invocations_to_keep=3),
    ],
)
```

**Rationale:** This structure allows the ADK CLI (`adk web`, `adk run`, etc.) to automatically discover and load agents without additional configuration.

## Development Setup

### Requirements

**Minimum requirements:**
- Python 3.9+ (**Python 3.11+ strongly recommended** for best performance)
- `uv` package manager (**required** - faster than pip/venv)

**Install uv if not already installed:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Setup Instructions

**Standard setup for development:**
```bash
# Create virtual environment with Python 3.11
uv venv --python "python3.11" ".venv"
source .venv/bin/activate

# Install all dependencies for development
uv sync --all-extras
```

**Minimal setup for testing only (matches CI):**
```bash
uv sync --extra test --extra eval --extra a2a
```

**Virtual Environment Usage (Required):**
- **Always use** `.venv/bin/python` or `.venv/bin/pytest` directly
- **Or activate** with `source .venv/bin/activate` before running commands
- **Never use** `python -m venv` - always create with `uv venv` if missing

**Rationale:** `uv` is significantly faster and ensures consistent dependency resolution across the team.

### Building

```bash
# Build wheel
uv build

# Install local build for testing
pip install dist/google_adk-<version>-py3-none-any.whl
```

### Running Agents Locally

**For interactive development and debugging:**
```bash
# Launch web UI (recommended for development)
adk web .
```

## ADK: Style Guides

### Python Style Guide

The project follows the Google Python Style Guide. Key conventions are enforced using `pylint` with the provided `pylintrc` configuration file. Here are some of the key style points:

*   **Indentation**: 2 spaces.
*   **Line Length**: Maximum 80 characters.
*   **Naming Conventions**:
    *   `function_and_variable_names`: `snake_case`
    *   `ClassNames`: `CamelCase`
    *   `CONSTANTS`: `UPPERCASE_SNAKE_CASE`
*   **Docstrings**: Required for all public modules, functions, classes, and methods.
*   **Imports**: Organized and sorted.
*   **Error Handling**: Specific exceptions should be caught, not general ones like `Exception`.

