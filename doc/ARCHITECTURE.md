# Platform Agent 架构文档

## 1. 系统概述

Platform Agent 是一个基于 `crewai` 框架构建的智能多智能体（Multi-Agent）系统，旨在为平台运维人员提供一个自然语言交互接口，以查询和管理 Kubernetes (k8s) 集群。

系统的核心设计思想是**任务自动化**和**动态工具发现**。它通过一个专门的“工具勘察员” Agent 自动发现和缓存可用的 k8s 操作工具，再由一个“k8s 专家” Agent 利用这些工具来响应用户的请求。这种设计使得系统具有高度的可扩展性，能够适应不断变化的运维环境。

## 2. 核心模块职责

### 2.1. `main.py` - 用户交互入口

- **职责**: 作为应用程序的主入口点，提供一个交互式的命令行界面 (CLI)。
- **功能**:
  - 启动和欢迎用户。
  - 检查必要的环境变量（如 `OPENROUTER_API_KEY`）是否已配置。
  - 循环接收用户输入的自然语言指令。
  - 将用户输入传递给核心处理模块 `ops_crew.crew.run_crew`。
  - 打印执行结果或错误信息。

### 2.2. `tool_inspector.py` - MCP 工具管理器

- **职责**: 一个独立的 CLI 工具，用于手动管理通过 MCP (Model Context Protocol) 发现的工具缓存。
- **功能**:
  - `--refresh`: 强制触发工具发现流程，并刷新 `tools_cache.json` 文件。
  - `--check`: 检查当前缓存的状态，包括上次更新时间、缓存龄期以及是否“陈旧”（Stale）。
  - `--list`: 详细列出缓存中的所有工具及其描述和所需参数，并按工具类型分组。
- **重要性**: 该工具对于开发、调试和 CI/CD 流程至关重要，它确保了 Agent 能够访问到最新的工具集。

### 2.3. `ops_crew/crew.py` - 核心业务逻辑

- **职责**: 定义和编排系统的核心 Agent、任务和工作流 (Crew)。
- **关键组件**:
  - **`OpsCrew` (CrewBase)**:
    - 定义了两个核心 Agent：`tool_inspector` 和 `k8s_expert`。
    - 定义了两个核心任务：`tool_discovery_task` 和 `k8s_analysis_task`。
    - 编排了两个工作流：
      - `discovery_crew`: 仅用于执行工具发现任务。
      - `ops_crew`: 用于处理用户的 k8s 相关请求，并启用了基于 Qwen 词向量的记忆功能，以理解长期对话的上下文。
  - **`_should_refresh_cache()`**: 判断工具缓存是否需要刷新（默认阈值为 24 小时），实现了缓存的自动管理。
  - **`_load_cached_tools()`**: 智能地从缓存中加载工具。它会筛选出名称以 `list_`, `get_`, `describe_` 开头的工具，专门提供给 `k8s_expert` Agent，确保其操作的专注性和相关性。
  - **`run_crew()`**: 整个系统的总指挥。它首先根据 `_should_refresh_cache()` 的结果决定是否需要运行 `discovery_crew` 来更新工具，然后启动 `ops_crew` 来执行用户的主要任务。

## 3. 数据流与工作流程

1.  **启动**: 用户在命令行运行 `python src/main.py`。
2.  **用户输入**: 用户在 `Platform Agent >` 提示符后输入一个请求，例如 "列出所有在 'default' 命名空间下的 Pods"。
3.  **任务分派**: `main.py` 捕获输入并调用 `run_crew(user_input)`。
4.  **缓存检查**: `run_crew` 调用 `_should_refresh_cache()` 检查 `tools_cache.json`。
5.  **工具发现 (如果需要)**:
    - 如果缓存不存在或已过期，`run_crew` 会启动 `discovery_crew`。
    - `tool_inspector` Agent 执行 `tool_discovery_task`，通过 `MCPServerAdapter` 扫描 MCP 服务器，并将发现的工具及其元数据写入 `tools_cache.json`。
6.  **主任务执行**:
    - `run_crew` 启动 `ops_crew`。
    - `_load_cached_tools()` 读取 `tools_cache.json`，筛选出 k8s 查询工具，并将其分配给 `k8s_expert` Agent。
    - `k8s_expert` Agent 接收到 `k8s_analysis_task`（已格式化并包含用户输入），分析用户意图。
    - Agent 根据意图选择最合适的工具（例如 `list_pods`）并执行它。
    - Agent 整合工具返回的结果，并生成一份人类可读的报告。
7.  **返回结果**: `ops_crew` 将最终报告作为结果返回给 `main.py`。
8.  **显示输出**: `main.py` 将结果打印在命令行中，完成一次交互。

## 4. 设计模式与关键技术

- **多智能体系统 (Multi-Agent System)**:
  - 采用 `crewai` 框架，将复杂的任务分解给不同角色的 Agent（`tool_inspector`, `k8s_expert`），实现了关注点分离。
- **动态工具绑定**:
  - Agent 的能力不是硬编码的，而是通过 MCP 动态发现并绑定的。这使得系统可以轻松扩展新功能，只需在 MCP 服务器端添加新工具即可。
- **缓存模式 (Cache Pattern)**:
  - 通过 `tools_cache.json` 缓存工具定义，避免了每次运行时都进行耗时的工具发现，显著提升了启动速度和性能。
- **记忆与上下文管理**:
  - `ops_crew` 启用了 `memory=True`，并配置了 `qwen_embedder`。这使得 Agent 能够记住之前的对话内容，从而处理更复杂的、有上下文依赖的连续性任务。

## 5. 目录结构说明

```
.
├── doc/
│   └── ARCHITECTURE.md       # (本文档) 架构说明
├── src/
│   ├── __init__.py
│   ├── main.py               # CLI 交互主程序
│   ├── tool_inspector.py     # MCP 工具缓存管理工具
│   └── ops_crew/
│       ├── __init__.py
│       ├── crew.py           # 核心 Agent 和 Crew 定义
│       └── config/
│           ├── agents.yaml   # Agent 配置 (角色、目标等)
│           └── tasks.yaml    # Task 配置 (任务描述等)
├── .env                      # 环境变量 (API Keys, URLs)
├── requirements.txt          # Python 依赖
└── tools_cache.json          # 动态生成的工具缓存文件
