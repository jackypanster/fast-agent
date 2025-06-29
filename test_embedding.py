import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

print("--- Testing OpenRouter Embedding Endpoint ---")

# Check if the necessary environment variables are set
api_key = os.getenv("OPENROUTER_API_KEY")
base_url = os.getenv("BASE_URL")

if not api_key or not base_url:
    print("❌ Error: Please make sure OPENROUTER_API_KEY and BASE_URL are set in your .env file.")
else:
    print(f"✅ Found API Key and Base URL: {base_url}")
    
    try:
        # Initialize the OpenAI client, pointing it to OpenRouter
        client = OpenAI(
            base_url=base_url,
            api_key=api_key,
        )
        
        print("\nSending request to embedding endpoint...")
        
        # Make a direct call to the embedding endpoint
        embedding = client.embeddings.create(
            model="google/text-embedding-004",
            input="This is a simple test."
        )
        
        # If we get here, the request was successful
        print("✅ Success! Embedding received.")
        print(f"Vector dimensions: {len(embedding.data[0].embedding)}")
        # print(f"First 5 dimensions: {embedding.data[0].embedding[:5]}")

    except Exception as e:
        print(f"\n❌ Test Failed. An error occurred: {e}")

print("\n--- Test Finished ---") 