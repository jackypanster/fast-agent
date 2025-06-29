import os
import sys
from dotenv import load_dotenv

# Import the crew runner
from src.k8s_copilot.crew import run_crew

# Load environment variables
load_dotenv()

def main():
    """
    Main function to run the K8s Copilot CLI interface.
    """
    print("🚀 Welcome to K8s Copilot!")
    print("Type 'exit' or 'quit' to end the session.")
    print("=" * 50)
    
    # Check if API key is configured
    if not os.getenv("OPENROUTER_API_KEY"):
        print("❌ Error: OPENROUTER_API_KEY not found in environment variables.")
        print("Please set your API key in a .env file or environment variable.")
        sys.exit(1)
    
    while True:
        try:
            # Get user input
            user_input = input("\n🤖 K8s Copilot > ").strip()
            
            # Check for exit commands
            if user_input.lower() in ['exit', 'quit', 'q']:
                print("👋 Goodbye!")
                break
            
            # Skip empty input
            if not user_input:
                continue
            
            print("\n🔍 Processing your request...")
            print("=" * 50)
            
            # Run the crew and get the result
            result = run_crew(user_input)
            
            print("\n📋 Result:")
            print("=" * 50)
            print(result)
            print("=" * 50)
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ An error occurred: {str(e)}")
            print("Please try again or type 'exit' to quit.")

if __name__ == "__main__":
    main()
