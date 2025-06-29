# K8s Copilot: MVP 伪代码与交互流程

## 1. 目的
本文档为初级开发者提供一份高度简化的伪代码，用于描述 MVP 的核心逻辑。它旨在帮助开发者在不关心具体库实现的情况下，快速理解"从用户输入到系统输出"的全过程。

本文档是 [技术架构文档](./ARCHITECTURE.md) 的具体实现蓝图，并已根据 `crewAI` 框架进行更新。

## 2. 文件伪代码

### 2.1. `src/tools.py`
```python
# 伪代码: tools.py

# 我们只需要定义一个简单的函数，它不需要任何参数，
# 并且返回一个固定的、代表集群信息的 Python 字典。
# 这个函数模拟了我们从 `kubernetes-mcp` 调研出的 GET_CLUSTER_INFO 工具。
# 在 crewAI 中，这个函数可以直接作为工具使用。

FUNCTION GET_CLUSTER_INFO():
    # 打印一条消息，这样我们运行时就能清楚地看到这个函数被调用了。
    PRINT "--- TOOL CALLED: GET_CLUSTER_INFO() ---"

    # 返回一个写死的数据结构。
    RETURN {
        "version": "v1.28.0",
        "platform": "linux/amd64",
        "status": "active"
    }
END FUNCTION
```

### 2.2. `src/crew.py` (原 `agent.py` 和 `llm_service.py`)
```python
# 伪代码: crew.py
# 这是我们系统的核心，负责定义和编排 Agent、Task 和 Crew。

# 引入我们自己写的 tools
IMPORT GET_CLUSTER_INFO from tools

# 引入 crewAI 的核心组件
IMPORT Agent, Task, Crew from "crewai"
# 引入用于连接 OpenRouter 的 LLM 客户端
IMPORT ChatOpenRouter from "langchain_community.chat_models.openrouter"


# 定义一个主函数，它接收用户的原始输入
FUNCTION run_crew(user_input):
    # 1. 从环境变量中读取 API Key
    api_key = GET_ENVIRONMENT_VARIABLE("OPENROUTER_API_KEY")

    # 2. 初始化 LLM 客户端
    #    我们告诉它使用哪个模型，并传入 API Key。
    llm = ChatOpenRouter(
        model="google/gemini-2.5-flash-preview-05-20",
        api_key=api_key
    )

    # 3. 定义我们的 K8s 运维专家 Agent
    k8s_expert = Agent(
        role="Senior Kubernetes Administrator",
        goal="Answer user questions about the Kubernetes cluster status.",
        backstory="You are a seasoned K8s expert with years of experience managing complex clusters. You use your available tools to provide clear and concise answers.",
        tools=[GET_CLUSTER_INFO], # 把我们的工具赋给 Agent
        llm=llm, # 把 LLM 赋给 Agent
        allow_delegation=False # MVP 阶段，我们不需要 Agent 之间的协作
    )

    # 4. 为 Agent 创建一个任务
    #    任务描述会结合用户的输入。
    query_task = Task(
        description=f"The user wants to know about the cluster. Here is their exact question: '{user_input}'. Use your tools to find the answer and report back.",
        agent=k8s_expert, # 把任务分配给我们的专家
        expected_output="A concise, human-readable sentence summarizing the cluster status based on the tool's output."
    )

    # 5. 组建一个 Crew (团队)
    #    团队里包含我们的 Agent 和要执行的任务。
    k8s_status_crew = Crew(
        agents=[k8s_expert],
        tasks=[query_task],
        verbose=2 # 设置为 2 可以打印出详细的思考和执行过程
    )

    # 6. 启动 Crew！
    #    `kickoff` 方法会运行整个流程，直到任务完成。
    final_response = k8s_status_crew.kickoff()

    # 7. 返回最终的回复
    RETURN final_response
END FUNCTION
```

### 2.3. `src/main.py`
```python
# 伪代码: main.py
# 这是用户直接运行的程序入口。

# 引入我们写的 crew
IMPORT run_crew from crew

# 定义主执行函数
FUNCTION main():
    # 打印一个欢迎信息
    PRINT "K8s Copilot MVP is running. Type 'exit' to quit."

    # 开始一个无限循环，来持续接收用户输入
    WHILE True:
        # 1. 从命令行读取用户输入
        user_input = READ_FROM_CONSOLE("You: ")

        # 2. 检查用户是否想退出
        IF user_input == "exit":
            BREAK

        # 3. 调用我们的 Crew Orchestrator，并传入用户输入
        agent_response = run_crew(user_input)

        # 4. 将 Agent 返回的结果打印到控制台
        PRINT "Copilot: ", agent_response
    END WHILE

    PRINT "Shutting down. Goodbye!"
END FUNCTION

# 当这个文件被直接执行时，调用 main 函数
IF __name__ == "__main__":
    main()
``` 