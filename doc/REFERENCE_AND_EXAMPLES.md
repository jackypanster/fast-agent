# Platform Agent - 函数参考和使用示例

本文档提供了 Platform Agent 系统中主要函数、类和方法的详细参考，并附带了具体的使用示例，以帮助开发者和用户理解和使用该系统。

## 1. 函数与方法参考

### 1.1. `src/main.py`

---

#### `main()`

- **功能概述**:
  应用程序的主入口函数，负责启动和管理交互式命令行界面 (CLI)。
- **输入参数**: 无。
- **输出结果**: 无。该函数会持续运行，直到用户输入 `exit` 或 `quit`。
- **内部逻辑**:
  1.  打印欢迎信息。
  2.  检查 `OPENROUTER_API_KEY` 环境变量是否存在，如果不存在则报错并退出。
  3.  进入一个无限循环，等待用户输入。
  4.  捕获用户输入，并去除首尾空格。
  5.  如果输入是退出命令 (`exit`, `quit`, `q`)，则结束循环。
  6.  如果输入为空，则跳过本次循环。
  7.  调用 `ops_crew.crew.run_crew()` 函数处理用户输入。
  8.  打印 `run_crew()` 返回的结果。
- **异常处理**:
  - `KeyboardInterrupt`: 用户按下 `Ctrl+C` 时，优雅地退出程序。
  - `Exception`: 捕获其他所有异常，并打印错误信息，防止程序崩溃。

### 1.2. `src/tool_inspector.py`

---

#### `refresh_cache() -> Dict`

- **功能概述**:
  强制触发 MCP 工具发现流程，并刷新本地的 `tools_cache.json` 缓存文件。
- **输入参数**: 无。
- **输出结果**:
  - `Dict`: 如果缓存成功，返回一个包含新缓存内容的字典。如果失败，则返回一个空字典。
- **内部逻辑**:
  1.  实例化 `OpsCrew`。
  2.  获取 `discovery_crew`。
  3.  调用 `discovery_crew.kickoff()` 启动工具发现任务。
  4.  打印发现结果。
  5.  读取新生成的 `tools_cache.json` 文件并返回其内容。
- **异常处理**:
  - `Exception`: 捕获在工具发现过程中可能发生的任何错误，并打印错误信息。

---

#### `check_cache_status()`

- **功能概述**:
  检查并显示当前 `tools_cache.json` 缓存文件的状态。
- **输入参数**: 无。
- **输出结果**: 无。直接在控制台打印缓存状态信息。
- **内部逻辑**:
  1.  检查 `tools_cache.json` 文件是否存在。
  2.  如果存在，则读取文件内容，解析出 `fetched_at` (上次更新时间) 和 `tools` 列表。
  3.  计算缓存的“年龄”（age）。
  4.  调用 `_should_refresh_cache()` 判断缓存是否“陈旧”（stale）。
  5.  打印详细的状态信息，包括更新时间、年龄、工具数量以及是否陈旧。
- **异常处理**:
  - `json.JSONDecodeError`, `KeyError`, `ValueError`: 如果缓存文件损坏或格式不正确，则捕获异常并提示用户运行 `--refresh`。

---

#### `list_cached_tools()`

- **功能概述**:
  详细列出 `tools_cache.json` 中所有已缓存的工具及其信息。
- **输入参数**: 无。
- **输出结果**: 无。直接在控制台打印工具列表。
- **内部逻辑**:
  1.  检查 `tools_cache.json` 文件是否存在。
  2.  读取并解析缓存文件。
  3.  为了更好地组织输出，将工具按其名称前缀（如 `k8s`, `git` 等）进行分组。
  4.  遍历分组后的工具，打印每个工具的名称、描述和必要的参数。

---

#### `main()` (in `tool_inspector.py`)

- **功能概述**:
  `tool_inspector.py` 脚本的 CLI 解析和执行入口。
- **内部逻辑**:
  1.  使用 `argparse` 定义和解析命令行参数 (`--refresh`, `--check`, `--list`)。
  2.  根据用户提供的参数，依次调用 `refresh_cache()`, `check_cache_status()`, `list_cached_tools()` 等函数。
  3.  如果没有提供任何参数，则打印帮助信息。

### 1.3. `src/ops_crew/crew.py`

---

#### `OpsCrew` (class)

- **功能概述**:
  一个基于 `crewai.CrewBase` 的类，用于定义和组织整个系统的 Agent、Task 和 Crew。
- **关键属性**:
  - `agents_config`: `config/agents.yaml` 文件的路径。
  - `tasks_config`: `config/tasks.yaml` 文件的路径。
  - `mcp_server_params`: MCP 服务器的配置信息。
  - `llm`: 全局的大语言模型实例（LLM）。
- **关键方法**:
  - `@agent tool_inspector()`: 创建并返回一个 `tool_inspector` Agent 实例，该 Agent 可以访问所有 MCP 工具。
  - `@agent k8s_expert()`: 创建并返回一个 `k8s_expert` Agent 实例，该 Agent 只能访问从缓存中智能筛选出的 k8s 相关工具。
  - `@task tool_discovery_task()`: 创建并返回一个用于工具发现的任务。
  - `@task k8s_analysis_task()`: 创建并返回一个用于分析用户 k8s 请求的任务。
  - `@crew discovery_crew()`: 创建并返回一个仅包含 `tool_inspector` Agent 和 `tool_discovery_task` 的 Crew，专门用于工具发现。
  - `@crew ops_crew()`: 创建并返回主操作 Crew，包含 `k8s_expert` Agent 和 `k8s_analysis_task`，并配置了基于 Qwen 词向量的记忆系统。

---

#### `_should_refresh_cache() -> bool`

- **功能概述**:
  一个辅助函数，用于判断 `tools_cache.json` 是否需要刷新。
- **输入参数**: 无。
- **输出结果**:
  - `bool`: 如果缓存文件不存在、损坏，或距离上次更新时间超过 24 小时，则返回 `True`；否则返回 `False`。
- **前置条件**: 无。

---

#### `_load_cached_tools()`

- **功能概述**:
  从 `tools_cache.json` 文件中智能加载和筛选工具。
- **输入参数**: 无。
- **输出结果**:
  - `List[Tool]`: 返回一个 `crewai` 工具对象列表。
- **内部逻辑**:
  1.  如果缓存文件不存在或损坏，则回退到加载所有可用的 MCP 工具。
  2.  读取缓存文件，提取所有工具。
  3.  筛选出名称以下列前缀开头的工具：`list_`, `get_`, `describe_`。
  4.  如果筛选出工具，则只加载这些工具；否则，回退到加载所有工具。
- **后置条件**: 返回的工具列表将用于初始化 `k8s_expert` Agent。

---

#### `run_crew(user_input: str) -> str`

- **功能概述**:
  设置并运行 Ops Crew 以处理用户的请求，是连接 `main.py` 和 `crew.py` 的桥梁。
- **输入参数**:
  - `user_input` (`str`): 用户输入的原始问题或指令。
- **输出结果**:
  - `str`: Crew 执行后返回的最终结果。
- **内部逻辑**:
  1.  实例化 `OpsCrew`。
  2.  调用 `_should_refresh_cache()` 检查缓存状态。如果需要，则运行 `discovery_crew` 来刷新缓存。
  3.  获取 `ops_crew`。
  4.  将 `user_input` 格式化到 `k8s_analysis_task` 的任务描述中。
  5.  调用 `main_crew.kickoff()` 启动主任务流程。
  6.  返回执行结果。
- **异常处理**:
  - `Exception`: 捕获执行过程中的任何错误，并返回格式化的错误信息。

## 2. 使用示例

### 2.1. 运行交互式 Platform Agent

```bash
# 确保你的 .env 文件已配置好 OPENROUTER_API_KEY
# 运行主程序
python src/main.py
```

**示例对话:**

```
🚀 Welcome to the Platform Agent!
Type 'exit' or 'quit' to end the session.
==================================================
🤖 Platform Agent > Please list all pods in the default namespace.

🔍 Processing your request...
==================================================
... (Agent 执行过程的日志输出) ...
==================================================

📋 Result:
==================================================
Here is a list of all pods in the 'default' namespace:
- pod-A (Running)
- pod-B (Completed)
- pod-C (Running)
==================================================
🤖 Platform Agent > describe pod-A

... (Agent 处理新请求) ...
```

### 2.2. 使用 `tool_inspector.py` 管理工具缓存

#### 强制刷新缓存

如果你刚刚在 MCP 服务器上添加了一个新工具，或者怀疑缓存已损坏，可以强制刷新。

```bash
python src/tool_inspector.py --refresh
```

**输出示例:**

```
🔧 MCP Tool Inspector
==================================================
🔍 Forcing tool discovery and cache refresh...
✅ Tool discovery completed: Successfully discovered and cached 25 tools.
📋 Successfully cached 25 tools
```

#### 检查缓存状态

检查缓存是否最新。

```bash
python src/tool_inspector.py --check
```

**输出示例:**

```
🔧 MCP Tool Inspector
==================================================
📋 Cache Status:
   📅 Last updated: 2023-10-27 10:30:00
   ⏰ Age: 0:15:30.123456
   🔧 Tools cached: 25
   🟢 FRESH (24h threshold)
```

#### 列出所有缓存的工具

查看当前 Agent 可以使用的所有工具。

```bash
python src/tool_inspector.py --list
```

**输出示例:**

```
🔧 MCP Tool Inspector
==================================================
📋 Cached Tools (25 total):
================================================================================

🔧 K8S Tools:
   • k8s_list_pods
     📝 List all pods in a given Kubernetes namespace.
     📋 Required params: namespace

   • k8s_get_pod_logs
     📝 Get logs from a specific pod.
     📋 Required params: namespace, pod_name

... (其他工具) ...
