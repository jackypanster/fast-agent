# Technical Architecture: K8s Copilot

## 1. Overview
This document outlines the technical architecture for the K8s Copilot, translating the requirements in the [PRD](./PRD.md) into a concrete implementation plan for the MVP.

**📋 Current Status**: MVP implementation completed and refactored to follow CrewAI official best practices.

## 2. Guiding Principles
- **Simplicity**: Prioritize clear, straightforward code over complex abstractions.
- **MVP First**: Focus exclusively on the functionality required to satisfy the MVP scope.
- **CLI-centric**: All initial development will be for a command-line interface.
- **Official Standards**: Follow CrewAI official documentation patterns and best practices.

## 3. System Components (MVP - Implemented)
Our MVP consists of the following key components, following CrewAI's official project structure.

### 3.1. CLI Application (`src/main.py`)
- **Responsibility**: The main entry point of the application. It handles the user-facing loop: reading input, printing output, and managing the conversation flow.
- **Implementation**: A simple `while` loop that takes user input via `input()` and passes it to the Crew Orchestrator.
- **Status**: ✅ **Completed**

### 3.2. Crew Orchestrator (`src/k8s_copilot/crew.py`)
- **Responsibility**: The brain of the application using CrewAI's @CrewBase decorator pattern.
- **Implementation**: 
  - Uses `@CrewBase` class decorator with YAML configuration files
  - Implements `@agent`, `@task`, and `@crew` method decorators
  - Manages interaction with OpenRouter LLM service
  - Orchestrates tool execution through CrewAI framework
- **Status**: ✅ **Completed** (Refactored to official standards)

### 3.3. Configuration Files (`src/k8s_copilot/config/`)
- **Responsibility**: YAML-based configuration for agents and tasks, following CrewAI best practices.
- **Implementation**: 
  - `agents.yaml`: Defines K8s expert agent configuration
  - `tasks.yaml`: Defines K8s query task configuration
- **Status**: ✅ **Completed** (New - follows official patterns)

### 3.4. Tool Subsystem (`src/tools.py`)
- **Responsibility**: Provides K8s cluster information tools.
- **Implementation**: 
  - Real K8s cluster data (9 clusters with detailed metadata)
  - `get_cluster_info()` function with comprehensive cluster information
  - CrewAI-compatible tool decorators
- **Status**: ✅ **Completed** (Enhanced with real data)

## 4. Data Flow (Implemented Scenario: "get all k8s cluster")
1.  **User**: Runs `./run.sh` or `uv run python -m src.main` and types "get all k8s cluster".
2.  **`main.py`**: Captures the input and passes it to the K8s Copilot Crew.
3.  **`k8s_copilot/crew.py`**:
    - Instantiates K8sCopilotCrew class with @CrewBase decorator
    - Loads agent configuration from `config/agents.yaml`
    - Loads task configuration from `config/tasks.yaml`
    - Initializes OpenRouter LLM with environment variables
    - Creates Agent with K8s tools and LLM configuration
4.  **CrewAI Framework**: 
    - Agent analyzes user request and determines tool needed
    - Calls `get_cluster_info` tool automatically
5.  **`tools.py`**: Returns comprehensive real cluster data (9 clusters).
6.  **LLM (via OpenRouter)**: 
    - Processes tool output
    - Generates professional DevOps analysis with:
      - Formatted cluster overview
      - Resource utilization analysis
      - Version distribution insights
      - Professional recommendations
7.  **`main.py`**: Displays the formatted result to user.

## 5. Current Project Structure (Implemented)
```
k8s-copilot/
├── .venv/                          # Python virtual environment
├── doc/                            # Documentation
│   ├── ARCHITECTURE.md             # This file
│   ├── PRD.md                      # Product requirements
│   ├── MVP_PSEUDOCODE.md           # Implementation pseudocode
│   ├── MVP_TASKS.md                # Task breakdown
│   └── TOOLS_SURVEY.md             # Tools research
├── src/                            # Source code
│   ├── __init__.py
│   ├── main.py                     # ✅ CLI entry point
│   ├── k8s_copilot/                # ✅ CrewAI project package
│   │   ├── __init__.py
│   │   ├── crew.py                 # ✅ @CrewBase orchestrator
│   │   └── config/                 # ✅ YAML configurations
│   │       ├── agents.yaml         # ✅ Agent definitions
│   │       └── tasks.yaml          # ✅ Task definitions
│   └── tools.py                    # ✅ K8s tools (real data)
├── .env                            # Environment variables
├── .gitignore                      # Git ignore patterns
├── requirements.txt                # ✅ Dependencies (223 packages)
├── run.sh                          # ✅ Startup script
├── uv.lock                         # UV lock file
└── README.md                       # Project documentation
```

## 6. Technical Implementation Details

### 6.1. CrewAI Integration
- **Framework**: CrewAI with official @CrewBase pattern
- **LLM Provider**: OpenRouter with `google/gemini-2.5-flash-preview-05-20`
- **Configuration**: YAML-based agent and task definitions
- **Tools**: Native CrewAI tool integration

### 6.2. Environment Management
- **Package Manager**: `uv` for fast dependency management
- **Environment**: Python virtual environment with 223 dependencies
- **Configuration**: Environment variables via `.env` file

### 6.3. Data Source
- **Real K8s Data**: 9 production-like clusters with:
  - Comprehensive metadata (creation timestamps, UIDs)
  - Resource utilization metrics (CPU, memory, pods)
  - Component health status
  - Version information
  - Node counts and capacity details

## 7. MVP Achievement Status

### ✅ All 5 MVP Tasks Completed:
1. **✅ Project Structure**: Standard CrewAI project layout
2. **✅ Mock Tools**: Enhanced with real K8s cluster data
3. **✅ Crew Orchestration**: @CrewBase pattern with YAML configs
4. **✅ CLI Interface**: Professional user experience
5. **✅ Integration Testing**: Full end-to-end functionality

### ✅ Additional Improvements:
- **Refactored to Official Standards**: Following CrewAI documentation patterns
- **YAML Configuration**: Separated concerns with config files
- **Enhanced Data**: Real cluster information instead of mock data
- **Professional Output**: DevOps-grade analysis and recommendations
- **Automation**: Startup script for easy deployment

## 8. Future Enhancements
- **MCP Integration**: Connect to real `k8s mcp server` for live data
- **Multi-cluster Support**: Extend to manage multiple K8s clusters
- **Advanced Caching**: Implement intelligent caching strategies
- **Web Interface**: Develop web-based UI for broader accessibility 