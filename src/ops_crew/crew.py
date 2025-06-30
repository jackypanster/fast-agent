import os
import json
import pathlib
from datetime import datetime, timedelta
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
        # Initialize the LLM with OpenRouter configuration
        self.llm = LLM(
            model=os.getenv("MODEL"),
            base_url=os.getenv("BASE_URL"),
            api_key=os.getenv("OPENROUTER_API_KEY"),
            temperature=0.1
        )

    def _load_cached_tools(self):
        """Load tools from cache and return filtered tool names for k8s operations"""
        cache_path = pathlib.Path("tools_cache.json")
        if not cache_path.exists():
            # Fallback: load all tools if no cache exists
            return self.get_mcp_tools()
        
        try:
            cache_data = json.loads(cache_path.read_text())
            # Filter tools for k8s operations (list_, get_, describe_ prefixes)
            k8s_tool_names = [
                tool["name"] for tool in cache_data.get("tools", [])
                if tool["name"].lower().startswith(("list_", "get_", "describe_"))
            ]
            if k8s_tool_names:
                return self.get_mcp_tools(*k8s_tool_names)
            else:
                # Fallback if no matching tools found
                return self.get_mcp_tools()
        except (json.JSONDecodeError, KeyError):
            # Fallback on cache corruption
            return self.get_mcp_tools()

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
            # Use cached tools with intelligent filtering
            tools=self._load_cached_tools(),
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
        """Creates the main Ops crew for user tasks"""
        return Crew(
            agents=[self.k8s_expert()],
            tasks=[self.k8s_analysis_task()],
            process=Process.sequential,
            verbose=True
        )


def _should_refresh_cache() -> bool:
    """Check if tools cache needs to be refreshed (older than 24h or missing)"""
    cache_path = pathlib.Path("tools_cache.json")
    if not cache_path.exists():
        return True
    
    try:
        cache_data = json.loads(cache_path.read_text())
        fetched_at = datetime.fromisoformat(cache_data.get("fetched_at", ""))
        return datetime.now() - fetched_at > timedelta(hours=24)
    except (json.JSONDecodeError, KeyError, ValueError):
        return True


def run_crew(user_input: str) -> str:
    """
    Sets up and runs the Ops crew to process a user's request.
    Automatically runs tool discovery if cache is stale.

    Args:
        user_input: The question or command from the user.

    Returns:
        The result from the crew execution.
    """
    
    try:
        ops_crew_instance = OpsCrew()
        
        # Step 1: Run tool discovery if needed
        if _should_refresh_cache():
            print("🔍 Discovering and caching MCP tools...")
            discovery_crew = ops_crew_instance.discovery_crew()
            discovery_result = discovery_crew.kickoff()
            print(f"📋 Tool Discovery: {discovery_result}")
        
        # Step 2: Run the main ops crew
        main_crew = ops_crew_instance.ops_crew()
        
        # Format the task with the user's input
        task_values = {"user_input": user_input}
        main_crew.tasks[0].description = main_crew.tasks[0].description.format(**task_values)
        
        result = main_crew.kickoff()
        return str(result)
        
    except Exception as e:
        return f"Error running crew: {str(e)}. Please check your configuration and try again."


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