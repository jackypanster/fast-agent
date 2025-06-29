# K8s Copilot: MVP 实施任务清单

## 1. 目的
本文档旨在将 K8s Copilot 的 MVP 开发过程分解为一系列小规模、原子化、可独立验收的任务。我们的核心目标是遵循"每个代码文件的代码行数越少越好"的原则，确保每一步的产出都简洁、清晰。

本文档是实现 [技术架构 (ARCHITECTURE.md)](./ARCHITECTURE.md) 和 [伪代码 (MVP_PSEUDOCODE.md)](./MVP_PSEUDOCODE.md) 的具体行动计划。

---

## 2. 任务分解 (Task Breakdown)

### ☑️ 任务 0: 环境准备 (已完成)
- [x] 创建 Python 虚拟环境 (`.venv`)
- [x] 创建本地环境变量文件 (`.env`)

---

### ☐ **任务 1: 项目结构初始化**

**目标**: 创建 MVP 所需的目录和文件，为后续编码工作打下基础。

**验收标准**:
1.  根目录下创建 `src` 目录。
2.  在 `src` 目录下创建以下空的 Python 文件：
    - `__init__.py`
    - `main.py` (CLI 入口)
    - `crew.py` (Crew 编排)
    - `tools.py` (工具定义)
3.  在项目根目录创建 `.env.example` 文件，并包含一行 `OPENROUTER_API_KEY=""` 作为示例。
4.  在项目根目录创建 `requirements.txt` 文件，并填入以下核心依赖：
    ```
    crewai
    crewai-tools
    python-dotenv
    langchain-community
    ```

---

### ☐ **任务 2: 实现独立的模拟工具 (Implement Mock Tool)**

**目标**: 编写并验证 MVP 所需的模拟工具，确保其可以独立工作。

**验收标准**:
1.  在 `src/tools.py` 中，实现伪代码中描述的 `GET_CLUSTER_INFO` 函数。
2.  该函数返回一个固定的、包含模拟集群信息的字典。
3.  函数内部包含一个 `print` 语句，用于在调用时在控制台明确地打印出提示信息（如 `--- TOOL CALLED: GET_CLUSTER_INFO() ---`）。
4.  可以通过直接运行 `python src/tools.py` 来测试该函数，并成功在控制台看到它的 `print` 输出和返回的字典内容，以此证明该模块的原子性和正确性。

---

### ☐ **任务 3: 实现 Crew 编排逻辑 (Implement Crew Orchestrator)**

**目标**: 按照 `crewAI` 的范式，定义 Agent、Task 和 Crew。

**验收标准**:
1.  在 `src/crew.py` 中，完成伪代码中描述的 `run_crew(user_input)` 函数。
2.  代码成功从 `src/tools.py` 导入 `GET_CLUSTER_INFO` 工具。
3.  代码根据伪代码的定义，正确初始化 `k8s_expert` Agent、`query_task` Task，以及 `k8s_status_crew` Crew。
4.  代码能从 `.env` 文件中正确读取 `OPENROUTER_API_KEY` 并配置 `ChatOpenRouter`。
5.  此阶段，该文件自身无法独立运行，它依赖于任务 2 和任务 4。

---

### ☐ **任务 4: 实现 CLI 用户交互入口 (Implement CLI Entrypoint)**

**目标**: 编写用户与应用程序交互的命令行界面。

**验收标准**:
1.  在 `src/main.py` 中，完成伪代码中描述的 `main()` 函数。
2.  程序包含一个 `while` 循环，能持续接收用户输入。
3.  程序能正确调用从 `src/crew.py` 导入的 `run_crew()` 函数。
4.  程序能将 `run_crew()` 返回的最终结果打印到控制台。
5.  输入 "exit" 时，程序能够正常退出。

---

### ☐ **任务 5: 集成测试与最终验收 (Integration Test)**

**目标**: 确保所有模块能够协同工作，完整地响应用户请求。

**验收标准**:
1.  在 `.env` 文件中配置好有效的 `OPENROUTER_API_KEY`。
2.  在虚拟环境中，通过 `uv pip install -r requirements.txt` 成功安装所有依赖。
3.  运行 `python src/main.py` 启动程序。
4.  输入指令 "帮我查看一下k8s状态"。
5.  控制台打印出 `crewAI` 的详细执行过程（因为 `verbose=2`）。
6.  在执行过程中，能看到任务 2 中定义的工具被调用的 `print` 信息。
7.  程序最终输出一句由 LLM 生成的、人类可读的、总结了集群状态的回答。 