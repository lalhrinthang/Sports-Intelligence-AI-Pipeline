import os
import anthropic
from dotenv import load_dotenv

load_dotenv()

# Debug: check if key is loading
api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    print("❌ API key not found! Check your .env file.")
else:
    print("✅ API key loaded successfully.")

# Initialize the Anthropic client
client = anthropic.Anthropic(api_key=api_key)

def test_client():
    try:
        response = client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=10,
            messages=[
                {"role": "user", "content": "What is the capital of France?"}
            ]
        )
        print("Test Response:", response.content[0].text.strip())
    except Exception as e:
        print(f"Error testing client: {e}")

test_client()