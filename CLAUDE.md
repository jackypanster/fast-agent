# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Platform Agent is an intelligent multi-agent system for DevOps and infrastructure management, powered by CrewAI and modern LLMs. The project enables platform engineering teams to interact with complex infrastructure using natural language.

## Key Architecture

- **Multi-Agent System**: Built with CrewAI framework using `@CrewBase` pattern
- **Agent Types**: 
  - `k8s_expert`: Handles Kubernetes operations with filtered tools
  - `tool_inspector`: Discovers and caches MCP tools automatically
- **Memory System**: Intelligent memory with Qwen embedding for context-aware conversations
  - Short-term memory for conversation context
  - Long-term memory for cross-session persistence
  - Entity memory for K8s resources and concepts
- **MCP Integration**: Uses `MCPServerAdapter` to connect to external MCP servers for live infrastructure capabilities
- **Tool Caching**: Automatic 24-hour TTL cache system in `tools_cache.json`

## Development Commands

### Environment Setup
```bash
# Use the smart startup script (handles Python, uv, dependencies)
./run.sh

# Force reinstall dependencies
./run.sh --force-reinstall

# Refresh tool cache
./run.sh --refresh-tools

# Environment check only
./run.sh --check-only

# System verification
./run.sh --verify
```

### Running Python Scripts
```bash
# Use uv for Python execution
uv run main.py
uv run src/main.py
uv run verify_setup.py
```

### Manual Tool Management
```bash
# Tool inspection CLI
python src/tool_inspector.py --refresh    # Refresh cache
python src/tool_inspector.py --check      # Check cache status
python src/tool_inspector.py --list       # List cached tools
```

## Configuration Requirements

### Environment Variables (.env)
- `OPENROUTER_API_KEY`: Required for LLM access
- `CREWAI_STORAGE_DIR`: CrewAI memory storage (defaults to `./crew_memory`)
- `OPENAI_API_KEY`: Qwen embedding API key for memory functionality
- `QWEN_API_BASE`: Qwen API endpoint (defaults to Dashscope compatible mode)
- `QWEN_EMBEDDING_MODEL`: Qwen embedding model (defaults to `text-embedding-v4`)
- `K8S_MCP_URL`: MCP server URL for Kubernetes tools
- `MODEL`: LLM model identifier
- `BASE_URL`: LLM API base URL

### Dependencies
- Python 3.11+ required
- Main dependencies: `crewai`, `crewai-tools[mcp]`, `chromadb`
- Full dependencies in `requirements.txt`

## Code Structure

- `src/main.py`: CLI entry point with conversation loop
- `src/ops_crew/crew.py`: Multi-agent CrewAI orchestrator with tool caching
- `src/ops_crew/config/`: YAML configurations for agents and tasks
- `src/tool_inspector.py`: Standalone tool cache management
- `run.sh`: Smart startup script with cross-platform compatibility
- `verify_setup.py`: System validation script

## Important Implementation Details

- **Memory System**: Uses Qwen text-embedding-v4 for superior Chinese language support
- **Cross-session Learning**: Agents remember previous conversations and user preferences
- **Tool Cache**: Automatically refreshes every 24 hours or on manual refresh
- **K8s Expert**: Uses filtered tools (prefixes: `list_`, `get_`, `describe_`)
- **Sequential Process**: Agent collaboration with memory-enhanced context
- **Environment Validation**: Checks before crew execution
- **Cross-platform Support**: macOS, Ubuntu with intelligent memory storage