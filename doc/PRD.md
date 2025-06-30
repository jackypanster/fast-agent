# 智能平台助手 (Platform Agent) 产品需求文档 (PRD)

## 1. 愿景与目标

### 1.1. 愿景
构建一个企业级的、由多个专家 Agent 协作的智能平台助手（Platform Agent）。

### 1.2. 核心目标
赋能团队所有成员（包括开发者、测试、运维），使其能通过自然语言与复杂的运维任务进行高效、安全的交互。Platform Agent 将集成多种工具，处理包括但不限于 Kubernetes 管理、网络信息获取、系统监控等多方面的工作，旨在将繁琐的运维操作自动化、智能化。

---

## 2. 核心功能需求

### 2.1. 系统集成
1.  **Agent 框架**: 基于 `crewAI` (https://www.crewai.com/) Python 框架进行开发，并遵循其多 Agent 协作的最佳实践。
2.  **工具集**:
    - **本地工具**: 支持加载本地 Python 函数作为工具（如获取 K8s 集群信息的模拟工具）。
    - **远程 MCP 工具**: 必须能够通过 `MCPServerAdapter` 连接并加载外部 MCP 服务器提供的工具集（如网页抓取、未来要集成的 `k8s mcp server` 等）。
3.  **LLM 集成**: 集成 Google `gemini-2.5-flash` 大语言模型。模型服务通过 `OpenRouter` (https://openrouter.ai/) 接入，配置信息通过 `.env` 文件管理。
4.  **记忆系统**: 必须启用并配置 CrewAI 的持久化记忆功能。这为 Agent 提供了跨会话的学习能力，是实现高级交互的基础。

### 2.2. 核心交互体验：多 Agent 协作
Platform Agent 的核心是不同领域的专家 Agent 协同工作，共同完成用户的复杂请求。
1.  **职责分离**: 每个 Agent 都有明确的角色（如 K8s 专家、网络研究员）和专属的工具集。
2.  **顺序流转**: 对于一个包含多个子任务的请求，Crew 会按顺序将任务分配给最合适的 Agent。例如，先由 K8s 专家分析集群，再由网络研究员抓取相关文档。
3.  **上下文共享与记忆**: Crew 中的所有 Agent 共享同一个记忆库。这使得它们不仅能理解初始的用户请求，还能回忆起历史交互，从而做出更智能、更具上下文的决策。

### 2.3. 核心交互场景示例
**场景**: DevOps 工程师 `Charlie` 需要快速了解当前所有 K8s 集群的概况，并同时获取 `crewAI` 官方网站的最新信息以评估其新特性。

**交互流程**:
1.  **Charlie**: "show me all k8s clusters and also fetch the main content from https://crewai.com"
2.  **Platform Agent (启动)**: Crew 接收到指令，开始顺序执行任务流。
3.  **K8s Expert Agent (任务一)**:
    - **分析**: "请求中包含'k8s clusters'，这属于我的职责范围。"
    - **行动**: 调用 `get_cluster_info` 工具。
    - **输出**: 生成一份详细的 K8s 集群分析报告，并将其存入记忆。
4.  **Web Researcher Agent (任务二)**:
    - **分析**: "请求中包含 URL 'https://crewai.com'，这是我的任务。"
    - **行动**: 通过 MCP 连接调用 `fetch` 工具。
    - **输出**: 生成一份 `crewai.com` 网站内容的摘要，并将其存入记忆。
5.  **Platform Agent (整合)**: Crew 整合两个 Agent 的输出，形成一份完整的、包含两部分内容的最终报告。
6.  **Charlie**: (收到一份包含 K8s 集群状态和网站摘要的综合报告)。

### 2.4. (规划中) 主动式引导与教学
*此部分功能继承自原 Platform Agent 设想，是下一步针对单个 Agent 进行能力增强的方向。*
1.  **快捷指令**
2.  **引导式探索**
3.  **运维最佳实践教学**

### 2.5. (规划中) 性能与效率：缓存策略
*此部分为未来优化项。*
1.  **缓存目标**
2.  **缓存实现**

---

## 4. MVP 实施计划与技术选型

### 4.1. 技术栈 (Technology Stack)
- **Python 环境与包管理**: `uv`
- **Agent 框架**: `crewAI`
- **LLM Provider**: `OpenRouter` (模型: `google/gemini-2.5-flash-preview-05-20`)

### 4.2. MVP 范围 (已完成并扩展)
- **交付形态**: 命令行界面 (CLI) 应用。
- **核心用户故事**: 完整实现对包含 K8s 分析和网络抓取两种任务的混合指令的响应。
- **成功标准**:
    1. 用户在 CLI 中输入混合指令。
    2. Platform Agent 成功启动，并将任务正确分配给两个 Agent。
    3. `k8s_expert` Agent 成功调用本地 `get_cluster_info` 工具。
    4. `web_researcher` Agent 成功调用远程 MCP `fetch` 工具。
    5. 程序将两个 Agent 的结果整合后，以清晰的格式打印在 CLI 中。

### 4.3. 开发原则 (Development Principles)
- **编码风格**: 遵循 CrewAI 官方最佳实践，使用 `@CrewBase` 和配置驱动的模式。
- **核心目标**: **用最少的代码跑通多 Agent 协作的核心链路**。
- **下一阶段目标**: **启用并验证持久化记忆能力**。

---

## 5. 已分离的需求：K8s 状态数据持久化

原 PRD 中提到的"将 K8s 所有信息统计出来并持久化到数据库"是一个明确的、周期性的数据提取（ETL）任务。

**结论**：**不建议**使用 LLM Agent 来执行此任务。

**理由**：
- **稳定性**: 传统脚本是确定性的，而 Agent 的多步推理存在不确定性，可能导致数据遗漏或错误。
- **成本效益**: ETL 任务需要高频、全量抓取，使用 LLM 会产生不必要的持续性API调用成本。
- **性能**: 专用脚本的执行效率远高于 Agent 的"思考->执行"循环。

**建议方案**:
- 使用官方的 `kubernetes-python` 客户端库，编写一个独立的、健壮的 Python 脚本。
- 该脚本负责连接 K8s API Server，遍历所需资源（Cluster, Namespace, Pod, PV, PVC 等），并将结果存入目标数据库。
- 可通过 CronJob 或其他调度系统实现该脚本的周期性执行。

此任务将作为独立项目进行，与 Platform Agent 项目解耦。

ref:

1. https://github.com/HSn0918/kubernetes-mcp
2. https://github.com/crewAI/crewAI
3. https://docs.crewai.com/
4. https://docs.crewai.com/en/concepts/memory (Memory System)
5. https://openrouter.ai/google/gemini-2.5-flash-preview-05-20
6. https://docs.crewai.com/en/mcp/overview (MCP Integration)
