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


    @agent
    def tool_inspector(self) -> Agent:
        return Agent(
            config=self.agents_config['tool_inspector'],
            # Give it access to all tools so it can catalog them
            tools=self.get_mcp_tools(),
            llm=self.llm,
            verbose=False
        )

    @agent
    def k8s_expert(self) -> Agent:
        return Agent(
            config=self.agents_config['k8s_expert'],
            # Load all MCP tools directly in real-time
            tools=self.get_mcp_tools(),
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