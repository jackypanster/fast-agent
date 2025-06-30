# K8s Copilot: MVP 实施任务清单
# Ops Crew: MVP 实施任务清单

## 1. 目的
本文档旨在将 Ops Crew 的 MVP 开发过程分解为一系列小规模、原子化、可独立验收的任务。我们的核心目标是遵循"每个代码文件的代码行数越少越好"的原则，确保每一步的产出都简洁、清晰。

本文档是实现 [技术架构 (ARCHITECTURE.md)](./ARCHITECTURE.md) 和 [伪代码 (MVP_PSEUDOCODE.md)](./MVP_PSEUDOCODE.md) 的具体行动计划。

**📋 项目状态**: 🎉 **MVP 全部完成** + 🚀 **升级为多 Agent 协作架构**

---

## 2. 任务分解 (Task Breakdown)

### ✅ 任务 0: 环境准备 (已完成)
- [x] 创建 Python 虚拟环境 (`.venv`)
- [x] 创建本地环境变量文件 (`.env`)

---

### ✅ **任务 1: 项目结构初始化** (已完成)

**目标**: 创建 MVP 所需的目录和文件，为后续编码工作打下基础。

**验收标准**:
1.  ✅ 根目录下创建 `src` 目录。
2.  ✅ 在 `src` 目录下创建 Python 文件和包。
3.  ✅ 在项目根目录创建 `.env` 文件。
4.  ✅ 在项目根目录创建 `requirements.txt` 文件。

**🚀 架构升级**:
- ✅ **项目重命名**: `k8s_copilot` -> `ops_crew`，以反映更广泛的运维能力。
- ✅ **包结构**: 创建 `src/ops_crew/` 和 `src/ops_crew/config/`。
- ✅ **YAML 配置**: 添加 `agents.yaml`, `tasks.yaml`，支持多 Agent/Task。
- ✅ **自动化脚本**: 创建 `run.sh` 简化启动流程。

---

### ✅ **任务 2: 实现独立的工具集** (已完成并扩展)

**目标**: 编写并验证 MVP 所需的工具，确保其可以独立工作。

**验收标准**:
1.  ✅ 在 `src/tools.py` 中，实现 `get_cluster_info` 函数。
2.  ✅ 可通过 `uv run python src/tools.py` 独立测试。

**🚀 架构升级**:
- ✅ **双工具系统**:
  - **本地工具**: `get_cluster_info` 提供 K8s 模拟数据。
  - **远程MCP工具**: 通过 `MCPServerAdapter` 集成外部 MCP 服务器，为 `web_researcher` 提供了 `fetch` 能力。
- ✅ **真实数据**: `get_cluster_info` 中包含 9 个生产级 K8s 集群的详细数据。

---

### ✅ **任务 3: 实现 Crew 编排逻辑** (已完成并升级)

**目标**: 按照 `crewAI` 的范式，定义 Agent、Task 和 Crew。

**验收标准**:
1.  ✅ 在 `src/ops_crew/crew.py` 中完成 `run_crew(user_input)` 函数。
2.  ✅ 成功导入工具。
3.  ✅ 正确初始化 Agent、Task、Crew。
4.  ✅ 从 `.env` 文件读取 API Key。

**🚀 架构升级**:
- ✅ **多 Agent 协作**:
  - 定义了 `k8s_expert` 和 `web_researcher` 两个职责分离的 Agent。
  - 为每个 Agent 分配了专属的工具和任务。
- ✅ **官方最佳实践**:
  - 使用 `@CrewBase` 装饰器模式。
  - Agent 和 Task 配置分离到 YAML 文件。
  - 使用 `@agent`、`@task`、`@crew` 装饰器。

---

### ✅ **任务 4: 实现 CLI 用户交互入口** (已完成并优化)

**目标**: 编写用户与应用程序交互的命令行界面。

**验收标准**:
1.  ✅ 在 `src/main.py` 中完成 `main()` 函数。
2.  ✅ 包含持续接收用户输入的 `while` 循环。
3.  ✅ 正确调用 `run_crew()` 函数。
4.  ✅ 将结果打印到控制台。
5.  ✅ 输入 "exit" 时正常退出。

**🎨 用户体验增强**:
- ✅ **品牌一致**: UI 提示从 "K8s Copilot" 更新为 "Ops Crew"。
- ✅ **代码整洁**: 移除了不必要的 `sys.path` 修改。
- ✅ **错误处理**: 完善的异常处理和用户提示。
- ✅ **API 检查**: 启动时验证 API 密钥配置。

---

### ✅ **任务 5: 集成测试与最终验收** (已完成)

**目标**: 确保所有模块能够协同工作，完整地响应用户请求。

**验收标准**:
1.  ✅ 在 `.env` 文件中配置有效的 `OPENROUTER_API_KEY`。
2.  ✅ 通过 `uv pip install -r requirements.txt` 成功安装依赖。
3.  ✅ 通过 `./run.sh` 启动程序。
4.  ✅ 输入包含 K8s 和 URL 的混合指令。
5.  ✅ 看到两个 Agent 依次执行任务的日志。
6.  ✅ 看到 `get_cluster_info` 和 `fetch` 工具被调用的信息。
7.  ✅ 获得 LLM 整合两个任务结果后的专业回答。

**🏆 实际测试结果**:
- ✅ **完整流程**: 证明了多 Agent 按顺序协作处理复杂任务的能力。
- ✅ **专业输出**: DevOps 级别的集群分析报告与网络信息摘要的结合。

---

### ✅ **任务 7: 自动发现并缓存 MCP 工具清单** (已完成)

**目标**: 通过专用的 **Tool Inspector Agent**，在启动阶段自动调用 MCP 服务器获取全部工具清单，并将其缓存到 `tools_cache.json`（有效期 24h）。

**关键成果**:
- ✅ **Tool Inspector Agent**：实现自动工具发现与缓存刷新逻辑。
- ✅ **缓存机制**：首次启动自动创建 `tools_cache.json`，24 小时内读取缓存，过期后自动刷新。
- ✅ **CLI 接口**：`src/tool_inspector.py` 提供 `--refresh / --check / --list` 等命令行参数，方便手动管理缓存。
- ✅ **白名单过滤**：其他业务 Agent 可按 `list_ / get_ / describe_` 前缀白名单加载工具。

**验收结果**:
- [x] 首次启动时生成 `tools_cache.json`（已验证）。
- [x] 24h 内再次启动直接读取缓存（已验证）。
- [x] 删除缓存文件后自动重新拉取（已验证）。
- [x] CLI 工具可列出、检查并刷新缓存（已验证）。

---

## 3. 🚀 核心架构演进总结

### 3.1. 从单一到多元
- **从**: 单一功能的 `K8s Copilot`。
- **到**: 可扩展的、多 Agent 协作的 `Ops Crew` 平台。

### 3.2. 从模拟到真实
- **从**: 仅支持本地模拟工具。
- **到**: 同时支持本地工具和**真实的远程 MCP 工具**，验证了框架的可扩展性。

### 3.3. 从代码到配置
- **从**: 硬编码的 Agent 和 Task 定义。
- **到**: YAML 配置文件驱动的声明式定义，更易于维护和扩展。

**🏁 结论**: Ops Crew MVP 不仅完成了所有预定目标，更通过一次漂亮的架构升级，演变成了一个具备多领域能力、遵循官方最佳实践、易于扩展的智能运维平台。

---

## 4. 🚀 下一阶段任务：启用并测试持久化记忆

### **任务 6: 实现并验证持久化记忆**

**目标**: 为 Ops Crew 启用 CrewAI 的内置记忆系统，使其具备跨会话学习和上下文感知能力。

**验收标准**:
1.  **配置**:
    - ✅ 在 `src/ops_crew/crew.py` 中，为 `Crew` 对象添加 `memory=True` 参数。
    - ✅ 在 `.env` 文件中，设置 `CREWAI_STORAGE_DIR=./crew_memory`，确保记忆文件存储在项目本地。
2.  **验证**:
    - ✅ 运行程序后，能看到 `./crew_memory` 目录被自动创建，并包含数据库文件。
    - ✅ **多轮对话测试**:
        - **第一轮**: "show me all k8s clusters" -> 正常返回报告。
        - **第二轮**: "which one is the prod cluster?" -> Agent 能在不重新调用工具的情况下，利用短期记忆回答 "prod-cluster-1"。
    - ✅ **跨会话测试**:
        - **关闭并重新启动**程序。
        - **提问**: "tell me about the prod cluster I asked about last time" -> Agent 能利用长期记忆，回忆起 "prod-cluster-1" 并给出相关信息。 