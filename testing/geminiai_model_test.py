import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

# 1. Load your .env file
load_dotenv()

# 2. Initialize the Client
# It will look for os.getenv("GEMINI_API_KEY") automatically
client = genai.Client()

def run_grounded_search():
    try:
        # 3. Define the tool using the 2026 stable class name
        # IMPORTANT: Use GoogleSearch(), not GoogleSearchRetrieval()
        search_tool = types.Tool(
            google_search = types.GoogleSearch()
        )

        # 4. Correct call for google-genai 1.67.0
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents="What is the latest news about the 2026 World Cup venues?",
            config=types.GenerateContentConfig(
                tools=[search_tool],  # Tools MUST be inside GenerateContentConfig
                # Thinking is only for Gemini 2.5/3 Pro/Flash
                thinking_config=types.ThinkingConfig(
                    include_thoughts=True,
                    thinking_budget=1024
                )
            )
        )

        # Print the final answer
        print("Response:", response.text)
        
        # 5. Check if grounding was actually used
        if response.candidates[0].grounding_metadata:
            print("\nSources used:")
            for chunk in response.candidates[0].grounding_metadata.grounding_chunks:
                if chunk.web:
                    print(f"- {chunk.web.title}: {chunk.web.uri}")

    except Exception as e:
        print(f"Error details: {e}")

if __name__ == "__main__":
    run_grounded_search()