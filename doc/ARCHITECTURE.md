# Technical Architecture: Platform Agent

## 📋 项目更新状态 (2024年最新)

**🎯 项目重命名**: 从 "Fast Agent" 重命名为 "Platform Agent"，更好地反映平台工程和DevOps基础设施管理的定位。

**📁 文档状态**: 
- ✅ 已删除过时的伪代码文档 (MVP_PSEUDOCODE.md)
- ✅ 技术架构已更新为多Agent协作模式
- ✅ 所有文档统一更新为Platform Agent命名

---

## 1. Overview
This document outlines the technical architecture for the Platform Agent, an intelligent, multi-agent system for DevOps tasks. It translates the requirements in the [PRD](./PRD.md) into a concrete implementation plan.

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

### 3.4. Tool Subsystem & Inspector

- **`src/tools.py`** (Local Mock):
  - **Responsibility**: Provides local, mock tools for development (kept for reference/testing).
  - **Status**: ✅ Completed
- **Remote MCP Tools**:
  - **Responsibility**: Connect to external MCP servers to provide live cluster and infrastructure capabilities.
  - **Status**: ✅ Completed
- **Tool Inspector & Cache**:
  - **Responsibility**: Automatically discover all remote MCP tools on startup and cache them to `tools_cache.json` (24 h TTL). Provides a CLI (`src/tool_inspector.py`) for manual `--refresh / --check / --list` operations.
  - **Implementation**: Implemented as the `tool_inspector` agent inside `src/ops_crew/crew.py`.
  - **Status**: ✅ **Completed** (Task 7)

### 3.5. Memory Subsystem (Completed)
- **Responsibility**: Provides the crew with intelligent short-term, long-term, and entity-based memory, enabling contextual conversations and cross-session learning with superior Chinese language support.
- **Implementation**: 
  - Activated via the `memory=True` parameter in the `Crew` object.
  - **Qwen Embedding Integration**: Uses Qwen text-embedding-v4 model via OpenAI-compatible API for superior Chinese language understanding and cost optimization.
  - **Storage Backend**: ChromaDB for vector storage, SQLite for long-term memory persistence.
  - **Configuration**: Embedder configured with dictionary format for proper CrewAI integration.
  - Storage path controlled via `CREWAI_STORAGE_DIR=./crew_memory/` environment variable.
- **Key Features**:
  - **Cross-session Memory**: Agents remember previous conversations and user preferences
  - **Chinese Optimization**: Enhanced understanding of Chinese K8s terminology and concepts
  - **Cost Efficiency**: Reduced embedding API costs compared to OpenAI
  - **Intelligent Context**: Automatic entity recognition and relationship mapping
- **Status**: ✅ **Completed and Verified** (Task 6)

## 4. Data Flow (Scenario: "get k8s clusters and fetch crewai.com")
1.  **User**: Runs `./run.sh` and types the command.
2.  **`main.py`**: Captures the input string and passes it to the `OpsCrew`.
3.  **`ops_crew/crew.py`**:
    - Instantiates the `OpsCrew`.
    - Initializes the `k8s_expert` agent and, **via the cached tool list**, assigns the `LIST_CLUSTERS` tool to fetch cluster information.
    - Initializes the `web_researcher` agent, connecting to the MCP server to get the `fetch` tool.
    - Creates two tasks (`k8s_analysis_task` and `web_fetch_task`) and assigns them to their respective agents.
4.  **CrewAI Framework (Sequential Process)**: 
    - **Task 1**: The `k8s_expert` analyzes the input. It finds K8s-related keywords and executes the `get_cluster_info` tool. It then formulates a report.
    - **Task 2**: The `web_researcher` analyzes the same input. It finds the URL, executes the `fetch` tool via the MCP connection, and summarizes the content.
5.  **LLM and Memory Integration**: 
    - **Primary LLM (via OpenRouter)**: Drives reasoning for both agents, deciding when to use tools and formulating responses.
    - **Memory System (via Qwen Embedding)**: Provides intelligent context from past conversations, learned entities, and user preferences.
    - **Cross-session Learning**: Agents can recall previous cluster discussions, user patterns, and accumulated knowledge.
    - **Intelligent Context**: Memory system enhances responses with relevant historical information and Chinese K8s terminology understanding.
6.  **`main.py`**: Displays the final, comprehensive result to the user, enriched with contextual memory insights.

## 5. Current Project Structure (Implemented)
```
platform-agent/
├── .venv/                          # Python virtual environment
├── crew_memory/                    # ✅ Persistent storage for CrewAI memory (auto-created)
├── doc/                            # Documentation
│   ├── ARCHITECTURE.md             # This file
│   ├── MVP_TASKS.md                # Task implementation status
│   ├── PRD.md                      # Product requirements
│   └── TOOLS_SURVEY.md             # Technical research
├── src/                            # Source code
│   ├── __init__.py
│   ├── main.py                     # ✅ CLI entry point
│   ├── ops_crew/                   # ✅ CrewAI project package
│   │   ├── __init__.py
│   │   ├── crew.py                 # ✅ Multi-agent orchestrator with Memory
│   │   └── config/                 # ✅ YAML configurations
│   │       ├── agents.yaml         # ✅ Agent definitions (2 agents)
│   │       └── tasks.yaml          # ✅ Task definitions (2 tasks)
│   └── tools.py                    # ✅ Local K8s tools
├── test_memory_basic.py            # ✅ Memory functionality basic tests
├── test_crew_memory_simple.py     # ✅ CrewAI Memory integration tests
├── test_qwen_api.py                # ✅ Qwen API connectivity tests
├── benchmark_memory.py             # ✅ Memory performance benchmarks
├── memory_acceptance_checklist.md # ✅ Memory feature acceptance guide
├── tools_cache.json               # ✅ MCP tools cache (24h TTL)
├── .env                            # Environment variables (includes Qwen config)
├── pyproject.toml                  # ✅ UV project configuration
├── requirements.txt                # ✅ Dependencies backup
├── run.sh                          # ✅ Smart startup script
├── uv.lock                         # UV dependency lock
├── CLAUDE.md                       # ✅ Development guidance
└── README.md                       # Project documentation
```

## 6. Technical Implementation Details

### 6.1. CrewAI Integration
- **Framework**: CrewAI with official `@CrewBase` pattern.
- **Architecture**: Multi-agent sequential process with intelligent memory integration.
- **Tools**: Supports both local Python functions and remote MCP tools via `MCPServerAdapter`.
- **Memory System**: 
  - **Embedder Configuration**: Dictionary-based configuration for Qwen embedding integration
  - **API Compatibility**: OpenAI-compatible interface using Qwen's Dashscope endpoint
  - **Memory Types**: Short-term, long-term, and entity memory all functional and verified

### 6.2. Qwen Embedding Integration
- **Model**: text-embedding-v4 with 1024-dimensional vectors
- **API Endpoint**: `https://dashscope.aliyuncs.com/compatible-mode/v1/embeddings`
- **Implementation Strategy**: Method 1 - OpenAI API replacement via environment variables
- **Configuration Format**:
  ```python
  embedder = {
      "provider": "openai",
      "config": {
          "api_key": "qwen_api_key",
          "api_base": "dashscope_endpoint",
          "model": "text-embedding-v4"
      }
  }
  ```
- **Benefits**: 
  - Superior Chinese language understanding (MTEB leaderboard #1)
  - Cost optimization compared to OpenAI embeddings
  - 32K context length support for long K8s configurations
  - Enhanced semantic understanding for DevOps terminology

### 6.3. Environment Management & Data
- **Configuration**: Extended `.env` file with Qwen embedding parameters
- **Storage**: Automatic `crew_memory/` directory creation for persistent memory
- **Dependencies**: Updated to include `crewai`, `langchain-openai`, and memory-related packages
- **Cross-platform**: Verified compatibility on macOS and Linux systems

## 7. MVP Achievement Status
- ✅ **All Original MVP Tasks Completed**: Multi-agent system, tool integration, and CLI interface
- ✅ **Memory System Implementation**: CrewAI memory with Qwen embedding successfully integrated
- ✅ **Advanced Features Added**: 
  - Cross-session learning and contextual conversations
  - Chinese language optimization for K8s terminology
  - Cost-efficient embedding solution
  - Comprehensive testing and validation framework
- ✅ **Production Ready**: Full verification through automated tests and acceptance checklist

## 8. Future Enhancements

### 8.1. Advanced Memory Features
- **Memory Analytics**: Implement dashboard for memory usage and learning metrics
- **Memory Cleanup**: Automated cleanup and archival of old memory data
- **Custom Memory Strategies**: User-defined memory retention and retrieval policies

### 8.2. Enhanced Agent Capabilities  
- **Guided Conversation**: Advanced multi-turn conversation logic leveraging memory for contextual understanding
- **Hierarchical Process**: Explore `Process.hierarchical` for complex multi-step workflows
- **Dynamic Tool Selection**: Smart tool selection based on task context and historical success

### 8.3. Performance and Scalability
- **Memory Optimization**: Fine-tune Qwen embedding parameters for specific use cases
- **Distributed Memory**: Support for distributed memory systems in enterprise environments
- **Performance Monitoring**: Real-time monitoring of memory system performance and costs

### 8.4. Enterprise Features
- **Multi-tenant Memory**: Isolated memory spaces for different teams or projects
- **Audit and Compliance**: Memory access logging and data governance features
- **Integration Ecosystem**: Extended MCP tool ecosystem for enterprise DevOps workflows 