# Ops Crew: MVP 伪代码与交互流程

## 1. 目的
本文档为初级开发者提供一份高度简化的伪代码，用于描述 MVP 的核心逻辑。它旨在帮助开发者在不关心具体库实现的情况下，快速理解"从用户输入到系统输出"的全过程。

本文档是 [技术架构文档](./ARCHITECTURE.md) 的具体实现蓝图，并已根据 `crewAI` 的多 Agent 协作模式进行更新。

## 2. 文件伪代码

### 2.1. `src/tools.py`
```python
# 伪代码: tools.py

# 这个工具是本地的，用于模拟获取 K8s 集群信息。
# 它将被赋予 K8s 专家 Agent。

FUNCTION GET_CLUSTER_INFO():
    PRINT "--- LOCAL TOOL CALLED: GET_CLUSTER_INFO() ---"
    RETURN { ... a fixed list of cluster data ... }
END FUNCTION
```

### 2.2. `src/ops_crew/crew.py`
```python
# 伪代码: crew.py
# 这是我们系统的核心，负责定义和编排多个 Agent、Task 和 Crew。

# 引入我们自己写的本地工具
IMPORT GET_CLUSTER_INFO from tools

# 引入 crewAI 的核心组件
IMPORT Agent, Task, Crew, CrewBase, agent, task, crew from "crewai"
# 引入用于连接 MCP 服务器的适配器
IMPORT MCPServerAdapter from "crewai_tools"
# 引入用于连接 OpenRouter 的 LLM 客户端
IMPORT LLM from "crewai" # Wrapper for various LLMs

# 使用 @CrewBase 装饰器定义我们的主类
@CrewBase
CLASS OpsCrew():
    # 定义 agent 和 task 的配置文件路径
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    # 定义远程 MCP 服务器的连接参数
    mcp_server_params = [{
        "url": "https://mcp.api-inference.modelscope.net/...",
        "transport": "sse"
    }]

    # 初始化函数，用于设置 LLM
    FUNCTION __init__():
        self.llm = LLM(model="google/gemini-2.5-flash-preview-05-20", ...)
    END FUNCTION

    # 定义第一个 Agent: K8s 专家
    @agent
    FUNCTION k8s_expert():
        RETURN Agent(
            config=self.agents_config['k8s_expert'],
            tools=[GET_CLUSTER_INFO], # 只给他本地 K8s 工具
            llm=self.llm
        )
    END FUNCTION

    # 定义第二个 Agent: 网络研究员
    @agent
    FUNCTION web_researcher():
        RETURN Agent(
            config=self.agents_config['web_researcher'],
            tools=self.get_mcp_tools(), # 从 MCP 服务器获取工具
            llm=self.llm
        )
    END FUNCTION

    # 定义 K8s 专家的任务
    @task
    FUNCTION k8s_analysis_task():
        RETURN Task(
            config=self.tasks_config['k8s_analysis_task'],
            agent=self.k8s_expert() # 将任务分配给 K8s 专家
        )
    END FUNCTION

    # 定义网络研究员的任务
    @task
    FUNCTION web_fetch_task():
        RETURN Task(
            config=self.tasks_config['web_fetch_task'],
            agent=self.web_researcher() # 将任务分配给网络研究员
        )
    END FUNCTION

    # 组建 Crew
    @crew
    FUNCTION crew():
        RETURN Crew(
            agents=[self.k8s_expert(), self.web_researcher()], # 两个 Agent 都在团队里
            tasks=[self.k8s_analysis_task(), self.web_fetch_task()], # 两个任务都加入
            process="sequential" # 按顺序执行
        )
    END FUNCTION
END CLASS
```

### 2.3. `src/main.py`
```python
# 伪代码: main.py
# 用户交互入口，逻辑基本不变。

# 引入我们写的 crew 启动器
IMPORT run_crew from "src.ops_crew.crew"

FUNCTION main():
    PRINT "Ops Crew is running. Type 'exit' to quit."
    WHILE True:
        user_input = READ_FROM_CONSOLE("You: ")
        IF user_input == "exit": BREAK
        
        # 调用 Crew，传入用户输入
        # run_crew 内部会处理好 Crew 的初始化和任务格式化
        crew_response = run_crew(user_input)
        
        PRINT "Ops Crew: ", crew_response
    END WHILE
END FUNCTION

IF __name__ == "__main__":
    main()
``` 