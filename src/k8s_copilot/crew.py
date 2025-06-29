import os
from dotenv import load_dotenv
from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task

# Import the K8s tool we created
from src.tools import get_cluster_info

# Load environment variables from .env file
load_dotenv()


@CrewBase
class K8sCopilotCrew():
    """K8s Copilot crew"""

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

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
            tools=[get_cluster_info],
            llm=self.llm,
            verbose=True
        )

    @task
    def k8s_query_task(self) -> Task:
        return Task(
            config=self.tasks_config['k8s_query_task'],
            agent=self.k8s_expert()
        )

    @crew
    def crew(self) -> Crew:
        """Creates the K8s Copilot crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )


def run_crew(user_input: str) -> str:
    """
    Sets up and runs the K8s Copilot crew to process a user's request.

    Args:
        user_input: The question or command from the user.

    Returns:
        The result from the crew execution.
    """
    
    # Create the crew instance
    k8s_crew = K8sCopilotCrew()
    
    # Update the task description with user input
    # Note: We need to handle the user_input parameter in the task
    crew_instance = k8s_crew.crew()
    
    # Update the task description to include user input
    for task in crew_instance.tasks:
        task.description = task.description.format(user_input=user_input)
    
    # Execute the crew and return the result
    result = crew_instance.kickoff()
    return str(result)


if __name__ == "__main__":
    # A simple test to run the crew directly if the user provides an API key
    if os.getenv("OPENROUTER_API_KEY"):
        print("--- Running K8s Copilot Test ---")
        print(f"--- Using Model: {os.getenv('MODEL')} ---")
        test_input = "show me all k8s clusters"
        crew_result = run_crew(test_input)
        print("\n--- Crew Final Result ---")
        print(crew_result)
    else:
        print("Please set your OPENROUTER_API_KEY in the .env file to run this test.") 