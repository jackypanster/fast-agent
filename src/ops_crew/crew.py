import os
from dotenv import load_dotenv
from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import MCPServerAdapter

# Load environment variables from .env file
load_dotenv()


@CrewBase
class OpsCrew():
    """Platform Agent for multi-agent collaboration"""

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'
    
    # MCP Server configuration
    mcp_server_params = [
        {
            "url": os.getenv("K8S_MCP_URL"),
            "transport": "sse"
        }
    ]

    def __init__(self) -> None:
        # Configure Qwen embedding as OpenAI replacement for memory functionality
        os.environ["OPENAI_API_BASE"] = os.getenv("QWEN_API_BASE", "https://dashscope.aliyuncs.com/compatible-mode/v1")
        
        # Initialize the LLM with OpenRouter configuration
        self.llm = LLM(
            model=os.getenv("MODEL"),
            base_url=os.getenv("BASE_URL"),
            api_key=os.getenv("OPENROUTER_API_KEY"),
            temperature=0.1
        )

    def _load_mcp_tools_required(self):
        """
        Loads MCP tools with fail-fast strategy.
        Raises exception if MCP server is unavailable since the platform agent 
        requires these tools for core functionality.
        """
        tools = []
        
        # Check if MCP server is configured
        if not any(config.get("url") for config in self.mcp_server_params):
            raise RuntimeError(
                "❌ MCP服务器未配置！\n"
                "Platform Agent需要MCP工具来执行K8s操作。\n"
                "请在.env文件中设置K8S_MCP_URL。\n\n"
                "解决步骤：\n"
                "1. 检查.env文件中的K8S_MCP_URL配置\n"
                "2. 确保MCP服务器正在运行\n"
                "3. 验证网络连接：curl <MCP_URL>/health\n"
                "4. 运行 ./run.sh --verify 检查系统状态"
            )
        
        for server_config in self.mcp_server_params:
            mcp_url = server_config.get("url")
            if not mcp_url:
                continue
                
            try:
                # MCPServerAdapter expects serverparams as a dict
                # For SSE transport, pass the URL in the dict
                server_params = {
                    "url": mcp_url,
                    "transport": server_config.get("transport", "sse")
                }
                
                mcp_adapter = MCPServerAdapter(server_params)
                server_tools = mcp_adapter.tools
                tools.extend(server_tools)
                
                print(f"✅ 成功加载 {len(server_tools)} 个MCP工具从 {mcp_url}")
                
            except Exception as e:
                raise RuntimeError(
                    f"❌ 无法连接到MCP服务器: {mcp_url}\n"
                    f"错误: {str(e)}\n\n"
                    "可能的解决方案：\n"
                    "1. 检查MCP服务器是否运行：curl {}/health\n"
                    "2. 验证URL格式是否正确（需要包含协议 http://或https://）\n"
                    "3. 检查网络连接和防火墙设置\n"
                    "4. 查看MCP服务器日志排查问题\n"
                    "5. 尝试重启MCP服务器\n\n"
                    "如果问题持续，请检查：\n"
                    "- MCP服务器版本兼容性\n"
                    "- 服务器配置文件\n"
                    "- 系统资源使用情况".format(mcp_url)
                ) from e
        
        if not tools:
            raise RuntimeError(
                "❌ 没有可用的MCP工具！\n"
                "Platform Agent需要MCP工具来执行K8s操作。\n"
                "请确保MCP服务器正确配置并包含K8s工具。"
            )
            
        return tools

    @agent
    def tool_inspector(self) -> Agent:
        from crewai_tools import FileWriterTool, FileReadTool
        
        # Create file operations tools for cache management
        file_tools = [
            FileWriterTool(),  # For writing tools_cache.json
            FileReadTool(),    # For reading existing cache files
        ]
        
        # Combine MCP tools with file operation tools
        all_tools = self._load_mcp_tools_required() + file_tools
        
        return Agent(
            config=self.agents_config['tool_inspector'],
            # Give it access to all tools so it can catalog them AND write cache files
            tools=all_tools,
            llm=self.llm,
            verbose=False
        )

    @agent
    def k8s_expert(self) -> Agent:
        return Agent(
            config=self.agents_config['k8s_expert'],
            # Load all MCP tools directly in real-time
            tools=self._load_mcp_tools_required(),
            llm=self.llm,
            verbose=True
        )

    @task
    def tool_discovery_task(self) -> Task:
        return Task(
            config=self.tasks_config['tool_discovery_task'],
            agent=self.tool_inspector()
        )

    @task
    def k8s_analysis_task(self) -> Task:
        return Task(
            config=self.tasks_config['k8s_analysis_task'],
            agent=self.k8s_expert()
        )

    @crew
    def discovery_crew(self) -> Crew:
        """Creates a crew for tool discovery only"""
        return Crew(
            agents=[self.tool_inspector()],
            tasks=[self.tool_discovery_task()],
            process=Process.sequential,
            verbose=False
        )

    @crew
    def ops_crew(self) -> Crew:
        """Creates the main Ops crew for user tasks with memory enabled using Qwen embeddings"""
        
        # Configure Qwen embeddings for memory system
        qwen_embedder_config = {
            "provider": "openai",
            "config": {
                "api_key": os.getenv("OPENAI_API_KEY"),  # This is actually Qwen's key
                "api_base": os.getenv("QWEN_API_BASE", "https://dashscope.aliyuncs.com/compatible-mode/v1"),
                "model": os.getenv("QWEN_EMBEDDING_MODEL", "text-embedding-v4")
            }
        }
        
        return Crew(
            agents=[self.k8s_expert()],
            tasks=[self.k8s_analysis_task()],
            process=Process.sequential,
            verbose=True,
            memory=True,  # Enable CrewAI memory system
            embedder=qwen_embedder_config  # Use Qwen embeddings via OpenAI-compatible config
        )




def run_crew(user_input: str) -> str:
    """
    Sets up and runs the Ops crew to process a user's request.

    Args:
        user_input: The question or command from the user.

    Returns:
        The result from the crew execution.
    """
    ops_crew_instance = OpsCrew()
    main_crew = ops_crew_instance.ops_crew()
    
    # Format the task with the user's input
    task_values = {"user_input": user_input}
    main_crew.tasks[0].description = main_crew.tasks[0].description.format(**task_values)
    
    result = main_crew.kickoff()
    return str(result)


if __name__ == "__main__":
    if os.getenv("OPENROUTER_API_KEY"):
        print("--- Running Platform Agent Test ---")
        print(f"--- Using Model: {os.getenv('MODEL')} ---")
        test_input = "Please provide a report on all Kubernetes clusters"
        crew_result = run_crew(test_input)
        print("\n--- Crew Final Result ---")
        print(crew_result)
    else:
        print("Please set your OPENROUTER_API_KEY in the .env file to run this test.") 