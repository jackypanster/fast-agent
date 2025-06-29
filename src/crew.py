import os
import json
from dotenv import load_dotenv

from crewai import Agent, Task, Crew, LLM

# Import the K8s tool we created
from src.tools import get_cluster_info

# Load environment variables from .env file
load_dotenv()

def run_crew(user_input: str) -> str:
    """
    Sets up and runs the K8s Copilot crew to process a user's request.

    Args:
        user_input: The question or command from the user.

    Returns:
        The result from the crew execution.
    """
    
    # Initialize the LLM with OpenRouter configuration according to CrewAI docs
    llm = LLM(
        model=os.getenv("MODEL"),
        base_url=os.getenv("BASE_URL"),
        api_key=os.getenv("OPENROUTER_API_KEY"),
        temperature=0.1
    )

    # Define the K8s expert agent with tools
    k8s_agent = Agent(
        role='Kubernetes Operations Expert',
        goal='Provide accurate and helpful information about Kubernetes clusters and operations',
        backstory="""You are a senior Kubernetes operations expert with deep knowledge of 
        cluster management, troubleshooting, and best practices. You have access to real 
        cluster information and can provide detailed insights about cluster status, 
        resources, and recommendations.""",
        verbose=True,
        allow_delegation=False,
        tools=[get_cluster_info],
        llm=llm
    )

    # Define the task
    task = Task(
        description=f"""
        Process the user's request: "{user_input}"
        
        Use the available tools to gather relevant cluster information if needed.
        Provide a comprehensive and helpful response that addresses the user's question or request.
        
        If the request is about cluster information, use the get_cluster_info tool to retrieve 
        current data and provide detailed insights.
        
        Format your response in a clear, professional manner suitable for a DevOps engineer.
        """,
        expected_output="""A detailed, professional response that addresses the user's request 
        with relevant cluster information, insights, and actionable recommendations where appropriate.""",
        agent=k8s_agent
    )

    # Create and run the crew
    crew = Crew(
        agents=[k8s_agent],
        tasks=[task],
        verbose=True
    )

    # Execute the crew and return the result
    result = crew.kickoff()
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
