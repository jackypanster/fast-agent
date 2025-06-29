from src.crew import run_crew

def main():
    """
    The main entry point for the K8s Copilot CLI application.
    
    This function runs a loop to continuously accept user input and
    pass it to the crew for processing.
    """
    print(" K8s Copilot ".center(50, "="))
    print("Welcome to the K8s Copilot! I am ready to assist you.")
    print("Type 'exit' or 'quit' to end the session.")
    print("-" * 50)

    # Start a loop to continuously get user input
    while True:
        try:
            # 1. Read user input from the console
            user_input = input("You: ")

            # 2. Check for exit commands
            if user_input.lower() in ["exit", "quit"]:
                break

            # 3. If input is empty, continue to the next iteration
            if not user_input.strip():
                continue

            # 4. Call our Crew to process the input
            crew_response = run_crew(user_input)

            # 5. Print the crew's response to the console
            print("\nCopilot:")
            print(crew_response)
            print("-" * 50)

        except KeyboardInterrupt:
            # Handle Ctrl+C gracefully
            print("\n\nSession terminated by user.")
            break
        except Exception as e:
            # Handle other potential errors gracefully
            print(f"\nAn unexpected error occurred: {e}")
            print("Please try again.")
            print("-" * 50)

    print("=" * 50)
    print(" Thank you for using K8s Copilot! ".center(50, "="))


if __name__ == "__main__":
    main()
