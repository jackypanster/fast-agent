# K8s 智能运维助手 (K8s Copilot) 产品需求文档 (PRD)

## 1. 愿景与目标

### 1.1. 愿景
构建一个企业级的、交互式的 Kubernetes 智能运维助手（K8s Copilot）。

### 1.2. 核心目标
赋能团队所有成员（包括开发者、测试、运维），使其能通过自然语言与 Kubernetes 集群进行高效、安全的交互，从而极大地降低 K8s 的使用门槛，提升日常管理和问题排查的效率。

---

## 2. 核心功能需求

### 2.1. 系统集成
1.  **Agent 框架**: 基于 `crewAI` (https://www.crewai.com/) Python 框架进行开发。
2.  **K8s 工具集**: 动态连接并加载由内部 `k8s mcp server` (http://localhost:8001/sse) 提供的全套（约 47 个）K8s 管理工具。Agent 必须能够理解并使用这些动态加载的工具。
3.  **LLM 集成**: 集成 Google `gemini-2.5-flash` 大语言模型。模型服务通过 `OpenRouter` (https://openrouter.ai/) 接入，相关的 API Key 等配置信息需通过本地 `.env` 文件进行管理，确保安全与灵活性。

### 2.2. 核心交互体验：引导式对话（Guided Conversation）
Copilot 必须能够智能地引导用户，特别是对 K8s 不熟悉的成员，完成操作。这是产品的核心价值所在。
1.  **多轮对话与参数补全**: 当用户指令缺少必要参数时（如 `pod_name`, `namespace`），Copilot 必须通过反问来澄清，引导用户补全信息，而不是直接报错。
2.  **主动推荐与选项列表**: 当用户不清楚参数值时，Copilot 应主动调用其他工具（如 `list_namespaces`）查询可能的选项，并以列表形式呈现给用户，将"填空题"变为"选择题"。
3.  **上下文感知**: Copilot 需具备上下文记忆能力。在连续对话中，能够复用之前提到的实体（如 `namespace`），避免重复提问。
4.  **复杂意图分解**: 对于模糊的、高层次的运维指令（如"检查服务健康状况"），Copilot 应能将其分解为一系列具体的、可执行的工具调用步骤，并向用户确认后执行。

### 2.3. 核心交互场景示例
**场景**: 新手开发者 `Alex` 需要查看他刚刚部署的应用 `cart-service` 的日志，但他不确定完整的 Pod 名称和所在的命名空间。

**交互流程**:
1.  **Alex**: "hi，帮我看一下 `cart-service` 的日志"
2.  **Copilot**: "好的。为了找到正确的日志，我需要知道它在哪个 **命名空间（Namespace）** 里。您知道吗？如果您不确定，我可以列出所有的命名空间供您选择。"
3.  **Alex**: "我不确定，你列出来吧"
4.  **Copilot**: (调用 `list_namespaces`) "好的，当前集群有以下命名空间：`[default, dev, production]`。您觉得 `cart-service` 可能在哪个里面？"
5.  **Alex**: "应该在 `dev`"
6.  **Copilot**: (调用 `list_pods(namespace='dev')`) "收到。在 `dev` 命名空间下，我找到了几个包含 `cart-service` 的 Pod：`[cart-service-v1-abcdef, cart-service-v2-ghijk]`。您想看哪个的日志？"
7.  **Alex**: "v2 那个"
8.  **Copilot**: (调用 `get_pod_logs(namespace='dev', pod_name='cart-service-v2-ghijk')`) "好的，正在拉取 `cart-service-v2-ghijk` 的日志..." (展示日志)

### 2.4. 主动式引导与教学（Proactive Guidance & Tutoring）
为了降低学习曲线并固化最佳实践，Copilot 需要具备主动引导和教学的能力。

1.  **快捷指令（Quick Commands）**:
    -   为了方便用户快速上手，Copilot 应提供一组无需参数的"快捷指令"。
    -   这些指令可以在对话开始时或用户请求帮助时主动推送。
    -   **示例**: `[列出所有集群]`, `[查看集群资源总览]`, `[显示所有命名空间]`。用户可以直接点击或输入来执行。

2.  **引导式探索（Guided Exploration）**:
    -   Copilot 不应被动地等待命令，而应在每次操作后，根据上下文智能推荐下一步可能的操作。
    -   **示例**: 当用户列出所有 Pod 后，Copilot 可以追问："接下来，您可能想 `[查看某个Pod的日志]`，`[获取Pod的详细描述]` 或者 `[检查Pod的事件]`。您想做什么？"

3.  **运维最佳实践教学（Teaching Best Practices）**:
    -   Copilot 应化身为 K8s 导师，在交互中教授用户最佳实践。
    -   **示例**: 如果用户在排查问题，Copilot 可以建议："在查看日志之前，检查一下 Pod 的 `Events` 通常能更快地发现部署、调度或健康检查相关的问题。需要我帮您查一下吗？"

### 2.5. 性能与效率：缓存策略 (Performance & Efficiency: Caching)
为了提升响应速度、降低系统负载并优化成本，Copilot 必须实现一套智能缓存机制。

1.  **缓存目标**:
    -   **高频只读操作**: 优先缓存高频的、重复性强的查询操作结果，特别是各类 `list` 操作（如 `list_clusters`, `list_namespaces`）。
    -   **半静态数据**: 对于不经常变动的数据（如集群名称、节点信息），应采用较长的缓存时间。

2.  **缓存实现**:
    -   **缓存存储**: 初期可使用简单的**内存缓存**实现。
    -   **缓存周期 (TTL)**: 缓存必须带有过期时间（Time-To-Live）。不同数据的 TTL 应不同（例如：集群列表1小时，命名空间列表5分钟）。
    -   **智能失效与刷新**:
        -   Copilot 应默认优先使用缓存数据进行响应。
        -   当后续操作基于缓存数据执行失败时（例如：在一个已不存在的缓存命名空间中查找 Pod），Copilot 必须能智能地识别出数据已失效。
        -   识别失效后，应自动清除相关缓存，重新调用工具获取最新数据，并完成用户请求。
    -   **手动刷新**: 提供一个明确的指令（如 `[刷新缓存]` 或 `[重新扫描]`），允许用户在需要时强制清除所有缓存，获取最新状态。

---

## 4. MVP 实施计划与技术选型

### 4.1. 技术栈 (Technology Stack)
- **Python 环境与包管理**: `uv` ([https://github.com/astral-sh/uv](https://github.com/astral-sh/uv))。利用其高效的特性管理项目虚拟环境和依赖。
- **Agent 框架**: `crewAI`。
- **LLM Provider**: `OpenRouter` (模型: `google/gemini-2.5-flash-preview-05-20`)。

### 4.2. MVP 范围 (MVP Scope)
- **交付形态**: 命令行界面 (CLI) 应用。暂不考虑图形化界面。
- **核心用户故事**: 完整实现对用户指令 **"帮我查看一下k8s状态"** 的响应。
- **成功标准**:
    1. 用户在 CLI 中输入指令。
    2. 程序能够调用 LLM 理解用户意图。
    3. LLM 规划出需要调用 `list_clusters` (或类似) 工具。
    4. 程序执行工具，成功从 `k8s mcp server` 获取到集群列表。
    5. 程序将查询到的集群列表信息，以人类可读的格式打印在 CLI 中。

### 4.3. 开发原则 (Development Principles)
- **编码风格**: 采用简洁、平铺直叙的函数式风格，避免复杂的类和抽象。
- **核心目标**: **用最少的代码跑通 MVP**。优先保证核心链路能够工作，此阶段不追求代码的健壮性、性能优化和完备的错误处理。

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

此任务将作为独立项目进行，与 K8s Copilot 项目解耦。

ref:

1. https://github.com/HSn0918/kubernetes-mcp
2. https://github.com/crewAI/crewAI
3. https://docs.crewai.com/
4. https://openrouter.ai/google/gemini-2.5-flash-preview-05-20
