# K8s Copilot: MVP 伪代码与交互流程

## 1. 目的
本文档为初级开发者提供一份高度简化的伪代码，用于描述 MVP 的核心逻辑。它旨在帮助开发者在不关心具体库实现的情况下，快速理解"从用户输入到系统输出"的全过程。

本文档是 [技术架构文档](./ARCHITECTURE.md) 的具体实现蓝图。

## 2. 文件伪代码

### 2.1. `src/tools.py`
```python
# 伪代码: tools.py

# 我们只需要定义一个简单的函数，它不需要任何参数，
# 并且返回一个固定的、代表集群信息的 Python 字典。
# 这个函数模拟了我们从 `kubernetes-mcp` 调研出的 GET_CLUSTER_INFO 工具。

FUNCTION GET_CLUSTER_INFO():
    # 打印一条消息，这样我们运行时就能清楚地看到这个函数被调用了。
    PRINT "--- MOCK TOOL: GET_CLUSTER_INFO() CALLED ---"

    # 返回一个写死的数据结构。
    RETURN {
        "version": "v1.28.0",
        "platform": "linux/amd64",
        "status": "active"
    }
END FUNCTION
```

### 2.2. `src/llm_service.py`
```python
# 伪代码: llm_service.py
# 这个文件负责与大模型服务（OpenRouter）的所有交互。

# 需要引入 fast-agent 的 ChatPrompt 模板和 OpenRouter 的客户端
IMPORT ChatPrompt from fast_agent.prompt
IMPORT OpenRouter from openrouter

# 定义一个函数，它接收用户的输入和可用的工具列表
FUNCTION get_llm_response(user_input, tools):
    # 1. 从环境变量中读取 API Key (这部分需要一个 .env 文件)
    api_key = GET_ENVIRONMENT_VARIABLE("OPENROUTER_API_KEY")

    # 2. 初始化 OpenRouter 客户端
    client = OpenRouter(api_key=api_key)

    # 3. 创建一个 fast-agent 的 prompt 实例
    prompt = ChatPrompt()

    # 4. 调用 prompt 的 `build` 方法，传入用户输入和工具
    #    这会生成一个符合 LLM API 要求的、结构化的消息列表
    messages = prompt.build(user_input, tools=tools)

    # 5. 调用 OpenRouter 客户端，发送消息，并指定使用哪个模型
    response = client.chat.completions.create(
        model="google/gemini-2.5-flash-preview-05-20",
        messages=messages,
    )

    # 6. 返回从 LLM 得到的完整响应对象
    RETURN response
END FUNCTION
```

### 2.3. `src/agent.py`
```python
# 伪代码: agent.py
# 这是我们系统的核心，负责编排一切。

# 引入我们自己写的 llm_service 和 tools
IMPORT GET_CLUSTER_INFO from tools
IMPORT get_llm_response from llm_service

# 引入 fast-agent 的 Agent 类
IMPORT Agent from fast_agent

# 定义一个主函数，接收用户的原始输入
FUNCTION run_agent(user_input):
    # 1. 初始化 Agent
    #    我们把模拟工具 GET_CLUSTER_INFO 作为一个列表传给它。
    agent = Agent(tools=[GET_CLUSTER_INFO])

    # 2. 调用 Agent 的 `run` 方法
    #    这个方法是整个流程的入口。它需要一个回调函数来实际调用 LLM。
    #    我们把 `get_llm_response` 函数作为回调传给它。
    final_response = agent.run(user_input, llm_callback=get_llm_response)

    # 3. Agent 的 `run` 方法会自动处理所有事情：
    #    - 调用 get_llm_response，第一次询问 LLM 该怎么做。
    #    - LLM 返回说要调用 GET_CLUSTER_INFO 工具。
    #    - Agent 解析 LLM 的回答，并自动执行 GET_CLUSTER_INFO() 函数。
    #    - Agent 拿到工具的返回结果。
    #    - Agent 再次调用 get_llm_response，把工具结果给 LLM，让它生成最终回复。
    #    - Agent 返回最终的人类可读的回复。

    # 4. 返回这个最终回复
    RETURN final_response
END FUNCTION
```

### 2.4. `src/main.py`
```python
# 伪代码: main.py
# 这是用户直接运行的程序入口。

# 引入我们写的 agent
IMPORT run_agent from agent

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

        # 3. 调用我们的 Agent Orchestrator，并传入用户输入
        agent_response = run_agent(user_input)

        # 4. 将 Agent 返回的结果打印到控制台
        PRINT "Copilot: ", agent_response
    END WHILE

    PRINT "Shutting down. Goodbye!"
END FUNCTION

# 当这个文件被直接执行时，调用 main 函数
IF __name__ == "__main__":
    main()
``` 