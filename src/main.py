#!/usr/bin/env python
"""Platform Agent - 智能平台助手主程序"""

import warnings
import os
import sys
from dotenv import load_dotenv

from src.ops_crew.crew import run_crew

# 过滤警告，提升用户体验
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=PendingDeprecationWarning)
warnings.filterwarnings("ignore", category=SyntaxWarning)
warnings.filterwarnings("ignore", message=".*pydantic.*")
warnings.filterwarnings("ignore", message=".*invalid escape sequence.*")

# 设置环境变量禁用 pydantic 警告
os.environ["PYDANTIC_SILENCE_DEPRECATION_WARNINGS"] = "1"

# Load environment variables from .env file
load_dotenv()

def main():
    """
    Main function to run the CLI interface.
    """
    print("🚀 Welcome to the Platform Agent!")
    print("Type 'exit' or 'quit' to end the session.")
    print("==================================================")
    
    # Check if API key is configured
    if not os.getenv("OPENROUTER_API_KEY"):
        print("❌ Error: OPENROUTER_API_KEY not found in environment variables.")
        print("Please set your API key in a .env file or environment variable.")
        sys.exit(1)
    
    while True:
        try:
            # Get user input
            user_input = input("🤖 Platform Agent > ").strip()
            
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
