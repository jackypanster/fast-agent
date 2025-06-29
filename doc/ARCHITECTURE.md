# Technical Architecture: Ops Crew

## 1. Overview
This document outlines the technical architecture for the Ops Crew, an intelligent, multi-agent system for DevOps tasks. It translates the requirements in the [PRD](./PRD.md) into a concrete implementation plan.

**📋 Current Status**: MVP implementation completed and refactored into a multi-agent system following CrewAI official best practices.

## 2. Guiding Principles
- **Simplicity**: Prioritize clear, straightforward code over complex abstractions.
- **MVP First**: Focus exclusively on the functionality required to satisfy the MVP scope.
- **CLI-centric**: All initial development will be for a command-line interface.
- **Official Standards**: Follow CrewAI official documentation patterns and best practices for creating collaborative agent crews.
- **Separation of Concerns**: Each agent has a distinct role and a dedicated set of tools.

## 3. System Components (Multi-Agent Implemented)
Our system consists of a crew of collaborating agents, orchestrated by CrewAI.

### 3.1. CLI Application (`src/main.py`)
- **Responsibility**: The main entry point. Handles the user-facing loop: reading input, printing output, and managing the conversation flow.
- **Implementation**: A simple `while` loop that passes user input to the Crew Orchestrator.
- **Status**: ✅ **Completed** (Refined with better UI prompts)

### 3.2. Crew Orchestrator (`src/ops_crew/crew.py`)
- **Responsibility**: The brain of the application, defining the crew of agents, their tools, and their collaborative tasks.
- **Implementation**: 
  - Uses `@CrewBase` to define the `OpsCrew`.
  - Defines two distinct agents: `k8s_expert` and `web_researcher`.
  - Assigns a local tool (`get_cluster_info`) to the K8s expert.
  - Assigns an MCP tool (`fetch`) to the web researcher via `MCPServerAdapter`.
  - Defines sequential tasks for the agents to perform.
- **Status**: ✅ **Completed** (Refactored to a multi-agent system)

### 3.3. Configuration Files (`src/ops_crew/config/`)
- **Responsibility**: YAML-based configuration for multiple agents and their tasks.
- **Implementation**: 
  - `agents.yaml`: Defines configurations for `k8s_expert` and `web_researcher`.
  - `tasks.yaml`: Defines task descriptions for K8s analysis and web fetching.
- **Status**: ✅ **Completed** (Expanded for multiple agents)

### 3.4. Tool Subsystem
- **`src/tools.py`**:
  - **Responsibility**: Provides local, mock tools for development.
  - **Implementation**: Contains the `get_cluster_info()` function with real K8s cluster data.
  - **Status**: ✅ **Completed**
- **Remote MCP Tools**:
  - **Responsibility**: Connect to external MCP servers to provide additional capabilities.
  - **Implementation**: The `crew.py` file uses `MCPServerAdapter` to connect to a remote MCP server for web fetching.
  - **Status**: ✅ **Completed**

### 3.5. Memory Subsystem (Planned)
- **Responsibility**: To provide the crew with short-term, long-term, and entity-based memory, enabling contextual conversations and cross-session learning.
- **Implementation**: 
  - Activated via the `memory=True` parameter in the `Crew` object.
  - Utilizes CrewAI's built-in memory system (ChromaDB for short-term/entity, SQLite for long-term).
  - Storage path is controlled via the `CREWAI_STORAGE_DIR` environment variable, set to `./crew_memory/` for persistence and explicit management.
- **Status**: ⏳ **Planned**

## 4. Data Flow (Scenario: "get k8s clusters and fetch crewai.com")
1.  **User**: Runs `./run.sh` and types the command.
2.  **`main.py`**: Captures the input string and passes it to the `OpsCrew`.
3.  **`ops_crew/crew.py`**:
    - Instantiates the `OpsCrew`.
    - Initializes the `k8s_expert` agent with the `get_cluster_info` tool.
    - Initializes the `web_researcher` agent, connecting to the MCP server to get the `fetch` tool.
    - Creates two tasks (`k8s_analysis_task` and `web_fetch_task`) and assigns them to their respective agents.
4.  **CrewAI Framework (Sequential Process)**: 
    - **Task 1**: The `k8s_expert` analyzes the input. It finds K8s-related keywords and executes the `get_cluster_info` tool. It then formulates a report.
    - **Task 2**: The `web_researcher` analyzes the same input. It finds the URL, executes the `fetch` tool via the MCP connection, and summarizes the content.
5.  **LLM (via OpenRouter)**: The LLM drives the reasoning for both agents, deciding when to use tools and how to formulate the final, combined response based on the outputs of both tasks. **With memory enabled, the LLM can also access past conversations and learned entities to provide richer, more contextual answers.**
6.  **`main.py`**: Displays the final, comprehensive result to the user.

## 5. Current Project Structure (Implemented)
```
fast-agent/
├── .venv/                          # Python virtual environment
├── crew_memory/                    # (Planned) Persistent storage for CrewAI memory
├── doc/                            # Documentation
│   ├── ARCHITECTURE.md             # This file
│   └── ...                         # Other docs
├── src/                            # Source code
│   ├── __init__.py
│   ├── main.py                     # ✅ CLI entry point
│   ├── ops_crew/                   # ✅ CrewAI project package
│   │   ├── __init__.py
│   │   ├── crew.py                 # ✅ Multi-agent @CrewBase orchestrator
│   │   └── config/                 # ✅ YAML configurations
│   │       ├── agents.yaml         # ✅ Agent definitions (2 agents)
│   │       └── tasks.yaml          # ✅ Task definitions (2 tasks)
│   └── tools.py                    # ✅ Local K8s tools
├── .env                            # Environment variables
├── .gitignore                      # Git ignore patterns
├── requirements.txt                # ✅ Dependencies, including 'crewai-tools[mcp]'
├── run.sh                          # ✅ Startup script
├── uv.lock                         # UV lock file
└── README.md                       # Project documentation
```

## 6. Technical Implementation Details

### 6.1. CrewAI Integration
- **Framework**: CrewAI with official `@CrewBase` pattern.
- **Architecture**: Multi-agent sequential process.
- **Tools**: Supports both local Python functions and remote MCP tools via `MCPServerAdapter`.

### 6.2. Environment Management & Data
- Unchanged.

## 7. MVP Achievement Status
- Status unchanged, all tasks completed. The implementation was refactored and expanded upon.

## 8. Future Enhancements
- **Guided Conversation**: Implement the advanced multi-turn conversation logic from the PRD for the `k8s_expert`, **leveraging the new memory capabilities for true contextual understanding.**
- **Hierarchical Process**: Explore changing the `Process.sequential` to `Process.hierarchical` for more complex workflows.
- **Dynamic Tool Selection**: Allow agents to choose from a larger set of tools based on the task.
- **Leverage Long-Term Memory**: Design specific tests to validate that the crew learns and improves over multiple sessions. 