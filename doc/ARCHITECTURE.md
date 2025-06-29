# Technical Architecture: K8s Copilot

## 1. Overview
This document outlines the technical architecture for the K8s Copilot, translating the requirements in the [PRD](./PRD.md) into a concrete implementation plan for the MVP.

## 2. Guiding Principles
- **Simplicity**: Prioritize clear, straightforward code over complex abstractions.
- **MVP First**: Focus exclusively on the functionality required to satisfy the MVP scope.
- **CLI-centric**: All initial development will be for a command-line interface.
- **Statelessness (as much as possible)**: Core agent logic should be stateless, with stateful information (like cache) handled by dedicated modules.

## 3. System Components (MVP)
Our MVP will consist of the following key components, designed to be simple and "flat" as per our development principles.

### 3.1. CLI Application (`src/main.py`)
- **Responsibility**: The main entry point of the application. It handles the user-facing loop: reading input, printing output, and managing the conversation flow.
- **Implementation**: A simple `while` loop that takes user input via `input()` and passes it to the Agent Orchestrator.

### 3.2. Agent Orchestrator (`src/agent.py`)
- **Responsibility**: The brain of the application. It orchestrates the entire process from receiving user input to returning a final answer.
- **Implementation**: This module will initialize the `crewAI` components (Agents, Tasks, and a Crew), load them with tools, manage the interaction with the LLM Service, and execute the tool-calling logic.

### 3.3. LLM Service (`src/llm_service.py`)
- **Responsibility**: A dedicated interface for all communications with the Large Language Model.
- **Implementation**: A function or simple class that configures the `OpenRouter` client using the API key from the `.env` file and makes the actual API calls. This isolates LLM provider-specific code.

### 3.4. Tool Subsystem (`src/tools.py`)
- **Responsibility**: Dynamically acquiring and representing the K8s tools.
- **Implementation (MVP Simplification)**:
    - Based on our [Tools Survey](./TOOLS_SURVEY.md), we will **not** build the full SSE client to connect to the `k8s mcp server` in the MVP.
    - Instead, we will create a **mock tool** within this file that accurately reflects a real tool: `GET_CLUSTER_INFO`.
    - This `GET_CLUSTER_INFO` function will return a hardcoded dictionary of fake cluster data (e.g., `{'version': 'v1.28.0', 'platform': 'linux/amd64', 'status': 'active'}`).
    - This approach allows us to build and test the entire agent-LLM-tool loop with a realistic tool, without the dependency on the external MCP server.

## 4. Data Flow (MVP Scenario: "帮我查看一下k8s状态")
1.  **User**: Runs `python src/main.py` and types "帮我查看一下k8s状态".
2.  **`main.py`**: Captures the input and passes it to the `Agent Orchestrator`.
3.  **`agent.py`**:
    - Takes the input string.
    - Adds the `GET_CLUSTER_INFO` mock tool to its toolset.
    - Formats a prompt for the LLM, including the user's query and the available tool's definition.
    - Sends the request to the `LLM Service`.
4.  **`llm_service.py`**: Calls the OpenRouter API with the prompt.
5.  **LLM**: Analyzes the request and determines that it needs to call the `GET_CLUSTER_INFO` tool. It responds with a structured message indicating this intent.
6.  **`agent.py`**:
    - Parses the LLM's response.
    - Recognizes the request to call `GET_CLUSTER_INFO`.
    - Executes the local `GET_CLUSTER_INFO` mock function from `tools.py`.
7.  **`tools.py`**: The mock function runs and instantly returns the hardcoded cluster information dictionary.
8.  **`agent.py`**:
    - Takes the tool's output.
    - Makes a second call to the LLM, providing the tool's output and asking it to formulate a user-friendly response.
9.  **LLM**: Generates a natural language sentence, e.g., "好的，当前集群状态正常，版本为 v1.28.0。"
10. **`agent.py`**: Receives the final text response.
11. **`main.py`**: Prints the final response to the console.

## 5. Proposed Project Structure
```
k8s-copilot/
├── .venv/
├── doc/
│   ├── ARCHITECTURE.md
│   └── PRD.md
├── src/
│   ├── __init__.py
│   ├── main.py         # CLI entry point
│   ├── agent.py        # Core agent logic
│   ├── llm_service.py  # LLM communication
│   └── tools.py        # Mock tools for MVP
├── .env.example        # Example environment variables
├── .gitignore
└── README.md
``` 