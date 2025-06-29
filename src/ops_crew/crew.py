import os
from dotenv import load_dotenv
from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import MCPServerAdapter

# Import the K8s tool we created
from src.tools import get_cluster_info

# Load environment variables from .env file
load_dotenv()


@CrewBase
class OpsCrew():
    """Ops Crew for multi-agent collaboration"""

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'
    
    # MCP Server configuration for the web researcher
    mcp_server_params = [
        {
            "url": "https://mcp.api-inference.modelscope.net/da81fcffd39044/sse",
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

    @agent
    def k8s_expert(self) -> Agent:
        return Agent(
            config=self.agents_config['k8s_expert'],
            tools=[get_cluster_info], # Only K8s tools
            llm=self.llm,
            verbose=True
        )
        
    @agent
    def web_researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['web_researcher'],
            tools=self.get_mcp_tools(), # Only MCP tools
            llm=self.llm,
            verbose=True
        )

    @task
    def k8s_analysis_task(self) -> Task:
        return Task(
            config=self.tasks_config['k8s_analysis_task'],
            agent=self.k8s_expert()
        )

    @task
    def web_fetch_task(self) -> Task:
        return Task(
            config=self.tasks_config['web_fetch_task'],
            agent=self.web_researcher()
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Ops crew"""
        return Crew(
            agents=[self.k8s_expert(), self.web_researcher()],
            tasks=[self.k8s_analysis_task(), self.web_fetch_task()],
            process=Process.sequential,
            memory=True,
            verbose=True,
            # Embedder will use OpenAI by default,
            # as long as OPENAI_API_KEY is set in the environment.
            # We are explicitly defining it here for clarity.
            embedder={
                "provider": "openai"
            }
        )


def run_crew(user_input: str) -> str:
    """
    Sets up and runs the Ops crew to process a user's request.

    Args:
        user_input: The question or command from the user.

    Returns:
        The result from the crew execution.
    """
    
    try:
        ops_crew = OpsCrew()
        crew_instance = ops_crew.crew()
        
        # Format the tasks with the user's input
        task_values = {"user_input": user_input}
        crew_instance.tasks[0].description = crew_instance.tasks[0].description.format(**task_values)
        crew_instance.tasks[1].description = crew_instance.tasks[1].description.format(**task_values)
        
        result = crew_instance.kickoff()
        return str(result)
        
    except Exception as e:
        return f"Error running crew: {str(e)}. Please check your configuration and try again."


if __name__ == "__main__":
    if os.getenv("OPENROUTER_API_KEY"):
        print("--- Running Ops Crew Test ---")
        print(f"--- Using Model: {os.getenv('MODEL')} ---")
        test_input = "Please provide a report on all Kubernetes clusters and also fetch the main content from https://crewai.com"
        crew_result = run_crew(test_input)
        print("\n--- Crew Final Result ---")
        print(crew_result)
    else:
        print("Please set your OPENROUTER_API_KEY in the .env file to run this test.") 